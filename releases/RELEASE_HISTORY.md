# Release History — PyCode Tracer

All releases are stored in this folder as versioned zip archives.
Each release is self-contained and can be extracted and run on any machine with Python 3.10+.

**How to create a new release:**
```bash
python code_tracer/download_release.py              # patch bump
python code_tracer/download_release.py --bump minor
python code_tracer/download_release.py --bump major
```

**How to install a release:**
```bash
# Extract the zip, then:
pip install -r requirements.txt
python engine/launch.py C:\path\to\your\project     # Windows
python engine/launch.py /path/to/your/project       # Linux/Mac
# Dashboard opens automatically at http://localhost:8000
```

---

## v1.0.2 — 2026-05-01

**File:** [`pycode-tracer-v1.0.2.zip`](pycode-tracer-v1.0.2.zip)
**Type:** Patch release
**Packaged from:** `code_tracer/`

### Summary

Single-port architecture (Phase R8). The tool now runs entirely on port 8000 — no second file server process required. `http://localhost:8000` serves both the dashboard and the API.

### Changes

#### R8 — Single-Port Mode
- `engine/backend/server.py`: Added `GET /` route serving `static_dashboard.html` via `FileResponse`; mounted `code_tracer/ui/` at `/ui` for CSS and assets; removed broken `StaticFiles(directory="dist")` stub; removed `root()` API info endpoint
- `ui/static_dashboard.html`: `const API = '/api'` → `const API = ''`; CSS href → `/ui/dcc-design-system.css`
- `engine/launch.py`: Removed `--serve-port` arg and `serve.py` subprocess; added health-check retry loop before opening browser; single URL `http://localhost:8000`

### Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| `python engine/launch.py <target>` starts one process on port 8000 | ✅ |
| `http://localhost:8000` serves the dashboard HTML | ✅ |
| `http://localhost:8000/ui/dcc-design-system.css` returns CSS | ✅ |
| All API calls (`/static/analyze`, `/health`, `/file/read`) work | ✅ |
| No second process or port 5000 required | ✅ |

### Log References

| Log | Entry |
|-----|-------|
| `code_tracer/Log/update_log.md` | Phase R8 — Single-Port Mode |
| `code_tracer/Log/update_log.md` | Phase R8 — dashboard 404 bugfix |
| `code_tracer/Log/test_log.md` | Phase R8 end-to-end test (7/7 PASS) |
| `code_tracer/Log/issue_log.md` | [#CT-14](../code_tracer/Log/issue_log.md#issue-CT-14) — two-port architecture |
| `code_tracer/Log/issue_log.md` | [#CT-15](../code_tracer/Log/issue_log.md#issue-CT-15) — dashboard 404 |
| `code_tracer/workplan/code_tracing_release_workplan.md` | Phase R8 ✅ |

---

## v1.0.1 — 2026-04-22

**File:** [`pycode-tracer-v1.0.1.zip`](pycode-tracer-v1.0.1.zip)
**Type:** Patch release
**Packaged from:** `code_tracer/`

### Summary

Post-migration stabilisation. Fixed broken import paths, asset serving, and release packaging after the tracer was migrated from `dcc/tracer/` to the standalone `code_tracer/` project structure.

### Changes

- `engine/launch.py`: Fixed uvicorn module string `tracer.backend.server:app` → `backend.server:app`; fixed `cwd` to `engine/`
- `engine/backend/server.py`: Updated `sys.path` to add `engine/` root; replaced all `from tracer.X import` with `from X import`; replaced brittle `.startswith()` path checks with `Path.is_relative_to()`; `_resolve_base()` now prioritises `.target` file over env var for dynamic root switching; `static_analyze` updates `.target` on each run
- `code_tracer/serve.py`: Moved from `engine/` to root; serves from `code_tracer/` root using `ui/static_dashboard.html`
- `ui/static_dashboard.html`: Moved from `engine/` to `ui/`; added dedicated Load Project sidebar panel; breadcrumb moved to status bar; title bar borders removed
- `download_release.py`: Moved to `code_tracer/` root; standardised zip prefix to `pycode-tracer`; updated MANIFEST paths to `engine/` prefix; version regex supports both `pycode-tracer` and legacy `dcc-tracer` prefixes
- `engine/pyproject.toml` + `MANIFEST.in`: Updated for `engine/` layout

### Log References

| Log | Entry |
|-----|-------|
| `code_tracer/Log/update_log.md` | launch.py Fix — Post-Migration |
| `code_tracer/Log/update_log.md` | Standalone Release Refinement & Path Fixes |
| `code_tracer/Log/update_log.md` | Reorganization: Standalone Launcher Assets |
| `code_tracer/Log/issue_log.md` | #CT-01 through #CT-13 |

---

## v1.0.0 — 2026-04-22

**File:** [`pycode-tracer-v1.0.0.zip`](pycode-tracer-v1.0.0.zip)
**Type:** Initial release (migrated from `dcc/tracer/`)
**Packaged from:** `code_tracer/`

### Summary

First release under the `code_tracer/` standalone project structure. Migrated from `dcc/tracer/` to an independent top-level project. Includes the full static analysis dashboard, FastAPI backend with portable path resolution, launcher, pip package, and Docker support.

### What's Included

| File | Description |
|------|-------------|
| `engine/backend/server.py` | FastAPI backend with portable `_resolve_base()` path resolution |
| `engine/static/` | AST crawler, parser, call graph builder, metrics, visualizer |
| `engine/launch.py` | Single entry point — starts backend + file server + opens browser |
| `code_tracer/serve.py` | Standalone file server + `/api/*` proxy |
| `ui/static_dashboard.html` | Interactive call graph dashboard |
| `ui/dcc-design-system.css` | Design system CSS |
| `engine/pyproject.toml` | pip-installable package |
| `requirements.txt` | `fastapi>=0.100`, `uvicorn>=0.23`, `networkx>=3.0` |

### Changes (R1–R7 from dcc/tracer baseline)

- **R1** — Portable path resolution via `_resolve_base()` replacing hard-coded `dcc/` paths
- **R2** — `launch.py` launcher + standalone `serve.py` file server
- **R3** — `pyproject.toml` with `dcc-tracer` CLI entry point
- **R4** — `Dockerfile` + `docker-compose.yml`
- **R5** — Dashboard UX: target directory input, breadcrumb, copy button
- **R6** — External `README.md` + `USER_GUIDE.md`
- **R7** — `download_release.py` distribution packager with auto-versioning

### Log References

| Log | Entry |
|-----|-------|
| `dcc/Log/update_log.md` | `#tracer-standalone-release` — R1–R6 |
| `dcc/Log/update_log.md` | `#tracer-r7-downloader` — R7 |
| `code_tracer/Log/update_log.md` | Migration: dcc/tracer → code_tracer |

---
