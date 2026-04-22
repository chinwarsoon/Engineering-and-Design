# Code Tracer — Update Log

## Instructions
1. Always log changes immediately after the change is made.
2. Add a timestamp at the beginning of each log entry.
3. Summarize what was changed, why, and the impact.

---

## 2026-04-19 06:00:00

### Migration: dcc/tracer → code_tracer

**Status:** COMPLETE

**Change:** Migrated all tracer-related files from `dcc/` into the standalone `code_tracer/` project folder.

**Files Migrated:**

| Source | Destination |
|--------|-------------|
| `dcc/tracer/` (all engine code) | `code_tracer/engine/` |
| `dcc/workplan/code_tracing/` | `code_tracer/workplan/` |
| `dcc/workplan/code_tracing/reports/` | `code_tracer/workplan/reports/` |
| `dcc/workflow/code_tracing/archive/` | `code_tracer/workplan/archive/` |
| `dcc/ui/tracer_pro.html` | `code_tracer/ui/` |
| `releases/dcc-tracer-v*.zip` | `code_tracer/releases/` |
| `releases/RELEASE_HISTORY.md` | `code_tracer/releases/` |

**Folder structure:**
```
code_tracer/
├── engine/          <- all tracer source code (was dcc/tracer/)
├── ui/              <- tracer_pro.html dashboard
├── workplan/        <- workplans + phase reports
│   ├── reports/     <- phase completion reports
│   └── archive/     <- v1 workplan archive
├── releases/        <- release zips + history
└── Log/             <- this log folder
```

**Rationale:** The tracer is a standalone tool independent of the DCC pipeline. Separating it into its own top-level project folder improves maintainability and allows independent versioning.

**Original files remain in dcc/ — not deleted (per agent_rule.md: archive before delete).**

---

## 2026-04-19 07:00:00

### launch.py Fix — Post-Migration Import Path Correction

**Status:** COMPLETE

**Problem:** After migration, `launch.py` called `uvicorn tracer.backend.server:app` with `cwd=tracer_dir.parent`. The package is now at `engine/` (not a `tracer/` subfolder), so `tracer` module was not found (`ModuleNotFoundError: No module named 'tracer'`).

**Fixes applied:**

| File | Change |
|------|--------|
| `engine/launch.py` line 71-73 | `tracer.backend.server:app` → `backend.server:app`; `cwd=tracer_dir.parent` → `cwd=tracer_dir` |
| `engine/backend/server.py` line 26-28 | `_tracer_root` (2 levels up) → `_engine_root` (engine dir); added to `sys.path` |
| `engine/backend/server.py` line 46-47 | `from tracer import ...` → `from core.trace_engine import ...` + `from utils.trace_filters import ...` |
| `engine/backend/server.py` line 49 | `from tracer.utils.trace_filters import ...` → `from utils.trace_filters import ...` |
| `engine/backend/server.py` lines 638,680-682 | `from tracer.pipeline_sandbox/static...` → `from pipeline_sandbox/static...` |

**Dependency fix:** `networkx` was not installed — caused `edges=0` in call graph. Installed `networkx==3.6.1`. Added to `dcc/dcc.yml` and root `dcc.yml`.

---

## 2026-05-01

### Phase R8 — Single-Port Mode (bugfix: dashboard 404)

**Status:** COMPLETE

**Problem:** After initial R8 implementation, `GET /` returned 404. `StaticFiles(html=True)` requires a file named `index.html` — the dashboard is named `static_dashboard.html`.

**Fix:**
- Added explicit `GET /` route using `FileResponse` to serve `static_dashboard.html` directly
- Removed the catch-all `StaticFiles` SPA mount (no longer needed)
- Re-added `FileResponse` import

**Files Changed:** `engine/backend/server.py`

**Verified:** `http://localhost:8000` serves the dashboard correctly. Single-port mode fully operational.

