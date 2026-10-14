import asyncio
import csv
import gzip
import io
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
    ExportLogsServiceResponse,
)
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
    ExportMetricsServiceResponse,
)

from .store import Store, PHASES, now
from .otel import ingest_logs, ingest_metrics
from .demo import seed

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.getenv("TOKENLENS_DATA_DIR", str(ROOT / "data")))
DATA.mkdir(parents=True, exist_ok=True)
try:
    DATA.chmod(0o700)
except OSError:
    pass
CONFIG = DATA / "config.json"
if not CONFIG.exists():
    CONFIG.write_text(json.dumps({"ingest_token": secrets.token_urlsafe(32)}, indent=2))
    try:
        CONFIG.chmod(0o600)
    except OSError:
        pass
INGEST_TOKEN = json.loads(CONFIG.read_text())["ingest_token"]
store = Store(DATA / "tokenlens.sqlite3")
revision = 0


@asynccontextmanager
async def lifespan(app):
    from scripts.hook_agent import drain

    async def flush_hooks():
        while True:
            await asyncio.to_thread(drain, DATA, 100)
            await asyncio.sleep(5)

    task = asyncio.create_task(flush_hooks())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="TokenLens Local Pilot", version="0.1.0", lifespan=lifespan)


def changed():
    global revision
    revision += 1


