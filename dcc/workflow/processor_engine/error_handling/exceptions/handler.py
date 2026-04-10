"""
Global Exception Handler Module

Provides top-level exception handling for DCC processing:
- Catches unhandled exceptions
- Maps exceptions to error codes
- Logs with full context
- Re-raises with enriched information
- Fail-fast support
"""

import sys
import json
import traceback
from typing import Optional, Callable, Dict, Any, List
from functools import wraps

from .base import DCCError, DCCSchemaError, DCCInputError, DCCValidationError


class ExceptionHandler:
    """
    Global exception handler for DCC processing.
    
    Responsibilities:
    - Map Python exceptions to DCC error codes
    - Enrich exceptions with context
    - Log errors via structured logger
    - Support fail-fast behavior
    - Track error statistics
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize exception handler."""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self._error_count = 0
        self._errors: List[Dict[str, Any]] = []
        self._on_error_callbacks: List[Callable] = []
        self._fail_fast_enabled = True
        self._logger = None
    
    def set_logger(self, logger):
        """Set structured logger instance."""
        self._logger = logger
    
    def enable_fail_fast(self, enabled: bool = True) -> None:
        """Enable or disable fail-fast behavior."""
        self._fail_fast_enabled = enabled
    
    def register_error_callback(self, callback: Callable) -> None:
        """Register callback to be called on each error."""
        self._on_error_callbacks.append(callback)
    
    def map_exception_to_error_code(self, exc: Exception) -> str:
        """
        Map Python exception to DCC error code.
        
        Args:
            exc: Python exception
        
        Returns:
            DCC error code string
        """
        exception_map = {
            FileNotFoundError: "S0-I-F-0804",
            PermissionError: "S0-I-F-0804",
            ValueError: "P-C-P-0301",
            TypeError: "P-C-P-0301",
            KeyError: "P-C-P-0102",
            IndexError: "P-C-P-0301",
            json.JSONDecodeError: "S0-I-F-0803",
            UnicodeDecodeError: "S0-I-V-0501",
        }
        
        for exc_type, error_code in exception_map.items():
            if isinstance(exc, exc_type):
                return error_code
        
        # Default for unknown exceptions
        return "P-C-P-0301"
    
    def get_error_message(self, exc: Exception) -> str:
        """Get user-friendly error message from exception."""
        if isinstance(exc, DCCError):
            return exc.message
        
        # Map common exceptions to messages
        message_map = {
            FileNotFoundError: f"File not found: {exc}",
            PermissionError: f"Permission denied: {exc}",
            ValueError: f"Invalid value: {exc}",
            TypeError: f"Type mismatch: {exc}",
            KeyError: f"Missing required field: {exc}",
            IndexError: f"Index out of range: {exc}",
        }
        
        return message_map.get(type(exc), f"Unexpected error: {exc}")
    
    def handle_exception(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None,
        row: Optional[int] = None,
        column: Optional[str] = None,
        phase: Optional[str] = None,
        layer: Optional[str] = None
    ) -> DCCError:
        """
        Handle an exception and convert to DCCError.
        
        Args:
            exc: Original exception
            context: Additional context
            row: Row index
            column: Column name
            phase: Processing phase
            layer: Validation layer
        
        Returns:
            Enriched DCCError
        """
        # If already DCCError, just enrich it
        if isinstance(exc, DCCError):
            dcc_error = exc
            if context:
                dcc_error.context.update(context)
        else:
            # Map to DCCError
            error_code = self.map_exception_to_error_code(exc)
            message = self.get_error_message(exc)
            
            # Determine layer based on error code
            if error_code.startswith("S0"):
                layer = layer or "L0"
                dcc_error = DCCSchemaError(
                    error_code=error_code,
                    message=message,
                    context=context,
                    row=row,
                    column=column,
                    cause=exc
                )
            elif error_code.startswith("S1"):
                layer = layer or "L1"
                dcc_error = DCCInputError(
                    error_code=error_code,
                    message=message,
                    context=context,
                    row=row,
                    column=column,
                    cause=exc
                )
            else:
                layer = layer or "L3"
                dcc_error = DCCValidationError(
                    error_code=error_code,
                    message=message,
                    context=context,
                    row=row,
                    column=column,
                    cause=exc
                )
        
        # Add phase/layer to context
        if phase:
            dcc_error.context["phase"] = phase
        if layer:
            dcc_error.context["layer"] = layer
        
        # Track error
        self._error_count += 1
        error_record = {
            "error_code": dcc_error.error_code,
            "message": dcc_error.message,
            "row": row,
            "column": column,
            "phase": phase,
            "layer": layer or dcc_error.layer,
            "severity": dcc_error.severity
        }
        self._errors.append(error_record)
        
        # Log if logger available
        if self._logger:
            self._logger.log_error(
                error_code=dcc_error.error_code,
                message=dcc_error.message,
                row=row,
                column=column,
                phase=phase,
                layer=layer or dcc_error.layer,
                severity=dcc_error.severity,
                context=dcc_error.context,
                exception=exc
            )
        
        # Call registered callbacks
        for callback in self._on_error_callbacks:
            try:
                callback(dcc_error)
            except Exception:
                pass  # Don't let callbacks break handling
        
        return dcc_error
    
    def handle(self, context: Optional[Dict[str, Any]] = None):
        """
        Decorator to wrap functions with exception handling.
        
        Args:
            context: Default context for all errors in this scope
        
        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except DCCError:
                    # Re-raise DCC errors as-is
                    raise
                except Exception as exc:
                    # Convert to DCCError
                    merged_context = {**(context or {})}
                    
                    # Extract context from kwargs if present
                    if 'context' in kwargs:
                        merged_context.update(kwargs['context'])
                    
                    dcc_error = self.handle_exception(
                        exc,
                        context=merged_context
                    )
                    
                    # Check fail-fast
                    if self._fail_fast_enabled and dcc_error.is_fail_fast():
                        if self._logger:
                            self._logger.log_fail_fast(
                                error_code=dcc_error.error_code,
                                reason=dcc_error.message,
                                phase=merged_context.get("phase"),
                                row=merged_context.get("row")
                            )
                        raise dcc_error  # Re-raise to stop processing
                    
                    raise dcc_error
            
            return wrapper
        return decorator
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        by_code = {}
        by_layer = {}
        
        for error in self._errors:
            code = error["error_code"]
            layer = error.get("layer", "UNKNOWN")
            
            by_code[code] = by_code.get(code, 0) + 1
            by_layer[layer] = by_layer.get(layer, 0) + 1
        
        return {
            "total_errors": self._error_count,
            "by_code": by_code,
            "by_layer": by_layer,
            "fail_fast_enabled": self._fail_fast_enabled
        }
    
    def clear_errors(self) -> None:
        """Clear error history."""
        self._error_count = 0
        self._errors.clear()


# Global singleton
_handler = ExceptionHandler()


def get_handler() -> ExceptionHandler:
    """Get global exception handler instance."""
    return _handler


def handle_exceptions(context: Optional[Dict[str, Any]] = None):
    """Convenience decorator for exception handling."""
    return _handler.handle(context)


def register_error_callback(callback: Callable) -> None:
    """Register global error callback."""
    _handler.register_error_callback(callback)


def enable_fail_fast(enabled: bool = True) -> None:
    """Enable/disable global fail-fast."""
    _handler.enable_fail_fast(enabled)
