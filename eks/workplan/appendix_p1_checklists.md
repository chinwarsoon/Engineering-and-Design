# Appendix P1-D: Phase 1 Checklists

> Extracted from [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)
> Auto-generated: 2026-07-20

---

## Contents

- [36. Success Criteria](#success-criteria)
- [37. Deliverables](#deliverables)

---

## 36. Success Criteria

- [x] EKS folder structure created and compliant with AGENTS.md project folder conventions
- [x] `eks.yml` created and environment activates cleanly (`conda env create -f eks.yml`)
- [x] Canonical schema files (base/setup/config) created with Triple-File pattern for all components
- [x] Schema inheritance implemented: all setup schemas use `allOf` to reference their respective base schemas
- [x] Schema loader resolves all $ref types (string, object, nested, recursive) across inherited files
- [x] Document registry operational: CRUD for document metadata
- [x] Revision management working: preserve all revisions, is_latest flag, chain lookup
- [x] PDF, DOCX, XLSX parsers functional via abstract plug-in interface
- [x] Tiered logger (levels 0–3), debug object, trace table all operational
- [x] SSOT config registry operational; zero hardcoded global parameters
- [x] All unit tests passing for Phase 1 components
- [x] `update_log.md` and `issue_log.md` created under `eks/log/`
- [x] `__init__.py` files created for all engine packages per AGENTS.md §4.2
- [x] `jsonschema.RefResolver` deprecation resolved — migrated to `referencing` library
- [x] Phase 1 test report generated at `eks/workplan/reports/phase_1_foundation_report.md`
- [x] Universal plant item schema designed: 13 fragments in `eks_asset_base_schema.json` covering all 7 datadrop categories
- [x] Asset type registry mapped: all 14 AT_ categories composed from fragments in `eks_asset_config.json`
- [x] Zero-code extensibility: `conditional_fragments` structure declared in `eks_asset_setup_schema.json`; AT_EQUIP and AT_MOTOR entries include conditional fragment rules in `eks_asset_config.json`
- [x] All 13 fragment `$defs` present and correct in `eks_asset_base_schema.json`
- [x] Document Registry G1-G3 resolved: `source_type` supported, SQL injection protection in place, SQL-level sorting implemented.
- [x] Extended Metadata Support (T1.22): 11 new fields added to schema and DB; JSON array support for asset_tags; migration logic verified.
- [x] ISO 15926-aligned ontology schema design and dynamic config file implemented (T1.23, T1.24)
- [x] Schema loader extended to validate and load the ontology registry dynamically (T1.25)
- [x] Ontology unit tests passing in test_phase1.py and test_loader_full.py (T1.26)
- [x] Asset schema compliant with ontology: fragments categorized (functional/physical) and linked to ontology classes (T1.27)
- [x] Relationship metadata embedded in asset schemas (T1.28)
- [x] Document ontology hierarchy and lifecycle mapping triggers implemented (T1.29)
- [x] Core, asset, and ontology schema/config files reorganized under `eks/config/schemas/` folder and verified by all passing tests (T1.33)
- [x] Document schema reorganized into dedicated 3-layer pattern: `eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json` (T1.34)
- [x] `eks_base_schema.json` no longer contains document definitions (moved to doc schema) (T1.34)
- [x] `document_element_def` added to `eks_doc_base_schema.json` (7 columns) (T1.34)
- [x] `eks_doc_setup_schema.json` declares table structure, extraction rules, health scoring schema (T1.34)
- [x] `eks_doc_config.json` contains ontology triggers, health scoring dimensions/tiers, element expectations per document type (T1.34)
- [x] `registry.py` loads doc schema from `eks_doc_base_schema.json` (T1.34)
- [x] Schema loader discovers doc schema in fallback chain (T1.34)
- [x] All Phase 1 tests pass after reorganization (T1.34)
- [x] Document type enum (7 codes) defined and validated in `eks_doc_base_schema.json` (T1.35.1)
- [x] File type enum (5 codes) defined and validated (T1.35.1)
- [x] Element type enum (8 codes) defined and validated (T1.35.1)
- [x] `document_metadata_def` includes `file_path`, `ingested_at`, `file_type` fields (T1.35.1)
- [x] `document_type_registry` declared in setup and populated in config with 7 entries (T1.35.2, T1.35.3)
- [x] `file_type_registry` declared in setup and populated in config with 5 entries (T1.35.2, T1.35.3)
- [x] `element_type_registry` declared in setup and populated in config with 8 entries (T1.35.2, T1.35.3)
- [x] `element_expectations` keys refactored from cover types (A-E) to document type codes (T1.35.3)
- [x] Schema loader validates registry completeness and enum values (T1.35.4)
- [x] 6 new doc schema tests added and passing (T1.35.5)
- [x] Auto-DDL generated from JSON schema definitions; registry.py uses generated DDL (T1.36)
- [x] File scanner walks directory, validates extensions, registers placeholder rows (T1.37)
- [x] Parser router maps file_type to parser class, orchestrates parse flow (T1.38)
- [x] Pipeline orchestrator coordinates scan → register → route → parse → detect → score → update (T1.39)
- [x] Manual review workflow surfaces flagged docs, supports correction and lock (T1.40)
- [x] Error/message schemas follow 3-layer pattern with setup layer (T1.41)
- [x] I014 resolved: error/message schema validation now passes
- [x] Project code fragment schema created with real WSD11 codes (T1.42)
- [x] Discipline fragment schema created with 21 valid codes (T1.43)
- [x] Department fragment schema created with 11 valid codes (T1.44)
- [x] Facility fragment schema created with 12 valid prefixes (T1.45)
- [x] Base schema updated with project_entry_def, department_entry_def, facility_entry_def (T1.46)
- [x] Config updated: P123/P456 replaced with 131101/131242; $ref to fragment schemas (T1.46)
- [x] Setup schema updated with project_registry, department_registry, facility_registry declarations (T1.46)
- [x] I005 resolved: placeholder data replaced with real project codes
- [x] 6 new fragment schema tests added and passing (T1.47)
- [x] 114/114 total Phase 1 tests passing
- [x] Error/message base schema URIs aligned to filename-based convention (I027 resolved)
- [x] `verbosity_level` enum consolidated into shared `eks_base_schema.json#/definitions/verbosity_level` (message + logging share SSOT)
- [x] `document_relationship_trigger_map` shared between asset and doc configs via `eks_base_schema.json` definition
- [x] `base_schema` added to all validation registries enabling cross-schema `$ref` resolution
- [x] Data challenges from twrp sample documented in issue_log.md (I015–I021)
- [x] DGN parser gap identified as risk with Phase 3 mitigation plan
- [x] `document_relationship_trigger_map` stripped to shape-only in base — actual entries SSOT in config files (I031, U086)
- [x] `revision_id` moved from base to doc schema set with full 3-layer chain (I032, U087)
- [x] `revision_pattern` removed from project_rules_def; `revision_validation` added to doc setup+config
- [x] `ConfigRegistry` resolves `$ref` entries on-the-fly for project-scoped data access
- [x] `schema_inheritance_chain.md` v1.6 updated: document_relationship_trigger_map + revision_id changes
- [x] Initiation integrity gate wired (T1.77): `validate_all()` + `get_readiness_status()` fail-fast in `phase1_server._run()`; `--debug`/`--level` CLI flags; `data_dir`/`recursive` validated pre-lock
- [x] DCC initiation gaps closed (T1.78): `eks/eks.yml` path fix, input readability, dependency probe, output-path validation, `--skip-readiness`, error code constants
- [x] `P1-SETUP-*` error codes attached to every `validate_all()` result entry (T1.79)
- [x] Readiness gate raises via `ErrorManager.handle_system_error("P1-SETUP-READINESS")` (T1.79)
- [x] Output/eks.yml paths derived from `global_paths` schema config (T1.80)
- [x] Hardcoded fallback lists removed from `setup_validator.py` — raises `ValueError` if config absent (T1.81)
- [x] `validation_options.auto_create_folders` passed from config to `validate_all()` (T1.82)
- [x] `data_dir` default derived from `config.global_paths.data_dir` (T1.82)
- [x] `eks_root` added to schema; all `PRJ_DIR/"eks"` literals replaced (T1.83)
- [x] Universal `ValidationManager` created in `common/library/utility/validation/` (T1.84)
- [x] EKS `project_setup` schema reshaped to DCC object model — 8 new object defs (T1.85)
- [x] `project_setup` instance data extracted to `eks_project_setup_config.json` (T1.86)
- [x] `setup_validator.py` refactored as thin adapter to universal `ValidationManager` (T1.87)
- [x] Validator tests migrated + universal-module tests added; full suite 235/235 green (T1.88)
- [x] Phase 1.3 docs/logs/knowledge updated; I085 resolved (T1.89)

---

## 37. Deliverables

- EKS project folder structure (including `eks/config/schemas/`)
- `eks/eks.yml` — Conda environment file
- Canonical schema files (Base/Setup/Config): `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json` (moved to `eks/config/schemas/`)
- Engine modules: `registry.py`, `revision.py`, `config_registry.py`, `schema_loader.py`
- Parser modules: `base_parser.py`, `pdf_parser.py`, `docx_parser.py`, `xlsx_parser.py`
- Logging module: `logger.py`
- Test files: `test_phase1.py`, `test_asset_schema.py`, `test_loader_full.py`, `validate_ontology.py`
- Log files: `update_log.md`, `issue_log.md`
- Package init files: `engine/__init__.py`, `engine/core/__init__.py`, `engine/parsers/__init__.py`, `engine/logging/__init__.py`
- Asset schema files: `eks_asset_base_schema.json` (13 fragments), `eks_asset_setup_schema.json` (fragment categories + inheritance), `eks_asset_config.json` (fragment categories populated) (moved to `eks/config/schemas/`)
- Ontology files: `eks_ontology_base_schema.json`, `eks_ontology_setup_schema.json`, `eks_ontology_config.json` (moved to `eks/config/schemas/`)
- Pipeline message & error schema files: `eks_error_code_base.json`, `eks_error_config.json`, `eks_message_base.json`, `eks_message_config.json` (`eks/config/schemas/`)
- Error/message/scoring modules: `error_manager.py`, `message_manager.py`, `health_scorer.py`, `structure_detector.py`
- Test file: `test_t132_modules.py` (47 tests, all passing)
- Reports: `phase_1_foundation_report.md` (includes T1.30–T1.32 results consolidated)
- Document schema files (T1.34): `eks_doc_base_schema.json` (document + element definitions), `eks_doc_setup_schema.json` (table declarations, extraction rules, health scoring), `eks_doc_config.json` (ontology triggers, health score tiers, element expectations)
- Enhanced document schema files (T1.35): `eks_doc_base_schema.json` v1.1 (enums + missing fields), `eks_doc_setup_schema.json` v1.1 (3 registries), `eks_doc_config.json` v1.1 (registry values + refactored expectations)
- Updated test file: `test_phase1.py` (+6 tests for enhanced doc schema)
- Updated appendix: `appendix_b_document_registry.md` v0.9 (B3.2, B3.3, B3.4 sections)
- Auto-DDL module (T1.36): `schema_to_ddl.py` (generates SQL from JSON schema definitions)
- File scanner module (T1.37): `file_scanner.py` (directory walk, type validation, placeholder registration)
- Parser router module (T1.38): `parser_router.py` (file_type → parser class routing)
- Pipeline orchestrator (T1.39): `pipeline_orchestrator.py` (Phase A/B/C coordinator)
- Manual review workflow (T1.40): `review_manager.py` (query flagged docs, metadata correction, element confirmation, score recalculation, document lock) + 4 tests
- Error/message schema setup layers (T1.41): `eks_error_setup_schema.json`, `eks_message_setup_schema.json` (allOf + $ref pattern)
- Fragment schemas (T1.42–T1.45): `eks_project_code_schema.json` (3 projects), `eks_discipline_schema.json` (21 disciplines), `eks_department_schema.json` (11 departments), `eks_facility_schema.json` (12 facilities)
- Base schema definitions (T1.46): `project_entry_def`, `department_entry_def`, `facility_entry_def` added to `eks_base_schema.json`
- Config updates (T1.46): `eks_config.json` with real WSD11 codes (131101, 131242) and `$ref` to fragment schemas
- Setup schema updates (T1.46): `eks_setup_schema.json` with `project_registry`, `department_registry`, `facility_registry` property declarations
- Fragment schema tests (T1.47): 6 new tests in `test_phase1.py` (59/59 total)
- Data challenge analysis: I015–I021 logged to `eks/log/issue_log.md`, §25 added to master workplan
- Schema audit fixes (T1.48): duplicate defs removed, parser paths aligned, missing parsers added, I022–I028 logged
- URI alignment (I027): error/message base schema `$id` changed to filename-based pattern
- Shared `verbosity_level` definition in `eks_base_schema.json` (SSOT for message + logging levels)
- Shared `document_relationship_trigger_map` definition in `eks_base_schema.json` (SSOT for asset + doc trigger mappings)
- `schema_loader.py` updated: `base_schema` added to all validation registries for cross-schema `$ref` support
- `test_asset_schema.py` and `test_phase1.py` updated: `eks_base_schema.json` included in validation registries
- **T1.50 Base schema SSOT enforcement**: `document_relationship_trigger_map` stripped to shape-only (U086), `revision_id` moved to doc schema set + `revision_validation` 3-layer chain (U087), `revision_pattern` removed from `project_rules_def`
- `eks_doc_setup_schema.json` v1.3.0: added `revision_validation` property
- `eks_doc_config.json` v1.2.0: added `revision_validation` entries (131101→`^[A-Z0-9]{1,2}$`, 131242→`^[0-9]{3}$`)
- `eks_project_rules_config.json` v1.1.0: removed `revision_pattern` (now SSOT in doc config)
- `config_registry.py`: `_load_ref()` + `get()` + helper methods resolve `$ref` on-the-fly
- `schema_inheritance_chain.md` v1.6: report updated with SSOT changes
- **Initiation Integrity & Hardening (T1.77–T1.83)**: `setup_validator.py` v0.6 (P1-SETUP-* codes + ErrorManager gate), `phase1_server.py` v0.8 (config-driven paths, `eks_root`, `--skip-readiness`), `eks_error_code_base.json`/`eks_error_setup_schema.json`/`eks_error_config.json` (7 P1-SETUP-* codes, "Setup" category), `test_setup_validator.py` (+7 T1.79 tests + 1 SSOT test), `test_phase1_server.py` (+36 tests); 215/215 pass
- **Phase 1.3 Initiation Harmonization (T1.84–T1.89)**: `common/library/utility/validation/manager.py` + `__init__.py` (universal `ValidationManager`), `eks_project_setup_config.json` v1.0.0 (extracted `project_setup`), `eks_base_schema.json` v1.7.0 (8 object defs), `eks_setup_schema.json` v1.4.0, `eks_config.json` v1.5.0, `setup_validator.py` v0.7 (thin adapter), `test_validation_manager.py` (20), `test_setup_validator.py` (19); 235/235 pass
- **Bootstrap path-rooting fix (I130 / T1.99.101–T1.99.103)**: `bootstrap.py` L250 — `if self._path_resolver is not None:` → `if self._path_resolver is not None and self.config:`. Option A guard prevents resolver call with empty config during P2_paths (runs before P3_registry), falling through to else-branch correctly anchored under `pipeline_root_dir="eks"`. See §39.
- **KeyError 'revision' fix (I131 / T1.99.104–T1.99.107)**: 3-level layered fix in `file_scanner.py` + `registry.py`: (L1) `_parse_filename()` fallback returns `revision="00"`, (L2) `build_placeholder_metadata()` safety net `setdefault("revision", "00")`, (L3) `register_document()` uses `.get("revision", "00")` + `.get("document_number")`. Pipeline now runs Phase A→B→C: 19 files, 7 flagged. See §40.
- **.dwg file type orphan fix (I132 / Option B)**: Added `"CAD"` document type to `eks_doc_base_schema.json` enum, `eks_doc_setup_schema.json` propertyNames pattern, and `eks_doc_config.json` document_type_registry + element_expectations. `.dwg` files now have a document type that expects them. See §41.


---

