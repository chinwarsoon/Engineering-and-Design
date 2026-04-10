"""
Base Detector Module

Provides base class for all error detectors with:
- Structured logging integration
- Fail-fast capability
- Context collection
- Error aggregation
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DetectionResult:
    """Result of error detection."""
    error_code: str
    message: str
    row: Optional[int] = None
    column: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "ERROR"
    layer: Optional[str] = None
    fail_fast: bool = False
    remediation_type: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "row": self.row,
            "column": self.column,
            "context": self.context,
            "severity": self.severity,
            "layer": self.layer,
            "fail_fast": self.fail_fast,
            "remediation_type": self.remediation_type,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }


class BaseDetector(ABC):
    """
    Abstract base class for all error detectors.
    
    Features:
    - Structured logging via injected logger
    - Context collection
    - Error aggregation
    - Fail-fast support
    - Result tracking
    """
    
    def __init__(
        self,
        layer: str,
        logger=None,
        enable_fail_fast: bool = True
    ):
        """
        Initialize base detector.
        
        Args:
            layer: Validation layer (L1, L2, L3, etc.)
            logger: StructuredLogger instance (optional)
            enable_fail_fast: Whether to enable fail-fast behavior
        """
        self.layer = layer
        self._logger = logger
        self._enable_fail_fast = enable_fail_fast
        self._errors: List[DetectionResult] = []
        self._context: Dict[str, Any] = {}
        self._on_error_callbacks: List[Callable] = []
    
    def set_context(self, **kwargs) -> None:
        """Set detection context."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear detection context."""
        self._context = {}
    
    def set_logger(self, logger) -> None:
        """Set logger instance."""
        self._logger = logger
    
    def register_error_callback(self, callback: Callable) -> None:
        """Register callback for each detected error."""
        self._on_error_callbacks.append(callback)
    
    def detect_error(
        self,
        error_code: str,
        message: str,
        row: Optional[int] = None,
        column: Optional[str] = None,
        severity: str = "ERROR",
        fail_fast: bool = False,
        remediation_type: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> DetectionResult:
        """
        Record a detected error.
        
        Args:
            error_code: Error code (E-M-F-U format)
            message: Error message
            row: Row index (optional)
            column: Column name (optional)
            severity: Error severity
            fail_fast: Whether this error triggers fail-fast
            remediation_type: Suggested remediation
            additional_context: Additional context dict
        
        Returns:
            DetectionResult object
        """
        # Merge contexts
        merged_context = self._context.copy()
        if additional_context:
            merged_context.update(additional_context)
        
        result = DetectionResult(
            error_code=error_code,
            message=message,
            row=row,
            column=column,
            context=merged_context,
            severity=severity,
            layer=self.layer,
            fail_fast=fail_fast,
            remediation_type=remediation_type
        )
        
        # Store error
        self._errors.append(result)
        
        # Log if logger available
        if self._logger:
            self._logger.log_error(
                error_code=error_code,
                message=message,
                row=row,
                column=column,
                layer=self.layer,
                severity=severity,
                context=merged_context,
                remediation_type=remediation_type
            )
        
        # Call callbacks
        for callback in self._on_error_callbacks:
            try:
                callback(result)
            except Exception:
                pass
        
        # Check fail-fast
        if self._enable_fail_fast and fail_fast:
            if self._logger:
                self._logger.log_fail_fast(
                    error_code=error_code,
                    reason=message,
                    phase=merged_context.get("phase"),
                    row=row
                )
            raise FailFastError(result)
        
        return result
    
    def get_errors(self) -> List[DetectionResult]:
        """Get all detected errors."""
        return self._errors.copy()
    
    def get_errors_by_severity(self, severity: str) -> List[DetectionResult]:
        """Get errors filtered by severity."""
        return [e for e in self._errors if e.severity == severity]
    
    def get_fail_fast_errors(self) -> List[DetectionResult]:
        """Get all fail-fast errors."""
        return [e for e in self._errors if e.fail_fast]
    
    def has_fail_fast_errors(self) -> bool:
        """Check if any fail-fast errors occurred."""
        return any(e.fail_fast for e in self._errors)
    
    def get_error_count(self) -> int:
        """Get total error count."""
        return len(self._errors)
    
    def get_error_count_by_code(self) -> Dict[str, int]:
        """Get error count grouped by error code."""
        counts = {}
        for error in self._errors:
            code = error.error_code
            counts[code] = counts.get(code, 0) + 1
        return counts
    
    def clear_errors(self) -> None:
        """Clear all detected errors."""
        self._errors.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics."""
        severities = {}
        codes = {}
        
        for error in self._errors:
            severities[error.severity] = severities.get(error.severity, 0) + 1
            codes[error.error_code] = codes.get(error.error_code, 0) + 1
        
        return {
            "layer": self.layer,
            "total_errors": len(self._errors),
            "fail_fast_errors": len(self.get_fail_fast_errors()),
            "by_severity": severities,
            "by_code": codes
        }
    
    @abstractmethod
    def detect(self, data: Any, context: Optional[Dict[str, Any]] = None) -> List[DetectionResult]:
        """
        Abstract method for detection logic.
        
        Args:
            data: Data to analyze (DataFrame, dict, etc.)
            context: Additional context
        
        Returns:
            List of DetectionResult objects
        """
        pass


class FailFastError(Exception):
    """Exception raised when a fail-fast error is detected."""
    
    def __init__(self, detection_result: DetectionResult):
        self.result = detection_result
        super().__init__(
            f"FAIL FAST triggered: [{detection_result.error_code}] {detection_result.message}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error": self.result.to_dict(),
            "message": str(self)
        }


class CompositeDetector(BaseDetector):
    """Detector that combines multiple sub-detectors."""
    
    def __init__(
        self,
        layer: str,
        detectors: Optional[List[BaseDetector]] = None,
        logger=None,
        enable_fail_fast: bool = True
    ):
        super().__init__(layer, logger, enable_fail_fast)
        self._detectors = detectors or []
    
    def add_detector(self, detector: BaseDetector) -> None:
        """Add a sub-detector."""
        self._detectors.append(detector)
    
    def detect(self, data: Any, context: Optional[Dict[str, Any]] = None) -> List[DetectionResult]:
        """
        Run all sub-detectors and aggregate results.
        
        Args:
            data: Data to analyze
            context: Additional context
        
        Returns:
            Combined list of all detection results
        """
        all_results = []
        
        for detector in self._detectors:
            try:
                results = detector.detect(data, context)
                all_results.extend(results)
                
                # Check for fail-fast
                if self._enable_fail_fast:
                    for result in results:
                        if result.fail_fast:
                            raise FailFastError(result)
                
            except FailFastError:
                raise
            except Exception as e:
                # Log detector failure but continue
                if self._logger:
                    self._logger.error(
                        message=f"Detector {type(detector).__name__} failed: {e}",
                        detector_type=type(detector).__name__,
                        exception=str(e)
                    )
        
        return all_results
