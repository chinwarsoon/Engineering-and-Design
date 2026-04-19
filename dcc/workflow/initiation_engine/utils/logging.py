"""
Tiered logging and debug utilities for initiation_engine.
Implements structured logging with hierarchy levels, trace tables, and debug objects.
"""

import logging
import sys
import builtins
import json
import time
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
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
    """
    Initialize the global debug object with system snapshot.

    Breadcrumb Comments:
        - DEBUG_OBJECT: Global dict initialized here with metadata.
                       Modified by all logging functions to accumulate debug info.
                       Saved to debug_log.json at workflow end.
    """
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
    """Capture system information for level 1 logging."""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "timestamp": datetime.now().isoformat(),
    }


def get_debug_object() -> Dict[str, Any]:
    """Get the current debug object."""
    return DEBUG_OBJECT


def save_debug_log(output_path: Optional[Path] = None) -> Path:
    """
    Save debug object to debug_log.json.

    Args:
        output_path: Optional path for debug log. Defaults to base_path/debug_log.json.

    Returns:
        Path to saved debug log file.

    Breadcrumb Comments:
        - DEBUG_OBJECT: Read here and serialized to JSON.
                       Saved to disk for post-mortem analysis.
    """
    global DEBUG_OBJECT
    DEBUG_OBJECT["duration_ms"] = _calculate_duration()

    if output_path is None:
        output_path = Path("debug_log.json")

    output_path = Path(output_path)
    output_path.write_text(json.dumps(DEBUG_OBJECT, indent=2, default=str))
    return output_path


def _calculate_duration() -> float:
    """Calculate elapsed time since debug object initialization."""
    if DEBUG_OBJECT.get("timestamp"):
        start = datetime.fromisoformat(DEBUG_OBJECT["timestamp"])
        return (datetime.now() - start).total_seconds() * 1000
    return 0.0


# =============================================================================
# TIERED LOGGING
# =============================================================================

def set_debug_level(level: int) -> None:
    """
    Set global debug verbosity level.

    Args:
        level: 0=silent/errors only, 1=status/info, 2=warning/debug, 3=trace

    Breadcrumb Comments:
        - DEBUG_LEVEL: Global integer modified here.
                      Consumed by log_status(), log_debug(), log_trace().
    """
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, level))
    # Suppress third-party library warnings at levels 0 and 1
    import warnings
    if DEBUG_LEVEL < 2:
        warnings.filterwarnings("ignore")
    else:
        warnings.resetwarnings()


def _get_indent() -> str:
    """Get indentation based on call depth."""
    return "  " * CALL_DEPTH


