"""
Universal Interactive Python Code Tracer - Phase 1-6: Complete Implementation
"""

try:
    # Try relative imports first (when used as package)
    from .core.trace_engine import TraceEngine, start_trace, stop_trace, get_trace_data, is_tracing
    from .utils.trace_filters import should_trace_file, filter_trace_data, format_trace_for_display, get_call_hierarchy
except ImportError:
    # Fallback to absolute imports (when run directly or path issues)
    from core.trace_engine import TraceEngine, start_trace, stop_trace, get_trace_data, is_tracing
    from utils.trace_filters import should_trace_file, filter_trace_data, format_trace_for_display, get_call_hierarchy

# Phase 2: Backend components (available when needed)
try:
    try:
        from .backend.server import app, ConnectionManager, manager
    except ImportError:
        from backend.server import app, ConnectionManager, manager
    _backend_available = True
except ImportError:
    _backend_available = False

# Phase 6: CLI components
try:
    try:
        from .cli.main import main as cli_main
    except ImportError:
        from cli.main import main as cli_main
    _cli_available = True
except ImportError:
    _cli_available = False

__version__ = "0.6.0"
__author__ = "Engineering-and-Design Team"
__description__ = "Phase 1-6: Complete Implementation of Universal Interactive Python Code Tracer"

# Public API
__all__ = [
    'TraceEngine',
    'start_trace',
    'stop_trace', 
    'get_trace_data',
    'is_tracing',
    'should_trace_file',
    'filter_trace_data',
    'format_trace_for_display',
    'get_call_hierarchy'
]

# Add backend components to __all__ if available
if _backend_available:
    __all__.extend(['app', 'ConnectionManager', 'manager'])

# Add CLI components to __all__ if available
if _cli_available:
    __all__.append('cli_main')