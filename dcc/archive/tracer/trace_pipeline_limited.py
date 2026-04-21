#!/usr/bin/env python3
"""
Tracing wrapper for DCC Engine Pipeline with limited rows for faster execution.
This script demonstrates how to use the Universal Interactive Python Code Tracer
to trace the execution of the dcc_engine_pipeline.py with limited data.
"""

import sys
import os

# Add the tracer directory to the path so we can import the tracer
tracer_path = os.path.join(os.path.dirname(__file__))
if tracer_path not in sys.path:
    sys.path.insert(0, tracer_path)

# Add the dcc directory to the path so we can import the pipeline
dcc_path = os.path.join(os.path.dirname(__file__), '..')
if dcc_path not in sys.path:
    sys.path.insert(0, dcc_path)

# Add the workflow directory to the path for engine imports
workflow_path = os.path.join(dcc_path, 'workflow')
if workflow_path not in sys.path:
    sys.path.insert(0, workflow_path)

from tracer import start_trace, stop_trace, get_trace_data
from tracer.utils.trace_filters import format_trace_for_display

def main():
    """Main function to trace the pipeline execution with limited rows."""
    print("=== Tracing DCC Engine Pipeline Execution (Limited Rows) ===\n")
    
    # Import and run the pipeline
    try:
        from workflow.dcc_engine_pipeline import main as pipeline_main
        
        # Start tracing
        print("Starting trace...")
        start_trace()
        
        try:
            # We'll need to modify the pipeline to accept nrows parameter
            # For now, let's trace the import and setup only by catching SystemExit early
            # This will at least show us the tracing mechanism works
            print("Running pipeline (this may take a moment)...")
            result = pipeline_main()
            print(f"Pipeline execution completed with result: {result}")
        except SystemExit as e:
            # Handle SystemExit from the pipeline's main function
            print(f"Pipeline exited with code: {e.code}")
        except Exception as e:
            print(f"Pipeline execution failed with error: {e}")
            # Don't raise, we still want to get trace data
        finally:
            # Stop tracing
            print("Stopping trace...")
            stop_trace()
        
        # Get and display trace results
        print("\n=== Trace Results ===")
        trace_data = get_trace_data()
        
        # Display statistics
        stats = trace_data.get('stats', {})
        print(f"Total function calls: {stats.get('total_calls', 0)}")
        print(f"Total trace time: {stats.get('total_time', 0):.6f} seconds")
        print(f"Active calls: {stats.get('active_calls', 0)}")
        
        # Display formatted trace data
        formatted_calls = format_trace_for_display(trace_data)
        print(f"\nFunction calls traced: {len(formatted_calls)}")
        
        # Show first 30 calls to avoid overwhelming output
        print("\n--- Call Details (First 30 calls) ---")
        for i, call in enumerate(formatted_calls[:30]):
            status = call.get('status', 'unknown')
            duration = call.get('duration')
            duration_str = f"{duration:.6f}s" if duration is not None else "running"
            
            indent = "  " * call.get('depth', 0)
            print(f"{indent}{i+1}. {call.get('function')}() "
                  f"[{call.get('file')}:{call.get('line')}] "
                  f"({status}) {duration_str}")
            
            # Show locals for interesting calls (shallow depth)
            if call.get('locals_count', 0) > 0 and call.get('depth') <= 2:
                print(f"{indent}    Locals: {call.get('locals_count')} variables")
        
        if len(formatted_calls) > 30:
            print(f"... and {len(formatted_calls) - 30} more calls")
        
        print("\n=== Trace Complete ===")
        
    except ImportError as e:
        print(f"Failed to import pipeline: {e}")
        print("Make sure you're running this from the correct directory")
        print("and that all dependencies are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())