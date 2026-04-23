# Code Tracer — Test Log

## Instructions
1. Always log new test results immediately after completion.
2. Add a timestamp at the beginning of each log entry.
3. Summarize results and link to issue log where applicable.

---

# Section 2. Test Log Entries

*(none — see dcc/Log/test_log.md for pre-migration history)*

## 2026-05-01

### Phase R8 — Single-Port Mode End-to-End Test

**Method:** `python engine/launch.py <target>` from `code_tracer/` root, browser opened automatically.

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | Single process starts | PASS | Only uvicorn on port 8000, no port 5000 process |
| T2 | `GET /` serves dashboard | PASS | `http://localhost:8000` loads `static_dashboard.html` |
| T3 | `GET /ui/code-tracer.css` | PASS | CSS loads, dashboard fully styled |
| T4 | `GET /health` | PASS | `status=healthy` |
| T5 | `/static/analyze` | PASS | Analysis runs, call graph rendered |
| T6 | `/file/read` source viewer | PASS | Source code loads in inspector |
| T7 | Browser auto-opens | PASS | Opens after health-check confirms backend ready |

**Final result:** 7/7 PASS
- Confirms Phase R8 complete. Single port 8000 serves both API and dashboard.
- Related: [Issue #CT-14](issue_log.md#issue-CT-14), [Issue #CT-15](issue_log.md#issue-CT-15)

---

## 2026-04-21 23:15:00

### UI: Sidebar & Activity Bar Verification

**Method:** Manual verification of sidebar interaction and panel state.

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | Load Icon Presence | PASS | `📥` is the first icon in the activity bar. |
| T2 | Load Panel Toggle | PASS | Clicking `📥` toggles the dedicated "Load Project" panel. |
| T3 | Controls Cleanup | PASS | "Load" section no longer appears in "Analysis Controls" panel. |
| T4 | Default State | PASS | "Load Project" panel is active on startup. |

**Final result:** 4/4 PASS
- Confirms successful implementation of CT-08.

---

## 2026-04-21 23:00:00

### UI: Title Bar Aesthetic Verification

**Method:** Visual inspection of header components.

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | Logo Divider | PASS | No vertical line between icon/name and rest of bar. |
| T2 | Action Button Borders | PASS | Theme picker and other buttons show no borders. |
| T3 | Global Reset Impact | PASS | No regressions in title bar layout or alignment. |

**Final result:** 3/3 PASS
- Confirms successful implementation of CT-07.

---

## 2026-04-21 22:15:00

### UX: Flow Tree & File Selection Test

**Method:** Manual browser interaction simulation

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | Click Function in Tree | PASS | Inspector opens, Flow Tree updates, Graph focuses. |
| T2 | Click Module in Tree | PASS | Graph filters to module, **Flow Tree updates to first function**, Inspector opens. |
| T3 | Click Flow Tree Node | PASS | Graph focuses, Inspector updates, File Tree marks active. |
| T4 | Click Graph Node | PASS | Inspector opens, File Tree marks active. |

**Final result:** 4/4 PASS
- Fixes CT-06: Flow Tree now provides immediate context when clicking files.
- UI synchronization via `selectNodeUI()` confirmed.

---

## 2026-04-21 22:00:00

### Source Code Viewer Fix & Security Boundary Test

**Method:** Simulated analysis from dashboard followed by file fetch.

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | `launch.py` (code_tracer/engine) | PASS | Dashboard loads correctly at root. |
| T2 | `/static/analyze` (parent dir) | PASS | Successfully analyzed `code_tracer/` from dashboard. |
| T3 | `/file/read` (download_release.py) | PASS | Successfully fetched source for file in the new root. |
| T4 | Security Block (outside root) | PASS | Attempting to read outside `code_tracer/` returns 403. |
| T5 | `.target` Persistence | PASS | `.target` file is updated to `code_tracer/` after analysis. |

**Final result:** 5/5 PASS
- Fixes CT-05: Resolves 403 Forbidden errors when switching analysis targets.
- Enhances path validation using `is_relative_to()`.

---

## 2026-04-19 07:00:00

### launch.py + Backend Endpoint Test — Post-Migration

**Method:** Direct uvicorn start + curl endpoint tests against `dcc/workflow` target (754 Python files)

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | `/health` | PASS | `status=healthy version=0.2.0` |
| T2 | `/static/analyze` | PASS | `nodes=754 edges=737 entry_points=383` |
| T3 | `/static/report` | PASS | `total=754 top=apply_validation CC=100` |
| T4 | `/static/graph` | PASS | `nodes=754 edges=737` |
| T5 | `/file/read` relative path | PASS | `size=13931 chars` |
| T6 | `/file/read` security block | PASS | `/etc/passwd` → `Access denied` |
| T7 | `/file/validate` | PASS | `valid=True` |
| T8 | `launch.py --help` | PASS | Help text rendered correctly |

**Issues found and fixed:**
- CT-01: `ModuleNotFoundError: No module named 'tracer'` → fixed import paths
- CT-02: `edges=0` → installed `networkx==3.6.1`

**Final result:** 8/8 PASS
