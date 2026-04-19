"""
Structured JSON Logger Module

Provides structured JSON logging for error handling with context preservation.
Outputs logs in JSON format for parsing and analysis.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Import centralized logging from initiation_engine
try:
    from initiation_engine import log_error as init_log_error
    from initiation_engine import log_status as init_log_status
    from initiation_engine import log_warning as init_log_warning
    HAS_INITIATION_LOGGING = True
except ImportError:
    HAS_INITIATION_LOGGING = False

# Check DEBUG_LEVEL at import time (will be correct once all modules loaded)
try:
    from initiation_engine.utils.logging import DEBUG_LEVEL
    _INIT_LOG_LEVEL = DEBUG_LEVEL
except ImportError:
    _INIT_LOG_LEVEL = 1

class StructuredLogger:
    """
    Structured JSON logger for error handling.
    
    Outputs logs in JSON format with:
    - Timestamps with timezone
    - Structured context (row, column, phase, layer, error codes)
    - Severity levels
    - Machine-parseable format
    
    Bridges to initiation_engine's DEBUG_OBJECT for debug_log.json support.
    """
    
    _instance = None
    
    def __new__(cls, name: str = "error_handling"):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = "error_handling"):
        """Initialize structured logger."""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        
        # Prevent propagation to root logger to avoid duplicate messages
        self._logger.propagate = False
        
        # Only add handler if not already added
        if not self._logger.handlers:
            # Console handler with simple formatter for clean output
            handler = logging.StreamHandler(sys.stdout)
            # Respect DEBUG_LEVEL: quiet(0)=ERROR, normal(1)=ERROR, debug(2+)=WARNING
            handler_level = logging.WARNING if _INIT_LOG_LEVEL >= 2 else logging.ERROR
            handler.setLevel(handler_level)
            handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
            self._logger.addHandler(handler)
        
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set global context for all subsequent log entries."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear global context."""
        self._context = {}
    
    def log_error(
        self,
        error_code: str,
        message: str,
        row: Optional[int] = None,
        column: Optional[str] = None,
        phase: Optional[str] = None,
        layer: Optional[str] = None,
        severity: str = "ERROR",
        context: Optional[Dict[str, Any]] = None,
        remediation_type: Optional[str] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Log an error with full structured context.
        Suppresses non-critical errors at default verbosity level (1).
        """
        # Check DEBUG_LEVEL at runtime to get current value
        current_level = 1
        try:
            from initiation_engine.utils.logging import DEBUG_LEVEL
            current_level = DEBUG_LEVEL
        except ImportError:
            pass
        
        # Suppress at level 1 (default) - only CRITICAL shows
        if current_level <= 1 and severity != "CRITICAL":
            # Still bridge to init_log_error for debug_log.json persistence
            if HAS_INITIATION_LOGGING:
                msg_with_code = f"[{error_code}] {message}"
                if row is not None:
                    msg_with_code += f" (Row: {row+1})"
                if column:
                    msg_with_code += f" (Col: {column})"
                init_log_error(
                    msg_with_code,
                    module="processor",
                    context=f"phase:{phase}, layer:{layer}, source:StructuredLogger",
                    fatal=False,
                    show_summary=False  # Don't print, just store
                )
            return
        
        extra = {
            "error_code": error_code,
            "error_severity": severity,
            "row": row,
            "column": column,
            "phase": phase,
            "layer": layer,
            "remediation_type": remediation_type,
        }
        
        # Merge with global context
        extra.update(self._context)
        
        # Merge with provided context
        if context:
            extra.update(context)
        
        # Add exception info if provided
        if exception:
            extra["exception_type"] = type(exception).__name__
            extra["exception_message"] = str(exception)
        
        # Map severity to logging level
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(severity, logging.ERROR)
        
        # 1. Log to standard logger (stdout JSON)
        self._logger.log(level, message, extra={"structured": extra})
        
        # 2. Bridge to initiation_engine for debug_log.json
        if HAS_INITIATION_LOGGING:
            msg_with_code = f"[{error_code}] {message}"
            if row is not None:
                msg_with_code += f" (Row: {row+1})"
            if column:
                msg_with_code += f" (Col: {column})"
                
            init_log_error(
                msg_with_code, 
                module=extra.get("module", "processor"),
                context=f"phase:{phase}, layer:{layer}, source:StructuredLogger",
                fatal=False # Fail-fast is handled by the detector
            )
    
    def log_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        row_count: Optional[int] = None,
        error_count: Optional[int] = None
    ) -> None:
        """Log a phase transition in the processing pipeline."""
        extra = {
            "event_type": "phase_transition",
            "from_phase": from_phase,
            "to_phase": to_phase,
            "row_count": row_count,
            "error_count": error_count
        }
        extra.update(self._context)
        
        self._logger.info(
            f"Phase transition: {from_phase} -> {to_phase}",
            extra={"structured": extra}
        )
        
        if HAS_INITIATION_LOGGING:
            init_log_status(
                f"Phase transition: {from_phase} -> {to_phase}",
                module="processor"
            )
    
    def log_remediation(
        self,
        error_code: str,
        remediation_type: str,
        success: bool,
        row: Optional[int] = None,
        column: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a remediation attempt."""
        extra = {
            "event_type": "remediation",
            "error_code": error_code,
            "remediation_type": remediation_type,
            "remediation_success": success,
            "row": row,
            "column": column
        }
        
        if details:
            extra["remediation_details"] = details
        
        extra.update(self._context)
        
        level = logging.INFO if success else logging.WARNING
        status = "succeeded" if success else "failed"
        
        self._logger.log(
            level,
            f"Remediation {status}: {error_code} -> {remediation_type}",
            extra={"structured": extra}
        )
    
    def log_status_change(
        self,
        error_code: str,
        from_status: str,
        to_status: str,
        actor: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Log an error status change."""
        extra = {
            "event_type": "status_change",
            "error_code": error_code,
            "from_status": from_status,
            "to_status": to_status,
            "actor": actor,
            "reason": reason
        }
        extra.update(self._context)
        
        self._logger.info(
            f"Status change: {error_code} {from_status} -> {to_status}",
            extra={"structured": extra}
        )
    
    def log_fail_fast(
        self,
        error_code: str,
        reason: str,
        phase: str,
        row: Optional[int] = None
    ) -> None:
        """Log a fail-fast event."""
        extra = {
            "event_type": "fail_fast",
            "error_code": error_code,
            "fail_reason": reason,
            "phase": phase,
            "row": row,
            "processing_stopped": True
        }
        extra.update(self._context)
        
        self._logger.critical(
            f"FAIL FAST triggered: {error_code} - {reason}",
            extra={"structured": extra}
        )
    
    def log_suppression(
        self,
        error_code: str,
        rule_id: Optional[str],
        justification: str,
        approved_by: Optional[str] = None
    ) -> None:
        """Log an error suppression."""
        extra = {
            "event_type": "suppression",
            "error_code": error_code,
            "rule_id": rule_id,
            "justification": justification,
            "approved_by": approved_by,
            "requires_audit": True
        }
        extra.update(self._context)
        
        self._logger.warning(
            f"Error suppressed: {error_code} - {justification[:50]}...",
            extra={"structured": extra}
        )
    
    def log_health_score(
        self,
        total_rows: int,
        critical_errors: int,
        high_errors: int,
        health_score: float,
        grade: str
    ) -> None:
        """Log data health KPI."""
        extra = {
            "event_type": "health_score",
            "total_rows": total_rows,
            "critical_errors": critical_errors,
            "high_errors": high_errors,
            "health_score": health_score,
            "health_grade": grade,
            "clean_run": health_score == 100.0
        }
        extra.update(self._context)
        
        self._logger.info(
            f"Data Health Score: {health_score:.1f}% ({grade})",
            extra={"structured": extra}
        )
    
    def debug(self, message: str, **context) -> None:
        """Log debug message with context."""
        extra = context
        extra.update(self._context)
        self._logger.debug(message, extra={"structured": extra})
    
    def info(self, message: str, **context) -> None:
        """Log info message with context."""
        extra = context
        extra.update(self._context)
        self._logger.info(message, extra={"structured": extra})
    
    def warning(self, message: str, **context) -> None:
        """Log warning message with context."""
        extra = context
        extra.update(self._context)
        self._logger.warning(message, extra={"structured": extra})
    
    def error(self, message: str, **context) -> None:
        """Log error message with context."""
        extra = context
        extra.update(self._context)
        self._logger.error(message, extra={"structured": extra})
    
    def critical(self, message: str, **context) -> None:
        """Log critical message with context."""
        extra = context
        extra.update(self._context)
        self._logger.critical(message, extra={"structured": extra})


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON structured logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # Add structured context if available
        if hasattr(record, "structured"):
            log_data["context"] = record.structured
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)
