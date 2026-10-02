"""Phase 2 recorder tests: persist / zip / import round trip (T22/T27)."""
from __future__ import annotations

import json

from engine.browser.base import RecordConfig
from engine.browser.mock import MockBrowserAdapter
from engine.browser.recorder import Recorder
from engine import paths


def _valid_span():
    return {
        "trace_id": "a" * 32, "span_id": "b" * 16, "parent_span_id": None,
        "layer": "browser", "event_type": "navigation", "name": "x", "kind": "event",
        "source": {"file": "f"}, "start_time_unix_ns": 1, "duration_ms": 1.0,
        "status": "ok", "confidence": 1.0,
        "correlation": {"method": "trace_id", "score": 1.0, "reason": None},
        "attributes": {}, "clock_offset_ms": 0.0,
        "collector": {"name": "n", "version": "v", "run_id": "r"},
    }


def test_persist_and_read():
    a = MockBrowserAdapter()
    a.start(RecordConfig(url="http://app"))
    spans = a.stop()
    rec = Recorder(None)
    path = rec.persist(a._run_id, spans)
    assert path.exists()
    assert len(json.loads(path.read_text())) == len(spans)


def test_zip_roundtrip():
    a = MockBrowserAdapter()
    a.start(RecordConfig(url="http://app"))
    spans = a.stop()
    rec = Recorder(None)
    rec.persist(a._run_id, spans)
    zp = rec.package(a._run_id)
    assert zp.exists()
    new_id = rec.import_zip(zp)
    imported = json.loads(paths.run_dir(new_id).joinpath("browser_trace.json").read_text())
    assert len(imported) == len(spans)


def test_import_payload_json():
    spans = [_valid_span()]
    rec = Recorder(None)
    run_id, n = rec.import_payload("t.json", json.dumps(spans).encode())
    assert n == 1
    assert (paths.run_dir(run_id) / "browser_trace.json").exists()
