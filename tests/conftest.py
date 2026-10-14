import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["TOKENLENS_DATA_DIR"] = tempfile.mkdtemp(prefix="tokenlens-tests-")
os.environ.pop("TOKENLENS_PREVIEW", None)

import pytest
from fastapi.testclient import TestClient
from backend import app as mod
from backend.store import Store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "store", Store(tmp_path / "test.sqlite3"))
    monkeypatch.setattr(mod, "INGEST_TOKEN", "test-token")
    with TestClient(mod.app) as c:
        yield c


@pytest.fixture
def auth():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def ledger(tmp_path):
    return Store(tmp_path / "domain.sqlite3")
