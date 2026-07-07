"""
common.library.core.logging — Universal logging for all pipeline projects.

Exports
-------
UniversalLogger     L01  Tiered logger with debug object (merges EKSLogger + DCC log_handlers)
log_depth           L02  Decorator — increments/decrements global call-depth counter
log_context         L02  Context manager — same depth counter, times the block
trace_step          L03  Append a structured entry to the active logger's trace_table
track_global_param  L03  Track a named parameter value at a named stage
get_system_snapshot L04  Capture OS/Python/memory/CPU snapshot dict

Sources
-------
L01/L02/L03/L04  dcc: core_engine/logging/log_handlers.py, log_state.py, log_formatters.py
L01/L02/L03/L04  eks: engine/logging/logger.py
"""

from common.library.core.logging.logger import UniversalLogger
from common.library.core.logging.depth import log_depth, log_context
from common.library.core.logging.trace import trace_step, track_global_param
from common.library.core.logging.snapshot import get_system_snapshot

__all__ = [
    "UniversalLogger",
    "log_depth",
    "log_context",
    "trace_step",
    "track_global_param",
    "get_system_snapshot",
]