**Related:** [Issue #CT-15](issue_log.md#issue-CT-15)

---

## 2026-05-01

### Phase R8 — Single-Port Mode

**Status:** COMPLETE

**Changes:**

| File | Change |
|------|--------|
| `engine/backend/server.py` | Removed `root()` endpoint and broken `StaticFiles(directory="dist")` stub; added `app.mount("/ui", StaticFiles(_UI_DIR))` and `app.mount("/", StaticFiles(_UI_DIR, html=True))`; removed unused `HTMLResponse` import; `_UI_DIR` resolves to `code_tracer/ui/` relative to `server.py` |
| `ui/static_dashboard.html` | `const API = '/api'` → `const API = ''`; CSS href `ui/dcc-design-system.css` → `/ui/dcc-design-system.css` |
| `engine/launch.py` | Removed `--serve-port` arg, `serve_script` lookup, `file_server` subprocess, and `file_server.terminate()`; added `urllib.request` import; replaced `time.sleep(2)` with health-check retry loop (20×1s); dashboard URL now points to `args.port` directly |

**Result:** Single process on port 8000 serves both API and dashboard. `serve.py` is no longer invoked by `launch.py` (still available standalone).

**Related:** [Issue #CT-14](issue_log.md#issue-CT-14)

---

## 2026-04-22 09:30:00

### Standalone Release Refinement & Path Fixes

**Status:** COMPLETE

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `engine/launch.py` | `serve_script` logic | Added fallback to check current directory for `serve.py`, fixing broken launcher in ZIP release. |
| `engine/pyproject.toml` | Root & Scripts | Updated to use `engine/` as root (`where = ["."]`) and fixed `dcc-tracer` CLI entry point. |
| `engine/MANIFEST.in` | Asset Paths | Removed outdated `tracer/` prefix from include rules. |
| `download_release.py` | Version Logic | Updated regex to support both `pycode-tracer` and legacy `dcc-tracer` prefixes. |
| `download_release.py` | Filename Prefix | Standardized on `pycode-tracer` for ZIP files and `RELEASE_HISTORY.md` entries. |
| `USER_GUIDE.md` | Refresh | Updated all paths and installation instructions to match the standalone `code_tracer/` structure. |

**Impact:** Ensures a fully functional standalone release. ZIP files now contain correct internal paths, the `pip install` package is valid, and documentation is accurate.

---

## 2026-04-21 21:05:00

### Reorganization: Standalone Launcher Assets & Serve Logic

**Status:** COMPLETE

**Problem:** CT-03 identified a 404 error for `ui/dcc-design-system.css` because `serve.py` served from `engine/` while assets were in root `ui/`.

**Changes applied:**

| File | New Location | Description |
|------|--------------|-------------|
| `engine/serve.py` | `code_tracer/serve.py` | Moved to root; updated to serve from root and use `ui/static_dashboard.html`. |
| `engine/static_dashboard.html` | `ui/static_dashboard.html` | Moved to `ui/` folder with other frontend assets. |
| `engine/launch.py` | (same) | Updated `serve_script` path to find root `serve.py`. |

**Impact:** Resolves asset path mismatch. Consolidates frontend/UI logic into the `ui/` folder while keeping the launcher at project root.

---

## 2026-04-21 21:30:00

### Call Graph Fix: networkx Installation & Data Regeneration

**Status:** COMPLETE

**Problem:** After launching `launch.py`, the dashboard showed no link arrows, entry points, or flow tree. The `call_graph.json` had stale data from when `networkx` was not installed: `nodes: 945, edges: 0, entry_points: 0`.

**Root Cause:**
1. `networkx==3.6.1` was installed in base conda env but not in the active `dcc` env
2. The existing `call_graph.json` was generated without networkx (edges=0)
3. The `.target` file pointed to the wrong path (`/home/franklin/dsai` instead of `code_tracer/engine`)

**Actions:**
1. Activated `dcc` conda environment: `conda activate dcc`
2. Installed networkx: `pip install networkx==3.6.1`
3. Regenerated `call_graph.json` with proper edges using `CallGraph(modules).build()`
4. Updated `.target` file to correct path

**Results:**
- Before: `nodes: 945, edges: 0, entry_points: 0`
- After: `nodes: 106, edges: 93, entry_points: 50`

**Files Updated:**
- `code_tracer/engine/output/call_graph.json` — regenerated with valid edges
- `code_tracer/engine/output/.target` — corrected path
- Environment: `dcc` conda env now has `networkx==3.6.1`

---

## 2026-04-21 23:15:00

### UI Reorganization: Dedicated Load Project Panel

**Status:** COMPLETE

**Problem:** The "Load Directory" functionality was hidden inside the "Controls" panel. Moving it to its own top-level icon improves accessibility and follows standard IDE patterns.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `ui/static_dashboard.html` | New Icon Bar Button | Added `📥 Load Project` as the first icon in the activity bar. |
| `ui/static_dashboard.html` | New Sidebar Panel | Created `sb-panel-load` to hold project loading inputs independently. |
| `ui/static_dashboard.html` | Panel Cleanup | Removed the "Load" section from the "Controls" panel. |
| `ui/static_dashboard.html` | Default State | Set the "Load" panel as the default visible panel on startup. |

**Impact:** Faster access to project loading functionality. Cleaner separation between project management (Load) and analysis tuning (Controls).

---

## 2026-04-21 23:00:00

### UI Refinement: Clean Title Bar (No Vertical Lines)

**Status:** COMPLETE

**Problem:** Title bar contained vertical lines/borders (logo separator, button borders) that cluttered the interface.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `ui/dcc-design-system.css` | Global Title Bar Rule | Added `.dcc-titlebar * { border: none !important; }` to remove all borders from elements inside the title bar. |
| `dcc/ui/dcc-design-system.css` | Global Title Bar Rule | Applied the same clean-up to the main project CSS for consistency. |

**Impact:** Minimalist, modern title bar without any vertical separators or element borders.

---

## 2026-04-21 22:45:00

### UI Refinement: Breadcrumb Relocation to Status Bar

**Status:** COMPLETE

**Problem:** Breadcrumb was taking up space in the title bar (under the logo). Moving it to the status bar provides a cleaner header and utilizes available space at the bottom.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `ui/static_dashboard.html` | Relocate Breadcrumb | Moved `#bc-root` container from `dcc-titlebar` to `dcc-statusbar`. |
| `ui/tracer_pro.html` | Relocate Breadcrumb | Moved breadcrumb for consistency with the static dashboard. |
| `ui/dcc-design-system.css` | `.dcc-statusbar-breadcrumb` | Renamed from `.dcc-titlebar-breadcrumb` and restyled for status bar colors (white/light text). |
| `ui/dcc-design-system.css` | Remove Logo Stack | Removed `.logo-text-stack` as the title bar logo name is no longer stacked. |

**Impact:** Improved vertical space in the title bar and better information hierarchy by placing path information in the status bar.

---

## 2026-04-21 22:30:00

### UI Refinement: Title Bar Breadcrumb & Logo Layout

**Status:** COMPLETE

**Problem:** Title bar layout had a dividing line and the breadcrumb was side-by-side with the logo, which could be improved for a cleaner look.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `ui/dcc-design-system.css` | Remove Dividing Line | Removed `border-right` from `.dcc-titlebar-logo`. |
| `ui/dcc-design-system.css` | `.logo-text-stack` | Added a flex-column wrapper to stack logo name and breadcrumb. |
| `ui/static_dashboard.html` | Restructured Title Bar | Moved `titlebar-breadcrumb` inside the logo div and wrapped it in the new stack. |
| `ui/dcc-design-system.css` | Breadcrumb Styling | Reduced font size to `10px` and removed padding to fit the new stacked layout. |

**Impact:** Cleaner, more modern header layout that follows a vertical information hierarchy within the logo area.

---

## 2026-04-21 22:15:00

### UX Improvement: Auto-updating Flow Tree on File Selection

**Status:** COMPLETE

**Problem:** Clicking a file (module) in the file tree filtered the graph but did not update the Flow Tree or Inspector, leading to confusion about whether "flow" was detected.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `ui/static_dashboard.html` | `selectNodeUI` helper | Consolidated selection logic (Graph + Inspector + File Tree + Flow Tree) into a single reusable function. |
| `ui/static_dashboard.html` | Auto-selection | Clicking a file node now automatically selects the first function in that file, triggering a Flow Tree update. |
| `ui/static_dashboard.html` | Refactored Clicks | Updated Graph and Flow Tree click handlers to use the consolidated selection logic. |

**Impact:** Improved discoverability of "Flow" information. Users now get immediate feedback about a file's contents and call hierarchy when selecting it in the tree.

---

## 2026-04-21 22:00:00

### Dynamic Target Resolution & Path Security Fixes

**Status:** COMPLETE

**Problem:** Issue CT-05 identified a 403 Forbidden error when analyzing a new directory from the dashboard and attempting to read its source code. The security boundary was stuck on the initial directory.

**Changes applied:**

| Component | Change | Description |
|-----------|--------|-------------|
| `backend/server.py` (`_resolve_base`) | Priority Swap | Prioritizes `.target` file over `TRACER_TARGET` env var, allowing dynamic root updates. |
| `backend/server.py` (`static_analyze`) | Persist Root | Now updates the `.target` file upon successful analysis, in sync with `call_graph.json`. |
| `backend/server.py` (all endpoints) | Robust Validation | Replaced brittle `.startswith()` string checks with `Path.is_relative_to(base)` for security boundaries. |

**Impact:** Fixes source code fetch failure in the dashboard. Allows the tracer backend to dynamically switch between projects without restart or 403 errors. Improves overall security validation reliability.

---

## 2026-04-21 21:45:00

### Moved: download_release.py to code_tracer Root

**Status:** COMPLETE

**Change:** Moved `download_release.py` from `code_tracer/engine/` to `code_tracer/` root folder per workplan R7 requirements.

**Path Updates:**

| Original | Updated | Description |
|----------|---------|-------------|
| `parents[1] / "ui"` | `parent / "ui"` | CSS source now relative to code_tracer root |
| `parents[2] / "releases"` | `parent / "releases"` | Releases directory at code_tracer/releases |
| `engine/` prefix | Added to MANIFEST entries | All engine files now prefixed with `engine/` |
| `dcc/tracer/` refs | `code_tracer/` | Updated docstring examples |

**MANIFEST Adjustments:**
- `USER_GUIDE.md` — moved from `engine/` to root (was already at root)
- Removed `engine/MANIFEST.in` — file doesn't exist in current structure

**Verification:**
- Script runs successfully: `python download_release.py --bump patch`
- Created release: `dcc-tracer-v1.0.4.zip` (16 files, 190KB)
- All files packed correctly, 0 skipped

**Files Changed:**
- Created: `code_tracer/download_release.py` (new location)
- Deleted: `code_tracer/engine/download_release.py` (old location)
