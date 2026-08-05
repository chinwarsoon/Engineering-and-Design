"""
Schema Loader for EKS - Handles loading and validation of base, setup, and config schemas.

Uses config-driven discovery (T1.96): reads schema_files + discovery_rules from
eks_config.json instead of hardcoding 22 filenames.

Revision: 1.4.0 — I282 (T1.228): migrated document-type projection + validation
           from the concept layer to the class/type/family carrier
           (eks_document_type_schema.json v2.1.0). _derive_doc_type_projection()
           resolves label/ontology_class via binding.class_id; _validate_doc_registries()
           cross-references document_classes/document_types/document_family/
           project_document_types; added class-based helpers
           get_documents_by_class / get_documents_by_family / get_class_ancestry.
1.3.0 — T1.196 (I265/I267/I268): removed eks_project_rules_config from
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
from typing import Any, Dict, List, Optional
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
        "eks_processing_config": "processing_config",
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
        self.processing_config: Dict[str, Any] = {}
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

        # I279 (T1.213): derive flat document-type projections from the
        # three-section carrier so consumers (FileScanner, FilenameParser,
        # pipeline_orchestrator, project_definition, health_scorer) read the
        # single-source schema instead of a committed config array.
        self._derive_doc_type_projection()

    def _validate(self) -> None:
        """Stage 3: Validate all loaded schemas and cross-registries."""
        self._validate_asset_config()
        self._validate_ontology()
        self._build_ontology_index()
        self._validate_ontology_fragments()
        self._validate_ontology_class_map()
        self._validate_doc_config()
        self._validate_doc_registries()
        self._validate_processing_config()
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

    def _derive_doc_type_projection(self) -> None:
        """Derive flat document-type projections from the four-section carrier.

        I279 (T1.213) / I282 (T1.228): the carrier
        (eks_document_type_schema.json v2.1.0) is the single runtime source.
        Runtime consumers expect a flat ``document_type_registry``
        (code → label/ontology_class/class_id/expected_file_types/format_category map)
        plus the template registry. We project these into ``doc_config`` at load
        time so no committed flat array (the old dead-duplicate SSOT) survives.
        I282: the concept layer is removed (D4) — the flat registry resolves
        label/ontology_class from the carrier ``document_classes`` registry via
        the binding's ``class_id``.
        """
        classes = self.document_type_schema.get("document_classes", [])
        bindings = self.document_type_schema.get("project_document_types", {})
        templates = self.document_type_schema.get("document_templates", {})

        # class_id lookup for label / ontology_class resolution
        class_by_id = {c.get("class_id"): c for c in classes}

        # Build flat document_type_registry (union across all project bindings).
        # A local_code may appear under multiple projects; first wins.
        flat = []
        seen_codes = set()
        for project_code, binding_list in sorted(bindings.items()):
            for entry in binding_list:
                local_code = entry.get("local_code")
                if local_code in seen_codes:
                    continue
                seen_codes.add(local_code)
                class_entry = class_by_id.get(entry.get("class_id"), {})
                flat.append({
                    "code": local_code,
                    "label": class_entry.get("label", local_code),
                    "description": "Projected from eks_document_type_schema.json#/project_document_types (I279)",
                    "ontology_class": class_entry.get("ontology_class", ""),
                    "class_id": entry.get("class_id"),
                    "template": entry.get("template"),
                    "format_category": entry.get("format_category", "print"),
                    "native_source": entry.get("native_source", ""),
                    "expected_file_types": entry.get("expected_file_types", []),
                    # I276 (T1.206): default parsing profile id for two-axis routing
                    "default_parsing_profile": entry.get("default_parsing_profile", ""),
                })
        self.doc_config["document_type_registry"] = flat

        # Template registry projection = the carrier document_templates section.
        self.doc_config["document_templates"] = templates

        # element_expectations projection (backward-compatible shape) derived
        # from document_templates so legacy consumers of cover_type/threshold
        # keep working without a second SSOT.
        expect = {}
        for template_id, tpl in templates.items():
            expect[template_id] = {
                "expected_elements": tpl.get("expected_elements", []),
                "threshold": tpl.get("threshold", 0),
                "cover_type": tpl.get("cover_type", "C"),
            }
        self.doc_config["element_expectations"] = expect

        # document_type_schema_ref marker (I279 T1.213)
        self.doc_config["document_type_schema_ref"] = (
            self.document_type_schema.get("$id", "https://eks.engineering/schemas/eks_document_type_schema.json")
        )

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

    def _validate_processing_config(self) -> None:
        """Validates self.processing_config profile sections against the core setup schema.

        I281 (T1.224): eks_processing_config.json holds the VALUES for all 11
        processing profile types (SSOT §9/§16). Each top-level section
        ({type}_profiles) is validated against the corresponding
        processing_profiles.properties.{type}_profiles sub-schema in
        eks_setup_schema.json, whose per-type additionalProperties $ref the
        core eks_base_schema.json profile defs. The full setup schema is NOT
        applied — the processing config is a profile-values-only file and does
        not carry the core config sections.
        """
        resources = {}
        if self.base_schema.get("$id"):
            resources[self.base_schema["$id"]] = DRAFT7.create_resource(self.base_schema)
        if self.setup_schema.get("$id"):
            resources[self.setup_schema["$id"]] = DRAFT7.create_resource(self.setup_schema)
        # extraction_profile_def.supported_extensions $refs the doc-base
        # file_type_code def — register doc schemas for ref resolution (I281).
        if self.doc_base_schema.get("$id"):
            resources[self.doc_base_schema["$id"]] = DRAFT7.create_resource(self.doc_base_schema)
        if self.doc_setup_schema.get("$id"):
            resources[self.doc_setup_schema["$id"]] = DRAFT7.create_resource(self.doc_setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        section_schemas = (
            (self.setup_schema.get("properties", {})
             .get("processing_profiles", {})
             .get("properties", {}))
        )
        for section_key, section_value in self.processing_config.items():
            if section_key.startswith("$") or section_key in ("version", "title", "description"):
                continue
            section_schema = section_schemas.get(section_key)
            if section_schema is None:
                raise ValueError(
                    f"eks_processing_config.json has unknown section '{section_key}' — "
                    f"not declared in eks_setup_schema.json#/properties/processing_profiles"
                )
            validate(instance=section_value, schema=section_schema, registry=registry)

    def _validate_doc_registries(self) -> None:
        """Validates doc config cross-registries.

        I279 (T1.213) / I282 (T1.228): document_type data now sources from the
        four-section carrier (eks_document_type_schema.json v2.1.0), not a flat
        registry array. Validation cross-checks the carrier sections
        (document_classes / document_types / document_family /
        project_document_types / document_templates) against ontology and
        element types. The flat project_document_type view is derived at load
        time in _derive_doc_type_projection() and injected into doc_config.
        """
        valid_element_types = {"cover_page", "revision_table", "section", "table", "image", "link", "legend", "note"}

        file_type_reg = self.doc_config.get("file_type_registry", [])
        elem_type_reg = self.doc_config.get("element_type_registry", [])

        # I282: carrier sections — class/family/type registries plus bindings.
        classes = self.document_type_schema.get("document_classes", [])
        families = self.document_type_schema.get("document_family", [])
        types = self.document_type_schema.get("document_types", [])
        bindings = self.document_type_schema.get("project_document_types", {})
        templates = self.document_type_schema.get("document_templates", {})
        class_by_id = {c.get("class_id"): c for c in classes}
        family_by_id = {f.get("family_id"): f for f in families}
        type_by_id = {t.get("type_id"): t for t in types}
        local_codes = set()

        # 1a. Validate classes: unique class_id; ontology_class must exist in ontology config.
        for c in classes:
            cid = c.get("class_id")
            if not cid:
                raise ValueError("Document class entry missing 'class_id'.")
            ontology_class = c.get("ontology_class", "")
            if ontology_class and ontology_class not in self.ontology_class_names:
                raise ValueError(
                    f"Document class '{cid}' references undefined ontology class: "
                    f"'{ontology_class}'. Available: {sorted(self.ontology_class_names)}"
                )
        if len({c.get("class_id") for c in classes}) != len(classes):
            raise ValueError("Document classes contain duplicate 'class_id' values.")

        # 1a2. Validate families: unique family_id; discipline label present.
        for f in families:
            fid = f.get("family_id")
            if not fid:
                raise ValueError("Document family entry missing 'family_id'.")
            if not f.get("discipline"):
                raise ValueError(f"Document family '{fid}' is missing its 'discipline' label.")
        if len({f.get("family_id") for f in families}) != len(families):
            raise ValueError("Document families contain duplicate 'family_id' values.")

        # 1a3. Validate types: unique type_id; class_id exists; family_id exists-or-null.
        for t in types:
            tid = t.get("type_id")
            if not tid:
                raise ValueError("Document type entry missing 'type_id'.")
            cid = t.get("class_id")
            if cid not in class_by_id:
                raise ValueError(
                    f"Document type '{tid}' references undefined class_id: "
                    f"'{cid}'. Available classes: {sorted(class_by_id)}"
                )
            fid = t.get("family_id")
            if fid is not None and fid not in family_by_id:
                raise ValueError(
                    f"Document type '{tid}' references undefined family_id: "
                    f"'{fid}'. Available families: {sorted(family_by_id)}"
                )
        if len({t.get("type_id") for t in types}) != len(types):
            raise ValueError("Document types contain duplicate 'type_id' values.")

        # 1b. Validate each project binding: class_id exists; template exists;
        #     element_type entries valid; format_category/enum valid.
        for project_code, binding_list in bindings.items():
            for entry in binding_list:
                local_code = entry.get("local_code")
                local_codes.add(local_code)
                class_id = entry.get("class_id")
                if class_id not in class_by_id:
                    raise ValueError(
                        f"Binding {project_code}/{local_code} references undefined class_id: "
                        f"'{class_id}'. Available classes: {sorted(class_by_id)}"
                    )
                template_id = entry.get("template")
                if template_id not in templates:
                    raise ValueError(
                        f"Binding {project_code}/{local_code} references undefined template: "
                        f"'{template_id}'. Available templates: {sorted(templates)}"
                    )
                if entry.get("format_category") not in ("native", "print"):
                    raise ValueError(
                        f"Binding {project_code}/{local_code} has invalid format_category: "
                        f"'{entry.get('format_category')}'. Must be 'native' or 'print'."
                    )
                for ext in entry.get("expected_file_types", []):
                    # file_type_registry is the source of truth for extensions
                    known = {ft.get("extension") for ft in file_type_reg}
                    if ext not in known:
                        raise ValueError(
                            f"Binding {project_code}/{local_code} expects unknown file type: '{ext}'. "
                            f"Known: {sorted(known)}"
                        )

        # 1b2. Cross-reference column_processing applies_to_document_types against
        #      the class registry (I282 T1.235): the base schema only checks shape
        #      (plain string), so runtime validates the referenced class exists.
        col_proc = self.doc_config.get("column_processing", {})
        col_proc_items = col_proc.values() if isinstance(col_proc, dict) else col_proc
        for col_entry in col_proc_items:
            if not isinstance(col_entry, dict):
                continue
            applies = col_entry.get("applies_to_document_types") or []
            for ref in applies:
                if ref not in class_by_id:
                    raise ValueError(
                        f"column_processing entry applies_to_document_types references undefined "
                        f"class_id: '{ref}'. Available classes: {sorted(class_by_id)}"
                    )

        # 1c. Validate template registry: cover_type enum, expected_elements valid,
        #     section/singular drift resolved (T1.213).
        for tid, tpl in templates.items():
            if tpl.get("cover_type") not in ("A", "B", "C", "D", "E"):
                raise ValueError(
                    f"Template '{tid}' has invalid cover_type: '{tpl.get('cover_type')}'"
                )
            for el in tpl.get("expected_elements", []):
                if el not in valid_element_types:
                    raise ValueError(
                        f"Template '{tid}' has invalid expected element: '{el}'. "
                        f"Valid: {sorted(valid_element_types)}"
                    )
            det = tpl.get("detection", {})
            for mec in (det.get("native"), det.get("print")):
                if mec not in ("embedded_structure", "page1_ocr"):
                    raise ValueError(
                        f"Template '{tid}' has invalid detection mechanism: '{mec}'"
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

    def _doc_class_by_id(self) -> Dict[str, Dict[str, Any]]:
        return {c.get("class_id"): c for c in self.document_type_schema.get("document_classes", [])}

    def get_documents_by_class(self, class_id: str) -> List[str]:
        """Returns the type_ids of every document type classified under ``class_id``.

        I282 (T1.228): class-based lookup into the carrier document_types
        registry — replaces the old concept-wide lookup.
        """
        return [
            t.get("type_id")
            for t in self.document_type_schema.get("document_types", [])
            if t.get("class_id") == class_id
        ]

    def get_documents_by_family(self, family_id: str) -> List[str]:
        """Returns the type_ids of every document type grouped under ``family_id``.

        I282 (T1.228): family-based lookup into the carrier document_types
        registry. Types with no family_id are never returned.
        """
        return [
            t.get("type_id")
            for t in self.document_type_schema.get("document_types", [])
            if t.get("family_id") == family_id
        ]

    def get_class_ancestry(self, class_id: str) -> List[str]:
        """Returns the ordered class chain from ``class_id`` up to the root.

        I282 (T1.228): walks the document class hierarchy (optional
        ``parent_class_id`` per class entry) from a class to the root, ordered
        top-down (class_id first). Guards against cycles (self-ref, A->B->A)
        and dangling parents. Currently every carrier class is a top-level
        root, so each class returns ``[class_id]``; the walk supports future
        nested class hierarchies.
        """
        class_by_id = self._doc_class_by_id()
        if class_id not in class_by_id:
            raise ValueError(f"Unknown document class: '{class_id}'. Available: {sorted(class_by_id)}")
        chain = []
        seen = set()
        current = class_id
        while current is not None:
            if current in seen:
                raise ValueError(f"Document class hierarchy cycle detected at '{current}'.")
            seen.add(current)
            chain.append(current)
            entry = class_by_id.get(current)
            if entry is None:
                raise ValueError(f"Document class '{current}' references an undefined parent class.")
            current = entry.get("parent_class_id")
        return chain


def load_eks_config(config_dir: str | Path = "config") -> Dict[str, Any]:
    """Helper function to quickly load and validate EKS config."""
    loader = SchemaLoader(config_dir)
    return loader.load_all()
