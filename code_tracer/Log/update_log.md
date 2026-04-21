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
