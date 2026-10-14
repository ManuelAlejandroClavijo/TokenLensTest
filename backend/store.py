"""TokenLens domain storage. No conversation content is persisted."""

import hashlib
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PHASES = [
    "discovery",
    "enrichment",
    "planning",
    "proposal",
    "specs",
    "design",
    "tasks",
    "apply",
    "verify",
    "close",
    "unassigned",
]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode()
    ).hexdigest()


def number(v):
    try:
        n = int(v or 0)
        return max(0, min(n, 10**12))
    except (ValueError, TypeError, OverflowError):
        return 0


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
 source TEXT NOT NULL, id TEXT NOT NULL, started_at TEXT NOT NULL, last_seen TEXT NOT NULL,
 developer TEXT DEFAULT 'local-user', repo TEXT DEFAULT '', work_item TEXT DEFAULT '', change_id TEXT DEFAULT '',
 phase TEXT DEFAULT 'unassigned', status TEXT DEFAULT 'active', PRIMARY KEY(source,id));
CREATE TABLE IF NOT EXISTS prompts (
 source TEXT NOT NULL, session_id TEXT NOT NULL, id TEXT NOT NULL, started_at TEXT NOT NULL,
 ended_at TEXT, work_item TEXT DEFAULT '', change_id TEXT DEFAULT '', phase TEXT DEFAULT 'unassigned',
 attribution TEXT DEFAULT 'unassigned', status TEXT DEFAULT 'running', command TEXT DEFAULT '', developer TEXT DEFAULT 'local-user',
 PRIMARY KEY(source,session_id,id));
CREATE TABLE IF NOT EXISTS requests (
 id INTEGER PRIMARY KEY, source TEXT NOT NULL, dedup_key TEXT NOT NULL, session_id TEXT NOT NULL,
 prompt_id TEXT DEFAULT '', request_id TEXT DEFAULT '', occurred_at TEXT NOT NULL, model TEXT DEFAULT 'unknown',
 input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0, cache_read_tokens INTEGER DEFAULT 0,
 cache_creation_tokens INTEGER DEFAULT 0, cost_usd REAL, duration_ms INTEGER DEFAULT 0,
 query_source TEXT DEFAULT 'unknown', status TEXT DEFAULT 'success', identity_quality TEXT DEFAULT 'fallback',
 work_item TEXT DEFAULT '', change_id TEXT DEFAULT '', phase TEXT DEFAULT 'unassigned',
 attribution TEXT DEFAULT 'unassigned', developer TEXT DEFAULT 'local-user', UNIQUE(source,dedup_key));
CREATE INDEX IF NOT EXISTS requests_session ON requests(source,session_id,prompt_id);
CREATE INDEX IF NOT EXISTS requests_task ON requests(source,work_item,phase);
CREATE TABLE IF NOT EXISTS tools (
 id INTEGER PRIMARY KEY, source TEXT, dedup_key TEXT, session_id TEXT, prompt_id TEXT,
 tool_name TEXT, duration_ms INTEGER, input_bytes INTEGER, output_bytes INTEGER, success INTEGER,
 occurred_at TEXT, UNIQUE(source,dedup_key));
CREATE TABLE IF NOT EXISTS metrics (
 id INTEGER PRIMARY KEY, source TEXT, dedup_key TEXT, session_id TEXT, model TEXT, type TEXT,
 query_source TEXT, value REAL, start_time TEXT, time TEXT, temporality INTEGER,
 UNIQUE(source,dedup_key));
