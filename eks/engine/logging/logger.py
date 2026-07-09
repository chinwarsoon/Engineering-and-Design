"""
Tiered Logging for EKS - Implements agent_rule.md Section 6.
"""
import json
import os
import sys
import time
import psutil
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Global depth counter for indentation (Section 6.4)
_depth = 0

class EKSLogger:
    """
    Tiered logging strategy for EKS.
    Supports levels 0-3, debug object collection, structured trace table, and run_id correlation.
    """
    def __init__(self, name: str, level: int = 1, debug_file: Optional[str | Path] = None,
                 run_id: Optional[str] = None):
        self.name = name
        self.level = level
        self.run_id = run_id
        self.debug_file = Path(debug_file) if debug_file else None
        self.debug_object: Dict[str, Any] = {
            "project": "EKS",
            "start_time": datetime.now().isoformat(),
            "system_snapshot": self._get_system_snapshot(),
            "run_id": run_id,
            "trace_table": [],
            "logs": [],
            "errors": []
        }

    def _get_system_snapshot(self) -> Dict[str, Any]:
        """Record system snapshot (Section 6.8)."""
        return {
            "os": sys.platform,
            "python_version": sys.version,
            "cpu_count": os.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "cwd": os.getcwd()
        }

    def _indent(self) -> str:
        return "  " * _depth

    def _log(self, level: int, msg: str, category: str = "INFO", context: Optional[str] = None):
        if level <= self.level:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            indent = self._indent()
            ctx_str = f" [{context}]" if context else ""
            print_msg = f"{timestamp} | {category:7} | {self.name}{ctx_str} | {indent}{msg}"
            print(print_msg)
            
            # Record in debug object
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "category": category,
                "context": context,
                "module": self.name,
                "run_id": self.run_id,
                "message": msg
            }
            if self.run_id:
                print_msg = f"[{self.run_id}] {print_msg}"
            self.debug_object["logs"].append(log_entry)

    def status(self, msg: str, context: Optional[str] = None):
        """Level 1: Milestone progress / high-level workflow status."""
        self._log(1, msg, "STATUS", context)

    def info(self, msg: str, context: Optional[str] = None):
        """Level 1: General info."""
        self._log(1, msg, "INFO", context)

    def warning(self, msg: str, context: Optional[str] = None):
        """Level 2: Warnings / detailed info for debugging."""
        self._log(2, msg, "WARNING", context)

    def debug(self, msg: str, context: Optional[str] = None):
        """Level 2: Debug information."""
        self._log(2, msg, "DEBUG", context)

    def trace(self, msg: str, context: Optional[str] = None):
        """Level 3: Deep technical info."""
        self._log(3, msg, "TRACE", context)

    def error(self, msg: str, context: Optional[str] = None):
        """Level 0: Critical errors."""
        self._log(0, msg, "ERROR", context)
        self.debug_object["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "message": msg
        })

    def trace_step(self, step: str, parameter: str, value: Any, source: str, status: str = "SUCCESS", duration: float = 0.0):
        """Structured trace table (Section 6.3)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "parameter": parameter,
            "value": str(value),
            "source": source,
            "status": status,
            "duration_ms": round(duration * 1000, 2)
        }
        self.debug_object["trace_table"].append(entry)
        if self.level >= 2:
            self.debug(f"TRACE_STEP: {step} | {parameter}={value} | {status}", context=source)

    def save_debug_log(self):
        """Save debug object to JSON file (Section 6.2)."""
        if self.debug_file:
            self.debug_object["end_time"] = datetime.now().isoformat()
            self.debug_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.debug_file, "w", encoding="utf-8") as f:
                json.dump(self.debug_object, f, indent=4)
            self.status(f"Debug log saved to {self.debug_file}")

def log_depth(func):
    """Decorator to manage global depth counter (Section 6.4)."""
    def wrapper(*args, **kwargs):
        global _depth
        _depth += 1
        try:
            return func(*args, **kwargs)
        finally:
            _depth -= 1
    return wrapper
