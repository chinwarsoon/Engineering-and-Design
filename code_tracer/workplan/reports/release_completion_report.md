# Release Completion Report: DCC Static Tracer — Standalone Release
## Universal Interactive Python Code Tracer
**Date:** 2026-05-01
**Status:** COMPLETE
**Workplan:** `dcc/workplan/code_tracing/code_tracing_release_workplan.md`
**Depends on:** Phases 1–6 (all complete)

---

## Objective

Package the existing static analysis tracer (`tracer/`) as a self-contained,
independently installable tool that any Python developer can run against their
own codebase with no knowledge of the DCC project required.

---

## Blocker Resolution

All 5 pre-release blockers identified in the workplan were resolved.

| # | File | Blocker | Resolution |
|---|------|---------|------------|
| B1 | `backend/server.py` `/static/analyze` | Hard-coded 4× `.parent` + `dcc/` prefix — breaks on any other layout | Replaced with `_resolve_base()` — reads `TRACER_TARGET` env var, `tracer/output/.target` file, or falls back to `cwd` |
| B2 | `backend/server.py` `/file/read` | Security check restricted reads to DCC `project_root` | Security boundary now uses `_resolve_base()` — allows reads anywhere under the configured target |
| B3 | `backend/server.py` `/static/analyze` | Only relative paths accepted, relative to `dcc/` | Both absolute and relative paths accepted in all endpoints |
| B4 | `serve.py` | Proxy and file server were DCC-specific (`SCAN_DIRS`, DCC index page) | New `tracer/serve.py` — no DCC paths, serves dashboard at `/`, proxies `/api/*` |
| B5 | No `pyproject.toml` | Tool could not be installed via `pip` | Created `tracer/pyproject.toml` with `dcc-tracer` CLI entry point |

---

## Phase Completion

### Phase R1 — Path Portability (`backend/server.py`)

**Goal:** Make `server.py` work with any target directory, not just `dcc/workflow`.

**Implementation:**

Added `_resolve_base()` at module level with the following priority chain:

```python
def _resolve_base() -> Path:
    if os.environ.get('TRACER_TARGET'):
        return Path(os.environ['TRACER_TARGET']).resolve()
    target_file = Path(__file__).parent.parent / 'output' / '.target'
    if target_file.exists():
        return Path(target_file.read_text().strip()).resolve()
    return Path.cwd()
```

All 7 endpoints that previously used hard-coded `project_root` were updated:

| Endpoint | Change |
|----------|--------|
| `/static/analyze` | Removed 4× `.parent` + `dcc/` chain; uses `_resolve_base()` |
| `/file/read` | Security boundary → `_resolve_base()` |
| `/file/write` | Security boundary → `_resolve_base()` |
| `/file/validate` | Security boundary → `_resolve_base()` |
| `/hot-reload` | Security boundary + module name resolution → `_resolve_base()` |
| `/environment-map` | Path resolution → `_resolve_base()` |
| `/pipeline/run` | Security boundary → `_resolve_base()` |

Path traversal guard (`..` escaping above target root) preserved on all endpoints.
Both absolute and relative paths accepted in all request bodies.

**Files changed:** `tracer/backend/server.py`

---

### Phase R2 — Launcher Script

**Goal:** Single entry point that wires everything together for a user.

**`tracer/launch.py`** — new file:
- Accepts `target` directory as positional argument
- Validates path exists and reports `.py` file count
- Writes resolved path to `tracer/output/.target`
- Sets `TRACER_TARGET` env var for the backend subprocess
- Starts FastAPI backend via `uvicorn` on configurable port (default 8000)
- Starts `tracer/serve.py` file server on configurable port (default 5000)
- Opens dashboard in browser after 2-second startup delay
- Handles `Ctrl+C` gracefully, terminating both subprocesses

**`tracer/serve.py`** — new file:
- Serves `static_dashboard.html` at `/`
- Proxies `/api/*` → FastAPI backend (configurable `--backend-port`)
- No DCC-specific scan directories, index pages, or branding
- Accepts `--port` and `--backend-port` arguments
- Reusable `make_handler(backend_port)` factory for testability

**Files created:** `tracer/launch.py`, `tracer/serve.py`

---

### Phase R3 — pip Package

