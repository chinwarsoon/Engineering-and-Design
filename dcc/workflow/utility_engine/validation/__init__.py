"""
Universal Validation Utilities - Class-Based Design Approach

Provides a ValidationManager class that encapsulates all validation functionality
for files, folders, and parameters that can be used across all pipeline components.

Phase 2 Enhancement: Type-driven parameter validation with ParameterTypeRegistry
and ParameterValidator for schema-based, type-driven validation.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""

# Phase 2: Type-driven parameter validation imports (keep these as they are separate modules)
from utility_engine.validation.parameter_type_registry import (
    ParameterType,
    ParameterTypeRegistry,
    get_parameter_registry,
    load_default_registry,
    get_default_registry,
)
from utility_engine.validation.parameter_validator import (
    ParameterValidationResult,
    ParameterValidator,
)

# Phase 1: Core validation models
from utility_engine.validation.validation_models import (
    ValidationStatus,
    ValidationItem,
    ValidationResult,
)

# Phase 1: Validation manager class
from utility_engine.validation.validation_manager import (
    ValidationManager,
    default_validator,
)

# Phase 1: Standalone validation functions
from utility_engine.validation.validation_functions import (
    validate_file_exists,
    validate_directory_exists,
    validate_parameter,
    validate_paths_and_parameters,
)

__all__ = [
    # Phase 2: Type-driven validation
    "ParameterType",
    "ParameterTypeRegistry",
    "get_parameter_registry",
    "load_default_registry",
    "get_default_registry",
    "ParameterValidationResult",
    "ParameterValidator",
    # Phase 1: Core models
    "ValidationStatus",
    "ValidationItem",
    "ValidationResult",
    # Phase 1: Manager
    "ValidationManager",
    "default_validator",
    # Phase 1: Functions
    "validate_file_exists",
    "validate_directory_exists",
    "validate_parameter",
    "validate_paths_and_parameters",
]
