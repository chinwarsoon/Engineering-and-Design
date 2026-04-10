"""
Error Handling Detectors Module - Phase 2 Implementation

Provides detector classes for multi-layer validation.
"""

from .base import (
    BaseDetector,
    CompositeDetector,
    DetectionResult,
    FailFastError,
)

from .input import InputDetector
from .schema import SchemaDetector

__all__ = [
    # Base classes
    "BaseDetector",
    "CompositeDetector",
    "DetectionResult",
    "FailFastError",
    # Layer detectors
    "InputDetector",
    "SchemaDetector",
]
