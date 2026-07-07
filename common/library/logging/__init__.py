"""Architecture-aligned logging package for shared pipeline libraries."""

from common.library.core.logging.logger import UniversalLogger, get_global_logger, set_global_logger
from common.library.core.logging.depth import log_depth, log_context
from common.library.core.logging.trace import trace_parameter, track_global_param, trace_step
from common.library.core.logging.snapshot import get_system_snapshot

__all__ = [
    "UniversalLogger",
    "get_global_logger",
    "set_global_logger",
    "log_depth",
    "log_context",
    "trace_parameter",
    "track_global_param",
    "trace_step",
    "get_system_snapshot",
]
