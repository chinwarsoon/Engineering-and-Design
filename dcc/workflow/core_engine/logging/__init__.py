"""
Tiered logging and debug utilities.
Implements structured logging with hierarchy levels, trace tables, and debug objects.
"""
import logging
import sys
import builtins
import json
import time
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager


# =============================================================================
# GLOBAL STATE
# =============================================================================

DEBUG_LEVEL = 1  # 0=silent, 1=status/info, 2=warning/debug, 3=trace
CALL_DEPTH = 0   # For hierarchical indentation
DEBUG_OBJECT: Dict[str, Any] = {
    "timestamp": None,
    "system_snapshot": {},
    "trace_table": [],
    "global_parameters": {},
    "messages": [],
    "errors": [],
}

# =============================================================================
# DEBUG OBJECT MANAGEMENT
# =============================================================================

def init_debug_object() -> None:
    global DEBUG_OBJECT
    DEBUG_OBJECT = {
        "timestamp": datetime.now().isoformat(),
        "system_snapshot": _get_system_snapshot(),
        "trace_table": [],
        "global_parameters": {},
        "messages": [],
        "errors": [],
        "duration_ms": 0,
    }

def _get_system_snapshot() -> Dict[str, Any]:
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat(),
    }

def get_debug_object() -> Dict[str, Any]:
    return DEBUG_OBJECT

def save_debug_log(output_path: Optional[Path] = None) -> Path:
    global DEBUG_OBJECT
    DEBUG_OBJECT["duration_ms"] = _calculate_duration()
    if output_path is None:
        output_path = Path("debug_log.json")
    output_path = Path(output_path)
    output_path.write_text(json.dumps(DEBUG_OBJECT, indent=2, default=str))
    return output_path

def _calculate_duration() -> float:
    if DEBUG_OBJECT.get("timestamp"):
        start = datetime.fromisoformat(DEBUG_OBJECT["timestamp"])
        return (datetime.now() - start).total_seconds() * 1000
    return 0.0

# =============================================================================
# TIERED LOGGING
# =============================================================================

def set_debug_level(level: int) -> None:
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, level))
    import warnings
    if DEBUG_LEVEL < 2:
        warnings.filterwarnings("ignore")
    else:
        warnings.resetwarnings()

def _get_indent() -> str:
    return "  " * CALL_DEPTH

def log_status(message: str, module: str = "", context: str = "", min_level: int = 1) -> None:
    if DEBUG_LEVEL >= min_level:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}{message}", flush=True)

    DEBUG_OBJECT["messages"].append({
        "level": min_level,
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": context,
        "message": message,
    })

def log_warning(message: str, module: str = "", context: str = "") -> None:
    if DEBUG_LEVEL >= 2:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}[DEBUG] {message}", flush=True)

    DEBUG_OBJECT["messages"].append({
        "level": 2,
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": context,
        "message": message,
    })

def log_trace(message: str, module: str = "", context: str = "") -> None:
    if DEBUG_LEVEL >= 3:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}[TRACE] {message}", flush=True)

    DEBUG_OBJECT["messages"].append({
        "level": 3,
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": context,
        "message": message,
    })

def log_error(message: str, module: str = "", context: str = "", fatal: bool = False, severity: Optional[str] = None, show_summary: bool = True) -> None:
    if severity is None:
        severity = "CRITICAL" if fatal else "ERROR"
        
    prefix = _get_indent()
    if module:
        prefix += f"[{module}] "
    if context:
        prefix += f"({context}) "

    if DEBUG_LEVEL >= 3:
        builtins.print(f"{prefix}[ERROR] {message}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 2:
        short_msg = message[:97] + "..." if len(message) > 100 else message
        builtins.print(f"{prefix}[ERROR] {short_msg}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 1:
        pass
    else:
        if severity == "CRITICAL" or fatal:
            builtins.print(f"{prefix}[ERROR] {message}", flush=True, file=sys.stderr)

    DEBUG_OBJECT["errors"].append({
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": context,
        "message": message,
        "fatal": fatal,
        "severity": severity
    })

    if fatal:
        raise RuntimeError(f"[{module}] {context}: {message}")

# =============================================================================
# TRACE TABLE & GLOBAL PARAMETERS
# =============================================================================

def trace_parameter(name: str, value: Any, source: str = "", status: str = "", duration_ms: float = 0.0) -> None:
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
    if name not in DEBUG_OBJECT["global_parameters"]:
        DEBUG_OBJECT["global_parameters"][name] = {}
    DEBUG_OBJECT["global_parameters"][name][stage or "current"] = {
        "value": str(value)[:200],
        "timestamp": datetime.now().isoformat(),
    }
    if DEBUG_LEVEL >= 2:
        log_warning(f"Global '{name}' at stage '{stage}': {value!r}", "global")

# =============================================================================
# CONTEXT MANAGER & SETUP
# =============================================================================

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

def setup_logger(debug_mode: bool = False) -> None:
    global DEBUG_LEVEL
    if DEBUG_LEVEL >= 3:
        level = logging.DEBUG
    elif DEBUG_LEVEL >= 2:
        level = logging.INFO
    elif DEBUG_LEVEL >= 1:
        level = logging.WARNING
    else:
        level = logging.ERROR
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    engine_loggers = ['ai_ops_engine', 'processor_engine', 'schema_engine', 'mapper_engine']
    for logger_name in engine_loggers:
        logging.getLogger(logger_name).setLevel(level)
    
    if DEBUG_LEVEL <= 1:
        logging.getLogger('ai_ops_engine.persistence').setLevel(logging.ERROR)
        logging.getLogger('processor_engine.error_handling.detectors').setLevel(logging.ERROR)
    if DEBUG_LEVEL == 0:
        logging.getLogger('processor_engine.calculations.validation').setLevel(logging.CRITICAL)
    
    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            stream=sys.stdout,
        )

def set_debug_mode(enabled: bool) -> None:
    set_debug_level(2 if enabled else 1)

def get_verbose_mode() -> str:
    return {0: "quiet", 1: "normal", 2: "debug", 3: "trace"}.get(DEBUG_LEVEL, "normal")
