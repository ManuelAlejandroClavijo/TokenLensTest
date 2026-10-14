import io
import json
import sys
from scripts import hook_agent as h


def prepare(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "config.json").write_text(
        json.dumps({"ingest_token": "local-only", "endpoint": "http://127.0.0.1:4318"})
    )
    queue = data / "outbox"
    queue.mkdir()
    return data, queue


def test_outbox_removed_only_after_success(tmp_path, monkeypatch):
    data, queue = prepare(tmp_path)
    (queue / "1.json").write_text('{"event_id":"unique-id"}')

    class OK:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(h, "urlopen", lambda req, timeout: OK())
    assert h.drain(data) == 1
    assert not list(queue.glob("*.json"))


def test_receiver_failure_keeps_outbox_and_removes_lock(tmp_path, monkeypatch):
    data, queue = prepare(tmp_path)
    (queue / "1.json").write_text('{"event_id":"unique-id"}')

    def fail(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(h, "urlopen", fail)
    assert h.drain(data) == 0
    assert (queue / "1.json").exists()
    assert not (queue / ".drain.lock").exists()


def test_competing_drain_does_not_take_lock(tmp_path):
    data, queue = prepare(tmp_path)
    (queue / ".drain.lock").write_text("locked")
    assert h.drain(data) == 0


def test_hook_main_only_spools_metadata(tmp_path, monkeypatch):
    data, queue = prepare(tmp_path)
    secret = "NEVER_SPOOL_THIS_PROMPT"
    monkeypatch.setattr(
        sys, "argv", ["hook_agent.py", "--data", str(data), "--project", str(tmp_path)]
    )
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            json.dumps(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "s1",
                    "prompt_id": "p1",
                    "cwd": str(tmp_path),
                    "prompt": "/opsx:apply " + secret,
                }
            )
        ),
    )
    monkeypatch.setattr(h, "drain", lambda *args: 0)
    assert h.main() == 0
    payload = list(queue.glob("*.json"))[0].read_text()
    assert secret not in payload
    assert json.loads(payload)["phase_hint"] == "apply"
