"""
ProjectDefinitionResolver — Resolves Project Definitions into immutable
RuntimeProjectConfiguration objects consumed by the EKS pipeline.

Implements Appendix L (I265):
- L.7.2  ProjectDefinitionResolver responsibilities
- L.8    RuntimeProjectConfiguration (17 domains, immutable, strongly typed)
- L.9.6  Configuration Slice Principle
- L.13   Validation requirements

Revision: 1.2.0
Date: 2026-07-31
Author: Franklin
Summary: T1.196 (I266) — fragment_required_fields exposed: resolved per project in
         _resolve_project(), carried into the AssetExtractor slice via
         AssetsDomain.resolved, and validation_report schema_versions now sourced
         from the config file version (compatibility block removed in T1.196).
1.1.0 (2026-07-31, T1.195): Configuration Validation implementation (approved V1/V2/V3):
         V1 failure semantics (system errors via resolver.errors hard-fail,
         data errors via new resolver.data_errors never fail); V2 capability-
         driven L.13.6 consistency via exact-key profile lookup + generic
         _evaluate_capability_compat() (no hardcoded compatibility matrix);
         V3 structured error codes (S-C-S-0901..0904 system,
         P1-C-V-0001..0003 data). Adds per-category validators for L.13.3
         completeness, L.13.4/13.5 profile+environment refs, L.13.7 metadata
         policy, L.13.8 construction, L.13.9 duplicates, L.13.10 unused
         profiles, L.13.11 runtime modules; extends validation_report to
         L.13.12 content.
1.0.0 (2026-07-31, T1.193): Initial implementation of ProjectDefinitionResolver,
         RuntimeProjectConfiguration (17 domain dataclasses),
         and ProjectConfigurationRegistry.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# RuntimeProjectConfiguration — 17 immutable domain dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProjectDomain:
    """Project identity and business context (L.8.4)."""
    project_code: str
    project_name: str
    project_type: str
    discipline: str
    client: str
    contractor: str
    region: str
    execution_center: str
    status: str


@dataclass(frozen=True)
class LifecycleDomain:
    """Project lifecycle information."""
    project_phase: str
    execution_stage: str
    baseline_revision: str
    issue_status: str
    document_status: str
    planned_completion: Optional[str] = None


@dataclass(frozen=True)
class EngineeringDomain:
    """Engineering conventions."""
    drawing_standard: str
    numbering_scheme: str
    revision_scheme: str
    tag_format: str
    engineering_units: str
    allowed_disciplines: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StandardsDomain:
    """Applicable engineering standards."""
    standards: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentDomain:
    """Document processing rules."""
    filename_pattern: str
    parser_profile: str
    revision_scheme: str
    ocr_profile: str
    column_processing: str


@dataclass(frozen=True)
class ParsingDomain:
    """Parser and OCR configuration (profile reference after resolution)."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChunkingDomain:
    """Document fragmentation strategy (profile reference)."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EmbeddingsDomain:
    """Embedding generation configuration (profile reference)."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MetadataDomain:
    """Metadata extraction and inheritance policy."""
    policy_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetsDomain:
    """Engineering asset extraction configuration."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OntologyDomain:
    """Knowledge graph configuration."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalDomain:
    """Search and retrieval configuration."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PromptsDomain:
    """AI prompt templates and policies."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationDomain:
    """Validation policies."""
    profile_id: str
    resolved: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SecurityDomain:
    """Security and access policies."""
    document_classification: str = "internal"
    access_policy: str = "restricted"
    redaction_policy: str = "none"


@dataclass(frozen=True)
class RuntimeProfilesDomain:
    """Runtime infrastructure service references (environment-resolved)."""
    storage: str = "default_storage"
    vector_db: str = "default_vector"
    graph_db: str = "default_graph"
    messaging: str = "none"
    cache: str = "default_cache"


@dataclass(frozen=True)
class RuntimeMetadata:
    """Runtime metadata generated during configuration construction."""
    configuration_version: str = ""
    schema_version: str = ""
    configuration_checksum: str = ""
    build_timestamp: str = ""
    resolved_profiles: List[str] = field(default_factory=list)
    validation_status: str = "pending"


@dataclass(frozen=True)
class RuntimeProjectConfiguration:
    """Immutable runtime representation of a resolved Project Definition.

    Produced by ProjectDefinitionResolver after loading, resolving,
    validating, and merging all configuration sources.  Runtime modules
    consume only this object — they never access Project Definitions
    or config files directly (L.8.1).
    """
    project: ProjectDomain
    lifecycle: LifecycleDomain
    engineering: EngineeringDomain
    standards: StandardsDomain
    document: DocumentDomain
    parsing: ParsingDomain
    chunking: ChunkingDomain
    embeddings: EmbeddingsDomain
    metadata: MetadataDomain
    assets: AssetsDomain
    ontology: OntologyDomain
    retrieval: RetrievalDomain
    prompts: PromptsDomain
    validation: ValidationDomain
    security: SecurityDomain
    runtime_profiles: RuntimeProfilesDomain
    runtime: RuntimeMetadata

    # ------------------------------------------------------------------
    # Configuration Slice accessors (L.9.6)
    # ------------------------------------------------------------------

    def slice_for(self, module_name: str) -> Dict[str, Any]:
        """Return the configuration slice required by a runtime module.

        See L.9.6 Configuration Slice Principle.  Each runtime module
        receives only the configuration domains it needs.
        """
        _SLICE_MAP = {
            "FilenameParser":    ["project", "engineering", "document"],
            "RevisionValidator": ["engineering", "document"],
            "DocumentParser":    ["parsing"],
            "OCRProcessor":      ["parsing"],
            "MetadataExtractor": ["metadata"],
            "ColumnProcessor":   ["parsing"],
            "AssetExtractor":    ["assets"],
            "GraphBuilder":      ["ontology", "metadata"],
            "Retriever":         ["retrieval", "embeddings", "ontology"],
            "PromptEngine":      ["prompts"],
            "ValidationEngine":  ["validation"],
            "FileScanner":       ["project"],
            "Pipeline":          ["project", "document"],
        }
        keys = _SLICE_MAP.get(module_name, [])
        return {k: getattr(self, k, None) for k in keys}


