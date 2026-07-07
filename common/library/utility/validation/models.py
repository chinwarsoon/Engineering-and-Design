"""
L13 — Validation data models.

Source: dcc/workflow/utility_engine/validation/validation_models.py
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ValidationStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class ValidationItem:
    """Individual validation result for a single file, directory, or parameter."""
    name: str
    path: Path
    status: ValidationStatus
    message: str
    details: Optional[str] = None
    exists: Optional[bool] = None


@dataclass
class ValidationResult:
    """Aggregate result of a batch validation run."""
    status: ValidationStatus
    items: List[ValidationItem]
    summary: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

    @property
    def passed(self) -> bool:
        return self.status == ValidationStatus.PASS

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
