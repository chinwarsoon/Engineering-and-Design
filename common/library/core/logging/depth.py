"""
L02 — Call-depth tracking: log_depth decorator + log_context context manager.

Both forms share the same _depth counter imported from logger.py.

Sources
-------
dcc: core_engine/logging/log_formatters.py  (log_context context manager, CALL_DEPTH global)
eks: engine/logging/logger.py               (log_depth decorator, _depth global)
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Optional

import common.library.core.logging.logger as _logger_module


def log_depth(func):
    """
    Decorator — increments the global call-depth counter before the call
    and decrements it after, enabling indented log output.

    Usage
    -----
    @log_depth
    def my_method(self, ...):
        ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        _logger_module._depth += 1
        try:
            return func(*args, **kwargs)
        finally:
            _logger_module._depth -= 1
    return wrapper


@contextmanager
def log_context(
    module: str,
    context: str,
    min_level: int = 3,
    logger=None,
):
    """
    Context manager — increments depth, logs entry/exit with timing.

    Parameters
    ----------
    module    : str  — component name for log prefix
    context   : str  — label for the block (shown on entry and exit)
    min_level : int  — minimum verbosity level to emit entry/exit lines
    logger    : UniversalLogger | None — uses global logger if None

    Usage
    -----
    with log_context("MyEngine", "load_schema"):
        ...
    """
    from common.library.core.logging.logger import get_global_logger
    lg = logger or get_global_logger()

    if lg.level >= min_level:
        lg.status(f"▶ {context}", context=module)

    _logger_module._depth += 1
    start = time.time()
    try:
        yield
    except Exception as exc:
        lg.error(f"Exception in {context}: {exc}", context=module, fatal=False)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        _logger_module._depth -= 1
        if lg.level >= min_level:
            lg.status(f"◀ {context} ({duration_ms:.1f}ms)", context=module)
