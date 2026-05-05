"""
Log formatters and context management.
"""
import time
from contextlib import contextmanager
from typing import Any

from core_engine.logging.log_state import DEBUG_LEVEL, DEBUG_OBJECT, CALL_DEPTH
from core_engine.logging.log_handlers import log_status, log_warning, log_error


def trace_parameter(name: str, value: Any, source: str = "", status: str = "", duration_ms: float = 0.0) -> None:
    from datetime import datetime
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "value": str(value)[:200],
        "source": source,
        "status": status,
        "depth": CALL_DEPTH,
        "duration_ms": duration_ms,
    }
    DEBUG_OBJECT["trace_table"].append(entry)
    if DEBUG_LEVEL >= 2:
        log_warning(f"Param '{name}' = {value!r} [{status}] from {source}", "trace")

def track_global_param(name: str, value: Any, stage: str = "") -> None:
    from datetime import datetime
    if name not in DEBUG_OBJECT["global_parameters"]:
        DEBUG_OBJECT["global_parameters"][name] = {}
    DEBUG_OBJECT["global_parameters"][name][stage or "current"] = {
        "value": str(value)[:200],
        "timestamp": datetime.now().isoformat(),
    }
    if DEBUG_LEVEL >= 2:
        log_warning(f"Global '{name}' at stage '{stage}': {value!r}", "global")


@contextmanager
def log_context(module: str, context: str, min_level: int = 3):
    global CALL_DEPTH
    log_status(f"▶ {context}", module, min_level=min_level)
    CALL_DEPTH += 1
    start_time = time.time()
    try:
        yield
    except Exception as e:
        log_error(f"Exception in {context}: {e}", module, fatal=False)
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        CALL_DEPTH -= 1
        log_status(f"◀ {context} ({duration:.1f}ms)", module, min_level=min_level)
