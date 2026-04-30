"""
Type-driven parameter validation with 6 type-specific validators.

Validates parameters based on type from ParameterTypeRegistry.
Follows agent_rule.md Section 5 (Function coding) with standardized docstrings.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import os

from utility_engine.validation.parameter_type_registry import ParameterType, ParameterTypeRegistry


@dataclass
class ParameterValidationResult:
    """
    Result of parameter validation.
    
    Attributes:
        parameter_name: Canonical parameter key name
        parameter_type: Data type that was validated
        value: Value that was validated
        is_valid: Whether validation passed
        source: Source of value (cli, schema, native)
        error_message: Error description if failed
        resolved_path: Resolved Path object if applicable
        warnings: List of non-fatal warnings
    """
    parameter_name: str
    parameter_type: str
    value: Any
    is_valid: bool
    source: str
    error_message: Optional[str] = None
    resolved_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize warnings list if None."""
        if self.warnings is None:
            self.warnings = []


class ParameterValidator:
    """
    Type-driven parameter validator using ParameterTypeRegistry.
    
    Dispatches validation to type-specific methods based on parameter type.
    Supports 6 types: file, directory, scalar, boolean, integer, object.
    
    Breadcrumb: registry -> validate_parameter() -> type dispatcher -> type-specific validator
    """
    
    def __init__(
        self, 
        registry: ParameterTypeRegistry, 
        base_path: Optional[Path] = None,
        system_context: Optional[str] = None
    ):
        """
        Initialize validator with registry and base path.
        
        Args:
            registry: ParameterTypeRegistry with loaded parameter definitions
            base_path: Base directory for relative path resolution
            system_context: System context (windows, linux, colab) for platform-specific defaults
        """
        self.registry = registry
        self.base_path = base_path or Path.cwd()
        self.system_context = system_context or self._detect_system()
        self.results: List[ParameterValidationResult] = []
        
    def _detect_system(self) -> str:
        """
        Detect current system context.
        
        Returns:
            System identifier: windows, linux, or colab
        """
        import platform
        
        # Check for Colab first
        try:
            import google.colab
            return "colab"
        except ImportError:
            pass
        
        # Check platform
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        return "linux"
    
    def validate_parameter(
        self, 
        name: str, 
        value: Any, 
        source: str = "native"
    ) -> ParameterValidationResult:
        """
        Validate a single parameter by type from registry.
        
        Breadcrumb: name -> registry.get_parameter() -> type dispatcher -> validator
        
        Args:
            name: Parameter key name
            value: Value to validate
            source: Source of value (cli, schema, native, env)
            
        Returns:
            ParameterValidationResult with validation status and details
        """
        param_type = self.registry.get_parameter(name)
        
        if not param_type:
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="unknown",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Unknown parameter: {name} - not registered in global_parameters.json"
            )
        
        # Type-driven dispatch
        validators = {
            "file": self._validate_file_parameter,
            "directory": self._validate_directory_parameter,
            "scalar": self._validate_scalar_parameter,
            "boolean": self._validate_boolean_parameter,
            "integer": self._validate_integer_parameter,
            "object": self._validate_object_parameter,
        }
        
        validator = validators.get(param_type.param_type)
        if not validator:
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type=param_type.param_type,
                value=value,
                is_valid=False,
                source=source,
                error_message=f"No validator implemented for type: {param_type.param_type}"
            )
        
        result = validator(name, value, param_type, source)
        self.results.append(result)
        return result
    
    def validate_parameters(
        self,
        parameters: Dict[str, Any],
        source: str = "native"
    ) -> List[ParameterValidationResult]:
        """
        Batch validate multiple parameters.
        
        Breadcrumb: parameters dict -> validate_parameter() for each -> results list
        
        Args:
            parameters: Dictionary of parameter names to values
            source: Source of all parameters (cli, schema, native)
            
        Returns:
            List of ParameterValidationResult for each parameter
        """
        results = []
        for name, value in parameters.items():
            result = self.validate_parameter(name, value, source)
            results.append(result)
        return results
    
    def validate_all_registered(self, source: str = "native") -> List[ParameterValidationResult]:
        """
        Validate all registered parameters using their default values.
        
        Args:
            source: Source to report for validation
            
        Returns:
            List of validation results for all registered parameters
        """
        results = []
        for name, param in self.registry.get_all_parameters().items():
            value = param.default_value
            result = self.validate_parameter(name, value, source)
            results.append(result)
        return results
    
    def _resolve_path(self, value: Union[str, Path], base_path_relative: bool = True) -> Path:
        """
        Resolve path relative to base_path if needed.
        
        Args:
            value: Path string or Path object
            base_path_relative: Whether to resolve relative to base_path
            
        Returns:
            Resolved Path object
        """
        path = Path(value)
        if base_path_relative and not path.is_absolute():
            path = self.base_path / path
        return path
    
    def _validate_file_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate file type parameter.
        
        Checks: existence (if required), file extensions, path resolution
        
        Breadcrumb: value -> _resolve_path() -> exists check -> extension check
        
        Args:
            name: Parameter name
            value: File path value
            param_type: ParameterType with validation rules
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        rules = param_type.validation_rules
        
        # Resolve path
        base_relative = rules.get("base_path_relative", True)
        path = self._resolve_path(value, base_relative)
        
        # Check existence if required
        must_exist = rules.get("must_exist", True)
        if must_exist and not path.exists():
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="file",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"File does not exist: {path}",
                resolved_path=path
            )
        
        # Check if actually a file (if exists)
        if path.exists() and not path.is_file():
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="file",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Path exists but is not a file: {path}",
                resolved_path=path
            )
        
        # Check extension
        file_types = rules.get("file_types", [])
        if file_types and path.suffix not in file_types:
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="file",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Invalid file extension: {path.suffix}. Allowed: {', '.join(file_types)}",
                resolved_path=path
            )
        
        return ParameterValidationResult(
            parameter_name=name,
            parameter_type="file",
            value=value,
            is_valid=True,
            source=source,
            resolved_path=path.resolve() if path.exists() else path
        )
    
    def _validate_directory_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate directory type parameter.
        
        Checks: existence, creation if missing, path resolution
        
        Breadcrumb: value -> _resolve_path() -> exists check -> create_if_missing
        
        Args:
            name: Parameter name
            value: Directory path value
            param_type: ParameterType with validation rules
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        rules = param_type.validation_rules
        
        # Resolve path
        base_relative = rules.get("base_path_relative", True)
        path = self._resolve_path(value, base_relative)
        
        warnings = []
        
        # Handle non-existent path
        if not path.exists():
            create_if_missing = rules.get("create_if_missing", False)
            if create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    warnings.append(f"Created directory: {path}")
                except Exception as e:
                    return ParameterValidationResult(
                        parameter_name=name,
                        parameter_type="directory",
                        value=value,
                        is_valid=False,
                        source=source,
                        error_message=f"Cannot create directory {path}: {e}",
                        resolved_path=path
                    )
            elif rules.get("must_exist", True):
                return ParameterValidationResult(
                    parameter_name=name,
                    parameter_type="directory",
                    value=value,
                    is_valid=False,
                    source=source,
                    error_message=f"Directory does not exist: {path}",
                    resolved_path=path
                )
        
        # Check if actually a directory (if exists)
        if path.exists() and not path.is_dir():
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="directory",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Path exists but is not a directory: {path}",
                resolved_path=path
            )
        
        result = ParameterValidationResult(
            parameter_name=name,
            parameter_type="directory",
            value=value,
            is_valid=True,
            source=source,
            resolved_path=path.resolve()
        )
        result.warnings = warnings
        return result
    
    def _validate_scalar_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate scalar/string parameter.
        
        Checks: pattern matching, non-empty
        
        Breadcrumb: value -> pattern check -> validation result
        
        Args:
            name: Parameter name
            value: Scalar/string value
            param_type: ParameterType with validation rules
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        rules = param_type.validation_rules
        
        # Pattern validation
        pattern = rules.get("pattern")
        if pattern:
            if not re.match(pattern, str(value)):
                return ParameterValidationResult(
                    parameter_name=name,
                    parameter_type="scalar",
                    value=value,
                    is_valid=False,
                    source=source,
                    error_message=f"Value '{value}' does not match pattern: {pattern}"
                )
        
        return ParameterValidationResult(
            parameter_name=name,
            parameter_type="scalar",
            value=value,
            is_valid=True,
            source=source
        )
    
    def _validate_boolean_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate boolean parameter.
        
        Checks: type is bool
        
        Breadcrumb: value -> isinstance(bool) -> validation result
        
        Args:
            name: Parameter name
            value: Boolean value
            param_type: ParameterType
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        if not isinstance(value, bool):
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="boolean",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Expected boolean (true/false), got {type(value).__name__}: {value}"
            )
        
        return ParameterValidationResult(
            parameter_name=name,
            parameter_type="boolean",
            value=value,
            is_valid=True,
            source=source
        )
    
    def _validate_integer_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate integer parameter.
        
        Checks: type is int, range validation
        
        Breadcrumb: value -> isinstance(int) -> range check
        
        Args:
            name: Parameter name
            value: Integer value
            param_type: ParameterType with validation rules
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        # Type check
        if not isinstance(value, int):
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="integer",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Expected integer, got {type(value).__name__}: {value}"
            )
        
        rules = param_type.validation_rules
        
        # Range validation
        min_val = rules.get("min_value")
        if min_val is not None and value < min_val:
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="integer",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Value {value} is below minimum {min_val}"
            )
        
        max_val = rules.get("max_value")
        if max_val is not None and value > max_val:
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="integer",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Value {value} is above maximum {max_val}"
            )
        
        return ParameterValidationResult(
            parameter_name=name,
            parameter_type="integer",
            value=value,
            is_valid=True,
            source=source
        )
    
    def _validate_object_parameter(
        self,
        name: str,
        value: Any,
        param_type: ParameterType,
        source: str
    ) -> ParameterValidationResult:
        """
        Validate object parameter (complex nested data).
        
        Checks: type is dict, basic structure
        
        Breadcrumb: value -> isinstance(dict) -> validation result
        
        Args:
            name: Parameter name
            value: Object/dict value
            param_type: ParameterType
            source: Value source
            
        Returns:
            ParameterValidationResult
        """
        if not isinstance(value, dict):
            return ParameterValidationResult(
                parameter_name=name,
                parameter_type="object",
                value=value,
                is_valid=False,
                source=source,
                error_message=f"Expected object/dict, got {type(value).__name__}"
            )
        
        return ParameterValidationResult(
            parameter_name=name,
            parameter_type="object",
            value=value,
            is_valid=True,
            source=source
        )
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all validation results.
        
        Returns:
            Dictionary with total, valid, invalid counts and error list
        """
        total = len(self.results)
        valid = sum(1 for r in self.results if r.is_valid)
        invalid = total - valid
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "errors": [
                {
                    "parameter": r.parameter_name,
                    "type": r.parameter_type,
                    "error": r.error_message,
                    "value": r.value
                }
                for r in self.results if not r.is_valid
            ]
        }
    
    def has_errors(self) -> bool:
        """
        Check if any validation resulted in error.
        
        Returns:
            True if any result has is_valid=False
        """
        return any(not r.is_valid for r in self.results)
    
    def get_errors(self) -> List[ParameterValidationResult]:
        """
        Get all failed validation results.
        
        Returns:
            List of failed ParameterValidationResult
        """
        return [r for r in self.results if not r.is_valid]
    
    def clear_results(self) -> None:
        """Clear all validation results."""
        self.results.clear()


__all__ = [
    "ParameterValidationResult",
    "ParameterValidator",
]
