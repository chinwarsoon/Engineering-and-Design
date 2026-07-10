# EKS Phase 1 — Foundation: Project Structure, Schema & Document Registry

**Document ID**: WP-EKS-P1-001  
**Current Version**: 3.44  
**Status**: 🔶 PARTIAL — Phase 1 foundation, bootstrap closure, initiation integrity, config flattening, and schema discovery & registration (T1.96) ✅ COMPLETE. **T1.97 (System Parameters — SSOT Centralization) 🔷 PLANNED** — schema-defined system_parameters block with universal `get_system_param()` in `common/library/`. 236/236 tests pass.  
**Last Updated**: 2026-07-10  
**Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)  
**Phase Dependency**: None — first phase  
**Sub-Phase Workplans**: [phase_1.2_interactive_ui_workplan.md](phase_1.2_interactive_ui_workplan.md) — WP-EKS-P1.2-001; [phase_1.3_initiation_harmonization_workplan.md](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001 (archived; content integrated into §16)

---

## 1. Title and Description

Establish the EKS project foundation: folder structure, canonical schema design (including project-specific discipline registries), document ingestion plug-ins for common formats (PDF, DOCX, XLSX), document registry (metadata DB), revision management, and foundational logging/debug infrastructure.
 This phase creates the bedrock that all subsequent phases build upon.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                            |
| :------ | :--------- | :----- | :-------------------------------------------- |
| 3.40    | 2026-07-09 | opencode | **Consolidated + COMPLETE**: Restored pre-truncation workplan body (v3.29) and integrated Phase 1.3 (T1.84–T1.89) Initiation Schema & Validation Harmonization into §16. Added §15 Initiation Integrity & Hardening (T1.77–T1.83) summary referencing `phase_1_t179_t183_report.md`. Phase status set to ✅ COMPLETE through T1.89 (235/235 tests pass). Phase 1.3 stand-alone workplan archived in `eks/archive/`. |
| 3.41    | 2026-07-09 | opencode | **Initiation Config Flattening (T1.90–T1.95)**: Added §17. Flatten `project_setup` from `eks_config.json` to top-level (DCC `project_config` pattern); update `eks_setup_schema.json` (drop wrapper, v1.5.0); make `setup_validator.py` + `phase1_server.py` flatten-aware with `project_setup` backward-compat fallback; delete orphan `eks_project_setup_config.json` (archived); update tests; full suite green. |
| 3.42    | 2026-07-10 | opencode | **Schema Discovery & Registration (T1.96)**: Added §18. Extract `discover_schema_files()` from DCC `ref_resolver.py` into `common/` as shared function; add `discovery_rules` data to `eks_config.json`; refactor `schema_loader.py` to use config-driven loading (explicit + discovery); wire `ValidationManager.validate_discovery_rules()` in `setup_validator.py`. Updated §5 index, §18, §19. Logged I087–I090. |
| 3.43    | 2026-07-10 | opencode | **T1.96f COMPLETE**: Fixed discovery-driven schema loading — added `*_base.json` discovery rule to catch `eks_error_code_base.json` and `eks_message_base.json` (missed by `*_base_schema.json` pattern). All 236/236 tests green. Updated §18 statuses. Phase 1 foundation marked ✅ COMPLETE. |
| 3.44    | 2026-07-10 | opencode | **T1.97 (PLANNED)**: Added §19 System Parameters — SSOT Centralization. Universal `get_system_param()` in `common/library/config/`; `system_parameters_def` in `eks_base_schema.json`; `system_parameters` block in `eks_config.json`; replace hardcoded values in `phase1_server.py`, `error_manager.py`, `registry.py`, `server.py`. Phase status set to 🔶 PARTIAL. Updated index, revision table, §5. |
| 3.29    | 2026-07-08 | opencode | Expanded Bootstrap closure scope: added T1.75 (activate ErrorManager/MessageManager in phase1_server — closes silent T1.68 gap where managers were never passed to the running server) and T1.76 (persist debug_log.json + message/status JSON to `eks/output/` per AGENTS.md §7/§19). Updated T1.69 (run_id correlation) and T1.73 (checkpoint to `eks/output/checkpoints/{job_id}.json`). Updated §4 scope, §8 task table, §9 files table, §14 Mermaid, and test report. |
| 3.26    | 2026-07-08 | System | Appended a new revision entry to the history and documented the shared common-library architecture milestone under `common/library` as a follow-on foundation item for future EKS integration work. |
| 3.28    | 2026-07-08 | opencode | Implemented T1.68 (wired ErrorManager/MessageManager into PipelineOrchestrator), T1.71 (added update_document_status + _with_retry to registry), T1.74 (anchored phase1_server paths to PRJ_DIR, EKSPaths.to_dict uses .as_posix()). Fixed pre-existing get_document() bug. Added 7 new tests. 191/191 tests pass. |
| 3.27    | 2026-07-08 | System | Added `Related Tasks` column to §4 Scope Summary table and `Scope` column to §8 Task Breakdown table with full cross-references; added R99 Foundation & Compliance scope entry. |
| 3.25    | 2026-07-08 | System | Added note that shared common-library package structure under `common/library` now exists for architecture-aligned logging, telemetry, pipeline, errors, messages, paths, validation, UI, and factory modules; documented as a reusable foundation for future EKS integration work. |
| 3.24    | 2026-07-08 | System | Added T1.68–T1.73: wire ErrorManager/MessageManager into orchestrator (T1.68), add run_id correlation ID to EKSLogger (T1.69), add data_dir traversal guard to phase1_server.py (T1.70), replace raw duckdb.connect in _update_doc_status with registry method (T1.71), enforce DiscoveryInput/Output and ParserInput/Output contracts in orchestrator phases (T1.72), persist checkpoint JSON to disk in _run() thread (T1.73). |
| 3.23    | 2026-07-08 | System | Added T1.74 (cross-platform path compatibility) addressing 4 gaps: unanchored relative paths in phase1_server.py, backslash paths in _handle_config_paths, EKSPaths.to_dict() using str() not as_posix(), and context.py checkpoint serialization. |
| 0.1     | 2026-06-11 | System | Initial phase workplan draft for approval     |
| 0.2     | 2026-06-11 | System | Added Section 7b: Proposed Project Folder Structure (full tree across all phases); added eks.yml task; fixed duplicate T1.5 numbering |
| 0.3     | 2026-06-11 | System | T1.1 complete: EKS folder scaffolding created. T1.2 complete: eks.yml created with all Phase 1–5 dependencies. Log files created. |
| 0.4     | 2026-06-15 | System | Remediation: created missing `__init__.py` files (I001); generated Phase 1 test report (I002); migrated `schema_loader.py` and `verify_schema_metadata.py` from deprecated `RefResolver` to `referencing` library (I003); logged all issues to `eks/log/issue_log.md` |
| 0.5     | 2026-06-15 | System | Added universal plant item asset schema (R36): 11 reusable fragment definitions covering all 7 datadrop categories. Appendix A added to workplan with fragment tables, type composition map, relationship graph, and column normalization. |
| 0.6     | 2026-06-15 | opencode | Created and validated actual schema files: `eks_asset_base_schema.json` (11 fragment $defs), `eks_asset_setup_schema.json` (registry + normalization declarations), `eks_asset_config.json` (14 AT_ mappings + 7-sheet column map). Appendix A extracted to stand-alone file. Fixed "10 fragments"→"11 fragments" in 4 locations. |
| 0.7     | 2026-06-16 | System | Gap analysis against actual datadrop Excel. Added 2 new fragments: `specialist_equipment` (A2.12) and `motor_control` (A2.13). Expanded `actuator` fragment with full actuator manufacturer+lifecycle block. Fragment count: 11 → 13. Updated T1.17, success criteria, and deliverables accordingly. |
| 0.8     | 2026-06-17 | System | Added R39: zero-code asset extensibility. Added T1.20: update 3 asset schema files with gap analysis findings (13 fragments, expanded fields, conditional_fragments structure). Phase 1 status set to PARTIAL pending T1.20 completion. |
| 0.9     | 2026-06-18 | System | T1.20 complete: all 3 asset schema files updated and validated. Added asset schema + R39 test cases to test_phase1.py. Updated update_log.md (U017-U021) and issue_log.md (I004 resolved, I005 added). Updated phase_1_foundation_report.md to v0.2. Marked eks_config.json placeholder data. Phase status set to COMPLETE. |
| 1.0     | 2026-06-18 | System | Added T1.21: Document Registry Remediation (G1-G3 gaps identified in Appendix B). Reverted status to PARTIAL. |
| 1.1     | 2026-06-18 | System | Added T1.22: Extended Document Metadata Schema & Migration logic (11 new fields, JSON array support). |
| 1.2     | 2026-06-16 | System | Review corrections: fixed v1.1 date typo; added R36 and R39 to Section 4 scope table; corrected `pipeline_route.p_and_id_files` to array in Appendix A; added `submergence_min` overlap note in A2.12; renumbered B11/B12 → B5/B6 in Appendix B; clarified `asset_tags` as VARCHAR JSON string. |
| 1.3     | 2026-06-16 | System | Added T1.23–T1.26 for dynamic ISO 15926-aligned ontology. Set phase status to PARTIAL. |
| 1.4     | 2026-06-16 | System | Ontology Option C gap closure: added `rdflib` to eks.yml dependency note in T1.2; added SHACL constraint reference to T1.23; added T1.27 (ontology_class_map planning in eks_asset_config.json); added `eks_ontology_schema.json` SHACL note to files table. |
| 1.5     | 2026-06-18 | Gemini CLI | Phase 1 marked COMPLETE. T1.23–T1.27 pass: ontology schema/config implemented, schema_loader extended with cross-validation, asset fragments categorized (functional/physical) and linked to ontology classes. |
| 1.6     | 2026-06-18 | Gemini CLI | Added T1.28: Embedded Relationship Metadata in Asset Schemas per AGENTS.md Section 2 & 4. |
| 1.7     | 2026-06-18 | Gemini CLI | Added T1.29: Document Ontology & Mapping Metadata (Triggers for SUPERSEDES, Asset Tag Linking) to Phase 1 foundation per approved Document Ontology implementation (U036). |
| 1.8     | 2026-06-19 | opencode | Added T1.30 (error code taxonomy schema), T1.31 (pipeline message catalog schema), T1.32 (error/message manager modules) for R51 Pipeline Messages & Error Codes. Added Appendix D reference. |
| 1.9     | 2026-06-19 | opencode | Updated T1.30–T1.32 for 6-dimension health scoring (added structural completeness), structure_detector.py module, document_elements table. Updated R51 description. |
| 2.0     | 2026-06-22 | opencode | Implemented T1.30 (error code schema), T1.31 (message schema), T1.32 (error_manager, message_manager, health_scorer, structure_detector, document_elements). All 47 new tests + 20 existing tests passing. Phase 1 complete. |
| 2.1     | 2026-06-22 | opencode | Added T1.33: Reorganize core, asset, and ontology schemas/configs under `eks/config/schemas/` to comply with DCC and AGENTS.md pattern. Set status to PARTIAL. |
| 2.2     | 2026-06-22 | opencode | T1.33 complete: all 13 schema/config files confirmed in `eks/config/schemas/`; `test_phase1.py` updated to resolve `config_dir` to `eks/config/schemas/` (schemas/-first fallback chain); section 7b folder tree updated to reflect canonical layout; issue log (I010) and update log (U051) updated. Phase 1 status COMPLETE. |
| 2.3     | 2026-06-22 | opencode | Added T1.34: Reorganize document schema into dedicated 3-layer pattern (`eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json`) following asset schema pattern. Separates document definitions from pipeline config. Set status to PARTIAL. |
| 2.4     | 2026-06-22 | opencode | T1.34 complete: Created 3 doc schema files (`eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json`). Removed `document_metadata_def` and `project_metadata_def` from `eks_base_schema.json`. Updated `schema_loader.py` to load and validate doc schemas. Added 6 new tests verifying doc schema existence, definitions, validation, and pipeline base cleanup. All 73 tests pass. Phase 1 status COMPLETE. |
| 2.5     | 2026-06-22 | opencode | **T1.35 COMPLETE**: Enhanced Document Schema v2 — Added 3 enums (7 doc type codes, 5 file type codes, 8 element type codes); created 3 registries (document_type, file_type, element_type) in `eks_doc_config.json`; refactored element_expectations keyed by doc type codes with backward-compatible `cover_type` field; added `_validate_doc_registries()` to schema_loader (ontology class, parser import, element type, expectation key validation); added 6 new tests; created DGN/DWG parser stubs; added DataSheet/OpsManual to ontology with document_type_mapping; 31/31 tests pass. Phase 1 COMPLETE. |
| 3.0     | 2026-06-22 | opencode | Added T1.36–T1.40: Pipeline integration workflow — auto-DDL from schema, file scanner with type validation, parser router, pipeline orchestrator, manual review workflow. Added R54–R58 to scope. Status: PARTIAL. |
| 3.1     | 2026-06-22 | opencode | T1.36 complete: `SchemaToDDL` auto-generates DDL from JSON schema; `registry.py` refactored with generated DDL, `sync_schema()`, schema-derived `COLUMN_ALLOWLIST`; 8 new tests; 39/39 pass. |
| 3.2     | 2026-06-22 | opencode | T1.37–T1.40 complete: FileScanner (T1.37), ParserRouter (T1.38), PipelineOrchestrator (T1.39), ManualReviewManager (T1.40). Fixed DGN/DWG stubs. All R54–R58 PASS. 53/53 tests pass. Phase 1 COMPLETE. |
| 3.3     | 2026-06-22 | opencode | Added §14: Phase 1 Pipeline Architecture (detailed Mermaid diagram) moved from master workplan §10.2. |
| 3.4     | 2026-06-22 | opencode | T1.41 complete: Fixed error/message schemas to follow AGENTS.md §9 3-layer pattern. Created `eks_error_setup_schema.json` and `eks_message_setup_schema.json` (allOf + $ref to base). Cleaned config files (removed $schema/$id/title/description/version/type). Updated `eks_error_code_base.json` function_code enum (added X, G, E). Updated `schema_loader.py` with error/message validation methods. I014 resolved. 53/53 tests pass. |
| 3.5     | 2026-06-23 | opencode | Added §12 success criteria: data challenges documented (I015–I021), DGN gap identified as risk. Added §13 deliverable: data challenge analysis. |
| 3.6     | 2026-06-23 | opencode | Added T1.41–T1.47 to task list (§8): error/message schema fix, 4 fragment schemas (project, discipline, department, facility), base schema definitions, config/setup updates, validation tests. Updated §9 files table (+15 entries). Updated §12 success criteria (+13 items). Updated §13 deliverables (+6 items). Test count: 53 → 59. Schema count: 17 → 21. I005 resolved. |
| 3.7     | 2026-06-23 | opencode | Added T1.48: Schema audit — duplicate defs, parser path mismatch, missing parsers, missing `$schema` in error/message configs. Logged I022–I027. |
| 3.8     | 2026-06-23 | opencode | T1.48 complete: fixed duplicate defs, parser paths, missing parsers. Reverted metadata fields from config files (broke `additionalProperties: false` validation). Logged I028. All 114 tests pass. |
| 3.9     | 2026-06-23 | opencode | Three optional fixes: (1) I027 — aligned error/message base schema URIs to filename-based pattern; (2) Consolidated `verbosity_level` enum into shared `eks_base_schema.json#/definitions/verbosity_level`; (3) Added shared `document_relationship_trigger_map` def — both asset and doc configs now `$ref` it. Added `base_schema` to all validation registries in `schema_loader.py` and tests. I027 resolved, I028 updated. Bumped 6 file versions. 114/114 tests pass. |
| 3.10 | 2026-06-24 | opencode | Consolidated T1.30–T1.32 test report into `phase_1_foundation_report.md` (v1.4). Removed `phase_1_t130_t132_report.md`. Updated deliverable list to reflect consolidation. |
| 3.11 | 2026-06-24 | opencode | T1.49: Cross-cutting workplan remediation — replaced `agent_rule.md` with `AGENTS.md` across 11 files; converted Linux absolute paths to relative; fixed stale statuses; reordered master sections; fixed Phase 2 dates; filled Phase 3 gaps; added reranker criteria and eval metrics to Phase 4; resolved frontend tech, auth note, expanded Mermaid for Phase 5. |
| 3.12 | 2026-06-24 | opencode | T1.50: Base schema SSOT enforcement — stripped `document_relationship_trigger_map` to shape-only (U086); moved `revision_id` to doc schema set + added `revision_validation` 3-layer chain (U087); removed `revision_pattern` from `project_rules`. Updated `ConfigRegistry` to resolve `$ref` entries on-the-fly. I031–I032 resolved. 114/114 tests pass. |
| 3.13 | 2026-06-25 | opencode | T1.51 implemented: `asset_context` fragment added to all 3 asset schema files (base 1.3.0, setup 1.3.0, config 1.4.0) with extensible location_hierarchy (`additionalProperties: true`), extensible system_hierarchy (`additionalProperties: true`), project_context, asset_relationships, document_relationships, lifecycle_context. Location as link context (no keytag). Updated schema_inheritance_chain.md v1.11. Updated tests: 118/118 pass. Phase 1 marked COMPLETE. |
| 3.14 | 2026-06-25 | opencode | Integrated full Schema Inheritance Chain from `schema_inheritance_chain.md` (v1.11) into `appendix_e_schema_design.md` (v0.6) as E11–E12. Updated E1 (23 files, asset_context), E2 Mermaid (14 fragments), E5.1/5.3 (14 fragments, 55 base defs). Archived `schema_inheritance_chain.md` → `archive/`. U089 logged. |
| 3.15 | 2026-06-26 | Cascade | Added Section 16: Phase 1.2 Foundation Enhancement (Future Work) with 19 tasks for applying universal pipeline architecture patterns (PipelineContext, Dependency Injection, Phase-Based Orchestration, Telemetry Heartbeat, Standardized Engine I/O, UI Contracts, Project Setup Validation). Tasks derived from Appendix F. Updated Section 5 index to include new section. |
| 3.16 | 2026-06-29 | System | Refactored Phase 1.2 scope: kept only I/O check, test, and UI design tasks (T1.2.1-T1.2.5). Moved unrelated Appendix F architecture tasks (PipelineContext, Dependency Injection, Telemetry, etc.) to Phase 1 main task breakdown as T1.52-T1.66. Updated Files and Modules section accordingly. |
| 3.17 | 2026-06-30 | opencode | Fixed 3 issues: (1) Phase status changed from COMPLETE to PARTIAL reflecting T1.52-T1.66 pending; (2) T1.35.1-T1.35.5 sub-task statuses corrected to match actual implementation (3x ✅, 2x 🔶); (3) Removed `$schema` from `eks_error_config.json` and `eks_message_config.json` (violated `additionalProperties: false` in setup schemas, breaking all 63 phase 1 tests). System back to 118/118 tests pass. I045 resolved. |
| 3.18 | 2026-06-30 | opencode | Migrated Section 16 (I/O Contract tasks) to phase_1.2_interactive_ui_workplan.md as Phase 1.2.0. Removed section from this workplan. Updated index and renumbered Section 17→16. |
| 3.19 | 2026-06-30 | System | Completed Appendix F architecture integration tasks T1.52-T1.66: Implemented EKSPipelineContext, BaseEngine, TelemetryHeartbeat, Multi-Stage Validation, CLI Entry Points, HTTP API Endpoints, Checkpoint State Serialization, Factories (ParserFactory, HealthScorerFactory, StructureDetectorFactory), updated ParserRouter to use factories, enhanced PipelineOrchestrator with checkpoints and rollback, implemented Project Setup Validator and schema. Phase 1 status COMPLETE. |
| 3.20 | 2026-06-30 | opencode | Added T1.67: Integrate `project_setup.json` into core eks_base/setup/config schemas per AGENTS.md §9 3-layer pattern. Logged I046. Phase 1 status set to PARTIAL pending review. |
| 3.21 | 2026-06-30 | opencode | T1.67 complete: Added 4 defs to `eks_base_schema.json` v1.6.0; added `project_setup` property to `eks_setup_schema.json` v1.3.0; added values to `eks_config.json` v1.4.0; archived `project_setup.json`; refactored `setup_validator.py` to load from ConfigRegistry. I046 resolved. 118/118 tests pass. Phase 1 COMPLETE. |
| 3.22 | 2026-07-01 | opencode | Enhanced §14 Mermaid diagram with explicit function call annotations per pipeline step. Added §14.1 Function Table (11 module tables) per AGENTS.md §17 — covers all pipeline-critical functions with description, parameters, return values, dependencies, error handling, and tracing. |

---

## 3. Objective

- Create the EKS project folder structure compliant with AGENTS.md
- Design and implement the canonical schema (base/setup/config pattern)
- Build the document registry (metadata DB) with full CRUD support
- Implement plug-in document parsers: PDF, DOCX, XLSX
- Implement revision management: preserve all revisions, latest revision flag
- Establish tiered logging (levels 0–3), debug object, and structured trace table
- Implement SSOT global parameter registry via schema-driven config

---

## 4. Scope Summary

| ID  | Category             | Requirement               | Details                                                                                      | Related Tasks | Status     |
| :-- | :------------------- | :------------------------ | :------------------------------------------------------------------------------------------- | :------------ | :--------: |
| R01 | Knowledge Base       | Document Ingestion        | Ingest PDF, DOCX, XLSX formats via plug-in parsers (DWG/DGN deferred to Phase 3)            | T1.9–T1.12    | ✅ PASS |
| R02 | Knowledge Base       | Document Registry         | Store document metadata in structured DB (PostgreSQL/DuckDB)                                 | T1.7, T1.21, T1.22, T1.71 | ✅ PASS |
| R06 | Schema               | SSOT Schema-Driven Design | Metadata schema reuses dcc/config/schemas pattern; project_setup_base / setup / config       | T1.3–T1.6, T1.14, T1.33, T1.42–T1.47, T1.50 | ✅ PASS |
| R07 | Schema               | Canonical Data Model      | Foundation for metadata schemas, retrieval filters, relationship graphs, future integrations | T1.3–T1.5     | ✅ PASS |
| R08 | Schema               | Schema Fragment Pattern   | Fragment-based, inheritance (base + project) pattern per AGENTS.md Section 2                | T1.3–T1.5     | ✅ PASS |
| R09 | Metadata             | Project & Document Metadata | project_title, project_number, area, discipline, department, document_type, document_number | T1.3–T1.5     | ✅ PASS |
| R21 | Revision Management  | Preserve All Revisions    | All document revisions retained; no overwrite                                                | T1.8           | ✅ PASS |
| R22 | Revision Management  | Latest Revision Filtering | Support filtering to latest revision only                                                    | T1.8           | ✅ PASS |
| R26 | Plug-in Architecture | Document Parser Plugins   | Plug-in parsers for PDF, DOCX, XLSX (abstract base + concrete implementations)              | T1.9–T1.12, T1.59, T1.62 | ✅ PASS |
| R29 | Infrastructure       | Metadata DB               | PostgreSQL or DuckDB for structured metadata storage                                        | T1.7           | ✅ PASS |
| R33 | Logging & Debug      | Tiered Logging (levels 0–3) | Per AGENTS.md Section 6: status, warning, trace levels                                   | T1.13, T1.69  | ✅ PASS |
| R34 | Logging & Debug      | Debug Object & Trace Table | Debug dict → debug_log.json, trace table with timestamps                                   | T1.13          | ✅ PASS |
| R35 | Module Design        | SSOT Global Parameters    | All global keys, paths, codes in schema-driven config; no hardcoding                        | T1.14, T1.50  | ✅ PASS |
| R36 | Asset Schema         | Universal Plant Item Schema | 13 reusable fragment definitions covering all 7 datadrop categories; base/setup/config pattern | T1.17–T1.20, T1.51 | ✅ PASS |
| R39 | Asset Schema         | Zero-Code Asset Extensibility | New asset types added via config only; no code changes required; `conditional_fragments` structure | T1.20 | ✅ PASS |
| R44 | Schema               | ISO 15926 Ontology Integration | Define dynamic, config-driven ontology schema (classes, properties, relationships) for EKS | T1.23–T1.29  | ✅ PASS |
| R51 | Logging & Debug      | Pipeline Messages & Error Codes | Schema-driven error catalog (system + data domains), pipeline message catalog, per-document 6-dimension health scoring (completeness, confidence, structural, source, xref, consistency), structural elements table (`document_elements`), run_id correlation (T1.69), ErrorManager/MessageManager activation in server (T1.75), persisted debug/message/status JSON logs to `eks/output/` (T1.76) per AGENTS.md §19 | T1.30–T1.32, T1.41, T1.60, T1.68, T1.69, T1.75, T1.76 | ✅ PASS |
| R52 | Schema               | Document Schema Reorganization | Separate document definitions from pipeline config into dedicated 3-layer pattern (`eks_doc_base/setup/config`); align with asset schema pattern for SSOT compliance | T1.34 | ✅ PASS |
| R53 | Schema               | Enhanced Document Schema v2    | Document type codes (7), file type codes (5), element type codes (8) with enums; document type registry (ontology mapping, file expectations); file type registry (parser mapping); element type registry (descriptions, source, Phase 2/3 uses); element expectations keyed by document type | T1.35.1–T1.35.6 | ✅ PASS |
| R54 | Infrastructure       | Auto-DDL Generation | Auto-generate SQL DDL from JSON schema `definitions`; replaces hard-coded DDL in `registry.py`; supports `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN IF NOT EXISTS` | T1.36 | ✅ PASS |
| R55 | Infrastructure       | File Scanner | Walk project directory; validate extensions against `file_type_registry`; match expected types against `document_type_registry[].expected_file_types`; register placeholder rows with `extract_status = 'pending'` | T1.37 | ✅ PASS |
| R56 | Plug-in Architecture | Parser Router | Map `file_type` → parser class from `file_type_registry`; instantiate parser; call `parse()` + `extract_metadata()` + `StructureDetector.detect()` in sequence | T1.38 | ✅ PASS |
| R57 | Pipeline             | Pipeline Orchestration | Coordinate scan → register → route → parse → detect → score → update; error handling, logging, rollback per AGENTS.md §12 | T1.39, T1.52, T1.54, T1.58, T1.63, T1.64, T1.72, T1.73 | ✅ PASS |
| R58 | Pipeline             | Manual Review Workflow | Surface flagged docs (`extract_status != 'success'`); correct metadata; confirm elements; recalculate score; lock for Phase 2 | T1.40 | ✅ PASS |
| R99 | Foundation           | Project Infrastructure & Compliance | Folder scaffolding, environment, tests, logs, schema migration, audit, cross-cutting remediation, architectural patterns (BaseEngine, Validator, CLI, HTTP, factories, setup validation), data_dir traversal guard (T1.70), ErrorManager/MessageManager server activation (T1.75), persisted debug/message/status logs (T1.76) | T1.1, T1.2, T1.15, T1.16, T1.48, T1.49, T1.53, T1.55–T1.57, T1.61, T1.65–T1.67, T1.70, T1.74, T1.75, T1.76 | ✅ PASS |

**Status Legend:** ✅ PASS | 🔶 PARTIAL | ❌ FAIL | 🔷 PLANNED

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Objective](#3-objective)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Evaluation and Alignment](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies](#7-dependencies-with-other-tasks)
- [7b. Proposed Project Folder Structure](#7b-proposed-project-folder-structure)
- [8. Task Breakdown](#8-task-breakdown)
- [9. Files and Modules](#9-files-and-modules-to-createupdate)
- [10. Risks and Mitigation](#10-risks-and-mitigation)
- [11. Potential Future Issues](#11-potential-future-issues)
- [12. Success Criteria](#12-success-criteria)
- [13. Deliverables](#13-deliverables)
- [14. Phase 1 Pipeline Architecture (Detailed)](#14-phase-1-pipeline-architecture-detailed)
- [15. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89)](#15-initiation-integrity-hardening--harmonization-t177t189)
- [16. Phase 1.3 — Initiation Schema & Validation Harmonization (T1.84–T1.89)](#16-phase-13--initiation-schema--validation-harmonization-t184t189)
- [17. Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)](#17-initiation-config-flattening--dcc-project_config-pattern-t190t195)
- [18. Schema Discovery & Registration — Discovery-Driven Loading (T1.96)](#18-schema-discovery--registration--discovery-driven-loading-t196)
- [19. System Parameters — SSOT Centralization (T1.97)](#19-system-parameters--ssot-centralization-t197)
- [20. References](#20-references)

---

## 6. Evaluation and Alignment with Existing Architecture

- **Schema pattern**: Directly adopts `project_setup_base.json / project_setup.json / project_config.json` from `dcc/config/schemas`
- **Logging**: Directly adopts tiered logging and debug object from `dcc/workflow/core_engine/` patterns
- **Module design**: SSOT global parameters via schema-driven config per AGENTS.md Section 4
- **New**: Document registry with metadata DB is new to this workspace; no prior precedent in DCC

---

## 7. Dependencies with Other Tasks

1. **AGENTS.md** — Governs all coding standards, module design, logging
2. **dcc/config/schemas** — Schema base/setup/config pattern to replicate
3. **External**: DuckDB (preferred for dev) or PostgreSQL for metadata DB
4. **Next Phase**: Phase 2 depends on document registry and parsers from this phase

---

## 7b. Proposed Project Folder Structure

The EKS project folder follows the standard structure defined in `AGENTS.md`. All folders are created in Phase 1 (T1.1) as empty scaffolding so subsequent phases can populate them without restructuring.

```
eks/
├── eks.yml                         # Conda environment file (all phases)
├── readme.md                       # Project overview (existing)
│
├── archive/                        # Archived/superseded files
│
├── config/                         # Schema and configuration files
│   └── schemas/                    # All schema and config JSON files (AGENTS.md §9)
│       ├── eks_base_schema.json        # Core schema — definitions
│       ├── eks_setup_schema.json       # Core schema — property declarations
│       ├── eks_config.json             # Core config values (paths, DB, providers)
│       ├── eks_asset_base_schema.json  # Asset schema — 13 fragment definitions
│       ├── eks_asset_setup_schema.json # Asset schema — declarations
│       ├── eks_asset_config.json       # Asset config — 14 AT_ type mappings
│       ├── eks_doc_base_schema.json    # Document schema — column definitions
│       ├── eks_doc_setup_schema.json   # Document schema — table declarations
│       ├── eks_doc_config.json         # Document config — DB, thresholds
│       ├── eks_ontology_base_schema.json  # Ontology schema — base definitions
│       ├── eks_ontology_setup_schema.json # Ontology schema — property declarations
│       ├── eks_ontology_config.json    # Ontology config — ISO 15926-aligned classes
│       ├── eks_error_code_base.json    # Error code taxonomy base schema
│       ├── eks_error_config.json       # Error code catalog (65 codes)
│       ├── eks_message_base.json       # Pipeline message base schema
│       └── eks_message_config.json     # Pipeline message catalog (25 messages)
│
├── data/                           # Input documents for ingestion
│   └── (user-supplied engineering documents)
│
├── output/                         # Pipeline outputs (debug logs, reports, graphs)
│   └── debug_log.json              # Debug object output
│
├── engine/                         # Core processing modules (all phases)
│   ├── __init__.py                 # Package init with version
│   │
│   ├── core/                       # Foundation: registry, revision, config (Phase 1)
│   │   ├── __init__.py
│   │   ├── registry.py             # Document registry — metadata DB CRUD
│   │   ├── revision.py             # Revision management logic
│   │   ├── config_registry.py     # SSOT global parameter access
│   │   ├── schema_to_ddl.py       # Auto-generate SQL DDL from JSON schema (T1.36)
│   │   ├── file_scanner.py        # Directory walk, type validation, placeholder registration (T1.37)
│   │   └── pipeline_orchestrator.py # Pre-parse → parse → score → review coordinator (T1.39)
│   │
│   ├── logging/                    # Tiered logging infrastructure (Phase 1)
│   │   ├── __init__.py
│   │   └── logger.py               # Levels 0–3, debug object, trace table
│   │
│   ├── parsers/                    # Plug-in document parsers (Phase 1 + 3)
│   │   ├── __init__.py
│   │   ├── base_parser.py          # Abstract parser interface
│   │   ├── pdf_parser.py           # PDF parser
│   │   ├── docx_parser.py          # DOCX parser
│   │   ├── xlsx_parser.py          # XLSX parser
│   │   ├── dwg_parser.py           # DWG stub (Phase 3)
│   │   ├── dgn_parser.py           # DGN stub (Phase 3)
│   │   └── parser_router.py        # File_type → parser class routing (T1.38)
│   │
│   ├── chunking/                   # Chunking strategies and registry (Phase 2)
│   │   ├── __init__.py
│   │   ├── chunker.py              # Abstract + size-based chunker
│   │   ├── section_chunker.py      # Section-aware chunker
│   │   └── chunk_registry.py       # Parent-child chunk management
│   │
│   ├── embedding/                  # Embedding providers (Phase 2)
│   │   ├── __init__.py
│   │   ├── base_embedder.py        # Abstract embedder interface
│   │   ├── openai_embedder.py      # OpenAI provider
│   │   ├── ollama_embedder.py      # Ollama provider
│   │   └── hybrid_strategy.py      # Contextual header + embedding pipeline
│   │
│   ├── vector_store/               # Vector DB interface (Phase 2)
│   │   ├── __init__.py
│   │   ├── base_vector_store.py    # Abstract vector store interface
│   │   └── qdrant_store.py         # Qdrant implementation
│   │
│   ├── graph/                      # Knowledge graph (Phase 3)
│   │   ├── __init__.py
│   │   ├── graph_store.py          # Abstract graph store interface
│   │   ├── neo4j_store.py          # Neo4j implementation
│   │   ├── graph_schema.py         # Node labels and relationship types
│   │   └── relationship_builders.py # Doc-to-doc, doc-to-object builders
│   │
│   ├── extractors/                 # Engineering object metadata extractors (Phase 3)
│   │   ├── __init__.py
│   │   ├── base_extractor.py       # Abstract extractor interface
│   │   ├── equipment_extractor.py  # Equipment metadata
│   │   ├── instrument_extractor.py # Instrument metadata
│   │   ├── valve_extractor.py      # Valve metadata
│   │   └── pipeline_extractor.py   # Pipeline metadata
│   │
│   ├── retrieval/                  # Retrieval and scoring pipeline (Phase 4)
│   │   ├── __init__.py
│   │   ├── metadata_filter.py      # Metadata + revision-aware filtering
│   │   ├── graph_expander.py       # Graph relationship expansion
│   │   ├── vector_search.py        # Qdrant vector similarity search
│   │   ├── keyword_search.py       # BM25/full-text keyword search
│   │   ├── hybrid_search.py        # Merge vector + keyword results
│   │   ├── scorer.py               # Candidate scoring
│   │   ├── reranker.py             # Reranking top-k candidates
│   │   ├── context_assembler.py    # Context window assembly
│   │   ├── llm_interface.py        # Abstract LLM provider interface
│   │   ├── openai_llm.py           # OpenAI LLM provider
│   │   ├── ollama_llm.py           # Ollama LLM provider
│   │   └── pipeline.py             # End-to-end pipeline orchestrator
│   │
│   └── cache/                      # Retrieval cache (Phase 5)
│       ├── __init__.py
│       ├── retrieval_cache.py      # Abstract cache interface
│       ├── memory_cache.py         # In-memory LRU cache
│       └── redis_cache.py          # Redis cache (optional)
│
├── ui/                             # User interface (Phase 5)
│   ├── app.py                      # FastAPI/Flask application entry point
│   ├── routes/
│   │   ├── query.py                # /query endpoint
│   │   ├── ingest.py               # /ingest endpoint
│   │   └── status.py               # /status, /health endpoints
│   ├── static/                     # Frontend assets (CSS, JS)
│   └── templates/
│       └── index.html              # Main query interface
│
├── test/                           # Unit and integration tests (all phases)
│   ├── test_phase1.py              # Phase 1 tests
│   ├── test_phase2.py              # Phase 2 tests
│   ├── test_phase3.py              # Phase 3 tests
│   ├── test_phase4.py              # Phase 4 tests
│   └── test_phase5.py              # Phase 5 tests
│
├── docs/                           # Documentation
│   └── eks_system_documentation.md # 16-section system docs (Phase 5)
│
├── log/                            # Issue, update, and test logs
│   ├── issue_log.md
│   └── update_log.md
│
└── workplan/                       # Workplans and reports
    ├── eks_system_workplan.md      # Master index workplan
    ├── phase_1_foundation_workplan.md
    ├── phase_2_chunking_embedding_workplan.md
    ├── phase_3_knowledge_graph_workplan.md
    ├── phase_4_retrieval_pipeline_workplan.md
    ├── phase_5_ui_integration_workplan.md
    └── reports/                    # Phase test reports
        ├── phase_1_foundation_report.md
        ├── phase_2_chunking_embedding_report.md
        ├── phase_3_knowledge_graph_report.md
        ├── phase_4_retrieval_pipeline_report.md
        └── phase_5_ui_integration_report.md
```

**Notes:**
- Folders for all phases (chunking, embedding, graph, retrieval, cache, ui) are created as **empty scaffolding** in Phase 1 (T1.1) to establish the full layout upfront
- Each phase populates only its designated folders; no folder restructuring is needed later
- `data/` is for raw input documents supplied by the user; not committed to version control
- `output/` holds runtime artifacts (debug logs, exported graphs); not committed to version control

---

## 7c. Detailed Schema Design (T1.3 - T1.5)

Following the standards in `AGENTS.md` Section 2 (Schema Fragments & Inheritance) and Section 4 (SSOT), the EKS canonical schema is designed across three files to separate definitions, declarations, and actual values.

### T1.3: `eks_base_schema.json` (Definitions)
- **Purpose**: Store reusable fragments and type definitions (`definitions` or `$defs`).
- **Standard**: Flat structure, use array of objects, `additionalProperties: false`.
- **Key Definitions**:
    - `discipline_code`: Enum (PI, EL, IN, CI, ME, etc.) for engineering discipline identification.
    - `revision_id`: String with regex pattern (e.g., `^[A-Z0-9]{1,2}$`) for strict revision control.
    - `ProjectMetadata`: Shared fragment for project identification (title, number, area, discipline, department).
    - `DocumentMetadata`: Shared fragment for document identification (type, number, revision, status, latest_flag).
    - `EngineeringObject`: Fragment for engineering items (tag, object_type, properties dict).
    - `SourceTraceability`: Fragment for chunk source tracking (file_path, page, section, chunk_id).
        - **Asset Schema Fragments (R36, R39)** — 13 fragments for universal plant item schema (see [appendix_a_asset_schema.md](appendix_a_asset_schema.md)):
        - `item_core_def`, `process_conditions_def`, `manufacturer_def`, `asset_lifecycle_def`, `control_system_def`, `piping_connection_def`, `valve_internals_def`, `actuator_def` (full manufacturer+lifecycle block), `rotating_equipment_def`, `instrumentation_def`, `pipeline_route_def`, `specialist_equipment_def` (UV/filtration/conveyor), `motor_control_def` (starter type, MCC feed). `conditional_fragments` structure added for zero-code extensibility (R39).

### T1.4: `eks_setup_schema.json` (Declarations / Properties)
- **Purpose**: Define the structure and metadata of the system configuration (`properties`).
- **Standard**: One-to-one match with `eks_base_schema.json` via `$ref`.
- **Sections**:
    - `global_paths`: Mandatory directory paths (data, output, archive, config).
    - `registry`: Metadata database configuration (type, connection_string, timeout).
    - `parsers`: Configuration for document parser plugins (enabled list, specific parser settings).
    - `embedding`: SSOT for embedding provider settings (active_provider, model_name, dimensions).
    - `vector_store`: Vector database configuration (qdrant_url, collection_name, distance_metric).
    - `graph_db`: Knowledge graph settings (neo4j_uri, credentials, relationship_labels).
    - `logging`: Tiered logging configuration (default_level, debug_file_path).
    - `asset_type_registry`: Tag-type-to-fragment mapping registry declaring which fragments compose each AT_ category.

### T1.5: `eks_config.json` (Actual Values / Config)
- **Purpose**: Store the actual runtime values used by the EKS engine.
- **Standard**: Validates strictly against `eks_setup_schema.json`.
- **Example SSOT Values**:
    - `registry.type`: "duckdb"
    - `registry.connection`: "output/eks_registry.db"
    - `embedding.active_provider`: "openai"
    - `vector_store.collection_name`: "eks_chunks"
    - `logging.default_level`: 1
    - `project_assets.WSD11.datadrop_path`: "data/twrp/datadrop/Datadrop Summary.xlsx"
    - `asset_type_registry.AT_EQUIP.fragments`: ["core", "process_conditions", "manufacturer", "asset_lifecycle", "control_system", "rotating_equipment"]

---

## 7d. Independent Parser Module Architecture (T1.8 - T1.11)

To support diverse engineering document types (PDF, Word, Excel, AutoCAD, DGN) while maintaining system extensibility, EKS implements a **Plug-in Parser Architecture**.

### 1. The Parser Interface (`BaseParser`)
Every independent parser module must inherit from the `BaseParser` abstract class located in `engine/parsers/base_parser.py`.
- **`parse(file_path)`**: Returns a list of standardized content dictionaries.
- **`extract_metadata(file_path)`**: Returns file-level metadata (e.g., author, system properties).
- **`get_source_location(element_id)`**: Maps content back to its physical/logical source (e.g., page, sheet, layer, coordinates).

### 2. Standardized Output Format
Regardless of the file type, parsers must output a unified structure to prevent downstream logic pollution:
- **Textual Data**: Content string with associated formatting hints.
- **Structural Metadata**: Section headings, table identifiers, or sheet names.
- **Source Context**: Page numbers (PDF/DOCX), Cell references (XLSX), or Layer names/Coordinates (DWG/DGN).

### 3. Schema-Driven Discovery (SSOT)
Parsers are mapped to file extensions in `eks_config.json`. The EKS engine uses this mapping to dynamically instantiate the correct parser at runtime:
```json
"parsers": {
    ".pdf": "engine.parsers.pdf_parser.PDFParser",
    ".docx": "engine.parsers.docx_parser.DocxParser",
    ".xlsx": "engine.parsers.xlsx_parser.XlsxParser",
    ".dwg": "engine.parsers.dwg_parser.DWGParserStub",
    ".dgn": "engine.parsers.dgn_parser.DGNParserStub"
}
```

### 4. Implementation Strategy
- **Phase 1**: Full implementation of PDF, DOCX, and XLSX parsers.
- **CAD Support**: `DWGParserStub` and `DGNParserStub` will be created to define the interface requirements, returning "Format supported - Implementation Pending" for future Phase 3 integration.

---

## 8. Task Breakdown

**Timeline**: TBD — starts after approval  
**Estimated Effort**: Medium (foundation build)

| # | Task | Details | Scope | Status | Timestamp |
| :- | :--- | :------ | :---- | :----: | :-------- |
| T1.1 | Create EKS folder structure | archive, config, data, output, engine, log, docs, workplan, test, ui | R99 | ✅ | — |
| T1.2 | Create environment file `eks.yml` | Conda environment with all Phase 1–5 dependencies (Python, DuckDB, FastAPI, parsers, vector DB, graph DB clients, embedding providers, rdflib for ontology OWL/Turtle file parsing) | R99 | ✅ | — |
| T1.3 | Design canonical schema — base | `eks_base_schema.json`: definitions for all shared types & project-scoped fragments | R06, R07, R08, R09 | ✅ | — |
| T1.4 | Design canonical schema — setup | `eks_setup_schema.json`: registry-based declarations for project-scoped config | R06, R07, R08, R09 | ✅ | — |
| T1.5 | Design canonical schema — config | `eks_config.json`: project-namespaced values (discipline/rules registries) | R06, R07, R08, R09 | ✅ | — |
| T1.6 | Implement schema loader | Load and resolve base/setup/config with $ref support (reuse dcc pattern) | R06 | ✅ | — |
| T1.7 | Implement document registry | CRUD interface for document metadata backed by DuckDB/PostgreSQL | R02, R29 | ✅ | — |
| T1.8 | Implement revision management | Preserve all revisions; is_latest flag; revision chain lookup | R21, R22 | ✅ | — |
| T1.9 | Implement abstract base parser | `base_parser.py`: plug-in interface with parse(), extract_metadata() | R01, R26 | ✅ | — |
| T1.10 | Implement PDF parser | `pdf_parser.py`: extract text, metadata, page numbers | R01, R26 | ✅ | — |
| T1.11 | Implement XLSX parser | `xlsx_parser.py`: extract sheet data, metadata | R01, R26 | ✅ | — |
| T1.12 | Implement DOCX parser | `docx_parser.py`: extract text, metadata, sections | R01, R26 | ✅ | — |
| T1.13 | Implement tiered logger | `logger.py`: levels 0–3, debug object, trace table, depth counter | R33, R34 | ✅ | — |
| T1.14 | Implement SSOT config registry | Global parameter access via schema-driven config; no hardcoding | R06, R35 | ✅ | — |
| T1.15 | Write unit tests | Schema loader, document registry, revision management, parsers, logger | R99 | ✅ | — |
| T1.16 | Create log files | `update_log.md`, `issue_log.md` under `eks/log/` | R99 | ✅ | — |
| T1.17 | Design asset schema — fragment definitions | Add 13 reusable asset fragments to `eks_asset_base_schema.json` (item_core, process_conditions, manufacturer, asset_lifecycle, control_system, piping_connection, valve_internals, actuator, rotating_equipment, instrumentation, pipeline_route, specialist_equipment, motor_control) | R36 | ✅ | — |
| T1.18 | Design asset schema — type registry | Add `asset_type_registry` to `eks_setup_schema.json`; map all 14 AT_ categories to their fragment compositions in `eks_config.json` | R36 | ✅ | — |
| T1.19 | Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | R36 | ✅ | — |
| T1.20 | Update asset schema files for R39 + gap analysis | (1) `eks_asset_base_schema.json`: add `specialist_equipment` and `motor_control` fragment `$defs`; expand `actuator`, `rotating_equipment`, `instrumentation`, `valve_internals` with gap analysis fields. (2) `eks_asset_setup_schema.json`: update fragment enum to 13 names; add `conditional_fragments` object structure to registry. (3) `eks_asset_config.json`: add `conditional_fragments` entries for AT_EQUIP and AT_MOTOR; add missing column normalization entries (manufacturer_fax, valve_internal_type, dual alarm TP columns) | R36, R39 | ✅ | — |
| T1.21 | Document Registry Remediation (G1-G3) | Add `source_type` column (G1); implement column allowlist for `list_documents` (G2); migrate `get_revision_history` sorting to SQL `ORDER BY` (G3). Update schema files accordingly. | R02 | ✅ | — |
| T1.22 | Extended Document Metadata | Implement 11 new fields (Accountability, Quality, Technical groups); support `asset_tags` as JSON array; implement `ALTER TABLE` migration logic in `registry.py` for schema evolution. | R02 | ✅ | — |
| T1.23 | Design ontology schema | `eks_ontology_schema.json`: validate classes, properties, and relationship types; include SHACL constraint definitions for data quality rules (e.g. every PumpTag must have unit and service) | R44 | ✅ | — |
| T1.24 | Create ontology config | `eks_ontology_config.json`: define classes, inheritance, and relationship properties (ISO 15926 aligned) | R44 | ✅ | — |
| T1.25 | Extend schema loader | Update `schema_loader.py` to validate and load the ontology registry dynamically at startup | R44 | ✅ | — |
| T1.26 | Write ontology unit tests | Test ontology schema validation and loading in `test_phase1.py` | R44 | ✅ | — |
| T1.27 | Plan alias-aware ontology mapping | Define alias support and `ontology_class_map` design for `eks_asset_config.json`; document AT_ code-to-ontology class mapping and alias-driven asset onboarding; hold actual schema/code updates pending approval | R44 | ✅ | — |
| T1.28 | Embedded Relationship Metadata | Update `eks_asset_base_schema.json` to annotate relationship-triggering fields; update `eks_asset_config.json` with `relationship_triggers` section mapping fields to graph edges (Flow, Power, Control, Governance, Set Points) | R44 | ✅ | — |
| T1.29 | Document Ontology & Mapping Metadata | Update `eks_ontology_config.json` with Document hierarchy (Drawing, Spec, Manual) and lifecycle relationships (SUPERSEDES, SUPPLEMENTS, REFERENCES_DOC); update `eks_asset_config.json` with `document_triggers` section mapping registry fields to graph edges. | R44 | ✅ | — |
| T1.30 | Error Code Taxonomy Schema | Create `eks/config/schemas/eks_error_code_base.json` (error code format definitions, severity levels, phase/module/function codes) and `eks/config/schemas/eks_error_config.json` (full system + data error catalog including structural error codes P3-E-E-0010–0017). Follow DCC pattern from `dcc/config/schemas/error_code_base.json`. | R51 | ✅ | — |
| T1.31 | Pipeline Message Catalog Schema | Create `eks/config/schemas/eks_message_base.json` (message ID format, verbosity levels, categories) and `eks/config/schemas/eks_message_config.json` (milestone, status, progress, warning, error message templates including structural messages). Follow DCC pattern from `dcc/config/schemas/pipeline_message_base.json`. | R51 | ✅ | — |
| T1.32 | Error & Message Manager Modules | Create `eks/engine/core/error_manager.py` (handle_system_error, handle_data_error, fail-fast check, error summary) and `eks/engine/core/message_manager.py` (catalog lookup, template hydration, verbosity control). Create `eks/engine/core/health_scorer.py` (6-dimension scoring: completeness, confidence, structural, source, xref, consistency) and `eks/engine/core/structure_detector.py` (PDF structural element detection). Add `document_elements` table to `registry.py`. Follow DCC pattern from `dcc/workflow/core_engine/errors/error_manager.py`. | R51 | ✅ | — |
| T1.33 | Migrate EKS schemas to config/schemas/ | Move core/asset/ontology config & schema files to `eks/config/schemas/`; update SchemaLoader, ErrorManager, MessageManager, tests, and documentation | R06, R99 | ✅ | 2026-06-22 |
| T1.34 | Reorganize document schema (3-layer) | Create `eks_doc_base_schema.json` (document + element definitions), `eks_doc_setup_schema.json` (table declarations, extraction rules, health scoring schema), `eks_doc_config.json` (ontology triggers, health score tiers, element expectations). Move `document_metadata_def` and `project_metadata_def` from `eks_base_schema.json` to `eks_doc_base_schema.json`. Add `document_element_def` (7 columns) to doc base schema. Update `schema_loader.py` with doc schema loading and validation. Update `eks_base_schema.json` to remove doc defs. Add 6 new tests in `test_phase1.py`. Registry config stays in `eks_config.json` (pipeline-level setting). | R52 | ✅ | 2026-06-22 |
| T1.35.1 | Enhance doc base schema — enums & missing fields | Add `doc_id_format`, `document_type_code` enum (7 codes), `file_type_code` enum (5), `element_type_code` enum (8); add `file_path`, `ingested_at`, `file_type` to `document_metadata_def`; type `document_element_def.element_type` with enum ref | R53 | ✅ | 2026-06-22 |
| T1.35.2 | Enhance doc setup schema — registries | Add `document_type_registry`, `file_type_registry`, `element_type_registry` property declarations; update `element_expectations` key schema to use document type codes; add all three registries to `required` | R53 | ✅ | 2026-06-22 |
| T1.35.3 | Enhance doc config — registry values | Populate `document_type_registry` (7 entries with ontology class + expected file types), `file_type_registry` (5 entries with parser class + MIME), `element_type_registry` (8 entries with description + source + Phase 2/3 use); refactor `element_expectations` keys from A-E → DWG/PI-PID/SPC/RPT/MAN/DS/OM | R53 | ✅ | 2026-06-22 |
| T1.35.4 | Update schema loader — validate new registries | Add `_validate_doc_registries()` for enum value checks, registry completeness, file type parser class references in `load_all()` | R53 | ✅ | 2026-06-22 |
| T1.35.5 | Update tests — new validation tests | Add tests: `test_doc_type_enum`, `test_doc_type_registry`, `test_file_type_registry`, `test_element_type_registry`, `test_element_expectations_keys`, `test_doc_metadata_complete_fields` | R53 | ✅ | 2026-06-22 |
| T1.35.6 | Update appendix B — document registry schema | Add B3.2 Document Type Registry, B3.3 File Type Registry, B3.4 Element Type Registry sections; update B3 schema table with `file_type` column; version bump to v0.9 | R53 | ✅ | 2026-06-22 |
| T1.36 | Auto-DDL from schema | Create `eks/engine/core/schema_to_ddl.py`: read `document_metadata_def` + `project_metadata_def` + `document_element_def` from `eks_doc_base_schema.json` and generate `CREATE TABLE` / `ALTER TABLE` SQL. Refactor `registry.py` to use generated DDL instead of hard-coded DDL. Add `sync_schema()` method. | R54 | ✅ | 2026-06-22 |
| T1.37 | File scanner | Create `eks/engine/core/file_scanner.py`: walk project directory; match files to `file_type_registry[].extension`; validate against `document_type_registry[].expected_file_types`; register placeholder rows in `documents` table with `extract_status = 'pending'`, `file_path`, `file_type`, filename-parsed metadata. | R55 | ✅ | 2026-06-22 |
| T1.38 | Parser router | Create `eks/engine/parsers/parser_router.py`: map `file_type` → `file_type_registry[].parser_class`; instantiate parser; call `parse()`, `extract_metadata()`, `StructureDetector.detect()` in sequence; return structured results. | R56 | ✅ | 2026-06-22 |
| T1.39 | Pipeline orchestrator | Create `eks/engine/core/pipeline_orchestrator.py`: coordinate Phase A (scan → register placeholders), Phase B (route → parse → detect → score → update), Phase C (flag for review). Error handling, logging, batch processing. | R57 | ✅ | 2026-06-22 |
| T1.40 | Manual review workflow | Create review surface: query `documents` where `extract_status != 'success'` or `extraction_confidence < 0.70`. Support metadata correction, element confirmation, score recalculation, document lock. Update `test_phase1.py` with tests. | R58 | ✅ | 2026-06-22 |
| T1.41 | Fix error/message schemas 3-layer pattern | Create `eks_error_setup_schema.json` and `eks_message_setup_schema.json` (allOf + $ref to base). Clean config files (remove $schema/$id/title/description/version). Update `schema_loader.py` with error/message validation methods. Resolve I014. | R51 | ✅ | 2026-06-22 |
| T1.42 | Project code fragment schema | Create `eks_project_code_schema.json` with valid project codes (131101, 131242, 999999). Follow DCC fragment pattern: draft-07, $id URI, allOf/$ref to base, additionalProperties: false. | R06 | ✅ | 2026-06-23 |
| T1.43 | Discipline fragment schema | Create `eks_discipline_schema.json` with 21 valid discipline codes (PI, EL, IN, CI, AR, ME, CL, BQ, QA, VI, M3, DR, DS, SP, RT, CD, CH, PP, IM, SG, NA). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.44 | Department fragment schema | Create `eks_department_schema.json` with 11 valid department codes (PRJ, QAQC, CNT, PRC, PIP, CSA, ELE, ICA, MEC, BIM, NA). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.45 | Facility fragment schema | Create `eks_facility_schema.json` with 12 valid facility prefixes (WSD11, WSW41, WST02, WIL00, WIL11, WIL12, WIL13, WIL22, WIL23, WSB01, WSE00, WST01). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.46 | Update base schema, config, and setup for fragment integration | Add `project_entry_def`, `department_entry_def`, `facility_entry_def` to `eks_base_schema.json`. Replace P123/P456 with real WSD11 codes in `eks_config.json`. Add `$ref` to fragment schemas. Add property declarations for new registries in `eks_setup_schema.json`. Resolve I005. | R06 | ✅ | 2026-06-23 |
| T1.47 | Add fragment schema validation tests | Add 6 new tests: fragment files exist, base definitions exist, fragment required fields, no placeholder data, config has $ref, setup has new properties. Update test_project_scoped_config. 59/59 tests pass. | R06 | ✅ | 2026-06-23 |
| T1.48 | Schema audit — duplicates, inconsistencies, missing validations | (1) Remove duplicate `revision_id` and `discipline_code` from `eks_doc_base_schema.json`; (2) Align parser import paths (`engine.parsers.*` → `eks.engine.parsers.*`); (3) Add dgn/dwg stub parsers to `eks_config.json`; (4) Add `$schema` to `eks_error_config.json` and `eks_message_config.json` (reverted — broke `additionalProperties: false` validation); (5) Log all issues (I022–I028). All 114 tests pass. | R06, R99 | ✅ Complete | 2026-06-23 |
| T1.49 | Cross-cutting workplan remediation | Fix `agent_rule.md` references → `AGENTS.md`; convert Linux absolute paths to relative; update stale statuses (master DRAFT, T1.33, Appendix D); reorder §9/§11 in master; fix Phase 2 date ordering; fill Phase 3 placeholders (sections, tasks T3.1–T3.27); add reranker criteria and eval metrics to Phase 4; choose React for Phase 5 frontend, expand Mermaid diagram, add auth note. | R99 | ✅ Complete | 2026-06-24 |
| T1.50 | Base schema SSOT enforcement | (1) Strip `document_relationship_trigger_map` to shape-only — remove `properties`/`required` with hardcoded enum values (I031); (2) Move `revision_id` from `eks_base_schema.json` to `eks_doc_base_schema.json`, add `revision_validation` 3-layer chain to doc set, remove `revision_pattern` from `project_rules_def` (I032); (3) Update `ConfigRegistry` to resolve `$ref` entries on-the-fly; (4) Update `schema_inheritance_chain.md` v1.6. 114/114 tests pass. | R06, R35 | ✅ Complete | 2026-06-24 |
| T1.51 | Asset Context Fragment — Extensible Location & System Hierarchy + Explicit Relationship Schema | Add `asset_context` fragment to `eks_asset_base_schema.json` with: (1) `project_context` — project_code, phase, client, contractor; (2) `location_hierarchy` — **extensible** nested hierarchy (site→area→unit→building→floor→room) with `additionalProperties: true` for future levels (zone, bay, skid, module) without schema migration; unit is primary anchor. **Location is a context to be linked (LOCATED_IN edges), no specific location keytag generated**; (3) `system_hierarchy` — **extensible** functional decomposition (system_code→subsystem_code) with `additionalProperties: true` for future subsystem levels; discipline + utility_category enums; (4) `asset_relationships` — explicit asset-to-asset links (connects_to, flows_from, flows_to, controlled_by, energized_by, has_actuator, instrumented_by, references_dwg, governed_by_spec, installed_at, set_point_in, redundant_to, spare_for); (5) `document_relationships` — asset↔document links (references_documents, supersedes, produced_by, approved_by, inspected_by); (6) `lifecycle_context` — commissioning_status, operational_status, criticality, safety_class (SIL), redundancy_group, maintenance_strategy, regulatory_tag. Update `eks_asset_setup_schema.json` fragment enum + `fragment_category_registry` (functional). Populate `asset_context` for all 14 AT_ types in `eks_asset_config.json` with column normalization mappings. Version bumps: base→1.3.0, setup→1.3.0, config→1.4.0 per AGENTS.md §13. | R36 | ✅ | 2026-06-25 |
| T1.52 | Implement EKSPipelineContext | Create `eks/engine/core/context.py` with nested dataclasses for centralized state management (paths, data, parameters, state, telemetry, schema_registry) per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.53 | Implement BaseEngine abstract class | Create `eks/engine/core/base.py` with standard execution flow (validate → execute → validate) per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.54 | Implement TelemetryHeartbeat | Create `eks/engine/core/telemetry.py` for document processing checkpoints per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.55 | Implement Multi-Stage Validation | Create `eks/engine/core/validator.py` with setup, schema, data, parser validation stages per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.56 | Implement CLI Entry Points | Create `eks/engine/*/cli.py` for independent engine execution via command line per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.57 | Implement HTTP API Endpoints | Create `eks/ui/backend/engine_endpoints.py` for independent engine execution via HTTP per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.58 | Implement Checkpoint State Serialization | Add checkpoint state serialization/deserialization for resume capability per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.59 | Implement ParserFactory | Create `eks/engine/core/factories.py` with file type routing per Appendix F | R26 | ✅ | 2026-06-30 |
| T1.60 | Implement HealthScorerFactory | Factory with config-driven dimensions per Appendix F | R51 | ✅ | 2026-06-30 |
| T1.61 | Implement StructureDetectorFactory | Factory for structure detector instantiation per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.62 | Update Engines to Use Factories | Refactor existing engines to use factories instead of direct instantiation per Appendix F | R26 | ✅ | 2026-06-30 |
| T1.63 | Enhance PipelineOrchestrator with Checkpoints | Add 5 clear phases (A-E) with telemetry heartbeat integration per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.64 | Implement Phase Rollback Capability | Add checkpoint restoration mechanism for failed phases per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.65 | Implement Project Setup Validator | Create `eks/engine/core/setup_validator.py` with auto-creation of missing folders per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.66 | Create Project Setup Schema | Create `eks/config/schemas/project_setup.json` for setup validation per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.67 | Integrate project_setup into core 3-layer schemas (I046) | Refactor `project_setup.json` content into `eks_base_schema.json` (4 new defs: `required_folder_setup_def`, `required_file_setup_def`, `environment_setup_def`, `validation_options_def`), `eks_setup_schema.json` (new `project_setup` property with `$ref`), and `eks_config.json` (actual values). Delete orphan `project_setup.json`. Refactor `setup_validator.py` to load from `ConfigRegistry` chain instead of hardcoded lists. Resolves I046. | R99 | ✅ | 2026-06-30 |
| T1.68 | Wire ErrorManager/MessageManager into pipeline orchestrator | Call `ErrorManager.handle_system_error()` and `ErrorManager.handle_data_error()` at runtime in `pipeline_orchestrator.py`: emit D4/D5 error codes on phase failures and per-file parse failures; call `MessageManager.format()` for D6 milestone messages at phase start/complete. Resolves AGENTS.md §5.9 violation. | R51 | ✅ Done | T1.70, T1.72 |
| T1.69 | Add run_id correlation ID to EKSLogger and _LogCapture | Add `run_id: Optional[str]` param to `EKSLogger.__init__`; prepend `[run_id]` to all log entries. In `phase1_server.py` `_handle_pipeline_start()`, pass `job_id` as `run_id` to `_LogCapture` and `PipelineOrchestrator` logger so all log entries for a job share a traceable ID (universal §3.12 Structured Logging & Correlation IDs). Persist per-run log to `eks/output/debug_log.json` (T1.76). | R33, R51 | 🟠 High | T1.76 |
| T1.70 | Add data_dir traversal guard to phase1_server.py | In `_handle_files_load()` and `_handle_pipeline_start()`, resolve `data_dir` against `PRJ_DIR` and check `is_relative_to(PRJ_DIR)` — return HTTP 403 if outside project root. Mirrors the guard already present in `_handle_list_dirs()`. | R99 | 🔴 Critical | — |
| T1.71 | Replace raw duckdb.connect in _update_doc_status | Replace `__import__('duckdb').connect(str(self.registry.db_path))` in `pipeline_orchestrator.py` `_update_doc_status()` with a call to a new `registry.update_document_status(doc_id, status, confidence, notes)` method that uses the existing `_with_retry()` wrapper and the registry singleton connection. | R02 | ✅ Done | T1.68 |
| T1.72 | Enforce DiscoveryInput/Output and ParserInput/Output contracts in orchestrator | Wrap `run_phase_a()` to construct `DiscoveryInput` and validate `DiscoveryOutput`; wrap `_process_file()` to construct `ParserInput` and validate `ParserOutput` — enforcing the `BaseEngine.run()` contract defined in `base.py` and `io_contracts.py`. | R57 | 🟠 High | — |
| T1.73 | Persist checkpoint JSON to disk in _run() thread | In `phase1_server.py` `_run()`, after each `_set_phase()` call, invoke `orchestrator.save_checkpoint(phase, checkpoint_path=PRJ_DIR / "eks" / "output" / f"checkpoint_{job_id}.json")` so checkpoint state survives server restarts (universal §3.11 Idempotency & Checkpointing). Resume from last completed phase on re-run. | R57 | 🟡 Medium | — |
| T1.74 | Cross-platform path compatibility | Fix 4 cross-platform gaps: (1) Anchor all bare relative paths in `phase1_server.py` `_run()` and `_handle_files_load()` to `PRJ_DIR` — `SchemaLoader(str(PRJ_DIR / "eks" / "config"))`, `orchestrator.initialize_context(data_dir=PRJ_DIR / data_dir, ...)`, `scanner.scan(PRJ_DIR / data_dir)`; (2) Fix `_handle_config_paths()` to return `as_posix()` strings instead of `str(Path)` which produces backslashes on Windows; (3) Fix `EKSPaths.to_dict()` in `context.py` to use `.as_posix()` for all path fields so checkpoint JSON is OS-portable; (4) Fix `EKSPipelineContext.from_dict()` to reconstruct `Path` objects from posix strings. Resolves I078–I081. | R99 | ✅ Done | T1.69, T1.70 |
| T1.75 | Activate ErrorManager/MessageManager in phase1_server | **Closes silent T1.68 gap**: `phase1_server.py` constructs `PipelineOrchestrator` WITHOUT passing `error_manager`/`message_manager`, so the T1.68 wiring is dead code in production. Construct `ErrorManager(registry.logger)` and `MessageManager(...)` loading `eks_error_config.json`/`eks_message_config.json`, and pass them to `PipelineOrchestrator(...)`. Verify D5/S-PIP error codes and D6 status messages appear in `GET /api/v1/pipeline/logs/{job_id}`. | R51, R99 | 🔴 Critical | T1.68, T1.76 |
| T1.76 | Persist debug/message/status JSON to eks/output | Per AGENTS.md §7/§19, generate machine-parseable run artifacts in `eks/output/`: (1) `debug_log.json` — pass `debug_file=eks/output/debug_log.json` to `EKSLogger("Phase1Server")` and call `save_debug_log()` at end of `_run()`; (2) `pipeline_status_{job_id}.json` — write final `_job_state[job_id]` summary; (3) `pipeline_messages_{job_id}.json` — write MessageManager/ErrorManager catalog output for the run. Mirrors DCC `dcc/output/` artifact convention. | R51, R99 | 🟠 High | T1.69, T1.75 |

---

## 9. Files and Modules to Create/Update

| File/Folder                                         | Action | Purpose                                                    |
| :-------------------------------------------------- | :----- | :--------------------------------------------------------- |
| `eks/eks.yml`                                       | Create | Conda environment file with all EKS dependencies           |
| `eks/engine/__init__.py`                            | Create | Package init with version info                             |
| `eks/engine/core/__init__.py`                       | Create | Core engine package init                                   |
| `eks/engine/core/registry.py`                       | Update | Document registry — implement G1-G3 remediation + Extended Metadata |
| `eks/engine/core/revision.py`                       | Create | Revision management — preserve, filter, chain lookup       |
| `eks/engine/core/config_registry.py"                | Create | SSOT global parameter access via schema config             |
| `eks/engine/parsers/__init__.py`                    | Create | Parser plug-in package init                                |
| `eks/engine/parsers/base_parser.py`                 | Create | Abstract base parser interface                             |
| `eks/engine/parsers/pdf_parser.py`                  | Create | PDF document parser                                        |
| `eks/engine/parsers/docx_parser.py`                 | Create | DOCX document parser                                       |
| `eks/engine/parsers/xlsx_parser.py"                 | Create | XLSX document parser                                       |
| `eks/engine/logging/__init__.py`                    | Create | Logging package init                                       |
| `eks/engine/logging/logger.py`                      | Create | Tiered logger (levels 0–3), debug object, trace table      |
| `eks/config/eks_base_schema.json`                   | Update | Canonical schema — add relationship annotations            |
| `eks/config/eks_asset_config.json`                  | Update | Add `relationship_triggers` and `document_triggers` sections |
| `eks/config/eks_ontology_config.json"               | Update | Add new relationship pairs and classes (Asset & Document)  |
| `eks/engine/core/schema_loader.py`                  | Update | Extended to validate ontology and asset fragments alignment |
| `eks/config/schemas/eks_error_code_base.json`        | Create | Error code base definitions (T1.30) |
| `eks/config/schemas/eks_error_config.json`           | Create | Full error code catalog — 65 codes (T1.30) |
| `eks/config/schemas/eks_message_base.json`           | Create | Pipeline message base definitions (T1.31) |
| `eks/config/schemas/eks_message_config.json`         | Create | Full message catalog — 33 messages (T1.31) |
| `eks/engine/core/error_manager.py`                   | Create | System/data error handling with fail-fast (T1.32) |
| `eks/engine/core/message_manager.py`                 | Create | Message catalog lookup and template hydration (T1.32) |
| `eks/engine/core/health_scorer.py`                   | Create | 6-dimension per-document health scoring (T1.32) |
| `eks/engine/core/structure_detector.py`              | Create | PDF structural element detection (T1.32) |
| `eks/engine/core/registry.py`                        | Update | Add document_elements table CRUD (T1.32) |
| `eks/test/test_t132_modules.py`                      | Create | 47 unit tests for T1.32 modules (T1.32) |
| `eks/config/schemas/eks_doc_base_schema.json`         | Create | Document + element definitions (T1.34) |
| `eks/config/schemas/eks_doc_setup_schema.json`        | Create | Document table declarations, extraction rules, health scoring (T1.34) |
| `eks/config/schemas/eks_doc_config.json`              | Create | Ontology triggers, health score tiers, element expectations (T1.34) |
| `eks/config/schemas/eks_base_schema.json`             | Update | Remove `document_metadata_def`, `project_metadata_def` (T1.34) |
| `eks/engine/core/schema_loader.py`                    | Update | Add doc schema loading and validation (T1.34) |
| `eks/test/test_phase1.py`                             | Update | Add 6 doc schema validation tests (T1.34) |
| `eks/workplan/appendix_b_document_registry.md`        | Update | Reference doc schema files instead of eks_base_schema.json (T1.34) |
| `eks/config/schemas/eks_doc_base_schema.json`         | Update | Add enums, missing fields, typed element_type (T1.35.1) |
| `eks/config/schemas/eks_doc_setup_schema.json`        | Update | Add 3 registry declarations, update expectations key (T1.35.2) |
| `eks/config/schemas/eks_doc_config.json`              | Update | Populate 3 registries, refactor expectations keys (T1.35.3) |
| `eks/engine/core/schema_loader.py`                    | Update | Add `_validate_doc_registries()` (T1.35.4) |
| `eks/test/test_phase1.py`                             | Update | Add 6 new doc schema validation tests (T1.35.5) |
| `eks/workplan/appendix_b_document_registry.md`        | Update | Add B3.2, B3.3, B3.4 sections, update B3 table (T1.35.6) |
| `eks/engine/core/schema_to_ddl.py`                    | Create | Auto-generate SQL DDL from JSON schema definitions (T1.36) |
| `eks/engine/core/file_scanner.py`                     | Create | Walk directory, validate file types, register placeholders (T1.37) |
| `eks/engine/parsers/parser_router.py`                 | Create | Map file_type to parser class, orchestrate parse flow (T1.38) |
| `eks/engine/core/pipeline_orchestrator.py`            | Create | Pre-parse → parse → score → review pipeline coordinator (T1.39) |
| `eks/engine/core/registry.py`                         | Update | Replace hard-coded DDL with SchemaToDDL output; add sync_schema() (T1.36) |
| `eks/test/test_phase1.py`                             | Update | Add pipeline workflow tests (T1.40) |
| `eks/engine/core/error_manager.py`                   | Update | Add error/message validation methods (T1.41) |
| `eks/engine/core/message_manager.py`                 | Update | Add error/message validation methods (T1.41) |
| `eks/config/schemas/eks_error_setup_schema.json`     | Create | Error schema setup layer — allOf + $ref (T1.41) |
| `eks/config/schemas/eks_message_setup_schema.json`   | Create | Message schema setup layer — allOf + $ref (T1.41) |
| `eks/config/schemas/eks_error_config.json`           | Update | Remove $schema/$id/title/description/version (T1.41) |
| `eks/config/schemas/eks_message_config.json`         | Update | Remove $schema/$id/title/description/version (T1.41) |
| `eks/config/schemas/eks_project_code_schema.json`    | Create | Project code fragment schema (T1.42) |
| `eks/config/schemas/eks_discipline_schema.json`      | Create | Discipline fragment schema (T1.43) |
| `eks/config/schemas/eks_department_schema.json`      | Create | Department fragment schema (T1.44) |
| `eks/config/schemas/eks_facility_schema.json`        | Create | Facility fragment schema (T1.45) |
| `eks/config/schemas/eks_base_schema.json`            | Update | Add project_entry_def, department_entry_def, facility_entry_def (T1.46) |
| `eks/config/schemas/eks_config.json`                 | Update | Replace P123/P456 with real codes; add $ref to fragments (T1.46) |
| `eks/config/schemas/eks_setup_schema.json`           | Update | Add project_registry, department_registry, facility_registry (T1.46) |
| `eks/test/test_phase1.py`                             | Update | Add 6 fragment schema tests; update test_project_scoped_config (T1.47) |
| `eks/config/schemas/eks_asset_base_schema.json`      | Update | Add asset_context fragment (T1.51) |
| `eks/config/schemas/eks_asset_setup_schema.json`     | Update | Add asset_context to fragment enum (T1.51) |
| `eks/config/eks_asset_config.json`                   | Update | Populate asset_context for all 14 AT_ types (T1.51) |
| `eks/engine/core/context.py`                         | Create | EKSPipelineContext implementation (T1.52) |
| `eks/engine/core/base.py`                            | Create | BaseEngine abstract class (T1.53) |
| `eks/engine/core/telemetry.py`                       | Create | TelemetryHeartbeat implementation (T1.54) |
| `eks/engine/core/validator.py`                       | Create | Multi-stage validation logic (T1.55) |
| `eks/engine/discovery/cli.py`                        | Create | CLI entry point for discovery engine (T1.56) |
| `eks/engine/parsers/cli.py`                          | Create | CLI entry point for parser engine (T1.56) |
| `eks/engine/health/cli.py`                           | Create | CLI entry point for health scorer (T1.56) |
| `eks/ui/backend/engine_endpoints.py`                | Create | HTTP API endpoints for independent engine execution (T1.57) |
| `eks/engine/core/factories.py`                       | Create | Factory implementations (T1.59, T1.60, T1.61) |
| `eks/engine/core/setup_validator.py`                 | Create | Setup validator (T1.65) |
| `eks/config/schemas/project_setup.json`              | Create | Setup schema (T1.66) |
| `eks/ui/backend/phase1_server.py`                    | Update | Anchor all relative paths to PRJ_DIR; fix `_handle_config_paths()` to return `.as_posix()` strings (T1.74); add `data_dir` traversal guard to `_handle_files_load()` and `_handle_pipeline_start()` (T1.70); pass `job_id` as `run_id` to logger (T1.69); persist checkpoint after each phase (T1.73); construct & pass ErrorManager/MessageManager to PipelineOrchestrator (T1.75); set `debug_file=eks/output/debug_log.json` + call `save_debug_log()`; write `pipeline_status_{job_id}.json` and `pipeline_messages_{job_id}.json` (T1.76) |
| `eks/engine/core/context.py`                         | Update | `EKSPaths.to_dict()` use `.as_posix()`; `from_dict()` reconstruct from posix strings (T1.74) |
| `eks/engine/core/pipeline_orchestrator.py`           | Update | Wire `ErrorManager`/`MessageManager` calls at phase boundaries and per-file failures (T1.68); replace raw `duckdb.connect` in `_update_doc_status()` with `registry.update_document_status()` (T1.71); wrap phase A/B with `DiscoveryInput/Output` and `ParserInput/Output` contracts (T1.72); accept `error_manager`/`message_manager` from server (T1.75) |
| `eks/engine/core/registry.py`                        | Update | Add `update_document_status(doc_id, status, confidence, notes)` method using `_with_retry()` (T1.71) |
| `eks/engine/logging/logger.py`                       | Update | Add `run_id: Optional[str]` param; prepend `[run_id]` to all log entries (T1.69); accept `debug_file` and write `eks/output/debug_log.json` (T1.76) |
| `eks/engine/core/io_contracts.py`                    | Update | Add `ParserInput`/`ParserOutput` dataclasses (mirror `DiscoveryInput/Output`); used by T1.72 contract enforcement |
| `eks/engine/core/error_manager.py`                   | Update | Load catalog from `eks_error_config.json`; callable from `phase1_server.py` with registry logger (T1.75) |
| `eks/engine/core/message_manager.py`                 | Update | Load catalog from `eks_message_config.json`; callable from `phase1_server.py` (T1.75); emit run messages to `eks/output/pipeline_messages_{job_id}.json` (T1.76) |
| `eks/output/debug_log.json`                          | Create | Per-run structured debug log (logs/errors/trace_table) written by `save_debug_log()` (T1.76, AGENTS.md §7/§19) |
| `eks/output/checkpoint_{job_id}.json`                | Create | Per-run checkpoint state for resume (T1.73) |
| `eks/output/pipeline_status_{job_id}.json`           | Create | Per-run final status summary (T1.76) |
| `eks/output/pipeline_messages_{job_id}.json`         | Create | Per-run message/error catalog output (T1.76) |

---

## 10. Risks and Mitigation

| Risk                                         | Likelihood | Impact | Mitigation                                                         |
| :------------------------------------------- | :--------: | :----: | :----------------------------------------------------------------- |
| DB schema changes cascade to downstream code | Medium     | High   | Schema-driven design isolates DB structure from processing logic   |
| PDF/DOCX parsing quality varies by doc type  | High       | Medium | Abstract parser interface allows per-format tuning; log errors     |
| DWG/DGN parsing requires CAD libraries       | High       | Low    | Deferred to Phase 3; stub plug-in interface stubbed in this phase  |
| Schema design diverges from dcc pattern      | Low        | Medium | Explicitly use dcc/config/schemas as template reference            |
| Metadata extraction accuracy is low          | Medium     | Medium | Implement Manual Verification workflow in Phase 5                  |

---

## 11. Potential Future Issues

- CAD format parsing (DWG/DGN) may require specialized third-party libraries or commercial services
- Large document volumes may require async/batch ingestion pipelines
- Document registry may need sharding or partitioning for very large corpora
- Manual verification queue may become a bottleneck if not optimized

---

## 12. Success Criteria

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

## 13. Deliverables

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
- Data challenge analysis: I015–I021 logged to `eks/log/issue_log.md`, §11 added to master workplan
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


---

## 14. Phase 1 Pipeline Architecture (Detailed)

```mermaid
graph TB
    subgraph BOOT["Bootstrap — Schema & Registry Init"]
        direction TB
        CL["1. ConfigRegistry.__new__()<br/><i>eks/engine/core/config_registry.py</i><br/>Purpose: SSOT global config singleton<br/>Input: config_dir path<br/>Output: ConfigRegistry instance<br/>Calls: SchemaLoader(config_dir).load_all()"]
        SL["2. SchemaLoader.load_all()<br/><i>eks/engine/core/schema_loader.py</i><br/>Purpose: Load & validate 23 JSON schema files<br/>Input: eks/config/schemas/*.json (6 schema triples + 4 fragments)<br/>Output: In-memory dicts: core, asset, ontology, doc, error, message<br/>Dep: jsonschema, referencing"]
        DDL["3. SchemaToDDL.generate_documents_ddl()<br/><i>eks/engine/core/schema_to_ddl.py</i><br/>Purpose: Generate CREATE TABLE from doc_base_schema<br/>Input: eks_doc_base_schema.json<br/>Output: SQL DDL string for documents table"]
        DDL2["4. SchemaToDDL.generate_document_elements_ddl()<br/>Purpose: Generate CREATE TABLE for elements<br/>Output: SQL DDL string for document_elements table"]
        IDX["5. SchemaToDDL.generate_indexes()<br/>Purpose: Generate index DDL<br/>Output: SQL index statements"]
        REG["6. DocumentRegistry.__init__()<br/><i>eks/engine/core/registry.py</i><br/>Purpose: Connect DuckDB, init schema<br/>Input: ConfigRegistry, DDL strings<br/>Output: output/eks_registry.db with documents + document_elements tables<br/>Dep: duckdb, SchemaToDDL"]
        SYNC["7. DocumentRegistry.sync_schema()<br/>Purpose: ALTER TABLE ADD COLUMN for schema evolution<br/>Dep: PRAGMA table_info, SchemaToDDL.generate_migration_ddl()"]
        EM["8. ErrorManager & MessageManager init<br/><i>eks/engine/core/error_manager.py</i><br/><i>eks/engine/core/message_manager.py</i><br/>Purpose: Load error/message catalogs<br/>Input: eks_error_config.json, eks_message_config.json<br/>Output: In-memory error/message catalogs"]
        CL --> SL --> DDL --> DDL2 --> IDX --> REG --> SYNC
        SL --> EM
    end

    subgraph PHA["Phase A — File Discovery (PipelineOrchestrator.run_phase_a)"]
        direction TB
        PCTX["9. PipelineOrchestrator.initialize_context()<br/><i>eks/engine/core/pipeline_orchestrator.py</i><br/>Purpose: Set EKSPipelineContext paths<br/>Input: data_dir, schema_dir, output_dir, archive_dir, config_dir, log_dir<br/>Output: ctx: EKSPipelineContext<br/>Dep: EKSPipelineContext, TelemetryHeartbeat<br/><br/>✅ T1.74: Cross-platform path — EKSPaths.to_dict() uses .as_posix()"]
        I72A["🔷 T1.72: Wrap run_phase_a() with DiscoveryInput/Output contracts<br/>Construct DiscoveryInput → validate → pass to phase logic<br/>→ Validate DiscoveryOutput before return"]
        FS["10. FileScanner.scan(root_dir)<br/><i>eks/engine/core/file_scanner.py</i><br/>Purpose: Walk directory, discover recognized files<br/>Input: Filesystem directory tree<br/>Output: List[Dict] {file_path, file_name, file_type, display_name, parser_class}<br/>Dep: os.walk, _build_extension_map(), EKSLogger"]
        FV["11. FileScanner.validate_file_types(discovered)<br/>Purpose: Split by recognized extensions<br/>Input: List[Dict] discovered files<br/>Output: Tuple(valid: List[Dict], unknown: List[Dict])<br/>Dep: document_type_registry from doc_config"]
        FM["12. FileScanner.register_placeholders(valid, registry)<br/>Purpose: Insert placeholder rows in DuckDB<br/>Method: build_placeholder_metadata() per file<br/> → _parse_filename(), _infer_doc_type()<br/> → DocumentRegistry.register_document(metadata)<br/>Output: DuckDB documents rows with extract_status='pending'"]
        PCTX --> I72A --> FS --> FV --> FM
    end

    subgraph PHB["Phase B — Parse → Detect → Score (PipelineOrchestrator.run_phase_b)"]
        direction TB
        FS2["13. FileScanner.scan() + validate_file_types()<br/>Purpose: Discover files again (or use Phase A results)"]
        I72B["🔷 T1.72: Wrap _process_file() with ParserInput/Output contracts<br/>Construct ParserInput → validate → pass to _process_file()<br/>→ Validate ParserOutput before returning"]
        PR["14. PipelineOrchestrator._process_file(file_path, file_type)<br/>Purpose: Process single file end-to-end<br/>Input: file_path, file_type from scanner<br/>Output: Dict {parse_status, elements, score, status, error}"]
        PRR["15. ParserRouter.route(file_path, file_type)<br/><i>eks/engine/parsers/parser_router.py</i><br/>Purpose: Route file to correct parser<br/>Method: get_parser_class() → instantiate_parser()<br/>Dep: ParserFactory, dynamic import"]
        PAR["16. Plug-in Parser<br/>PDFParser | DOCXParser | XLSXParser<br/>DGNParserStub | DWGParserStub<br/><i>eks/engine/parsers/</i><br/>Purpose: Extract content + metadata<br/>Input: File (PDF/DOCX/XLSX/DGN/DWG)<br/>Output: List[Dict] content_blocks + Dict metadata<br/>Dep: pymupdf, python-docx, openpyxl"]
        SD["17. StructureDetector.detect(file_path, pages)<br/><i>eks/engine/core/structure_detector.py</i><br/>Purpose: Detect structural elements<br/>Methods: _detect_cover_page, _detect_revision_table, _detect_sections, _detect_data_tables, _detect_images, _detect_links, _detect_legends<br/>Input: Parsed content blocks grouped as pages<br/>Output: List[Dict] {element_type, element_id, title, content, confidence, source}<br/>Dep: re"]
        HS["18. HealthScorer.score(metadata, structural_elements)<br/><i>eks/engine/core/health_scorer.py</i><br/>Purpose: Compute 6-dimension health score<br/>Methods: _score_completeness (20%), _score_extraction_confidence (20%), _score_structural (20%), _score_source_quality (15%), _score_xref_quality (15%), _score_consistency (10%)<br/>Input: document metadata, structural elements<br/>Output: Dict {overall, completeness, extraction_confidence, structural_completeness, source_quality, xref_quality, consistency, extract_status}"]
        UP["19. PipelineOrchestrator._update_doc_status()<br/>Purpose: Write results to DuckDB<br/>Methods: DocumentRegistry.get_document() → registry.update_document_status()<br/>DocumentRegistry.store_elements(doc_id, elements)<br/>Output: Updated DuckDB documents + document_elements rows<br/><br/>✅ T1.71: Raw duckdb.connect() replaced with registry.update_document_status(doc_id, status, confidence, notes) using _with_retry()"]
        ERR["✅ T1.68: ErrorManager/MessageManager wired into pipeline<br/>→ PipelineOrchestrator.run_phase_a/b/c() call ErrorManager.handle_data_error() on per-file parse failures (emit D5 codes)<br/>→ Call MessageManager.format() for D6 milestone messages at phase start/complete<br/>→ PipelineOrchestrator._process_file() calls ErrorManager.handle_data_error() on parse/detect/score failures<br/>→ PipelineOrchestrator.run_phase_b() calls ErrorManager.handle_system_error() on unrecoverable phase errors (emit D4 codes)"]
        FS2 --> I72B --> PR --> PRR --> PAR --> SD --> HS --> UP
        PAR -.->|"on failure"| ERR
        UP -.->|"on failure"| ERR
    end

    subgraph PHC["Phase C — Manual Review (PipelineOrchestrator.run_phase_c)"]
        direction TB
        LIST["20. DocumentRegistry.list_documents(latest_only=False)<br/>Purpose: Query all documents from DuckDB"]
        FLAG["21. Filter: extract_status ≠ 'success' OR extraction_confidence < 0.70<br/>Purpose: Flag low-confidence/failed docs"]
        MR["22. ManualReviewManager<br/><i>eks/engine/core/review_manager.py</i><br/>Main workflow:<br/>→ get_flagged_documents(confidence_threshold=0.70)<br/>→ correct_metadata(doc_id, updates) — allowed_fields validation<br/>→ confirm_elements(doc_id, element_ids)<br/>→ recalculate_score(doc_id) — calls HealthScorer.score()<br/>→ lock_document(doc_number, verified_by) — sets verified_by, is_locked<br/>Dep: DocumentRegistry, HealthScorer, StructureDetector"]
        DONE["23. Document locked & marked ready<br/>→ is_locked = True<br/>→ ready for Phase 2 chunking"]
        CKPT["🔷 T1.73: Persist checkpoint JSON to disk<br/>→ After each _set_phase() call, invoke orchestrator.save_checkpoint(phase, PRJ_DIR/eks/output/checkpoints/{job_id}.json)<br/>→ Enables resume after server restart"]
        LIST --> FLAG --> MR --> DONE
        DONE --> CKPT
    end

    BOOT --> PHA --> PHB --> PHC

    subgraph LEGEND["Legend"]
        L1["✅ Complete"]:::green
        L2["🔶 Bootstrap closure pending: T1.69 run_id, T1.70 traversal guard, T1.72 I/O contracts, T1.73 checkpoint disk, T1.75 activate Error/MessageManager in server, T1.76 persist debug/message/status JSON to eks/output"]:::amber
    end

    M75["🔶 T1.75: Activate ErrorManager/MessageManager in phase1_server<br/>→ Construct ErrorManager(registry.logger) + MessageManager(...)<br/>→ Pass to PipelineOrchestrator(...) in _run()<br/>→ Closes silent T1.68 gap (managers were never passed → dead code in prod)"]
    M76["🔶 T1.76: Persist debug/message/status JSON to eks/output<br/>→ EKSLogger(debug_file=eks/output/debug_log.json) + save_debug_log() at end of _run()<br/>→ Write pipeline_status_{job_id}.json + pipeline_messages_{job_id}.json<br/>→ Mirrors DCC dcc/output/ artifact convention (AGENTS.md §7/§19)"]

    classDef green fill:#1a3a2a,stroke:#4caf50
    classDef amber fill:#3a3a1a,stroke:#ffc107
    class I72A,I72B,UP,ERR,CKPT,M75,M76 amber
    style BOOT fill:#1a2a4a,stroke:#4a9eff
    style PHA fill:#1a3a2a,stroke:#4caf50
    style PHB fill:#2a1a3a,stroke:#9c27b0
    style PHC fill:#3a1a1a,stroke:#f44336
```

### 14.1 Phase 1 Function Table

Table organized by module, listing all pipeline-critical public functions per AGENTS.md §17.

#### 14.1.1 Pipeline Orchestrator (`eks/engine/core/pipeline_orchestrator.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `PipelineOrchestrator.__init__` | Initialize with config, registry, logger | `config: dict`, `doc_config: dict`, `registry`, `logger: EKSLogger`, `use_telemetry: bool` | `None` | ConfigRegistry, FileScanner, ParserRouter, HealthScorer, StructureDetector, TelemetryHeartbeat | N/A (constructor) | N/A |
| `initialize_context` | Set pipeline paths and context | `data_dir: Path`, `schema_dir: Path`, `output_dir: Path`, `archive_dir: Path`, `config_dir: Path`, `log_dir: Path` | `None` | EKSPipelineContext, EKSPaths | N/A | Sets context attribute |
| `run_phase_a` | Scan directory → register placeholder documents | `root_dir: Path`, `recursive: bool = True` | `dict` with keys: `discovered`, `valid`, `unknown`, `registered` | FileScanner.scan(), validate_file_types(), register_placeholders(), DocumentRegistry | try/except in scanner; caught + logged at orchestrator level | `@log_depth`, telemetry checkpoint per phase |
| `run_phase_b` | Route → parse → detect → score → update for all files | `root_dir: Path`, `recursive: bool = True` | `dict` with keys: `total`, `success`, `partial`, `failed`, `results` | FileScanner, ParserRouter.route(), StructureDetector.detect(), HealthScorer.score(), Registry | `_process_file()` wraps each file in try/except; `failed` status on exception | `@log_depth`, telemetry checkpoint per file + per phase |
| `run_phase_c` | Flag low-confidence / failed documents for review | (none) | `dict` with keys: `flagged`, `documents` | DocumentRegistry.list_documents() | Pass-through from registry | `@log_depth`, telemetry checkpoint |
| `run_full_pipeline` | Execute A → B → C in sequence | `root_dir: Path`, `recursive: bool = True` | `dict` with keys: `phase_a`, `phase_b`, `phase_c` | run_phase_a(), run_phase_b(), run_phase_c(), TelemetryHeartbeat | Individual phase exceptions propagate up | `@log_depth`, telemetry start/stop |
| `_process_file` | Process single file: route → detect → score → update | `file_path: str`, `file_type: str` | `dict` with keys: `file_path`, `file_type`, `parse_status`, `elements`, `score`, `status`, `error` | ParserRouter.route(), StructureDetector.detect(), HealthScorer.score(), _update_doc_status() | try/except — failure sets `status: "failed"` + error message; non-fatal detection failure yields partial result | Error logged via `EKSLogger.error()` |
| `save_checkpoint` | Save pipeline state to file | `phase: str`, `checkpoint_path: Path` | `None` | EKSPipelineContext.save_checkpoint() | IOError caught and logged | Status message on success |
| `rollback_to_checkpoint` | Restore pipeline from saved state | `phase: str`, `checkpoint_path: Path` | `bool` | EKSPipelineContext.load_checkpoint() | Returns `False` on failure; error logged | Status message on success |

#### 14.1.2 File Scanner (`eks/engine/core/file_scanner.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `FileScanner.__init__` | Load file + document type registries | `config: dict`, `doc_config: dict`, `logger: EKSLogger` | `None` | file_type_registry, document_type_registry | N/A | N/A |
| `scan` | Walk directory, discover files with recognized extensions | `root_dir: Path`, `recursive: bool = True` | `List[Dict]` — each with `file_path`, `file_name`, `file_type`, `display_name`, `parser_class` | os.walk, Path.exists(), _build_extension_map() | Handles missing directory gracefully; logs warning | `@log_depth`, status message on start |
| `validate_file_types` | Separate discovered files into valid/unknown by extension | `discovered: List[Dict]` | `Tuple[List[Dict], List[Dict]]` — (valid, unknown) | _ext_map | None; returns empty lists on edge cases | Info logged with counts |
| `build_placeholder_metadata` | Construct placeholder metadata dict from file info + filename parsing | `file_info: Dict` | `Dict[str, Any]` with fields: doc_number, revision, project_title, etc. | _parse_filename(), _infer_doc_type() | Default values for unparseable filenames | None |
| `register_placeholders` | Register placeholder rows in registry for valid files | `valid_files: List[Dict]`, `registry: DocumentRegistry` | `int` — count of successfully registered | build_placeholder_metadata(), DocumentRegistry.register_document() | Skips files that fail registration; logs each error | `@log_depth`, status with count |

#### 14.1.3 Parser Router (`eks/engine/parsers/parser_router.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `ParserRouter.__init__` | Set up parser mapping from file_type_registry | `doc_config: dict`, `logger: EKSLogger`, `use_factory: bool` | `None` | ParserFactory (if use_factory=True), file_type_registry | N/A | N/A |
| `get_parser_class` | Look up parser class path for file type | `file_type: str` | `Optional[str]` — class path or None | _ext_parser_map or ParserFactory | Returns None if not found; caller handles | None |
| `instantiate_parser` | Create parser instance from class path | `parser_class_path: str`, `file_path: str` | `Any` — parser instance | importlib.import_module() | ImportError or AttributeError caught; logged | None |
| `route` | Full parse flow for single file: look up → instantiate → parse → extract metadata | `file_path: str`, `file_type: str` | `Dict` with keys: `status`, `content_blocks`, `metadata`, `parser_class`, `error` | get_parser_class(), instantiate_parser(), parser.parse(), parser.extract_metadata() | try/except around each step; `status: "failed"` + error detail on failure | `@log_depth` |
| `route_batch` | Batch route for multiple files | `files: List[Dict]` | `List[Dict]` — per-file route results | route() per file | Individual file failures isolated | None |

#### 14.1.4 Plug-in Parsers (`eks/engine/parsers/`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `BaseParser.__init__` | Initialize with file path | `file_path: str | Path` | `None` | pathlib | N/A | N/A |
| `BaseParser.parse` (abstract) | Parse file into structured content blocks | (none — uses `self.file_path`) | `List[Dict]` — each with `type`, `content`, `metadata` | Subclass implementation | Subclass must handle file I/O errors | None |
| `BaseParser.extract_metadata` (abstract) | Extract file metadata | (none — uses `self.file_path`) | `Dict[str, Any]` — metadata fields | Subclass implementation | Subclass must handle | None |
| `PDFParser.parse` | Extract text + tables from PDF | (none) | `List[Dict]` — content blocks with page numbers | pymupdf (fitz) | FileNotFoundError, RuntimeError caught; logged | None |
| `DOCXParser.parse` | Extract text + tables from DOCX | (none) | `List[Dict]` — content blocks | python-docx | FileNotFoundError caught; logged | None |
| `XLSXParser.parse` | Extract data from XLSX sheets | (none) | `List[Dict]` — content blocks | openpyxl | FileNotFoundError caught; logged | None |
| `DGNParserStub.parse` | Stub — returns placeholder | (none) | `List[Dict]` — single block with "DGN parsing not implemented" | None | Returns content block with error status | None |
| `DWGParserStub.parse` | Stub — returns placeholder | (none) | `List[Dict]` — single block with "DWG parsing not implemented" | None | Returns content block with error status | None |

#### 14.1.5 Structure Detector (`eks/engine/core/structure_detector.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `StructureDetector.__init__` | Initialize detector | `logger: EKSLogger` | `None` | EKSLogger | N/A | N/A |
| `detect` | Analyze document pages for structural elements | `file_path: str`, `pages: List[Dict]` — each with `text`, `tables`, `images` | `List[Dict]` — elements with `element_type`, `element_id`, `title`, `content`, `confidence`, `source` | Element type heuristics (cover_page, revision_table, section, table, image, link, legend, note) | Logged warning on failure; returns empty list | `@log_depth` |

#### 14.1.6 Health Scorer (`eks/engine/core/health_scorer.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `HealthScorer.__init__` | Initialize with 6-dimension weights | `logger: EKSLogger` | `None` | EKSLogger | N/A | N/A |
| `score` | Compute 6-dimension composite health score | `document: Dict`, `elements: List[Dict]` | `Dict` with keys: `overall` (float 0.0–1.0), `completeness`, `extraction_confidence`, `structural_completeness`, `source_quality`, `xref_quality`, `consistency` | Element type analysis, metadata completeness check | Returns all dimensions as 0.0 on error; logged | `@log_depth` |

#### 14.1.7 Document Registry (`eks/engine/core/registry.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `DocumentRegistry.__init__` | Connect to DuckDB, init schema | `logger: EKSLogger` | `None` | ConfigRegistry, DuckDB, SchemaToDDL, _init_db(), _migrate_schema() | DB connection failure logged | Status message |
| `register_document` | Insert/update document row | `metadata: Dict` — with `document_number`, `revision`, etc. | `str` — doc_id (`{number}-{rev}`) | DuckDB, COLUMN_ALLOWLIST | Duplicate handled via INSERT OR REPLACE | Status message on success |
| `get_document` | Retrieve document by number + optional revision | `doc_number: str`, `revision: str` | `Optional[Dict]` — row as dict, or None | DuckDB | Returns None on not found | Info logged |
| `list_documents` | List with filters, sorting, latest-only | `filters: Dict`, `latest_only: bool`, `order_by: str` | `List[Dict]` — matching rows | DuckDB, COLUMN_ALLOWLIST validation | Untrusted filter/sort columns silently ignored with warning | Warning logged for rejected columns |
| `store_elements` | Insert structural elements | `doc_id: str`, `elements: List[Dict]` | `int` — count inserted | DuckDB | Insert errors logged | Info with count |
| `get_elements` | Retrieve elements for a document | `doc_id: str` | `List[Dict]` | DuckDB | Returns empty list on error | None |
| `sync_schema` | Sync DB columns with JSON schema | (none) | `Dict` with `documents_added`, `document_elements_added`, `indexes_created` | SchemaToDDL, DuckDB, PRAGMA table_info | Logged per column | Status message with total changes |

#### 14.1.8 Review Manager (`eks/engine/core/review_manager.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `ManualReviewManager.__init__` | Initialize with registry + optional config | `registry`, `doc_config: dict`, `logger: EKSLogger` | `None` | DocumentRegistry, HealthScorer, StructureDetector | N/A | N/A |
| `get_flagged_documents` | Query documents needing manual review | `confidence_threshold: float = 0.70` | `List[Dict]` — flagged document metadata | DocumentRegistry.list_documents() | Pass-through from registry | `@log_depth`, info with count |
| `correct_metadata` | Update specific document fields | `doc_id: str`, `updates: Dict` — allowed fields only | `bool` — True on success | DocumentRegistry, allowed_fields validation | Returns False on invalid field; logged | `@log_depth` |
| `lock_document` | Lock document with reviewer attribution | `doc_number: str`, `verified_by: str`, `score_override: float` | `bool` — True on success | HealthScorer.score(), DocumentRegistry | Returns False on document not found; logged | `@log_depth` |

#### 14.1.9 Schema Loader (`eks/engine/core/schema_loader.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `SchemaLoader.__init__` | Initialize with config directory | `config_dir: str | Path` | `None` | pathlib, json | N/A | N/A |
| `load_all` | Load all 23 schema files across 6 schema sets + fragments | (none — uses `self.config_dir`) | `Dict` with: `base_schema`, `setup_schema`, `config`, `doc_base_schema`, `doc_setup_schema`, `doc_config`, `asset_base_schema`, `asset_setup_schema`, `asset_config`, `ontology_base_schema`, `ontology_setup_schema`, `ontology_config`, `error_code_base`, `error_setup_schema`, `error_config`, `message_base`, `message_setup_schema`, `message_config`, and fragment schemas, `project_rules_config` | json.load(), file discovery by pattern, $ref resolution | FileNotFoundError → graceful fallback with warning; validation errors collected without aborting | Status message per file loaded |

#### 14.1.10 Config Registry (`eks/engine/core/config_registry.py`)

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `ConfigRegistry.__init__` | Singleton — load config via SchemaLoader | `config_dir: str | Path` | `ConfigRegistry` instance | SchemaLoader | SchemaLoader errors propagate | N/A |
| `get` | Get config value by dot-separated key path | `key_path: str`, `default: Any` | `Any` — resolved value | SchemaLoader.load_all(), _load_ref() returns None on unresolved `$ref` | Returns default on missing key | None |
| `data_dir` | Shorthand for `get("registry_settings.data_dir")` | (none) | `Path` | get() | Returns fallback path | None |
| `output_dir` | Shorthand for `get("registry_settings.output_dir")` | (none) | `Path` | get() | Returns fallback path | None |

#### 14.1.11 Infrastructure Functions

| Function | Description | Parameters (In) | Return (Out) | Dependencies | Error Handling | Tracing |
| :------- | :---------- | :-------------- | :----------- | :----------- | :------------- | :------ |
| `EKSLogger.__init__` | Create tiered logger | `name: str`, `level: int`, `debug_file: Path` | `None` | psutil (system snapshot) | N/A | N/A |
| `EKSLogger.save_debug_log` | Write debug object to JSON file | (none) | `None` | json.dump | IOError logged | Status message |
| `ErrorManager.handle_system_error` | Look up + log system error | `code: str`, `detail: str` | `Dict` — error info with code, message, severity | error catalog, EKSLogger | Unknown code → fallback to generic error | Logged at error level |
| `ErrorManager.handle_data_error` | Look up + log data error per doc | `code: str`, `doc_id: str`, `detail: str` | `Dict` — error info | error catalog, EKSLogger | Unknown code → fallback | Logged at error level |
| `MessageManager.format` | Format pipeline message with params | `message_id: str`, `**kwargs` | `str` — formatted message | message catalog, string formatting | Unknown ID → returns ID as fallback | None |
| `SchemaToDDL.generate_documents_ddl` | Generate CREATE TABLE for documents | (none) | `str` — SQL DDL | document_metadata_def, project_metadata_def | Missing definition → raises ValueError | None |
| `SchemaToDDL.generate_document_elements_ddl` | Generate CREATE TABLE for elements | (none) | `str` — SQL DDL | document_element_def | Missing definition → raises ValueError | None |
| `SchemaToDDL.generate_migration_ddl` | Generate ALTER TABLE for missing columns | `table_name: str`, `existing_cols: set` | `List[str]` — ALTER TABLE statements | Schema definitions | Empty list if no migration needed | None |
| `TelemetryHeartbeat.add_checkpoint` | Record pipeline progress checkpoint | `phase: str`, `details: Dict`, `document_count: int` | `None` | Checkpoint dataclass | N/A | Verbose output if enabled |
| `EKSPipelineContext.save_checkpoint` | Serialize context to JSON file | `checkpoint_path: Path` | `None` | json.dump, to_json() | IOError caught | Status message |
| `EKSPipelineContext.update_phase` | Track current phase and status | `phase: str`, `status: str` | `None` | TelemetryHeartbeat.add_checkpoint() | N/A | Telemetry checkpoint |

---

## 15. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89)

Phase 1 foundation is extended by two follow-on initiation work batches that close DCC-alignment gaps and universalize project-setup validation. Detailed test evidence lives in the consolidated foundation report (§15/§16) and in `../archive/phase_1_t179_t183_report.md` (RP-EKS-P1-T179-001, archived) for T1.79–T1.83.

### 15.1 Initiation Integrity (T1.77–T1.78)
- **T1.77**: `ProjectSetupValidator.validate_all()` + `get_readiness_status()` wired into `phase1_server._run()` fail-fast gate; `--debug`/`--level` CLI flags with effective-level logic; `data_dir` existence + `recursive` bool validated before concurrency guard. 8 validator unit tests + 3 server integration tests. 202/202 pass.
- **T1.78**: Remediation of DCC gaps — `eks.yml`→`eks/eks.yml` path fix, input-file readability (G2), dependency probe + output-path validation (G3/G4), `--skip-readiness` override (G5), error code constants (G7); fixed pre-existing `_LogCapture.level` bug. 207/207 pass.

### 15.2 Initiation Schema-Driven Hardening (T1.79–T1.83)
| Task | I-Ref | Description | Status |
| :--- | :---- | :---------- | :----: |
| T1.79 | I079 | Wire `P1-SETUP-*` error codes into `validate_all()` results; raise readiness failure via `ErrorManager.handle_system_error("P1-SETUP-READINESS")` | ✅ |
| T1.80 | I080 | Derive output/eks.yml paths from `global_paths` + schema config | ✅ |
| T1.81 | I081 | Remove hardcoded fallback lists duplicating `eks_config.json` (SSOT) | ✅ |
| T1.82 | I082/I083 | Honor `validation_options.auto_create_folders` + schema-driven input defaults | ✅ |
| T1.83 | I084 | Make `eks` package root schema-driven via `global_paths.eks_root` (10× `PRJ_DIR/"eks"` literals replaced) | ✅ |

Full test-case detail (T1.79-a … T1.83-c) is integrated into the foundation report §15.3 and the archived `../archive/phase_1_t179_t183_report.md`.

### 15.3 Initiation Harmonization (T1.84–T1.89) — see §16
Universal `ValidationManager` + EKS `project_setup` reshape to the DCC object model. Full scope, task breakdown, files, and success criteria are consolidated in §16 below (sourced from WP-EKS-P1.3-001).

---

## 16. Phase 1.3 — Initiation Schema & Validation Harmonization (T1.84–T1.89)

**Source workplan (archived)**: [phase_1.3_initiation_harmonization_workplan.md](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
**Status**: ✅ COMPLETE — T1.84–T1.89 all implemented. Universal `ValidationManager` in `common/library/utility/validation/`. EKS `project_setup` schema reshaped to DCC-aligned object model. DCC itself NOT modified (deferred follow-up).

### 16.1 Objective
Achieve **schema-design consistency** and **code-module universality** for project-setup validation, so that EKS and (later) DCC validate project structure through one shared, well-tested module and through schemas that follow the same shape. EKS's AGENTS.md §6-mandated folder names are preserved — only the *schema shape* (not the folder names) aligns with DCC.

### 16.2 Scope Summary
| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| R99 | Foundation & Compliance | Initiation Harmonization | Universal `ValidationManager` + EKS `project_setup` reshape to DCC object model | T1.84–T1.89 | T1.67, T1.77, T1.78, T1.79–T1.83 |
| T1.84 | Foundation | Universal ValidationManager | Create `common/library/utility/validation/manager.py` (path-agnostic) — `validate_folders`, `validate_named_files`, `validate_environment`, `validate_dependencies`, `validate_discovery_rules`, `validate_project_setup` | ✅ DONE | R99 |
| T1.85 | Schema | EKS schema reshape | Replace flat-array defs with DCC-aligned object defs (8 new defs) in `eks_base_schema.json` v1.7.0 + `eks_setup_schema.json` v1.4.0 | ✅ DONE | T1.84, T1.67 |
| T1.86 | Schema | Extract project_setup config | Create `eks_project_setup_config.json` v1.0.0; `eks_config.json` v1.5.0 references it | ✅ DONE | T1.85, T1.67 |
| T1.87 | Code | EKS validator adapter | `setup_validator.py` v0.7 thin adapter delegating to universal module; preserves `P1-SETUP-*` + ErrorManager wiring | ✅ DONE | T1.84, T1.86 |
| T1.88 | Testing | Test migration + coverage | `test_setup_validator.py` (19 tests) migrated; `test_validation_manager.py` (20 tests) created; full suite 235/235 green | ✅ DONE | T1.87 |
| T1.89 | Docs | Workplan/log/knowledge update | Workplan, `knowledge.json` v2.3.0, `update_log` (U130), `issue_log` (I085 resolved), universal architecture doc, foundation report | ✅ DONE | T1.84–T1.88 |

### 16.3 Task Breakdown
- **T1.84** — Create universal `ValidationManager` in `common/library/utility/validation/manager.py` (path-agnostic, takes `base_path`), modeled on DCC's mature `validation_manager.py` + `initiation_engine/validators/items.py`. Methods: `validate_folders` (with `auto_created`), `validate_named_files` (generic for `root_files`/`schema_files`), `validate_environment` (location-aware), `validate_dependencies` (required/optional/engines probe), `validate_discovery_rules`, `validate_project_setup`. Structured result `{readiness, folders, files, environment, dependencies, error_codes[]}`; emits codes via `common/library/core/errors/error_manager.py`. Exported from `__init__.py`.
- **T1.85** — Reshape EKS base/setup schema defs to DCC-aligned object model. In `eks_base_schema.json`, replace flat-array defs (`required_folder_setup_def`, `required_engine_subfolder_setup_def`, `required_file_setup_def`, `environment_setup_def`, `validation_options_def`) with 8 object defs: `folder_entry_def`, `root_file_entry_def`, `schema_file_entry_def`, `discovery_rule_def`, `environment_entry_def`, `dependency_config_def`, `validation_rule_def`, `project_metadata_def`. In `eks_setup_schema.json`, reshape `project_setup` to `folders` / `root_files` / `schema_files` / `discovery_rules` / `environment` / `dependencies` / `validation_rules` / `project_metadata`; keep `additionalProperties: false`. `global_paths_def` untouched.
- **T1.86** — Extract `project_setup` instance data to `eks_project_setup_config.json` v1.0.0 (20 folders, root files, schema files, environment, dependencies, project metadata); remove inline `project_setup` from `eks_config.json` v1.5.0, wire via the `$ref`/`ConfigRegistry` mechanism used by `eks_project_rules_config.json` (T1.67). `global_paths` stays in `eks_config.json`.
- **T1.87** — Refactor `setup_validator.py` v0.7 to a thin adapter delegating to `common.library.validation.ValidationManager`. Preserve public `validate_all()` / `get_missing_items()` signatures, `P1-SETUP-*` error codes (universal generic codes mapped to `P1-SETUP-*`), and `ErrorManager.handle_system_error("P1-SETUP-READINESS")` readiness gate. Add `_convert_flat_to_object()` for backward compat.
- **T1.88** — Migrate `test_setup_validator.py` (19 tests) to object-array config; create `test_validation_manager.py` (20 tests) for the universal module. Full EKS suite 235/235 green.
- **T1.89** — Update workplan, `knowledge.json` v2.3.0, `update_log` (U130), `issue_log` (I085 resolved), `common/universal_pipeline_architecture_design.md`, and the foundation report. Generate `phase_1_t179_t183_report.md` (now archived in `eks/archive/`) and this §16 integration.

### 16.4 Files and Modules (T1.84–T1.89)
| File/Folder | Action | Purpose |
| :---------- | :----- | :------ |
| `common/library/utility/validation/manager.py` | Create | Universal, path-agnostic `ValidationManager` |
| `common/library/utility/validation/__init__.py` | Update | Export `ValidationManager` |
| `eks/config/schemas/eks_project_setup_config.json` | Create | Instance data for `project_setup` (object model) |
| `eks/config/schemas/eks_base_schema.json` | Update | Replace flat-array defs with 8 DCC-aligned object defs (v1.7.0) |
| `eks/config/schemas/eks_setup_schema.json` | Update | Reshape `project_setup` property (v1.4.0) |
| `eks/config/schemas/eks_config.json` | Update | Remove inline `project_setup`; keep `global_paths` + `$ref` (v1.5.0) |
| `eks/engine/core/setup_validator.py` | Update | Thin adapter delegating to universal `ValidationManager` (v0.7) |
| `eks/test/test_setup_validator.py` | Update | Migrate to object-array config; keep `P1-SETUP-*` + SSOT tests |
| `eks/test/test_validation_manager.py` | Create | Unit tests for universal module (20) |

### 16.5 Success Criteria
- [x] EKS `project_setup` schema shape matches DCC's (object arrays with metadata; per-folder `auto_created`).
- [x] Reusable `ValidationManager` exists in `common/library/utility/validation/` and is path-agnostic (usable by EKS and later DCC).
- [x] EKS validation runs through the universal module; `phase1_server.py` readiness gate, `P1-SETUP-*` codes, and `ErrorManager` wiring behaviorally unchanged.
- [x] Full EKS test suite green (235/235); universal module has its own tests (20).
- [x] DCC left untouched (deferred follow-up).
- [x] Workplan, `knowledge.json`, `update_log`, `issue_log`, and universal architecture doc updated.

### 16.6 References
- [Phase 1.3 Initiation Harmonization Workplan (archived)](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
- [Phase 1 T1.79–T1.83 Report (archived)](../archive/phase_1_t179_t183_report.md) — RP-EKS-P1-T179-001
- [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md) — §3.9 Project Setup Validation, §3.9.1 Initiation Integrity Layers
- DCC reference (not modified): `dcc/config/schemas/project_setup_base.json`, `project_setup.json`, `project_config.json`; `dcc/workflow/initiation_engine/core/validator.py`; `dcc/utility_engine/validation/validation_manager.py`
- EKS issue: I085 (schema-design divergence between EKS and DCC `project_setup`)

---

## 17. Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)

**Objective**: Align EKS `eks_config.json` with DCC `project_config.json` — store the actual setup values (`folders` / `root_files` / `schema_files` / `environment` / `dependencies` / `project_metadata` / `discovery_rules`) at the **top level** instead of nested under a `project_setup` wrapper. This makes the universal `ValidationManager` (and a future universal schema loader) work for both projects with **zero per-project branching**, completing the Phase 1.3 universality goal, and removes the orphaned `eks_project_setup_config.json` (T1.86 artifact).

### 17.1 Scope Summary
| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.90 | Schema/Config | Flatten `project_setup` in `eks_config.json` | Move 7 setup keys to top level; remove `project_setup` wrapper; fix title note (drop "T1.86 extracted") | ✅ DONE | T1.67, T1.85, T1.86 |
| T1.91 | Schema | Update `eks_setup_schema.json` | Remove `project_setup` wrapper property; declare the 7 setup keys top-level (reuse `eks_base_schema.json` defs); bump v1.5.0 | ✅ DONE | T1.90 |
| T1.92 | Code | Update `setup_validator.py` adapter | Read setup from top-level config (DCC pattern) with `project_setup` fallback; keep public API, P1-SETUP-* codes, ErrorManager wiring | ✅ DONE | T1.91 |
| T1.93 | Code | Update `phase1_server.py` call site | `_cfg.get("project_setup", _cfg)` — flatten-aware | ✅ DONE | T1.92 |
| T1.94 | Cleanup | Delete orphan `eks_project_setup_config.json` | Archive first per AGENTS.md §5.3 | ✅ DONE | T1.86 |
| T1.95 | Testing | Tests + suite green | Update `test_setup_schema_has_project_setup`; run full EKS suite (236 pass) | ✅ DONE | T1.92–T1.94 |

### 17.2 Success Criteria
- [x] `eks_config.json` has setup values top-level (no `project_setup` wrapper), matching DCC `project_config.json`.
- [x] `eks_setup_schema.json` declares the 7 setup keys top-level (no `project_setup` property); `additionalProperties: false` preserved.
- [x] `setup_validator.py` reads setup from top-level config with backward-compat `project_setup` fallback; public API + P1-SETUP-* codes + ErrorManager wiring unchanged.
- [x] `phase1_server.py` is flatten-aware.
- [x] `eks_project_setup_config.json` removed (archived); no dangling references.
- [x] Full EKS suite green (236/236).

---

## 18. Schema Discovery & Registration — Discovery-Driven Loading (T1.96)

**Objective**: Add discovery-driven schema registration to EKS by (a) extracting the shared `discover_schema_files()` function from DCC `ref_resolver.py:164-230` into the `common/` library, (b) adding `discovery_rules` data to `eks_config.json`, (c) refactoring `schema_loader.py` to use config-driven loading (explicit `schema_files` + `discovery_rules` glob), and (d) wiring `ValidationManager.validate_discovery_rules()` into `setup_validator.py`. Closes I087.

**Rationale**: Currently `schema_loader.py` hardcodes 22 filenames — adding a new schema set requires source code changes. DCC's `_extract_registered_schemas()` implements a reusable pattern: explicit `schema_files` merge with glob-based `discovery_rules`. Extracting this to `common/` makes it available to both projects and future phases.

### 18.1 Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.96a | Common | Extract `discover_schema_files()` to `common/` | Extract the core discovery loop (glob walk + merge with explicit `schema_files`) from DCC `ref_resolver.py` into a standalone function in `common/library/loader/`. Function signature: `discover_schema_files(project_setup: dict, project_root: Path) -> dict`. Also extracted `safe_resolve()` and `find_schema_file()`. | ✅ COMPLETE | DCC `ref_resolver.py:164-230`, I087 |
| T1.96b | Schema/Config | Add `discovery_rules` to `eks_config.json` | Add 5 discovery rules matching existing schema file conventions (`*_base_schema.json`, `*_base.json`, `*_setup_schema.json`, `*_config.json` in `eks/config/schemas/`; `*.json` in `eks/engine/parsers/`). Update `eks_setup_schema.json` if needed. | ✅ COMPLETE | T1.96a, I087 |
| T1.96c | Code | Refactor `schema_loader.py` for config-driven loading | Replace hardcoded 22-filename list: read `schema_files` from config (explicit registration), execute `discovery_rules`, merge results (explicit wins). Keep backward compat. | ✅ COMPLETE | T1.96a, T1.96b, I087 |
| T1.96d | Code | Wire `validate_discovery_rules()` in `setup_validator.py` | Call `ValidationManager.validate_discovery_rules()` when `discovery_rules` present in config — runs as pre-validation gate before schema loading. | ✅ COMPLETE | T1.96b, I087 |
| T1.96e | Docs | Update `common/universal_pipeline_architecture_design.md` | §3.16 Schema Discovery and Registration Pattern already added. Verify alignment with extracted function. | ✅ COMPLETE | T1.96a |
| T1.96f | Testing | Tests + suite green | Fixed `*_base.json` pattern gap (missing `eks_error_code_base.json` and `eks_message_base.json`). Full EKS suite 236/236 green. | ✅ COMPLETE | T1.96a–T1.96e |

### 18.2 DCC Function Reuse Mapping

Each sub-task reuses specific DCC functions (priority: P0 = must extract, P1 = valuable, P2 = nice-to-have):

| Sub-Task | Priority | DCC Function | DCC Location | Lines | Role |
| :------- | :------: | :----------- | :----------- | :---: | :--- |
| T1.96a | **P0** | `RefResolver._extract_registered_schemas()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 164–256 | Extract → `discover_schema_files()`. Core glob-walk, exclude-filter, merge-with-explicit loop. |
| T1.96a | **P0** | `safe_resolve()` | `dcc/workflow/schema_engine/utils/paths.py` | 10–12 | Resolve `project_root / directory_rel` to absolute path. Used at line 221 of `_extract_registered_schemas`. Also present in `dcc/workflow/core_engine/paths/path_core.py:29` and `dcc/workflow/utility_engine/paths/path_resolvers.py:71`. |
| T1.96a | P1 | `SchemaCache` (class) | `dcc/workflow/schema_engine/loader/schema_cache.py` | 41–250 | Multi-level cache (L1 mem, L2 disk, L3 session) with TTL + mtime validation. Load-after-discovery caching pattern. |
| T1.96a | P1 | `SchemaDependencyGraph.build_graph()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 83–102 | Build adjacency list from `$ref` links in registered schemas — load ordering post-discovery. |
| T1.96a | P2 | `SchemaPaths.list_available_schemas()` | `dcc/workflow/core_engine/paths/path_schema.py` | 99–111 | Simple `glob("*.json")` — fallback if full discovery not needed. |
| T1.96c | **P0** | `RefResolver._build_uri_registry()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 258–298 | Scan directories for JSON files, extract `$id`, build URI→Path map. Essential for `$ref` resolution post-discovery. |
| T1.96c | **P0** | `RefResolver._find_schema_file()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 679–705 | Search multiple directories for schema file by name. Replaces EKS `schema_loader.py` two-location hardcoded search. |
| T1.96c | P1 | `SchemaLoader.load_schema()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 309–353 | Load by stem name from registered directories with caching — pattern for consuming discovery output. |
| T1.96c | P1 | `SchemaLoader._resolve_reference_path()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 282–307 | Multi-fallback path resolution (base → main → CWD). |
| T1.96c | P1 | `SchemaLoader.load_json_file()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 276–280 | Generic JSON file loader. |
| T1.96c | P1 | `SchemaLoader.set_main_schema_path()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 124–129 | Anchor base_path to schema's parent directory. |
| T1.96c | P1 | `SchemaDependencyGraph._extract_dependencies()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 140–184 | Recursive JSON walker extracting all `$ref` targets. |
| T1.96c | P1 | `SchemaDependencyGraph.detect_cycles()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 186–226 | DFS cycle detection for dependency graph. |
| T1.96c | P1 | `SchemaDependencyGraph.get_resolution_order()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 228–262 | Topological sort for load ordering. |
| T1.96c | P2 | `SchemaLoader.load_recursive()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 172–228 | Full recursive load with dependency resolution. |
| T1.96d | already in `common/` | `ValidationManager.validate_discovery_rules()` | `common/library/utility/validation/manager.py` | 449–489 | Validates rule payload + directory existence. **Does NOT execute discovery** — validation gate only. |
| T1.96b | config only | `project_config.json` data pattern | `dcc/config/schemas/project_config.json` | 41–46 | 4 discovery rules as live example. Schema def already in `eks_base_schema.json:167`. |

### 18.3 Success Criteria
- [x] `discover_schema_files()` exists in `common/library/loader/schema_discovery.py` and returns unified registry dict.
- [x] `eks_config.json` has `discovery_rules` array with 5 rules matching existing schema conventions (incl. `*_base.json` for outlier files).
- [x] `schema_loader.py` reads `schema_files` + `discovery_rules` from config; 22 hardcoded filenames replaced with config-driven loop.
- [x] Path root inconsistency fixed: discovery rules use `eks/config/schemas/...` paths to match actual file locations.
- [x] `setup_validator.py` calls `validate_discovery_rules()` when rules present.
- [x] Full EKS suite 236/236 green.
- [x] `common/universal_pipeline_architecture_design.md` §3.16 references align with implementation.

---

## 19. System Parameters — SSOT Centralization (T1.97)

**Objective**: Centralize all runtime behavior knobs (`fail_fast`, `log_level`, `debug_mode`, `skip_readiness`, `retry_count`, `retry_delay`, `api_timeout`, `ollama_timeout`, `db_timeout`) into a schema-defined `system_parameters` block in `eks_config.json`. Create a universal `get_system_param()` function in `common/library/config/` that handles both EKS flat-object and DCC array-of-entries shapes. Remove hardcoded equivalents from `phase1_server.py`, `error_manager.py`, `registry.py`, `server.py`. Closes I088.

**Rationale**: Currently these values are scattered across global variables (`phase1_server.py:103-105`), constructor defaults (`error_manager.py:21`), function defaults (`registry.py:326`), and literal constants (`server.py:359,429`). I088 documents this as a SSOT violation versus DCC's `project_config.json → system_parameters` pattern. A universal `get_system_param()` in `common/` makes the fix reusable for DCC and future phases.

### 19.1 Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.97a | Common | Create `common/library/config/__init__.py` | Implement `normalize_system_parameters(config)` (handles flat-object and array-of-entries shapes) and `get_system_param(config, key, default)`. Export from `common/library/config/`. | 🔷 PLANNED | I088 |
| T1.97b | Schema | Add `system_parameters_def` to `eks_base_schema.json` | Flat-object definition with typed properties: `fail_fast` (bool, default true), `log_level` (int, 1), `debug_mode` (bool, false), `skip_readiness` (bool, false), `retry_count` (int, 3), `retry_delay` (number, 0.5), `api_timeout` (int, 120), `ollama_timeout` (int, 30), `db_timeout` (int, 30). | 🔷 PLANNED | T1.97a, I088 |
| T1.97c | Schema | Add `system_parameters` property to `eks_setup_schema.json` | Optional `$ref` to base def, `additionalProperties: false`. | 🔷 PLANNED | T1.97b, I088 |
| T1.97d | Config | Add `system_parameters` block to `eks_config.json` | Instance data matching `system_parameters_def`. Consolidates the standalone `registry.timeout` into the block. | 🔷 PLANNED | T1.97b, T1.97c, I088 |
| T1.97e | Code | Replace hardcoded values in `phase1_server.py` | Replace `_debug_mode`, `_log_level`, `_skip_readiness` globals and `_with_retry` defaults with `get_system_param(config, ...)`. | 🔷 PLANNED | T1.97a, T1.97d, I088 |
| T1.97f | Code | Replace hardcoded values in `error_manager.py` | Accept `fail_fast` from config instead of hardcoded `True`. | 🔷 PLANNED | T1.97a, T1.97d, I088 |
| T1.97g | Code | Replace hardcoded values in `registry.py` | `_with_retry` reads `retry_count` / `retry_delay` from config via `get_system_param()`. | 🔷 PLANNED | T1.97a, T1.97d, I088 |
| T1.97h | Code | Replace hardcoded timeouts in `server.py` | `api_timeout` / `ollama_timeout` from config via `get_system_param()`. | 🔷 PLANNED | T1.97a, T1.97d, I088 |
| T1.97i | Testing | Tests + suite green | Unit test for `normalize_system_parameters()` (flat object, array, empty, malformed). Integration: config validates against updated setup schema. Full EKS suite green. | 🔷 PLANNED | T1.97a–T1.97h |

### 19.2 Success Criteria
- [ ] `common/library/config/__init__.py` exports `get_system_param()` and `normalize_system_parameters()`.
- [ ] `normalize_system_parameters()` handles EKS flat-object, DCC flat-object, and DCC array-of-entries shapes.
- [ ] `eks_base_schema.json` has `system_parameters_def` with all 9 typed properties and defaults.
- [ ] `eks_setup_schema.json` has `system_parameters` property with `additionalProperties: false`.
- [ ] `eks_config.json` has `system_parameters` block; `registry.timeout` consolidated into block.
- [ ] `phase1_server.py`, `error_manager.py`, `registry.py`, `server.py` read from config via `get_system_param()`, no hardcoded defaults remain for these 9 parameters.
- [ ] Full EKS suite green; unit tests for normalize + get cover all 3 source shapes.
- [ ] I088 closed.

---

## 20. References

1. [eks_system_workplan.md](eks_system_workplan.md) — Master workplan
2. [AGENTS.md](../AGENTS.md) — Repository guidelines
3. [eks/readme.md](../readme.md) — EKS project overview
4. [dcc/config/schemas](../../dcc/config/schemas) — Schema pattern reference
5. [appendix_a_asset_schema.md](appendix_a_asset_schema.md) — Universal Plant Item Schema appendix
6. [appendix_c_ontology.md](appendix_c_ontology.md) — Dynamic ISO 15926-Aligned Ontology
7. [appendix_d_pipeline_messages_errors.md](appendix_d_pipeline_messages_errors.md) — Pipeline Messages & Error Codes (v0.3)
8. [appendix_e_schema_design.md](appendix_e_schema_design.md) — EKS Schema Design (v0.1)
