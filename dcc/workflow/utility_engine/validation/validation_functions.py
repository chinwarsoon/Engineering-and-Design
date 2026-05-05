"""
Standalone validation functions.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union, Callable

from utility_engine.validation.validation_models import (
    ValidationStatus,
    ValidationItem,
    ValidationResult,
)


def validate_file_exists(
    file_path: Path,
    name: Optional[str] = None,
    required: bool = True,
    create_parent: bool = False
) -> ValidationItem:
    """
    Validate that a file exists.

    Args:
        file_path: Path to validate
        name: Descriptive name for the file
        required: Whether file must exist
        create_parent: Whether to create parent directory if missing

    Returns:
        ValidationItem with result
    """
    name = name or str(file_path)

    if create_parent and not file_path.parent.exists():
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return ValidationItem(
                name=name,
                path=file_path,
                status=ValidationStatus.FAIL,
                message=f"Cannot create parent directory: {e}",
                details=str(e),
                exists=False
            )

    exists = file_path.exists()
    status = ValidationStatus.PASS if exists else (ValidationStatus.WARNING if not required else ValidationStatus.FAIL)

    if exists:
        message = f"File exists: {file_path}"
    elif required:
        message = f"Required file not found: {file_path}"
    else:
        message = f"Optional file not found: {file_path}"

    return ValidationItem(
        name=name,
        path=file_path,
        status=status,
        message=message,
        exists=exists
    )


def validate_directory_exists(
    dir_path: Path,
    name: Optional[str] = None,
    required: bool = True,
    create_if_missing: bool = False,
    folder_creation_config: Optional[Dict[str, Any]] = None
) -> ValidationItem:
    """
    Validate that a directory exists.

    Args:
        dir_path: Directory path to validate
        name: Descriptive name for the directory
        required: Whether directory must exist
        create_if_missing: Whether to create directory if missing (deprecated, use folder_creation_config)
        folder_creation_config: Folder creation configuration from project_config

    Returns:
        ValidationItem with result
    """
    name = name or str(dir_path)

    # Determine creation behavior from project_config if available
    should_create = create_if_missing  # Fallback to parameter for backward compatibility
    if folder_creation_config:
        should_create = folder_creation_config.get("create_missing_parents", create_if_missing)

    if should_create and not dir_path.exists():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return ValidationItem(
                name=name,
                path=dir_path,
                status=ValidationStatus.FAIL,
                message=f"Cannot create directory: {e}",
                details=str(e),
                exists=False
            )

    exists = dir_path.exists()
    status = ValidationStatus.PASS if exists else (ValidationStatus.WARNING if not required else ValidationStatus.FAIL)

    if exists:
        message = f"Directory exists: {dir_path}"
    elif required:
        message = f"Required directory not found: {dir_path}"
    else:
        message = f"Optional directory not found: {dir_path}"

    return ValidationItem(
        name=name,
        path=dir_path,
        status=status,
        message=message,
        exists=exists
    )


def validate_parameter(
    param_name: str,
    param_value: Any,
    required: bool = True,
    allow_empty: bool = False,
    validator_func: Optional[Callable] = None
) -> ValidationItem:
    """
    Validate a parameter value.

    Args:
        param_name: Name of the parameter
        param_value: Value to validate
        required: Whether parameter is required
        allow_empty: Whether empty values are allowed
        validator_func: Optional custom validation function

    Returns:
        ValidationItem with result
    """
    # Check if parameter exists
    if param_value is None:
        status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
        message = f"Required parameter missing: {param_name}" if required else f"Optional parameter missing: {param_name}"
        return ValidationItem(
            name=param_name,
            path=Path(""),
            status=status,
            message=message,
            exists=False
        )

    # Check if parameter is empty
    if not allow_empty and (isinstance(param_value, str) and not param_value.strip()):
        status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
        message = f"Required parameter empty: {param_name}" if required else f"Optional parameter empty: {param_name}"
        return ValidationItem(
            name=param_name,
            path=Path(""),
            status=status,
            message=message,
            exists=True
        )

    # Custom validation
    if validator_func:
        try:
            custom_result = validator_func(param_value)
            if isinstance(custom_result, bool):
                status = ValidationStatus.PASS if custom_result else ValidationStatus.FAIL
                message = f"Parameter {param_name} {'passed' if custom_result else 'failed'} custom validation"
            elif isinstance(custom_result, tuple):
                passed, msg = custom_result
                status = ValidationStatus.PASS if passed else ValidationStatus.FAIL
                message = f"Parameter {param_name}: {msg}"
            else:
                status = ValidationStatus.FAIL
                message = f"Invalid custom validation result for {param_name}"
        except Exception as e:
            status = ValidationStatus.FAIL
            message = f"Custom validation error for {param_name}: {e}"

        return ValidationItem(
            name=param_name,
            path=Path(""),
            status=status,
            message=message,
            exists=True,
            details=str(param_value)
        )

    # Default success
    return ValidationItem(
        name=param_name,
        path=Path(""),
        status=ValidationStatus.PASS,
        message=f"Parameter valid: {param_name}",
        exists=True,
        details=str(param_value)
    )


def validate_paths_and_parameters(
    files: List[Tuple[Path, str, bool, bool]] = None,
    directories: List[Tuple[Path, str, bool, bool]] = None,
    parameters: List[Tuple[str, Any, bool, bool, Optional[Callable]]] = None,
    folder_creation_config: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """
    Validate multiple files, directories, and parameters.

    Args:
        files: List of tuples (path, name, required, create_parent)
        directories: List of tuples (path, name, required, create_if_missing)
        parameters: List of tuples (name, value, required, allow_empty, validator_func)

    Returns:
        ValidationResult with comprehensive results
    """
    items = []
    errors = []
    warnings = []

    # Validate files
    if files:
        for file_path, name, required, create_parent in files:
            item = validate_file_exists(file_path, name, required, create_parent)
            items.append(item)

            if item.status == ValidationStatus.FAIL:
                errors.append(item.message)
            elif item.status == ValidationStatus.WARNING:
                warnings.append(item.message)

    # Validate directories
    if directories:
        for dir_path, name, required, create_if_missing in directories:
            item = validate_directory_exists(dir_path, name, required, create_if_missing, folder_creation_config)
            items.append(item)

            if item.status == ValidationStatus.FAIL:
                errors.append(item.message)
            elif item.status == ValidationStatus.WARNING:
                warnings.append(item.message)

    # Validate parameters
    if parameters:
        for param_name, param_value, required, allow_empty, validator_func in parameters:
            item = validate_parameter(param_name, param_value, required, allow_empty, validator_func)
            items.append(item)

            if item.status == ValidationStatus.FAIL:
                errors.append(item.message)
            elif item.status == ValidationStatus.WARNING:
                warnings.append(item.message)

    # Determine overall status
    if errors:
        status = ValidationStatus.FAIL
    elif warnings:
        status = ValidationStatus.WARNING
    else:
        status = ValidationStatus.PASS

    # Create summary
    summary = {
        "total_items": len(items),
        "passed": len([i for i in items if i.status == ValidationStatus.PASS]),
        "failed": len([i for i in items if i.status == ValidationStatus.FAIL]),
        "warnings": len([i for i in items if i.status == ValidationStatus.WARNING]),
        "files_validated": len(files) if files else 0,
        "directories_validated": len(directories) if directories else 0,
        "parameters_validated": len(parameters) if parameters else 0
    }

    return ValidationResult(
        status=status,
        items=items,
        summary=summary,
        errors=errors,
        warnings=warnings
    )
