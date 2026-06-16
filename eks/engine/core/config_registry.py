"""
SSOT Config Registry for EKS - Centralized access to global parameters.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
from .schema_loader import load_eks_config

class ConfigRegistry:
    """
    Singleton registry for EKS configuration.
    Ensures that all modules access global parameters from the same validated source.
    """
    _instance: Optional['ConfigRegistry'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls, config_dir: str | Path = "eks/config"):
        if cls._instance is None:
            cls._instance = super(ConfigRegistry, cls).__new__(cls)
            # Try eks/config if config doesn't exist (handle root execution)
            if not Path(config_dir).exists() and Path("config").exists():
                 config_dir = "config"
            elif not Path(config_dir).exists():
                 # Last ditch effort for common dev layouts
                 pass 
            cls._instance._config = load_eks_config(config_dir)
        return cls._instance

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieves a nested value using dot notation (e.g., 'registry.type' or 'discipline_registry.P123').
        """
        parts = key_path.split(".")
        val = self._config
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val

    # Helper methods for project-scoped data
    def get_project_disciplines(self, project_id: str) -> List[Dict[str, str]]:
        return self.get(f"discipline_registry.{project_id}", [])

    def get_project_rules(self, project_id: str) -> Dict[str, Any]:
        return self.get(f"project_rules_registry.{project_id}", {})

    # Common accessors for frequently used paths/settings
    @property
    def data_dir(self) -> Path:
        return Path(self.get("global_paths.data_dir", "data"))

    @property
    def output_dir(self) -> Path:
        return Path(self.get("global_paths.output_dir", "output"))

    @property
    def registry_settings(self) -> Dict[str, Any]:
        return self.get("registry", {})

    @property
    def logging_settings(self) -> Dict[str, Any]:
        return self.get("logging", {})
