"""Stdlib-only hook adapter. Reads Claude's stdin, persists metadata only, never prints prompts."""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener

# Never send local metadata through a corporate/environment HTTP proxy.
urlopen = build_opener(ProxyHandler({})).open

MAP = {
    "/opsx:propose": "planning",
    "/openspec:proposal": "planning",
    "/opsx:apply": "apply",
    "/openspec:apply": "apply",
    "/opsx:archive": "close",
    "/openspec:archive": "close",
    "/opsx:explore": "discovery",
    "/opsx:verify": "verify",
    "/opsx:new": "planning",
    "/opsx:continue": "planning",
    "/opsx:ff": "planning",
    "/opsx:update": "planning",
    "/opsx:sync": "close",
}

# Matches "HU 1111", "HU-1111", "HU#1111", "HU:1111" (the Azure DevOps work
# item number devs type after an /opsx:* command). Only the digits are kept;
# the rest of the prompt is never inspected beyond its first line.
HU_PATTERN = re.compile(r"\bHU\s*[:#-]?\s*(\d{1,10})\b", re.IGNORECASE)


def sanitize(raw, project=None):
    cwd = Path(raw.get("cwd") or ".")
    if project:
        try:
            cwd.resolve().relative_to(Path(project).resolve())
        except (ValueError, OSError):
            return None
    event = raw.get("hook_event_name")
    if event not in (
        "SessionStart",
        "SessionEnd",
        "UserPromptSubmit",
        "Stop",
        "StopFailure",
    ) or not raw.get("session_id"):
        return None
    # Inspect only the slash-command prefix and an "HU <number>" pattern on
    # the first line; the rest of the prompt is never read or persisted.
    first_line = str(raw.get("prompt") or "").strip().split("\n", 1)[0][:200]
    prefix = first_line.split(" ", 1)[0]
    command = prefix if prefix in MAP else ""
    hu_match = HU_PATTERN.search(first_line)
    return {
        "schema_version": 1,
        "event_id": str(uuid.uuid4()),
        "event": event,
        "session_id": str(raw["session_id"])[:160],
        "prompt_id": str(raw.get("prompt_id") or "")[:160],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": cwd.name[:120],
        "command": command,
        "phase_hint": MAP.get(command, ""),
        "work_item_hint": hu_match.group(1) if hu_match else "",
    }


def drain(data, max_files=30):
    data = Path(data)
    queue = data / "outbox"
    queue.mkdir(parents=True, exist_ok=True)
    lock = queue / ".drain.lock"
    try:
        if lock.exists() and time.time() - lock.stat().st_mtime > 120:
            lock.unlink(missing_ok=True)
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    except (FileExistsError, OSError):
        return 0
    sent = 0
    try:
        config = json.loads((data / "config.json").read_text())
        endpoint = config.get("endpoint", "http://127.0.0.1:4318")
        parsed = urlparse(endpoint)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in ("127.0.0.1", "localhost")
            or parsed.path not in ("", "/")
            or parsed.username
        ):
            return 0
        endpoint = endpoint.rstrip("/")
        for file in sorted(queue.glob("*.json"))[:max_files]:
            try:
                req = Request(
                    endpoint + "/hooks",
                    data=file.read_bytes(),
                    method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + config["ingest_token"],
                    },
                )
                with urlopen(req, timeout=0.5) as response:
                    if response.status == 200:
                        file.unlink(missing_ok=True)
                        sent += 1
            except Exception:
                break
    finally:
        lock.unlink(missing_ok=True)
    return sent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--project")
    args = parser.parse_args()
    try:
        raw = json.loads(sys.stdin.read(2_000_000))
        meta = sanitize(raw, args.project)
        if meta:
            queue = Path(args.data) / "outbox"
            queue.mkdir(parents=True, exist_ok=True)
            dest = queue / (str(time.time_ns()) + "-" + meta["event_id"] + ".json")
            temp = dest.with_suffix(".tmp")
            temp.write_text(json.dumps(meta), encoding="utf-8")
            try:
                temp.chmod(0o600)
            except OSError:
                pass
            temp.replace(dest)
        drain(args.data, 10)
    except Exception:
        # Observability is fail-open: never block Claude development.
        print(
            "TokenLens: hook no capturado; revisa la configuración local.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
