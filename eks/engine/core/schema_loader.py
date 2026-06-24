"""
Schema Loader for EKS - Handles loading and validation of base, setup, and config schemas.
"""
import importlib
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
        self.doc_base_schema: Dict[str, Any] = {}
        self.doc_setup_schema: Dict[str, Any] = {}
        self.doc_config: Dict[str, Any] = {}
        self.error_base_schema: Dict[str, Any] = {}
        self.error_setup_schema: Dict[str, Any] = {}
        self.error_config: Dict[str, Any] = {}
        self.message_base_schema: Dict[str, Any] = {}
        self.message_setup_schema: Dict[str, Any] = {}
        self.message_config: Dict[str, Any] = {}
        self.project_rules_config: Dict[str, Any] = {}

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
        self.doc_base_schema = self._load_json("eks_doc_base_schema.json")
        self.doc_setup_schema = self._load_json("eks_doc_setup_schema.json")
        self.doc_config = self._load_json("eks_doc_config.json")
        self.error_base_schema = self._load_json("eks_error_code_base.json")
        self.error_setup_schema = self._load_json("eks_error_setup_schema.json")
        self.error_config = self._load_json("eks_error_config.json")
        self.message_base_schema = self._load_json("eks_message_base.json")
        self.message_setup_schema = self._load_json("eks_message_setup_schema.json")
        self.message_config = self._load_json("eks_message_config.json")

        self.project_rules_config = self._load_json("eks_project_rules_config.json")

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
        self._validate_doc_config()
        self._validate_doc_registries()
        self._validate_error_config()
        self._validate_message_config()
        self._validate_project_rules()
        return self.config

    def _load_json(self, filename: str) -> Dict[str, Any]:
        path = self.config_dir / "schemas" / filename
        if not path.exists():
            path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found in {self.config_dir} or its schemas/ subdirectory: {filename}")
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
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)

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

    def _validate_doc_config(self) -> None:
        """Validates self.doc_config against self.doc_setup_schema using doc_base_schema for $ref resolution."""
        resources = {}
        if self.doc_base_schema.get("$id"):
            resources[self.doc_base_schema["$id"]] = DRAFT7.create_resource(self.doc_base_schema)
        if self.doc_setup_schema.get("$id"):
            resources[self.doc_setup_schema["$id"]] = DRAFT7.create_resource(self.doc_setup_schema)
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.doc_config, schema=self.doc_setup_schema, registry=registry)

    def _validate_doc_registries(self) -> None:
        """Validates doc config cross-registries:
        1. document_type_registry: ontology_class must exist in ontology config.
        2. file_type_registry: parser_class must be importable.
        3. element_type_registry: element_type must be valid.
        4. element_expectations keys must match document_type_registry codes.
        """
        valid_element_types = {"cover_page", "revision_table", "section", "table", "image", "link", "legend", "note"}

        doc_type_reg = self.doc_config.get("document_type_registry", [])
        file_type_reg = self.doc_config.get("file_type_registry", [])
        elem_type_reg = self.doc_config.get("element_type_registry", [])
        elem_expect = self.doc_config.get("element_expectations", {})

        # 1. Validate document_type_registry ontology_class
        doc_type_codes = set()
        for entry in doc_type_reg:
            code = entry.get("code")
            doc_type_codes.add(code)
            ontology_class = entry.get("ontology_class", "")
            if ontology_class not in self.ontology_class_names:
                raise ValueError(
                    f"Document type '{code}' references undefined ontology class: "
                    f"'{ontology_class}'. Available: {sorted(self.ontology_class_names)}"
                )

        # 2. Validate file_type_registry parser_class is importable
        for entry in file_type_reg:
            ext = entry.get("extension")
            parser = entry.get("parser_class", "")
            try:
                module_path, class_name = parser.rsplit(".", 1)
                importlib.import_module(module_path)
            except (ValueError, ImportError, ModuleNotFoundError) as e:
                raise ValueError(
                    f"File type '{ext}' has unimportable parser_class: '{parser}'. Error: {e}"
                )

        # 3. Validate element_type_registry element_type
        for entry in elem_type_reg:
            et = entry.get("element_type", "")
            if et not in valid_element_types:
                raise ValueError(
                    f"Element type '{et}' is not a valid element type. "
                    f"Valid: {sorted(valid_element_types)}"
                )

        # 4. Validate element_expectations keys match document_type_registry codes
        for key in elem_expect:
            if key not in doc_type_codes:
                raise ValueError(
                    f"element_expectations key '{key}' does not match any document_type_registry code. "
                    f"Valid codes: {sorted(doc_type_codes)}"
                )

    def _validate_error_config(self) -> None:
        """Validates self.error_config against self.error_setup_schema using error_base_schema for $ref resolution."""
        resources = {}
        if self.error_base_schema.get("$id"):
            resources[self.error_base_schema["$id"]] = DRAFT7.create_resource(self.error_base_schema)
        if self.error_setup_schema.get("$id"):
            resources[self.error_setup_schema["$id"]] = DRAFT7.create_resource(self.error_setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.error_config, schema=self.error_setup_schema, registry=registry)

    def _validate_message_config(self) -> None:
        """Validates self.message_config against self.message_setup_schema using message_base_schema for $ref resolution."""
        resources = {}
        if self.message_base_schema.get("$id"):
            resources[self.message_base_schema["$id"]] = DRAFT7.create_resource(self.message_base_schema)
        if self.message_setup_schema.get("$id"):
            resources[self.message_setup_schema["$id"]] = DRAFT7.create_resource(self.message_setup_schema)
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        validate(instance=self.message_config, schema=self.message_setup_schema, registry=registry)

    def _validate_project_rules(self) -> None:
        """Validates self.project_rules_config against project_rules_def from base schema.

        Checks:
        1. Each project entry conforms to project_rules_def (allowed_disciplines required).
        2. fragment_required_fields (if present) references valid fragment names from asset base schema.
        3. Fragment field names in fragment_required_fields correspond to actual fragment properties.
        """
        if not self.project_rules_config:
            return

        resources = {}
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        base_def = self.base_schema.get("definitions", {}).get("project_rules_def", {})
        project_rules_wrapper = self.project_rules_config.get("project_rules", {})
        for project_id, entry in project_rules_wrapper.items():
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Project '{project_id}' entry in project_rules is not an object."
                )

            fragment_overrides = entry.get("fragment_required_fields", {})
            if not isinstance(fragment_overrides, dict):
                raise ValueError(
                    f"Project '{project_id}': fragment_required_fields must be an object."
                )

            for frag_name, field_list in fragment_overrides.items():
                if not isinstance(field_list, list) or len(field_list) < 1:
                    raise ValueError(
                        f"Project '{project_id}': fragment_required_fields['{frag_name}'] must be a non-empty array."
                    )

                frag_def = self.asset_base_schema.get("definitions", {}).get(frag_name)
                if frag_def is None:
                    raise ValueError(
                        f"Project '{project_id}': fragment_required_fields references undefined fragment '{frag_name}'. "
                        f"Valid: {sorted(self.asset_base_schema.get('definitions', {}).keys())}"
                    )

                frag_props = frag_def.get("properties", {})
                for field in field_list:
                    if field not in frag_props:
                        raise ValueError(
                            f"Project '{project_id}': fragment_required_fields['{frag_name}'] contains "
                            f"unknown field '{field}'. Valid: {sorted(frag_props.keys())}"
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
