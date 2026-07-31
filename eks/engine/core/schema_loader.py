"""
Schema Loader for EKS - Handles loading and validation of base, setup, and config schemas.

Uses config-driven discovery (T1.96): reads schema_files + discovery_rules from
eks_config.json instead of hardcoding 22 filenames.

Revision: 1.3.0 — T1.196 (I265/I267/I268): removed eks_project_rules_config from
           _STEM_TO_ATTR and _validate_project_rules() — eks_project_rules_config.json
           retired (I267). Removed dead revision_validation backward-compat injection
           (I268 — no consumers; RevisionManager migrated to slices in T1.194).
1.2.0 — T1.192: registered eks_project_definition_config in _STEM_TO_ATTR;
           added _validate_project_definition() validation stage;
           added project_definition $ref resolution in _extract() for backward compat.
           T1.191: inject filename_patterns and revision_validation from
           project_definition_config into doc_config for backward compat.
1.1.0: T1.159 (I256): registered eks_project_code_schema in _STEM_TO_ATTR;
"""
import importlib
import json
from pathlib import Path
from typing import Any, Dict, Optional
from jsonschema import validate
from referencing import Registry
from referencing.jsonschema import DRAFT7

from common.library.loader import discover_schema_files, discover_schema_files_tier3, find_schema_file


_STEM_TO_ATTR = {
    "eks_base_schema": "base_schema",
    "eks_setup_schema": "setup_schema",
    "eks_config": "config",
    "eks_asset_base_schema": "asset_base_schema",
    "eks_asset_setup_schema": "asset_setup_schema",
    "eks_asset_config": "asset_config",
    "eks_ontology_base_schema": "ontology_base_schema",
    "eks_ontology_setup_schema": "ontology_setup_schema",
    "eks_ontology_config": "ontology",
    "eks_doc_base_schema": "doc_base_schema",
    "eks_doc_setup_schema": "doc_setup_schema",
    "eks_doc_config": "doc_config",
    "eks_document_type_schema": "document_type_schema",
    "eks_project_code_schema": "project_code_schema",
    "eks_department_schema": "department_schema",
    "eks_discipline_schema": "discipline_schema",
    "eks_facility_schema": "facility_schema",
    "eks_error_code_base": "error_base_schema",
    "eks_error_setup_schema": "error_setup_schema",
    "eks_error_config": "error_config",
    "eks_message_base": "message_base_schema",
    "eks_message_setup_schema": "message_setup_schema",
    "eks_message_config": "message_config",
    "eks_project_definition_config": "project_definition_config",
}

_BOOTSTRAP_STEMS = {"eks_base_schema", "eks_setup_schema", "eks_config"}


