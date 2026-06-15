"""
Schema Loader for EKS - Handles loading and validation of base, setup, and config schemas.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate
from referencing import Registry
from referencing.jsonschema import DRAFT7

class SchemaLoader:
    """
    Orchestrates the loading and validation of EKS canonical schemas:
    1. eks_base_schema.json (Definitions)
    2. eks_setup_schema.json (Declarations)
    3. eks_config.json (Actual Values)
    """

    def __init__(self, config_dir: str | Path = "config"):
        self.config_dir = Path(config_dir)
        self.base_schema: Dict[str, Any] = {}
        self.setup_schema: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}

    def load_all(self) -> Dict[str, Any]:
        """
        Loads all three schema files and validates the config against the setup schema.
        Returns the validated config dictionary.
        """
        self.base_schema = self._load_json("eks_base_schema.json")
        self.setup_schema = self._load_json("eks_setup_schema.json")
        self.config = self._load_json("eks_config.json")

        self._validate_config()
        return self.config

    def _load_json(self, filename: str) -> Dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _validate_config(self) -> None:
        """
        Validates self.config against self.setup_schema using base_schema for $ref resolution.
        """
        resources = {}
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)
        if self.setup_schema.get("$id"):
            resources[self.setup_schema["$id"]] = DRAFT7.create_resource(self.setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.config, schema=self.setup_schema, registry=registry)

def load_eks_config(config_dir: str | Path = "config") -> Dict[str, Any]:
    """Helper function to quickly load and validate EKS config."""
    loader = SchemaLoader(config_dir)
    return loader.load_all()
