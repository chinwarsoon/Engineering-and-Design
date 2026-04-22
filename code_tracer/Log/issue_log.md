# Code Tracer — Issue Log

## Instructions
1. Always log new issues immediately after identified.
2. Add a timestamp at the beginning of each log entry.
3. When resolved, update status and link to update_log.

---

# Section 2. Pending Issues

## 2026-05-01

<a id="issue-CT-14"></a>
[Issue #CT-14]: Two-port architecture requires users to manage two processes and two URLs
- `[Status]`: **PENDING APPROVAL**
- `[Context]`: `launch.py` currently starts two subprocesses: uvicorn on port 8000 (API) and a Python http.server on port 5000 (dashboard + `/api/*` proxy). Users must open `http://localhost:5000` for the dashboard. The proxy adds latency and a failure point (Bad Gateway if backend is slow to start). FastAPI already imports `StaticFiles` and has a broken `app.mount("/", StaticFiles(directory="dist", html=True))` stub in `server.py` pointing to a non-existent `dist/` directory.
- `[Root Cause]`: Original design separated concerns across two servers. Now that the project is standalone, a single FastAPI process can serve both the API and the static dashboard with no proxy needed.
- `[Proposed Resolution]`: Phase R8 — mount `code_tracer/ui/` as FastAPI static files; change `const API = '/api'` to `const API = ''` in the dashboard; remove the file server subprocess from `launch.py`. Full plan in `code_tracing_release_workplan.md` Phase R8.
- `[Files to Change]`: `engine/backend/server.py`, `ui/static_dashboard.html`, `engine/launch.py`
- `[Awaiting]`: Approval before implementation
- `[Link to workplan]`: [code_tracing_release_workplan.md](../workplan/code_tracing_release_workplan.md#phase-r8)

---

## 2026-04-22 09:00:00

[Issue #CT-09]: `launch.py` fails to find `serve.py` in standalone release.
- `[Status]`: **Resolved**
- `[Root Cause]`: Hard-coded path `tracer_dir.parent / "serve.py"` assumes repository layout where `launch.py` is in `engine/` and `serve.py` is in root. In ZIP release, both are at root.
- `[Resolution]`: Updated `launch.py` to check both `.` and `..` for `serve.py`.
- `[Link to update_log]`: [update_log.md](update_log.md)

[Issue #CT-10]: `pyproject.toml` and `MANIFEST.in` broken for `pip install`.
- `[Status]`: **Resolved**
- `[Root Cause]`: Configuration still uses `tracer/` prefix which was removed during migration to `engine/` folder.
- `[Resolution]`: Updated `pyproject.toml` and `MANIFEST.in` to match current `engine/` layout (root `.`).
- `[Link to update_log]`: [update_log.md](update_log.md)

[Issue #CT-11]: Filename inconsistency and broken links in `download_release.py`.
- `[Status]`: **Resolved**
- `[Root Cause]`: Script creates `pycode-tracer-v*.zip` but links to `py-tracer-v*.zip` in `RELEASE_HISTORY.md`.
- `[Resolution]`: Standardized on `pycode-tracer` prefix everywhere.
- `[Link to update_log]`: [update_log.md](update_log.md)

[Issue #CT-12]: Version detection fails to account for legacy `dcc-tracer` prefix.
- `[Status]`: **Resolved**
- `[Root Cause]`: Regex only looks for `pycode-tracer`, causing it to ignore existing `dcc-tracer-v1.0.0.zip` and restart versioning at `v1.0.0`.
- `[Resolution]`: Updated regex to `(pycode|dcc)-tracer-v(\d+)\.(\d+)\.(\d+)\.zip`.
- `[Link to update_log]`: [update_log.md](update_log.md)

[Issue #CT-13]: `USER_GUIDE.md` contains outdated paths and instructions.
- `[Status]`: **Resolved**
- `[Root Cause]`: References to `dcc/tracer/` and `tracer/` subfolders remain after migration to `code_tracer/` and `engine/`.
- `[Resolution]`: Refreshed documentation to match new standalone structure and naming.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

## 2026-04-21 23:15:00

[Issue #CT-08]: Improved accessibility for project loading (Sidebar Reorganization).
- `[Status]`: **Resolved**
- `[Root Cause]`: Key feature (Load Directory) was nested within Analysis Controls, requiring extra clicks and reducing discoverability.
- `[Resolution]`: Promoted "Load Project" to a dedicated top-level panel with its own icon in the activity bar.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

## 2026-04-21 23:00:00

[Issue #CT-07]: Title bar visual clutter (unnecessary vertical borders/separators).
- `[Status]`: **Resolved**
- `[Root Cause]`: Default component styles included vertical dividers and button borders that conflicted with the desired minimalist aesthetic.
- `[Resolution]`: Applied a global reset to the title bar scope in `dcc-design-system.css` to suppress all internal borders.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

## 2026-04-21 22:15:00

[Issue #CT-06]: Flow Tree and Inspector not updating when clicking a file in the file tree.
- `[Status]`: **Resolved**
- `[Root Cause]`: Selection logic was fragmented. Clicking a module only filtered the graph but didn't trigger a node selection event, leaving the Flow Tree and Inspector showing stale or empty data.
- `[Resolution]`: 
    1. Consolidated selection logic into `selectNodeUI()` helper.
    2. Implemented auto-selection of the first function when a module node is clicked in the file tree.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

## 2026-04-21 22:00:00

[Issue #CT-05]: `403 Forbidden` when fetching source code after analyzing a new directory.
- `[Status]`: **Resolved**
- `[Root Cause]`: 
    1. `_resolve_base()` prioritized `TRACER_TARGET` env var (set by `launch.py`) over the `.target` file, preventing the security boundary from updating when a new directory was analyzed.
    2. Brittle `.startswith()` string comparison failed for logically valid paths due to missing trailing slashes or path normalization differences.
- `[Resolution]`: 
    1. Updated `_resolve_base()` to prioritize the `.target` file.
    2. Modified `static_analyze` to update the `.target` file with the new root after successful analysis.
    3. Replaced all `.startswith()` security checks with robust `Path.is_relative_to()` validation.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

## 2026-04-21 21:30:00

[Issue #CT-04]: Call graph showing no edges, arrows, or entry points after loading `launch.py`.
- `[Status]`: **Resolved**
- `[Root Cause]`: `call_graph.json` contained stale data from when `networkx` was not installed in the active `dcc` conda environment. File showed `nodes: 945, edges: 0, entry_points: 0`.
- `[Resolution]`: Installed `networkx==3.6.1` in `dcc` conda environment, regenerated `call_graph.json` with `106 nodes, 93 edges, 50 entry_points`, updated `.target` file path.
- `[Link to update_log]`: [update_log.md](update_log.md)

---

# Section 3. Closed Issues

*(none — see dcc/Log/issue_log.md for pre-migration history)*

## 2026-04-21 21:05:00

[Issue #CT-03]: `404 File not found` for `ui/dcc-design-system.css` in dashboard.
- `[Status]`: **Resolved**
- `[Root Cause]`: `static_dashboard.html` was in `engine/` but assets were in `ui/`. `serve.py` only served from `engine/`.
- `[Resolution]`: Moved `serve.py` to root and serve from `code_tracer/` root; moved all HTML to `ui/`. Updated `launch.py` to point to root `serve.py`.
- `[Link to update_log]`: [update_log.md](update_log.md)

## 2026-04-19 07:00:00

[Issue #CT-01]: `ModuleNotFoundError: No module named 'tracer'` when running `launch.py` after migration.
- `[Status]`: **Resolved**
- `[Root Cause]`: `launch.py` used `uvicorn tracer.backend.server:app` with `cwd=tracer_dir.parent`. After migration the package root is `engine/` itself, not a `tracer/` subfolder inside a parent.
- `[Resolution]`: Changed to `backend.server:app` with `cwd=tracer_dir`. Updated `server.py` `sys.path` to add `engine/` dir. Replaced all `from tracer.X import` with `from X import`.
- `[Link to update_log]`: [update_log.md](update_log.md)

## 2026-04-19 07:00:00

[Issue #CT-02]: `edges=0, entry_points=0` in call graph — `networkx` not installed.
- `[Status]`: **Resolved**
- `[Root Cause]`: `networkx` listed in `pyproject.toml` but not installed in active conda env. `_NX_AVAILABLE=False` caused `edge_count` to return 0.
- `[Resolution]`: `pip install networkx==3.6.1`. Added to `dcc/dcc.yml` and root `dcc.yml`.
- `[Link to update_log]`: [update_log.md](update_log.md)