def log_status(message: str, module: str = "", context: str = "", min_level: int = 1) -> None:
    """
    Level 1: Milestone progress / high-level workflow status.

    Args:
        message: Status message to display.
        module: Module name for context.
        context: Additional calling context.
        min_level: Minimum DEBUG_LEVEL required to print (default 1).
                   Use min_level=2 for step detail, min_level=3 for internal calls.

    Breadcrumb Comments:
        - DEBUG_LEVEL: Checked here - only outputs if level >= min_level.
        - DEBUG_OBJECT: Appends message to 'messages' list.
    """
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
    """
    Level 2: Warnings, detailed debugging, variable values, path resolutions.

    Args:
        message: Warning/debug message.
        module: Module name for context.
        context: Additional calling context.

    Breadcrumb Comments:
        - DEBUG_LEVEL: Checked here - only outputs if level >= 2.
        - DEBUG_OBJECT: Appends message to 'messages' list.
    """
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
    """
    Level 3: Deep technical info - OS path slashes, JSON raw extraction, etc.

    Args:
        message: Trace message.
        module: Module name for context.
        context: Additional calling context.

    Breadcrumb Comments:
        - DEBUG_LEVEL: Checked here - only outputs if level >= 3.
        - DEBUG_OBJECT: Appends message to 'messages' list.
    """
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
    """
    Log errors. Always shown regardless of debug level.

    Args:
        message: Error message.
        module: Module name for context.
        context: Additional calling context.
        fatal: If True, raises exception (fail-fast).
        severity: Error severity (CRITICAL, HIGH, MEDIUM, WARNING, INFO).
                  Defaults to CRITICAL if fatal=True, else ERROR.
        show_summary: If True, show abbreviated error + reference to report file.

    Breadcrumb Comments:
        - DEBUG_LEVEL: Errors always output regardless of level.
        - DEBUG_OBJECT: Appends to 'errors' list.
        - If fatal=True, raises RuntimeError immediately (fail-fast).
    """
    if severity is None:
        severity = "CRITICAL" if fatal else "ERROR"
        
    prefix = _get_indent()
    if module:
        prefix += f"[{module}] "
    if context:
        prefix += f"({context}) "

    # Show errors based on verbosity level
    # Level 0: Silent (no error output)
    # Level 1: Summary only (no individual errors)
    # Level 2: Abbreviated errors (truncated)
    # Level 3: Full errors
    if DEBUG_LEVEL >= 3:
        # Level 3: Show full error
        builtins.print(f"{prefix}[ERROR] {message}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 2:
        # Level 2: Truncate long messages
        if len(message) > 100:
            short_msg = message[:97] + "..."
        else:
            short_msg = message
        builtins.print(f"{prefix}[ERROR] {short_msg}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 1:
        # Level 1: No individual errors - they appear in final summary
        # Only log to DEBUG_OBJECT, don't print
        pass
    else:
        # Level 0: Silent - only critical/fatal errors
        if severity == "CRITICAL" or fatal:
            builtins.print(f"{prefix}[ERROR] {message}", flush=True, file=sys.stderr)

    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": context,
        "message": message,
        "fatal": fatal,
        "severity": severity
    }
    DEBUG_OBJECT["errors"].append(error_entry)

    if fatal:
        raise RuntimeError(f"[{module}] {context}: {message}")


# =============================================================================
# TRACE TABLE
# =============================================================================

def trace_parameter(
    name: str,
    value: Any,
    source: str = "",
    status: str = "",
    duration_ms: float = 0.0,
) -> None:
    """
    Add entry to structured trace table for parameter flow tracking.

    Args:
        name: Parameter name.
        value: Parameter value (will be stringified).
        source: Where the parameter came from.
        status: Status of the parameter (e.g., 'resolved', 'modified', 'error').
        duration_ms: Optional timing information.

    Breadcrumb Comments:
        - DEBUG_OBJECT['trace_table']: Appends structured entry here.
                                     Used for tracking parameter lifecycle.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "value": str(value)[:200],  # Truncate long values
        "source": source,
        "status": status,
        "depth": CALL_DEPTH,
        "duration_ms": duration_ms,
    }
    DEBUG_OBJECT["trace_table"].append(entry)

    if DEBUG_LEVEL >= 2:
        log_warning(f"Param '{name}' = {value!r} [{status}] from {source}", "trace")


# =============================================================================
# GLOBAL PARAMETER TRACKING
# =============================================================================

def track_global_param(name: str, value: Any, stage: str = "") -> None:
    """
    Track global parameter state before/after major transformations.

    Args:
        name: Parameter name.
        value: Current value.
        stage: 'before' or 'after' transformation.

    Breadcrumb Comments:
        - DEBUG_OBJECT['global_parameters']: Records parameter state.
                                          Captures before/after for debugging.
    """
    if name not in DEBUG_OBJECT["global_parameters"]:
        DEBUG_OBJECT["global_parameters"][name] = {}

    DEBUG_OBJECT["global_parameters"][name][stage or "current"] = {
        "value": str(value)[:200],
        "timestamp": datetime.now().isoformat(),
    }

    if DEBUG_LEVEL >= 2:
        log_warning(f"Global '{name}' at stage '{stage}': {value!r}", "global")


# =============================================================================
# HIERARCHICAL CONTEXT MANAGER
# =============================================================================

@contextmanager
def log_context(module: str, context: str, min_level: int = 3):
    """
    Context manager for hierarchical logging with automatic indentation.

    Args:
        module: Module name.
        context: Function or operation name.
        min_level: Minimum level to print enter/exit markers (default 3 = trace only).

    Breadcrumb Comments:
        - CALL_DEPTH: Incremented on entry, decremented on exit.
                     Used by _get_indent() for visual hierarchy.
    """
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


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

def status_print(*args: Any, **kwargs: Any) -> None:
    """
    Legacy status print - maps to level 1 logging.
    Accepts optional min_level kwarg (default 1).
    """
    message = " ".join(str(a) for a in args)
    min_level = kwargs.get("min_level", 1)
    log_status(message, min_level=min_level)


def milestone_print(step: str, detail: str, ok: bool = True) -> None:
    """
    Print a clean pipeline milestone line — always visible at level 1+.

    Args:
        step: Step label (e.g. 'Setup validated')
        detail: Detail string (e.g. '7 folders, 11 files')
        ok: True for ✓, False for ✗

    Breadcrumb Comments:
        - DEBUG_LEVEL: Prints at level >= 1 only.
    """
    if DEBUG_LEVEL >= 1:
        icon = "✓" if ok else "✗"
        builtins.print(f"  {icon}  {step:<22} {detail}", flush=True)
    DEBUG_OBJECT["messages"].append({
        "level": 1,
        "timestamp": datetime.now().isoformat(),
        "module": "milestone",
        "context": step,
        "message": detail,
    })


def debug_print(*args: Any, **kwargs: Any) -> None:
    """
    Legacy debug print - maps to level 2 logging.
    Kept for backward compatibility.
    """
    message = " ".join(str(a) for a in args)
    log_warning(message)


def setup_logger(debug_mode: bool = False) -> None:
    """
    Legacy setup - configures standard Python logging.
    Respects DEBUG_LEVEL for tiered output control.
    """
    global DEBUG_LEVEL
    # Map DEBUG_LEVEL to Python logging levels
    # 0=quiet: ERROR only, 1=normal: WARNING+ (filtered), 2=debug: INFO+, 3=trace: DEBUG+
    if DEBUG_LEVEL >= 3:
        level = logging.DEBUG
    elif DEBUG_LEVEL >= 2:
        level = logging.INFO
    elif DEBUG_LEVEL >= 1:
        level = logging.WARNING
    else:  # quiet mode - only errors
        level = logging.ERROR
    
    # Forcefully set root logger level (handles cases where handlers already exist)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Set levels for engine loggers
    engine_loggers = ['ai_ops_engine', 'processor_engine', 'schema_engine', 'mapper_engine']
    for logger_name in engine_loggers:
        logging.getLogger(logger_name).setLevel(level)
    
    # Suppress optional dependency warnings (duckdb, etc.) at normal and quiet levels
    # These are non-critical and don't affect pipeline functionality
    if DEBUG_LEVEL <= 1:
        logging.getLogger('ai_ops_engine.persistence').setLevel(logging.ERROR)
        # Suppress non-critical detector registration warnings
        logging.getLogger('processor_engine.error_handling.detectors').setLevel(logging.ERROR)
    if DEBUG_LEVEL == 0:
        # At quiet level, also suppress non-critical validation errors (they appear in final summary)
        logging.getLogger('processor_engine.calculations.validation').setLevel(logging.CRITICAL)
    
    # Only configure basicConfig if no handlers exist yet
    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            stream=sys.stdout,
        )


def set_debug_mode(enabled: bool) -> None:
    """
    Legacy debug mode setter.
    Kept for backward compatibility.
    """
    set_debug_level(2 if enabled else 1)


# =============================================================================
# FRAMEWORK BANNER (ALWAYS VISIBLE)
# =============================================================================

def print_framework_banner(
    input_file: str = None,
    output_dir: str = None,
    version: str = "3.0",
) -> None:
    """
    Print default framework banner (visible at ALL verbosity levels).
    
    Args:
        input_file: Input Excel filename
        output_dir: Output directory path
        version: Pipeline version
    """
    mode = {0: "quiet", 1: "normal", 2: "debug", 3: "trace"}.get(DEBUG_LEVEL, "normal")
    
    # Simplify paths to basenames
    input_name = Path(input_file).name if input_file else "stdin"
    output_name = Path(output_dir).name if output_dir else "output"
    
    if DEBUG_LEVEL == 0:
        # Quiet mode - minimal single line
        banner = f"╔ DCC Pipeline v{version} | Input: {input_name} | Mode: quiet ═╗"
    elif DEBUG_LEVEL == 1:
        # Normal mode - clean milestone
        banner = f"""╔═══════════════════════════════════════════════════════╗
║  DCC Pipeline v{version} | Input: {input_name}     ║
║  Mode: {mode:^43}║
╚═══════════════════════════════════════════════════════╝"""
    else:
        # Debug/trace mode - with context
        banner = f"""╔═══════════════════════════════════════════════════════════════╗
║  DCC Pipeline v{version} | Input: {input_name} | Mode: {mode} ═╗
║  Output: {output_name:<49}║
║  DEBUG {'ENABLED' if DEBUG_LEVEL >= 2 else 'DISABLED':<49}║
╚═══════════════════════════════════════════════════════════════════════╝"""
    
    builtins.print(banner, flush=True)


def get_verbose_mode() -> str:
    """Get current verbosity mode as string."""
    return {0: "quiet", 1: "normal", 2: "debug", 3: "trace"}.get(DEBUG_LEVEL, "normal")
