"""Phase 2 browser module + endpoint tests (T22-T28).

Run from the project root: ``pytest test/test_browser.py``.
No real browser required — ``MockBrowserAdapter`` covers the abstraction, the six event
types, the user-action root, and the recorder round trip; the PlaywrightAdapter's span
builder is unit-tested directly. The backend routes use a factory override.
"""
from __future__ import annotations

import json
import pathlib

import pytest
from fastapi.testclient import TestClient

from engine.browser.base import Action, RecordConfig
from engine.browser.mock import MockBrowserAdapter
from engine.browser.playwright_adapter import PlaywrightAdapter
from engine.browser.traceparent import CorsProbe
from engine.schema.validate import validate_span
from backend.routes import browser as browser_routes
from backend.web_server import app

client = TestClient(app)
_TNOTE = pathlib.Path(__file__).resolve().parents[1] / "output" / ".target"


@pytest.fixture(autouse=True)
def _setup():
    browser_routes.set_tracer_factory(lambda: MockBrowserAdapter())
    browser_routes._SESSIONS.clear()
    # Avoid real network in the CORS probe during route tests.
    browser_routes.probe_cors = lambda url: CorsProbe(observed=False, allowed=True)  # type: ignore[assignment]
    yield
    browser_routes._SESSIONS.clear()
    browser_routes.set_tracer_factory(None)
    _TNOTE.write_text("")


def _types(spans):
    return {s["event_type"] for s in spans}


# ---- T22: abstraction is runnable by a mock adapter ----
def test_mock_adapter_six_event_types():
    a = MockBrowserAdapter()
    a.start(RecordConfig(url="http://app"))
    spans = a.stop()
    types = _types(spans)
    for t in ("navigation", "http_request", "http_response", "console", "error", "dom_event"):
        assert t in types, f"missing event type {t}"
    for s in spans:
        validate_span(s)  # every span is schema-valid


# ---- T25: user action is the trace root ----
def test_user_action_is_trace_root():
    a = MockBrowserAdapter()
    a.start(RecordConfig(url="http://app", actions=[Action(kind="click", selector="#submit")]))
    spans = a.stop()
    user = [s for s in spans if s["layer"] == "user"]
    assert user, "no layer=user root span"
    user_id = user[0]["span_id"]
    children = [s for s in spans if s.get("parent_span_id") == user_id]
    assert children, "no spans nested under the user root"


# ---- T23: PlaywrightAdapter._to_span validates for all six event types (no browser) ----
def test_playwright_adapter_to_span_validates():
    a = PlaywrightAdapter()
    samples = [
        dict(etype="navigation", name="http://x", layer="browser", kind="event", source={"file": "<page>"}),
        dict(etype="http_request", name="http://x/api", layer="http", kind="request",
             source={"file": "js.js"}, attributes={"http": {"method": "GET", "url": "http://x/api"}}),
        dict(etype="http_response", name="http://x/api", layer="http", kind="request",
             source={"file": "js.js"},
             attributes={"http": {"method": "GET", "url": "http://x/api", "status": 200}}),
        dict(etype="console", name="log", layer="browser", kind="event", source={"file": "<c>"},
             attributes={"text": "hi"}),
        dict(etype="error", name="pageerror", layer="browser", kind="event", source={"file": "<p>"},
             status="error", attributes={"message": "x"}),
        dict(etype="dom_event", name="screenshot", layer="browser", kind="event", source={"file": "<p>"},
             attributes={"screenshot": "x.png"}),
    ]
    for s in samples:
        span = a._to_span(start_ns=123, duration_ms=1.0, **s)
        validate_span(span)


# ---- T28: the five browser endpoints are usable ----
def test_routes_record_stop_trace_roundtrip():
    r = client.post("/browser/record/start", json={"url": "http://app"})
    assert r.status_code == 200
    run_id = r.json()["run_id"]
    assert "cors_probe" in r.json()

    s = client.post("/browser/record/stop", json={"run_id": run_id})
    assert s.status_code == 200
    assert s.json()["span_count"] > 0

    st = client.get("/browser/record/status", params={"run_id": run_id})
    assert st.status_code == 200
    assert st.json()["recording"] is False

    tr = client.get(f"/browser/trace/{run_id}")
    assert tr.status_code == 200
    body = tr.json()
    assert isinstance(body, list) and body


def test_routes_import_json():
    span = {
        "trace_id": "a" * 32, "span_id": "b" * 16, "parent_span_id": None,
        "layer": "browser", "event_type": "navigation", "name": "x", "kind": "event",
        "source": {"file": "f"}, "start_time_unix_ns": 1, "duration_ms": 1.0,
        "status": "ok", "confidence": 1.0,
        "correlation": {"method": "trace_id", "score": 1.0, "reason": None},
        "attributes": {}, "clock_offset_ms": 0.0,
        "collector": {"name": "n", "version": "v", "run_id": "r"},
    }
    files = {"file": ("trace.json", json.dumps([span]).encode(), "application/json")}
    r = client.post("/browser/import", files=files)
    assert r.status_code == 200
    assert r.json()["span_count"] == 1
