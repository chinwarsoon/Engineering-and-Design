"""
Tiered logging and debug utilities.
Implements structured logging with hierarchy levels, trace tables, and debug objects.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
# State exports (for backward compatibility)
from core_engine.logging.log_state import (
    DEBUG_LEVEL,
    CALL_DEPTH,
    DEBUG_OBJECT,
    init_debug_object,
    get_debug_object,
    save_debug_log,
)

# Handler exports
from core_engine.logging.log_handlers import (
    set_debug_level,
    log_status,
    log_warning,
    log_trace,
    log_error,
    setup_logger,
    set_debug_mode,
    get_verbose_mode,
)

# Formatter exports
from core_engine.logging.log_formatters import (
    trace_parameter,
    track_global_param,
    log_context,
)

__all__ = [
    # State
    "DEBUG_LEVEL",
    "CALL_DEPTH",
    "DEBUG_OBJECT",
    "init_debug_object",
    "get_debug_object",
    "save_debug_log",
    # Handlers
    "set_debug_level",
    "log_status",
    "log_warning",
    "log_trace",
    "log_error",
    "setup_logger",
    "set_debug_mode",
    "get_verbose_mode",
    # Formatters
    "trace_parameter",
    "track_global_param",
    "log_context",
]
