"""
L03 — Trace parameter / trace step utilities.

Provides module-level functions that append structured entries to the
active logger's trace_table and global_parameters dict.

Sources
-------
dcc: core_engine/logging/log_formatters.py  (trace_parameter, track_global_param)
eks: engine/logging/logger.py               (EKSLogger.trace_step)
"""

from datetime import datetime
from typing import Any, Optional

import common.library.core.logging.logger as _logger_module


def trace_parameter(
    name: str,
    value: Any,
    source: str = "",
    status: str = "SUCCESS",
    duration_ms: float = 0.0,
    logger=None,
) -> None:
    """Compatibility wrapper for the DCC-style trace_parameter API."""
    from common.library.core.logging.logger import get_global_logger
    lg = logger or get_global_logger()
    lg.trace_step("trace_parameter", name, value, source, status, duration_ms / 1000)


def trace_step(
    step: str,
    parameter: str,
    value: Any,
    source: str = "",
    status: str = "SUCCESS",
    duration_ms: float = 0.0,
    logger=None,
) -> None:
    """
    Append a structured trace entry to the active logger's trace_table.

    Unified schema (union of DCC trace_parameter + EKS trace_step):
        timestamp, step, parameter, value, source, status, duration_ms, depth

    Parameters
    ----------
    step        : str   — logical step name (e.g. "load_schema", "P1")
    parameter   : str   — parameter or variable name being traced
    value       : Any   — value (truncated to 200 chars in storage)
    source      : str   — origin module or function
    status      : str   — "SUCCESS", "FAIL", "SKIP", etc.
    duration_ms : float — elapsed time for this step in milliseconds
    logger      : UniversalLogger | None — uses global logger if None
    """
    from common.library.core.logging.logger import get_global_logger
    lg = logger or get_global_logger()
    lg.trace_step(step, parameter, value, source, status, duration_ms / 1000)


def track_global_param(
    name: str,
    value: Any,
    stage: str = "",
    logger=None,
) -> None:
    """
    Record a named parameter value at a named pipeline stage.

    Stored under debug_object["global_parameters"][name][stage].

    Parameters
    ----------
    name   : str — parameter name
    value  : Any — current value
    stage  : str — pipeline stage label (e.g. "post_cli", "post_schema")
    logger : UniversalLogger | None — uses global logger if None
    """
    from common.library.core.logging.logger import get_global_logger
    lg = logger or get_global_logger()
    lg.track_global_param(name, value, stage)
