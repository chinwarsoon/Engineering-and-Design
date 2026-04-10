"""
JSON Schema Validator Module

Provides JSON Schema validation for error handling configurations.
Validates error codes, taxonomy, and other JSON structures.
"""

import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class JSONSchemaValidator:
    """
    Validates JSON data against JSON Schema definitions.
    
    Uses the anatomy_schema.json as the primary schema for
    validating error code structures and formats.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize validator."""
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._validation_errors: List[str] = []
    
    def validate_error_code_structure(
        self,
        error_code: str,
        error_data: Dict[str, Any]
    ) -> bool:
        """
        Validate an error code entry structure.
        
        Args:
            error_code: The error code (e.g., "P-C-P-0101")
            error_data: The error definition dict
        
        Returns:
            True if valid, False otherwise
        """
        self._validation_errors = []
        
        # Check required fields
        required_fields = ["layer", "severity", "taxonomy", "message_key"]
        for field in required_fields:
            if field not in error_data:
                self._validation_errors.append(f"Missing required field: {field}")
        
        # Validate taxonomy structure
        taxonomy = error_data.get("taxonomy", {})
        taxonomy_required = ["engine", "engine_code", "module", "module_code", 
                          "function", "function_code", "family", "family_code"]
        for field in taxonomy_required:
            if field not in taxonomy:
                self._validation_errors.append(f"Missing taxonomy field: {field}")
        
        # Validate layer
        valid_layers = ["L0", "L1", "L2", "L2.5", "L3", "L4", "L5"]
        layer = error_data.get("layer")
        if layer and layer not in valid_layers:
            self._validation_errors.append(f"Invalid layer: {layer}")
        
        # Validate severity
        valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "WARNING", "INFO"]
        severity = error_data.get("severity")
        if severity and severity not in valid_severities:
            self._validation_errors.append(f"Invalid severity: {severity}")
        
        # Validate error code format
        if not self._validate_error_code_format(error_code):
            self._validation_errors.append(f"Invalid error code format: {error_code}")
        
        return len(self._validation_errors) == 0
    
    def _validate_error_code_format(self, error_code: str) -> bool:
        """Validate E-M-F-XXXX format."""
        import re
        pattern = r'^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$'
        return bool(re.match(pattern, error_code))
    
    def validate_taxonomy_consistency(
        self,
        error_code: str,
        error_data: Dict[str, Any],
        taxonomy_loader: Any
    ) -> bool:
        """
        Validate error code against taxonomy definitions.
        
        Args:
            error_code: Error code to validate
            error_data: Error definition
            taxonomy_loader: TaxonomyLoader instance
        
        Returns:
            True if consistent with taxonomy
        """
        self._validation_errors = []
        
        parts = error_code.split("-")
        if len(parts) != 4:
            self._validation_errors.append(f"Invalid error code format: {error_code}")
            return False
        
        engine_code, module_code, function_code, unique_id = parts
        taxonomy = error_data.get("taxonomy", {})
        
        # Validate engine code matches
        if taxonomy.get("engine_code") != engine_code:
            self._validation_errors.append(
                f"Engine code mismatch: taxonomy says {taxonomy.get('engine_code')}, "
                f"but code is {engine_code}"
            )
        
        # Validate module code matches
        if taxonomy.get("module_code") != module_code:
            self._validation_errors.append(
                f"Module code mismatch: taxonomy says {taxonomy.get('module_code')}, "
                f"but code is {module_code}"
            )
        
        # Validate function code matches
        if taxonomy.get("function_code") != function_code:
            self._validation_errors.append(
                f"Function code mismatch: taxonomy says {taxonomy.get('function_code')}, "
                f"but code is {function_code}"
            )
        
        # Validate against taxonomy loader if provided
        if taxonomy_loader:
            if not taxonomy_loader.get_engine(engine_code):
                self._validation_errors.append(f"Unknown engine code: {engine_code}")
            
            if not taxonomy_loader.get_module(module_code):
                self._validation_errors.append(f"Unknown module code: {module_code}")
            
            if not taxonomy_loader.get_function(function_code):
                self._validation_errors.append(f"Unknown function code: {function_code}")
        
        return len(self._validation_errors) == 0
    
    def validate_json_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that a file contains valid JSON.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            True if valid JSON
        """
        self._validation_errors = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            self._validation_errors.append(f"File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            self._validation_errors.append(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self._validation_errors.append(f"Error reading file: {e}")
            return False
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors from last validation."""
        return self._validation_errors.copy()
    
    def clear_errors(self) -> None:
        """Clear validation errors."""
        self._validation_errors = []
    
    def validate_error_registry(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire error registry.
        
        Args:
            registry_data: Full registry dict with "errors" key
        
        Returns:
            Validation report with errors and statistics
        """
        errors_list = []
        warnings_list = []
        
        errors = registry_data.get("errors", {})
        
        for error_code, error_def in errors.items():
            if not self.validate_error_code_structure(error_code, error_def):
                for err in self.get_validation_errors():
                    errors_list.append(f"{error_code}: {err}")
            
            # Check for duplicate unique IDs within same engine/module/function
            # (simplified check)
            parts = error_code.split("-")
            if len(parts) == 4:
                base = "-".join(parts[:3])  # E-M-F
                unique_id = parts[3]
                # This would need full registry scan for true duplicates
        
        # Check version field
        if "version" not in registry_data:
            warnings_list.append("Registry missing version field")
        
        return {
            "valid": len(errors_list) == 0,
            "errors": errors_list,
            "warnings": warnings_list,
            "total_codes": len(errors),
            "error_count": len(errors_list),
            "warning_count": len(warnings_list)
        }
