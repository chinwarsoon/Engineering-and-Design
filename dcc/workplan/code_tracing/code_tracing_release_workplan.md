# Workplan: DCC Static Tracer — Standalone Release
**Status:** AWAITING APPROVAL
**Depends on:** `code_tracing_workplan.md` Phases 1–6 (all complete)

---

## Objective

Package the existing static analysis tracer (`tracer/`) as a self-contained,
independently installable tool that any Python developer can run against their
own codebase — with no knowledge of the DCC project required.

---

## Scope

| In scope | Out of scope |
|---|---|
| Static analysis dashboard (`static_dashboard.html`) | Runtime `sys.settrace` tracing UI |
| FastAPI backend (`backend/server.py`) | Monaco editor / live code editing (Phase 4) |
| Portable path resolution | DCC pipeline-specific endpoints (`/pipeline/run`, `/truth-table-generator`, etc.) |
| Launcher script + CLI entry point | React frontend rebuild |
| pip-installable package (`pyproject.toml`) | Cloud hosting / SaaS deployment |
| Docker image | Authentication / multi-user support |
| Updated README for external users | |

---

## Current Blockers (must fix before release)

| # | File | Issue | Impact |
|---|---|---|---|
| B1 | `backend/server.py` `/static/analyze` | `project_root` resolved with hard-coded 4× `.parent` + `dcc/` prefix — breaks on any other layout | Analysis fails for external users |
| B2 | `backend/server.py` `/file/read` | Security check restricts reads to `project_root` — blocks reading user's own codebase | Source viewer broken |
| B3 | `backend/server.py` `/static/analyze` | Path accepted as relative to `dcc/` only — no support for absolute paths | Users cannot point to arbitrary directories |
| B4 | `serve.py` | Proxy and file server are DCC-specific (`DIRECTORY`, default HTML path) | External users cannot use `serve.py` as-is |
| B5 | No `pyproject.toml` | Tool cannot be installed via `pip` | High friction for external users |

---

## Phases

---

### Phase R1 — Path Portability (server.py)
**Goal:** Make `server.py` work with any target directory, not just `dcc/workflow`.
**Effort:** ~2 hours

#### R1.1 — Configurable analysis root
- Add `TRACER_TARGET` environment variable support.
- On startup, if `TRACER_TARGET` is set, use it as the base for all path resolution.
- Fall back to a `.target` file written by the launcher (see Phase R2).
- Fall back to current working directory as last resort.

```python
# Resolution priority in server.py
def _resolve_base() -> Path:
    if os.environ.get('TRACER_TARGET'):
        return Path(os.environ['TRACER_TARGET']).resolve()
    target_file = Path(__file__).parent.parent / 'output' / '.target'
    if target_file.exists():
        return Path(target_file.read_text().strip()).resolve()
    return Path.cwd()
```

#### R1.2 — Fix `/static/analyze` path resolution
- Replace hard-coded `parent.parent.parent.parent / "dcc"` chain with `_resolve_base()`.
- Accept both relative paths (relative to base) and absolute paths.
- Return a clear `404` with the resolved path in the error message if not found.

#### R1.3 — Fix `/file/read` security boundary
- Replace `project_root` check with `_resolve_base()` — allow reads anywhere under the configured target.
- Keep the path traversal guard (no `..` escaping above the target root).

**Files changed:** `tracer/backend/server.py`

---

### Phase R2 — Launcher Script
**Goal:** Single entry point that wires everything together for a user.
**Effort:** ~2 hours

#### R2.1 — `tracer/launch.py`
Create a launcher that:
1. Accepts `target` directory as a positional argument.
2. Validates the path exists and contains `.py` files.
3. Writes the resolved path to `tracer/output/.target`.
4. Sets `TRACER_TARGET` env var.
5. Starts the FastAPI backend (`server.py`) on a configurable port (default 8000).
6. Starts a minimal file server for `static_dashboard.html` on a configurable port (default 5000).
7. Prints the dashboard URL and opens it in the browser.

```
Usage:
  python tracer/launch.py /path/to/any/python/project
  python tracer/launch.py /path/to/any/python/project --port 8000 --serve-port 5000 --no-browser
```

#### R2.2 — Minimal standalone file server
- Serve `static_dashboard.html` and proxy `/api/*` → backend.
- Extracted from `dcc/serve.py` into `tracer/serve.py` — no DCC-specific paths.

**Files created:** `tracer/launch.py`, `tracer/serve.py`

---

### Phase R3 — pip Package
**Goal:** `pip install dcc-tracer` works and provides a `dcc-tracer` CLI command.
**Effort:** ~1 hour

#### R3.1 — `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "dcc-tracer"
version = "1.0.0"
description = "Static call-graph analyser and interactive dashboard for any Python codebase"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100",
    "uvicorn>=0.23",
    "networkx>=3.0",
]

