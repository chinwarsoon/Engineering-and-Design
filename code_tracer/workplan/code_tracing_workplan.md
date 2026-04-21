# Workplan: Universal Interactive Python Code Tracer

## Project Overview
Development of a standalone, web-based instrumentation tool to visualize, trace, and edit Python code pipelines (e.g., DCC Engine) in real-time.

---

## Phase 1: Core Instrumentation Engine (Week 1)
**Goal:** Build the "observer" layer to intercept Python's execution flow.
* **Global Trace Hook:** ✅ Implemented `sys.settrace` to capture `call`, `line`, and `return` events.
* **State Snapshotting:** ✅ Captures `frame.f_locals` and return value on `return` events.
* **Call Stack Mapper:** ✅ Reconstructs function call hierarchy into a tree structure.
* **Performance Profiling:** ✅ Integrates `time.perf_counter()` for per-function duration.

### Phase 1b: Static Analysis Module ✅ COMPLETED (2026-04-20)
**Goal:** AST-based code analysis without execution — crawl, parse, graph, visualise.

**Deliverables:**

| File | Purpose | Status |
|---|---|---|
| `tracer/static/__init__.py` | Sub-package public API | ✅ Done |
| `tracer/static/crawler.py` | Directory walker, collects `.py` files | ✅ Done |
| `tracer/static/metrics.py` | Cyclomatic complexity, loop/try counters | ✅ Done |
| `tracer/static/parser.py` | AST extractor — functions, args, calls | ✅ Done |
| `tracer/static/graph.py` | networkx DiGraph — caller→callee edges | ✅ Done |
| `tracer/static/visualizer.py` | pyvis / vis-network HTML generator | ✅ Done |
| `tracer/static_dashboard.html` | VS Code-layout interactive dashboard | ✅ Done |
| `tracer/backend/server.py` | `/static/analyze`, `/static/graph`, `/static/report` endpoints | ✅ Done |
| `tracer/output/call_graph.json` | Generated graph data (DCC workflow) | ✅ Done |
| `tracer/output/call_graph.html` | Interactive HTML network (DCC workflow) | ✅ Done |

**Analysis Results (DCC workflow):**
- 137 modules crawled, 754 functions extracted, 0 parse errors
- 737 call edges resolved, 383 entry points, 233 complexity hotspots (CC ≥ 5)
- Top hotspot: `apply_validation` CC=100 (`processor_engine.calculations.validation`)

**Key parameters extracted per function:**
- Name, qualified name, start/end line numbers
- Arguments with type annotations and default values
- Cyclomatic complexity, if/for/while/try/except counts
- Raw call edges (caller → callee)
- Docstring and decorators

**Features implemented:**
1. ✅ Directory crawler with agent_rule §3 exclusions (backup, test, archive, dot-folders)
2. ✅ AST parser using `ast` module — no code execution
3. ✅ Complexity metrics: cyclomatic complexity, loop count, try/except count
4. ✅ Call graph with networkx DiGraph and skip-list for generic names
5. ✅ Entry-point detection (in-degree 0 nodes)
6. ✅ Complexity heatmap (colour-coded: green→yellow→orange→red)
7. ✅ Interactive HTML network via pyvis / vis-network CDN fallback
8. ✅ VS Code-layout dashboard with Graph / Metrics / Heatmap / Entry Points panels
9. ✅ FastAPI endpoints: `/static/analyze`, `/static/graph`, `/static/report`
10. ✅ Output files saved to `tracer/output/`

**Dependencies added to `dcc.yml`:**
- `networkx>=3.0`
- `pyvis>=0.3.2`

### Phase 1c: Static Dashboard — File Tree & Function Inspector ✅ COMPLETED (2026-04-20)
**Goal:** Upgrade `static_dashboard.html` with a navigable file tree and a rich function inspector panel so users can fully examine code context, relationships, I/O, and source without leaving the dashboard.

