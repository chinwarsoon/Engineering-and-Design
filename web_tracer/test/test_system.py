"""backend/tests/test_system.py — Phase 1 system-endpoint contract tests (T21).

Run from the project root: ``pytest test``. Single test source per AGENTS.md §6.1.
"""
from __future__ import annotations

import pathlib

import pytest
from fastapi.testclient import TestClient

from backend.web_server import app

client = TestClient(app)

# Reset the runtime .target marker between tests so resolve_base is deterministic.
_TNOTE = pathlib.Path(__file__).resolve().parents[1] / "output" / ".target"


@pytest.fixture(autouse=True)
def _reset_target():
    yield
    _TNOTE.write_text("")


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["schema_version"] == "1.0"
    assert body["version"] == "0.1.0"


def test_capabilities_shape():
    r = client.get("/api/capabilities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and data
    assert all({"name", "available", "version", "level", "message"} <= set(c) for c in data)
    # A missing required package would surface as FATAL here.
    assert any(c["level"] in ("OK", "WARN", "FATAL") for c in data)


def test_target_roundtrip(tmp_path: pathlib.Path):
    r = client.post("/api/target/set", json={"path": str(tmp_path)})
    assert r.status_code == 200
    assert r.json()["base"] == str(tmp_path)

    g = client.get("/api/target")
    assert g.status_code == 200
    assert g.json()["base"] == str(tmp_path)
    assert g.json()["source"] == "target_file"


def test_file_read_relative_to_target(tmp_path: pathlib.Path):
    client.post("/api/target/set", json={"path": str(tmp_path)})
    f = tmp_path / "demo.txt"
    f.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    r = client.post("/file/read", json={"path": "demo.txt"})
    assert r.status_code == 200
    assert r.json()["content"] == "alpha\nbeta\ngamma"

    # line range
    r2 = client.post("/file/read", json={"path": "demo.txt", "start": 2, "end": 2})
    assert r2.json()["content"] == "beta"


def test_file_read_escapes_are_rejected():
    # cwd base; an absolute path outside must be refused (PathEscapeError -> 403).
    r = client.post("/file/read", json={"path": "/etc/passwd"})
    assert r.status_code == 403
