# Code Tracer

A standalone static call-graph analyser and interactive dashboard for any Python codebase.
Point it at any directory, click Analyse, and explore your code's structure visually.

---

## What it does

Code Tracer crawls your Python project, parses every function with the AST,
builds a directed call-dependency graph, and serves an interactive dashboard where you can:

- **Call Graph** — visualise caller/callee relationships as a force-directed network
- **Metrics Table** — cyclomatic complexity, loop count, try/except count, arg count per function
- **Complexity Heatmap** — colour-coded cards sorted by complexity
- **Entry Points** — functions with no callers (likely your public API or main functions)
- **Function Inspector** — signature, docstring, parameters, callers, callees, source code viewer
- **Flow Tree** — persistent sidebar showing the call chain for any selected function
- **Error Analysis** — static risk signals (unhandled exceptions, dead code, high complexity)

---

## Project Structure

```
code_tracer/
├── engine/                  <- core tracer source code
│   ├── backend/             <- FastAPI server (server.py)
│   ├── cli/                 <- CLI entry point (main.py)
│   ├── core/                <- trace engine (trace_engine.py)
│   ├── frontend/            <- React dashboard components
│   ├── static/              <- static analysis modules (crawler, parser, graph, metrics)
│   ├── pipeline_sandbox/    <- pipeline runner for testing
│   ├── tests/               <- unit tests
│   ├── utils/               <- trace filters and helpers
│   ├── output/              <- generated call graph outputs
│   ├── launch.py            <- main entry point
│   ├── serve.py             <- file server + proxy
│   ├── pyproject.toml       <- package definition
│   ├── Dockerfile           <- Docker build
│   ├── docker-compose.yml   <- Docker Compose
│   └── README.md            <- engine-level docs
├── ui/
│   └── tracer_pro.html      <- standalone dashboard UI
├── workplan/
│   ├── reports/             <- phase completion reports (phase1-6 + release)
│   ├── archive/             <- v1 workplan archive
│   ├── code_tracing_workplan.md
│   ├── code_tracing_release_workplan.md
│   └── python_inspector_workplan.md
├── releases/
│   ├── dcc-tracer-v1.0.0.zip
│   ├── dcc-tracer-v1.0.1.zip
│   └── RELEASE_HISTORY.md
└── Log/
    ├── update_log.md
    ├── issue_log.md
    └── test_log.md
```

---

## Quick Start

```bash
# Install
pip install ./engine

# Run against any Python project
code-tracer /path/to/your/project

# Dashboard opens at http://localhost:5000
```

## Docker

```bash
TARGET_DIR=/path/to/your/project docker compose -f engine/docker-compose.yml up
```

## Manual (no install)

```bash
python engine/launch.py /path/to/your/project
```

---

## Requirements

- Python 3.10+
- `fastapi`, `uvicorn`, `networkx`

---

## Migration Note

This project was migrated from `dcc/tracer/` on 2026-04-19.
Original files remain in `dcc/tracer/` for reference.
All workplans, reports, and releases have been consolidated here.
