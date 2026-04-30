"""
Parameter Type Registry for type-driven validation.

Loads global_parameters.json and provides parameter metadata lookups.
Follows agent_rule.md Section 4 (Module Design) with standardized docstrings.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union


@dataclass
class ParameterType:
    """
    Single parameter type definition with complete metadata.
    
    Attributes:
        name: Canonical parameter key name
        param_type: Data type (file, directory, scalar, boolean, integer, object)
        description: Human-readable description
        required: Whether parameter is mandatory
        default_source: Source precedence (cli, schema, native, env)
        cli_arg_name: CLI argument name (e.g., --excel-file)
        cli_arg_short: Short CLI argument (e.g., -e)
        validation_rules: Type-specific validation rules
        default_value: Default value if not provided
        aliases: Alternative key names for backward compatibility
    """
    name: str
    param_type: str
    description: str
    required: bool = False
    default_source: str = "native"
    cli_arg_name: Optional[str] = None
    cli_arg_short: Optional[str] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    default_value: Any = None
    aliases: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterType":
        """
        Create ParameterType from dictionary loaded from global_parameters.json.
        
        Breadcrumb: global_parameters.json -> ParameterType.from_dict() -> validation_rules extraction
        
        Args:
            data: Dictionary containing parameter definition
            
        Returns:
            ParameterType instance with parsed validation rules
        """
        validation_rules = {}
        
        # Extract validation rules (flattened structure per agent_rule.md Section 2)
        if "check_exists" in data:
            validation_rules["must_exist"] = data["check_exists"]
        if "create_if_missing" in data:
            validation_rules["create_if_missing"] = data["create_if_missing"]
        if "file_extensions" in data:
            validation_rules["file_types"] = data["file_extensions"]
        if "pattern" in data:
            validation_rules["pattern"] = data["pattern"]
        if "min_value" in data:
            validation_rules["min_value"] = data["min_value"]
        if "max_value" in data:
            validation_rules["max_value"] = data["max_value"]
            
        return cls(
            name=data["key"],
            param_type=data["type"],
            description=data["description"],
            required=data.get("required", False),
            default_source=data.get("default_source", "native"),
            cli_arg_name=data.get("cli_arg_name"),
            cli_arg_short=data.get("cli_arg_short"),
            validation_rules=validation_rules,
            default_value=data.get("default_value"),
            aliases=data.get("aliases", [])
        )


class ParameterTypeRegistry:
    """
    Registry for parameter type definitions from global_parameters.json.
    
    Provides type lookups, CLI parameter generation, and validation metadata.
    Follows singleton pattern for caching (load once, reuse).
    
    Breadcrumb: global_parameters.json -> ParameterTypeRegistry.load_from_schema() -> _register_parameter()
    """
    
    _instance: Optional["ParameterTypeRegistry"] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - return cached instance if available."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        """
        Initialize registry. Only loads on first instantiation.
        
        Args:
            schema_path: Path to global_parameters.json
        """
        # Skip re-initialization for singleton
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._parameters: Dict[str, ParameterType] = {}
        self._cli_map: Dict[str, str] = {}  # cli_arg_name -> parameter_name
        self._type_index: Dict[str, List[str]] = {}  # type -> [parameter_names]
        self._metadata: Dict[str, Any] = {}
        self._initialized = False
        
        if schema_path:
            self.load_from_schema(schema_path)
    
    def load_from_schema(self, schema_path: Union[str, Path]) -> None:
        """
        Load parameter definitions from global_parameters.json.
        
        Breadcrumb: schema_path -> json.load() -> ParameterType.from_dict() -> _register_parameter()
        
        Args:
            schema_path: Path to global_parameters.json
            
        Raises:
            FileNotFoundError: If schema file not found
            json.JSONDecodeError: If invalid JSON
        """
        schema_path = Path(schema_path)
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Parameter schema not found: {schema_path}")
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Load metadata
        self._metadata = {
            "version": data.get("version", "unknown"),
            "title": data.get("title", ""),
            "description": data.get("description", "")
        }
        
        # Load parameters
        for param_data in data.get("global_parameters", []):
            param = ParameterType.from_dict(param_data)
            self._register_parameter(param)
        
        self._initialized = True
    
    def _register_parameter(self, param: ParameterType) -> None:
        """
        Register a parameter type in indexes.
        
        Breadcrumb: param -> _parameters, _cli_map, _type_index
        
        Args:
            param: ParameterType instance to register
        """
        # Main index by name
        self._parameters[param.name] = param
        
        # Index by CLI arg name
        if param.cli_arg_name:
            self._cli_map[param.cli_arg_name] = param.name
            
        # Index by type
        if param.param_type not in self._type_index:
            self._type_index[param.param_type] = []
        if param.name not in self._type_index[param.param_type]:
            self._type_index[param.param_type].append(param.name)
        
        # Index by aliases (point to same object)
        for alias in param.aliases:
            if alias not in self._parameters:
                self._parameters[alias] = param
    
    def get_parameter(self, name: str) -> Optional[ParameterType]:
        """
        Get parameter type by name or alias.
        
        Args:
            name: Parameter key name or alias
            
        Returns:
            ParameterType if found, None otherwise
        """
        return self._parameters.get(name)
    
    def get_cli_parameters(self) -> Dict[str, ParameterType]:
        """
        Get all parameters with CLI arguments.
        
        Returns:
            Dictionary of parameter_name -> ParameterType for CLI-enabled parameters
        """
        return {
            name: self._parameters[name] 
            for name in self._cli_map.values()
            if name in self._parameters
        }
    
    def get_parameters_by_type(self, param_type: str) -> List[ParameterType]:
        """
        Get all parameters of a specific type.
        
        Args:
            param_type: Type filter (file, directory, scalar, boolean, integer, object)
            
        Returns:
            List of ParameterType instances
        """
        names = self._type_index.get(param_type, [])
        # Use id() to deduplicate (aliases point to same object)
        seen = set()
        result = []
        for name in names:
            param = self._parameters.get(name)
            if param and id(param) not in seen:
                seen.add(id(param))
                result.append(param)
        return result
    
    def validate_parameter_name(self, name: str) -> bool:
        """
        Check if parameter name is registered.
        
        Args:
            name: Parameter key to validate
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._parameters
    
    def get_canonical_key(self, name: str) -> str:
        """
        Get canonical parameter key from name or alias.
        
        Args:
            name: Parameter key name or alias
            
        Returns:
            Canonical parameter name if found, otherwise returns input name
        """
        param = self._parameters.get(name)
        if param:
            return param.name
        return name
    
    def get_all_parameters(self) -> Dict[str, ParameterType]:
        """
        Get all registered parameters (canonical names only, no aliases).
        
        Returns:
            Dictionary of canonical parameter names to ParameterType
        """
        # Filter to canonical names only (exclude aliases)
        canonical = {}
        seen = set()
        for name, param in self._parameters.items():
            if id(param) not in seen:
                seen.add(id(param))
                canonical[name] = param
        return canonical
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get registry metadata."""
        return self._metadata.copy()
    
    @property
    def parameter_count(self) -> int:
        """Get count of unique parameters (aliases excluded)."""
        return len(set(id(p) for p in self._parameters.values()))
    
    def reload(self, schema_path: Union[str, Path]) -> None:
        """
        Clear and reload from schema.
        
        Args:
            schema_path: Path to global_parameters.json
        """
        self._parameters.clear()
        self._cli_map.clear()
        self._type_index.clear()
        self._metadata.clear()
        self.load_from_schema(schema_path)


def get_parameter_registry(schema_path: Optional[Union[str, Path]] = None) -> ParameterTypeRegistry:
    """
    Get or create singleton ParameterTypeRegistry instance.
    
    Convenience function for accessing the global registry.
    
    Args:
        schema_path: Path to global_parameters.json (only used on first call)
        
    Returns:
        ParameterTypeRegistry singleton instance
        
    Example:
        >>> registry = get_parameter_registry("config/schemas/global_parameters.json")
        >>> param = registry.get_parameter("upload_file_name")
    """
    return ParameterTypeRegistry(schema_path)


# Backward compatibility - default instance
_default_registry: Optional[ParameterTypeRegistry] = None


def load_default_registry(schema_path: Union[str, Path]) -> None:
    """
    Load default global registry (non-singleton for testing).
    
    Args:
        schema_path: Path to global_parameters.json
    """
    global _default_registry
    _default_registry = ParameterTypeRegistry(schema_path)


def get_default_registry() -> Optional[ParameterTypeRegistry]:
    """
    Get default registry instance.
    
    Returns:
        Default registry or None if not loaded
    """
    return _default_registry


__all__ = [
    "ParameterType",
    "ParameterTypeRegistry",
    "get_parameter_registry",
    "load_default_registry",
    "get_default_registry",
]