@app.middleware("http")
async def local_boundary(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0].strip("[]")
    allowed = {"localhost", "127.0.0.1", "::1", "testserver"}
    allowed.update(x for x in os.getenv("TOKENLENS_ALLOWED_HOSTS", "").split(",") if x)
    preview = os.getenv("TOKENLENS_PREVIEW") == "1" and host.endswith(".e2b.app")
    if host not in allowed and not preview:
        return JSONResponse(
            {"detail": "Host no permitido. TokenLens es local."}, status_code=403
        )
    origin = request.headers.get("origin")
    if origin and (
        urlparse(origin).netloc != request.headers.get("host")
        or urlparse(origin).scheme not in ("http", "https")
    ):
        return JSONResponse({"detail": "Origen externo no permitido."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    # UI must also work inside Arena's preview; default local installation blocks framing.
    if os.getenv("TOKENLENS_PREVIEW") != "1":
        response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


async def payload(request, kind):
    auth = request.headers.get("authorization", "")
    if not secrets.compare_digest(auth, "Bearer " + INGEST_TOKEN):
        raise HTTPException(
            401, "Credencial de ingesta incorrecta. Ejecuta pilot.py init."
        )
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > 8_000_000:
            raise HTTPException(413, "Payload superior a 8 MB.")
    raw = bytes(content)
    encoding = request.headers.get("content-encoding", "identity")
    if encoding not in ("identity", "gzip"):
        raise HTTPException(415, "Content-Encoding no soportado.")
    try:
        if encoding == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:
                raw = f.read(8_000_001)
            if len(raw) > 8_000_000:
                raise HTTPException(413, "Payload descomprimido superior a 8 MB.")
        ctype = request.headers.get("content-type", "application/json").split(";")[0]
        if ctype in ("application/x-protobuf", "application/protobuf"):
            msg = (
                ExportLogsServiceRequest()
                if kind == "logs"
                else ExportMetricsServiceRequest()
            )
            msg.ParseFromString(raw)
            return MessageToDict(msg), True
        if ctype != "application/json":
            raise HTTPException(415, "Usa OTLP HTTP JSON o protobuf.")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Se esperaba objeto JSON")
        return data, False
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Payload OTLP inválido; no se guarda su contenido.")


async def receive(request, kind):
    data, isproto = await payload(request, kind)
    root = "resourceLogs" if kind == "logs" else "resourceMetrics"
    if root not in data and data:
        raise HTTPException(
            400, f"Falta {root}. Se espera el envelope OTLP, no un evento plano."
        )
    try:
        counts = (
            ingest_logs(store, data) if kind == "logs" else ingest_metrics(store, data)
        )
    except (TypeError, KeyError, AttributeError, ValueError):
        raise HTTPException(400, "Estructura OTLP inválida. Revisa diagnósticos.")
    changed()
    rejected = counts["invalid"]
    if isproto:
        result = (
            ExportLogsServiceResponse()
            if kind == "logs"
            else ExportMetricsServiceResponse()
        )
        if rejected:
            if kind == "logs":
                result.partial_success.rejected_log_records = rejected
            else:
                result.partial_success.rejected_data_points = rejected
            result.partial_success.error_message = (
                "Registros sin session.id; no atribuibles."
            )
        return Response(result.SerializeToString(), media_type="application/x-protobuf")
    return (
        {
            "partialSuccess": {
                "rejectedLogRecords" if kind == "logs" else "rejectedDataPoints": str(
                    rejected
                ),
                "errorMessage": "Registros sin session.id" if rejected else "",
            }
        }
        if rejected
        else {}
    )


@app.post("/v1/logs")
async def logs(request: Request):
    return await receive(request, "logs")


@app.post("/v1/metrics")
async def metrics(request: Request):
    return await receive(request, "metrics")


class Hook(BaseModel):
    event_id: str = Field(min_length=1, max_length=160)
    event: Literal[
        "SessionStart", "SessionEnd", "UserPromptSubmit", "Stop", "StopFailure"
    ]
    session_id: str = Field(min_length=1, max_length=160)
    prompt_id: str = Field(default="", max_length=160)
    timestamp: str | None = None
    repo: str = Field(default="", max_length=120)
    phase_hint: str = Field(default="", max_length=60)
    command: str = Field(default="", max_length=60)
    work_item_hint: str = Field(default="", max_length=32)
    schema_version: int = 1

    @field_validator("work_item_hint")
    @classmethod
    def digits_only(cls, v):
        return "".join(c for c in (v or "") if c.isdigit())[:32]

    @field_validator("timestamp")
    @classmethod
    def valid_time(cls, v):
        if v:
            from datetime import datetime, timezone

            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return (
                dt.replace(tzinfo=dt.tzinfo or timezone.utc)
                .astimezone(timezone.utc)
                .isoformat()
            )
        return v


@app.post("/hooks")
async def hooks(request: Request):
    data, _ = await payload(request, "logs")
    try:
        obj = Hook.model_validate(data)
    except Exception:
        raise HTTPException(
            422, "Hook inválido. Se necesita session_id, event_id y event."
        )
    result = store.hook("real", obj.model_dump())
    store.receipt("real", "hooks", {result: 1})
    changed()
    return {"result": result}


def source_check(source):
    if source not in ("real", "demo"):
        raise HTTPException(400, "Fuente inválida")


@app.get("/api/dashboard")
def dashboard(source: str = "real"):
    source_check(source)
    return {
        **store.dashboard(source),
        "revision": revision,
        "version": "0.1.0",
        "normalizer_version": 1,
    }


class Binding(BaseModel):
    work_item: str = Field(default="", max_length=100)
    change_id: str = Field(default="", max_length=160)
    phase: str = "unassigned"
    developer: str = Field(default="local-user", max_length=100)
    scope: Literal["future", "session", "prompt"] = "future"
    prompt_id: str = Field(default="", max_length=160)

    @field_validator("phase")
    @classmethod
    def phase_known(cls, v):
        if v not in PHASES:
            raise ValueError("Fase no admitida")
        return v


@app.put("/api/sessions/{sid}/binding")
def binding(sid: str, body: Binding, source: str = "real"):
    source_check(source)
    if not store.rows("SELECT id FROM sessions WHERE source=? AND id=?", (source, sid)):
        raise HTTPException(404, "Sesión no encontrada")
    if body.scope == "prompt" and not body.prompt_id:
        raise HTTPException(422, "Selecciona una petición")
    store.bind(source, sid, body.model_dump())
    changed()
    return {"ok": True}


@app.post("/api/demo")
def demo():
    seed(store)
    changed()
    return {"ok": True, "source": "demo"}


@app.delete("/api/demo")
def delete_demo():
    store.clear_demo()
    changed()
    return {"ok": True}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "local_only": os.getenv("TOKENLENS_PREVIEW") != "1",
        "database": "SQLite / WAL",
        "privacy": "metadata-only",
        "time": now(),
    }


@app.get("/api/events")
async def events(request: Request):
    async def stream():
        previous = -1
        ticks = 0
        while not await request.is_disconnected():
            if previous != revision:
                previous = revision
                yield f"event: update\ndata: {json.dumps({'revision': revision})}\n\n"
            elif ticks % 15 == 0:
                yield ": keepalive\n\n"
            ticks += 1
            await asyncio.sleep(1)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/export.csv")
def export(
    source: str = "real",
    work_item: str = "",
    session_id: str = "",
    developer: str = "",
    repo: str = "",
    q: str = "",
    range: Literal["all", "24h", "7d"] = "all",
):
    source_check(source)
    rows = store.rows(
        "SELECT * FROM requests WHERE source=? ORDER BY occurred_at", (source,)
    )
    if work_item:
        rows = [r for r in rows if r["work_item"] == work_item]
    if repo:
        session_repos = {
            s["id"]: s["repo"]
            for s in store.rows(
                "SELECT id,repo FROM sessions WHERE source=?", (source,)
            )
        }
        rows = [r for r in rows if session_repos.get(r["session_id"], "") == repo]
    if session_id:
        rows = [r for r in rows if r["session_id"] == session_id]
    if developer:
        rows = [r for r in rows if r["developer"] == developer]
    if q:
        rows = [
            r
            for r in rows
            if q.lower()
            in " ".join(
                str(r[k])
                for k in (
                    "work_item",
                    "change_id",
                    "session_id",
                    "model",
                    "phase",
                    "prompt_id",
                )
            ).lower()
        ]
    if range != "all":
        from datetime import datetime, timezone, timedelta

        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=24 if range == "24h" else 168)
        ).isoformat()
        rows = [r for r in rows if r["occurred_at"] > cutoff]
    fields = [
        "source",
        "developer",
        "work_item",
        "change_id",
        "phase",
        "session_id",
        "prompt_id",
        "request_id",
        "occurred_at",
        "model",
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_creation_tokens",
        "cost_usd",
        "duration_ms",
        "query_source",
        "status",
        "identity_quality",
        "attribution",
    ]
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        # Spreadsheet formula injection protection. Text identifiers stay literal.
        writer.writerow(
            {
                k: (
                    "'" + v
                    if isinstance(v, str)
                    and v.startswith(("=", "+", "-", "@", "\t", "\r"))
                    else v
                )
                for k, v in r.items()
            }
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="tokenlens-{source}.csv"'
        },
    )


