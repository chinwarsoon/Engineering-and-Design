# Workplan: Universal Interactive Python Code Tracer

## Project Overview
Development of a standalone, web-based instrumentation tool designed to visualize, trace, and edit Python code pipelines within the DCC ecosystem in real-time. This tool will allow developers to debug complex data transformations by observing state changes at every function call.

---

## Core Engine & Functions
The tracer will be powered by a new `TracerEngine` located in `dcc/workflow/code_tracing/tracer_engine.py`.

### 1. TracerEngine (The Core)
- **`initialize_tracer(config)`**: Configures the trace hooks, depth limits, and ignored modules (e.g., standard libraries).
- **`start_tracing()` / `stop_tracing()`**: Toggles the global `sys.settrace` or `sys.monitoring` hooks.
- **`trace_dispatch(frame, event, arg)`**: The main hook function to intercept `call`, `line`, `return`, and `exception` events.
- **`capture_frame_state(frame)`**: Extracts `f_locals` and `f_globals` for the current execution context.
- **`serialize_context(data)`**: Recursively serializes Python objects into JSON-compatible formats, handling circular references and large DataFrames.
- **`log_event(event_type, metadata)`**: Buffers events for real-time streaming or disk persistence.

### 2. Bridge & API Layer (`tracer_api.py`)
- **`stream_trace_data()`**: WebSocket endpoint for real-time UI updates.
- **`resolve_source_code(filepath)`**: Returns the content of the target file for UI visualization.
- **`execute_sandbox(target_func, inputs)`**: Runs code within the tracer's context.

---

## Phase Breakdown

### Phase 1: Core Instrumentation Engine
**Goal:** Build the "observer" layer to intercept Python's execution flow.
- **Achievements:** Successful interception of function calls within `dcc/workflow/processor_engine.py`.
- **Deliverables:** `dcc/workflow/code_tracing/tracer_engine.py`.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_1_engine_report.md`.
- **Logs:** Initialization logs in `dcc/output/logs/tracer_init.json`.

### Phase 2: Communication & File Bridge
**Goal:** Create the backend server and file I/O layer.
- **Achievements:** Real-time data streaming between backend and test clients via FastAPI.
- **Deliverables:** `dcc/workflow/code_tracing/tracer_api.py`, `dcc/workflow/code_tracing/communication_bridge.py`.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_2_bridge_report.md`.
- **Logs:** Socket connection logs in `dcc/output/logs/tracer_network.json`.

### Phase 3: Interactive Visualization UI
**Goal:** Build the "Command Center" dashboard.
- **Achievements:** Tree-view visualization of the `DCC Engine` pipeline execution.
- **Deliverables:** `dcc/ui/tracer_dashboard.html`, `dcc/ui/js/trace_viz.js`.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_3_ui_report.md`.

### Phase 4: IDE Integration (Live Edit)
**Goal:** Enable "Live Editing" and hot-reloading.
- **Achievements:** Successful on-the-fly code modification and immediate re-execution without restarting the server.
- **Deliverables:** Monaco Editor integration in UI, `hot_reload_handler.py`.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_4_ide_report.md`.

### Phase 5: Pipeline Sandbox & Integration
**Goal:** Connect the tracer to actual DCC datasets and engines.
- **Achievements:** Tracing of "Calculated Columns" logic for complex Excel datasets.
- **Deliverables:** Sandbox environment config, Mock Data Injector.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_5_integration_report.md`.

### Phase 6: Final Packaging & CLI
**Goal:** Finalize the standalone tool.
- **Achievements:** Deployment-ready CLI tool for tracing any Python directory.
- **Deliverables:** `dcc/tracer_cli.py`, `setup.py` (optional), Performance Heatmap module.
- **Phase Report:** `dcc/workplan/code_tracing/reports/phase_6_final_report.md`.

---

## Success Evaluation Criteria
1. **Zero Execution Error**: The tracer must not crash the target application.
2. **Performance Overhead**: Trace execution should not exceed 15% overhead in "Light Mode".
3. **Data Integrity**: Serialized states in the UI must exactly match the memory state.
4. **Usability**: Developer can identify a bug within 3 clicks in the UI.
5. **Path Resolution**: Must handle WSL/Linux paths seamlessly.

---

## Issues & Risks
| Issue | Mitigation |
| :--- | :--- |
| **Object Serialization** | Use `pandas.to_json()` for DataFrames and a custom recursive serializer for complex classes. |
| **Performance Lag** | Implement "Step-by-Step" mode or "Function Filtering" to limit tracing depth. |
| **Memory Overflow** | Limit the size of captured `f_locals` and trim large strings/arrays. |
| **Concurrent Access** | Use threading locks in `TracerEngine` to ensure thread-safe tracing. |

---

## Update & Log Strategy
- **Logs**: All trace events will be appended to `dcc/output/logs/code_tracing_main.log`.
- **Structured Logs**: Detailed JSON logs saved to `dcc/output/logs/structured_trace_data.json`.
- **Workplan Updates**: This document will be updated after each phase completion with links to reports.

---

## Technical Stack
- **Languages**: Python (Backend), Javascript (Frontend).
- **Backend Framework**: FastAPI + WebSockets.
- **Front-end**: Vanilla HTML/JS, Tailwind CSS (CDI), Monaco Editor.
- **Analysis**: `sys.settrace`, `inspect`, `ast`, `importlib`.
- **Visualization**: D3.js or React Flow (Standalone version).
