# Workplan: Universal Interactive Python Code Tracer

## Project Overview
Development of a standalone, web-based instrumentation tool to visualize, trace, and edit Python code pipelines (e.g., DCC Engine) in real-time.

---

## Phase 1: Core Instrumentation Engine (Week 1)
**Goal:** Build the "observer" layer to intercept Python's execution flow.
* **Global Trace Hook:** Implement `sys.settrace` or `sys.monitoring` to capture `call`, `line`, and `return` events.
* **State Snapshotting:** Logic to capture `frame.f_locals` (inputs/locals) and the return value (`arg`) upon `return` events.
* **Call Stack Mapper:** Reconstruct the hierarchy of function calls into a tree structure.
* **Performance Profiling:** Integrate `time.perf_counter_ns()` to calculate execution duration per function.

## Phase 2: Communication & File Bridge (Week 2)
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

---

## Technical Stack
* **Backend:** Python, FastAPI, WebSockets.
* **Frontend:** React, Tailwind CSS, Lucide Icons.
* **Visualization:** React-Flow or D3.js.
* **Editor:** Microsoft Monaco Editor.
* **Analysis:** `ast`, `inspect`, `sys.monitoring`.