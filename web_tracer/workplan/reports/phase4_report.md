# Phase 4 Report — Correlation, Execution Tree, Minimal Dashboard

| Field | Value |
|---|---|
| **Project** | Web Application Tracer (abbreviation `web_tracer`) |
| **Workplan** | `WP-WEB-TRACER-001` r4, §10.4 |
| **Phase** | P4 — Correlation and execution tree |
| **Tasks** | T34, T35, T36, T37, T38, T39, T40 |
| **Contracts** | WT-30 (correlation), WT-31 (ExecutionTree), WT-32, WT-33 |
| **Date** | 2026-10-02 |
| **Author** | AI assistant |
| **Governance** | AGENTS.md §5.6 (test report per phase), §5.4 (log everything) |

---

## 1. Scope and deliverables

| Task | Deliverable | Status |
|---|---|---|
| T34 | `engine/correlation/engine.py` — clock normalisation + primary `trace_id` join | done |
| T35 | `engine/correlation/fallback.py` — URL + time-window matching | done |
| T36 | `engine/correlation/metrics.py` + `correlation_report.json` | done |
| T37 | `engine/correlation/execution_tree.py` + `execution_tree.json` | done |
| T38 | `backend/routes/correlation.py` — three endpoints | done |
| T39 | Execution tree tab in `ui/static_dashboard.html` | done |
| T40 | Span inspector, six cross-layer sections | done |

Supporting files: `engine/correlation/models.py` (shared vocabulary + dataclasses),
`engine/config.py` (five new contract constants: `/correlate`, `/correlation/report`,
`/execution_tree`, `/`, `/ui`), `backend/web_server.py` (router),
`ui/web-tracer.css` (layer colour band + tree styles), `ui/code-tracer.css` (shared design
system, copied as planned in §7.2), `backend/routes/system.py` (serves the page and its
assets), `scripts/check_contracts.py`.

Beyond the frozen task list, two pre-existing gaps had to be closed for T39 to work end to
end: the dashboard was never served (so `launch.py` opened `/` on a 404) and its stylesheet
was missing from `ui/`. Both are fixed and recorded as U018.

---

## 2. Milestone verification

| # | Milestone (§10.4) | Result |
|---|---|---|
| M1 | Primary correlation ≥ 95 % on the target app | **1.0 (100 %)** on the synthetic end-to-end fixture. Not yet measured on the real target — no recorded run of the target application exists in this repository; M1 is re-measured at the first real capture. |
| M2 | Fallback correlation reproducible | **Pass.** Unique candidate 0.8, ambiguous 0.6, path-only 0.4, plus `out_of_window`, `clock_skew_exceeded` and a widened-window success — each covered by a test. |
| M3 | Metrics report with reason breakdown | **Pass.** All six reasons are produced by one scenario each in `test_metrics_report_shape_and_all_six_reasons`. |
| M4 | `ExecutionTreeBuilder` produces the proposal's example tree | **Pass.** 6 nodes, `max_depth` 5, layers `{user:1, browser:1, http:1, java:2, db:1}`, `unmatched_count` 0, `correlation_rate` 1.0, total 61.2 ms — identical to workplan §8.3.2. |
| M5 | Dashboard renders the tree | **Pass.** Served over HTTP (`GET /` → 200, `GET /ui/web-tracer.css` → 200), markup/behaviour asserted, JS syntax-checked, and the full `POST /correlate` → `GET /execution_tree/{run_id}` round trip executed against a live `uvicorn` instance (output in §3.1). A headless-browser render check is still pending (Phase 7). |

---

## 3. Test execution

```
pytest test/             → 58 passed
scripts/check_contracts.py → CONTRACT OK: 23 backend route(s), 23 contract path(s);
                             frontend fetches consistent.
node --check (dashboard) → JS SYNTAX OK
uvicorn smoke            → GET / 200 (80 KB), GET /ui/web-tracer.css 200,
                           GET /ui/code-tracer.css 200, GET /health 200
```

### 3.1 End-to-end run over HTTP (fabricated six-span run)

```
POST /correlate {"run_id":"run-20260929-101233"}
  → {"rate": 1.0, "matched": 1, "total": 1, "unmatched": []}

GET /execution_tree/run-20260929-101233
  trace_id 8f3a1c2e4b5d6a7f8f3a1c2e4b5d6a7f
  clock    {"base": "playwright-adapter",
            "offset_ms": {"playwright-adapter": 0.0, "otlp-receiver": -3.2}}
  stats    {"node_count": 6, "max_depth": 5, "total_duration_ms": 61.2,
            "layers": {"browser":1,"db":1,"http":1,"java":2,"user":1},
            "unmatched_count": 0, "correlation_rate": 1.0}
  chain    user:Click "Submit"        +0.0 ms  61.2 ms  self 42.8 ms
           browser:submitDocument     +1.1 ms  18.4 ms  self  0.0 ms
           http:https://t/api/document +8.0 ms  42.1 ms  self  5.1 ms
           java:DocumentController.create +9.1 ms 37.0 ms self  4.3 ms
           java:DocumentService.create    +9.8 ms 32.7 ms self 22.9 ms
           db:INSERT INTO document   +26.8 ms   9.8 ms  self  9.8 ms

GET /correlation/report/run-20260929-101233
  rate 1.0 · by_method {"trace_id": 1, "url_time_window": 0, "inferred": 0, "unmatched": 0}
```

