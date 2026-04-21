#!/usr/bin/env python3
"""
Example showing how to trace the DCC Engine Pipeline execution.
This demonstrates the basic usage pattern for tracing any Python script.
"""

import sys
import os

# Add necessary paths
tracer_path = os.path.join(os.path.dirname(__file__))
if tracer_path not in sys.path:
    sys.path.insert(0, tracer_path)

dcc_path = os.path.join(os.path.dirname(__file__), '..')
if dcc_path not in sys.path:
    sys.path.insert(0, dcc_path)

workflow_path = os.path.join(dcc_path, 'workflow')
if workflow_path not in sys.path:
    sys.path.insert(0, workflow_path)

from tracer import start_trace, stop_trace, get_trace_data
from tracer.utils.trace_filters import format_trace_for_display, should_trace_file

def trace_pipeline_execution():
    """
    Example function showing how to trace pipeline execution.
    In practice, you would modify your actual pipeline call to include tracing.
    """
    print("=== Example: How to Trace DCC Engine Pipeline ===\n")
    
    # Example 1: Basic tracing approach
    print("1. Basic Tracing Pattern:")
    print("   from tracer import start_trace, stop_trace, get_trace_data")
    print("   ")
    print("   start_trace()")
    print("   try:")
    print("       # Your pipeline execution code here")
    print("       from workflow.dcc_engine_pipeline import main")
    print("       main()")
    print("   finally:")
    print("       stop_trace()")
    print("   ")
    print("   # Get and process trace data")
    print("   trace_data = get_trace_data()")
    print("   formatted_calls = format_trace_for_display(trace_data)")
    print()
    
    # Example 2: With filtering to focus on specific modules
    print("2. Focused Tracing (Recommended for Pipeline):")
    print("   # Trace only your workflow modules, exclude standard library")
    print("   from tracer import start_trace, stop_trace, get_trace_data")
    print("   from tracer.utils.trace_filters import filter_trace_data")
    print("   ")
    print("   start_trace()")
    print("   try:")
    print("       # Run pipeline")
    print("       from workflow.dcc_engine_pipeline import main")
    print("       main()")
    print("   finally:")
    print("       stop_trace()")
    print("   ")
    print("   # Get raw trace data")
    print("   raw_trace_data = get_trace_data()")
    print("   ")
    print("   # Filter to focus on workflow engine code")
    print("   workflow_paths = [")
    print("       os.path.join(os.path.dirname(__file__), '..', 'workflow')")
    print("   ]")
    print("   ")
    print("   filtered_trace_data = filter_trace_data(")
    print("       raw_trace_data,")
    print("       include_paths=workflow_paths,")
    print("       exclude_stdlib=True")
    print("   )")
    print("   ")
    print("   # Format for display")
    print("   formatted_calls = format_trace_for_display(filtered_trace_data)")
    print()
    
    # Example 3: Minimal tracing for specific functions
    print("3. Functional Tracing Approach:")
    print("   def traced_pipeline_run():")
    print("       start_trace()")
    print("       try:")
    print("           from workflow.dcc_engine_pipeline import main")
    print("           return main()")
    print("       finally:")
    print("           stop_trace()")
    print("   ")
    print("   # Run and get results")
    print("   pipeline_result = traced_pipeline_run()")
    print("   trace_data = get_trace_data()")
    print()
    
    # Show what the trace data looks like (using demo data)
    print("4. Sample Trace Data Structure:")
    print("   The trace_data dictionary contains:")
    print("   - 'calls': Dict of all function calls with details")
    print("   - 'call_tree': Hierarchical view of function calls")
    print("   - 'stats': Overall statistics (calls, time, active)")
    print()
    print("   Each call entry includes:")
    print("   - function_name, filename, lineno")
    print("   - start_time, end_time, duration")
    print("   - return_value, exception (if any)")
    print("   - locals_, globals_ (variable states)")
    print("   - depth (call stack level)")
    print()
    
    print("=== To Actually Trace the Pipeline ===")
    print("1. Ensure you have the required input files:")
    print("   - Excel data: dcc/data/Submittal and RFI Tracker Lists.xlsx")
    print("   - Schema: dcc/config/schemas/dcc_register_*.json")
    print()
    print("2. Run this command:")
    print("   cd /home/franklin/dsai/Engineering-and-Design/dcc")
    print("   python3 tracer/trace_pipeline.py")
    print()
    print("3. For custom tracing in your own scripts:")
    print("   Add the tracing start/stop calls around your pipeline execution")
    print()

if __name__ == "__main__":
    trace_pipeline_execution()