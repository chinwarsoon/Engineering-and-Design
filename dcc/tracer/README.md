# DCC Static Tracer

A static call-graph analyser and interactive dashboard for any Python codebase.
Point it at any directory, click Analyse, and explore your code's structure visually.

![Dashboard screenshot placeholder]

---

## What it does

DCC Static Tracer crawls your Python project, parses every function with the AST,
builds a directed call-dependency graph, and serves an interactive dashboard where you can:

- **Call Graph** — visualise caller/callee relationships as a force-directed network
- **Metrics Table** — cyclomatic complexity, loop count, try/except count, arg count per function
- **Complexity Heatmap** — colour-coded cards sorted by complexity
- **Entry Points** — functions with no callers (likely your public API or main functions)
- **Function Inspector** — signature, docstring, parameters, callers, callees, source code viewer
- **Flow Tree** — persistent sidebar showing the call chain for any selected function
- **Error Analysis** — static risk signals (unhandled exceptions, dead code, high complexity)

---

## Quick start (3 commands)

```bash
# 1. Install
pip install ./tracer          # from the dcc/ directory, or:
pip install dcc-tracer        # once published to PyPI

# 2. Run against any Python project
dcc-tracer /path/to/your/project

# 3. Dashboard opens automatically at http://localhost:5000
```

---

## Docker quick start

```bash
# Build and run — mount your project as /target
TARGET_DIR=/path/to/your/project docker compose -f tracer/docker-compose.yml up

# Dashboard at http://localhost:5000
```

---

## Manual start (no install)

```bash
# From the dcc/ directory:
python tracer/launch.py /path/to/your/project

# Custom ports:
python tracer/launch.py /path/to/your/project --port 8000 --serve-port 5000

# Headless (no browser):
python tracer/launch.py /path/to/your/project --no-browser
```

---

## What you get

| Feature | Description |
|---|---|
| Call Graph | Interactive vis-network graph, zoom/pan, click to inspect |
| Node colours | Green = low CC, Yellow = medium, Orange = high, Red = very high |
| Entry points | Shown as ★ stars in the graph |
| Metrics table | Sortable, exportable to CSV |
| Heatmap | Filterable by minimum complexity |
| Inspector | 7 tabs: Info, Signature, Trace, Flow, Seq, Errors, Source |
| Source viewer | Read-only code view with line numbers |
| Flow Tree | Sidebar showing callers → selected → callees |
| Themes | Dark, Light, Sky, Ocean, Presentation |
| Resizable panels | Drag sidebar and inspector panel edges |

---

## Requirements

- Python 3.10+
- `fastapi`, `uvicorn`, `networkx` (installed automatically via pip)
- No other project dependencies — works on any Python codebase

---

## CLI reference

```
dcc-tracer <target> [options]

Positional:
  target              Path to the Python project directory to analyse

Options:
  --port INT          Backend API port (default: 8000)
  --serve-port INT    Dashboard file server port (default: 5000)
  --no-browser        Do not open browser automatically
  -h, --help          Show this help message
```

You can also set the target via environment variable instead of the CLI:

```bash
export TRACER_TARGET=/path/to/your/project
python tracer/backend/server.py   # backend only, no file server
```

---

## API reference

All endpoints are available at `http://localhost:8000` (or your configured port).
The dashboard proxies them via `/api/*` on port 5000.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/static/analyze` | Crawl and analyse a directory. Body: `{"root": "<path>"}` |
| GET | `/static/graph` | Return the last saved call graph JSON |
| GET | `/static/report` | Return per-function metrics table |
| POST | `/file/read` | Read a source file. Body: `{"path": "<path>"}` |
| GET | `/health` | Health check |

Paths in request bodies can be absolute or relative to the configured target directory.

---

## Limitations

- Static analysis only — no runtime `sys.settrace` tracing UI in this release
- No authentication or multi-user support
- Very large codebases (10 000+ functions) may be slow to render in the browser
- Dynamic imports and `__getattr__`-based calls are not resolved

---

## Running inside the DCC project

If you are using the tracer within the DCC project itself (not as a standalone tool),
start both servers with the existing `serve.py`:

```bash
# Terminal 1 — backend
/opt/conda/envs/dcc/bin/python tracer/backend/server.py

# Terminal 2 — file server + proxy
python serve.py

# Dashboard at http://localhost:5000/tracer/static_dashboard.html
```

Set `TRACER_TARGET` or use the Target Directory input in the dashboard Controls panel
to point at any directory you want to analyse.
