"""
Centralized schema path configuration for single point of truth.

Eliminates hardcoded paths scattered across the codebase and provides
a consistent way to reference schema files throughout the pipeline.
"""

from pathlib import Path
from typing import Dict, Any


class SchemaPaths:
    """Centralized schema path configuration with single point of truth."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._config_dir = base_path / "config" / "schemas"
    
    @property
    def config_dir(self) -> Path:
        """Get the config/schemas directory."""
        return self._config_dir
    
    # Project Setup Schema Files
    @property
    def project_setup_schema(self) -> Path:
        """Project setup validation schema."""
        return self._config_dir / "project_setup.json"
    
    @property
    def project_config_data(self) -> Path:
        """Project configuration data (actual values)."""
        return self._config_dir / "project_config.json"
    
    @property
    def project_setup_base(self) -> Path:
        """Base schema with reusable definitions."""
        return self._config_dir / "project_setup_base.json"
    
    # Data Register Schema Files
    @property
    def dcc_register_config(self) -> Path:
        """DCC register configuration schema."""
        return self._config_dir / "dcc_register_config.json"
    
    @property
    def dcc_register_enhanced(self) -> Path:
        """Enhanced DCC register schema."""
        return self._config_dir / "dcc_register_enhanced.json"
    
    @property
    def dcc_register_base(self) -> Path:
        """DCC register base definitions."""
        return self._config_dir / "dcc_register_base.json"
    
    # Project Code and Parameter Schemas
    @property
    def project_code_schema(self) -> Path:
        """Project codes and descriptions schema."""
        return self._config_dir / "project_code_schema.json"
    
    @property
    def global_parameters(self) -> Path:
        """Global parameters configuration."""
        return self._config_dir / "global_parameters.json"
    
    # Error Handling Schemas
    @property
    def data_error_config(self) -> Path:
        """Data error configuration schema."""
        return self._config_dir / "data_error_config.json"
    
    # Utility Methods
    def get_schema_path(self, schema_name: str) -> Path:
        """
        Get schema path by name.
        
        Args:
            schema_name: Name of the schema file (without extension)
            
        Returns:
            Full path to the schema file
        """
        return self._config_dir / f"{schema_name}.json"
    
    def exists(self, schema_name: str) -> bool:
        """
        Check if a schema file exists.
        
        Args:
            schema_name: Name of the schema file (without extension)
            
        Returns:
            True if file exists, False otherwise
        """
        return self.get_schema_path(schema_name).exists()
    
    def list_available_schemas(self) -> Dict[str, Path]:
        """
        List all available schema files.
        
        Returns:
            Dictionary mapping schema names to their paths
        """
        schemas = {}
        if self._config_dir.exists():
            for schema_file in self._config_dir.glob("*.json"):
                schema_name = schema_file.stem
                schemas[schema_name] = schema_file
        return schemas
    
    def validate_required_schemas(self) -> Dict[str, bool]:
        """
        Validate that required schemas exist.
        
        Returns:
            Dictionary mapping schema names to existence status
        """
        required_schemas = [
            "project_setup",
            "project_config", 
            "project_setup_base",
            "dcc_register_config",
            "project_code_schema",
            "global_parameters"
        ]
        
        return {name: self.exists(name) for name in required_schemas}


def get_schema_paths(base_path: Path) -> SchemaPaths:
    """
    Get SchemaPaths instance for the given base path.
    
    Args:
        base_path: Project base path
        
    Returns:
        SchemaPaths instance
    """
    return SchemaPaths(base_path)


# Legacy compatibility functions (to be phased out)
def get_schema_path(base_path: Path) -> Path:
    """Legacy function - use SchemaPaths.project_setup_schema instead."""
    return get_schema_paths(base_path).project_setup_schema


def default_schema_path(base_path: Path) -> Path:
    """Legacy function - use SchemaPaths.dcc_register_config instead.""" 
    return get_schema_paths(base_path).dcc_register_config
