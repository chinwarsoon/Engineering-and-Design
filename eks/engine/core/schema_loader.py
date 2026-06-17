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
        self.asset_base_schema: Dict[str, Any] = {}
        self.asset_setup_schema: Dict[str, Any] = {}
        self.asset_config: Dict[str, Any] = {}
        self.ontology_base_schema: Dict[str, Any] = {}
        self.ontology_setup_schema: Dict[str, Any] = {}
        self.ontology: Dict[str, Any] = {}
        self.ontology_tag_type_map: Dict[str, str] = {}
        self.ontology_tag_type_alias_map: Dict[str, str] = {}
        self.ontology_class_names: set[str] = set()
        self.asset_ontology_class_map: Dict[str, str] = {}

    def load_all(self) -> Dict[str, Any]:
        """
        Loads all schema files, ontology config, and validates them.
        Returns the validated project config dictionary.
        """
        self.base_schema = self._load_json("eks_base_schema.json")
        self.setup_schema = self._load_json("eks_setup_schema.json")
        self.config = self._load_json("eks_config.json")
        self.asset_base_schema = self._load_json("eks_asset_base_schema.json")
        self.asset_setup_schema = self._load_json("eks_asset_setup_schema.json")
        self.asset_config = self._load_json("eks_asset_config.json")
        self.ontology_base_schema = self._load_json("eks_ontology_base_schema.json")
        self.ontology_setup_schema = self._load_json("eks_ontology_setup_schema.json")
        self.ontology = self._load_json("eks_ontology_config.json")

        self.asset_ontology_class_map = {
            self._normalize_tag_type(k): v
            for k, v in self.asset_config.get("ontology_class_map", {}).items()
            if isinstance(k, str) and isinstance(v, str)
        }

        self._validate_config()
        self._validate_asset_config()
        self._validate_ontology()
        self._build_ontology_index()
        self._validate_ontology_fragments()
        self._validate_ontology_class_map()
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

    def _validate_ontology(self) -> None:
        """
        Validates self.ontology against self.ontology_setup_schema.
        """
        resources = {}
        if self.ontology_base_schema.get("$id"):
            resources[self.ontology_base_schema["$id"]] = DRAFT7.create_resource(self.ontology_base_schema)
        if self.ontology_setup_schema.get("$id"):
            resources[self.ontology_setup_schema["$id"]] = DRAFT7.create_resource(self.ontology_setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.ontology, schema=self.ontology_setup_schema, registry=registry)

    def _validate_asset_config(self) -> None:
        """Validates self.asset_config against self.asset_setup_schema using asset_base_schema for $ref resolution."""
        resources = {}
        if self.asset_base_schema.get("$id"):
            resources[self.asset_base_schema["$id"]] = DRAFT7.create_resource(self.asset_base_schema)
        if self.asset_setup_schema.get("$id"):
            resources[self.asset_setup_schema["$id"]] = DRAFT7.create_resource(self.asset_setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.asset_config, schema=self.asset_setup_schema, registry=registry)

    def _normalize_tag_type(self, tag_type: str) -> str:
        if not isinstance(tag_type, str):
            return tag_type
        return tag_type.strip().upper()

    def _build_ontology_index(self) -> None:
        """Builds canonical and alias tag type indexes for ontology classes."""
        self.ontology_tag_type_map = {}
        self.ontology_tag_type_alias_map = {}
        self.ontology_class_names = set()

        for class_entry in self.ontology.get("classes", []):
            name = class_entry.get("name")
            if not name:
                continue
            self.ontology_class_names.add(name)

            mapping = class_entry.get("tag_type_mapping")
            if mapping:
                normalized = self._normalize_tag_type(mapping)
                existing = self.ontology_tag_type_map.get(normalized)
                if existing and existing != name:
                    raise ValueError(
                        f"Duplicate ontology tag_type_mapping '{normalized}' for classes '{existing}' and '{name}'."
                    )
                self.ontology_tag_type_map[normalized] = name

            for alias in class_entry.get("tag_type_aliases", []):
                normalized = self._normalize_tag_type(alias)
                existing = self.ontology_tag_type_alias_map.get(normalized)
                if existing and existing != name:
                    raise ValueError(
                        f"Duplicate ontology tag_type_alias '{normalized}' for classes '{existing}' and '{name}'."
                    )
                if normalized in self.ontology_tag_type_map and self.ontology_tag_type_map[normalized] != name:
                    raise ValueError(
                        f"Alias '{normalized}' conflicts with existing tag_type_mapping for class '{self.ontology_tag_type_map[normalized]}'."
                    )
                self.ontology_tag_type_alias_map[normalized] = name

    def _validate_ontology_fragments(self) -> None:
        """Validates that all fragment names in ontology exist in asset_base_schema."""
        base_frags = set(self.asset_base_schema.get("definitions", {}).keys())
        for class_entry in self.ontology.get("classes", []):
            for frag in class_entry.get("fragments", []):
                if frag not in base_frags:
                    raise ValueError(
                        f"Ontology class '{class_entry['name']}' references undefined fragment: {frag}"
                    )

    def _validate_ontology_class_map(self) -> None:
        """Validates that config ontology_class_map references real ontology classes."""
        for target_class in self.asset_ontology_class_map.values():
            if target_class not in self.ontology_class_names:
                raise ValueError(
                    f"ontology_class_map references undefined ontology class: {target_class}"
                )

    def resolve_ontology_class(self, tag_type: str) -> Optional[str]:
        """Resolves a TAG_TYPE or alias to an ontology class name."""
        normalized = self._normalize_tag_type(tag_type)
        if not isinstance(normalized, str):
            return None

        if normalized in self.asset_ontology_class_map:
            return self.asset_ontology_class_map[normalized]
        if normalized in self.ontology_tag_type_map:
            return self.ontology_tag_type_map[normalized]
        if normalized in self.ontology_tag_type_alias_map:
            return self.ontology_tag_type_alias_map[normalized]
        return None


def load_eks_config(config_dir: str | Path = "config") -> Dict[str, Any]:
    """Helper function to quickly load and validate EKS config."""
    loader = SchemaLoader(config_dir)
    return loader.load_all()
