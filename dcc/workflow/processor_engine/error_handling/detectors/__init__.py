"""
Error Handling Detectors Module - Phase 2 & 3 Implementation

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

# Phase 3: Business Logic Detectors
from .anchor import AnchorDetector
from .identity import IdentityDetector
from .business import BusinessDetector, ProcessingPhase, create_business_detector
from .logic import LogicDetector
from .fill import FillDetector
from .validation import ValidationDetector, ValidationRule
from .calculation import CalculationDetector

__all__ = [
    # Base classes
    "BaseDetector",
    "CompositeDetector",
    "DetectionResult",
    "FailFastError",
    # Layer 1-2 detectors (Phase 2)
    "InputDetector",
    "SchemaDetector",
    # Phase 3: Business Logic Detectors
    "AnchorDetector",
    "IdentityDetector",
    "BusinessDetector",
    "ProcessingPhase",
    "create_business_detector",
    "LogicDetector",
    "FillDetector",
    "ValidationDetector",
    "ValidationRule",
    "CalculationDetector",
]
