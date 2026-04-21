"""
Demo script showing how to use the Universal Interactive Python Code Tracer - Phase 1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tracer import start_trace, stop_trace, get_trace_data
from tracer.utils.trace_filters import format_trace_for_display


def fibonacci(n):
    """Calculate Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


def process_data(data):
    """Process some sample data."""
    results = []
    for item in data:
        if item % 2 == 0:
            results.append(fibonacci(item))
        else:
            results.append(item * 2)
    return results


def main():
    """Main demo function."""
    print("=== Universal Interactive Python Code Tracer - Phase 1 Demo ===\n")
    
    # Sample data to process
    sample_data = [1, 2, 3, 4, 5]
    
    print(f"Processing data: {sample_data}")
    
    # Start tracing
    print("\nStarting trace...")
    start_trace()
    
    try:
        # Execute the code we want to trace
        result = process_data(sample_data)
        print(f"Result: {result}")
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
    
    print("\n--- Call Details ---")
    for i, call in enumerate(formatted_calls[:10]):  # Show first 10 calls
        status = call.get('status', 'unknown')
        duration = call.get('duration')
        duration_str = f"{duration:.6f}s" if duration is not None else "running"
        
        indent = "  " * call.get('depth', 0)
        print(f"{indent}{i+1}. {call.get('function')}() "
              f"[{call.get('file')}:{call.get('line')}] "
              f"({status}) {duration_str}")
        
        # Show locals for interesting calls
        if call.get('locals_count', 0) > 0 and call.get('depth') <= 2:
            # In a real implementation, we'd show actual local values
            print(f"{indent}    Locals: {call.get('locals_count')} variables")
    
    if len(formatted_calls) > 10:
        print(f"... and {len(formatted_calls) - 10} more calls")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()