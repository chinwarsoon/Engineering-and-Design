"""
Log handlers for output operations.
"""
import sys
import builtins
import warnings
from typing import Optional, Dict
from datetime import datetime

from core_engine.logging.log_state import DEBUG_LEVEL, DEBUG_OBJECT, CALL_DEPTH


def _get_indent() -> str:
    return "  " * CALL_DEPTH


def set_debug_level(level: int) -> None:
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, level))
    if DEBUG_LEVEL < 2:
        warnings.filterwarnings("ignore")
    else:
        warnings.resetwarnings()


def log_status(message: str, module: str = "", context: str = "", min_level: int = 1, context_dict: Optional[Dict] = None) -> None:
    if DEBUG_LEVEL >= min_level:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}{message}", flush=True)

        # Dry Logging: Only store messages in JSON if they match the current debug level
        ctx_dict = context_dict if context_dict is not None else context
        DEBUG_OBJECT["messages"].append({
            "level": min_level,
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "context": ctx_dict,
            "message": {"description": message},
        })

def log_warning(message: str, module: str = "", context: str = "", context_dict: Optional[Dict] = None) -> None:
    if DEBUG_LEVEL >= 2:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}[DEBUG] {message}", flush=True)

        # Dry Logging: Respect level for storage
        ctx_dict = context_dict if context_dict is not None else context
        DEBUG_OBJECT["messages"].append({
            "level": 2,
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "context": ctx_dict,
            "message": {"description": message},
        })

def log_trace(message: str, module: str = "", context: str = "", context_dict: Optional[Dict] = None) -> None:
    if DEBUG_LEVEL >= 3:
        prefix = _get_indent()
        if module:
            prefix += f"[{module}] "
        if context:
            prefix += f"({context}) "
        builtins.print(f"{prefix}[TRACE] {message}", flush=True)

        # Dry Logging: Trace data is largest, only store if level is exactly TRACE
        ctx_dict = context_dict if context_dict is not None else context
        DEBUG_OBJECT["messages"].append({
            "level": 3,
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "context": ctx_dict,
            "message": {"description": message},
        })

def log_error(
    message: str = None, module: str = "", context: str = "",
    fatal: bool = False, severity: Optional[str] = None, show_summary: bool = True,
    error_code: str = None, description: str = None,
    row: int = None, column: str = None, context_dict: Optional[Dict] = None
) -> None:
    if severity is None:
        severity = "CRITICAL" if fatal else "ERROR"

    # Build structured message dict
    # Dry Logging: If error_code is provided, we omit the 'description' to save space.
    # The dashboard and reporters will "hydrate" the description from the error schemas.
    msg_dict = {
        "error_code": error_code,
        "row": row,
        "column": column,
    }
    
    # We only include description if:
    # 1. No error_code is provided (unstructured system error)
    # 2. It was explicitly provided and likely contains dynamic instance info
    if not error_code:
        msg_dict["description"] = description or message
    elif description and description != message:
        # If both are provided and different, 'description' might be specific context
        msg_dict["description"] = description

    msg_dict = {k: v for k, v in msg_dict.items() if v is not None}

    # Build structured context dict
    ctx_dict = context_dict or {}
    if context and not ctx_dict:
        ctx_dict = context

    # Dry Logging: Strip massive redundant objects from context (SSOT)
    # These are already available in schema files; logging them per-error caused 1.4GB bloat.
    if isinstance(ctx_dict, dict):
        ctx_dict = ctx_dict.copy() # Don't mutate caller's dict
        ctx_dict.pop("schema_data", None)
        ctx_dict.pop("error_catalog", None)
        ctx_dict.pop("blueprint", None)
        ctx_dict.pop("fill_history", None) # Also potentially large

    # Compose display string for console output (always remains descriptive)
    display_msg = message or ""
    if error_code and not display_msg.startswith(f"[{error_code}]"):
        display_msg = f"[{error_code}] {description or ''}"
    if row is not None:
        display_msg += f" (Row: {row + 1})"
    if column:
        display_msg += f" (Col: {column})"

    prefix = _get_indent()
    if module:
        prefix += f"[{module}] "
    if context and isinstance(context, str):
        prefix += f"({context}) "

    if DEBUG_LEVEL >= 3:
        builtins.print(f"{prefix}[ERROR] {display_msg}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 2:
        short_msg = display_msg[:97] + "..." if len(display_msg) > 100 else display_msg
        builtins.print(f"{prefix}[ERROR] {short_msg}", flush=True, file=sys.stderr)
    elif DEBUG_LEVEL == 1:
        pass
    else:
        if severity == "CRITICAL" or fatal:
            builtins.print(f"{prefix}[ERROR] {display_msg}", flush=True, file=sys.stderr)

    DEBUG_OBJECT["errors"].append({
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "context": ctx_dict,
        "message": msg_dict,
        "fatal": fatal,
        "severity": severity
    })

    if fatal:
        raise RuntimeError(f"[{module}] {context}: {display_msg}")


def setup_logger(debug_mode: bool = False) -> None:
    import logging
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
