"""
Global state variables for logging system.
"""
import logging
import sys
import platform
from typing import Any, Dict
from datetime import datetime


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

def save_debug_log(output_path=None) -> Any:
    from pathlib import Path
    global DEBUG_OBJECT
    DEBUG_OBJECT["duration_ms"] = _calculate_duration()
    
    if output_path is None:
        # Task B5a: Use filename from parameters if available (SSOT)
        params = DEBUG_OBJECT.get("global_parameters", {})
        filename = params.get("debug_log_filename", "debug_log.json")
        output_path = Path(filename)
    
    output_path = Path(output_path)
    import json
    output_path.write_text(json.dumps(DEBUG_OBJECT, indent=2, default=str))
    return output_path

def _calculate_duration() -> float:
    if DEBUG_OBJECT.get("timestamp"):
        start = datetime.fromisoformat(DEBUG_OBJECT["timestamp"])
        return (datetime.now() - start).total_seconds() * 1000
    return 0.0