`DocumentService.create` carries 22.9 ms of self time — this is exactly the answer the
project exists to give ("where did the time actually go?").

`test/test_correlation.py` adds 31 tests:

* T34 — primary join, confidence 1.0, `parent_overrides` stitch, `inferred` inheritance,
  clock normalisation (`clock.offset_ms` = `{"playwright-adapter": 0.0, "otlp-receiver": -3.2}`),
  `strategy="trace_id"` disables the fallback.
* T35 — 0.8 / 0.6 / 0.4 tiers, out-of-window, clock-skew, widened window, URL normalisation.
* T36 — every one of the six reasons, report shape, missing-Java-stream note.
* T37 — the workplan example tree, `self_time_ms` excluding children, synthetic root,
  parent-cycle guard.
* T38 — `POST /correlate`, `GET /correlation/report/{run_id}`, `GET /execution_tree/{run_id}`
  (including the 404 paths), contract registration.
* T39/T40 — dashboard ships the tree tab, the panel, and the inspector sections.

---

## 4. Design decisions taken in this phase

1. **Clock base is the browser collector.** Each collector's offset is the median of its
   spans' `clock_offset_ms`; the correction applied to a collector is
   `offset − base_offset`, and the tree records the inverse in `clock.offset_ms`, matching
   the worked example in §8.3.2 (`{"browser": 0.0, "java": -3.2}`).
2. **`inferred` is the fourth method.** A Java span in a trace whose handler was matched is
   joined by inheritance, not by a direct comparison — it is marked `inferred` (workplan
   §8.3.1 allows `trace_id | url_time_window | inferred | unmatched`).
3. **Fallback never returns 1.0.** A URL+time match is a guess and is scored 0.8 / 0.6 / 0.4.
4. **Separate run ids are first-class.** The browser recorder and the Java receiver each
   issue their own `run_id`, so `/correlate` accepts optional `browser_run_id` /
   `java_run_id` overrides; when omitted both traces are looked up under `run_id`.
5. **Nothing is silently dropped.** Unmatched requests carry a reason, empty Java streams
   produce a `note` plus a warning, and parent cycles are reported and broken.
6. **The clock correction is applied to `start_offset_ms`.** A Java span stamped 12.3 ms on
   a clock that is 3.2 ms ahead of the browser appears at `+9.1 ms` on the shared timeline.
   The worked example in §8.3.2 keeps the raw 12.3 ms next to an offset of `−3.2`; this
   implementation is internally consistent (offset reported *and* applied), so the tree is a
   single honest timeline.

---

## 5. Known limitations

* **M1 is not yet measured on the real target.** The ≥ 95 % gate needs a recorded run of the
  target application (browser + OTel agent); the engine is verified on fixtures only.
* **The dashboard is verified structurally, not visually.** The page and its assets are
  served (HTTP 200) and the tree rendering, the layer chips and the inspector are asserted in
  the HTML/JS and syntax-checked; no headless browser render was performed in this phase
  (a Playwright UI check is a candidate for Phase 7).
* **A very wide tree will need virtualised rendering** — already noted as a potential future
  issue in §10.4; deferred to Phase 7 (T51).
* **Phase 0's Go/No-Go gate (T19/T20)** was executed only as a spike; the Phase 4 engine
  supersedes the minimal P0 correlation code and P0's status remains to be reconciled.
* **Pre-existing test artefact leak (not introduced here).** `web_tracer/output/runs/`
  holds 104 untracked run folders written by earlier phases' tests, which contradicts
  AGENTS.md §6.1 ("test artefacts must not leak to the repository root"). Phase 4 tests
  write only into `tmp_path` — verified: running `test/test_correlation.py` changes the
  folder count by 0. The older tests should be migrated to `tempfile` / `test_output/`
  in a dedicated housekeeping task.

---

## 6. Revision history

| Revision | Date | Author | Summary |
|---|---|---|---|
| r0 | 2026-10-02 | AI assistant | Phase 4 report created: T34–T40 deliverables, M1–M5 verification, test execution, design decisions, limitations |
| r1 | 2026-10-02 | AI assistant | Added the live end-to-end HTTP run (§3.1), the dashboard/asset serving fix (U018), the clock-correction design decision (§4.6) and the updated counts (58 pytest, 23 routes) |
