"""
Data models for validation system.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class ValidationItem:
    """Individual validation result."""
    name: str
    path: Path
    status: ValidationStatus
    message: str
    details: Optional[str] = None
    exists: Optional[bool] = None


@dataclass
class ValidationResult:
    """Comprehensive validation results."""
    status: ValidationStatus
    items: List[ValidationItem]
    summary: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASS

    @property
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0
