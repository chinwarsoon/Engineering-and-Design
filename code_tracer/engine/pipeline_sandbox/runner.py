"""
Pipeline Sandbox Runner for the Universal Interactive Python Code Tracer.
Provides dynamic loading and tracing of arbitrary Python scripts.
"""

import sys
import os
import importlib.util
from typing import Any, Dict, Optional
from pathlib import Path

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tracer import start_trace, stop_trace, get_trace_data
from tracer.utils.trace_filters import format_trace_for_display

def load_and_trace_script(script_path: str, function_name: str = "main", args: list = None, kwargs: dict = None) -> Dict[str, Any]:
    """
    Dynamically loads a Python script and traces the execution of a specific function.
    
    Args:
        script_path: Absolute or relative path to the .py file
        function_name: Name of the function to execute (default: "main")
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        
    Returns:
        Trace data collected during execution
    """
    args = args or []
    kwargs = kwargs or {}
    
    # Resolve path
    p = Path(script_path)
    if not p.is_absolute():
        p = (Path(os.getcwd()) / p).resolve()
        
    if not p.exists():
        raise FileNotFoundError(f"Script not found: {p}")
    
    # Setup module loading
    module_name = p.stem
    spec = importlib.util.spec_from_file_location(module_name, str(p))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {p}")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    # Add script's directory to path to allow relative imports within the script
    script_dir = str(p.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        
    try:
        # Execute module
        spec.loader.exec_module(module)
        
        # Get target function
        if not hasattr(module, function_name):
            raise AttributeError(f"Module {module_name} has no function '{function_name}'")
            
        target_func = getattr(module, function_name)
        
        # Start tracing
        print(f"Tracing {module_name}.{function_name}() from {p}...")
        start_trace()
        
        try:
            # Execute function
            result = target_func(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "trace_data": get_trace_data()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "trace_data": get_trace_data()
            }
        finally:
            # Always stop tracing
            stop_trace()
            
    finally:
        # Cleanup path if we added it
        if script_dir in sys.path:
            sys.path.remove(script_dir)

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python3 runner.py <script_path> [function_name]")
        sys.exit(1)
        
    target_script = sys.argv[1]
    target_func = sys.argv[2] if len(sys.argv) > 2 else "main"
    
    try:
        run_result = load_and_trace_script(target_script, target_func)
        
        if run_result["success"]:
            print(f"\nExecution successful. Result: {run_result['result']}")
        else:
            print(f"\nExecution failed: {run_result['error']}")
            
        trace_data = run_result["trace_data"]
        stats = trace_data.get('stats', {})
        print(f"\nTotal calls: {stats.get('total_calls')}")
        
        formatted = format_trace_for_display(trace_data)
        print(f"Traced functions: {len(formatted)}")
        
        # Print top 10 calls
        print("\nTop 10 calls:")
        for i, call in enumerate(formatted[:10]):
            indent = "  " * call.get('depth', 0)
            print(f"{indent}{i+1}. {call.get('function')}() [{call.get('file')}:{call.get('line')}]")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
