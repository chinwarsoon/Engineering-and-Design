# PyCode Tracer — User Instructions

> Analyse any Python project's call graph in minutes, with no setup beyond `pip install`.

---

## 1. Installation

### Option A — pip (recommended)

```bash
# From the code_tracer/engine directory:
pip install .

# Verify:
dcc-tracer --help
```

### Option B — run directly (no install)

```bash
# Requires: pip install fastapi uvicorn networkx
python engine/launch.py /path/to/your/project
```

### Option C — Docker (zero Python setup)

```bash
TARGET_DIR=/path/to/your/project docker compose -f engine/docker-compose.yml up
```

---

## 2. Running the tracer

### Basic usage

```bash
# If installed via pip:
dcc-tracer /path/to/your/project

# If running from source:
python engine/launch.py /path/to/your/project
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

---

## 3. Using the dashboard

### Step 1 — Load or Analyse a project

1. Click the **📥 Load Project** icon in the left icon bar (default on startup)
2. In the **Target Directory** field, enter a path (absolute or relative)
3. Click **▶ Analyse**
4. Wait for the status to show `✓ Done (N fns)`

The breadcrumb in the status bar (bottom) shows the resolved path.

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
- Click a **package/module** to filter the graph to that module and auto-select the first function
- Click a **function** to focus the graph and open the Inspector
- The **Flow Tree** section below updates to show the call chain

---

## 4. Loading a saved graph

If you have previously run an analysis, click **📂 Load Saved** in the Load Project panel to reload the last `engine/output/call_graph.json` without re-running the analysis.

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
| `dcc-tracer: command not found` | Run `pip install ./engine` first, or use `python engine/launch.py` |
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