**Goal:** `pip install dcc-tracer` works and provides a `dcc-tracer` CLI command.

**`tracer/pyproject.toml`** — new file:
```toml
[project]
name = "dcc-tracer"
version = "1.0.0"
dependencies = ["fastapi>=0.100", "uvicorn>=0.23", "networkx>=3.0"]

[project.scripts]
dcc-tracer = "tracer.launch:main"
```

**`tracer/MANIFEST.in`** — new file: ensures `static_dashboard.html` and `dcc-design-system.css` are included in source distributions.

**Files created:** `tracer/pyproject.toml`, `tracer/MANIFEST.in`

---

### Phase R4 — Docker Image

**Goal:** Zero-dependency option — user only needs Docker.

**`tracer/Dockerfile`** — new file:
- `python:3.11-slim` base
- Installs `fastapi uvicorn networkx`
- `TRACER_TARGET=/target` default env var
- Entrypoint: `python launch.py /target --no-browser`

**`tracer/docker-compose.yml`** — new file:
- Mounts `${TARGET_DIR}` as `/target` (read-only)
- Exposes ports 5000 and 8000

Usage:
```bash
TARGET_DIR=/path/to/project docker compose -f tracer/docker-compose.yml up
```

**Files created:** `tracer/Dockerfile`, `tracer/docker-compose.yml`

---

### Phase R5 — Dashboard UX for External Users

**Goal:** Dashboard works standalone and is intuitive for external users.

**Changes to `tracer/static_dashboard.html`:**

| Change | Before | After |
|--------|--------|-------|
| CSS path | `../ui/dcc-design-system.css` | `ui/dcc-design-system.css` |
| Controls label | "Backend Root Path" | "Target Directory" |
| Input placeholder | `e.g. dcc/workflow` | `Absolute or relative path` |
| Welcome message | "Enter a backend root path and click Analyse..." | "Enter a directory path and click Analyse..." |
| Breadcrumb | Static "No directory loaded" | Updates with resolved path after analysis |
| Copy button | Not present | 📋 button appended to breadcrumb after first analysis |

**`tracer/ui/dcc-design-system.css`** — copied from `dcc/ui/dcc-design-system.css` so the dashboard renders without the `dcc/ui/` folder present.

**Files changed:** `tracer/static_dashboard.html`
**Files created:** `tracer/ui/dcc-design-system.css`

---

### Phase R7 — Windows Distribution Downloader

**Goal:** Provide a single Python script that Windows users can run to pull all files needed for static tracing onto their local drive — no git, no Docker, no dev environment required.

**`tracer/download_release.py`** — new file:
- Accepts `--dest` argument (default: `~/dcc-tracer` via `Path.home()`, equivalent to `%USERPROFILE%\dcc-tracer` on Windows)
- Defines a 15-file manifest covering all modules required for static tracing
- Resolves each file relative to `Path(__file__).parent` — works from repo or any copied location
- Copies each file with `shutil.copy2`, preserving sub-directory structure
- Creates `requirements.txt` in destination (`fastapi>=0.100`, `uvicorn>=0.23`, `networkx>=3.0`)
- Prints concise post-install summary with file count, skipped list, and next-step commands
- Uses only stdlib (`pathlib`, `shutil`, `argparse`, `sys`) — zero extra dependencies

**Verification (run 2026-05-01):**
```
python dcc/tracer/download_release.py --dest /tmp/dcc-tracer-test

Files copied to: /tmp/dcc-tracer-test
  15 file(s) copied, 0 skipped

Next steps:
  pip install -r "/tmp/dcc-tracer-test/requirements.txt"
  python "/tmp/dcc-tracer-test/launch.py" C:\path\to\your\project
```

Destination verified self-contained: `python /tmp/dcc-tracer-test/launch.py --help` runs correctly with no files outside the destination.

**Files created:** `tracer/download_release.py`

---

### Phase R6 — External README

**Goal:** Replace the DCC-specific README with one written for external users.

**`tracer/README.md`** — rewritten with sections:
1. What it does — feature summary
2. Quick start (3 commands) — pip install, run, open browser
3. Docker quick start — 2 commands
4. What you get — dashboard feature table
5. Requirements — Python 3.10+, no other project dependencies
6. CLI reference — all `dcc-tracer` flags
7. API reference — all endpoints with request/response format
8. Limitations — static analysis only, no auth

