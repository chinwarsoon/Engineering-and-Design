"""
Error Registry Module

Loads and manages error codes from JSON configuration.
Provides query capabilities for error code lookup and filtering.
"""

import json
import os
from typing import Dict, List, Optional, Any, Set
from pathlib import Path


class ErrorRegistry:
    """
    Loads and manages error codes from config/error_codes.json.
    
    Provides methods to:
    - Load error registry from JSON
    - Query errors by code, layer, severity, family
    - Get error details with full context
    - Validate error code existence
    """
    
    _instance = None
    _registry_data: Optional[Dict[str, Any]] = None
    _errors: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern to ensure single registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the error registry.
        
        Args:
            config_path: Path to error_codes.json. If None, uses default path.
        """
        if self._registry_data is not None:
            return  # Already initialized
            
        if config_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "error_codes.json"
        
        self.config_path = Path(config_path)
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load the error registry from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Error registry not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._registry_data = json.load(f)
        
        self._errors = self._registry_data.get("errors", {})
        self.version = self._registry_data.get("version", "unknown")
        self.last_updated = self._registry_data.get("last_updated", "unknown")
    
    def reload(self) -> None:
        """Reload the registry from disk (useful for hot updates)."""
        self._registry_data = None
        self._errors = {}
        self._load_registry()
    
    def get_error(self, error_code: str) -> Optional[Dict[str, Any]]:
        """
        Get full error definition by code.
        
        Args:
            error_code: Error code in E-M-F-XXXX format (e.g., "P-C-P-0101")
        
        Returns:
            Error definition dict or None if not found
        """
        return self._errors.get(error_code)
    
    def error_exists(self, error_code: str) -> bool:
        """Check if an error code exists in the registry."""
        return error_code in self._errors
    
    def get_by_layer(self, layer: str) -> List[Dict[str, Any]]:
        """
        Get all errors for a specific validation layer.
        
        Args:
            layer: Layer code (L0, L1, L2, L2.5, L3, L4, L5)
        
        Returns:
            List of error definitions
        """
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("layer") == layer
        ]
    
    def get_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Get all errors of a specific severity.
        
        Args:
            severity: CRITICAL, HIGH, MEDIUM, WARNING, INFO
        
        Returns:
            List of error definitions
        """
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("severity") == severity
        ]
    
    def get_by_family(self, family_code: str) -> List[Dict[str, Any]]:
        """
        Get all errors in an error family.
        
        Args:
            family_code: Family code (1-9)
        
        Returns:
            List of error definitions
        """
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("taxonomy", {}).get("family_code") == family_code
        ]
    
    def get_by_engine(self, engine_code: str) -> List[Dict[str, Any]]:
        """
        Get all errors from a specific engine.
        
        Args:
            engine_code: P, M, I, S, R, H, V
        
        Returns:
            List of error definitions
        """
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("taxonomy", {}).get("engine_code") == engine_code
        ]
    
    def get_fail_fast_errors(self) -> List[Dict[str, Any]]:
        """Get all errors that should trigger fail-fast behavior."""
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("fail_fast", False)
        ]
    
    def get_auto_remediation_errors(self) -> List[Dict[str, Any]]:
        """Get all errors that support automatic remediation."""
        return [
            {**error, "code": code}
            for code, error in self._errors.items()
            if error.get("auto_remediation", False)
        ]
    
    def get_remediation_type(self, error_code: str) -> Optional[str]:
        """
        Get the remediation type for an error.
        
        Args:
            error_code: Error code
        
        Returns:
            Remediation type (AUTO_FIX, MANUAL_FIX, SUPPRESS, etc.) or None
        """
        error = self._errors.get(error_code)
        return error.get("remediation_type") if error else None
    
    def get_message_key(self, error_code: str) -> Optional[str]:
        """Get the localization message key for an error."""
        error = self._errors.get(error_code)
        return error.get("message_key") if error else None
    
    def get_action_key(self, error_code: str) -> Optional[str]:
        """Get the user action key for an error."""
        error = self._errors.get(error_code)
        return error.get("action_key") if error else None
    
    def get_all_codes(self) -> Set[str]:
        """Get all error codes in the registry."""
        return set(self._errors.keys())
    
    def get_error_count(self) -> int:
        """Get total number of error codes."""
        return len(self._errors)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict with counts by layer, severity, engine, etc.
        """
        stats = {
            "total_errors": len(self._errors),
            "version": self.version,
            "by_layer": {},
            "by_severity": {},
            "by_engine": {},
            "by_family": {},
            "fail_fast_count": 0,
            "auto_remediation_count": 0
        }
        
        for error in self._errors.values():
            layer = error.get("layer", "unknown")
            severity = error.get("severity", "unknown")
            engine = error.get("taxonomy", {}).get("engine_code", "unknown")
            family = error.get("taxonomy", {}).get("family_code", "unknown")
            
            stats["by_layer"][layer] = stats["by_layer"].get(layer, 0) + 1
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            stats["by_engine"][engine] = stats["by_engine"].get(engine, 0) + 1
            stats["by_family"][family] = stats["by_family"].get(family, 0) + 1
            
            if error.get("fail_fast", False):
                stats["fail_fast_count"] += 1
            if error.get("auto_remediation", False):
                stats["auto_remediation_count"] += 1
        
        return stats
    
    def validate_code_format(self, error_code: str) -> bool:
        """
        Validate error code format (E-M-F-XXXX).
        
        Args:
            error_code: Error code to validate
        
        Returns:
            True if format is valid
        """
        import re
        pattern = r'^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$'
        return bool(re.match(pattern, error_code))
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search errors by partial match in code, description, or message key.
        
        Args:
            query: Search string
        
        Returns:
            List of matching error definitions
        """
        query_lower = query.lower()
        results = []
        
        for code, error in self._errors.items():
            if (query_lower in code.lower() or
                query_lower in error.get("description", "").lower() or
                query_lower in error.get("message_key", "").lower()):
                results.append({**error, "code": code})
        
        return results
