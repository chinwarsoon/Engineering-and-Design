# Universal Interactive Python Code Tracer

## Description

The Universal Interactive Python Code Tracer is a powerful tool for monitoring and analyzing Python program execution. Built using `sys.settrace`, it captures detailed information about function calls, execution times, and variable states without modifying the target code.

This implementation represents Phase 1-6 of a complete tracing solution, featuring:
- Low-overhead function call tracing
- Execution time measurement
- Call stack hierarchy visualization
- Filtering capabilities for focused tracing
- Web-based visualization interface (Phase 2)
- Command-line interface (Phase 6)

## Features

- **Function Call Tracking**: Monitors all function calls including built-ins and user-defined functions
- **Performance Metrics**: Measures execution time for each function call
- **Call Hierarchy**: Builds and displays the call tree showing parent-child relationships
- **Variable Inspection**: Captures local and global variables at each call (configurable)
- **Flexible Filtering**: Include/exclude specific files or standard library code
- **Multiple Output Formats**: Console display, JSON data, and web visualization
- **Minimal Performance Impact**: Optimized tracing engine with low overhead
- **Thread-Safe**: Designed to work with multi-threaded applications

## Installation

This tracer is designed to work within the existing Engineering-and-Design project environment. Ensure you have the required dependencies installed:

```bash
# From the project root
conda env create -f dcc.yml
conda activate dcc
```

Key dependencies include:
- Python 3.13+
- pandas
- openpyxl
- numpy
- jsonschema
- matplotlib
- seaborn
- fastapi (for backend)
- uvicorn (for backend server)
- Other tracing utilities

## Usage

### Basic Usage

The tracer provides three main functions that can be imported and used in any Python script:

```python
from tracer import start_trace, stop_trace, get_trace_data
from tracer.utils.trace_filters import format_trace_for_display

# Start tracing
start_trace()

# Execute the code you want to trace
result = your_function()

# Stop tracing
stop_trace()

# Get and display trace results
trace_data = get_trace_data()
formatted_calls = format_trace_for_display(trace_data)

# Process or display the formatted calls as needed
```

### Using the Demo

Run the included demo to see the tracer in action:

```bash
cd /home/franklin/dsai/Engineering-and-Design/dcc
python3 tracer/demo.py
```

This will trace a sample Fibonacci calculation and display:
- Total function calls
- Execution time
- Call hierarchy with indentation showing call depth
- Local variable counts for selected calls

### Programmatic Integration

To trace specific parts of your code:

```python
from tracer import start_trace, stop_trace, get_trace_data

def my_application_logic():
    # Code you don't want to trace
    setup_data()
    
    # Start tracing for specific section
    start_trace()
    try:
        # Code you want to trace
        result = process_critical_section(data)
    finally:
        # Stop tracing
        stop_trace()
    
    # Continue with non-traced code
    cleanup()
    
    # Analyze trace data
    trace_data = get_trace_data()
    # ... process trace_data as needed
```

## Architecture

The tracer consists of several key components:

### 1. Core Tracing Engine (`core/trace_engine.py`)
- Implements the `TraceEngine` class using `sys.settrace`
- Captures call, return, and exception events
- Maintains call stack and timing information
- Provides thread-safe data collection

### 2. Utility Filters (`utils/trace_filters.py`)
- File filtering functions to include/expecific paths
- Trace data filtering based on file properties
- Formatting functions for display output
- Call hierarchy construction utilities

### 3. Backend Server (`backend/server.py`) - Phase 2
- FastAPI-based web server for visualization
- REST API endpoints for accessing trace data
- WebSocket support for real-time updates (planned)
- Health check and monitoring endpoints

### 4. Command-Line Interface (`cli/main.py`) - Phase 6
- CLI commands for tracing scripts
- Configuration options for filtering and output
- Integration with standard Python tools

### 5. Public Interface (`__init__.py`)
- Exposes the main functions and classes
- Handles conditional imports for optional components
- Provides version and metadata information