#### Layout
```
┌──────────────────────────────────────────────────────────────────────────┐
│ Title Bar                                                                │
├──────┬──────────────────┬──────────────────────────┬────────────────────┤
│ Icon │ LEFT SIDEBAR     │ CONTENT (graph/metrics/  │ RIGHT INSPECTOR    │
│ Bar  │ ─────────────    │  heatmap/entries)        │ ──────────────     │
│ 48px │ Tab A: Controls  │                          │ Function detail    │
│      │ Tab B: File Tree │                          │ ─ Signature        │
│      │ ─────────────    │                          │ ─ Docstring        │
│      │ 📁 ai_ops_engine │                          │ ─ I/O table        │
│      │  📄 risk_analyzer│                          │ ─ Callers list     │
│      │   ⚡ analyze     │                          │ ─ Callees list     │
│      │   ⚡ compute_risk│                          │ ─ Metrics          │
│      │ 📁 initiation_.. │                          │ ─ Source code      │
│      │  ...             │                          │                    │
├──────┴──────────────────┴──────────────────────────┴────────────────────┤
│ Status Bar                                                               │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Deliverables

| Component | Description | Status |
|---|---|---|
| Left sidebar — Tab A | Existing load/filter/legend controls (unchanged) | ✅ Done |
| Left sidebar — Tab B | File tree: 📁 package → 📄 module → ⚡ function | ✅ Done |
| Right inspector panel | Full function detail panel, 320px, collapsible | ✅ Done |
| Graph node click | Opens right inspector (replaces floating overlay) | ✅ Done |
| Tree function click | Selects graph node + opens inspector | ✅ Done |
| Tree file click | Filters graph to that file's functions only | ✅ Done |
| Tree package click | Filters graph to that package's functions | ✅ Done |
| Caller/callee links | Clickable — navigate to that function in graph + inspector | ✅ Done |
| Source code viewer | Read-only, fetched via `/api/file/read`, lines `start_line`–`end_line` | ✅ Done |
| Graph neighbourhood | Double-click node → isolate 1-hop subgraph | ✅ Done |
| 🌳 Tree icon bar btn | Toggles file tree tab in left sidebar | ✅ Done |

#### Left Sidebar — File Tree (Tab B)
- Built from `ALL_NODES` grouped by `module` field, split on `.` to reconstruct folder hierarchy
- Three node types with distinct icons and indentation:
  - 📁 **Package** — top-level dotted path segment (e.g. `ai_ops_engine`)
  - 📄 **Module** — leaf module file (e.g. `risk_analyzer`)
  - ⚡ **Function** — individual function/method with CC colour dot
- Clicking a **function** → selects it in the vis-network graph AND opens right inspector
- Clicking a **module** → filters graph to show only that module's functions
- Clicking a **package** → filters graph to show that package's functions
- Search box at top filters tree nodes by name in real-time
- Expand/collapse all buttons
- CC colour dot (green/yellow/orange/red) next to each function node
- Entry-point star ★ badge on entry-point functions

#### Right Inspector Panel
Triggered by clicking any function node (in graph or tree). Fixed 320px width, slides in from right, collapsible with a toggle button.

| Section | Source field | Display |
|---|---|---|
| **Header** | `label`, `class_name`, `is_async`, entry-point | Name + badges |
| **Signature** | `args[]` (name, annotation, default, kind) | Reconstructed `def name(…)` |
| **Docstring** | `docstring` | Formatted text block |
| **Metrics** | `cyclomatic_complexity`, `loop_count`, `try_except_count`, lines | Badge row |
| **Arguments (I)** | `args[]` | Table: name / type / default / kind |
| **Returns (O)** | Parsed from `docstring` `Returns:` section | Text block |
| **Callers** | `ALL_EDGES` where `target === nodeId` | Clickable list with CC badge |
| **Callees** | `ALL_EDGES` where `source === nodeId` | Clickable list with CC badge |
| **Raw Calls** | `raw_calls[]` | Dim monospace list (unresolved) |
| **Source Code** | `GET /api/file/read` → slice `start_line`–`end_line` | Read-only `<pre>` block |

#### Data Flow
```
loadGraphData(data)
  → buildFileTree(ALL_NODES)      groups by module path → tree structure
  → buildEdgeIndex(ALL_EDGES)     callerMap[target] = [sources]
                                  calleeMap[source] = [targets]

click node (graph or tree)
  → openInspector(nodeId)
      → find node in ALL_NODES
      → render signature, docstring, metrics, args table
      → lookup callerMap[nodeId]  → render callers list
      → lookup calleeMap[nodeId]  → render callees list
      → fetch /api/file/read {path: node.file}
          → slice lines start_line..end_line
          → display in <pre> with line numbers

click caller/callee link
  → openInspector(linkedNodeId)
  → network.focus(linkedNodeId, {scale:1.5, animation:true})
  → highlight node in tree
