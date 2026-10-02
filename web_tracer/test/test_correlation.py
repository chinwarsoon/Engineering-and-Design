"""Phase 4 correlation + execution tree tests (T34-T38).

Covers the CorrelationEngine (primary + fallback), the six unmatched reasons, the
correlation report, the ExecutionTreeBuilder (including the workplan's example tree)
and the three REST endpoints. No browser and no JVM are needed: every span is built
with the shared ``make_span`` factory.

Run from the project root: ``pytest test/test_correlation.py``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from engine import config, ids, paths
from engine.browser.base import make_span
from engine.correlation import (
    CorrelationEngine,
    CorrelationInput,
    CorrelationMetrics,
    ExecutionTreeBuilder,
    FallbackMatcher,
    normalize_url,
)
from engine.correlation.engine import handler_spans, join_units
from engine.correlation.models import (
    REASON_CLOCK_SKEW,
    REASON_CORS_BLOCKED,
    REASON_MULTIPLE_CANDIDATES,
    REASON_NO_CANDIDATE,
    REASON_NO_TRACE_ID,
    REASON_OUT_OF_WINDOW,
)
from engine.schema.validate import validate_execution_tree
from backend.web_server import app

client = TestClient(app)

T0 = 1_759_145_553_482_000_000  # 2026-09-29T10:12:33.482Z


def ms(n: float) -> int:
    """A timestamp ``n`` milliseconds after T0, in nanoseconds."""
    return T0 + int(n * 1_000_000)


# ── span factories ───────────────────────────────────────────────────────────────
def browser_span(trace_id, span_id, parent, layer, etype, name, start_ms, dur, **kw):
    return make_span(
        trace_id=trace_id, span_id=span_id, parent_span_id=parent, layer=layer,
        event_type=etype, name=name, kind=kw.pop("kind", "event"),
        source=kw.pop("source", {"file": "static/index.html", "line": 88, "symbol": "#submit"}),
        start_time_unix_ns=ms(start_ms), duration_ms=dur, run_id=kw.pop("run_id", "run-test"),
        collector_name="playwright-adapter", clock_offset_ms=0.0,
        attributes=kw.pop("attributes", {}), **kw,
    )


def http_span(trace_id, span_id, parent, start_ms, dur, url="https://t/api/document",
              method="POST", **kw):
    attrs = {"http": {"method": method, "url": url, "status": 200}}
    attrs.update(kw.pop("attributes", {}))
    return make_span(
        trace_id=trace_id, span_id=span_id, parent_span_id=parent, layer="http",
        event_type="http_request", name=url, kind="request",
        source={"file": "static/js/document.js", "line": 145, "symbol": "fetch"},
        start_time_unix_ns=ms(start_ms), duration_ms=dur, run_id=kw.pop("run_id", "run-test"),
        collector_name="playwright-adapter", clock_offset_ms=0.0, attributes=attrs, **kw,
    )


def java_span(trace_id, span_id, parent, layer, etype, name, start_ms, dur, **kw):
    return make_span(
        trace_id=trace_id, span_id=span_id, parent_span_id=parent, layer=layer,
        event_type=etype, name=name, kind=kw.pop("kind", "method"),
        source=kw.pop("source", {"file": "com/example/doc/DocumentService.java", "line": 84,
                                 "symbol": name.split(".")[-1], "class_name": name.split(".")[0],
                                 "package": "com.example.doc"}),
        start_time_unix_ns=ms(start_ms), duration_ms=dur, run_id=kw.pop("run_id", "run-test"),
        collector_name="otlp-receiver", collector_version="0.1.0", clock_offset_ms=3.2,
        language="java", attributes=kw.pop("attributes", {}), **kw,
    )


def controller_span(trace_id, span_id, parent, start_ms, dur, route="/api/document",
                    method="POST", name="DocumentController.create"):
    return java_span(
        trace_id, span_id, parent, "java", "controller", name, start_ms, dur,
        kind="request",
        attributes={"http.method": method, "http.route": route,
                    "code.namespace": "com.example.doc.DocumentController"},
    )


# ── T34: primary correlation by trace_id ─────────────────────────────────────────
def test_primary_trace_id_correlation_rate_1():
    tid = ids.new_trace_id()
    browser = [
        browser_span(tid, "a" * 16, None, "user", "user_action", 'Click "Submit"', 0.0, 61.2),
        browser_span(tid, "b" * 16, "a" * 16, "browser", "js_function", "submitDocument", 1.1, 18.4),
        http_span(tid, "c" * 16, "b" * 16, 8.0, 42.1),
    ]
    java = [
        controller_span(tid, "d" * 16, "c" * 16, 12.3, 37.0),
        java_span(tid, "e" * 16, "d" * 16, "java", "service", "DocumentService.create", 13.0, 32.7),
        java_span(tid, "f" * 16, "e" * 16, "db", "sql", "INSERT INTO document", 30.0, 9.8, kind="statement"),
    ]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, run_id="r1"))

    assert res.rate == 1.0
    assert res.stats["matched"] == 1
    assert res.matches[0].method == "trace_id"
    assert res.matches[0].score == 1.0
    assert res.matches[0].java_span_id == "d" * 16
    # the java handler is stitched under the browser request span
    assert res.parent_overrides == {"d" * 16: "c" * 16}
    # children of a matched handler inherit "inferred"
    svc = next(s for s in res.java if s["span_id"] == "e" * 16)
    assert svc["correlation"]["method"] == "inferred"


def test_clock_normalisation_base_is_browser():
    tid = ids.new_trace_id()
    browser = [http_span(tid, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(tid, "d" * 16, "c" * 16, 12.3, 37.0)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))

    assert res.clock["base"] == "playwright-adapter"
    assert res.clock["offset_ms"]["playwright-adapter"] == 0.0
    # java collector reports +3.2 ms against the base, so its correction is -3.2
    assert res.clock["offset_ms"]["otlp-receiver"] == -3.2


def test_strategy_trace_id_only_disables_fallback():
    tid = ids.new_trace_id()
    browser = [http_span(tid, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span("f" * 32, "d" * 16, None, 12.3, 37.0)]  # different trace
    res = CorrelationEngine().correlate(
        CorrelationInput(browser=browser, java=java, strategy="trace_id")
    )
    assert res.rate == 0.0
    assert res.unmatched[0]["reason"] == REASON_NO_CANDIDATE


# ── T35: fallback URL + time window ──────────────────────────────────────────────
def test_fallback_unique_candidate_scores_08():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))

    assert res.rate == 1.0
    assert res.matches[0].method == "url_time_window"
    assert res.matches[0].score == 0.8
    assert res.matches[0].reason is None


def test_fallback_multiple_candidates_scores_06():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [
        controller_span(ids.new_trace_id(), "d" * 16, None, 10.0, 30.0),  # 2 ms after the request
        controller_span(ids.new_trace_id(), "e" * 16, None, 20.0, 30.0),  # 12 ms after it
    ]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))

    assert res.matches[0].score == 0.6
    assert res.matches[0].reason == REASON_MULTIPLE_CANDIDATES
    assert res.matches[0].java_span_id == "d" * 16  # nearest wins


def test_fallback_path_only_scores_04():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1, method="POST")]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0, method="GET")]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))

    assert res.matches[0].score == 0.4


def test_fallback_out_of_window():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 400.0, 37.0)]  # 392 ms late
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, window_ms=200))

    assert res.rate == 0.0
    assert res.unmatched[0]["reason"] == REASON_OUT_OF_WINDOW
    assert res.unmatched[0]["nearest_delta_ms"] > 200


def test_fallback_clock_skew_exceeded():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 5000.0, 37.0)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))

    assert res.unmatched[0]["reason"] == REASON_CLOCK_SKEW


def test_widened_window_matches():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 400.0, 37.0)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, window_ms=500))
    assert res.rate == 1.0


# ── T36: all six reasons reproducible ────────────────────────────────────────────
def test_reason_no_candidate():
    # a usable trace_id that no java span shares, and no URL match either
    browser = [http_span(ids.new_trace_id(), "c" * 16, "b" * 16, 8.0, 42.1, url="https://t/api/document")]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0, route="/api/other")]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))
    assert res.unmatched[0]["reason"] == REASON_NO_CANDIDATE


def test_reason_no_trace_id():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1, url="https://t/api/document")]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0, route="/api/other")]
    # force the fallback off so the "no usable trace_id" cause is what gets reported
    res = CorrelationEngine().correlate(
        CorrelationInput(browser=browser, java=java, strategy="url_time_window")
    )
    assert res.unmatched[0]["reason"] == REASON_NO_TRACE_ID


def test_reason_cors_preflight_blocked():
    browser = [
        http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1,
                  attributes={"preflight": {"observed": True, "allowed": False}})
    ]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java))
    assert res.unmatched[0]["reason"] == REASON_CORS_BLOCKED


def test_metrics_report_shape_and_all_six_reasons():
    """One request per reason, on its own URL so the scenarios cannot interfere."""
    tid = ids.new_trace_id()
    browser = [
        http_span(tid, "c0" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/document"),
        http_span(ids.new_trace_id(), "c1" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/slow"),
        http_span(ids.new_trace_id(), "c2" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/skew"),
        http_span(ids.new_trace_id(), "c3" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/nothing"),
        http_span(ids.new_trace_id(), "c4" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/cors",
                  attributes={"preflight": {"observed": True, "allowed": False}}),
        http_span(ids.new_trace_id(), "c5" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/multi"),
        http_span("0" * 32, "c6" + "0" * 14, "b" * 16, 8.0, 42.1, url="https://t/api/notid"),
    ]
    java = [
        controller_span(tid, "d0" + "0" * 14, "c0" + "0" * 14, 12.3, 37.0),          # trace_id match
        controller_span(ids.new_trace_id(), "d1" + "0" * 14, None, 400.0, 37.0, route="/api/slow"),
        controller_span(ids.new_trace_id(), "d2" + "0" * 14, None, 9000.0, 37.0, route="/api/skew"),
        controller_span(ids.new_trace_id(), "d4" + "0" * 14, None, 10.0, 37.0, route="/api/cors"),
        controller_span(ids.new_trace_id(), "d5" + "0" * 14, None, 10.0, 37.0, route="/api/multi"),
        controller_span(ids.new_trace_id(), "d6" + "0" * 14, None, 11.0, 37.0, route="/api/multi"),
    ]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, run_id="r"))
    report = CorrelationMetrics().report(res)

    reasons = report["unmatched_reasons"]
    assert reasons[REASON_OUT_OF_WINDOW] >= 1
    assert reasons[REASON_CLOCK_SKEW] >= 1
    assert reasons[REASON_NO_CANDIDATE] >= 1
    assert reasons[REASON_CORS_BLOCKED] == 1
    assert reasons[REASON_MULTIPLE_CANDIDATES] >= 1
    assert reasons[REASON_NO_TRACE_ID] >= 1
    assert set(report["unmatched_reasons"]) == {
        REASON_NO_CANDIDATE, REASON_MULTIPLE_CANDIDATES, REASON_CORS_BLOCKED,
        REASON_CLOCK_SKEW, REASON_NO_TRACE_ID, REASON_OUT_OF_WINDOW,
    }
    assert report["total"] == 7
    assert report["matched"] == 2
    assert report["rate"] == pytest.approx(2 / 7, abs=1e-4)
    assert report["by_method"]["trace_id"] == 1
    assert report["by_method"]["url_time_window"] == 1
    assert len(report["matched_pairs"]) == 2
    assert report["run_id"] == "r"


def test_report_notes_missing_java_stream():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=[], run_id="r"))
    report = CorrelationMetrics().report(res)
    assert "note" in report
    assert res.warnings


# ── URL normalisation ────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("https://t/api/document", "/api/document"),
        ("https://t/api/doc/123", "/api/doc/{id}"),
        ("https://t/api/doc/123?q=1#f", "/api/doc/{id}"),
        ("https://t/api/doc/8f3a1c2e-4b5d-6a7f-8f3a-1c2e4b5d6a7f", "/api/doc/{id}"),
        ("/api/document/", "/api/document"),
    ],
)
def test_normalize_url(raw, expected):
    assert normalize_url(raw) == expected


def test_handler_and_unit_selection():
    tid = ids.new_trace_id()
    browser = [browser_span(tid, "a" * 16, None, "user", "user_action", "click", 0.0, 10.0)]
    assert join_units(browser)[0]["span_id"] == "a" * 16  # no http layer → user roots

    java = [
        controller_span(tid, "d" * 16, None, 12.3, 37.0),
        java_span(tid, "e" * 16, "d" * 16, "java", "service", "Svc.x", 13.0, 30.0),
        java_span(tid, "f" * 16, "e" * 16, "db", "sql", "SELECT 1", 14.0, 5.0, kind="statement"),
    ]
    assert [s["span_id"] for s in handler_spans(java)] == ["d" * 16]


def test_fallback_matcher_batch_shape():
    browser = [http_span("0" * 32, "c" * 16, "b" * 16, 8.0, 42.1)]
    java = [controller_span(ids.new_trace_id(), "d" * 16, None, 12.3, 37.0)]
    matcher = FallbackMatcher(window_ms=200)
    matches = matcher.match(browser, java)
    assert len(matches) == 1 and matcher.failures == []


# ── T37: execution tree ──────────────────────────────────────────────────────────
def _example_run():
    """The workplan §8.3.2 example: user → browser → http → java → java → db."""
    tid = ids.new_trace_id()
    browser = [
        browser_span(tid, "a" * 16, None, "user", "user_action", 'Click "Submit"', 0.0, 61.2, kind="event"),
        browser_span(tid, "b" * 16, "a" * 16, "browser", "js_function", "submitDocument", 1.1, 18.4,
                     kind="function"),
        http_span(tid, "c" * 16, "b" * 16, 8.0, 42.1),
    ]
    java = [
        controller_span(tid, "d" * 16, "c" * 16, 12.3, 37.0, name="DocumentController.create"),
        java_span(tid, "e" * 16, "d" * 16, "java", "service", "DocumentService.create", 13.0, 32.7),
        java_span(tid, "f" * 16, "e" * 16, "db", "sql", "INSERT INTO document", 30.0, 9.8, kind="statement"),
    ]
    return tid, browser, java


def test_execution_tree_matches_workplan_example():
    tid, browser, java = _example_run()
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, run_id="run-x"))
    tree = ExecutionTreeBuilder().build(res.spans(), result=res, run_id="run-x")

    validate_execution_tree(tree)
    assert tree["trace_id"] == tid
    assert tree["run_id"] == "run-x"

    stats = tree["stats"]
    assert stats["node_count"] == 6
    assert stats["max_depth"] == 5
    assert stats["layers"] == {"user": 1, "browser": 1, "http": 1, "java": 2, "db": 1}
    assert stats["unmatched_count"] == 0
    assert stats["correlation_rate"] == 1.0
    assert stats["total_duration_ms"] == pytest.approx(61.2, abs=0.01)

    root = tree["root"]
    assert root["layer"] == "user" and root["start_offset_ms"] == 0.0
    http_node = root["children"][0]["children"][0]
    assert http_node["layer"] == "http"
    assert http_node["start_offset_ms"] == pytest.approx(8.0, abs=0.01)
    # the java handler nests under the browser request span (the stitch)
    assert http_node["children"][0]["layer"] == "java"
    assert http_node["children"][0]["name"] == "DocumentController.create"
    db_node = http_node["children"][0]["children"][0]["children"][0]
    assert db_node["layer"] == "db" and db_node["self_time_ms"] == pytest.approx(9.8, abs=0.01)


def test_execution_tree_self_time_excludes_children():
    tid, browser, java = _example_run()
    res = CorrelationEngine().correlate(CorrelationInput(browser=browser, java=java, run_id="run-x"))
    tree = ExecutionTreeBuilder().build(res.spans(), result=res, run_id="run-x")
    http_node = tree["root"]["children"][0]["children"][0]
    # 42.1 ms request, 37.0 ms of it spent in the java subtree
    assert http_node["self_time_ms"] == pytest.approx(5.1, abs=0.01)


def test_execution_tree_synthetic_root_for_orphans():
    tid = ids.new_trace_id()
    spans = [
        browser_span(tid, "a" * 16, None, "user", "user_action", "click-1", 0.0, 10.0),
        browser_span(ids.new_trace_id(), "b" * 16, None, "user", "user_action", "click-2", 5.0, 10.0),
    ]
    tree = ExecutionTreeBuilder().build(spans, run_id="run-orphan")
    validate_execution_tree(tree)
    assert tree["root"]["id"] == "synthetic:root"
    assert tree["root"]["layer"] == "user"
    assert tree["root"]["confidence"] == 0.3
    assert len(tree["root"]["children"]) == 2
    assert tree["stats"]["node_count"] == 3


def test_execution_tree_cycle_is_reported_not_hung():
    tid = ids.new_trace_id()
    spans = [
        browser_span(tid, "a" * 16, "b" * 16, "user", "user_action", "x", 0.0, 10.0),
        browser_span(tid, "b" * 16, "a" * 16, "browser", "js_function", "y", 1.0, 5.0),
    ]
    builder = ExecutionTreeBuilder()
    tree = builder.build(spans, run_id="run-cycle")
    validate_execution_tree(tree)
    assert any("cycle" in w for w in builder.warnings)


# ── T38: REST endpoints ──────────────────────────────────────────────────────────
@pytest.fixture
def run_workspace(tmp_path, monkeypatch):
    """Point path resolution at a temp dir so test artefacts never hit the repo."""
    monkeypatch.setattr(paths, "resolve_base", lambda: tmp_path)
    return tmp_path


def _write_run(base: Path, run_id: str, tid):
    d = base / "output" / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    browser = [
        browser_span(tid, "a" * 16, None, "user", "user_action", 'Click "Submit"', 0.0, 61.2, kind="event"),
        browser_span(tid, "b" * 16, "a" * 16, "browser", "js_function", "submitDocument", 1.1, 18.4,
                     kind="function"),
        http_span(tid, "c" * 16, "b" * 16, 8.0, 42.1),
    ]
    java = [
        controller_span(tid, "d" * 16, "c" * 16, 12.3, 37.0),
        java_span(tid, "e" * 16, "d" * 16, "java", "service", "DocumentService.create", 13.0, 32.7),
        java_span(tid, "f" * 16, "e" * 16, "db", "sql", "INSERT INTO document", 30.0, 9.8, kind="statement"),
    ]
    (d / "browser_trace.json").write_text(json.dumps(browser), encoding="utf-8")
    (d / "java_trace.json").write_text(json.dumps(java), encoding="utf-8")
    return d


def test_post_correlate_endpoint(run_workspace):
    tid = ids.new_trace_id()
    d = _write_run(run_workspace, "run-api", tid)

    r = client.post(config.CORRELATE, json={"run_id": "run-api"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["rate"] == 1.0
    assert body["matched"] == 1
    assert body["unmatched"] == []
    assert (d / "correlation_report.json").exists()
    assert (d / "execution_tree.json").exists()


def test_get_correlation_report_endpoint(run_workspace):
    tid = ids.new_trace_id()
    _write_run(run_workspace, "run-rep", tid)

    r = client.get(f"{config.CORRELATION_REPORT}/run-rep")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["run_id"] == "run-rep"
    assert body["total"] == 1 and body["matched"] == 1
    assert set(body["unmatched_reasons"]) >= {REASON_NO_CANDIDATE}


def test_get_execution_tree_endpoint(run_workspace):
    tid = ids.new_trace_id()
    _write_run(run_workspace, "run-tree", tid)

    r = client.get(f"{config.EXECUTION_TREE}/run-tree")
    assert r.status_code == 200, r.text
    tree = r.json()
    validate_execution_tree(tree)
    assert tree["stats"]["node_count"] == 6
    assert tree["stats"]["layers"]["java"] == 2

    # narrowed to one trace_id
    r2 = client.get(f"{config.EXECUTION_TREE}/run-tree", params={"trace_id": tid})
    assert r2.status_code == 200
    assert r2.json()["trace_id"] == tid

    r3 = client.get(f"{config.EXECUTION_TREE}/run-tree", params={"trace_id": "f" * 32})
    assert r3.status_code == 404


def test_correlate_unknown_run_404(run_workspace):
    r = client.post(config.CORRELATE, json={"run_id": "run-nope"})
    assert r.status_code == 404


def test_contract_paths_registered():
    assert config.CORRELATE in config.CONTRACT_PATHS
    assert config.CORRELATION_REPORT in config.CONTRACT_PATHS
    assert config.EXECUTION_TREE in config.CONTRACT_PATHS


# ── T39/T40: minimal dashboard ───────────────────────────────────────────────────
def test_dashboard_has_tree_tab_and_span_inspector():
    """The dashboard must ship the tree tab and the cross-layer inspector (T39/T40)."""
    html = (Path(__file__).resolve().parent.parent / "ui" / "static_dashboard.html").read_text(
        encoding="utf-8"
    )
    assert 'id="tab-tree"' in html                  # tree tab
    assert 'id="panel-tree"' in html                # tree panel
    assert 'id="tree-scroll"' in html               # render target
    assert "async function runCorrelate()" in html  # correlate action
    assert "async function loadExecutionTree()" in html
    assert "/execution_tree/" in html               # the URL it fetches

    # inspector: at least four cross-layer sections (T40)
    assert 'id="ins-panel-span"' in html
    sections = [s for s in ("1 · Span", "2 · Timing", "3 · Source location",
                            "4 · Initiator &amp; HTTP", "5 · Backend span stack")]
    assert all(s in html for s in sections)
    assert "function openSpanInspector(" in html
    # import → render → inspect (T39 acceptance)
    assert "async function importTrace(" in html
    assert "/browser/import" in html and "/java/import" in html


def test_dashboard_is_served_by_the_service():
    """The one-command entry point must actually reach the dashboard (T10/T39)."""
    page = client.get(config.DASHBOARD)
    assert page.status_code == 200
    assert "Execution Tree" in page.text

    css = client.get("/ui/web-tracer.css")
    assert css.status_code == 200

    # an asset name with a path separator must not escape ui/
    assert client.get("/ui/sub/x.css").status_code == 404
    assert client.get("/ui/nope.css").status_code == 404