# ---------------------------------------------------------------------------
# _FrozenDict — immutable dict wrapper
# ---------------------------------------------------------------------------


class _FrozenDict:
    """Read-only dict wrapper that raises TypeError on mutation."""

    def __init__(self, data: Dict[str, Any]):
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        raise TypeError("Cannot modify frozen dict")

    def __delitem__(self, key: str) -> None:
        raise TypeError("Cannot modify frozen dict")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return repr(self._data)


# ---------------------------------------------------------------------------
# ProjectConfigurationRegistry
# ---------------------------------------------------------------------------


class ProjectConfigurationRegistry:
    """Immutable registry of RuntimeProjectConfiguration per project code.

    Populated by ProjectDefinitionResolver during pipeline bootstrap.
    Read-only after initialization (L.8.7).  Access or mutation attempts
    on internal storage raise TypeError.
    """

    def __init__(self, configurations: Dict[str, RuntimeProjectConfiguration]):
        self._configs: Dict[str, RuntimeProjectConfiguration] = _FrozenDict(configurations)

    @property
    def project_codes(self) -> List[str]:
        return list(self._configs.keys())

    def __contains__(self, project_code: str) -> bool:
        return project_code in self._configs

    def __len__(self) -> int:
        return len(self._configs)

    # -- lookup -------------------------------------------------------------

    def get(self, project_code: str) -> Optional[RuntimeProjectConfiguration]:
        """Lookup runtime configuration by project code."""
        return self._configs.get(project_code)

    # -- serialisation helpers ----------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return serializable dict (for debugging / checkpoints)."""
        return {
            code: str(cfg.__class__.__name__)
            for code, cfg in self._configs.items()
        }


# ---------------------------------------------------------------------------
# ProjectDefinitionResolver
# ---------------------------------------------------------------------------


