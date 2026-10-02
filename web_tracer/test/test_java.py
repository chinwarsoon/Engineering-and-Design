"""Phase 3 Java runtime tests (T29-T33).

Run from the project root: ``pytest test/test_java.py``.
No JVM required — OTLP JSON is decoded directly; protobuf is exercised via the
ProtobufUnavailable downgrade path (protobuf is an optional dep, not installed in CI).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from engine import ids
from engine.java import otlp_decode, strategies
from engine.java.otlp_receiver import OtlpReceiver
from engine.java.source_mapper import SourceMapper
from engine.schema.validate import validate_span
from backend.routes import java as java_routes
from backend.web_server import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_java_state():
    java_routes._RECEIVER = None
    java_routes._SESSIONS.clear()
    yield
    java_routes._RECEIVER = None
    java_routes._SESSIONS.clear()


# ── T29: OTLP decode (json + protobuf downgrade) ────────────────────────────────
def _otlp_json():
    tid = ids.new_trace_id()
    pid = ids.new_span_id()
    sid_ctrl = ids.new_span_id()
    sid_db = ids.new_span_id()
    return {
        "resourceSpans": [
            {
                "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "app"}}]},
                "scopeSpans": [
                    {
                        "scope": {"name": "io.opentelemetry.spring-webmvc"},
                        "spans": [
                            {
                                "traceId": tid, "spanId": sid_ctrl, "parentSpanId": pid,
                                "name": "POST /api/document", "kind": 2,
                                "startTimeUnixNano": "1000000000", "endTimeUnixNano": "1005000000",
                                "attributes": [
                                    {"key": "http.method", "value": {"stringValue": "POST"}},
                                    {"key": "http.route", "value": {"stringValue": "/api/document"}},
                                    {"key": "code.namespace", "value": {"stringValue": "com.app.DocumentController"}},
                                    {"key": "code.function", "value": {"stringValue": "create"}},
                                ],
                            },
                            {
                                "traceId": tid, "spanId": sid_db, "parentSpanId": sid_ctrl,
                                "name": "DocumentRepository.save", "kind": 1,
                                "startTimeUnixNano": "1005000000", "endTimeUnixNano": "1008000000",
                                "attributes": [
                                    {"key": "db.statement", "value": {"stringValue": "INSERT INTO document ..."}},
                                ],
                            },
                        ],
                    }
                ],
            }
        ]
    }


def test_decode_json_controller_and_db():
    spans = otlp_decode.decode(json.dumps(_otlp_json()).encode(), "application/json")
    assert len(spans) == 2
    by_name = {s["name"]: s for s in spans}
    ctrl = by_name["POST /api/document"]
    db = by_name["DocumentRepository.save"]
    assert ctrl["layer"] == "java" and ctrl["event_type"] == "controller"
    assert ctrl["source"]["class_name"] == "com.app.DocumentController"
    assert ctrl["parent_span_id"] is not None
    assert db["layer"] == "db" and db["event_type"] == "sql"
    assert db["parent_span_id"] == ctrl["span_id"]  # nested, not flat
    assert spans[0]["trace_id"] == spans[1]["trace_id"]
    for s in spans:
        validate_span(s)


def test_decode_protobuf_unavailable_raises():
    with pytest.raises(otlp_decode.ProtobufUnavailable):
        otlp_decode.decode(b"\x00", "application/x-protobuf")


def test_effective_channel_is_json_without_protobuf():
    r = OtlpReceiver(channel="auto")
    assert r.effective_channel() == "json"  # protobuf dep absent in CI -> downgrade
    r2 = OtlpReceiver(channel="json")
    assert r2.effective_channel() == "json"


# ── T29: receiver lifecycle + batch write ───────────────────────────────────────
def test_receiver_ingest_and_persist():
    r = OtlpReceiver()
    run_id = r.start()
    n = r.ingest(json.dumps(_otlp_json()).encode(), "application/json")
    assert n == 2
    st = r.status()
    assert st["running"] is True and st["span_count"] == 2 and st["channel"] == "json"
    spans = r.stop()
    assert len(spans) == 2
    import os
    from engine import paths
    assert (paths.run_dir(run_id) / "java_trace.json").exists()


# ── T31: instrumentation strategies ─────────────────────────────────────────────
def test_strategies_described():
    names = {s["name"] for s in strategies.describe_strategies()}
    assert names == {"framework_only", "spring_aop", "with_span", "bytebuddy"}


def test_select_strategy_auto_prefers_spring(tmp_path: Path):
    assert strategies.select_strategy("auto", None).name == "framework_only"  # no spring project
    (tmp_path / "pom.xml").write_text("<project><artifactId>x</artifactId><dependencies><dependency>"
                                       "<groupId>org.springframework.boot</groupId></dependency></dependencies></project>",
                                       encoding="utf-8")
    assert strategies.select_strategy("auto", tmp_path).name == "spring_aop"


# ── T32: source mapping (>=80% resolve) ─────────────────────────────────────────
_JAVA_SRC = """
package com.app;
public class DocumentController {
    public Document create(Document doc) {
        return save(doc);
    }
    public Document save(Document doc) {
        return doc;
    }
}
"""


def test_source_mapper_resolves_methods(tmp_path: Path):
    f = tmp_path / "DocumentController.java"
    f.write_text(_JAVA_SRC, encoding="utf-8")
    mapper = SourceMapper(tmp_path)
    span = {"layer": "java", "event_type": "method",
            "attributes": {"code.namespace": "com.app.DocumentController", "code.function": "create"},
            "source": {}}
    loc = mapper.map_span(span)
    assert loc is not None and loc.confidence == 0.9 and loc.start_line > 0
    # resolve rate over the methods present in the scanned source (create + save)
    spans = [
        span,
        {"layer": "java", "event_type": "method",
         "attributes": {"code.namespace": "com.app.DocumentController", "code.function": "save"}, "source": {}},
    ]
    assert mapper.resolve_rate(spans) >= 0.8


def test_source_mapper_runtime_evidence_is_1_0():
    mapper = SourceMapper()
    span = {"layer": "java", "event_type": "method",
            "attributes": {"code.filepath": "DocumentController.java", "code.lineno": 42,
                           "code.namespace": "com.app.DocumentController", "code.function": "create"},
            "source": {}}
    loc = mapper.map_span(span)
    assert loc is not None and loc.confidence == 1.0 and loc.start_line == 42


# ── T31: routes end-to-end ──────────────────────────────────────────────────────
def test_routes_receiver_flow():
    r = client.post("/java/receiver/start", json={"channel": "auto"})
    assert r.status_code == 200 and r.json()["channel"] == "json"
    run_id = r.json()["run_id"]

    body = json.dumps(_otlp_json()).encode()
    ingest = client.post("/v1/traces", json=json.loads(body))
    assert ingest.status_code == 200 and ingest.json()["accepted"] == 2

    stop = client.post("/java/receiver/stop")
    assert stop.status_code == 200 and stop.json()["span_count"] == 2

    tr = client.get(f"/java/trace/{run_id}")
    assert tr.status_code == 200 and len(tr.json()) == 2


def test_routes_instrumentation_config_and_import(tmp_path: Path):
    (tmp_path / "pom.xml").write_text("<project><dependency><groupId>org.springframework.boot</groupId></dependency></project>",
                                       encoding="utf-8")
    cfg = client.post("/java/instrumentation/config", json={"preference": "auto", "project_path": str(tmp_path)})
    assert cfg.status_code == 200
    body = cfg.json()
    assert body["selected"] == "spring_aop"
    assert body["nested_ok"] is True
    assert body["snippets"] and body["snippets"][0]["content"]
    assert body["cors"]["backend_allows_traceparent"] is True

    # import a pre-decoded SpanEvent[] json
    payload = json.dumps([{
        "trace_id": "a" * 32, "span_id": "b" * 16, "parent_span_id": None,
        "layer": "java", "event_type": "controller", "name": "x", "kind": "method",
        "source": {"file": "f", "class_name": "com.app.X"}, "start_time_unix_ns": 1, "duration_ms": 1.0,
        "status": "ok", "confidence": 1.0,
        "correlation": {"method": "trace_id", "score": 1.0, "reason": None},
        "attributes": {}, "clock_offset_ms": 0.0,
        "collector": {"name": "n", "version": "v", "run_id": "r"},
    }]).encode()
    imp = client.post("/java/import", files={"file": ("java_trace.json", payload, "application/json")})
    assert imp.status_code == 200 and imp.json()["span_count"] == 1
