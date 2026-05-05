"""
ValidationManager class for centralized validation operations.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from utility_engine.validation.validation_models import (
    ValidationStatus,
    ValidationItem,
    ValidationResult,
)
from utility_engine.validation.validation_functions import (
    validate_file_exists,
    validate_directory_exists,
    validate_parameter,
    validate_paths_and_parameters,
)


class ValidationManager:
    """
    Centralized validation manager that provides a unified interface for all validation operations.

    This class encapsulates all validation functionality including:
    - File and directory validation
    - Parameter validation
    - Path resolution with system context
    - Home directory validation
    - Pipeline prerequisite validation
    """

    def __init__(self, folder_creation_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ValidationManager.

        Args:
            folder_creation_config: Optional folder creation configuration from project_config
        """
        self.folder_creation_config = folder_creation_config or {}

    # File and Directory Validation Methods
    def validate_file_exists(self, file_path: Path, name: Optional[str] = None, required: bool = True) -> ValidationItem:
        """Validate that a file exists."""
        return validate_file_exists(file_path, name, required)

    def validate_directory_exists(self, dir_path: Path, name: Optional[str] = None, required: bool = True, create_if_missing: bool = False) -> ValidationItem:
        """Validate that a directory exists with optional creation."""
        return validate_directory_exists(dir_path, name, required, create_if_missing, self.folder_creation_config)

    def validate_parameter(self, param_name: str, param_value: Any, required: bool = True, allow_empty: bool = False, validator_func: Optional[callable] = None) -> ValidationItem:
        """Validate a parameter value."""
        return validate_parameter(param_name, param_value, required, allow_empty, validator_func)

    # Path Validation with System Context
    def validate_path_with_system_context(self, path_input: Union[str, Path], path_type: str = "file", name: Optional[str] = None, required: bool = True, base_path: Optional[Path] = None, create_if_missing: bool = False) -> ValidationItem:
        """Centralized path validation that combines safe_resolve with validation."""
        name = name or str(path_input)

        try:
            # Import path resolution utilities
            from utility_engine.paths import resolve_with_system_context, get_system_context

            # Step 1: Resolve path with system context using resolve_with_system_context for detailed results
            resolution_result = resolve_with_system_context(path_input, base_path=base_path)

            # Step 2: Check for resolution errors
            if resolution_result.errors:
                return ValidationItem(
                    name=name,
                    path=resolution_result.resolved_path,
                    status=ValidationStatus.FAIL,
                    message=f"Path resolution failed: {'; '.join(resolution_result.errors)}",
                    exists=resolution_result.exists,
                    details=f"Resolution errors: {'; '.join(resolution_result.errors)}"
                )

            # Step 3: Validate based on path type
            if path_type == "directory":
                # Use existing directory validation with folder creation config
                item = self.validate_directory_exists(
                    resolution_result.resolved_path,
                    name,
                    required,
                    create_if_missing
                )
            elif path_type == "file":
                # Use existing file validation
                item = self.validate_file_exists(resolution_result.resolved_path, name, required)
            else:
                return ValidationItem(
                    name=name,
                    path=resolution_result.resolved_path,
                    status=ValidationStatus.FAIL,
                    message=f"Invalid path_type: {path_type}. Must be 'file' or 'directory'",
                    exists=resolution_result.exists,
                    details=f"Path type '{path_type}' is not supported"
                )

            # Step 4: Enhance with system context information
            system_context = get_system_context()
            import platform
            platform_info = platform.system()
            base_details = item.details or ""
            resolution_details = f"OS: {system_context}, Platform: {platform_info}, Resolved: {resolution_result.resolved_path}"
            item.details = f"{base_details} | {resolution_details}" if base_details else resolution_details

            return item

        except Exception as e:
            return ValidationItem(
                name=name,
                path=Path(path_input),
                status=ValidationStatus.FAIL,
                message=f"Path validation failed: {e}",
                exists=False,
                details=str(e)
            )

    # Home Directory Validation
    def validate_home_directory(self) -> ValidationItem:
        """Validate and resolve the home directory using centralized validation."""
        try:
            # Import get_homedir for home directory resolution
            from core_engine.paths import get_homedir
            from utility_engine.paths import get_system_context

            # Step 1: Resolve home directory
            local_home = get_homedir()

            # Step 2: Validate home directory
            if not local_home or not Path(local_home).exists():
                return ValidationItem(
                    name="Home Directory",
                    path=Path(local_home) if local_home else Path(""),
                    status=ValidationStatus.WARNING,
                    message="Home directory not accessible or not found",
                    exists=False,
                    details=f"Resolved path: {local_home or 'None'}"
                )

            # Step 3: Enhance with system context information
            import platform
            system_context = get_system_context()
            platform_info = platform.system()
            details = f"OS: {system_context}, Platform: {platform_info}, Home: {local_home}"

            return ValidationItem(
                name="Home Directory",
                path=Path(local_home),
                status=ValidationStatus.PASS,
                message=f"Home directory resolved: {local_home}",
                exists=True,
                details=details
            )

        except Exception as e:
            return ValidationItem(
                name="Home Directory",
                path=Path(""),
                status=ValidationStatus.FAIL,
                message=f"Home directory validation failed: {e}",
                exists=False,
                details=str(e)
            )

    # Batch Validation Methods
    def validate_paths_and_parameters(self, files: List[Tuple[Path, str, bool, bool]] = None, directories: List[Tuple[Path, str, bool, bool]] = None, parameters: List[Tuple[str, Any, bool, bool, Optional[callable]]] = None) -> ValidationResult:
        """Validate multiple files, directories, and parameters."""
        return validate_paths_and_parameters(files, directories, parameters, self.folder_creation_config)

    # Pipeline Validation Methods
    def validate_pipeline_prerequisites(self, base_path: Path, schema_path: Path, input_file_path: Path, export_paths: Dict[str, Path], effective_parameters: Dict[str, Any], project_config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate all pipeline prerequisites using universal validation functions."""
        # Load folder creation configuration from project_config
        folder_creation_config = {}
        if project_config and "folder_creation" in project_config:
            folder_creation_config = project_config["folder_creation"]
            self.folder_creation_config = folder_creation_config
        else:
            # Default fallback configuration
            folder_creation_config = {
                "auto_create_output_directories": True,
                "auto_create_debug_directories": True,
                "auto_create_log_directories": True,
                "create_missing_parents": True
            }
            self.folder_creation_config = folder_creation_config

        # Define files to validate
        files = [
            (schema_path, "Schema File", True, False),
            (input_file_path, "Input Excel File", True, False)
        ]

        # Determine directory creation based on project_config
        auto_create_output = folder_creation_config.get("auto_create_output_directories", True)
        auto_create_debug = folder_creation_config.get("auto_create_debug_directories", True)
        create_parents = folder_creation_config.get("create_missing_parents", True)

        # Define directories to validate with schema-controlled creation
        directories = [
            (base_path, "Base Directory", True, False),  # Base directory should exist, don't create
            (export_paths["csv_path"].parent, "CSV Output Directory", True, auto_create_output and create_parents),
            (export_paths["excel_path"].parent, "Excel Output Directory", True, auto_create_output and create_parents),
            (export_paths["summary_path"].parent, "Summary Output Directory", True, auto_create_output and create_parents),
            (export_paths["csv_path"].parent, "Debug Log Directory", True, auto_create_debug and create_parents)
        ]

        # Add required directories from project_config if specified
        if "required_directories" in folder_creation_config:
            for dir_config in folder_creation_config["required_directories"]:
                dir_path = base_path / dir_config["name"]
                auto_create = dir_config.get("auto_create", True) and create_parents
                directories.append((dir_path, f"Required Directory: {dir_config['name']}", True, auto_create))

        # Add optional directories from project_config if specified
        if "optional_directories" in folder_creation_config:
            for dir_config in folder_creation_config["optional_directories"]:
                dir_path = base_path / dir_config["name"]
                auto_create = dir_config.get("auto_create", False) and create_parents
                directories.append((dir_path, f"Optional Directory: {dir_config['name']}", False, auto_create))

        # Define parameters to validate
        parameters = [
            ("effective_parameters", effective_parameters, True, False, lambda x: isinstance(x, dict) and len(x) > 0),
            ("upload_file_name", effective_parameters.get("upload_file_name"), True, False, None),
            ("nrows", effective_parameters.get("nrows"), False, True, lambda x: x is None or isinstance(x, int) and x >= 0),
            ("folder_creation_config", folder_creation_config, False, True, lambda x: isinstance(x, dict))
        ]

        return self.validate_paths_and_parameters(
            files=files,
            directories=directories,
            parameters=parameters
        )


# Create a default validation manager instance for backward compatibility
default_validator = ValidationManager()
