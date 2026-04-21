# DCC Static Tracer — User Instructions

> Analyse any Python project's call graph in minutes, with no setup beyond `pip install`.

---

## 1. Installation

### Option A — pip (recommended)

```bash
# From the dcc/ directory:
pip install ./tracer

# Verify:
dcc-tracer --help
```

### Option B — run directly (no install)

```bash
# Requires: pip install fastapi uvicorn networkx
python tracer/launch.py /path/to/your/project
```

### Option C — Docker (zero Python setup)

```bash
TARGET_DIR=/path/to/your/project docker compose -f tracer/docker-compose.yml up
```

---

## 2. Running the tracer

### Basic usage

```bash
dcc-tracer /path/to/your/project
```

This will:
1. Validate the target directory contains `.py` files
2. Start the FastAPI backend on port 8000
3. Start the dashboard file server on port 5000
4. Open `http://localhost:5000` in your browser automatically

### Custom ports

```bash
dcc-tracer /path/to/your/project --port 8001 --serve-port 5001
```

### Headless (no browser)

```bash
dcc-tracer /path/to/your/project --no-browser
```

### Environment variable (advanced)

If you start the backend manually, set the target via env var:

```bash
export TRACER_TARGET=/path/to/your/project
python tracer/backend/server.py
```

---

## 3. Using the dashboard

### Step 1 — Analyse a directory

1. Click the **⚙️ Controls** icon in the left icon bar
2. In the **Target Directory** field, enter a path (absolute or relative to your project root)
3. Click **▶ Analyse**
4. Wait for the status to show `✓ Done (N fns)`

The breadcrumb at the top shows the resolved path. Click **📋** to copy it.

### Step 2 — Explore the call graph

- **Click** a node to highlight its direct connections and open the Inspector
- **Double-click** a node to isolate its 1-hop subgraph
- **Double-click** the background to restore the full graph

### Step 3 — Use the tabs

| Tab | What it shows |
|-----|---------------|
| 🕸️ Call Graph | Force-directed network of all functions |
| 📊 Metrics | Sortable table of all functions with complexity metrics |
| 🔥 Heatmap | Colour-coded cards sorted by cyclomatic complexity |
| 🎯 Entry Points | Functions with no callers (public API / main functions) |

### Step 4 — Inspect a function

Click any node or function name to open the **Inspector** panel (right side):

| Inspector tab | Content |
|---------------|---------|
| Info | Module, file, line range, entry point status, metrics |
| Sig | Function signature and docstring |
| Trace | Callers and callees (clickable) |
| Flow | Visual swimlane: callers → selected → callees |
| Seq | Trace table with parameter types and risk outcome |
| Errors | Static risk signals (high complexity, missing error handling, dead code) |
| Code | Read-only source code viewer with line numbers |

### Step 5 — Navigate with the sidebar

The **📂 File Tree** panel (left sidebar) shows your project structure:
- Click a **package/module** to filter the graph to that module
- Click a **function** to focus the graph and open the Inspector
- The **Flow Tree** section below updates to show the call chain
- The **Parameters** section shows the selected function's signature

---

## 4. Loading a saved graph

If you have previously run an analysis, click **📂 Load Saved** to reload the last
`tracer/output/call_graph.json` without re-running the analysis.

---

## 5. Exporting metrics

On the **📊 Metrics** tab, click **📥 Export CSV** to download the full metrics table.

---

## 6. Themes

Click the theme button in the top-right corner to switch between:
Dark · Light · Sky · Ocean · Presentation

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| `dcc-tracer: command not found` | Run `pip install ./tracer` first, or use `python tracer/launch.py` |
| `ModuleNotFoundError: fastapi` | Run `pip install fastapi uvicorn networkx` |
| Dashboard shows "Failed to fetch" | Make sure the backend is running on port 8000 (check terminal output) |
| "Directory not found" error | Check the path in the Target Directory field — use an absolute path |
| 0 nodes in graph | The target directory may have no `.py` files, or all files are in excluded folders (`test`, `archive`, `.venv`, etc.) |
| Source viewer shows "Failed to load source" | The file path in the graph data doesn't match the current target. Re-run Analyse. |

---

## 8. What gets excluded from analysis

The crawler automatically skips these directories:

- `__pycache__`, `.git`, `.github`, `.venv`, `venv`, `env`
- `node_modules`, `archive`, `backup`, `backups`
- Any directory starting with `test` or `.`

---

## 9. Running inside the DCC project (existing users)

Nothing changes for existing DCC users. The original `dcc/serve.py` and backend startup
commands continue to work as before.

To analyse the DCC workflow directory specifically:

```bash
# In the Controls panel, enter:
workflow

# Or use an absolute path:
/workspaces/Engineering-and-Design/dcc/workflow
```
