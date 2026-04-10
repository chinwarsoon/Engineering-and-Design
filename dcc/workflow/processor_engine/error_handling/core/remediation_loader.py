"""
Remediation Loader Module

Loads and manages remediation strategy definitions from JSON configuration.
Provides remediation type lookup and selection rules.
"""

import json
from typing import Dict, List, Optional, Any, Set
from pathlib import Path


class RemediationLoader:
    """
    Loads remediation types from config/remediation_types.json.
    
    Manages:
    - Remediation strategy definitions (AUTO_FIX, MANUAL_FIX, etc.)
    - Selection rules by severity, layer, and family
    - Remediation eligibility checking
    """
    
    _instance = None
    _remediation_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize remediation loader."""
        if self._remediation_data is not None:
            return
            
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "remediation_types.json"
        
        self.config_path = Path(config_path)
        self._load_remediation()
    
    def _load_remediation(self) -> None:
        """Load remediation types from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Remediation config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._remediation_data = json.load(f)
        
        self.version = self._remediation_data.get("version", "unknown")
        self._types = self._remediation_data.get("types", {})
        self._selection_rules = self._remediation_data.get("selection_rules", {})
    
    def reload(self) -> None:
        """Reload remediation data from disk."""
        self._remediation_data = None
        self._load_remediation()
    
    def get_type(self, type_code: str) -> Optional[Dict[str, Any]]:
        """
        Get remediation type definition by code.
        
        Args:
            type_code: Remediation type code (AUTO_FIX, MANUAL_FIX, etc.)
        
        Returns:
            Type definition or None
        """
        return self._types.get(type_code)
    
    def get_all_types(self) -> Dict[str, Dict[str, Any]]:
        """Get all remediation type definitions."""
        return self._types.copy()
    
    def get_type_codes(self) -> Set[str]:
        """Get all available remediation type codes."""
        return set(self._types.keys())
    
    def is_auto_eligible(self, type_code: str) -> bool:
        """Check if remediation type supports automatic application."""
        type_def = self._types.get(type_code, {})
        return type_def.get("auto_eligible", False)
    
    def requires_approval(self, type_code: str) -> bool:
        """Check if remediation type requires approval."""
        type_def = self._types.get(type_code, {})
        return type_def.get("requires_approval", False)
    
    def requires_confirmation(self, type_code: str) -> bool:
        """Check if remediation type requires user confirmation."""
        type_def = self._types.get(type_code, {})
        return type_def.get("requires_confirmation", False)
    
    def get_applicable_layers(self, type_code: str) -> List[str]:
        """Get layers where this remediation type can be applied."""
        type_def = self._types.get(type_code, {})
        return type_def.get("applicable_layers", [])
    
    def is_applicable_to_layer(self, type_code: str, layer: str) -> bool:
        """Check if remediation type is applicable to a specific layer."""
        applicable = self.get_applicable_layers(type_code)
        return layer in applicable
    
    def get_selection_rules_by_severity(self, severity: str) -> List[str]:
        """
        Get recommended remediation types for a severity level.
        
        Args:
            severity: CRITICAL, HIGH, MEDIUM, WARNING, INFO
        
        Returns:
            List of remediation type codes
        """
        severity_rules = self._selection_rules.get("by_severity", {})
        return severity_rules.get(severity, [])
    
    def get_selection_rules_by_layer(self, layer: str) -> List[str]:
        """
        Get recommended remediation types for a layer.
        
        Args:
            layer: L0, L1, L2, L2.5, L3, L4, L5
        
        Returns:
            List of remediation type codes
        """
        layer_rules = self._selection_rules.get("by_layer", {})
        return layer_rules.get(layer, [])
    
    def get_selection_rules_by_family(self, family: str) -> List[str]:
        """
        Get recommended remediation types for an error family.
        
        Args:
            family: Anchor, Identity, Logic, Fill, Validation, Calculation, etc.
        
        Returns:
            List of remediation type codes
        """
        family_rules = self._selection_rules.get("by_family", {})
        return family_rules.get(family, [])
    
    def suggest_remediation_types(
        self,
        severity: str,
        layer: str,
        family: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest remediation types based on error characteristics.
        
        Args:
            severity: Error severity
            layer: Validation layer
            family: Error family
            context: Optional additional context
        
        Returns:
            List of suggested types with scores
        """
        suggestions = []
        type_scores = {}
        
        # Score by severity rules
        for type_code in self.get_selection_rules_by_severity(severity):
            type_scores[type_code] = type_scores.get(type_code, 0) + 3
        
        # Score by layer rules
        for type_code in self.get_selection_rules_by_layer(layer):
            type_scores[type_code] = type_scores.get(type_code, 0) + 2
        
        # Score by family rules
        for type_code in self.get_selection_rules_by_family(family):
            type_scores[type_code] = type_scores.get(type_code, 0) + 2
        
        # Filter to applicable types only
        for type_code, score in type_scores.items():
            type_def = self._types.get(type_code)
            if not type_def:
                continue
            
            # Check layer applicability
            if not self.is_applicable_to_layer(type_code, layer):
                continue
            
            suggestions.append({
                "type": type_code,
                "name": type_def.get("name"),
                "score": score,
                "auto_eligible": type_def.get("auto_eligible", False),
                "requires_approval": type_def.get("requires_approval", False),
                "description": type_def.get("description", "")
            })
        
        # Sort by score descending
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return suggestions
    
    def get_implementation_info(self, type_code: str) -> Optional[Dict[str, str]]:
        """
        Get implementation details for a remediation type.
        
        Returns:
            Dict with class, module, method information
        """
        type_def = self._types.get(type_code, {})
        return type_def.get("implementation")
    
    def get_audit_level(self, type_code: str) -> str:
        """Get audit log level for a remediation type."""
        type_def = self._types.get(type_code, {})
        return type_def.get("audit_level", "INFO")
    
    def can_rollback(self, type_code: str) -> bool:
        """Check if remediation type supports rollback."""
        type_def = self._types.get(type_code, {})
        return type_def.get("can_rollback", False)
    
    def get_type_name(self, type_code: str) -> str:
        """Get human-readable name for a remediation type."""
        type_def = self._types.get(type_code, {})
        return type_def.get("name", type_code)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get remediation types statistics."""
        auto_count = sum(1 for t in self._types.values() if t.get("auto_eligible", False))
        approval_count = sum(1 for t in self._types.values() if t.get("requires_approval", False))
        
        return {
            "total_types": len(self._types),
            "auto_eligible": auto_count,
            "requires_approval": approval_count,
            "version": self.version
        }
