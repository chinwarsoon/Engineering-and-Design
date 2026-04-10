"""
Error Code Anatomy Loader Module

Loads and validates error code anatomy definitions.
Provides validation against JSON Schema for error code format.
"""

import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class AnatomyLoader:
    """
    Loads error code anatomy schema from config/anatomy_schema.json.
    
    Provides:
    - JSON Schema validation for error codes
    - Component validation (engine, module, function codes)
    - Error code parsing and formatting
    - Anatomy structure information
    """
    
    _instance = None
    _schema_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize anatomy loader."""
        if self._schema_data is not None:
            return
            
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "anatomy_schema.json"
        
        self.config_path = Path(config_path)
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load anatomy schema from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Anatomy schema not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._schema_data = json.load(f)
        
        self.version = self._schema_data.get("version", "unknown")
        self._definitions = self._schema_data.get("definitions", {})
    
    def reload(self) -> None:
        """Reload schema from disk."""
        self._schema_data = None
        self._load_schema()
    
    def get_valid_engine_codes(self) -> List[str]:
        """Get list of valid engine codes from schema."""
        engine_def = self._definitions.get("engine_code", {})
        return engine_def.get("enum", [])
    
    def get_valid_module_codes(self) -> List[str]:
        """Get list of valid module codes from schema."""
        module_def = self._definitions.get("module_code", {})
        return module_def.get("enum", [])
    
    def get_valid_function_codes(self) -> List[str]:
        """Get list of valid function codes from schema."""
        function_def = self._definitions.get("function_code", {})
        return function_def.get("enum", [])
    
    def is_valid_engine_code(self, code: str) -> bool:
        """Check if engine code is valid."""
        return code in self.get_valid_engine_codes()
    
    def is_valid_module_code(self, code: str) -> bool:
        """Check if module code is valid."""
        return code in self.get_valid_module_codes()
    
    def is_valid_function_code(self, code: str) -> bool:
        """Check if function code is valid."""
        return code in self.get_valid_function_codes()
    
    def is_valid_unique_id(self, unique_id: str) -> bool:
        """Check if unique ID is valid (4 digits)."""
        pattern = r'^[0-9]{4}$'
        return bool(re.match(pattern, unique_id))
    
    def is_valid_error_code_format(self, error_code: str) -> bool:
        """
        Validate complete error code format (E-M-F-XXXX).
        
        Args:
            error_code: Error code to validate
        
        Returns:
            True if format matches E-M-F-XXXX pattern and components are valid
        """
        pattern = r'^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$'
        if not re.match(pattern, error_code):
            return False
        
        parts = error_code.split("-")
        engine, module, function, unique_id = parts
        
        return (self.is_valid_engine_code(engine) and
                self.is_valid_module_code(module) and
                self.is_valid_function_code(function) and
                self.is_valid_unique_id(unique_id))
    
    def parse_error_code(self, error_code: str) -> Optional[Dict[str, str]]:
        """
        Parse error code into its components.
        
        Args:
            error_code: Error code in E-M-F-XXXX format
        
        Returns:
            Dict with components or None if invalid
        """
        if not self.is_valid_error_code_format(error_code):
            return None
        
        parts = error_code.split("-")
        return {
            "engine_code": parts[0],
            "module_code": parts[1],
            "function_code": parts[2],
            "unique_id": parts[3],
            "family_code": parts[3][0]  # First digit indicates family
        }
    
    def get_error_code_pattern(self) -> str:
        """Get the regex pattern for valid error codes."""
        pattern_def = self._definitions.get("error_code_format", {})
        return pattern_def.get("pattern", r'^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$')
    
    def validate_components(self, engine: str, module: str, function: str, unique_id: str) -> Dict[str, Any]:
        """
        Validate individual components and return detailed results.
        
        Returns:
            Dict with validation results for each component
        """
        return {
            "engine": {
                "value": engine,
                "valid": self.is_valid_engine_code(engine),
                "allowed_values": self.get_valid_engine_codes()
            },
            "module": {
                "value": module,
                "valid": self.is_valid_module_code(module),
                "allowed_values": self.get_valid_module_codes()
            },
            "function": {
                "value": function,
                "valid": self.is_valid_function_code(function),
                "allowed_values": self.get_valid_function_codes()
            },
            "unique_id": {
                "value": unique_id,
                "valid": self.is_valid_unique_id(unique_id),
                "pattern": "^[0-9]{4}$"
            },
            "all_valid": (
                self.is_valid_engine_code(engine) and
                self.is_valid_module_code(module) and
                self.is_valid_function_code(function) and
                self.is_valid_unique_id(unique_id)
            )
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the full JSON Schema."""
        return self._schema_data.copy()
    
    def get_schema_version(self) -> str:
        """Get schema version."""
        return self.version
    
    def extract_family_from_unique_id(self, unique_id: str) -> Optional[str]:
        """
        Extract family code from unique ID.
        Family code is the first digit of the unique ID.
        """
        if not self.is_valid_unique_id(unique_id):
            return None
        return unique_id[0]
    
    def get_unique_id_range_for_family(self, family_code: str) -> tuple:
        """
        Get the numeric range for a family code.
        
        Args:
            family_code: Single digit (1-9)
        
        Returns:
            Tuple of (min, max) for the family range
        """
        if not family_code.isdigit() or len(family_code) != 1:
            return (0, 0)
        
        family_num = int(family_code)
        min_id = family_num * 100
        max_id = min_id + 99
        
        return (min_id, max_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get anatomy schema statistics."""
        return {
            "version": self.version,
            "valid_engine_codes": len(self.get_valid_engine_codes()),
            "valid_module_codes": len(self.get_valid_module_codes()),
            "valid_function_codes": len(self.get_valid_function_codes()),
            "unique_id_range": "0001-9999"
        }
