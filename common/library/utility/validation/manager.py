"""
L13 — ValidationManager

Unified validation manager for files, directories, and parameters.
Reference implementation from dcc/workflow/utility_engine/validation/validation_manager.py,
consolidated so EKS can replace its split setup_validator.py + validator.py.

Source: dcc/workflow/utility_engine/validation/validation_manager.py
        dcc/workflow/utility_engine/validation/validation_functions.py
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from common.library.utility.validation.models import (
    ValidationItem,
    ValidationResult,
    ValidationStatus,
)


class ValidationManager:
    """
    Centralized validation manager for all pipeline projects.

    Provides
    --------
    validate_file_exists()          — single file
    validate_directory_exists()     — single directory (with optional auto-create)
    validate_parameter()            — single parameter with optional custom validator
    validate_paths_and_parameters() — batch: files + dirs + params in one call
    validate_pipeline_prerequisites() — full pipeline pre-flight check
    """

    def __init__(self, folder_creation_config: Optional[Dict[str, Any]] = None):
        self.folder_creation_config = folder_creation_config or {}

    # ------------------------------------------------------------------
    # Single-item validators
    # ------------------------------------------------------------------

    def validate_file_exists(
        self,
        file_path: Path,
        name: Optional[str] = None,
        required: bool = True,
    ) -> ValidationItem:
        name = name or str(file_path)
        exists = file_path.exists()
        if exists:
            status, message = ValidationStatus.PASS, f"File exists: {file_path}"
        elif required:
            status, message = ValidationStatus.FAIL, f"Required file not found: {file_path}"
        else:
            status, message = ValidationStatus.WARNING, f"Optional file not found: {file_path}"
        return ValidationItem(name=name, path=file_path, status=status, message=message, exists=exists)

    def validate_directory_exists(
        self,
        dir_path: Path,
        name: Optional[str] = None,
        required: bool = True,
        create_if_missing: bool = False,
    ) -> ValidationItem:
        name = name or str(dir_path)
        should_create = create_if_missing or self.folder_creation_config.get("create_missing_parents", False)

        if should_create and not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                return ValidationItem(
                    name=name, path=dir_path,
                    status=ValidationStatus.FAIL,
                    message=f"Cannot create directory: {exc}",
                    details=str(exc), exists=False,
                )

        exists = dir_path.exists()
        if exists:
            status, message = ValidationStatus.PASS, f"Directory exists: {dir_path}"
        elif required:
            status, message = ValidationStatus.FAIL, f"Required directory not found: {dir_path}"
        else:
            status, message = ValidationStatus.WARNING, f"Optional directory not found: {dir_path}"
        return ValidationItem(name=name, path=dir_path, status=status, message=message, exists=exists)

    def validate_parameter(
        self,
        param_name: str,
        param_value: Any,
        required: bool = True,
        allow_empty: bool = False,
        validator_func: Optional[Callable] = None,
    ) -> ValidationItem:
        empty_path = Path("")

        if param_value is None:
            status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
            msg = f"{'Required' if required else 'Optional'} parameter missing: {param_name}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg, exists=False)

        if not allow_empty and isinstance(param_value, str) and not param_value.strip():
            status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
            msg = f"{'Required' if required else 'Optional'} parameter empty: {param_name}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg, exists=True)

        if validator_func:
            try:
                result = validator_func(param_value)
                if isinstance(result, bool):
                    status = ValidationStatus.PASS if result else ValidationStatus.FAIL
                    msg = f"Parameter {param_name} {'passed' if result else 'failed'} validation"
                elif isinstance(result, tuple):
                    passed, msg = result
                    status = ValidationStatus.PASS if passed else ValidationStatus.FAIL
                    msg = f"Parameter {param_name}: {msg}"
                else:
                    status, msg = ValidationStatus.FAIL, f"Invalid validator result for {param_name}"
            except Exception as exc:
                status, msg = ValidationStatus.FAIL, f"Validator error for {param_name}: {exc}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg,
                                  exists=True, details=str(param_value))

        return ValidationItem(name=param_name, path=empty_path, status=ValidationStatus.PASS,
                              message=f"Parameter valid: {param_name}", exists=True,
                              details=str(param_value))

    # ------------------------------------------------------------------
    # Batch validator
    # ------------------------------------------------------------------

    def validate_paths_and_parameters(
        self,
        files: Optional[List[Tuple[Path, str, bool, bool]]] = None,
        directories: Optional[List[Tuple[Path, str, bool, bool]]] = None,
        parameters: Optional[List[Tuple[str, Any, bool, bool, Optional[Callable]]]] = None,
    ) -> ValidationResult:
        """
        Validate multiple files, directories, and parameters in one call.

        Tuple formats
        -------------
        files       : (path, name, required, create_parent)
        directories : (path, name, required, create_if_missing)
        parameters  : (name, value, required, allow_empty, validator_func)
        """
        items, errors, warnings = [], [], []

        for file_path, name, required, _ in (files or []):
            item = self.validate_file_exists(file_path, name, required)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        for dir_path, name, required, create in (directories or []):
            item = self.validate_directory_exists(dir_path, name, required, create)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        for param_name, param_value, required, allow_empty, validator_func in (parameters or []):
            item = self.validate_parameter(param_name, param_value, required, allow_empty, validator_func)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        if errors:
            status = ValidationStatus.FAIL
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASS

        summary = {
            "total_items": len(items),
            "passed": sum(1 for i in items if i.status == ValidationStatus.PASS),
            "failed": sum(1 for i in items if i.status == ValidationStatus.FAIL),
            "warnings": sum(1 for i in items if i.status == ValidationStatus.WARNING),
            "files_validated": len(files or []),
            "directories_validated": len(directories or []),
            "parameters_validated": len(parameters or []),
        }
        return ValidationResult(status=status, items=items, summary=summary,
                                errors=errors, warnings=warnings)

    # ------------------------------------------------------------------
    # Pipeline pre-flight
    # ------------------------------------------------------------------

    def validate_pipeline_prerequisites(
        self,
        base_path: Path,
        schema_path: Path,
        input_file_path: Path,
        export_paths: Dict[str, Path],
        effective_parameters: Dict[str, Any],
        project_config: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Full pipeline pre-flight: files, output dirs, and key parameters."""
        fc = {}
        if project_config and "folder_creation" in project_config:
            fc = project_config["folder_creation"]
            self.folder_creation_config = fc
        else:
            fc = {"auto_create_output_directories": True, "create_missing_parents": True}
            self.folder_creation_config = fc

        auto_create = fc.get("auto_create_output_directories", True) and fc.get("create_missing_parents", True)

        files = [
            (schema_path, "Schema File", True, False),
            (input_file_path, "Input File", True, False),
        ]
        directories = [
            (base_path, "Base Directory", True, False),
            (export_paths["csv_path"].parent, "CSV Output Directory", True, auto_create),
            (export_paths["excel_path"].parent, "Excel Output Directory", True, auto_create),
            (export_paths["summary_path"].parent, "Summary Output Directory", True, auto_create),
        ]
        parameters = [
            ("effective_parameters", effective_parameters, True, False,
             lambda x: isinstance(x, dict) and len(x) > 0),
            ("upload_file_name", effective_parameters.get("upload_file_name"), True, False, None),
            ("nrows", effective_parameters.get("nrows"), False, True,
             lambda x: x is None or (isinstance(x, int) and x >= 0)),
        ]
        return self.validate_paths_and_parameters(files=files, directories=directories, parameters=parameters)
