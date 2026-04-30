"""
Universal Validation Utilities - Class-Based Design Approach

Provides a ValidationManager class that encapsulates all validation functionality
for files, folders, and parameters that can be used across all pipeline components.

Phase 2 Enhancement: Type-driven parameter validation with ParameterTypeRegistry
and ParameterValidator for schema-based, type-driven validation.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Phase 2: Type-driven parameter validation imports
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
        name = name or str(file_path)
        exists = file_path.exists() and file_path.is_file()
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
    
    def validate_directory_exists(self, dir_path: Path, name: Optional[str] = None, required: bool = True, create_if_missing: bool = False) -> ValidationItem:
        """Validate that a directory exists with optional creation."""
        name = name or str(dir_path)
        
        # Determine creation behavior from project_config if available
        should_create = create_if_missing  # Fallback to parameter for backward compatibility
        if self.folder_creation_config:
            should_create = self.folder_creation_config.get("create_missing_parents", create_if_missing)
        
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
    
    def validate_parameter(self, param_name: str, param_value: Any, required: bool = True, allow_empty: bool = False, validator_func: Optional[callable] = None) -> ValidationItem:
        """Validate a parameter value."""
        if param_value is None:
            if required:
                return ValidationItem(
                    name=param_name,
                    path=Path(""),
                    status=ValidationStatus.FAIL,
                    message=f"Required parameter '{param_name}' is missing",
                    exists=False
                )
            else:
                return ValidationItem(
                    name=param_name,
                    path=Path(""),
                    status=ValidationStatus.PASS,
                    message=f"Optional parameter '{param_name}' not provided",
                    exists=True
                )
        
        if not allow_empty and param_value == "":
            if required:
                return ValidationItem(
                    name=param_name,
                    path=Path(""),
                    status=ValidationStatus.FAIL,
                    message=f"Required parameter '{param_name}' is empty",
                    exists=False
                )
            else:
                return ValidationItem(
                    name=param_name,
                    path=Path(""),
                    status=ValidationStatus.WARNING,
                    message=f"Optional parameter '{param_name}' is empty",
                    exists=True
                )
        
        # Apply custom validator if provided
        if validator_func:
            try:
                is_valid = validator_func(param_value)
                if not is_valid:
                    return ValidationItem(
                        name=param_name,
                        path=Path(""),
                        status=ValidationStatus.FAIL,
                        message=f"Parameter '{param_name}' failed custom validation",
                        exists=False
                    )
            except Exception as e:
                return ValidationItem(
                    name=param_name,
                    path=Path(""),
                    status=ValidationStatus.WARNING,
                    message=f"Parameter '{param_name}' validation error: {e}",
                    exists=True
                )
        
        return ValidationItem(
            name=param_name,
            path=Path(""),
            status=ValidationStatus.PASS,
            message=f"Parameter '{param_name}' valid: {param_value}",
            exists=True,
            details=str(param_value)
        )
    
    # Path Validation with System Context
    def validate_path_with_system_context(self, path_input: Union[str, Path], path_type: str = "file", name: Optional[str] = None, required: bool = True, base_path: Optional[Path] = None, create_if_missing: bool = False) -> ValidationItem:
        """Centralized path validation that combines safe_resolve with validation."""
        name = name or str(path_input)
        
        try:
            # Import path resolution utilities
            import platform
            from utility_engine.paths import safe_resolve, get_system_context, resolve_with_system_context
            
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
        items = []
        errors = []
        warnings = []
        
        # Validate files
        if files:
            for file_path, name, required, create_parent in files:
                item = self.validate_file_exists(file_path, name, required)
                items.append(item)
                
                if item.status == ValidationStatus.FAIL:
                    errors.append(item.message)
                elif item.status == ValidationStatus.WARNING:
                    warnings.append(item.message)
        
        # Validate directories
        if directories:
            for dir_path, name, required, create_if_missing in directories:
                item = self.validate_directory_exists(dir_path, name, required, create_if_missing)
                items.append(item)
                
                if item.status == ValidationStatus.FAIL:
                    errors.append(item.message)
                elif item.status == ValidationStatus.WARNING:
                    warnings.append(item.message)
        
        # Validate parameters
        if parameters:
            for param_name, param_value, required, allow_empty, validator_func in parameters:
                item = self.validate_parameter(param_name, param_value, required, allow_empty, validator_func)
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
            'total_items': len(items),
            'passed': len([item for item in items if item.status == ValidationStatus.PASS]),
            'failed': len([item for item in items if item.status == ValidationStatus.FAIL]),
            'warnings': len([item for item in items if item.status == ValidationStatus.WARNING])
        }
        
        return ValidationResult(
            status=status,
            items=items,
            summary=summary,
            errors=errors,
            warnings=warnings
        )
    
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
    validator_func: Optional[callable] = None
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
                passed, message = custom_result
                status = ValidationStatus.PASS if passed else ValidationStatus.FAIL
                message = f"Parameter {param_name}: {message}"
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
    parameters: List[Tuple[str, Any, bool, bool, Optional[callable]]] = None,
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


def validate_path_with_system_context(
    path_input: Union[str, Path],
    path_type: str = "file",  # "file" or "directory"
    name: Optional[str] = None,
    required: bool = True,
    base_path: Optional[Path] = None,
    folder_creation_config: Optional[Dict[str, Any]] = None,
    create_if_missing: bool = False
) -> ValidationItem:
    """
    Centralized path validation that combines safe_resolve with validation.
    
    This function provides a unified interface for:
    - OS detection and system context handling
    - Path resolution with base path context
    - File/directory existence validation
    - Optional directory creation based on configuration
    
    Args:
        path_input: Path to validate (string or Path object)
        path_type: Type of path - "file" or "directory"
        name: Descriptive name for the path
        required: Whether the path must exist
        base_path: Base path for relative resolution
        folder_creation_config: Folder creation configuration from project_config
        create_if_missing: Whether to create directory if missing (deprecated, use folder_creation_config)
        
    Returns:
        ValidationItem with comprehensive validation results including:
        - Resolved path
        - OS context information
        - Existence status
        - Creation status (if applicable)
        - Validation status and messages
    """
    name = name or str(path_input)
    
    # Import safe_resolve for path resolution
    import platform
    from utility_engine.paths import safe_resolve, get_system_context
    
    try:
        # Step 1: Resolve path with system context using resolve_with_system_context for detailed results
        from utility_engine.paths import resolve_with_system_context
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
            item = validate_directory_exists(
                resolution_result.resolved_path, 
                name, 
                required, 
                create_if_missing, 
                folder_creation_config
            )
        elif path_type == "file":
            # Use existing file validation
            item = validate_file_exists(resolution_result.resolved_path, name, required)
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


def validate_home_directory() -> ValidationItem:
    """
    Validate and resolve the home directory using centralized validation.
    
    This function provides a unified interface for:
    - Home directory detection and resolution
    - System context handling for different platforms
    - Validation of home directory accessibility
    
    Returns:
        ValidationItem with home directory validation results including:
        - Resolved home directory path
        - System context information
        - Validation status and messages
    """
    try:
        # Import get_homedir for home directory resolution
        from core_engine.paths import get_homedir
        
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
        from utility_engine.paths import get_system_context
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


def validate_pipeline_prerequisites(
    base_path: Path,
    schema_path: Path,
    input_file_path: Path,
    export_paths: Dict[str, Path],
    effective_parameters: Dict[str, Any],
    project_config: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """
    Validate all pipeline prerequisites using universal validation functions.
    
    Args:
        base_path: Project base directory
        schema_path: Schema file path
        input_file_path: Input Excel file path
        export_paths: Dictionary of export paths
        effective_parameters: Resolved parameters
        project_config: Project configuration from project_config.json
        
    Returns:
        ValidationResult with comprehensive pipeline validation
    """
    # Load folder creation configuration from project_config
    folder_creation_config = {}
    if project_config and "folder_creation" in project_config:
        folder_creation_config = project_config["folder_creation"]
    else:
        # Default fallback configuration
        folder_creation_config = {
            "auto_create_output_directories": True,
            "auto_create_debug_directories": True,
            "auto_create_log_directories": True,
            "create_missing_parents": True
        }
    
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
    
    return validate_paths_and_parameters(
        files=files,
        directories=directories,
        parameters=parameters,
        folder_creation_config=folder_creation_config
    )