class Reconcile(BaseModel):
    session_id: str = Field(max_length=160)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cache_read_tokens: int = Field(ge=0)
    cache_creation_tokens: int = Field(ge=0)
    note: str = Field(default="", max_length=500)


@app.post("/api/reconcile")
def reconcile(body: Reconcile, source: str = "real"):
    source_check(source)
    rs = store.rows(
        "SELECT * FROM requests WHERE source=? AND session_id=? AND status=?",
        (source, body.session_id, "success"),
    )
    keys = [
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_creation_tokens",
    ]
    observed = {k: sum(r[k] for r in rs) for k in keys}
    expected = {k: getattr(body, k) for k in keys}
    with store.lock, store.connect() as db:
        db.execute(
            "INSERT INTO reconciliations(source,session_id,created_at,observed,expected,note) VALUES(?,?,?,?,?,?)",
            (
                source,
                body.session_id,
                now(),
                json.dumps(observed),
                json.dumps(expected),
                body.note,
            ),
        )
    changed()
    return {
        "observed": observed,
        "expected": expected,
        "delta": {k: observed[k] - expected[k] for k in keys},
        "warning": "Compara la misma sesión, modelos y período. Esto no prueba facturación ni cobertura completa.",
    }


STATIC = ROOT / "frontend" / "static"
if STATIC.exists():
    app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")


@app.get("/")
def index():
    if not (STATIC / "index.html").exists():
        return JSONResponse(
            {"detail": "Frontend no compilado. Ejecuta: python pilot.py build"},
            status_code=503,
        )
    return FileResponse(STATIC / "index.html")
