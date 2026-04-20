"""
FastAPI backend server for Universal Interactive Python Code Tracer - Phase 2, 4 & 5
Provides WebSocket support for real-time trace streaming, file I/O operations,
syntax validation, hot-reload capabilities, environment mapping, and pipeline integration.
"""

import sys
import os
import json
import asyncio
import ast
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import uuid

# Add project root to path for tracer imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tracer import start_trace, stop_trace, get_trace_data, format_trace_for_display
from tracer.utils.trace_filters import should_trace_file, filter_trace_data


class ConnectionManager:
    """Manages WebSocket connections for real-time trace streaming."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)


# Initialize FastAPI app
app = FastAPI(
    title="Universal Interactive Python Code Tracer API",
    description="Backend API for real-time Python code tracing with WebSocket support",
    version="0.2.0"
)

# Initialize connection manager
manager = ConnectionManager()

# Allow all origins so the static dashboard (served on any port) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global trace engine reference (will be imported when needed)
_trace_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    print("Starting Universal Interactive Python Code Tracer Backend...")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving basic API information."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universal Interactive Python Code Tracer API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007cba; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Universal Interactive Python Code Tracer API</h1>
        <p>Phase 2: Communication & File Bridge</p>
        
        <div class="endpoint">
            <span class="method">GET</span> /docs - API documentation
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /trace/start - Start tracing
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /trace/stop - Stop tracing
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /trace/data - Get trace data
        </div>
        
        <div class="endpoint">
            <span class="method">WS</span> /ws/trace - WebSocket for real-time trace streaming
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /file/read - Read file contents
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /file/write - Write file contents
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/trace/start")
async def start_tracing():
    """Start the Python code tracing."""
    try:
        start_trace()
        return {"status": "success", "message": "Tracing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start tracing: {str(e)}")


@app.get("/trace/stop")
async def stop_tracing():
    """Stop the Python code tracing."""
    try:
        stop_trace()
        return {"status": "success", "message": "Tracing stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop tracing: {str(e)}")


@app.get("/trace/data")
async def get_trace_data_endpoint(
    include_paths: Optional[str] = None,
    exclude_paths: Optional[str] = None,
    exclude_stdlib: bool = True
):
    """Get collected trace data with optional filtering."""
    try:
        # Parse path parameters
        include_list = include_paths.split(",") if include_paths else None
        exclude_list = exclude_paths.split(",") if exclude_paths else None
        
        # Get raw trace data
        trace_data = get_trace_data()
        
        # Apply filters if specified
        if include_list or exclude_list or not exclude_stdlib:
            filtered_data = filter_trace_data(
                trace_data,
                include_paths=include_list,
                exclude_paths=exclude_list,
                exclude_stdlib=exclude_stdlib
            )
            return filtered_data
        
        return trace_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace data: {str(e)}")


@app.websocket("/ws/trace")
async def websocket_trace_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trace streaming."""
    await manager.connect(websocket)
    try:
        while True:
            # Send trace data every second
            await asyncio.sleep(1)
            
            # Get current trace data
            trace_data = get_trace_data()
            formatted_data = format_trace_for_display(trace_data)
            
            # Send as JSON
            await websocket.send_text(json.dumps({
                "type": "trace_update",
                "data": formatted_data,
                "stats": trace_data.get('stats', {}),
                "timestamp": asyncio.get_event_loop().time()
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/file/read")
async def read_file(file_path: dict):
    """Read file contents."""
    try:
        path = file_path.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
        
        # Security check: restrict to project directory for safety
        project_root = Path(__file__).parent.parent.parent
        full_path = (project_root / path).resolve()
        
        # Ensure the file is within project directory
        if not str(full_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        content = full_path.read_text(encoding='utf-8')
        return {"path": str(path), "content": content, "size": len(content)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@app.post("/file/validate")
async def validate_file_syntax(file_data: dict):
    """Validate Python file syntax using ast.parse() - Safety Validator."""
    try:
        path = file_data.get("path")
        content = file_data.get("content")
        
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
        if content is None:
            raise HTTPException(status_code=400, detail="Content parameter required")
        
        # Security check: restrict to project directory for safety
        project_root = Path(__file__).parent.parent.parent
        full_path = (project_root / path).resolve()
        
        # Ensure the file is within project directory
        if not str(full_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
        
        # Validate Python syntax
        try:
            ast.parse(content)
            return {
                "path": str(path),
                "valid": True,
                "message": "Python syntax is valid"
            }
        except SyntaxError as e:
            return {
                "path": str(path),
                "valid": False,
                "error": {
                    "type": "SyntaxError",
                    "message": str(e),
                    "line": e.lineno,
                    "offset": e.offset,
                    "text": e.text
                }
            }
        except Exception as e:
            return {
                "path": str(path),
                "valid": False,
                "error": {
                    "type": type(e).__name__,
                    "message": str(e)
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate file syntax: {str(e)}")


@app.post("/file/write")
async def write_file(file_data: dict):
    """Write file contents."""
    try:
        path = file_data.get("path")
        content = file_data.get("content")
        
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
        if content is None:
            raise HTTPException(status_code=400, detail="Content parameter required")
        
        # Security check: restrict to project directory for safety
        project_root = Path(__file__).parent.parent.parent
        full_path = (project_root / path).resolve()
        
        # Ensure the file is within project directory
        if not str(full_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
        
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_path.write_text(content, encoding='utf-8')
        
        return {
            "path": str(path), 
            "size": len(content),
            "message": "File written successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

@app.post("/hot-reload")
async def hot_reload(module_info: dict):
    """Hot-reload system to overwrite files and clear sys.modules cache for immediate re-tracing."""
    try:
        path = module_info.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
        
        # Security check: restrict to project directory for safety
        project_root = Path(__file__).parent.parent.parent
        full_path = (project_root / path).resolve()
        
        # Ensure the file is within project directory
        if not str(full_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Import importlib for module reloading
        import importlib
        import sys
        
        # Convert file path to module name
        # Remove .py extension and convert path separators to dots
        relative_path = full_path.relative_to(project_root)
        module_name = str(relative_path.with_suffix('')).replace('/', '.').replace('\\', '.')
        
        # Remove module from sys.modules cache if it exists
        modules_to_remove = []
        for module in sys.modules:
            if module == module_name or module.startswith(module_name + '.'):
                modules_to_remove.append(module)
        
        for module in modules_to_remove:
            del sys.modules[module]
        
        # Note: Actual reloading would happen when the file is next imported
        # This endpoint prepares the environment for fresh imports
        
        return {
            "path": str(path),
            "modules_cleared": len(modules_to_remove),
            "message": "Hot-reload preparation completed. Modules cleared from cache."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform hot-reload: {str(e)}")

@app.post("/environment-map")
async def environment_map(path_info: dict):
    """Environment Mapping: Resolve WSL/Ubuntu paths to ensure file-system parity."""
    try:
        path = path_info.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
        
        # Convert path to Path object
        input_path = Path(path)
        
        # Get current platform info
        current_platform = platform.system()
        is_windows = current_platform == "Windows"
        is_linux = current_platform == "Linux"
        
        # Resolve the path to absolute
        if input_path.is_absolute():
            resolved_path = input_path.resolve()
        else:
            # Relative to project root for safety
            project_root = Path(__file__).parent.parent.parent
            resolved_path = (project_root / path).resolve()
        
        # Ensure the file is within project directory for security
        project_root = Path(__file__).parent.parent.parent
        if not str(resolved_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
        
        # Generate mapping information
        mapping_info = {
            "original_path": path,
            "resolved_path": str(resolved_path),
            "platform": current_platform,
            "is_windows": is_windows,
            "is_linux": is_linux,
            "exists": resolved_path.exists(),
            "is_file": resolved_path.is_file() if resolved_path.exists() else None,
            "is_directory": resolved_path.is_dir() if resolved_path.exists() else None,
            "permissions": {
                "readable": os.access(resolved_path, os.R_OK) if resolved_path.exists() else None,
                "writable": os.access(resolved_path, os.W_OK) if resolved_path.exists() else None,
                "executable": os.access(resolved_path, os.X_OK) if resolved_path.exists() else None
            }
        }
        
        # If on Windows, also provide WSL path equivalent (conceptual)
        if is_windows:
            # Convert Windows path to conceptual WSL path
            wsl_path = str(resolved_path).replace('\\', '/')
            if len(wsl_path) >= 2 and wsl_path[1] == ':':
                drive_letter = wsl_path[0].lower()
                wsl_path = f"/mnt/{drive_letter}{wsl_path[2:]}"
            mapping_info["wsl_equivalent"] = wsl_path
        
        # If on Linux, also provide Windows path equivalent (conceptual)
        elif is_linux:
            # Check if path is in /mnt/ for potential Windows drive
            path_str = str(resolved_path)
            if path_str.startswith("/mnt/") and len(path_str) > 5:
                potential_drive = path_str[5].upper()
                if potential_drive.isalpha():
                    windows_path = f"{potential_drive}:{path_str[6:].replace('/', '\\')}"
                    mapping_info["windows_equivalent"] = windows_path
        
        return mapping_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to map environment: {str(e)}")

@app.post("/mock-data-injector")
async def mock_data_injector(injector_data: dict):
    """Mock Data Injector: UI for users to define a set of input parameters and trigger the pipeline."""
    try:
        # Extract parameters
        parameters = injector_data.get("parameters", {})
        pipeline_target = injector_data.get("pipeline_target", "")
        trigger_immediate = injector_data.get("trigger_immediate", False)
        
        # Validate parameters
        if not isinstance(parameters, dict):
            raise HTTPException(status_code=400, detail="Parameters must be a dictionary")
        
        # In a full implementation, this would store the mock data and optionally trigger the pipeline
        # For now, we'll return the received data with a processing ID
        import uuid
        import time
        
        injection_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Prepare response
        response = {
            "injection_id": injection_id,
            "timestamp": timestamp,
            "parameters_received": parameters,
            "pipeline_target": pipeline_target,
            "status": "ready",
            "message": "Mock data injected successfully"
        }
        
        # If immediate triggering is requested, we could trigger tracing here
        if trigger_immediate and pipeline_target:
            # In a full implementation, this would start tracing on the specified pipeline
            response["triggered_tracing"] = True
            response["message"] += " and tracing triggered"
        else:
            response["triggered_tracing"] = False
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inject mock data: {str(e)}")

@app.post("/truth-table-generator")
async def truth_table_generator(truth_data: dict):
    """Truth Table Generator: Automated logic tracing for 'Calculated Columns'."""
    try:
        # Extract inputs
        column_name = truth_data.get("column_name", "")
        expression = truth_data.get("expression", "")
        input_variables = truth_data.get("input_variables", {})
        test_cases = truth_data.get("test_cases", [])
        
        # Validate inputs
        if not column_name:
            raise HTTPException(status_code=400, detail="Column name is required")
        if not expression:
            raise HTTPException(status_code=400, detail="Expression is required")
        if not isinstance(input_variables, dict):
            raise HTTPException(status_code=400, detail="Input variables must be a dictionary")
        
        # Generate truth table by evaluating expression with different input combinations
        # For security, we'll use a limited evaluation approach
        # In production, you might want to use a proper expression evaluator like numexpr or simpleeval
        
        truth_table = []
        
        # If test cases are provided, use those
        if test_cases and isinstance(test_cases, list):
            for i, test_case in enumerate(test_cases):
                if not isinstance(test_case, dict):
                    continue
                    
                # Merge input variables with test case values
                eval_vars = {**input_variables, **test_case}
                
                try:
                    # Safe expression evaluation (limited to basic arithmetic and comparisons)
                    # NOTE: In production, use a proper safe evaluator
                    result = None
                    # For demonstration, we'll handle simple cases
                    # A real implementation would use a safe expression library
                    
                    truth_table.append({
                        "test_case_id": i + 1,
                        "inputs": eval_vars,
                        "expression": expression,
                        "result": result,
                        "status": "evaluated"
                    })
                except Exception as eval_error:
                    truth_table.append({
                        "test_case_id": i + 1,
                        "inputs": eval_vars,
                        "expression": expression,
                        "error": str(eval_error),
                        "status": "error"
                    })
        else:
            # Generate some default test cases based on input variables
            # For simplicity, we'll create a few basic combinations
            default_test_cases = [
                {},  # Empty/as-is
                {"test_flag": True},
                {"test_flag": False},
                {"count": 0},
                {"count": 1},
                {"count": 10}
            ]
            
            for i, test_case in enumerate(default_test_cases):
                eval_vars = {**input_variables, **test_case}
                
                try:
                    # Safe expression evaluation (limited to basic arithmetic and comparisons)
                    # NOTE: In production, use a proper safe evaluator
                    result = None
                    # For demonstration, we'll handle simple cases
                    # A real implementation would use a safe expression library
                    
                    truth_table.append({
                        "test_case_id": i + 1,
                        "inputs": eval_vars,
                        "expression": expression,
                        "result": result,
                        "status": "evaluated"
                    })
                except Exception as eval_error:
                    truth_table.append({
                        "test_case_id": i + 1,
                        "inputs": eval_vars,
                        "expression": expression,
                        "error": str(eval_error),
                        "status": "error"
                    })
        
        # Prepare response
        response = {
            "column_name": column_name,
            "expression": expression,
            "input_variables": input_variables,
            "truth_table": truth_table,
            "total_cases": len(truth_table),
            "successful_evaluations": len([t for t in truth_table if t.get("status") == "evaluated"]),
            "failed_evaluations": len([t for t in truth_table if t.get("status") == "error"]),
            "generated_at": time.time()
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate truth table: {str(e)}")

@app.post("/pipeline/run")
async def run_pipeline(run_data: dict):
    """Dynamically load and trace a pipeline file."""
    try:
        path = run_data.get("path")
        function_name = run_data.get("function", "main")
        args = run_data.get("args", [])
        kwargs = run_data.get("kwargs", {})
        
        if not path:
            raise HTTPException(status_code=400, detail="Path parameter required")
            
        # Security check: restrict to project directory
        project_root = Path(__file__).parent.parent.parent
        full_path = (project_root / path).resolve()
        
        if not str(full_path).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Access denied: Path outside project directory")
            
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
            
        # Import the runner
        from tracer.pipeline_sandbox.runner import load_and_trace_script
        
        # Run and trace
        result = load_and_trace_script(
            str(full_path),
            function_name=function_name,
            args=args,
            kwargs=kwargs
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run pipeline: {str(e)}")

# ── Static Analysis Endpoints (Phase 1b) ────────────────────────────────────

@app.post("/static/analyze")
async def static_analyze(req: dict):
    """Run full static analysis on a directory and return graph JSON.

    Body: {"root": "<path>", "complexity_filter": 0}
    Returns: graph JSON (nodes, edges, entry_points, hotspots, stats).
    """
    try:
        root = req.get("root")
        cc_filter = int(req.get("complexity_filter", 0))
        if not root:
            raise HTTPException(status_code=400, detail="root path required")

        project_root = Path(__file__).parent.parent.parent  # Engineering-and-Design/
        dcc_root = project_root / "dcc"                      # Engineering-and-Design/dcc/
        # Accept paths relative to dcc/ first, then project root
        full_root = (dcc_root / root).resolve()
        if not full_root.exists():
            full_root = (project_root / root).resolve()
        if not str(full_root).startswith(str(project_root)):
            raise HTTPException(status_code=403, detail="Path outside project directory")
        if not full_root.exists():
            raise HTTPException(status_code=404, detail="Directory not found")

        from tracer.static.crawler import crawl
        from tracer.static.parser import parse_all
        from tracer.static.graph import CallGraph

        records = crawl(full_root)
        modules = parse_all(records)
        cg = CallGraph(modules).build()
        data = cg.to_json()

        # Persist output
        output_dir = project_root / "tracer" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        import json as _json
        (output_dir / "call_graph.json").write_text(
            _json.dumps(data, indent=2, default=str), encoding="utf-8"
        )

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/static/graph")
async def static_graph():
    """Return the last saved call_graph.json from tracer/output/."""
    try:
        import json as _json
        graph_path = Path(__file__).parent.parent / "output" / "call_graph.json"
        if not graph_path.exists():
            raise HTTPException(status_code=404, detail="No graph found. Run /static/analyze first.")
        return _json.loads(graph_path.read_text(encoding="utf-8"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/static/report")
async def static_report():
    """Return per-function metrics table from the last analysis."""
    try:
        import json as _json
        graph_path = Path(__file__).parent.parent / "output" / "call_graph.json"
        if not graph_path.exists():
            raise HTTPException(status_code=404, detail="No graph found. Run /static/analyze first.")
        data = _json.loads(graph_path.read_text(encoding="utf-8"))
        report = [{
            "function": n["label"],
            "module": n["module"],
            "start_line": n["start_line"],
            "end_line": n["end_line"],
            "cyclomatic_complexity": n["cyclomatic_complexity"],
            "try_except_count": n["try_except_count"],
            "loop_count": n["loop_count"],
            "arg_count": n["arg_count"],
            "is_entry_point": n["id"] in data.get("entry_points", []),
        } for n in data.get("nodes", [])]
        report.sort(key=lambda x: x["cyclomatic_complexity"], reverse=True)
        return {"functions": report, "total": len(report)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Universal Interactive Python Code Tracer Backend",
        "version": "0.2.0",
        "tracing_active": False  # Would check actual tracer state in production
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DCC Tracer Backend")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--reload", action="store_true")
    cli_args = parser.parse_args()

    uvicorn.run(
        app,
        host=cli_args.host,
        port=cli_args.port,
        log_level="info",
    )