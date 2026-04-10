"""
Taxonomy Loader Module

Loads and provides access to error taxonomy definitions from JSON configuration.
Manages engines, modules, functions, families, and layers.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class TaxonomyLoader:
    """
    Loads taxonomy definitions from config/taxonomy.json.
    
    Provides structured access to:
    - Engine definitions (P, M, I, S, R, H, V)
    - Module definitions (C, V, A, D, S, F, L, G, E, P)
    - Function definitions (P, V, C, F)
    - Family definitions (1-9)
    - Layer definitions (L0-L5)
    """
    
    _instance = None
    _taxonomy_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_path: Optional[str] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize taxonomy loader."""
        if self._taxonomy_data is not None:
            return
            
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "taxonomy.json"
        
        self.config_path = Path(config_path)
        self._load_taxonomy()
    
    def _load_taxonomy(self) -> None:
        """Load taxonomy from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Taxonomy config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._taxonomy_data = json.load(f)
        
        self.version = self._taxonomy_data.get("version", "unknown")
        self._engines = self._taxonomy_data.get("engines", {})
        self._modules = self._taxonomy_data.get("modules", {})
        self._functions = self._taxonomy_data.get("functions", {})
        self._families = self._taxonomy_data.get("families", {})
        self._layers = self._taxonomy_data.get("layers", {})
    
    def reload(self) -> None:
        """Reload taxonomy from disk."""
        self._taxonomy_data = None
        self._load_taxonomy()
    
    def get_engine(self, code: str) -> Optional[Dict[str, Any]]:
        """Get engine definition by code (P, M, I, S, R, H, V)."""
        return self._engines.get(code)
    
    def get_module(self, code: str) -> Optional[Dict[str, Any]]:
        """Get module definition by code (C, V, A, D, S, F, L, G, E, P)."""
        return self._modules.get(code)
    
    def get_function(self, code: str) -> Optional[Dict[str, Any]]:
        """Get function definition by code (P, V, C, F)."""
        return self._functions.get(code)
    
    def get_family(self, code: str) -> Optional[Dict[str, Any]]:
        """Get family definition by code (1-9)."""
        return self._families.get(code)
    
    def get_layer(self, code: str) -> Optional[Dict[str, Any]]:
        """Get layer definition by code (L0, L1, L2, L2.5, L3, L4, L5)."""
        return self._layers.get(code)
    
    def get_all_engines(self) -> Dict[str, Dict[str, Any]]:
        """Get all engine definitions."""
        return self._engines.copy()
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all module definitions."""
        return self._modules.copy()
    
    def get_all_functions(self) -> Dict[str, Dict[str, Any]]:
        """Get all function definitions."""
        return self._functions.copy()
    
    def get_all_families(self) -> Dict[str, Dict[str, Any]]:
        """Get all family definitions."""
        return self._families.copy()
    
    def get_all_layers(self) -> Dict[str, Dict[str, Any]]:
        """Get all layer definitions."""
        return self._layers.copy()
    
    def get_engine_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find engine by name (case-insensitive)."""
        name_lower = name.lower()
        for code, engine in self._engines.items():
            if engine.get("name", "").lower() == name_lower:
                return {**engine, "code": code}
        return None
    
    def get_families_by_layer(self, layer_code: str) -> List[Dict[str, Any]]:
        """Get all families associated with a layer."""
        return [
            {**family, "code": code}
            for code, family in self._families.items()
            if family.get("layer") == layer_code
        ]
    
    def get_modules_by_engine(self, engine_code: str) -> List[Dict[str, Any]]:
        """Get all modules available for an engine."""
        engine = self._engines.get(engine_code)
        if not engine:
            return []
        
        module_codes = engine.get("modules", [])
        return [
            {**self._modules.get(code, {}), "code": code}
            for code in module_codes
            if code in self._modules
        ]
    
    def build_error_code(self, engine: str, module: str, function: str, unique_id: str) -> str:
        """
        Build a complete error code from components.
        
        Args:
            engine: Engine code (e.g., "P")
            module: Module code (e.g., "C")
            function: Function code (e.g., "P")
            unique_id: 4-digit unique ID (e.g., "0101")
        
        Returns:
            Complete error code (e.g., "P-C-P-0101")
        """
        return f"{engine}-{module}-{function}-{unique_id}"
    
    def parse_error_code(self, error_code: str) -> Optional[Dict[str, str]]:
        """
        Parse an error code into its components.
        
        Args:
            error_code: Error code in E-M-F-XXXX format
        
        Returns:
            Dict with engine, module, function, unique_id or None if invalid
        """
        parts = error_code.split("-")
        if len(parts) != 4:
            return None
        
        engine, module, function, unique_id = parts
        
        # Validate each component exists
        if (engine not in self._engines or
            module not in self._modules or
            function not in self._functions):
            return None
        
        return {
            "engine": engine,
            "module": module,
            "function": function,
            "unique_id": unique_id
        }
    
    def get_taxonomy_for_error(self, error_code: str) -> Optional[Dict[str, Any]]:
        """
        Get full taxonomy information for an error code.
        
        Returns:
            Dict with engine, module, function details or None
        """
        parsed = self.parse_error_code(error_code)
        if not parsed:
            return None
        
        engine = self.get_engine(parsed["engine"])
        module = self.get_module(parsed["module"])
        function = self.get_function(parsed["function"])
        
        # Extract family code from unique_id (first digit)
        family_code = parsed["unique_id"][0]
        family = self.get_family(family_code)
        
        return {
            "engine": {**engine, "code": parsed["engine"]} if engine else None,
            "module": {**module, "code": parsed["module"]} if module else None,
            "function": {**function, "code": parsed["function"]} if function else None,
            "family": {**family, "code": family_code} if family else None,
            "unique_id": parsed["unique_id"]
        }
    
    def is_valid_error_code(self, error_code: str) -> bool:
        """Validate that an error code has valid taxonomy components."""
        parsed = self.parse_error_code(error_code)
        return parsed is not None
    
    def get_statistics(self) -> Dict[str, int]:
        """Get taxonomy statistics."""
        return {
            "engines": len(self._engines),
            "modules": len(self._modules),
            "functions": len(self._functions),
            "families": len(self._families),
            "layers": len(self._layers),
            "version": self.version
        }
