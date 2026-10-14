import importlib.util
import json
from argparse import Namespace
from pathlib import Path
import pytest

SPEC = importlib.util.spec_from_file_location(
    "pilot", Path(__file__).resolve().parents[1] / "pilot.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


@pytest.fixture
def settings(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "DATA", tmp_path / "data")
    repo = tmp_path / "repo"
    repo.mkdir()
    user = tmp_path / "user-settings.json"
    user.write_text('{"permissions": {"allow": ["Read"]}}\n')
    return (
        Namespace(
            project=str(repo), settings=str(user), port=4318, replace_telemetry=False
        ),
        user,
        repo,
    )


def test_install_preserves_other_settings_and_restore_exact_bytes(settings):
    args, user, repo = settings
    original = user.read_bytes()
    assert pilot.install(args) == 0
    obj = json.loads(user.read_text())
    assert obj["permissions"]["allow"] == ["Read"]
    assert obj["env"]["OTEL_LOG_USER_PROMPTS"] == "0"
    assert obj["env"]["OTEL_EXPORTER_OTLP_PROTOCOL"] == "http/protobuf"
    local = repo / ".claude" / "settings.local.json"
    assert "UserPromptSubmit" in json.loads(local.read_text())["hooks"]
    pilot.restore(Namespace(force=False))
    assert user.read_bytes() == original and not local.exists()


def test_conflicting_telemetry_requires_consent(settings):
    args, user, repo = settings
    user.write_text(
        '{"env":{"OTEL_EXPORTER_OTLP_ENDPOINT":"https://existing.example"}}'
    )
    original = user.read_bytes()
    assert pilot.install(args) == 2
    assert user.read_bytes() == original


def test_restore_refuses_to_overwrite_new_edits(settings):
    args, user, repo = settings
    pilot.install(args)
    obj = json.loads(user.read_text())
    obj["model"] = "my-model"
    user.write_text(json.dumps(obj))
    with pytest.raises(RuntimeError, match="cambiaron"):
        pilot.restore(Namespace(force=False))


def test_invalid_json_not_modified(settings):
    args, user, repo = settings
    user.write_text("NOT JSON")
    with pytest.raises(RuntimeError, match="JSON inválido"):
        pilot.install(args)
    assert user.read_text() == "NOT JSON"


def test_partial_install_attempts_rollback(settings, monkeypatch):
    args, user, repo = settings
    original = user.read_bytes()
    real_save = pilot.save

    def fail_project(path, data):
        if path.name == "settings.local.json":
            raise PermissionError("readonly")
        return real_save(path, data)

    monkeypatch.setattr(pilot, "save", fail_project)
    with pytest.raises(RuntimeError, match="rollback"):
        pilot.install(args)
    assert user.read_bytes() == original
