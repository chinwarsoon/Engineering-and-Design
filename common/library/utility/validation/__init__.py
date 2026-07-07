"""
common.library.utility.validation — ValidationManager and supporting models.

Exports
-------
ValidationManager   L13  Unified file/dir/parameter validation with batch support
ValidationItem      L13  Individual validation result
ValidationResult    L13  Aggregate validation result
ValidationStatus    L13  Enum: PASS | FAIL | WARNING

Sources
-------
dcc: utility_engine/validation/validation_manager.py  (mature reference impl)
     utility_engine/validation/validation_models.py
     utility_engine/validation/validation_functions.py
eks: engine/core/setup_validator.py + engine/core/validator.py  (split — consolidates here)
"""

from common.library.utility.validation.models import ValidationStatus, ValidationItem, ValidationResult
from common.library.utility.validation.manager import ValidationManager

__all__ = ["ValidationStatus", "ValidationItem", "ValidationResult", "ValidationManager"]