CREATE TABLE IF NOT EXISTS receipts (
 id INTEGER PRIMARY KEY, source TEXT, kind TEXT, received_at TEXT, accepted INTEGER, duplicates INTEGER,
 ignored INTEGER, invalid INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY, source TEXT, created_at TEXT, action TEXT, target TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS hook_receipts (source TEXT, event_id TEXT, PRIMARY KEY(source,event_id));
CREATE TABLE IF NOT EXISTS hook_edges (source TEXT, session_id TEXT, prompt_id TEXT, event TEXT, occurred_at TEXT);
CREATE TABLE IF NOT EXISTS reconciliations (
 id INTEGER PRIMARY KEY, source TEXT, session_id TEXT, created_at TEXT, observed TEXT, expected TEXT, note TEXT);
"""


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript(SCHEMA)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA busy_timeout=15000")
            with db:
                yield db
        finally:
            db.close()

    def rows(self, query, args=()):
        with self.connect() as db:
            return [dict(r) for r in db.execute(query, args)]

    def session(self, db, source, sid, timestamp=None):
        timestamp = timestamp or now()
        db.execute(
            "INSERT OR IGNORE INTO sessions(source,id,started_at,last_seen) VALUES(?,?,?,?)",
            (source, sid, timestamp, timestamp),
        )
        db.execute(
            "UPDATE sessions SET last_seen=MAX(last_seen,?) WHERE source=? AND id=?",
            (timestamp, source, sid),
        )
        return dict(
            db.execute(
                "SELECT * FROM sessions WHERE source=? AND id=?", (source, sid)
            ).fetchone()
        )

    def context_at(self, db, source, sid, pid, timestamp):
        # A delayed hook must not inherit a binding made AFTER it was submitted.
        records = db.execute(
            "SELECT * FROM audit WHERE source=? AND target=? AND action='bind' ORDER BY id DESC",
            (source, sid),
        )
        for row in records:
            data = json.loads(row["detail"])
            retrospective = data.get("scope") == "session" or (
                data.get("scope") == "prompt" and data.get("prompt_id") == pid
            )
            if source == "demo" or row["created_at"] <= timestamp or retrospective:
                return {
                    **data,
                    "method": "manual"
                    if retrospective and row["created_at"] > timestamp
                    else "explicit",
                }
        return {
            "work_item": "",
            "change_id": "",
            "phase": "unassigned",
            "developer": "local-user",
            "method": "unassigned",
        }

    def attribution(self, db, source, sid, pid):
        p = db.execute(
            "SELECT * FROM prompts WHERE source=? AND session_id=? AND id=?",
            (source, sid, pid),
        ).fetchone()
        if p:
            return (
                p["work_item"],
                p["change_id"],
                p["phase"],
                p["attribution"],
                p["developer"],
            )
        # Never guess from the current session: the event may have arrived late.
        return "", "", "unassigned", "unassigned", "local-user"

    def request(self, source, attrs, timestamp, event="api_request"):
        sid = str(attrs.get("session.id") or "")[:160]
        if not sid:
            return "invalid"
        pid = str(attrs.get("prompt.id") or "")[:160]
        rid = str(attrs.get("request_id") or "")[:160]
        cid = str(attrs.get("client_request_id") or "")[:160]
        quality = "server" if rid else ("client" if cid else "fallback")
        key = (
            digest([sid, rid or cid])
            if (rid or cid)
            else digest(
                [
                    sid,
                    pid,
                    timestamp,
                    event,
                    attrs.get("event.sequence"),
                    attrs.get("model"),
                ]
            )
        )
        fields = [
            "input_tokens",
            "output_tokens",
            "cache_read_tokens",
            "cache_creation_tokens",
        ]
        tokens = [number(attrs.get(f)) for f in fields]
        # An absent counter is unknown, not silently a complete zero-valued record.
        if event == "api_request" and not all(f in attrs for f in fields):
            quality += ":partial"
        cost = None
        try:
            if attrs.get("cost_usd_micros") is not None:
                cost = int(attrs["cost_usd_micros"]) / 1_000_000
            elif attrs.get("cost_usd") is not None:
                cost = float(attrs["cost_usd"])
            if cost is not None and (not 0 <= cost < 1e9):
                cost = None
        except (ValueError, TypeError):
            cost = None
        with self.lock, self.connect() as db:
            s = self.session(db, source, sid, timestamp)
            wi, change, phase, method, developer = self.attribution(
                db, source, sid, pid
            )
            cur = db.execute(
                """INSERT OR IGNORE INTO requests(source,dedup_key,session_id,prompt_id,request_id,occurred_at,
             model,input_tokens,output_tokens,cache_read_tokens,cache_creation_tokens,cost_usd,duration_ms,query_source,
             status,identity_quality,work_item,change_id,phase,attribution,developer)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    source,
                    key,
                    sid,
                    pid,
                    rid,
                    timestamp,
                    str(attrs.get("model", "unknown"))[:100],
                    *tokens,
                    cost,
                    number(attrs.get("duration_ms")),
                    str(attrs.get("query_source", "unknown"))[:100],
                    "error" if event == "api_error" else "success",
                    quality,
                    wi,
                    change,
                    phase,
                    method,
                    developer,
                ),
            )
            return "accepted" if cur.rowcount else "duplicates"

    def tool(self, source, attrs, timestamp):
        sid = str(attrs.get("session.id") or "")[:160]
        if not sid:
            return "invalid"
        pid = str(attrs.get("prompt.id") or "")[:160]
        key = digest(
            [
                sid,
                pid,
                timestamp,
                attrs.get("event.sequence"),
                attrs.get("tool_name"),
                attrs.get("tool_use_id"),
            ]
        )
        with self.lock, self.connect() as db:
            self.session(db, source, sid, timestamp)
            c = db.execute(
                """INSERT OR IGNORE INTO tools(source,dedup_key,session_id,prompt_id,tool_name,duration_ms,
            input_bytes,output_bytes,success,occurred_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    source,
                    key,
                    sid,
                    pid,
                    str(attrs.get("tool_name", "unknown"))[:140],
                    number(attrs.get("duration_ms")),
                    number(attrs.get("tool_input_size_bytes")),
                    number(attrs.get("tool_result_size_bytes")),
                    int(str(attrs.get("success", True)).lower() == "true"),
                    timestamp,
                ),
            )
            return "accepted" if c.rowcount else "duplicates"

    def hook(self, source, data):
        sid = data["session_id"]
        pid = data.get("prompt_id") or ""
        event = data["event"]
        timestamp = data.get("timestamp") or now()
        with self.lock, self.connect() as db:
            if not db.execute(
                "INSERT OR IGNORE INTO hook_receipts VALUES(?,?)",
                (source, data["event_id"]),
            ).rowcount:
                return "duplicates"
            s = self.session(db, source, sid, timestamp)
            repo = data.get("repo", "")[:120]
            if repo:
                db.execute(
                    "UPDATE sessions SET repo=? WHERE source=? AND id=?",
                    (repo, source, sid),
                )
            if event == "SessionStart":
                db.execute(
                    "UPDATE sessions SET status='active' WHERE source=? AND id=?",
                    (source, sid),
                )
            if event == "SessionEnd":
                db.execute(
                    "UPDATE sessions SET status='ended' WHERE source=? AND id=?",
                    (source, sid),
                )
                db.execute(
                    "UPDATE prompts SET status='interrupted',ended_at=? WHERE source=? AND session_id=? AND status='running'",
                    (timestamp, source, sid),
                )
            elif event in ("Stop", "StopFailure") and pid:
                db.execute(
                    "INSERT INTO hook_edges VALUES(?,?,?,?,?)",
                    (source, sid, pid, event, timestamp),
                )
                db.execute(
                    "UPDATE prompts SET status=?,ended_at=? WHERE source=? AND session_id=? AND id=?",
                    (
                        "error" if event == "StopFailure" else "completed",
                        timestamp,
                        source,
                        sid,
                        pid,
                    ),
                )
            elif event == "UserPromptSubmit" and pid:
                hint = data.get("phase_hint")
                wi_hint = str(data.get("work_item_hint") or "")[:32]
                ctx = self.context_at(db, source, sid, pid, timestamp)
                phase = (
                    ctx["phase"]
                    if ctx["phase"] != "unassigned"
                    else (hint if hint in PHASES else "unassigned")
                )
                work_item = ctx["work_item"] or wi_hint
                method = (
                    ctx["method"]
                    if ctx["method"] != "unassigned"
                    else (
                        "command"
                        if phase != "unassigned" or work_item
                        else "unassigned"
                    )
                )
                db.execute(
                    """INSERT OR IGNORE INTO prompts(source,session_id,id,started_at,work_item,change_id,phase,attribution,command,developer)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        source,
                        sid,
                        pid,
                        timestamp,
                        work_item,
                        ctx["change_id"],
                        phase,
                        method,
                        data.get("command", "")[:60],
                        ctx["developer"],
                    ),
                )
                terminal = db.execute(
                    "SELECT * FROM hook_edges WHERE source=? AND session_id=? AND prompt_id=? AND occurred_at>=? ORDER BY occurred_at DESC LIMIT 1",
                    (source, sid, pid, timestamp),
                ).fetchone()
                if terminal:
                    db.execute(
                        "UPDATE prompts SET status=?,ended_at=? WHERE source=? AND session_id=? AND id=?",
                        (
                            "error"
                            if terminal["event"] == "StopFailure"
                            else "completed",
                            terminal["occurred_at"],
                            source,
                            sid,
                            pid,
                        ),
                    )
                # Resolve only orphan events of this prompt, never overwrite manual attribution.
                p = db.execute(
                    "SELECT * FROM prompts WHERE source=? AND session_id=? AND id=?",
                    (source, sid, pid),
                ).fetchone()
                db.execute(
                    """UPDATE requests SET work_item=?,change_id=?,phase=?,attribution=?,developer=?
                 WHERE source=? AND session_id=? AND prompt_id=? AND attribution='unassigned' """,
                    (
                        p["work_item"],
                        p["change_id"],
                        p["phase"],
                        p["attribution"],
                        p["developer"],
                        source,
                        sid,
                        pid,
                    ),
                )
            return "accepted"

    def bind(self, source, sid, data):
        with self.lock, self.connect() as db:
            self.session(db, source, sid)
            db.execute(
                "UPDATE sessions SET work_item=?,change_id=?,phase=?,developer=? WHERE source=? AND id=?",
                (
                    data["work_item"],
                    data["change_id"],
                    data["phase"],
                    data["developer"],
                    source,
                    sid,
                ),
            )
            scope = data.get("scope", "future")
            if scope == "session":
                db.execute(
                    "UPDATE prompts SET work_item=?,change_id=?,phase=?,attribution=?,developer=? WHERE source=? AND session_id=?",
                    (
                        data["work_item"],
                        data["change_id"],
                        data["phase"],
                        "manual",
                        data["developer"],
                        source,
                        sid,
                    ),
                )
                db.execute(
                    "UPDATE requests SET work_item=?,change_id=?,phase=?,attribution=?,developer=? WHERE source=? AND session_id=?",
                    (
                        data["work_item"],
                        data["change_id"],
                        data["phase"],
                        "manual",
                        data["developer"],
                        source,
                        sid,
                    ),
                )
            elif scope == "prompt":
                pid = data["prompt_id"]
                db.execute(
                    "UPDATE prompts SET work_item=?,change_id=?,phase=?,attribution=?,developer=? WHERE source=? AND session_id=? AND id=?",
                    (
                        data["work_item"],
                        data["change_id"],
                        data["phase"],
                        "manual",
                        data["developer"],
                        source,
                        sid,
                        pid,
                    ),
                )
                db.execute(
                    "UPDATE requests SET work_item=?,change_id=?,phase=?,attribution=?,developer=? WHERE source=? AND session_id=? AND prompt_id=?",
                    (
                        data["work_item"],
                        data["change_id"],
                        data["phase"],
                        "manual",
                        data["developer"],
                        source,
                        sid,
                        pid,
                    ),
                )
            db.execute(
                "INSERT INTO audit(source,created_at,action,target,detail) VALUES(?,?,?,?,?)",
                (source, now(), "bind", sid, json.dumps(data)),
            )

    def receipt(self, source, kind, counts):
        with self.lock, self.connect() as db:
            db.execute(
                "INSERT INTO receipts(source,kind,received_at,accepted,duplicates,ignored,invalid) VALUES(?,?,?,?,?,?,?)",
                (
                    source,
                    kind,
                    now(),
                    *[
                        counts.get(k, 0)
                        for k in ("accepted", "duplicates", "ignored", "invalid")
                    ],
                ),
            )

    def metric(self, source, attrs, point, temporality):
        sid = str(attrs.get("session.id") or "")[:160]
        if not sid:
            return "invalid"
        value = point.get("asInt", point.get("asDouble", 0))
        key = digest(
            [
                sid,
                attrs,
                point.get("startTimeUnixNano"),
                point.get("timeUnixNano"),
                value,
                temporality,
            ]
        )
        with self.lock, self.connect() as db:
            c = db.execute(
                """INSERT OR IGNORE INTO metrics(source,dedup_key,session_id,model,type,query_source,value,start_time,time,temporality)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    source,
                    key,
                    sid,
                    str(attrs.get("model", "unknown"))[:100],
                    str(attrs.get("type", "unknown"))[:40],
                    str(attrs.get("query_source", "unknown"))[:80],
                    number(value),
                    str(point.get("startTimeUnixNano", "")),
                    str(point.get("timeUnixNano", "")),
                    temporality,
                ),
            )
            return "accepted" if c.rowcount else "duplicates"

    def dashboard(self, source):
        requests = self.rows(
            "SELECT * FROM requests WHERE source=? ORDER BY occurred_at DESC,id DESC",
            (source,),
        )
        sessions = self.rows(
            "SELECT * FROM sessions WHERE source=? ORDER BY last_seen DESC", (source,)
        )
        prompts = self.rows(
            "SELECT * FROM prompts WHERE source=? ORDER BY started_at DESC", (source,)
        )
        tools = self.rows(
            "SELECT * FROM tools WHERE source=? ORDER BY occurred_at DESC LIMIT 1000",
            (source,),
        )
        receipts = self.rows(
            "SELECT * FROM receipts WHERE source=? ORDER BY id DESC LIMIT 100",
            (source,),
        )
        audit = self.rows(
            "SELECT * FROM audit WHERE source=? ORDER BY id DESC LIMIT 50", (source,)
        )
        metrics = self.rows(
            "SELECT * FROM metrics WHERE source=? ORDER BY id DESC LIMIT 500", (source,)
        )
        return {
            "source": source,
            "requests": requests,
            "sessions": sessions,
            "prompts": prompts,
            "tools": tools,
            "receipts": receipts,
            "audit": audit,
            "metrics": metrics,
            "phases": PHASES,
            "reconciliations": self.rows(
                "SELECT * FROM reconciliations WHERE source=? ORDER BY id DESC LIMIT 50",
                (source,),
            ),
        }

    def clear_demo(self):
        with self.lock, self.connect() as db:
            for table in (
                "sessions",
                "prompts",
                "requests",
                "tools",
                "metrics",
                "receipts",
                "audit",
                "hook_receipts",
                "hook_edges",
                "reconciliations",
            ):
                db.execute(f"DELETE FROM {table} WHERE source='demo'")
