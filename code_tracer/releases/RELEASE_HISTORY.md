# Release History — DCC Tracer

All releases are stored in this folder as versioned zip archives.
Each release is self-contained and can be extracted and run on any machine with Python 3.10+.

**How to create a new release:**
```bash
python dcc/tracer/download_release.py              # patch bump
python dcc/tracer/download_release.py --bump minor
python dcc/tracer/download_release.py --bump major
```

**How to install a release on Windows:**
1. Download the zip from Codespaces (right-click → Download in VS Code Explorer)
2. Extract to `C:\Users\<user>\dcc\tools`
3. `pip install -r requirements.txt`
4. `python launch.py C:\path\to\your\project`

---

## v1.0.0 — 2026-05-01

**File:** [`dcc-tracer-v1.0.0.zip`](dcc-tracer-v1.0.0.zip)
**Type:** Initial release
**Packaged from:** `dcc/tracer/`

### Summary

First standalone release of the DCC Static Tracer. Packages the static analysis
dashboard as a self-contained tool that any Python developer can run against their
own codebase with no knowledge of the DCC project required.

All 5 pre-release blockers resolved across 7 phases (R1–R7).

### What's Included

| File | Description |
|------|-------------|
| `static_dashboard.html` | Interactive call graph dashboard |
| `ui/dcc-design-system.css` | Bundled CSS — no external dependency on `dcc/ui/` |
| `backend/server.py` | FastAPI backend with portable path resolution |
| `backend/__init__.py` | Backend package init |
| `static/crawler.py` | File system crawler |
| `static/graph.py` | Call graph builder |
| `static/metrics.py` | Cyclomatic complexity + metrics |
| `static/parser.py` | AST parser |
| `static/visualizer.py` | Graph visualizer |
| `static/__init__.py` | Static package init |
| `launch.py` | Single entry point — starts backend + file server + opens browser |
| `serve.py` | Standalone file server + `/api/*` proxy |
| `pyproject.toml` | pip-installable package (`dcc-tracer` CLI entry point) |
| `MANIFEST.in` | Ensures static assets included in source distributions |
| `__init__.py` | Package init (`__version__ = "1.0.0"`) |
| `requirements.txt` | `fastapi>=0.100`, `uvicorn>=0.23`, `networkx>=3.0` |

### Changes in This Release

#### R1 — Path Portability
- Replaced hard-coded 4× `.parent` + `dcc/` chain in `backend/server.py` with `_resolve_base()`
- Priority: `TRACER_TARGET` env var → `tracer/output/.target` file → `cwd`
- All 7 endpoints updated: `/static/analyze`, `/file/read`, `/file/write`, `/file/validate`, `/hot-reload`, `/environment-map`, `/pipeline/run`
- Both absolute and relative paths accepted in all request bodies

#### R2 — Launcher + Standalone File Server
- `launch.py`: accepts target dir, validates `.py` files, starts both servers, opens browser, handles Ctrl+C
- `serve.py`: serves dashboard at `/`, proxies `/api/*` → backend, no DCC-specific paths

#### R3 — pip Package
- `pyproject.toml` with `dcc-tracer` CLI entry point → `tracer.launch:main`
- `MANIFEST.in` ensures `static_dashboard.html` and `dcc-design-system.css` included in sdist

#### R4 — Docker Image
- `Dockerfile`: `python:3.11-slim`, installs deps, `TRACER_TARGET=/target`, `--no-browser` entrypoint
- `docker-compose.yml`: mounts `${TARGET_DIR}` as `/target` (read-only), exposes ports 5000 + 8000

#### R5 — Dashboard UX
- CSS path fixed: `../ui/dcc-design-system.css` → `ui/dcc-design-system.css`
- Label updated: "Backend Root Path" → "Target Directory"
- Breadcrumb updates with resolved path after analysis; 📋 copy button added
- `ui/dcc-design-system.css` bundled into `tracer/ui/` — no dependency on `dcc/ui/`

#### R6 — External README + User Guide
- `README.md` rewritten for external users (quick start, Docker, CLI reference, API reference, limitations)
- `USER_GUIDE.md` added with step-by-step instructions, troubleshooting table, theme guide

#### R7 — Distribution Packager
- `download_release.py` packages all 15 release files into a versioned zip under `releases/`
- Auto-increments version from existing zips in `releases/` (patch/minor/major via `--bump`)
- Outputs to `/workspaces/Engineering-and-Design/releases/dcc-tracer-v<version>.zip`
- Fixed: Windows path used as literal string on Linux — `sys.platform` guard added so default destination is platform-aware

