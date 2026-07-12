"""
SSOT Config Registry for EKS - Centralized access to global parameters.

Revision: 0.2
Date: 2026-07-11
Author: Codex
Summary: Add schema-driven system parameter accessor for T1.97/I088.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
from .schema_loader import SchemaLoader, load_eks_config
from common.library.config import get_system_param
from common.library.paths import resolve_paths, ResolvedPaths

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
            loader = SchemaLoader(config_dir)
            cls._instance._config = loader.load_all()
            cls._instance._loader = loader
        return cls._instance

    def _load_ref(self, ref_obj: Dict[str, str]) -> Dict[str, Any]:
        """Resolve a {'$ref': uri} dict by loading the referenced file."""
        uri = ref_obj.get("$ref", "")
        filename = uri.rstrip("/").split("/")[-1]
        for d in [self._loader.config_dir / "schemas", self._loader.config_dir]:
            path = d / filename
            if path.exists():
                with open(str(path), "r", encoding="utf-8") as f:
                    return json.load(f)
        return ref_obj

    @property
    def ontology(self) -> Dict[str, Any]:
        return getattr(self, '_loader', None).ontology if getattr(self, '_loader', None) else {}

    @property
    def asset_config(self) -> Dict[str, Any]:
        return getattr(self, '_loader', None).asset_config if getattr(self, '_loader', None) else {}

    def resolve_ontology_class(self, tag_type: str) -> Optional[str]:
        loader = getattr(self, '_loader', None)
        if loader is None:
            return None
        return loader.resolve_ontology_class(tag_type)

    @property
    def asset_ontology_class_map(self) -> Dict[str, str]:
        loader = getattr(self, '_loader', None)
        if loader is None:
            return {}
        return loader.asset_ontology_class_map

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieves a nested value using dot notation (e.g., 'registry.type' or 'discipline_registry.131101').
        Resolves {'$ref': uri} entries on-the-fly.
        """
        parts = key_path.split(".")
        val = self._config
        for part in parts:
            if isinstance(val, dict) and "$ref" in val:
                val = self._load_ref(val)
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val

    # Helper methods for project-scoped data
    def get_project_disciplines(self, project_id: str) -> List[Dict[str, str]]:
        rules = self.get(f"discipline_registry", {})
        if "$ref" in rules:
            rules = self._load_ref(rules)
        disciplines = rules.get("disciplines", [])
        return [d for d in disciplines if d.get("code") == project_id] if project_id else disciplines

    def get_project_rules(self, project_id: str) -> Dict[str, Any]:
        rules = self.get(f"project_rules_registry", {})
        if "$ref" in rules:
            rules = self._load_ref(rules)
        return rules.get("project_rules", {}).get(project_id, {})

    def get_fragment_required_fields(self, project_id: str) -> Dict[str, list[str]]:
        """
        Returns the per-fragment required field map for a given project.
        Shape-only definitions in asset base schema carry no required constraints;
        this is the SSOT for mandatory fragment fields.
        Returns an empty dict if no overrides are defined.
        """
        rules = self.get_project_rules(project_id)
        return rules.get("fragment_required_fields", {})

    def resolve_required_fields(self, project_id: str, fragment_name: str) -> list[str]:
        """
        Resolves the required field list for a specific fragment under a given project.
        Falls back to an empty list (no required constraints) when undefined.
        """
        fields = self.get_fragment_required_fields(project_id)
        return fields.get(fragment_name, [])

    # Common accessors for frequently used paths/settings
    @property
    def _resolved_paths(self) -> ResolvedPaths:
        """Canonical, schema-driven paths resolved via the universal PathResolver (T1.98a/I089)."""
        return resolve_paths(None, self._config)

    @property
    def data_dir(self) -> Path:
        return Path(self._resolved_paths.data_dir)

    @property
    def output_dir(self) -> Path:
        return Path(self._resolved_paths.output_dir)

    @property
    def archive_dir(self) -> Path:
        return Path(self._resolved_paths.archive_dir)

    @property
    def config_dir(self) -> Path:
        return Path(self._resolved_paths.config_dir)

    @property
    def log_dir(self) -> Path:
        return Path(self._resolved_paths.log_dir)

    @property
    def schema_dir(self) -> Path:
        return Path(self._resolved_paths.schema_dir)

    @property
    def eks_root(self) -> Path:
        return Path(self._resolved_paths.eks_root) if self._resolved_paths.eks_root else Path("")

    @property
    def registry_settings(self) -> Dict[str, Any]:
        return self.get("registry", {})

    @property
    def logging_settings(self) -> Dict[str, Any]:
        return self.get("logging", {})

    def get_system_param(self, key: str, default: Any = None) -> Any:
        """
        Return a runtime behavior parameter from ``system_parameters``.

        Parameters:
            key: Canonical system parameter name.
            default: Value returned when the parameter is not configured.

        Returns:
            Configured system parameter value or ``default``.
        """
        return get_system_param(self._config, key, default)