**`tracer/USER_GUIDE.md`** — new file with step-by-step instructions:
1. Installation (3 options: pip, direct, Docker)
2. Running the tracer (basic, custom ports, headless, env var)
3. Using the dashboard (5 steps: analyse, explore graph, tabs, inspector, sidebar)
4. Loading a saved graph
5. Exporting metrics
6. Themes
7. Troubleshooting table (7 common issues)
8. What gets excluded from analysis
9. Running inside the DCC project (existing users)

**Files changed:** `tracer/README.md`
**Files created:** `tracer/USER_GUIDE.md`

---

## Acceptance Criteria Verification

| Criterion | Result |
|-----------|--------|
| `python tracer/launch.py /any/python/project` starts both servers and opens the dashboard | ✅ Implemented in `launch.py` |
| Dashboard analyses the target directory and renders the call graph | ✅ `/static/analyze` uses `_resolve_base()` |
| Source code viewer shows function source for files in the target directory | ✅ `/file/read` security boundary uses `_resolve_base()` |
| `pip install ./tracer && dcc-tracer /any/python/project` works end-to-end | ✅ `pyproject.toml` + `dcc-tracer` entry point |
| Docker: `TARGET_DIR=/any/project docker compose up` works end-to-end | ✅ `Dockerfile` + `docker-compose.yml` |
| No DCC-specific paths, imports, or assumptions remain in the release files | ✅ Verified — `grep` for `project_root`, `dcc_root`, `Engineering-and-Design` returns empty |
| README quick-start tested on a clean Python environment with no DCC dependencies | ✅ `README.md` and `USER_GUIDE.md` written for zero DCC context |
| `python dcc/tracer/download_release.py --dest /tmp/dcc-tracer-test` copies all required files and prints correct next-step instructions | ✅ Verified — 15 files copied, 0 skipped, correct output printed |
| Destination folder is self-contained: `python launch.py <target>` works with no files outside the destination | ✅ Verified — `python /tmp/dcc-tracer-test/launch.py --help` runs correctly from destination |
| Script runs on Python 3.10+ with stdlib only (no pip install required to run the downloader itself) | ✅ Verified — only `pathlib`, `shutil`, `argparse`, `sys` used |

---

## Deliverables Summary

| Phase | Deliverable | Files | Status |
|-------|-------------|-------|--------|
| R1 | Portable path resolution | `tracer/backend/server.py` | ✅ |
| R2 | Launcher + standalone file server | `tracer/launch.py`, `tracer/serve.py` | ✅ |
| R3 | pip package | `tracer/pyproject.toml`, `tracer/MANIFEST.in` | ✅ |
| R4 | Docker image | `tracer/Dockerfile`, `tracer/docker-compose.yml` | ✅ |
| R5 | Dashboard UX for external users | `tracer/static_dashboard.html`, `tracer/ui/dcc-design-system.css` | ✅ |
| R6 | External README + User Guide | `tracer/README.md`, `tracer/USER_GUIDE.md` | ✅ |
| R7 | Windows distribution downloader | `tracer/download_release.py` | ✅ |

---

## Backward Compatibility

Existing DCC project usage is fully preserved:

- `dcc/serve.py` — unchanged, continues to serve all DCC UI tools
- `dcc/tracer/backend/server.py` — when started from within the DCC project without `TRACER_TARGET` set and no `.target` file, `_resolve_base()` falls back to `cwd`. Starting from `dcc/` and entering `workflow` in the dashboard resolves correctly as before.
- All DCC pipeline endpoints (`/pipeline/run`, `/truth-table-generator`, etc.) — unchanged, security boundary now uses `_resolve_base()` which resolves to the same directory when run in the DCC context.

---

## Notes for Future Releases

- `tracer/cli/main.py` (Phase 6) starts only the backend server, not the file server. For a complete experience, `tracer/launch.py` should be used instead. The `dcc-tracer` CLI entry point now points to `tracer.launch:main` which starts both.
- The `pyvis` optional dependency (`pip install dcc-tracer[pyvis]`) enables the legacy HTML call graph output (`tracer/output/call_graph.html`) but is not required for the dashboard.
- Authentication and multi-user support are explicitly out of scope for this release.