### Blockers Resolved

| # | Blocker | Resolution |
|---|---------|------------|
| B1 | Hard-coded `dcc/` path in `/static/analyze` | `_resolve_base()` |
| B2 | `/file/read` restricted to DCC project root | Security boundary → `_resolve_base()` |
| B3 | Only relative paths accepted | Absolute + relative paths accepted everywhere |
| B4 | `serve.py` was DCC-specific | New `tracer/serve.py` — no DCC paths |
| B5 | No `pyproject.toml` | Created with `dcc-tracer` CLI entry point |

### Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| `python launch.py /any/python/project` starts both servers and opens dashboard | ✅ |
| Dashboard analyses target directory and renders call graph | ✅ |
| Source viewer shows function source for files in target directory | ✅ |
| `pip install ./tracer && dcc-tracer /any/python/project` works end-to-end | ✅ |
| Docker: `TARGET_DIR=/any/project docker compose up` works end-to-end | ✅ |
| No DCC-specific paths, imports, or assumptions in release files | ✅ |
| README quick-start works on clean Python env with no DCC dependencies | ✅ |
| `download_release.py` packs 15 files, 0 skipped, prints correct next steps | ✅ |
| Destination self-contained: `python launch.py <target>` works with no external files | ✅ |
| Stdlib only — no pip install required to run the packager | ✅ |

### Log References

| Log | Entry |
|-----|-------|
| `dcc/Log/update_log.md` | [`#tracer-r7-dest-fix`](../dcc/Log/update_log.md#tracer-r7-dest-fix) — Windows path fix |
| `dcc/Log/update_log.md` | [`#tracer-r7-downloader`](../dcc/Log/update_log.md#tracer-r7-downloader) — R7 completion |
| `dcc/Log/update_log.md` | [`#tracer-standalone-release`](../dcc/Log/update_log.md#tracer-standalone-release) — R1–R6 completion |
| `dcc/Log/test_log.md` | `2026-05-01` — R7 dest fix verification |
| `dcc/Log/test_log.md` | `2026-05-01` — R7 end-to-end acceptance test |
| `dcc/workplan/code_tracing/reports/release_completion_report.md` | Full phase-by-phase report |
| `dcc/workplan/code_tracing/code_tracing_release_workplan.md` | Workplan — all phases ✅ |

---

## v1.0.1 — 2026-04-21

**File:** [`dcc-tracer-v1.0.1.zip`](dcc-tracer-v1.0.1.zip)
**Type:** Patch release
**Packaged from:** `dcc/tracer/`

16 file(s) packed, 0 skipped.

### Changes

_Update this section with a summary of changes in this release._

### Log References

| Log | Entry |
|-----|-------|
| `dcc/Log/update_log.md` | _link to relevant entry_ |
| `dcc/Log/test_log.md` | _link to relevant entry_ |

---

## v1.0.2 — 2026-04-21

**File:** [`dcc-tracer-v1.0.2.zip`](dcc-tracer-v1.0.2.zip)
**Type:** Patch release
**Packaged from:** `code_tracer/`

15 file(s) packed, 1 skipped.

### Changes

_Update this section with a summary of changes in this release._

### Log References

| Log | Entry |
|-----|-------|
| `code_tracer/Log/update_log.md` | _link to relevant entry_ |
| `code_tracer/Log/test_log.md` | _link to relevant entry_ |

---

## v1.0.3 — 2026-04-21

**File:** [`dcc-tracer-v1.0.3.zip`](dcc-tracer-v1.0.3.zip)
**Type:** Patch release
**Packaged from:** `code_tracer/`

14 file(s) packed, 1 skipped.

### Changes

_Update this section with a summary of changes in this release._

### Log References

| Log | Entry |
|-----|-------|
| `code_tracer/Log/update_log.md` | _link to relevant entry_ |
| `code_tracer/Log/test_log.md` | _link to relevant entry_ |

---

## v1.0.4 — 2026-04-21

**File:** [`dcc-tracer-v1.0.4.zip`](dcc-tracer-v1.0.4.zip)
**Type:** Patch release
**Packaged from:** `code_tracer/`

15 file(s) packed, 0 skipped.

### Changes

_Update this section with a summary of changes in this release._

### Log References

| Log | Entry |
|-----|-------|
| `code_tracer/Log/update_log.md` | _link to relevant entry_ |
| `code_tracer/Log/test_log.md` | _link to relevant entry_ |

---
