"""
Error Handling Exceptions Module - Phase 2 Implementation

Provides exception classes for DCC error handling.
"""

from .base import (
    DCCError,
    DCCValidationError,
    DCCBusinessLogicError,
    DCCInputError,
    DCCSchemaError,
    DCCRemediationError,
)

from .handler import (
    ExceptionHandler,
    get_handler,
    handle_exceptions,
    register_error_callback,
    enable_fail_fast,
)

__all__ = [
    # Base exceptions
    "DCCError",
    "DCCValidationError",
    "DCCBusinessLogicError",
    "DCCInputError",
    "DCCSchemaError",
    "DCCRemediationError",
    # Handler
    "ExceptionHandler",
    "get_handler",
    "handle_exceptions",
    "register_error_callback",
    "enable_fail_fast",
]