class SchemaLoader:
    """
    Orchestrates the loading and validation of EKS canonical schemas.

    Schemas are loaded from two sources in order:
      1. ``schema_files`` in eks_config.json (explicit, required)
      2. ``discovery_rules`` glob patterns (auto-discovered, optional)
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
        self.document_type_schema: Dict[str, Any] = {}
        self.project_code_schema: Dict[str, Any] = {}
        self.department_schema: Dict[str, Any] = {}
        self.discipline_schema: Dict[str, Any] = {}
        self.facility_schema: Dict[str, Any] = {}
        self.project_definition_config: Dict[str, Any] = {}
        self._extra_schemas: Dict[str, Dict[str, Any]] = {}

        self._search_dirs = [self.config_dir / "schemas", self.config_dir]

    def _project_root(self) -> Path:
        """Compute project root from config_dir."""
        root = self.config_dir.parent.parent  # config/ -> eks/ -> project_root
        if not root.exists():
            root = self.config_dir
        return root

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file, searching registered directories.

        If filename is a path relative to project root (e.g.
        ``eks/config/schemas/eks_base_schema.json``), resolve from
        project root first.  Otherwise search _search_dirs in order.
        """
        path = Path(filename)
        if not path.is_absolute() and len(path.parts) > 2:
            root_candidate = self._project_root() / filename
            if root_candidate.exists():
                with open(root_candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
        for d in self._search_dirs:
            candidate = d / filename
            if candidate.exists():
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
        raise FileNotFoundError(
            f"Schema file not found: {filename}. "
            f"Searched: {self._project_root()}, {self._search_dirs}"
        )

    def load_all(self) -> Dict[str, Any]:
        """Loads all schema files, ontology config, and validates them.

        Delegates to 4 stage methods: _discover → _load → _validate → _extract.
        """
        registry = self._discover()
        self._load(registry)
        self._validate()
        self._extract()
        return self.config

    def _discover(self) -> Dict[str, Dict[str, Any]]:
        """Stage 1: Bootstrap load + config-driven schema discovery with Tier 3 fallback.

        Loads core bootstrap schemas (base, setup, config), validates config,
        then runs discovery rules from config.  Falls back to Tier 3 scan
        for auxiliary schemas not matched by any glob pattern.
        """
        self.base_schema = self._load_json("eks_base_schema.json")
        self.setup_schema = self._load_json("eks_setup_schema.json")
        self.config = self._load_json("eks_config.json")

        # Resolve project_definition $ref before validation so the resolved
        # data satisfies the object schema type check.
        pd_ref = self.config.get("project_definition", {}).get("$ref")
        if pd_ref:
            ref_path = pd_ref.split("/")[-1]
            try:
                pd_file = self._load_json(ref_path)
                pd_data = pd_file.get("project_definition", pd_file)
                self.config["project_definition"] = pd_data
            except (FileNotFoundError, json.JSONDecodeError):
                raise ValueError(
                    f"project_definition $ref target not loadable: {pd_ref}"
                )

        self._validate_config()

        project_root = self._project_root()
        registry = discover_schema_files(self.config, project_root)

        # Tier 3 fallback: scan for known stems not yet discovered
        all_stems = list(_STEM_TO_ATTR.keys())
        tier3_entries = discover_schema_files_tier3(all_stems, self._search_dirs, registry)
        registry.update(tier3_entries)

        return registry

    def _load(self, registry: Dict[str, Dict[str, Any]]) -> None:
        """Stage 2: Load all non-bootstrap schemas from the discovered registry."""
        for stem, meta in registry.items():
            if stem in _BOOTSTRAP_STEMS:
                continue
            if stem not in _STEM_TO_ATTR:
                self._extra_schemas[stem] = meta
                continue
            attr_name = _STEM_TO_ATTR[stem]
            if getattr(self, attr_name):
                continue
            setattr(self, attr_name, self._load_json(meta["filename"]))

    def _validate(self) -> None:
        """Stage 3: Validate all loaded schemas and cross-registries."""
        self._validate_asset_config()
        self._validate_ontology()
        self._build_ontology_index()
        self._validate_ontology_fragments()
        self._validate_ontology_class_map()
        self._validate_doc_config()
        self._validate_doc_registries()
        self._validate_error_config()
        self._validate_message_config()
        self._validate_project_definition()

    def _extract(self) -> None:
        """Stage 4: Build runtime indexes and derived data from loaded schemas.

        This stage produces raw validated schema objects only — no
        RuntimeProjectDefinition assembly (contract boundary).
        RuntimeProjectDefinition is constructed by ProjectDefinitionResolver
        during pipeline bootstrap.
        """
        self.doc_config["project_code_titles"] = {
            p["code"]: p["description"]
            for p in self.project_code_schema.get("projects", [])
            if isinstance(p, dict) and "code" in p and "description" in p
        }

        # Functional reconstruction (T1.191): build filename_patterns from the
        # Project Definition so FileScanner / FilenameParser keep matching.
        # NOTE: revision_validation reconstruction removed in T1.196 (I268) — dead
        # (RevisionManager consumes runtime slices since T1.194).
        filename_profiles = self.doc_config.get("filename_profiles", {})
        if self.project_definition_config and filename_profiles:
            pd_data = self.project_definition_config.get("project_definition", {})
            injected_patterns = {}
            for proj_code, proj_entry in pd_data.items():
                if not isinstance(proj_entry, dict):
                    continue
                dp = proj_entry.get("document_profile", {})
                profile_name = dp.get("filename_pattern", "")
                if profile_name in filename_profiles:
                    injected_patterns[proj_code] = filename_profiles[profile_name]
            if injected_patterns:
                injected_patterns["*"] = filename_profiles.get("default", {})
                self.doc_config["filename_patterns"] = injected_patterns

        self.asset_ontology_class_map = {
            self._normalize_tag_type(k): v
            for k, v in self.asset_config.get("ontology_class_map", {}).items()
            if isinstance(k, str) and isinstance(v, str)
        }

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

    def _validate_project_definition(self) -> None:
        """Validate project_definition entries against setup schema project_definition_def.

        Each entry in project_definition must have required fields (project_identity,
        document_profile). Validates using jsonschema with base+setup $ref resolution.
        Silently returns if project_definition_config is not loaded.
        """
        if not self.project_definition_config:
            return
        resources = {}
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)
        if self.setup_schema.get("$id"):
            resources[self.setup_schema["$id"]] = DRAFT7.create_resource(self.setup_schema)
        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )
        pd_def = self.setup_schema.get("definitions", {}).get("project_definition_entry_def", {})
        if not pd_def:
            return
        pd_data = self.project_definition_config.get("project_definition", {})
        for proj_code, entry in pd_data.items():
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Project '{proj_code}' project_definition entry is not an object."
                )
            validate(instance=entry, schema=pd_def, registry=registry)

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