[project.optional-dependencies]
pyvis = ["pyvis>=0.3.2"]

[project.scripts]
dcc-tracer = "tracer.launch:main"
```

#### R3.2 — `tracer/MANIFEST.in`
Ensure `static_dashboard.html` and `dcc-design-system.css` are included in the package.

```
include tracer/static_dashboard.html
include tracer/ui/dcc-design-system.css
recursive-include tracer/static *.py
```

#### R3.3 — `tracer/__init__.py` version bump
Set `__version__ = "1.0.0"`.

**Files created/changed:** `tracer/pyproject.toml`, `tracer/MANIFEST.in`, `tracer/__init__.py`

---

### Phase R4 — Docker Image
**Goal:** Zero-dependency option — user only needs Docker.
**Effort:** ~1 hour

#### R4.1 — `tracer/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /tracer
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn networkx
EXPOSE 8000 5000
ENV TRACER_TARGET=/target
ENTRYPOINT ["python", "launch.py", "/target", "--no-browser"]
```

#### R4.2 — `tracer/docker-compose.yml`
```yaml
services:
  tracer:
    build: .
    ports:
      - "5000:5000"
      - "8000:8000"
    volumes:
      - ${TARGET_DIR}:/target:ro
```

Usage:
```bash
TARGET_DIR=/path/to/project docker compose up
# Dashboard at http://localhost:5000
```

**Files created:** `tracer/Dockerfile`, `tracer/docker-compose.yml`

---

### Phase R5 — Dashboard: Configurable Root Path UI
**Goal:** Let users change the analysis target from within the dashboard (no CLI restart needed).
**Effort:** ~1 hour

#### R5.1 — Update Controls sidebar
- Change "Backend Root Path" label to "Target Directory".
- Accept absolute paths in addition to relative paths.
- Show the resolved absolute path in the breadcrumb after a successful analysis.
- Add a "📋 Copy path" button next to the breadcrumb.

#### R5.2 — Update `loadSavedGraph` fallback message
- If no graph exists yet, show "Enter a directory path and click Analyse" instead of the current generic message.

**Files changed:** `tracer/static_dashboard.html`

---

### Phase R6 — External README
**Goal:** Replace the DCC-specific README with one written for external users.
**Effort:** ~1 hour

#### R6.1 — `tracer/README.md` rewrite
Sections:
1. **What it does** — one paragraph, screenshot placeholder
2. **Quick start (3 commands)** — pip install, run, open browser
3. **Docker quick start** — 2 commands
4. **What you get** — dashboard feature list (call graph, metrics, heatmap, inspector, flow tree, etc.)
5. **Requirements** — Python 3.10+, no other project dependencies
6. **CLI reference** — all `dcc-tracer` flags
7. **API reference** — `/static/analyze`, `/static/graph`, `/static/report`, `/file/read`
8. **Limitations** — static analysis only (no runtime tracing UI in this release), no auth

**Files changed:** `tracer/README.md`

---

## Deliverables Summary

| Phase | Deliverable | Files |
|---|---|---|
| R1 | Portable path resolution | `backend/server.py` |
| R2 | Launcher + standalone file server | `tracer/launch.py`, `tracer/serve.py` |
| R3 | pip package | `tracer/pyproject.toml`, `tracer/MANIFEST.in`, `tracer/__init__.py` |
| R4 | Docker image | `tracer/Dockerfile`, `tracer/docker-compose.yml` |
| R5 | Dashboard UX for external users | `tracer/static_dashboard.html` |
| R6 | External README | `tracer/README.md` |

---

## Acceptance Criteria

- [ ] `python tracer/launch.py /any/python/project` starts both servers and opens the dashboard
- [ ] Dashboard analyses the target directory and renders the call graph
- [ ] Source code viewer shows function source for files in the target directory
- [ ] `pip install ./tracer && dcc-tracer /any/python/project` works end-to-end
- [ ] Docker: `TARGET_DIR=/any/project docker compose up` works end-to-end
- [ ] No DCC-specific paths, imports, or assumptions remain in the release files
- [ ] README quick-start tested on a clean Python environment with no DCC dependencies

---

## Estimated Effort

| Phase | Effort |
|---|---|
| R1 Path portability | 2 h |
| R2 Launcher | 2 h |
| R3 pip package | 1 h |
| R4 Docker | 1 h |
| R5 Dashboard UX | 1 h |
| R6 README | 1 h |
| **Total** | **~8 h** |

---

## Dependencies

- All Phase 1–6 items in `code_tracing_workplan.md` must remain unchanged
- `dcc-design-system.css` must be copied into `tracer/` (or bundled inline) so the dashboard works without the `dcc/ui/` folder
- No changes to `dcc/serve.py` or any other DCC project files
