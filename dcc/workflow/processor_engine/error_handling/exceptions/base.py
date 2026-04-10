"""
DCC Error Base Exception Module

Provides the base exception class for all DCC errors with:
- Error code integration (E-M-F-U format)
- Context preservation
- JSON serialization
- User-friendly message generation
"""

import json
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path


class DCCError(Exception):
    """
    Base exception for all DCC Column Data errors.
    
    Features:
    - Error code following E-M-F-U format
    - Structured context preservation
    - JSON serialization for logging
    - Multi-language message support
    - Stack trace capture
    
    Attributes:
        error_code: Error code string (e.g., "P-C-P-0101")
        message: Human-readable error message
        context: Structured context dict
        layer: Validation layer (L0-L5)
        severity: Error severity (CRITICAL, HIGH, MEDIUM, WARNING, INFO)
        remediation_type: Suggested remediation strategy
        row: Row index if applicable
        column: Column name if applicable
    """
    
    def __init__(
        self,
        error_code: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        layer: Optional[str] = None,
        severity: str = "ERROR",
        remediation_type: Optional[str] = None,
        row: Optional[int] = None,
        column: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize DCCError.
        
        Args:
            error_code: Error code in E-M-F-U format (e.g., "P-C-P-0101")
            message: Human-readable error message
            context: Additional structured context
            layer: Validation layer (L0, L1, L2, L2.5, L3, L4, L5)
            severity: Error severity level
            remediation_type: Suggested remediation strategy
            row: Row index (if row-specific)
            column: Column name (if column-specific)
            cause: Original exception that caused this error
        """
        super().__init__(message)
        
        self.error_code = error_code
        self.message = message
        self.context = context or {}
        self.layer = layer
        self.severity = severity
        self.remediation_type = remediation_type
        self.row = row
        self.column = column
        self.cause = cause
        
        # Capture stack trace
        self.stack_trace = traceback.format_exc() if traceback.format_exc() != "NoneType: None\n" else None
        
        # Add standard context fields
        if row is not None:
            self.context["row"] = row
        if column is not None:
            self.context["column"] = column
        if layer:
            self.context["layer"] = layer
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary representation.
        
        Returns:
            Dict with all error details
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "layer": self.layer,
            "severity": self.severity,
            "remediation_type": self.remediation_type,
            "context": self.context,
            "row": self.row,
            "column": self.column,
            "stack_trace": self.stack_trace,
            "cause": str(self.cause) if self.cause else None
        }
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Serialize error to JSON string.
        
        Args:
            indent: JSON indentation (None for compact)
        
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def get_user_message(self, locale: str = "en") -> str:
        """
        Get localized user-friendly message.
        
        Args:
            locale: Language code ("en", "zh", etc.)
        
        Returns:
            Localized message string
        """
        # Try to load from messages file
        try:
            base_dir = Path(__file__).parent.parent
            messages_path = base_dir / "config" / "messages" / f"{locale}.json"
            
            if messages_path.exists():
                with open(messages_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                # Look up message by error code
                error_messages = messages.get("errors", {})
                if self.error_code in error_messages:
                    return error_messages[self.error_code]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Fall back to default message
        return self.message
    
    def get_remediation_message(self, locale: str = "en") -> Optional[str]:
        """
        Get localized remediation instructions.
        
        Args:
            locale: Language code
        
        Returns:
            Remediation message or None
        """
        if not self.remediation_type:
            return None
        
        try:
            base_dir = Path(__file__).parent.parent
            messages_path = base_dir / "config" / "messages" / f"{locale}.json"
            
            if messages_path.exists():
                with open(messages_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                
                remediation_messages = messages.get("remediation_types", {})
                return remediation_messages.get(self.remediation_type)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return None
    
    def is_fail_fast(self) -> bool:
        """
        Check if this error should trigger fail-fast.
        
        Returns:
            True if error requires immediate stop
        """
        # Check context for fail_fast flag
        if self.context.get("fail_fast", False):
            return True
        
        # Check severity
        if self.severity in ["CRITICAL"]:
            return True
        
        # Check specific error codes that require fail-fast
        fail_fast_codes = [
            "S0-I-F-0801",  # Template version mismatch
            "S0-I-F-0802",  # Template signature invalid
            "S0-I-F-0803",  # Configuration incompatible
            "S0-I-F-0804",  # Required file missing
        ]
        
        return self.error_code in fail_fast_codes
    
    def __str__(self) -> str:
        """String representation of error."""
        parts = [f"[{self.error_code}] {self.message}"]
        
        if self.row is not None:
            parts.append(f"Row: {self.row}")
        if self.column:
            parts.append(f"Column: {self.column}")
        if self.layer:
            parts.append(f"Layer: {self.layer}")
        
        return " | ".join(parts)
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"DCCError({self.error_code!r}, {self.message!r}, layer={self.layer!r})"


class DCCValidationError(DCCError):
    """Validation-specific error."""
    
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(
            error_code=error_code,
            message=message,
            layer=kwargs.get("layer", "L2"),
            severity=kwargs.get("severity", "HIGH"),
            **kwargs
        )


class DCCBusinessLogicError(DCCError):
    """Business logic error (Layer 3)."""
    
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(
            error_code=error_code,
            message=message,
            layer=kwargs.get("layer", "L3"),
            severity=kwargs.get("severity", "HIGH"),
            **kwargs
        )


class DCCInputError(DCCError):
    """Input validation error (Layer 1)."""
    
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(
            error_code=error_code,
            message=message,
            layer=kwargs.get("layer", "L1"),
            severity=kwargs.get("severity", "CRITICAL"),
            **kwargs
        )


class DCCSchemaError(DCCError):
    """Schema/template error (Layer 0)."""
    
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(
            error_code=error_code,
            message=message,
            layer=kwargs.get("layer", "L0"),
            severity=kwargs.get("severity", "CRITICAL"),
            **kwargs
        )


class DCCRemediationError(DCCError):
    """Remediation failure error."""
    
    def __init__(self, error_code: str, message: str, remediation_attempted: str, **kwargs):
        super().__init__(
            error_code=error_code,
            message=message,
            layer=kwargs.get("layer", "L4"),
            severity=kwargs.get("severity", "HIGH"),
            **kwargs
        )
        self.remediation_attempted = remediation_attempted