class ProjectDefinitionResolver:
    """Configuration orchestration component (L.7.2).

    Transforms Project Definitions into validated RuntimeProjectConfiguration
    objects.  Operates during pipeline initialisation, before runtime modules
    are instantiated.
    """

    def __init__(
        self,
        project_definition_config: Dict[str, Any],
        doc_config: Dict[str, Any],
        env_config: Dict[str, Any],
        logger: Any = None,
        processing_config: Optional[Dict[str, Any]] = None,
    ):
        self._pd_config: Dict[str, Any] = project_definition_config
        self._doc_config: Dict[str, Any] = doc_config
        self._env_config: Dict[str, Any] = env_config
        self._logger = logger
        # I281 (T1.224): processing profile VALUES SSOT. When injected, profile
        # registries read from here; otherwise fall back to doc_config for
        # backward compatibility (legacy parsing_profiles / empty sections).
        self._processing_config: Dict[str, Any] = (
            processing_config if processing_config is not None else {}
        )

        # Validation accumulators
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._data_errors: List[str] = []
        self._unresolved_refs: List[str] = []

    # -- public API ---------------------------------------------------------

    def resolve_all(self) -> ProjectConfigurationRegistry:
        """Resolve all Project Definitions → ProjectConfigurationRegistry.

        Workflow (L.7.2):
        1. Load each project definition from config
        2. Resolve reusable profile references (exact-key lookup — V2)
        3. Apply environment configuration
        4. Merge project-specific + reusable + environment config
        5. Validate complete resolved configuration (L.13)
        6. Construct RuntimeProjectConfiguration per project
        7. Register all in ProjectConfigurationRegistry

        Failure semantics (V1): system errors (schema violations, missing
        mandatory sections, unknown profile refs, unknown runtime profiles,
        duplicate project codes/profiles, runtime construction failure)
        accumulate in ``errors`` and hard-fail the pipeline — a project with
        system errors is not registered.  Data errors (L.13.6 capability
        consistency, L.13.7 metadata gaps, L.13.10 unused profiles) accumulate
        in ``data_errors`` and never block construction.
        """
        pd_data = self._pd_config.get("project_definition", self._pd_config)
        if not isinstance(pd_data, dict):
            raise ValueError("Project definition config must contain a 'project_definition' mapping")

        configurations: Dict[str, RuntimeProjectConfiguration] = {}
        build_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

        # L.13.9: duplicate detection (project codes + reusable profile names)
        self._validate_duplicates()

        for project_code, project_def in pd_data.items():
            if not isinstance(project_def, dict):
                self._log(f"Skipping non-dict project definition '{project_code}'", level=2)
                continue

            # L.13.3: mandatory sections + identity completeness
            project_errors = self._validate_project_completeness(project_code, project_def)
            if project_errors:
                for err in project_errors:
                    self._errors.append(err)
                self._log(f"Validation failed for project '{project_code}': {project_errors}", level=0)
                continue

            # Steps 1–2: resolve profiles (exact-key lookup — V2)
            resolved = self._resolve_project(project_code, project_def)

            # L.13.4/13.5: unresolved profile or runtime refs are system errors
            ref_errors = self._validate_profile_refs(project_code, resolved)
            ref_errors.extend(self._validate_environment_refs(project_code, resolved))
            if ref_errors:
                for err in ref_errors:
                    self._errors.append(err)
                self._log(f"Profile reference validation failed for project '{project_code}': {ref_errors}", level=0)
                continue

            # Step 3: apply environment
            resolved = self._apply_environment(resolved)

            # Step 4: merge
            resolved = self._merge_config(resolved)

            # Step 5: validate — data errors never fail (V1)
            data_errors = self._validate_capability_consistency(project_code, resolved)
            data_errors.extend(self._validate_metadata_policy(project_code, project_def))
            for derr in data_errors:
                self._data_errors.append(derr)
                self._log(f"Data warning for project '{project_code}': {derr}", level=2)

            # L.13.8: runtime construction failure is a system error (V1)
            try:
                checksum = self._compute_checksum(project_def, resolved)
                runtime_meta = RuntimeMetadata(
                    configuration_version=self._env_config.get("version", ""),
                    schema_version=project_def.get("compatibility", {}).get("schema_version", "1.0.0"),
                    configuration_checksum=checksum,
                    build_timestamp=build_ts,
                    resolved_profiles=list(resolved.get("_resolved_profiles", [])),
                    validation_status="passed",
                )
                rpc = self._build_runtime_config(project_code, project_def, resolved, runtime_meta)
            except Exception as exc:  # pragma: no cover - defensive
                construction_error = f"S-C-S-0904|PDEF_RUNTIME_CONSTRUCTION_FAILED|{exc}"
                self._errors.append(construction_error)
                self._log(
                    f"Runtime construction failed for project '{project_code}': {exc}",
                    level=0,
                )
                continue

            # Step 6: construct RuntimeProjectConfiguration
            # Step 7: register
            configurations[project_code] = rpc

        # L.13.10: unused configuration (data error — never fails)
        for unused in self._validate_unused_config():
            self._data_errors.append(unused)
            self._log(f"Unused configuration: {unused}", level=2)

        registry = ProjectConfigurationRegistry(configurations)

        if self._errors or self._data_errors:
            self._log(
                f"ProjectDefinitionResolver completed with {len(self._errors)} error(s), "
                f"{len(self._data_errors)} data error(s), {len(self._warnings)} warning(s)",
                level=1,
            )

        return registry

    # -- properties ---------------------------------------------------------

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    @property
    def warnings(self) -> List[str]:
        return list(self._warnings)

    @property
    def data_errors(self) -> List[str]:
        return list(self._data_errors)

    @property
    def validation_report(self) -> Dict[str, Any]:
        """Generate a validation report (L.13.12).

        Contents: resolved projects, resolved reusable profiles, resolved
        runtime profiles, validation results, warnings, errors, configuration
        checksum, schema version, RuntimeProjectConfiguration version.
        """
        project_data = self._pd_config.get("project_definition", self._pd_config)
        runtime_profiles: List[str] = []
        checksums: Dict[str, str] = {}
        schema_versions: Dict[str, str] = {}
        for code, pdef in project_data.items():
            if not isinstance(pdef, dict):
                continue
            rp = pdef.get("runtime_profiles", {})
            for key in ("storage", "vector_db", "graph_db", "messaging", "cache"):
                if rp.get(key):
                    runtime_profiles.append(rp[key])
            checksums[code] = self._compute_checksum(pdef, {})
            schema_versions[code] = self._pd_config.get("version", "1.0.0")
        return {
            "resolved_projects": list(project_data.keys()),
            "resolved_profiles": self._collect_resolved_profile_ids(project_data),
            "runtime_profiles": sorted(set(runtime_profiles)),
            "checksums": checksums,
            "schema_versions": schema_versions,
            "rpc_version": RuntimeProjectConfiguration.__name__,
            "errors": self._errors,
            "data_errors": self._data_errors,
            "warnings": self._warnings,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    # -- internal: resolution -----------------------------------------------

    def _resolve_project(
        self, project_code: str, project_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a single project definition's profile references."""
        resolved: Dict[str, Any] = {}
        resolved["_resolved_profiles"] = []

        # Document profile resolution (from doc_config)
        doc_profile = project_def.get("document_profile", {})
        resolved["document"] = {
            "filename_pattern": doc_profile.get("filename_pattern", ""),
            "parser_profile": doc_profile.get("parser", ""),
            "revision_scheme": doc_profile.get("revision", ""),
            "ocr_profile": doc_profile.get("ocr", ""),
            "column_processing": doc_profile.get("column_processing", ""),
        }

        # Profile references — resolve against owning schema registries (V2)
        profile_map = {
            "parsing_profile": ("parsing", self._resolve_profile("parsing")),
            "chunking_profile": ("chunking", self._resolve_profile("chunking")),
            "embedding_profile": ("embedding", self._resolve_profile("embedding")),
            "asset_profile": ("asset", self._resolve_profile("asset")),
            "ontology_profile": ("ontology", self._resolve_profile("ontology")),
            "retrieval_profile": ("retrieval", self._resolve_profile("retrieval")),
            "prompt_profile": ("prompt", self._resolve_profile("prompt")),
            "validation_profile": ("validation", self._resolve_profile("validation")),
        }
        for pd_key, (domain, resolver) in profile_map.items():
            profile_id = project_def.get(pd_key)
            if isinstance(profile_id, str):
                resolved[domain] = {"profile_id": profile_id, "resolved": resolver(profile_id)}
                resolved["_resolved_profiles"].append(profile_id)
            elif isinstance(profile_id, dict):
                nested = profile_id.get("profile", "")
                resolved[domain] = {"profile_id": nested, "resolved": resolver(nested)}
                resolved["_resolved_profiles"].append(nested)

        resolved["metadata"] = {
            "policy_id": project_def.get("metadata_policy", "standard_inherit"),
            "resolved": {},
        }

        # Security
        sec = project_def.get("security_profile", {})
        resolved["security"] = {
            "document_classification": sec.get("document_classification", "internal"),
            "access_policy": sec.get("access_policy", "restricted"),
            "redaction_policy": sec.get("redaction_policy", "none"),
        }

        # Runtime profiles
        rp = project_def.get("runtime_profiles", {})
        resolved["runtime_profiles"] = {
            "storage": rp.get("storage", "default_storage"),
            "vector_db": rp.get("vector_db", "default_vector"),
            "graph_db": rp.get("graph_db", "default_graph"),
            "messaging": rp.get("messaging", "none"),
            "cache": rp.get("cache", "default_cache"),
        }

        # T1.196 (I266): per-project asset validation rules (migrated from the
        # retired eks_project_rules_config.json). Surfaced for ConfigRegistry and
        # carried into the AssetExtractor slice via AssetsDomain.resolved.
        resolved["fragment_required_fields"] = project_def.get("fragment_required_fields", {})

        return resolved

    # -- internal: profile resolution (V2 — capability-driven) ---------------

    def _resolve_profile(self, domain: str):
        """Return a profile resolver callable for the given domain.

        V2 — exact-key lookup against the owning schema registry.  Capability
        fields declared by the profile (e.g. extraction_profile_def:
        supported_extensions / supported_document_profiles / requires_ocr) are
        carried into the resolved dict for the generic capability evaluator.
        Unknown profile identifiers for domains with a declared library are
        system errors (S-C-S-0902).
        """
        _DOMAIN_LIBRARY_MAP = {
            "parsing": self._processing_config.get("extraction_profiles", {})
                       or self._doc_config.get("parsing_profiles", {}),
            "chunking": self._processing_config.get("chunking_profiles", {})
                        or self._doc_config.get("chunking_profiles", {}),
            "embedding": self._processing_config.get("embedding_profiles", {})
                         or self._doc_config.get("embedding_profiles", {}),
            "asset": self._processing_config.get("asset_profiles", {})
                     or self._doc_config.get("asset_profiles", {}),
            "ontology": self._processing_config.get("ontology_profiles", {})
                        or self._doc_config.get("ontology_profiles", {}),
            "retrieval": self._processing_config.get("retrieval_profiles", {})
                         or self._doc_config.get("retrieval_profiles", {}),
            "prompt": self._processing_config.get("prompt_profiles", {})
                      or self._doc_config.get("prompt_profiles", {}),
            "validation": self._processing_config.get("validation_profiles", {})
                          or self._doc_config.get("validation_profiles", {}),
        }
        # Backward-compatible fallback for the legacy document domain.
        # I279 (T1.213): doc_config.document_type_registry is derived from the
        # three-section eks_document_type_schema.json carrier by SchemaLoader.
        _DOMAIN_LIBRARY_MAP["document"] = self._doc_config.get("document_type_registry", [])
        _LEGACY_INDEX = {"parsing": self._doc_config.get("file_type_registry", [])}

        def _resolve(profile_id: str) -> Dict[str, Any]:
            if not profile_id:
                return {}
            library = _DOMAIN_LIBRARY_MAP.get(domain)
            if isinstance(library, dict) and library:
                # Exact-key lookup against the owning schema registry (V2)
                if profile_id in library:
                    entry = dict(library[profile_id])
                    entry.setdefault("profile_id", profile_id)
                    return entry
                # Domain has a declared library but id is unknown → system error
                self._unresolved_refs.append(f"{domain}:{profile_id}")
                return {"reference": profile_id}
            # Legacy fallback: exact match on extension or parser_class
            legacy = _LEGACY_INDEX.get(domain, [])
            for entry in legacy:
                if profile_id == entry.get("extension") or profile_id == entry.get("parser_class"):
                    return dict(entry)
            # No dedicated library yet — future phases will populate
            self._warnings.append(
                f"Profile '{profile_id}' for domain '{domain}' could not be "
                f"resolved — library not yet available (deferred to future phase)"
            )
            return {"reference": profile_id}

        return _resolve

    def _apply_environment(self, resolved: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment configuration to resolved profile (L.6.3)."""
        # Environment config (e.g., vector_store, embedding, registry) is
        # layered on top of resolved profiles.  For Phase 1 the environment
        # config from eks_config.json is carried as a reference; deeper
        # merging happens in future phases.
        env_config = self._env_config if isinstance(self._env_config, dict) else {}
        env_ctx = {
            "vector_store": env_config.get("vector_store", {}),
            "embedding": env_config.get("embedding", {}),
            "registry": env_config.get("registry", {}),
            "logging": env_config.get("logging", {}),
        }
        resolved["_environment"] = env_ctx
        return resolved

    def _merge_config(self, resolved: Dict[str, Any]) -> Dict[str, Any]:
        """Merge project-specific, reusable, and environment config (L.7.2 step 4)."""
        # Mark as fully resolved — all mergeable layers have been applied
        resolved["_merged"] = True
        return resolved

    # -- internal: validation -----------------------------------------------

    def _validate_project_completeness(
        self, project_code: str, project_def: Dict[str, Any]
    ) -> List[str]:
        """L.13.3 — project definition completeness.

        System errors (S-C-S-0901): missing mandatory section or missing
        mandatory identity field → project is not registered.
        """
        errors: List[str] = []
        mandatory_sections = [
            "project_identity",
            "project_lifecycle",
            "engineering_convention",
            "engineering_standards",
            "document_profile",
        ]
        for section in mandatory_sections:
            if not isinstance(project_def.get(section), dict):
                errors.append(
                    f"S-C-S-0901|PDEF_MISSING_MANDATORY_SECTION|missing "
                    f"mandatory section '{section}'"
                )

        identity = project_def.get("project_identity", {})
        if not isinstance(identity, dict):
            errors.append(
                f"S-C-S-0901|PDEF_MISSING_MANDATORY_SECTION|'project_identity' "
                f"is not a mapping"
            )
            identity = {}
        mandatory_identity_fields = ["project_code", "project_name", "project_type"]
        for field in mandatory_identity_fields:
            if not identity.get(field):
                errors.append(
                    f"S-C-S-0901|PDEF_MISSING_MANDATORY_SECTION|missing "
                    f"mandatory field 'project_identity.{field}'"
                )
        return errors

    def _validate_profile_refs(
        self, project_code: str, resolved: Dict[str, Any]
    ) -> List[str]:
        """L.13.4 — reusable profile references resolved.

        System errors (S-C-S-0902): a referenced profile was not found in a
        domain that has a declared owning-schema library (recorded in
        ``_unresolved_refs``).  Domains whose library is not yet available are
        deferred with a warning and never fail (V1).
        """
        errors: List[str] = []
        unresolved_set = set(self._unresolved_refs)
        for domain in (
            "parsing", "chunking", "embedding", "asset", "ontology",
            "retrieval", "prompt", "validation",
        ):
            profile_id = resolved.get(domain, {}).get("profile_id", "")
            resolved_value = resolved.get(domain, {}).get("resolved") or {}
            if "reference" in resolved_value and profile_id:
                marker = f"{domain}:{profile_id}"
                if marker in unresolved_set:
                    errors.append(
                        f"S-C-S-0902|PDEF_UNKNOWN_PROFILE_REF|unresolved profile "
                        f"reference for domain '{domain}' ('{profile_id}' not "
                        f"registered in the owning schema library)"
                    )

        # L.13.4: document_profile.parser must be a registered parsing profile
        parser_profile = resolved.get("document", {}).get("parser_profile", "")
        parsing_library = self._processing_config.get("extraction_profiles", {}) \
            or self._doc_config.get("parsing_profiles", {})
        if parser_profile and isinstance(parsing_library, dict) and parsing_library:
            if parser_profile not in parsing_library:
                errors.append(
                    f"S-C-S-0902|PDEF_UNKNOWN_PROFILE_REF|document profile "
                    f"parser '{parser_profile}' is not registered in the "
                    f"extraction_profiles library"
                )
        return errors

    def _evaluate_capability_compat(
        self,
        resolved_profile: Dict[str, Any],
        capability_key: str,
        selected_value: str,
        label: str,
    ) -> List[str]:
        """Generic capability compatibility evaluator (V2).

        Compares a resolved profile's declared capability (e.g.
        ``supported_document_profiles``, ``supported_extensions``,
        ``supported_retrieval_strategies``, ``supported_asset_profiles``,
        ``supported_engineering_conventions``) against the project's selected
        value.  Returns ``P1-C-V-0001`` data errors when the selected value is
        not supported.  No hardcoded compatibility matrix — every capability
        list comes from the profile's owning schema declaration.
        """
        data_errors: List[str] = []
        supported = resolved_profile.get(capability_key) or []
        if not supported:
            return data_errors
        if not selected_value:
            return [
                f"P1-C-V-0001|PDEF_CAPABILITY_CONSISTENCY_FAILED|{label}: "
                f"no value selected for profile declaring {capability_key} "
                f"{supported}"
            ]
        if selected_value not in supported:
            return [
                f"P1-C-V-0001|PDEF_CAPABILITY_CONSISTENCY_FAILED|{label} "
                f"'{selected_value}' not supported by profile capability "
                f"{capability_key} {supported}"
            ]
        return data_errors

    def _validate_capability_consistency(
        self, project_code: str, resolved: Dict[str, Any]
    ) -> List[str]:
        """L.13.6 — configuration consistency (V2, capability-driven).

        Data errors (P1-C-V-0001): capability mismatch between a resolved
        profile's declared capabilities and the selected document profile /
        engineering convention.  All comparisons flow through the single
        generic ``_evaluate_capability_compat()`` — no hardcoded pairs.
        Never blocks construction (V1).
        """
        data_errors: List[str] = []

        parsing = resolved.get("parsing", {}).get("resolved") or {}
        document = resolved.get("document", {})

        # Parser ↔ selected document profile capability
        data_errors.extend(
            self._evaluate_capability_compat(
                parsing,
                "supported_document_profiles",
                document.get("filename_pattern", ""),
                "document profile",
            )
        )

        # Parser ↔ supported extensions capability (declared file extensions)
        filename_pattern = document.get("filename_pattern", "") or ""
        declared_extension = ""
        if "." in filename_pattern:
            declared_extension = filename_pattern.split(".")[-1]
        if declared_extension:
            data_errors.extend(
                self._evaluate_capability_compat(
                    parsing,
                    "supported_extensions",
                    declared_extension,
                    "document file extension",
                )
            )

        # OCR ↔ parser capability
        requires_ocr = parsing.get("requires_ocr", False)
        ocr_profile = document.get("ocr_profile", "")
        if requires_ocr and ocr_profile in ("", "none"):
            data_errors.append(
                f"P1-C-V-0001|PDEF_CAPABILITY_CONSISTENCY_FAILED|parser requires "
                f"OCR (requires_ocr=true) but document ocr_profile is '{ocr_profile}'"
            )

        # Revision scheme consistency between document profile and engineering convention
        revision_scheme = document.get("revision_scheme", "")
        project_def = self._pd_config.get("project_definition", {}).get(project_code, {})
        convention_revision = project_def.get("engineering_convention", {}).get(
            "revision_scheme", ""
        )
        if revision_scheme and convention_revision and revision_scheme != convention_revision:
            data_errors.append(
                f"P1-C-V-0001|PDEF_CAPABILITY_CONSISTENCY_FAILED|revision scheme "
                f"mismatch: document profile '{revision_scheme}' vs engineering "
                f"convention '{convention_revision}'"
            )

        return data_errors

    def _validate_metadata_policy(
        self, project_code: str, project_def: Dict[str, Any]
    ) -> List[str]:
        """L.13.7 — metadata policy validation.

        Data errors (P1-C-V-0002): a mandatory metadata field declared for the
        project has no inheritance rule in the resolved metadata policy.
        Never blocks construction (V1).
        """
        data_errors: List[str] = []
        policy_id = project_def.get("metadata_policy", "standard_inherit")
        if isinstance(policy_id, dict):
            policy_id = policy_id.get("profile", "standard_inherit")
        mandatory_metadata = project_def.get("mandatory_metadata", [])
        if not mandatory_metadata:
            return data_errors
        # standard_inherit covers project_code/revision/document_number/...
        inherited = {
            "project_code", "revision", "document_number", "sheet_number",
            "discipline", "client", "vendor",
        }
        for field_name in mandatory_metadata:
            if field_name not in inherited:
                data_errors.append(
                    f"P1-C-V-0002|PDEF_METADATA_POLICY_GAP|mandatory metadata "
                    f"field '{field_name}' has no inheritance rule under "
                    f"metadata policy '{policy_id}'"
                )
        return data_errors

    def _validate_duplicates(self) -> None:
        """L.13.9 — duplicate detection.

        System errors (S-C-S-0903): duplicate project codes (impossible in a
        dict keyed by project code — checked defensively) and duplicate
        reusable profile identifiers across owning schema registries.
        """
        pd_data = self._pd_config.get("project_definition", self._pd_config)
        if not isinstance(pd_data, dict):
            return

        # Duplicate project codes cannot occur in a dict — but a config may
        # pass a list-of-entries form; guard against it defensively.
        seen_codes: Dict[str, str] = {}
        for code in pd_data:
            if code in seen_codes:
                self._errors.append(
                    f"S-C-S-0903|PDEF_DUPLICATE_PROJECT_OR_PROFILE|duplicate "
                    f"project code '{code}'"
                )
            seen_codes[code] = code

        # Duplicate reusable profile identifiers across owning schema registries
        profile_registries = [
            self._processing_config.get("extraction_profiles", {})
            or self._doc_config.get("parsing_profiles", {}),
            self._processing_config.get("chunking_profiles", {})
            or self._doc_config.get("chunking_profiles", {}),
            self._processing_config.get("embedding_profiles", {})
            or self._doc_config.get("embedding_profiles", {}),
            self._processing_config.get("asset_profiles", {})
            or self._doc_config.get("asset_profiles", {}),
            self._processing_config.get("ontology_profiles", {})
            or self._doc_config.get("ontology_profiles", {}),
            self._processing_config.get("retrieval_profiles", {})
            or self._doc_config.get("retrieval_profiles", {}),
            self._processing_config.get("prompt_profiles", {})
            or self._doc_config.get("prompt_profiles", {}),
            self._processing_config.get("validation_profiles", {})
            or self._doc_config.get("validation_profiles", {}),
        ]
        seen_profiles: Dict[str, str] = {}
        for registry in profile_registries:
            if not isinstance(registry, dict):
                continue
            for profile_id in registry:
                if profile_id in seen_profiles:
                    self._errors.append(
                        f"S-C-S-0903|PDEF_DUPLICATE_PROJECT_OR_PROFILE|duplicate "
                        f"reusable profile '{profile_id}' (also registered in "
                        f"'{seen_profiles[profile_id]}')"
                    )
                seen_profiles[profile_id] = "schema registry"

    def _validate_environment_refs(
        self, project_code: str, resolved: Dict[str, Any]
    ) -> List[str]:
        """L.13.5 — environment / runtime profile references validated.

        System errors (S-C-S-0902): a runtime profile reference
        (storage/vector_db/graph_db/messaging/cache) is not one of the known
        profiles.  No runtime profile registry exists yet in the environment
        config, so the known-profile index falls back to the ``default_*``
        allowlist defined by RuntimeProfilesDomain defaults (V1 note).
        """
        errors: List[str] = []
        runtime_profiles = resolved.get("runtime_profiles", {})
        known_profiles = self._known_runtime_profiles()
        for key, ref in runtime_profiles.items():
            if not ref:
                errors.append(
                    f"S-C-S-0902|PDEF_UNKNOWN_PROFILE_REF|runtime profile "
                    f"'{key}' is empty"
                )
            elif ref not in known_profiles:
                errors.append(
                    f"S-C-S-0902|PDEF_UNKNOWN_PROFILE_REF|unknown runtime "
                    f"profile '{ref}' for '{key}' (known: {sorted(known_profiles)})"
                )
        return errors

    @staticmethod
    def _known_runtime_profiles() -> List[str]:
        """Known runtime profile names (schema-driven allowlist fallback).

        Derived from RuntimeProfilesDomain dataclass defaults plus the
        documented ``none`` sentinel.  When a runtime profile registry is
        added to the environment config, this becomes the registry lookup.
        """
        defaults = set()
        for f in fields(RuntimeProfilesDomain):
            if isinstance(f.default, str) and f.default:
                defaults.add(f.default)
        defaults.add("none")
        defaults.add("default_storage")
        defaults.add("default_vector")
        defaults.add("default_graph")
        defaults.add("default_cache")
        return sorted(defaults)

    def _validate_unused_config(self) -> List[str]:
        """L.13.10 — unused configuration detection.

        Data errors (P1-C-V-0003): reusable profiles registered in an owning
        schema library that no project definition references.  Warnings, never
        errors (L.13.10).
        """
        unused: List[str] = []
        referenced = self._collect_resolved_profile_ids(
            self._pd_config.get("project_definition", self._pd_config)
        )
        registries = {
            "extraction_profiles": self._processing_config.get("extraction_profiles", {})
                                   or self._doc_config.get("parsing_profiles", {}),
            "chunking_profiles": self._processing_config.get("chunking_profiles", {})
                                 or self._doc_config.get("chunking_profiles", {}),
            "embedding_profiles": self._processing_config.get("embedding_profiles", {})
                                  or self._doc_config.get("embedding_profiles", {}),
            "asset_profiles": self._processing_config.get("asset_profiles", {})
                              or self._doc_config.get("asset_profiles", {}),
            "ontology_profiles": self._processing_config.get("ontology_profiles", {})
                                 or self._doc_config.get("ontology_profiles", {}),
            "retrieval_profiles": self._processing_config.get("retrieval_profiles", {})
                                  or self._doc_config.get("retrieval_profiles", {}),
            "prompt_profiles": self._processing_config.get("prompt_profiles", {})
                               or self._doc_config.get("prompt_profiles", {}),
            "validation_profiles": self._processing_config.get("validation_profiles", {})
                                   or self._doc_config.get("validation_profiles", {}),
            "indexing_profiles": self._processing_config.get("indexing_profiles", {}),
            "ai_reasoning_profiles": self._processing_config.get("ai_reasoning_profiles", {}),
            "graph_mapping_profiles": self._processing_config.get("graph_mapping_profiles", {}),
        }
        for registry_name, registry in registries.items():
            if not isinstance(registry, dict):
                continue
            for profile_id in registry:
                if profile_id not in referenced:
                    unused.append(
                        f"P1-C-V-0003|PDEF_UNUSED_PROFILE|profile '{profile_id}' "
                        f"registered in '{registry_name}' but never referenced "
                        f"by any project definition"
                    )
        return unused

    def _collect_resolved_profile_ids(self, pd_data: Dict[str, Any]) -> List[str]:
        """Collect every reusable profile id referenced by any project."""
        ids: List[str] = []
        if not isinstance(pd_data, dict):
            return ids
        profile_keys = [
            "parsing_profile", "chunking_profile", "embedding_profile",
            "asset_profile", "ontology_profile", "retrieval_profile",
            "prompt_profile", "validation_profile", "document_profile",
        ]
        for pdef in pd_data.values():
            if not isinstance(pdef, dict):
                continue
            for key in profile_keys:
                value = pdef.get(key)
                if isinstance(value, str):
                    ids.append(value)
                elif isinstance(value, dict):
                    ids.append(value.get("profile", ""))
                elif isinstance(value, list):
                    ids.extend(v for v in value if isinstance(v, str))
            doc_profile = pdef.get("document_profile")
            if isinstance(doc_profile, dict) and doc_profile.get("parser"):
                ids.append(doc_profile["parser"])
        return [i for i in ids if i]

    # -- internal: construction ---------------------------------------------

    def _build_runtime_config(
        self,
        project_code: str,
        project_def: Dict[str, Any],
        resolved: Dict[str, Any],
        runtime_meta: RuntimeMetadata,
    ) -> RuntimeProjectConfiguration:
        """Construct an immutable RuntimeProjectConfiguration (L.8)."""
        identity = project_def.get("project_identity", {})
        lifecycle = project_def.get("project_lifecycle", {})
        engineering = project_def.get("engineering_convention", {})
        standards = project_def.get("engineering_standards", {})
        security = resolved.get("security", {})
        rp = resolved.get("runtime_profiles", {})

        return RuntimeProjectConfiguration(
            project=ProjectDomain(
                project_code=identity.get("project_code", project_code),
                project_name=identity.get("project_name", ""),
                project_type=identity.get("project_type", ""),
                discipline=identity.get("discipline", ""),
                client=identity.get("client", ""),
                contractor=identity.get("contractor", ""),
                region=identity.get("region", ""),
                execution_center=identity.get("execution_center", ""),
                status=identity.get("status", "active"),
            ),
            lifecycle=LifecycleDomain(
                project_phase=lifecycle.get("project_phase", ""),
                execution_stage=lifecycle.get("execution_stage", ""),
                baseline_revision=lifecycle.get("baseline_revision", ""),
                issue_status=lifecycle.get("issue_status", ""),
                document_status=lifecycle.get("document_status", ""),
                planned_completion=lifecycle.get("planned_completion"),
            ),
            engineering=EngineeringDomain(
                drawing_standard=engineering.get("drawing_standard", ""),
                numbering_scheme=engineering.get("numbering_scheme", ""),
                revision_scheme=engineering.get("revision_scheme", ""),
                tag_format=engineering.get("tag_format", ""),
                engineering_units=engineering.get("engineering_units", ""),
                allowed_disciplines=engineering.get("allowed_disciplines", []),
            ),
            standards=StandardsDomain(standards=dict(standards)),
            document=DocumentDomain(
                filename_pattern=resolved.get("document", {}).get("filename_pattern", ""),
                parser_profile=resolved.get("document", {}).get("parser_profile", ""),
                revision_scheme=resolved.get("document", {}).get("revision_scheme", ""),
                ocr_profile=resolved.get("document", {}).get("ocr_profile", ""),
                column_processing=resolved.get("document", {}).get("column_processing", ""),
            ),
            parsing=ParsingDomain(
                profile_id=resolved.get("parsing", {}).get("profile_id", ""),
                resolved=resolved.get("parsing", {}).get("resolved", {}),
            ),
            chunking=ChunkingDomain(
                profile_id=resolved.get("chunking", {}).get("profile_id", ""),
                resolved=resolved.get("chunking", {}).get("resolved", {}),
            ),
            embeddings=EmbeddingsDomain(
                profile_id=resolved.get("embedding", {}).get("profile_id", ""),
                resolved=resolved.get("embedding", {}).get("resolved", {}),
            ),
            metadata=MetadataDomain(
                policy_id=resolved.get("metadata", {}).get("policy_id", "standard_inherit"),
                resolved=resolved.get("metadata", {}).get("resolved", {}),
            ),
            assets=AssetsDomain(
                profile_id=resolved.get("asset", {}).get("profile_id", ""),
                resolved={
                    **resolved.get("asset", {}).get("resolved", {}),
                    "fragment_required_fields": resolved.get("fragment_required_fields", {}),
                },
            ),
            ontology=OntologyDomain(
                profile_id=resolved.get("ontology", {}).get("profile_id", ""),
                resolved=resolved.get("ontology", {}).get("resolved", {}),
            ),
            retrieval=RetrievalDomain(
                profile_id=resolved.get("retrieval", {}).get("profile_id", ""),
                resolved=resolved.get("retrieval", {}).get("resolved", {}),
            ),
            prompts=PromptsDomain(
                profile_id=resolved.get("prompt", {}).get("profile_id", ""),
                resolved=resolved.get("prompt", {}).get("resolved", {}),
            ),
            validation=ValidationDomain(
                profile_id=resolved.get("validation", {}).get("profile_id", ""),
                resolved=resolved.get("validation", {}).get("resolved", {}),
            ),
            security=SecurityDomain(
                document_classification=security.get("document_classification", "internal"),
                access_policy=security.get("access_policy", "restricted"),
                redaction_policy=security.get("redaction_policy", "none"),
            ),
            runtime_profiles=RuntimeProfilesDomain(
                storage=rp.get("storage", "default_storage"),
                vector_db=rp.get("vector_db", "default_vector"),
                graph_db=rp.get("graph_db", "default_graph"),
                messaging=rp.get("messaging", "none"),
                cache=rp.get("cache", "default_cache"),
            ),
            runtime=runtime_meta,
        )

    # -- internal: utilities ------------------------------------------------

    @staticmethod
    def _compute_checksum(
        project_def: Dict[str, Any], resolved: Dict[str, Any]
    ) -> str:
        """Compute deterministic checksum for auditing (L.8.5)."""
        raw = json.dumps(project_def, sort_keys=True) + json.dumps(resolved, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _log(self, msg: str, level: int = 1) -> None:
        """Log through optional logger."""
        if self._logger is not None:
            try:
                self._logger.log(msg, level=level)
            except Exception:
                pass
