# Code Tracer — Issue Log

## Instructions
1. Always log new issues immediately after identified.
2. Add a timestamp at the beginning of each log entry.
3. When resolved, update status and link to update_log.

---

# Section 2. Pending Issues

*(none)*

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
