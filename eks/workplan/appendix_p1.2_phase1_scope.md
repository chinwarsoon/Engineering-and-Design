# Appendix P1.2: Phase 1 — Scope Summary, Files & Modules, and Deliverables

**Document ID**: WP-EKS-P1-APX-1.2  
**Version**: 1.0  
**Last Updated**: 2026-07-21  
**Status**: 🔷 IN PROGRESS — Gap analysis review; added metadata block, scope caveat for I227–I233 (7 open pipeline issues), corrected 4 file paths to `eks/config/schemas/`, appended 12 missing deliverables (T1.72–T1.99), added §4 Issue Cross-Reference.  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) (WP-EKS-P1-001, v5.3, IN PROGRESS)

---

## Contents

- [1. Phase 1 Scope Summary](#1-phase-1-scope-summary)
- [2. Scope Summary](#2-scope-summary)
- [3. Files and Modules to Create/Update](#3-files-and-modules-to-createupdate)
- [4. Phase 1 Deliverables (Consolidated from §34 + §37)](#4-phase-1-deliverables-consolidated-from-34--37)
- [5. Issue Cross-Reference](#5-issue-cross-reference)
- [Revision History](#revision-history)

---

## 1. Phase 1 Scope Summary

> **Source:** [§5. Scope Summary](../phase_1_foundation_workplan.md#5-scope-summary)

## 2. Scope Summary

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
| R100 | Bootstrap            | Universal Bootstrap Manager (Option A / L19) | Extract DCC's mature `BootstrapManager` (~1223 lines, 8 phases) into `common/library/bootstrap/` as L19 — phase tracking, pre/post-load traces, `to_pipeline_context()` → `BasePipelineContext` (L06), dual-mode (`bootstrap_all`/`bootstrap_for_ui`), structured `BootstrapError`; wire EKS to delegate (I108–I111) | T1.99.50–T1.99.63 | ✅ COMPLETE |

**Status Legend:** ✅ PASS / COMPLETE | 🔶 PARTIAL | ❌ FAIL | ✅ COMPLETE  (status column uses only these four symbols; severity emojis 🟠/🔴/🟡 are not status values)

> **⚠️ Caveat — 7 Open Pipeline Issues (I227–I233):** The ✅ PASS statuses above reflect scope implementation completion. However, a 2026-07-20 pipeline audit identified 7 unresolved issues affecting runtime correctness, performance, and maintainability:
>
> | Issue | Scope Affected | Summary |
> |:------|:---------------|:--------|
> | **I227** 🔴 | R57 | Phase B re-scans entire directory (2× I/O) |
> | **I228** 🔴 | R36, R39 | Asset schema fragments have zero runtime pipeline code |
> | **I229** 🔴 | R33, R34, R51 | Per-file telemetry overwhelms storage at scale |
> | **I230** 🔴 | R57 | No `validate_phase_transition()` between phases |
> | **I231** 🔴 | R99 | Version diverges across 3 sources (SSOT violation) |
> | **I232** 🔴 | R21, R22 | Legacy `doc_id` fallback conflicts with `RevisionManager` |
> | **I233** 🔴 | R99 | 1500-line monolithic `eks_engine_pipeline.py` |
>
> See [§4 Issue Cross-Reference](#4-issue-cross-reference) for details and resolution tracking.

---


---

## 3. Files and Modules to Create/Update

> **Source:** [§10. Files and Modules to Create/Update](../phase_1_foundation_workplan.md#10-files-and-modules-to-createupdate)


| File/Folder                                         | Action | Purpose                                                    |
| :-------------------------------------------------- | :----- | :--------------------------------------------------------- |
| `eks/eks.yml`                                       | Create | Conda environment file with all EKS dependencies           |
| `eks/engine/__init__.py`                            | Create | Package init with version info                             |
| `eks/engine/core/__init__.py`                       | Create | Core engine package init                                   |
| `eks/engine/core/registry.py`                       | Update | Document registry — implement G1-G3 remediation + Extended Metadata |
| `eks/engine/core/revision.py`                       | Create | Revision management — preserve, filter, chain lookup       |
| `eks/engine/core/config_registry.py`                 | Create | SSOT global parameter access via schema config             |
| `eks/engine/parsers/__init__.py`                    | Create | Parser plug-in package init                                |
| `eks/engine/parsers/base_parser.py`                 | Create | Abstract base parser interface                             |
| `eks/engine/parsers/pdf_parser.py`                  | Create | PDF document parser                                        |
| `eks/engine/parsers/docx_parser.py`                 | Create | DOCX document parser                                       |
| `eks/engine/parsers/xlsx_parser.py`                  | Create | XLSX document parser                                       |
| `eks/engine/logging/__init__.py`                    | Create | Logging package init                                       |
| `eks/engine/logging/logger.py`                      | Create | Tiered logger (levels 0–3), debug object, trace table      |
| `eks/config/schemas/eks_base_schema.json`              | Update | Canonical schema — add relationship annotations            |
| `eks/config/schemas/eks_asset_config.json`             | Update | Add `relationship_triggers` and `document_triggers` sections |
| `eks/config/schemas/eks_ontology_config.json`          | Update | Add new relationship pairs and classes (Asset & Document)  |
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
| `eks/config/schemas/eks_asset_config.json`             | Update | Populate asset_context for all 14 AT_ types (T1.51) |
| `eks/engine/core/context.py`                         | Create | EKSPipelineContext implementation (T1.52) |
| `eks/engine/core/base.py`                            | Create | BaseEngine abstract class (T1.53) |
| `eks/engine/core/telemetry.py`                       | Create | TelemetryHeartbeat implementation (T1.54) |
| `eks/engine/core/validator.py`                       | Create | Multi-stage validation logic (T1.55) |
| `eks/engine/core/discovery_cli.py`                   | Update | CLI entry point for discovery engine (T1.56) — `run()` now calls `PipelineOrchestrator.run_phase_a()` via `bootstrap_pipeline()` (T1.56.1) |
| `eks/engine/eks_engine_pipeline.py`                    | Update | Add `resolve_pipeline_base_path()` with anchor-folder walk (`engine/` anchor); add `__main__` sys.path guard; make `--data-dir` optional with schema-driven default; route all paths through `global_paths` (T1.99.13–15) |
| `eks/engine/core/health_cli.py`                      | Update | CLI entry point for health scorer engine (T1.56) — `run()` now calls `HealthScorer.score()` / `score_batch()` over DuckDB registry (T1.56.2) |
| `eks/ui/backend/phase1_server.py`                   | Create | HTTP API endpoints for independent engine execution (T1.57, §18.13); `engine_endpoints.py` archived in T1.99.4 |
| `eks/engine/core/factories.py`                       | Create | Factory implementations (T1.59, T1.60, T1.61) |
| `eks/engine/core/setup_validator.py`                 | Create | Setup validator (T1.65) |
| `eks/config/schemas/project_setup.json`              | Create → Deleted (T1.67) | Setup schema (T1.66); content integrated into `eks_base/setup/config` 3-layer schemas and the file deleted in T1.67 (I046) |
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


---

## 4. Phase 1 Deliverables (Consolidated from §34 + §37)

> **Sources:** [§34. Deliverables](../phase_1_foundation_workplan.md#34-deliverables) and [§37. Deliverables](../phase_1_foundation_workplan.md#37-deliverables)
>
> Merged and deduplicated. §37 was a later extension of §34 with 3 additional bootstrap-fix deliverables appended.

| ID | Deliverable | Category | Status | Tasks | Issues | Ref |
|:---|:------------|:---------|:------:|:------|:-------|:---:|
| D001 | EKS project folder structure (including `eks/config/schemas/`) | Foundation | ✅ | T1.1 | — | §11 |
| D002 | `eks/eks.yml` Conda environment file | Config | ✅ | T1.2 | — | §5 |
| D003 | Canonical schema files (base/setup/config): `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json` | Schema | ✅ | T1.3–T1.5 | — | §12, §16 |
| D004 | Engine modules: `registry.py`, `revision.py`, `config_registry.py`, `schema_loader.py` | Module | ✅ | T1.7, T1.21 | — | §20 |
| D005 | Parser modules: `base_parser.py`, `pdf_parser.py`, `docx_parser.py`, `xlsx_parser.py` | Module | ✅ | T1.9–T1.12 | — | §21 |
| D006 | Logging module: `logger.py` | Module | ✅ | T1.13 | — | §19 |
| D007 | Test files: `test_phase1.py`, `test_asset_schema.py`, `test_loader_full.py`, `validate_ontology.py` | Test | ✅ | T1.47, T1.35.5 | — | §12, §22 |
| D008 | Log files: `update_log.md`, `issue_log.md` | Doc | ✅ | — | — | — |
| D009 | Package init files: `engine/__init__.py`, `engine/core/__init__.py`, `engine/parsers/__init__.py`, `engine/logging/__init__.py` | Module | ✅ | — | — | — |
| D010 | Asset schema files: `eks_asset_base_schema.json` (13 fragments), `eks_asset_setup_schema.json`, `eks_asset_config.json` | Schema | ✅ | T1.17–T1.20 | I228 | §17 |
| D011 | Ontology files: `eks_ontology_base_schema.json`, `eks_ontology_setup_schema.json`, `eks_ontology_config.json` | Schema | ✅ | T1.23–T1.29 | I007, I008 | §18 |
| D012 | Pipeline message & error schema files: `eks_error_code_base.json`, `eks_error_config.json`, `eks_message_base.json`, `eks_message_config.json` | Schema | ✅ | T1.41 | I014 | §19, §19.3 |
| D013 | Error/message/scoring modules: `error_manager.py`, `message_manager.py`, `health_scorer.py`, `structure_detector.py` | Module | ✅ | T1.30–T1.32, T1.68–T1.71 | I105, I195–I207 | §19 |
| D014 | `test_t132_modules.py` (47 tests, all passing) | Test | ✅ | T1.30–T1.32 | — | §19 |
| D015 | `phase_1_foundation_report.md` (includes T1.30–T1.32 results consolidated) | Doc | ✅ | T1.30–T1.32 | — | — |
| D016 | Document schema files (T1.34): `eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json` | Schema | ✅ | T1.34 | I012 | §22 |
| D017 | Enhanced document schema files (T1.35): v1.1 of all 3 doc schema files (enums, registries, expectations) | Schema | ✅ | T1.35 | I164–I175 | §22 |
| D018 | Updated test file: `test_phase1.py` (+6 tests for enhanced doc schema) | Test | ✅ | T1.35.5 | — | §22 |
| D019 | Updated `appendix_b_document_registry.md` v0.9 (B3.2, B3.3, B3.4 sections) | Doc | ✅ | T1.35.6 | — | §22 |
| D020 | Auto-DDL module (T1.36): `schema_to_ddl.py` | Module | ✅ | T1.36 | — | §23 |
| D021 | File scanner module (T1.37): `file_scanner.py` | Module | ✅ | T1.37 | — | §23 |
| D022 | Parser router module (T1.38): `parser_router.py` | Module | ✅ | T1.38 | — | §23 |
| D023 | Pipeline orchestrator (T1.39): `pipeline_orchestrator.py` (Phase A/B/C coordinator) | Module | ✅ | T1.39 | I013, I215, I225, I229 | §23 |
| D024 | Manual review workflow (T1.40): `review_manager.py` + 4 tests | Module | ✅ | T1.40 | — | §23 |
| D025 | Error/message schema setup layers (T1.41): `eks_error_setup_schema.json`, `eks_message_setup_schema.json` | Schema | ✅ | T1.41 | I014 | §19 |
| D026 | Fragment schemas (T1.42–T1.45): `eks_project_code_schema.json`, `eks_discipline_schema.json`, `eks_department_schema.json`, `eks_facility_schema.json` | Schema | ✅ | T1.42–T1.45 | — | §12, §16 |
| D027 | Base schema definitions (T1.46): `project_entry_def`, `department_entry_def`, `facility_entry_def` | Schema | ✅ | T1.46 | I005 | §12, §16 |
| D028 | Config updates (T1.46): real WSD11 codes (131101, 131242), `$ref` to fragment schemas | Config | ✅ | T1.46 | I005 | §12, §16 |
| D029 | Setup schema updates (T1.46): `project_registry`, `department_registry`, `facility_registry` registries | Schema | ✅ | T1.46 | — | §12, §16 |
| D030 | Fragment schema tests (T1.47): 6 new tests in `test_phase1.py` | Test | ✅ | T1.47 | — | §12, §16 |
| D031 | Data challenge analysis: I015–I021 logged to issue_log, §25 added to master workplan | Doc | ✅ | — | I015–I021 | §25 |
| D032 | Schema audit fixes (T1.48): duplicate defs removed, parser paths aligned, missing parsers added | Fix | ✅ | T1.48 | I022–I028 | §14 |
| D033 | URI alignment (I027): error/message base schema `$id` → filename-based pattern | Fix | ✅ | T1.48 | I027 | §14 |
| D034 | Shared `verbosity_level` definition in `eks_base_schema.json` (SSOT for message + logging) | Schema | ✅ | — | — | §19 |
| D035 | Shared `document_relationship_trigger_map` definition in `eks_base_schema.json` (SSOT for asset + doc) | Schema | ✅ | — | — | §17, §22 |
| D036 | `schema_loader.py` updated: `base_schema` added to all validation registries | Module | ✅ | T1.48 | I022 | §14 |
| D037 | Test files updated: `eks_base_schema.json` included in validation registries | Test | ✅ | T1.48 | — | §14 |
| D038 | T1.50 Base schema SSOT enforcement: trigger_map→shape-only, revision_id→doc schema chain | Fix | ✅ | T1.50 | I031, I032 | §16 |
| D039 | `eks_doc_setup_schema.json` v1.3.0: added `revision_validation` property | Schema | ✅ | T1.50 | — | §22 |
| D040 | `eks_doc_config.json` v1.2.0: revision_validation entries (131101→`^[A-Z0-9]{1,2}$`, 131242→`^[0-9]{3}$`) | Config | ✅ | T1.50 | — | §22 |
| D041 | `eks_project_rules_config.json` v1.1.0: removed `revision_pattern` (SSOT in doc config) | Config | ✅ | T1.50 | — | §16 |
| D042 | `config_registry.py`: `_load_ref()` + `get()` + helpers for on-the-fly `$ref` resolution | Module | ✅ | T1.50 | — | §14 |
| D043 | `schema_inheritance_chain.md` v1.6: report updated with SSOT changes | Doc | ✅ | T1.50 | — | — |
| D044 | Initiation Integrity & Hardening (T1.77–T1.83): `setup_validator.py`, `phase1_server.py`, P1-SETUP-* codes, test files | Module | ✅ | T1.77–T1.83 | I046, I100 | §24 |
| D045 | Phase 1.3 Initiation Harmonization (T1.84–T1.89): universal `ValidationManager`, adapted `setup_validator` | Module | ✅ | T1.84–T1.89 | I046 | §25 |
| D046 | Bootstrap path-rooting fix (I130): `self._path_resolver` guard in `bootstrap.py` | Fix | ✅ | T1.99.101–103 | I130 | §39 |
| D047 | KeyError `revision` fix (I131): 3-level layered fallback in `file_scanner.py` + `registry.py` | Fix | ✅ | T1.99.104–107 | I131 | §40 |
| D048 | `.dwg` file type orphan fix (I132): CAD document type added to doc schema enum + config | Fix | ✅ | T1.99.108 | I132 | §41 |
| D049 | Pipeline IO contracts (T1.72): `io_contracts.py` — phase-boundary dataclasses | Module | ✅ | T1.72 | — | §23 |
| D050 | Per-run artifacts (T1.73, T1.76): checkpoint, status, messages, debug JSON | Module | ✅ | T1.73, T1.76 | I124 | §23, §32 |
| D051 | Filename & property parsers (T1.99.133–167): `filename_parser.py`, `file_property_parser.py` | Module | ✅ | T1.99.133–167 | I133–I162 | §21, §42–§43 |
| D052 | Common library — bootstrap (T1.99.50–63): `BootstrapManager`, phase tracking, dual-mode, `BootstrapError` | Common | ✅ | T1.99.50–63 | I108–I111 | §30 |
| D053 | Common library — paths (T1.98): `global_paths` resolution, anchor-folder-based discovery | Common | ✅ | T1.98.1–8 | I089, I090, I130 | §29 |
| D054 | Common library — CLI (T1.99.27–29): shared CLI entry-point patterns | Common | ✅ | T1.99.27–29 | I099 | §30 |
| D055 | Common library — export (T1.99.147–167): `DataExporter` CSV/XLSX export utilities | Common | ✅ | T1.99.147–167 | I126, I188, I189 | §32 |
| D056 | DGN/DWG stub parsers (T1.35): Placeholder CAD parser stubs; full impl deferred to Phase 3 | Module | 🔷 | T1.35 | I132, I228 | §21 |

---

## 5. Issue Cross-Reference

> 7 open pipeline issues (I227–I233) — see [`p1_issue_log.md`](../log/phase1/p1_issue_log.md) for full details. Resolved issues I130–I226 are documented in [Appendix P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references).

> **Source:** `../log/phase1/p1_issue_log.md` — 2026-07-20 pipeline audit. See [Appendix P1.6](appendix_p1.6_phase1_revision_history.md) for change history.

---

## Revision History

| Version | Date       | Author    | Summary |
| :------ | :--------- | :-------- | :------ |
| 1.0     | 2026-07-21 | CodeBuddy | Initial versioning — added metadata block (Document ID, Version, Status, Parent Workplan), scope caveat for I227–I233 (7 open pipeline issues), corrected 4 file paths from `eks/config/` to `eks/config/schemas/`, fixed 3 trailing-quote typos in §3 file table, appended 12 missing deliverables (T1.72–T1.99) to §4, added §5 Issue Cross-Reference with full I227–I233 root cause / affected scope / status table, added Table of Contents and Revision History. |
| 1.1     | 2026-07-22 | opencode | §4 deliverable list converted to structured table (D001–D056) with columns: Category, Status, Tasks, Issues, Workplan Ref. All 56 entries preserved — includes bootstrap-fix artifacts (D046–D048), pipeline contracts (D049–D051), and common library modules (D052–D055). |



