#!/usr/bin/env python3
"""Cross-platform local lifecycle and safe Claude settings installer."""

import argparse
import hashlib
import json
import os
import secrets
import shlex
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.getenv("TOKENLENS_DATA_DIR", str(ROOT / "data"))).resolve()
PY = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def config():
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        DATA.chmod(0o700)
    except OSError:
        pass
    path = DATA / "config.json"
    if not path.exists():
        save(
            path,
            {
                "ingest_token": secrets.token_urlsafe(32),
                "endpoint": "http://127.0.0.1:4318",
            },
        )
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tokenlens-tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        tmp.chmod(0o600)
    except OSError:
        pass
    tmp.replace(path)


def setup():
    if not PY.exists():
        print("Creando entorno Python local…", flush=True)
        venv.EnvBuilder(with_pip=True).create(ROOT / ".venv")
    subprocess.run(
        [str(PY), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )


def load_settings(path):
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("Se esperaba objeto JSON")
        return obj
    except Exception as exc:
        raise RuntimeError(f"No se modifica {path}: JSON inválido. {exc}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def install(args):
    # No API credentials or Claude OAuth tokens are requested or extracted.
    c = config()
    c["endpoint"] = f"http://127.0.0.1:{args.port}"
    save(DATA / "config.json", c)
    user = Path(args.settings).expanduser().resolve()
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise RuntimeError("La carpeta del proyecto no existe.")
    target = project / ".claude" / "settings.local.json"
    if user == target.resolve():
        raise RuntimeError(
            "Settings de usuario y proyecto deben ser archivos distintos."
        )
    if not 1024 <= args.port <= 65535:
        raise RuntimeError("Puerto fuera de rango.")
    originals = {str(user): load_settings(user), str(target): load_settings(target)}
    updates = json.loads(json.dumps(originals))
    env = updates[str(user)].setdefault("env", {})
    endpoint = c["endpoint"]
    desired = {
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_LOGS_EXPORTER": "otlp",
        "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
        "OTEL_EXPORTER_OTLP_ENDPOINT": endpoint,
        "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer " + c["ingest_token"],
        "OTEL_METRIC_EXPORT_INTERVAL": "10000",
        "OTEL_LOGS_EXPORT_INTERVAL": "1000",
        "OTEL_METRICS_INCLUDE_SESSION_ID": "true",
        "OTEL_LOG_USER_PROMPTS": "0",
        "OTEL_LOG_ASSISTANT_RESPONSES": "0",
        "OTEL_LOG_TOOL_DETAILS": "0",
        "OTEL_LOG_TOOL_CONTENT": "0",
        "OTEL_LOG_RAW_API_BODIES": "0",
    }
    conflicts = {
        k: v
        for k, v in env.items()
        if (k in desired and v != desired[k])
        or k.startswith("OTEL_EXPORTER_OTLP_")
        or k
        in (
            "BETA_TRACING_ENDPOINT",
            "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA",
            "ENABLE_ENHANCED_TELEMETRY_BETA",
            "ENABLE_BETA_TRACING_DETAILED",
        )
    }
    # Existing endpoints/headers could redirect a signal or sensitive content.
    if conflicts and not args.replace_telemetry:
        print(
            "Existe configuración de telemetría. No se sobrescribe sin consentimiento."
        )
        print("Claves en conflicto:", ", ".join(conflicts))
        print("Revisa los settings y repite con --replace-telemetry si corresponde.")
        return 2
    for key in list(env):
        if key.startswith("OTEL_EXPORTER_OTLP_") or key in (
            "BETA_TRACING_ENDPOINT",
            "ENABLE_BETA_TRACING_DETAILED",
        ):
            del env[key]
    env.update(desired)
    env.update(
        {
            "OTEL_TRACES_EXPORTER": "none",
            "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "0",
            "ENABLE_ENHANCED_TELEMETRY_BETA": "0",
        }
    )
    executable = str(PY) if PY.exists() else sys.executable
    command_parts = [
        executable,
        str(ROOT / "scripts" / "hook_agent.py"),
        "--data",
        str(DATA),
        "--project",
        str(project),
    ]
    command = (
        subprocess.list2cmdline(command_parts)
        if os.name == "nt"
        else shlex.join(command_parts)
    )
    hooks = updates[str(target)].setdefault("hooks", {})
    for event in (
        "SessionStart",
        "SessionEnd",
        "UserPromptSubmit",
        "Stop",
        "StopFailure",
    ):
        entries = hooks.setdefault(event, [])
        entries[:] = [
            x
            for x in entries
            if not any(
                "hook_agent.py" in h.get("command", "") for h in x.get("hooks", [])
            )
        ]
        entries.append(
            {"hooks": [{"type": "command", "command": command, "timeout": 3}]}
        )
    record = {"created_at": time.time(), "project": str(project), "files": []}
    backupdir = DATA / "backups" / str(time.time_ns())
    try:
        for path_s, obj in updates.items():
            path = Path(path_s)
            existed = path.exists()
            backup = backupdir / (
                hashlib.sha256(path_s.encode()).hexdigest()[:12] + ".json"
            )
            # Exact original bytes, not a rewritten copy of the settings.
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(path.read_bytes() if existed else b"{}\n")
            try:
                backup.chmod(0o600)
            except OSError:
                pass
            save(path, obj)
            record["files"].append(
                {
                    "path": path_s,
                    "backup": str(backup),
                    "existed": existed,
                    "installed_hash": sha(path),
                }
            )
        installs = DATA / "installations.json"
        history = json.loads(installs.read_text()) if installs.exists() else []
        history.append(record)
        save(installs, history)
    except Exception:
        # Best-effort rollback if one of the writes failed. Backups remain available.
        for f in reversed(record["files"]):
            try:
                path = Path(f["path"])
                if f["existed"]:
                    path.write_bytes(Path(f["backup"]).read_bytes())
                else:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
        raise RuntimeError(
            f"Instalación incompleta; rollback intentado. Revisa los respaldos en {backupdir}."
        )
    print(f"Instalado. Receptor: {endpoint}; hooks limitados a {project}")
    print(f"Respaldos: {backupdir}")
    print(
        "IMPORTANTE: la telemetría de usuario afecta otras sesiones Claude Code mientras esté activa."
    )
    print(
        "Los hooks están limitados al proyecto. Consumos de otras sesiones quedarán sin atribuir."
    )
    print(
        "Políticas administradas pueden prevalecer; no se modifican. Reinicia completamente VS Code."
    )
    return 0


def restore(args):
    path = DATA / "installations.json"
    history = json.loads(path.read_text()) if path.exists() else []
    if not history:
        raise RuntimeError("No hay una instalación que restaurar.")
    record = history[-1]
    changed = [
        f["path"]
        for f in record["files"]
        if sha(Path(f["path"])) != f["installed_hash"]
    ]
    if changed and not args.force:
        raise RuntimeError(
            "Los settings cambiaron después de instalar. No se restauran automáticamente: "
            + ", ".join(changed)
            + ". Compara el respaldo o usa restore --force bajo tu responsabilidad."
        )
    for f in record["files"]:
        dest = Path(f["path"])
        if f["existed"]:
            dest.write_bytes(Path(f["backup"]).read_bytes())
        else:
            dest.unlink(missing_ok=True)
    history.pop()
    save(path, history)
    print(
        "Configuración anterior restaurada. Reinicia VS Code. Datos locales conservados."
    )


def main():
    p = argparse.ArgumentParser(
        description="TokenLens: piloto local de consumo Claude Code / OpenSpec"
    )
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("setup", help="Instalar dependencias Python en .venv")
    sub.add_parser("build", help="Compilar React (requiere Node 20+)")
    run = sub.add_parser("run", help="Ejecutar un único servidor local")
    run.add_argument("--port", type=int, default=4318)
    ini = sub.add_parser("init", help="Respaldar y configurar Claude Code")
    ini.add_argument("--project", required=True)
    ini.add_argument(
        "--settings", default=str(Path.home() / ".claude" / "settings.json")
    )
    ini.add_argument("--port", type=int, default=4318)
    ini.add_argument("--replace-telemetry", action="store_true")
    res = sub.add_parser("restore", help="Restaurar última configuración instalada")
    res.add_argument("--force", action="store_true")
    sub.add_parser("flush", help="Reenviar hooks de la cola local")
    sub.add_parser("test", help="Ejecutar suite automatizada")
    args = p.parse_args()
    try:
        if args.action == "setup":
            setup()
        elif args.action == "build":
            npm = "npm.cmd" if os.name == "nt" else "npm"
            subprocess.run([npm, "ci"], cwd=ROOT / "frontend", check=True)
            subprocess.run([npm, "run", "build"], cwd=ROOT / "frontend", check=True)
        elif args.action == "init":
            return install(args)
        elif args.action == "restore":
            restore(args)
        elif args.action == "flush":
            from scripts.hook_agent import drain

            print("Hooks enviados:", drain(DATA, 1000))
        elif args.action == "test":
            if not PY.exists():
                setup()
            return subprocess.run(
                [
                    str(PY),
                    "-m",
                    "pytest",
                    "-q",
                    "tests",
                    "--cov=backend",
                    "--cov-report=term",
                    "--cov-fail-under=80",
                ],
                cwd=ROOT,
            ).returncode
        elif args.action == "run":
            if not 1024 <= args.port <= 65535:
                raise RuntimeError("Puerto fuera de rango.")
            if not PY.exists():
                setup()
            c = config()
            c["endpoint"] = f"http://127.0.0.1:{args.port}"
            save(DATA / "config.json", c)
            print(f"TokenLens local → http://127.0.0.1:{args.port}", flush=True)
            print(
                "Sin llamadas LLM ni servicios externos. Ctrl+C para detener.",
                flush=True,
            )
            env = {**os.environ, "TOKENLENS_DATA_DIR": str(DATA)}
            env.pop("TOKENLENS_PREVIEW", None)
            return subprocess.call(
                [
                    str(PY),
                    "-m",
                    "uvicorn",
                    "backend.app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(args.port),
                    "--no-access-log",
                ],
                cwd=ROOT,
                env=env,
            )
        return 0
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
