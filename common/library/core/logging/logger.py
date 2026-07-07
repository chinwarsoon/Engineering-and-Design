"""
L01 — UniversalLogger

Merges DCC log_handlers/log_state (module-level functions + global DEBUG_OBJECT)
with EKS EKSLogger (class with per-instance debug_object).

Design decisions
----------------
- Class-based so each pipeline component owns its own debug_object (EKS pattern).
- Optional global singleton via get_global_logger() / set_global_logger() for
  DCC-style module-level log_status/log_error calls.
- 4 verbosity levels: 0=silent, 1=status/info, 2=warning/debug, 3=trace.
- debug_object schema is the union of DCC and EKS fields.

Sources
-------
dcc: core_engine/logging/log_handlers.py, log_state.py
eks: engine/logging/logger.py (EKSLogger)
"""

import json
import os
import sys
import platform
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from common.library.core.logging.snapshot import get_system_snapshot


# ---------------------------------------------------------------------------
# Global depth counter (shared with depth.py)
# ---------------------------------------------------------------------------
_depth: int = 0


class UniversalLogger:
    """
    Tiered logger for pipeline projects.

    Levels
    ------
    0  silent   — only fatal errors printed
    1  status   — milestone progress and high-level workflow status  (default)
    2  debug    — warnings, detailed info for debugging
    3  trace    — deep technical info

    Attributes
    ----------
    name        : str   — component name shown in every log line
    level       : int   — current verbosity level (0–3)
    debug_file  : Path  — optional path to write debug_object JSON on save()
    debug_object: dict  — structured log accumulator
    """

    def __init__(
        self,
        name: str,
        level: int = 1,
        debug_file: Optional[str | Path] = None,
    ):
        self.name = name
        self.level = level
        self.debug_file = Path(debug_file) if debug_file else None
        self.debug_object: Dict[str, Any] = {
            "project": name,
            "start_time": datetime.now().isoformat(),
            "system_snapshot": get_system_snapshot(),
            "trace_table": [],
            "global_parameters": {},
            "logs": [],
            "messages": [],
            "errors": [],
            "duration_ms": 0,
        }

    # ------------------------------------------------------------------
    # Internal emit
    # ------------------------------------------------------------------

    def _log(self, level: int, msg: str, category: str, context: Optional[str] = None) -> None:
        if level > self.level:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        indent = "  " * _depth
        ctx_str = f" [{context}]" if context else ""
        print(f"{timestamp} | {category:7} | {self.name}{ctx_str} | {indent}{msg}", flush=True)
        self.debug_object["logs"].append({
            "timestamp": timestamp,
            "level": level,
            "category": category,
            "context": context,
            "module": self.name,
            "message": msg,
        })

    # ------------------------------------------------------------------
    # Public log methods
    # ------------------------------------------------------------------

    def status(self, msg: str, context: Optional[str] = None) -> None:
        """Level 1 — milestone / high-level workflow status."""
        self._log(1, msg, "STATUS", context)

    def info(self, msg: str, context: Optional[str] = None) -> None:
        """Level 1 — general informational message."""
        self._log(1, msg, "INFO", context)

    def warning(self, msg: str, context: Optional[str] = None) -> None:
        """Level 2 — warning / detailed debug info."""
        self._log(2, msg, "WARNING", context)

    def debug(self, msg: str, context: Optional[str] = None) -> None:
        """Level 2 — debug information."""
        self._log(2, msg, "DEBUG", context)

    def trace(self, msg: str, context: Optional[str] = None) -> None:
        """Level 3 — deep technical info."""
        self._log(3, msg, "TRACE", context)

    def error(self, msg: str, context: Optional[str] = None, fatal: bool = False) -> None:
        """Level 0 — error always printed; fatal=True raises RuntimeError."""
        self._log(0, msg, "ERROR", context)
        self.debug_object["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "message": msg,
            "fatal": fatal,
        })
        if fatal:
            raise RuntimeError(f"[{self.name}] {context or ''}: {msg}")

    # ------------------------------------------------------------------
    # Trace table
    # ------------------------------------------------------------------

    def trace_step(
        self,
        step: str,
        parameter: str,
        value: Any,
        source: str,
        status: str = "SUCCESS",
        duration: float = 0.0,
    ) -> None:
        """Append a structured entry to the trace_table (L03)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "parameter": parameter,
            "value": str(value)[:200],
            "source": source,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "depth": _depth,
        }
        self.debug_object["trace_table"].append(entry)
        if self.level >= 2:
            self.debug(f"TRACE_STEP: {step} | {parameter}={value} | {status}", context=source)

    def track_global_param(self, name: str, value: Any, stage: str = "") -> None:
        """Track a named parameter value at a named pipeline stage (L03)."""
        if name not in self.debug_object["global_parameters"]:
            self.debug_object["global_parameters"][name] = {}
        self.debug_object["global_parameters"][name][stage or "current"] = {
            "value": str(value)[:200],
            "timestamp": datetime.now().isoformat(),
        }
        if self.level >= 2:
            self.debug(f"Global '{name}' at stage '{stage}': {value!r}")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, output_path: Optional[str | Path] = None) -> Path:
        """Save debug_object to JSON. Uses debug_file if output_path not given."""
        target = Path(output_path) if output_path else self.debug_file
        if target is None:
            target = Path(f"debug_{self.name.lower()}.json")
        self.debug_object["end_time"] = datetime.now().isoformat()
        start = self.debug_object.get("start_time")
        if start:
            elapsed = (datetime.fromisoformat(self.debug_object["end_time"]) -
                       datetime.fromisoformat(start)).total_seconds() * 1000
            self.debug_object["duration_ms"] = round(elapsed, 2)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.debug_object, indent=2, default=str), encoding="utf-8")
        self.status(f"Debug log saved to {target}")
        return target

    def set_level(self, level: int) -> None:
        """Set verbosity level (0–3)."""
        self.level = max(0, min(3, level))


# ---------------------------------------------------------------------------
# Global singleton (DCC-style module-level usage)
# ---------------------------------------------------------------------------

_global_logger: Optional[UniversalLogger] = None


def get_global_logger() -> UniversalLogger:
    """Return the process-wide logger, creating a default one if needed."""
    global _global_logger
    if _global_logger is None:
        _global_logger = UniversalLogger("global")
    return _global_logger


def set_global_logger(logger: UniversalLogger) -> None:
    """Replace the process-wide logger."""
    global _global_logger
    _global_logger = logger


# Convenience module-level functions (DCC backward-compat shim)
def log_status(msg: str, module: str = "", context: str = "", min_level: int = 1) -> None:
    get_global_logger().status(f"[{module}] {msg}" if module else msg, context=context or None)


def log_warning(msg: str, module: str = "", context: str = "") -> None:
    get_global_logger().warning(f"[{module}] {msg}" if module else msg, context=context or None)


def log_error(msg: str, module: str = "", context: str = "", fatal: bool = False) -> None:
    get_global_logger().error(f"[{module}] {msg}" if module else msg, context=context or None, fatal=fatal)


def log_trace(msg: str, module: str = "", context: str = "") -> None:
    get_global_logger().trace(f"[{module}] {msg}" if module else msg, context=context or None)