```

#### Scope Boundaries
- Source code display is **read-only** (no Monaco editor — that is Phase 4)
- No live code execution
- No file writing
- All existing panels (Graph, Metrics, Heatmap, Entry Points) preserved unchanged
- Backend: no new endpoints needed — `/api/file/read` already exists

#### File Changed
- `tracer/static_dashboard.html` — full rebuild of sidebar + add right inspector + tree JS

---


**Goal:** Create the backend server and file I/O layer.
* **FastAPI Backend:** Set up a server with WebSocket support for real-time trace streaming.
* **Source Resolver:** API endpoints to locate and read `.py` files using `inspect.getsourcefile`.
* **Dynamic Module Loader:** Implementation of `importlib.util` to execute targeted code within the tracer's context.

## Phase 3: Interactive Visualization UI (Week 3)
**Goal:** Build the "Command Center" dashboard.
* **Execution Tree View:** Interactive, collapsible tree showing the calling sequence (Modules > Functions).
* **Variable Inspector:** Side panel displaying In/Out parameters and local variable states.
* **Time & Status Indicators:** Visual badges for execution time and success/error status on each node.

## Phase 4: IDE Integration (Edit & Save) (Week 4)
**Goal:** Enable the "Live Editing" capability.
* **Monaco Editor Integration:** Embed the VS Code editor engine into the web interface.
* **Safety Validator:** Backend service to run `ast.parse()` on edited code to prevent saving syntax errors.
* **Hot-Reload System:** Mechanism to overwrite files and clear `sys.modules` cache for immediate re-tracing.

## Phase 5: Pipeline Sandbox & Integration (Week 5)
**Goal:** Connect the tracer to the actual DCC engine or any external repo.
* **Environment Mapping:** Resolve WSL/Ubuntu paths to ensure file-system parity.
* **Mock Data Injector:** UI for users to define a set of input parameters and trigger the pipeline.
* **Truth Table Generator:** Automated logic tracing for "Calculated Columns" (e.g., `submission_closed`).

## Phase 6: Final Packaging & CLI (Week 6)
**Goal:** Finalize the standalone tool.
* **CLI Entry Point:** Create a `pip`-installable command to launch the tracer on any directory.
* **Performance Heatmap:** Visual highlighting of bottlenecks in the call tree.
* **Session Persistence:** Ability to save and export trace logs for future comparison.

## phase 7: Documentation & User Support (Week 7)
**Goal:** Create a comprehensive documentation and user support system.
* **User Guide:** Detailed instructions on how to use the tool.
* **API Reference:** Documentation for the backend API endpoints.
* **Troubleshooting Guide:** Common issues and their solutions.

---

## Technical Stack
* **Backend:** Python, FastAPI, WebSockets.
* **Frontend:** React, Tailwind CSS, Lucide Icons.
* **Visualization:** React-Flow or D3.js, vis-network (static dashboard), pyvis.
* **Editor:** Microsoft Monaco Editor.
* **Analysis:** `ast`, `inspect`, `sys.monitoring`, `networkx`, `pyvis`.
* **Static Analysis:** `ast` (parsing), `networkx` (graph), `pyvis` / vis-network (HTML network).
* **Output:** `tracer/output/` — `call_graph.json`, `call_graph.html`.

---

## Deployment & Runtime Notes

### Starting the servers
```bash
# Terminal 1 — FastAPI backend (must use dcc conda env)
/opt/conda/envs/dcc/bin/python3 tracer/backend/server.py

# Terminal 2 — File server + API proxy
python3 serve.py
```

### serve.py proxy
`serve.py` (port 5000) proxies all `/api/*` requests to the FastAPI backend (port 8000) internally.
This means the browser only ever talks to port 5000 — no cross-origin issues in any environment
(local, GitHub Codespaces, Gitpod, etc.).

### GitHub Codespaces
- Port 5000 must be **Public** (or at minimum forwarded) in the Ports panel.
- Port 8000 does **not** need to be public — all browser traffic goes through the port 5000 proxy.
- The backend must be started with `/opt/conda/envs/dcc/bin/python3` (system `python3` lacks `fastapi`).

### Required packages in dcc conda env
| Package | Purpose |
|---|---|
| `fastapi` | Backend API server |
| `uvicorn` | ASGI server for FastAPI |
| `networkx>=3.0` | Call graph DiGraph |
| `pyvis>=0.3.2` | Interactive HTML network (optional, falls back to vis-network CDN) |

Install if missing:
```bash
/opt/conda/envs/dcc/bin/pip install networkx pyvis fastapi uvicorn
```