## API Reference

### Main Functions
- `start_trace()`: Begin tracing execution
- `stop_trace()`: End tracing execution
- `get_trace_data()`: Retrieve collected trace data as a dictionary
- `is_tracing()`: Check if tracing is currently active

### Utility Functions
- `should_trace_file(filename, include_paths=None, exclude_paths=None, exclude_stdlib=True)`: Determine if a file should be traced
- `filter_trace_data(trace_data, include_paths=None, exclude_paths=None, exclude_stdlib=True)`: Filter trace data based on file paths
- `format_trace_for_display(trace_data)`: Format trace data for console display
- `get_call_hierarchy(trace_data, call_id)`: Get the call hierarchy for a specific call

### Data Structures
The trace data returned by `get_trace_data()` contains:
- `calls`: Dictionary mapping call IDs to call event details
- `call_tree`: Hierarchical representation of function calls
- `stats`: Overall statistics (total calls, total time, active calls)

Each call event includes:
- `call_id`: Unique identifier
- `parent_id`: ID of the calling function (None for root calls)
- `depth`: Nesting level in the call stack
- `function_name`: Name of the function
- `filename`: Source file path
- `lineno`: Line number in the source file
- `start_time`: Timestamp when the call began
- `end_time`: Timestamp when the call ended
- `duration`: Execution time (end_time - start_time)
- `return_value`: Value returned by the function
- `exception`: Exception information if the call failed
- `locals`: Dictionary of local variables at the call
- `globals`: Dictionary of global variables at the call

## Example Output

See `demo.py` for a complete example. Sample output:

```
=== Universal Interactive Python Code Tracer - Phase 1 Demo ===

Processing data: [1, 2, 3, 4, 5]

Starting trace...
Result: [2, 1, 6, 3, 10]
Stopping trace...

=== Trace Results ===
Total function calls: 15
Total trace time: 0.000413 seconds
Active calls: 2

Function calls traced: 15

--- Call Details ---
1. process_data() [demo.py:20] (return) 0.000231s
    Locals: 1 variables
  2. fibonacci() [demo.py:13] (return) 0.000042s
      Locals: 1 variables
    3. fibonacci() [demo.py:13] (return) 0.000003s
        Locals: 1 variables
    4. fibonacci() [demo.py:13] (return) 0.000004s
        Locals: 1 variables
  5. fibonacci() [demo.py:13] (return) 0.000068s
      Locals: 1 variables
    6. fibonacci() [demo.py:13] (return) 0.000020s
        Locals: 1 variables
      7. fibonacci() [demo.py:13] (return) 0.000008s
        8. fibonacci() [demo.py:13] (return) 0.000001s
        9. fibonacci() [demo.py:13] (return) 0.000001s
      10. fibonacci() [demo.py:13] (return) 0.000002s
... and 5 more calls

=== Demo Complete ===
```

## Running Tests

Unit tests are located in the `tests/` directory. Run them from the project root:

```bash
cd /home/franklin/dsai/Engineering-and-Design/dcc
python3 -m unittest test/test_trace_engine.py
python3 -m unittest test/test_column_mapper.py
python3 -m unittest test/test_universal_document_processor_document_type_validation.py
```

Note: All test files add the `workflow/` directory to `sys.path` for imports.

## Extending the Tracer

To customize the tracer for specific needs:

1. **Modify Filtering**: Adjust the include/exclude paths in `filter_trace_data()` or `should_trace_file()`
2. **Change Data Collection**: Edit `core/trace_engine.py` to capture additional event types or data
3. **Add Output Formats**: Create new formatting functions in `utils/trace_filters.py`
4. **Enhance Web Interface**: Modify `backend/server.py` to add new visualization features

## License

See the project root directory for licensing information.

## Support

For questions or issues, please refer to the project documentation or contact the Engineering-and-Design team.

---
*Version 0.6.0 | Phase 1-6: Complete Implementation*