# EKS Phase 1 — Foundation: Project Structure, Schema & Document Registry — Test Report

**Report ID**: RP-EKS-P1-001  
**Current Version**: 2.12  
**Status**: ✅ COMPLETE — All Phase 1 tasks complete through T1.99.40-44/I106 (Context Threading). 278/278 tests pass. T1.98/I089/I090 (Universal Path Resolution & Schema-Driven Initialization) integrated into §20; T1.99.1–7/I092 convergence integrated into §21. Phases 2–5 of I092/R60 remain 🔷 PLANNED.  
**Last Updated**: 2026-07-16  
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md)  
**Parent Master**: [eks_system_workplan.md](../eks_system_workplan.md)

---

## 1. Title and Description

Test report for EKS Phase 1 foundation components: schema loading, config registry, document registry, revision management, tiered logging, document parsers, asset schema, ontology, error/message taxonomies, health scoring, document schema, enhanced document v2 registries, auto-DDL generation, file scanner, parser router, pipeline orchestration, and manual review workflow. Validates that all Phase 1 deliverables meet success criteria defined in WP-EKS-P1-001.

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :------ | :--- | :----- | :----------------- |
| 2.12 | 2026-07-16 | opencode | **I106 resolved — Context Threading (T1.99.40–44)**: `EKSPipelineContext` now extends `common.library.core.pipeline.BasePipelineContext` (L06) implementing universal contract. `PipelineOrchestrator.initialize_context()` accepts bootstrap data (parameters, config_registry, schema_registry, checkpoint_state). `run_pipeline()` accepts optional `context` parameter; when provided, skips bootstrap and surfaces context in return dict. `main()` builds `EKSPipelineContext` from `EngineInput` + bootstrap, passes to `run_pipeline(context=ctx)`, extracts `EngineOutput` from returned context. DCC-faithful context threading complete. Added `test_run_pipeline_surfaces_context()` test. Updated `eks/knowledge.json`, `update_log.md` (U163), `issue_log.md`, and workplan tasks T1.99.40-44 to COMPLETE. |
| 2.11 | 2026-07-11 | opencode | **I092/R60 — Phase 1 Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (T1.99.1–7) COMPLETE**: New `eks/engine/core/pipeline_runner.py` shared `bootstrap_pipeline()`/`run_pipeline(context)` funnel (ConfigRegistry → SchemaLoader.load_all → DocumentRegistry → ErrorManager/MessageManager → ProjectSetupValidator readiness gate → PipelineOrchestrator.run_full_pipeline → checkpoint + on_phase callback). Rewrote `eks/engine/parsers/cli.py` as real end-to-end CLI + `eks/pyproject.toml` `eks-pipeline` console_scripts. Wired `phase1_server._run` to `run_pipeline()` (409 guard + resolve_paths preserved). Archived orphan `ui/backend/engine_endpoints.py` → `archive/ui/backend/`. Added canonical `eks/serve.py` (§18.12); `server.py` is a thin re-export shim. `bootstrap_pipeline()` uses `ConfigRegistry` singleton SSOT (resets singleton on differing config_dir; soft readiness gate logs + continues despite `fail_fast:true`). New `eks/test/test_pipeline_runner.py`. Fixed `project_root` depth bug (`parent×4`) in cli.py + pipeline_runner.py; fixed `phase1_server._run` cancellation bug (cancelled job status no longer overwritten with `failed`). Full EKS suite 257/257 green (stable across repeated runs). `phase_1_foundation_workplan.md` → v3.51. U139. I092 narrowed to Phases 2–5. |
| 2.7 | 2026-07-09 | opencode | **Phase 1.3 integrated**: Added §16 (Phase 1.3 Initiation Harmonization test results — T1.84–T1.89). Updated scope summary, success criteria, files, recommendations, and references. Test count updated to 235/235. I085 resolved. Phase 1.3 stand-alone workplan retained as archived reference. |
| 2.6 | 2026-07-09 | opencode | **T1.79–T1.83 COMPLETE**: Initiation schema-driven hardening — error codes/ErrorManager wiring, config-driven paths, SSOT fallback removal, validation_options honored, eks_root schema-driven. 7 P1-SETUP-* error codes, 19 validator tests, 36 server tests. 215/215 tests pass. I079–I084 closed. Report created at `phase_1_t179_t183_report.md` (now integrated here). |
| 2.5 | 2026-07-09 | opencode | **T1.77 COMPLETE**: Initiation integrity checks — ProjectSetupValidator readiness gate, debug levels, arg validation. 202/202 tests pass. |
| 2.4 | 2026-07-09 | opencode | Reconciled T1.73 checkpoint files to `checkpoint_{job_id}_{A,B,C}.json`. |
| 2.3 | 2026-07-09 | opencode | Bootstrap closure complete: T1.72 enforced DiscoveryInput/Output and ParserInput/Output contracts. 191/191 tests pass. |
| 2.2 | 2026-07-08 | opencode | Expanded Bootstrap closure plan: added T1.75 (ErrorManager/MessageManager activation in server) and T1.76 (persist JSON outputs). |
| 2.1 | 2026-07-08 | opencode | Bootstrap update: T1.68 (ErrorManager/MessageManager in orchestrator), T1.71 (update_document_status in registry), T1.74 (cross-platform paths). 191/191 pass. |
| 0.1 | 2026-06-15 | System | Initial test report — Phase 1 foundation verified |
| 0.2 | 2026-06-18 | System | Updated for T1.17–T1.20 and R39: added test results for asset schema files (13 fragments), conditional_fragments structure, all 14 AT_ type registrations. 7 new test cases in `test_asset_schema.py` — all pass. I004 resolved; I005 raised for placeholder project data. |
| 0.3 | 2026-06-16 | System | Updated for T1.21: Document Registry remediation (G1-G3). Added 3 test cases for source_type, column allowlist, and SQL sorting. I006 resolved. |
| 0.4 | 2026-06-16 | System | Updated for T1.22: Extended Document Metadata. Added test case for 11 new fields and JSON array storage for asset_tags. |
| 0.5 | 2026-06-22 | opencode | Updated for T1.23–T1.35: ontology (3 schema files + loader), error/message taxonomies (Appendix D), health scoring, structure_detector, document_elements table, consolidated schemas under `eks/config/schemas/`, dedicated doc schema (3 files), enhanced doc schema v2 with 3 registries + 6 new tests. 31/31 tests pass. I010–I012 resolved. |
| 1.0 | 2026-06-22 | opencode | Updated for T1.36–T1.40: Auto-DDL from schema, FileScanner, ParserRouter, PipelineOrchestrator, ManualReviewManager. Fixed DGN/DWG stubs. 22 new tests added (53/53 total). I013 resolved. |
| 1.1 | 2026-06-23 | opencode | Added §10.2: Data Challenges Identified (I015–I021 from twrp sample analysis). Added §11 items 9–10: Lessons Learned (real data complexity, data quality variance). |
| 1.2 | 2026-06-23 | opencode | Added §7.18: Fragment Schema Validation tests (T1.42–T1.47, 6 new tests). Updated §5: test count 53 → 59. I005 resolved. |
| 1.3 | 2026-06-23 | opencode | Three optional fixes complete: (1) I027 URI alignment; (2) `verbosity_level` consolidated; (3) shared `document_relationship_trigger_map`. 114/114 tests pass. |
| 1.4 | 2026-06-24 | opencode | Consolidated T1.30–T1.32 test report into this report. Merged success criteria, files, recommendations, lessons learned. |
| 1.5 | 2026-06-24 | opencode | T1.50: Base schema SSOT enforcement — `document_relationship_trigger_map` stripped, `revision_id` moved, `ConfigRegistry` $ref resolution. 114/114 tests pass. |
| 2.0 | 2026-06-30 | opencode | T1.67: `project_setup.json` integrated into core 3-layer schema; `setup_validator.py` refactored to load from ConfigRegistry. I046 resolved. 120/120 tests pass (2 new). Phase 1 FINAL COMPLETE. |
| 2.1 | 2026-07-08 | opencode | Bootstrap update: T1.68 (ErrorManager/MessageManager in orchestrator), T1.71 (update_document_status in registry), T1.74 (cross-platform paths). Fixed get_document bug. 7 new tests, 191/191 pass. |
| 2.2 | 2026-07-08 | opencode | Expanded Bootstrap closure plan: added T1.75 (activate ErrorManager/MessageManager in server — closes silent T1.68 gap) and T1.76 (persist debug/message/status JSON to eks/output per AGENTS.md §7/§19). Updated T1.69 (run_id) and T1.73 (checkpoint path). Aligned with workplan v3.29. |
| 2.8 | 2026-07-09 | opencode | **T1.79–T1.83 detailed test cases integrated**: Added §15.3 with full test-case tables (T1.79-a…T1.83-c, REG-1) folded from `phase_1_t179_t183_report.md`. Stand-alone T1.79–T1.83 report now fully integrated. Report status notes Phase 1.3 + T1.79–T1.83 fully merged. |
| 2.9 | 2026-07-09 | opencode | **T1.90–T1.95 Initiation Config Flattening**: Flattened `project_setup` from `eks_config.json` to top-level (DCC `project_config` pattern); `eks_setup_schema.json` v1.5.0 drops the wrapper; `setup_validator.py` + `phase1_server.py` flatten-aware with `project_setup` backward-compat; orphan `eks_project_setup_config.json` deleted (archived). Full suite 236/236 pass. Resolves I086. |

---

## 3. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Index of Content](#3-index-of-content)
- [4. Test Objective](#4-test-objective)
- [5. Scope and Execution Summary](#5-scope-and-execution-summary)
- [6. Test Methodology, Environment, and Tools](#6-test-methodology-environment-and-tools)
- [7. Test Phases, Steps, Cases, and Results](#7-test-phases-steps-cases-and-results)
- [8. Test Success Criteria and Checklist](#8-test-success-criteria-and-checklist)
- [9. Files Archived, Modified, and Version Controlled](#9-files-archived-modified-and-version-controlled)
- [10. Recommendations for Future Actions](#10-recommendations-for-future-actions)
- [11. Lessons Learned](#11-lessons-learned)
- [13. Phase 1 Final Closure (T1.67)](#13-phase-1-final-closure-t167)
- [15. Bootstrap Updates & Initiation Hardening (T1.68–T1.83)](#15-bootstrap-updates--initiation-hardening-t168t183)
- [15.3 T1.79–T1.83 Detailed Test Cases](#153-t179t183-detailed-test-cases)
- [15.4 Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)](#154-initiation-config-flattening--dcc-project_config-pattern-t190t195)
- [16. Phase 1.3 Initiation Harmonization (T1.84–T1.89)](#16-phase-13-initiation-harmonization-t184t189)
- [17. Schema Discovery & Registration — Discovery-Driven Loading (T1.96)](#17-schema-discovery--registration--discovery-driven-loading-t196)
- [18. System Parameters — SSOT Centralization (T1.97/I088)](#18-system-parameters--ssot-centralization-t197i088)
- [19. Universal Architecture Elevation (T1.97.10–14 / I091)](#19-universal-architecture-elevation-t197j-n--i091)
- [20. Universal Path Resolution & Schema-Driven Initialization (T1.98 / I089 / I090)](#20-universal-path-resolution--schema-driven-initialization-t198--i089--i090)
- [21. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (T1.99.1–7 / I092 / R60)](#21-pipeline-entry-point--per-phase-sub-pipeline-convergence-t199ag--i092--r60)
- [22. References](#22-references)

---

## 4. Test Objective

Verify that all Phase 1 foundation components are implemented correctly and meet the success criteria defined in WP-EKS-P1-001 Section 12.

**Key areas:**
- Schema loading and validation (base/setup/config pattern with \$ref resolution)
- SSOT ConfigRegistry singleton pattern
- DocumentRegistry CRUD operations with DuckDB
- RevisionManager revision history and latest-revision filtering
- EKSLogger tiered logging (levels 0-3), debug object, trace table
- Parser base interface and concrete implementations (PDF, DOCX, XLSX)
- Document Registry G1-G3 remediation (T1.21)
- Extended Document Metadata support (T1.22)
- Asset schema (13 fragments, 14 AT_ types, conditional_fragments R39)
- ISO 15926-aligned dynamic ontology (3 schema files, alias resolution, class mapping)
- Error code taxonomy and pipeline message catalog (T1.30)
- Error/message manager, health scorer, structure detector modules (T1.32)
- Document schema extraction into dedicated 3-layer pattern (T1.34)
- Enhanced document schema v2 with enums and 3 registries (T1.35)
- Parser stubs for DGN and DWG formats
- Cross-registry validation at load time
- Auto-DDL generation from JSON schema (T1.36)
- File scanner with type validation and placeholder registration (T1.37)
- Parser router mapping file_type to parser class (T1.38)
- Pipeline orchestrator coordinating 3-phase workflow (T1.39)
- Manual review manager with metadata correction and document locking (T1.40)

---

## 5. Scope and Execution Summary

| Category | Count |
| :------- | :---- |
| Test cases planned | 236 |
| Test cases executed | 236 |
| Test cases passed | 236 |
| Test cases failed | 0 |
| Issues found | 57 (I001–I090 tracked; I001–I046, I079–I085, I087–I090 resolved; I015–I021 open for Phases 2/3; I064/I065/I067–I071 open for Phase 1.2.8–1.2.9; I086 open) |
| Blockers | 0 |

**Execution Date**: 2026-07-10 (T1.96 final validation)  
**Execution Duration**: ~16.8 seconds  
**Executor**: opencode (automated test suite)

### Test Distribution (T1.30–T1.32)

| Module | Test Cases | Status |
| :----- | :--------- | :----- |
| `error_manager.py` | 11 | ✅ All pass |
| `message_manager.py` | 9 | ✅ All pass |
| `health_scorer.py` | 9 | ✅ All pass |
| `structure_detector.py` | 8 | ✅ All pass |
| `registry.py` (`document_elements`) | 10 | ✅ All pass |
| **T1.32 subtotal** | **47** | ✅ **All pass** |

---

## 6. Test Methodology, Environment, and Tools

- **Methodology**: Unit testing with Python `unittest` framework via `pytest`
- **Environment**: Python 3.11.15, conda `eks` environment, Windows
- **Libraries tested**:
  - `jsonschema` 4.26.0 (via `referencing` library)
  - `duckdb` 1.5.3
  - `psutil` 7.2.2
  - `PyMuPDF` 1.27.2.3
  - `python-docx` 1.2.0
  - `openpyxl` 3.1.5
- **Test file**: `eks/test/test_phase1.py`
- **Command**: `python -m pytest eks/test/test_phase1.py -v`

---

## 7. Test Phases, Steps, Cases, and Results

### 7.1 Schema Loader

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 1 | `test_schema_loader` | Config loaded with `project_rules_registry`, `discipline_registry`, `registry.type == "duckdb"` | ✅ PASS | \$ref resolution works correctly via `referencing` |

### 7.2 Config Registry

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 2 | `test_project_scoped_config` | P123 has 3 disciplines; P456 has CI/AR rules | ✅ PASS | Dot-notation access works |
| 3 | `test_config_registry` | Multiple instances return same singleton | ✅ PASS | Singleton pattern confirmed |

### 7.3 Document Registry

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 4 | `test_document_registry` | DOC-001-A registered; revision B updates `is_latest`; doc_a `is_latest=False` | ✅ PASS | DuckDB CRUD and revision tracking verified |

### 7.4 Revision Manager

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 5 | `test_revision_manager` | 2 revisions found; B listed first (latest) | ✅ PASS | History sorted by `ingested_at` descending |

### 7.5 Logger

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 6 | `test_logger` | Debug log JSON created with `project`, `logs` (>=3), `trace_table` (>=1) | ✅ PASS | All levels, trace steps, and save_debug_log verified |

### 7.6 Parser Errors

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 7 | `test_parser_errors` | FileNotFoundError raised for non-existent file | ✅ PASS | Abstract base class validation works |

### 7.7 Ontology (T1.23–T1.27)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 8 | `test_ontology_loader_and_alias_resolution` | Canonical + alias tag types resolve to class; unknown returns None | ✅ PASS | AT_EQPMP→PumpTag, AT_PMP→PumpTag, AT_UNKNOWN→None |
| 9 | `test_ontology_class_map_validation` | ontology_class_map values reference ontology classes | ✅ PASS | AT_EQPMP→PumpTag, AT_MOTOR→MotorTag |
| 10 | `test_ontology_files_exist` | All 3 ontology files present | ✅ PASS | `eks_ontology_base_schema.json`, `eks_ontology_setup_schema.json`, `eks_ontology_config.json` |
| 11 | `test_ontology_validation` | Ontology config validates against setup schema | ✅ PASS | Loader has ontology attr with classes/relationships |
| 12 | `test_ontology_class_map_references_defined_class` | Every class_map value exists in ontology | ✅ PASS | Cross-validated via JSON load |

### 7.8 Asset Schema & R39 (T1.17–T1.20, R39)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 13 | `test_asset_schema_files_exist` | All 3 asset schema files present | ✅ PASS | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` |
| 14 | `test_asset_base_schema_fragments` | Exactly 13 fragment `definitions` present | ✅ PASS | All 13 fragments confirmed |
| 15 | `test_asset_schema_validation` | `eks_asset_config.json` validates against setup schema | ✅ PASS | `referencing` registry used for `$ref` resolution |
| 16 | `test_r39_conditional_fragments` | AT_EQUIP has conditional_fragments; AT_MOTOR has motor_control; all fragments in base | ✅ PASS | Zero-code extensibility verified |

### 7.9 Document Registry Remediation (T1.21)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 17 | `test_remediation_t121_source_type` | `source_type` stored as 'referenced'; defaults to 'ingested' | ✅ PASS | Verified in DuckDB metadata table |
| 18 | `test_remediation_t121_sql_injection_protection` | Untrusted filter columns are ignored | ✅ PASS | COLUMN_ALLOWLIST protects `list_documents` |
| 19 | `test_remediation_t121_sql_sorting` | Revision history sorted by `ingested_at DESC` at SQL level | ✅ PASS | Python-side sorting removed |

### 7.10 Extended Metadata (T1.22)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 20 | `test_extended_metadata_t122` | 11 new fields stored correctly; `asset_tags` as JSON array | ✅ PASS | JSON serialization/deserialization verified |

### 7.11 Document Schema (T1.34)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 21 | `test_doc_schema_files_exist` | All 3 doc schema files present | ✅ PASS | `eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json` |
| 22 | `test_doc_schema_base_definitions` | Base schema has document_metadata_def, project_metadata_def, document_element_def | ✅ PASS | 3 expected definitions confirmed |
| 23 | `test_doc_schema_validation` | Doc config validates against doc setup schema | ✅ PASS | ontology_triggers, health_scoring, element_expectations present |
| 24 | `test_doc_schema_no_doc_defs_in_pipeline_base` | Pipeline base schema no longer contains doc defs | ✅ PASS | `eks_base_schema.json` clean of doc definitions |
| 25 | `test_doc_element_def_has_required_fields` | document_element_def has all 7 fields | ✅ PASS | doc_id, element_type, element_id, title, content, confidence, source |

### 7.12 Enhanced Document Schema v2 (T1.35)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 26 | `test_doc_type_enum_matches_ontology` | Enum values (7) match ontology document_type_mapping | ✅ PASS | DWG/PI-PID/SPC/DS/MAN/OM/RPT all aligned |
| 27 | `test_file_type_registry_completeness` | 5 entries with parser_class and display_name | ✅ PASS | pdf/dgn/docx/xlsx/dwg all present |
| 28 | `test_element_type_registry_completeness` | 8 entries matching D7.10 | ✅ PASS | cover_page/revision_table/section/table/image/link/legend/note |
| 29 | `test_element_expectations_keys_match_doc_type_registry` | 7 expectation keys match 7 doc type codes | ✅ PASS | DWG/PI-PID/SPC/DS/MAN/OM/RPT → 7 entries |
| 30 | `test_doc_metadata_has_new_fields` | file_path, ingested_at, file_type present | ✅ PASS | All 3 new metadata fields confirmed |
| 31 | `test_doc_element_def_has_element_type_enum` | element_type uses $ref to element_type_code enum | ✅ PASS | Enum-based validation active |

### 7.13 Auto-DDL from Schema (T1.36)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 32 | `test_schema_to_ddl_documents_creates_table` | DDL contains CREATE TABLE, id PRIMARY KEY, file_type, TIMESTAMP | ✅ PASS | All expected columns and types confirmed |
| 33 | `test_schema_to_ddl_document_elements` | DDL contains CREATE TABLE with doc_id, element_type, source | ✅ PASS | 3 required columns present |
| 34 | `test_schema_to_ddl_indexes` | 2 indexes generated for document_elements | ✅ PASS | idx_elements_doc_id, idx_elements_type |
| 35 | `test_schema_to_ddl_migration_detects_missing_columns` | ALTER TABLE statements generated for missing columns | ✅ PASS | 20+ missing columns detected |
| 36 | `test_schema_to_ddl_no_migration_for_complete_schema` | No migration when all columns exist | ✅ PASS | Empty list returned |
| 37 | `test_registry_sync_schema` | sync_schema returns correct summary structure | ✅ PASS | documents_added, document_elements_added, indexes_created |
| 38 | `test_registry_column_allowlist_from_schema` | COLUMN_ALLOWLIST derived from JSON schema | ✅ PASS | id, file_type, extract_status all present |
| 39 | `test_schema_to_ddl_timestamp_format` | ingested_at is TIMESTAMP DEFAULT CURRENT_TIMESTAMP | ✅ PASS | Not VARCHAR |

### 7.14 File Scanner (T1.37)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 40 | `test_file_scanner_discovers_files` | Discovers pdf/dgn files, ignores .txt, recursive | ✅ PASS | 3 files found, subdir included |
| 41 | `test_file_scanner_validate_types` | Valid/unknown split based on document_type_registry | ✅ PASS | 2 valid, 0 unknown |
| 42 | `test_file_scanner_build_placeholder` | Filename parsed to doc_number + revision | ✅ PASS | DWG-001-A.pdf → DWG-001, A |
| 43 | `test_file_scanner_register_placeholders` | Document registered with extract_status='pending', file_type | ✅ PASS | FS-TEST-01-A registered |

### 7.15 Parser Router (T1.38)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 44 | `test_parser_router_lookup` | pdf/dgn/docx/xlsx return parser class; xyz returns None | ✅ PASS | All 4 known types found |
| 45 | `test_parser_router_instantiate` | Parser instance created from class path string | ✅ PASS | DGNParserStub instantiated |
| 46 | `test_parser_router_route_no_parser` | Unknown type returns status='failed' with error | ✅ PASS | "No parser for file type" error |
| 47 | `test_parser_router_route_batch` | Multiple files processed, all return results | ✅ PASS | 2 files, both failed (expected) |

### 7.16 Pipeline Orchestrator (T1.39)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 48 | `test_pipeline_orchestrator_phase_a` | Phase A discovers, validates, registers | ✅ PASS | 2 discovered, 2 valid, >=1 registered |
| 49 | `test_pipeline_orchestrator_phase_c` | Phase C returns flagged docs list | ✅ PASS | flagged + documents keys present |

### 7.17 Manual Review Manager (T1.40)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 50 | `test_review_manager_get_flagged` | Returns list of docs with status != 'success' | ✅ PASS | All flagged docs have pending status |
| 51 | `test_review_manager_correct_metadata` | Updates status + checked_by; persists in DB | ✅ PASS | REV-001-A updated to APPROVED |
| 52 | `test_review_manager_lock_document` | Sets verified_by + extract_status='success' | ✅ PASS | LOCK-001-A locked by admin |
| 53 | `test_review_manager_get_summary` | Returns total, status_counts, flagged, reviewed | ✅ PASS | All summary fields present |

### 7.18 Fragment Schema Validation (T1.42–T1.47)

| # | Test Case | Expected | Result | Notes |
| :- | :-------- | :------- | :----: | :---- |
| 54 | `test_fragment_schema_files_exist` | All 4 fragment schema files exist | ✅ PASS | project, discipline, department, facility |
| 55 | `test_base_schema_has_new_definitions` | project_entry_def, department_entry_def, facility_entry_def present | ✅ PASS | Plus existing discipline_entry_def |
| 60 | `test_base_schema_has_project_setup_defs` | required_folder_setup_def, required_file_setup_def, environment_setup_def, validation_options_def | ✅ PASS | 5 project_setup defs in base v1.6.0 |
| 61 | `test_setup_schema_has_project_setup` | project_setup property in setup schema properties and required | ✅ PASS | Core setup v1.3.0 |
| 56 | `test_fragment_schemas_have_required_fields` | Each fragment has $schema, $id, title, version, allOf | ✅ PASS | All 4 files validated |
| 57 | `test_config_no_placeholder_data` | P123/P456 removed; 131101/131242 present | ✅ PASS | Real WSD11 project codes |
| 58 | `test_config_has_fragment_references` | project_registry, department_registry, facility_registry have $ref | ✅ PASS | All 3 registries reference fragment schemas |
| 59 | `test_setup_schema_has_new_properties` | project_registry, department_registry, facility_registry in properties and required | ✅ PASS | Setup schema declarations validated |

---

### 7.19 Error Code Taxonomy & Pipeline Messages (T1.30–T1.32)

#### Schema Validation

| Step | Action | Expected Result | Actual Result | Status |
| :--- | :----- | :-------------- | :------------ | :----- |
| 1.1 | Validate `eks_error_code_base.json` is valid JSON and contains required definitions | Valid JSON with `definitions` for code format, severity, phase, module, function | Valid | ✅ |
| 1.2 | Validate `eks_error_config.json` references base definitions correctly | Config loads without `$ref` resolution errors | Valid | ✅ |
| 1.3 | Validate `eks_message_base.json` has message ID format, verbosity levels, categories | Valid JSON with `verbosity` enum and `message_category` enum | Valid | ✅ |
| 1.4 | Validate `eks_message_config.json` has 33 message entries across 5 categories | 33 entries present | 33 entries | ✅ |

#### error_manager.py (11 tests)

| # | Test Case | Expected | Actual | Status |
| :- | :-------- | :------- | :----- | :----- |
| 2.1 | `handle_system_error` returns formatted error with correct severity | Dict with `code`, `severity`, `message`, `context`, `timestamp` | Correct | ✅ |
| 2.2 | `handle_system_error` includes phase/module in `context` | `context` contains `phase`, `module` keys | Correct | ✅ |
| 2.3 | `handle_system_error` S-E-01xx (system-level) works | Returns proper error dict | Correct | ✅ |
| 2.4 | `handle_system_error` S-B-06xx (business-level) works | Returns proper error dict | Correct | ✅ |
| 2.5 | `handle_data_error` returns formatted data error with function context | Dict with phase, module, function info | Correct | ✅ |
| 2.6 | `fail_fast` raises `SystemExit` on critical errors | `SystemExit` raised | Raised | ✅ |
| 2.7 | `fail_fast` returns False on non-critical errors | Returns `False` | `False` | ✅ |
| 2.8 | `fail_fast` with unknown severity returns False | Returns `False` | `False` | ✅ |
| 2.9 | `get_error_summary` aggregates all recorded errors | List of error dicts | Correct | ✅ |
| 2.10 | `get_error_summary` returns empty list with no errors | Empty list `[]` | Correct | ✅ |
| 2.11 | `get_health_impact` calculates impact based on severity | Impact value | Correct | ✅ |

#### message_manager.py (9 tests)

| # | Test Case | Expected | Actual | Status |
| :- | :-------- | :------- | :----- | :----- |
| 3.1 | `show` returns rendered message from known ID | Formatted string | Correct | ✅ |
| 3.2 | `show` supports template hydration with `{placeholders}` | Replaced values | Correct | ✅ |
| 3.3 | `show` returns None for unknown message ID | `None` | `None` | ✅ |
| 3.4 | `show` respects verbosity level filtering | Verbose messages filtered | Correct | ✅ |
| 3.5 | `show` returns all messages at verbosity ≥ 0 | All messages | Correct | ✅ |
| 3.6 | `show` returns milestone messages correctly | Milestone category | Correct | ✅ |
| 3.7 | `show` returns warning messages correctly | Warning category | Correct | ✅ |
| 3.8 | `show` returns error messages correctly | Error category | Correct | ✅ |
| 3.9 | `list_messages` with category filter returns only matching | Filtered list | Correct | ✅ |

#### health_scorer.py (9 tests)

| # | Test Case | Expected | Actual | Status |
| :- | :-------- | :------- | :----- | :----- |
| 4.1 | `score_document` returns dict with all 6 dimensions + composite | 7 keys | Correct | ✅ |
| 4.2 | `score_document` completeness weight = 0.20 | 20% contribution | Correct | ✅ |
| 4.3 | `score_document` confidence weight = 0.20 | 20% contribution | Correct | ✅ |
| 4.4 | `score_document` structural completeness weight = 0.20 | 20% contribution | Correct | ✅ |
| 4.5 | `score_document` source quality weight = 0.15 | 15% contribution | Correct | ✅ |
| 4.6 | `score_document` xref weight = 0.15 | 15% contribution | Correct | ✅ |
| 4.7 | `score_document` consistency weight = 0.10 | 10% contribution | Correct | ✅ |
| 4.8 | `batch_score_documents` returns list with same length as input | Correct length | Correct | ✅ |
| 4.9 | `format_notes` returns non-empty string with dimension breakdown | Formatted notes | Correct | ✅ |

#### structure_detector.py (8 tests)

| # | Test Case | Expected | Actual | Status |
| :- | :-------- | :------- | :----- | :----- |
| 5.1 | `detect_cover_page` covers Type A (cover page with title, project, doc ID) | Type A + cover_text | Type A | ✅ |
| 5.2 | `detect_cover_page` covers Type B (cover page with title, project, doc ID, rev table) | Type B | Type B | ✅ |
| 5.3 | `detect_cover_page` covers Type C (scanned — very little text) | Type C (scanned) + `is_scanned=True` | Type C | ✅ |
| 5.4 | `detect_cover_page` covers Type D (volume cover) | Type D | Type D | ✅ |
| 5.5 | `detect_cover_page` covers Type E (specification cover) | Type E | Type E | ✅ |
| 5.6 | `detect_sections` returns list of section dicts with `title`, `level`, `start_page`, `end_page` | Section list | Correct | ✅ |
| 5.7 | `detect_tables` returns list of table locations | Table list | Correct | ✅ |
| 5.8 | `detect_images` returns list of image locations | Image list | Correct | ✅ |

#### registry.py — document_elements table (10 tests)

| # | Test Case | Expected | Actual | Status |
| :- | :-------- | :------- | :----- | :----- |
| 6.1 | `store_elements` inserts single element row | Row inserted | Inserted | ✅ |
| 6.2 | `store_elements` returns count of inserted rows | Count = 1 | Count = 1 | ✅ |
| 6.3 | `store_elements` inserts multiple elements in batch | All inserted | All inserted | ✅ |
| 6.4 | `store_elements` returns correct count for batch insert | Count = 3 | Count = 3 | ✅ |
| 6.5 | `get_elements` returns all rows for a doc_id | Matching rows | Correct | ✅ |
| 6.6 | `get_elements` returns empty list for unknown doc_id | `[]` | `[]` | ✅ |
| 6.7 | `get_elements_by_type` filters by element_type | Correct type | Correct | ✅ |
| 6.8 | `get_elements_by_type` returns empty for unknown type | `[]` | `[]` | ✅ |
| 6.9 | `delete_elements` removes all rows for a doc_id | Rows removed | Removed | ✅ |
| 6.10 | `delete_elements` returns count of deleted rows | Correct count | Correct | ✅ |

---

## 8. Test Success Criteria and Checklist

| Criterion | Status | Evidence |
| :-------- | :----: | :------- |
| EKS folder structure compliant with AGENTS.md | ✅ | All directories exist per §6 |
| `eks.yml` created and environment activates | ✅ | All dependencies importable |
| Canonical schema (base/setup/config) with one-to-one mapping | ✅ | \$ref resolution validated |
| Schema loader resolves all \$ref types | ✅ | Migrated from deprecated `RefResolver` to `referencing` |
| Document registry CRUD operational | ✅ | test_document_registry passed |
| Revision management: preserve all revisions, is_latest flag | ✅ | test_revision_manager passed |
| PDF, DOCX, XLSX parsers via abstract plug-in interface | ✅ | BaseParser abstract; concrete parsers implement interface |
| DGN, DWG parser stubs for Phase 3 | ✅ | DGNParserStub, DWGParserStub created |
| Tiered logger (levels 0-3), debug object, trace table | ✅ | test_logger passed |
| SSOT config registry; zero hardcoded global params | ✅ | All paths via ConfigRegistry.get() |
| Document Registry G1-G3 remediation (T1.21) | ✅ | test_remediation_t121_cases pass |
| Extended Metadata Support (T1.22) | ✅ | 11 fields supported; asset_tags JSON array passed |
| `__init__.py` files created per AGENTS.md §4.2 | ✅ | engine, core, parsers, logging |
| Deprecated API usage resolved | ✅ | `RefResolver` → `referencing` |
| Asset schema files present (T1.20): 3 files, 13 fragments | ✅ | `test_asset_schema_files_exist`, `test_asset_base_schema_fragments` |
| Asset config validates against setup schema | ✅ | `test_asset_schema_validation` |
| R39 zero-code extensibility: conditional_fragments | ✅ | `test_r39_conditional_fragments` |
| Ontology files present and validated (T1.23–T1.27) | ✅ | 3 files, alias resolution, class map validation |
| Ontology includes Document hierarchy + DataSheet/OpsManual | ✅ | DWG/PID_Drawing/Specification/DataSheet/Manual/OpsManual/Report |
| Error code taxonomy — base + config schema files exist and validate | ✅ | 65 codes (30 system + 35 data); correct format, severity, phase/module/function codes |
| Message catalog — base + config schema files exist and validate | ✅ | 33 messages (8 milestone, 8 status, 4 progress, 8 warning, 4 error) |
| Error manager — 5 public functions implemented | ✅ | `handle_system_error`, `handle_data_error`, `fail_fast`, `get_error_summary`, `get_health_impact` |
| Message manager — `show` + `list_messages` with template hydration | ✅ | Verbosity filtering, category filter |
| Health scorer — 6-dimension scoring with correct weights | ✅ | completeness 20%, confidence 20%, structural 20%, source 15%, xref 15%, consistency 10% |
| Structure detector — 4 detection methods + cover type A–E | ✅ | `detect_cover_page`, `detect_sections`, `detect_tables`, `detect_images` |
| `document_elements` table CRUD — `store_elements`, `get_elements`, `get_elements_by_type`, `delete_elements` | ✅ | 10 tests all passing |
| All T1.32 unit tests pass (47/47) | ✅ | No regressions in existing tests |
| All schemas consolidated under `eks/config/schemas/` (T1.33) | ✅ | 13 JSON files in canonical location |
| Document schema extracted to dedicated 3-layer pattern (T1.34) | ✅ | 3 doc schema files; base clean of doc defs |
| Enhanced doc schema v2 with enums and registries (T1.35) | ✅ | 3 enums, 3 registries, cross-validation, 6 tests |
| DGN/DWG parser stubs importable and validator-ready | ✅ | `_validate_doc_registries` imports successfully |
| Auto-DDL generated from JSON schema (T1.36) | ✅ | `schema_to_ddl.py` generates DDL; `registry.py` uses it; `sync_schema()` works |
| File scanner walks directory and registers placeholders (T1.37) | ✅ | `file_scanner.py` discovers, validates, registers; 4 tests pass |
| Parser router maps file_type to parser class (T1.38) | ✅ | `parser_router.py` routes dynamically; 4 tests pass |
| Pipeline orchestrator coordinates Phase A/B/C (T1.39) | ✅ | `pipeline_orchestrator.py` runs full pipeline; 2 tests pass |
| Manual review workflow with correction and locking (T1.40) | ✅ | `review_manager.py` queries, corrects, locks; 4 tests pass |
| Error/message schemas follow 3-layer pattern (T1.41) | ✅ | `eks_error_setup_schema.json`, `eks_message_setup_schema.json` created; I014 resolved |
| Fragment schemas present (T1.42–T1.45) | ✅ | 4 files: project, discipline, department, facility |
| Base schema definitions added (T1.46) | ✅ | `project_entry_def`, `department_entry_def`, `facility_entry_def` |
| Config updated with real data (T1.46) | ✅ | P123/P456 → 131101/131242; $ref to fragments; I005 resolved |
| Setup schema updated with new properties (T1.46) | ✅ | `project_registry`, `department_registry`, `facility_registry` declared |
| 6 new fragment schema tests (T1.47) | ✅ | 59/59 total tests pass |
| T1.48 schema audit — duplicate defs removed, parser paths aligned, missing parsers added | ✅ | I022–I028 logged |
| I027 URI alignment — error/message base `$id` → filename-based pattern | ✅ | I027 resolved |
| Shared `verbosity_level` — consolidated into `eks_base_schema.json` SSOT | ✅ | Message + logging both `$ref` shared def |
| Shared `document_relationship_trigger_map` — consolidated into `eks_base_schema.json` SSOT | ✅ | Asset + doc configs both `$ref` shared def |
| `base_schema` added to all validation registries for cross-schema `$ref` | ✅ | `schema_loader.py`, `test_asset_schema.py`, `test_phase1.py` updated |
| All unit tests passing | ✅ | 235/235 passed |
| `phase_1_foundation_workplan.md` current (v3.40 COMPLETE) | ✅ | All T1.x tasks marked complete |
| `update_log.md` and `issue_log.md` current | ✅ | U001–U130, I001–I085 logged; all resolved except Phase 2/3 deferred items |
| Phase 1 report generated/updated | ✅ | This document (v2.7) |
| `project_setup.json` integrated into core 3-layer schema (T1.67) | ✅ | 5 defs in base, project_setup property in setup, values in config |
| `setup_validator.py` refactored to load from ConfigRegistry (T1.67) | ✅ | No more hardcoded folder/file/env lists |
| I046 resolved: project_setup 7 violations fixed | ✅ | Archived, SSOT chain complete |
| T1.68–T1.76 (Bootstrap completion) | ✅ | ErrorManager/MessageManager wired, run_id logger, traversal guard, update_doc_status with retry, Discovery/Parser I/O contracts, checkpoints saved, debug/status/message JSON outputs |
| T1.77 (Initiation integrity checks) | ✅ | ProjectSetupValidator gate in phase1_server, CLI --debug/--level flags, pipeline args validation |
| T1.78–T1.83 (Initiation hardening) | ✅ | DCC gaps closed (readability, env probe, output-path checks, --skip-readiness, error codes), config-driven paths, fallback removal (SSOT), eks_root schema-driven |
| T1.84–T1.89 (Initiation harmonization) | ✅ | Universal ValidationManager created, EKS setup schema reshaped to DCC object model, project_setup config extracted, validator refactored as thin adapter, unit tests migrated/added |
| Phase 1 FINAL COMPLETE | ✅ | All 89 tasks delivered, 24 schemas, 235 tests, all issues resolved or deferred |
| T1.99.1 Shared `run_pipeline(context)`/`bootstrap_pipeline()` helper | ✅ | `eks/engine/eks_engine_pipeline.py` (relocated from `pipeline_runner.py`, archived in T1.99.11); ConfigRegistry → SchemaLoader.load_all → DocumentRegistry → Error/MessageManager → ProjectSetupValidator readiness gate → PipelineOrchestrator.run_full_pipeline → checkpoint + on_phase |
| T1.99.2 Unified end-to-end CLI + `eks-pipeline` console_scripts | ✅ | `eks/engine/eks_engine_pipeline.py` real CLI; `eks/pyproject.toml` `[project.scripts] eks-pipeline = "eks.engine.eks_engine_pipeline:main"` |
| T1.99.3 `phase1_server._run` wired to `run_pipeline()` | ✅ | Inline A→C replaced; 409 guard + resolve_paths preserved |
| T1.99.4 Orphan `engine_endpoints.py` removed | ✅ | Archived to `archive/ui/backend/engine_endpoints.py` (no references remained) |
| T1.99.5 Canonical `eks/serve.py` added (§18.12) | ✅ | `server.py` retained as thin re-export shim |
| T1.99.6 `ConfigRegistry` SSOT at entry | ✅ | Singleton passed (not raw dict) to ProjectSetupValidator; resets on differing config_dir |
| T1.99.7 Tests + full suite green | ✅ | New `eks/test/test_pipeline_runner.py`; full suite 257/257 pass (stable) |
| `phase1_server._run` cancellation preserves `cancelled` status | ✅ | Bug fixed: cancelled job no longer overwritten with `failed` |

---

## 9. Files Archived, Modified, and Version Controlled

### Files Created (Phase 1.3 Initiation Harmonization & Hardening)
- `common/library/utility/validation/manager.py` — Universal ValidationManager (T1.84)
- `common/library/utility/validation/models.py` — Validation dataclasses (T1.84)
- `common/library/utility/validation/__init__.py` — Exports (T1.84)
- `eks/config/schemas/eks_project_setup_config.json` — Extracted project setup config (T1.86)
- `eks/test/test_setup_validator.py` — Unit tests for validator adapter (T1.88)
- `eks/test/test_validation_manager.py` — Unit tests for universal ValidationManager (T1.88)
- `eks/archive/phase_1.3_initiation_harmonization_workplan.md` — Harmonization workplan (T1.89, archived)
- `eks/archive/phase_1_t179_t183_report.md` — Hardening test report (T1.89, archived)
- `eks/engine/core/io_contracts.py` — central input/output contracts (T1.72)

### Files Modified (Initiation Harmonization & Hardening)
- `eks/config/schemas/eks_base_schema.json` — Replaced flat-array defs with 8 object defs (v1.7.0, T1.85)
- `eks/config/schemas/eks_setup_schema.json` — Reshaped project_setup structure (v1.4.0, T1.85)
- `eks/config/schemas/eks_config.json` — References extracted config file (v1.5.0, T1.86)
- `eks/engine/core/setup_validator.py` — Adapter delegating to ValidationManager (v0.7, T1.87)
- `eks/ui/backend/phase1_server.py` — readiness gate, args, log persistence (T1.75-T1.83)
- `eks/engine/core/pipeline_orchestrator.py` — Error/message manager, contracts, checkpoints (T1.68-T1.72)
- `eks/engine/core/registry.py` — status update with retry, sync DDL (T1.71)
- `eks/engine/core/context.py` — EKSPaths posix conversion (T1.74)
- `eks/engine/logging/logger.py` — run_id logging (T1.69)
- `eks/knowledge.json` — records Phase 1.3 complete (v2.3.0, T1.89)
- `eks/log/update_log.md` — logged updates U094–U130 (T1.89)
- `eks/log/issue_log.md` — logged/resolved I047–I085 (T1.89)
- `common/universal_pipeline_architecture_design.md` — records universal ValidationManager (T1.89)
- `eks/workplan/phase_1_foundation_workplan.md` — version 3.40 consolidated workplan (T1.89)

### Files Archived
- `eks/config/schemas/project_setup.json` → `eks/archive/project_setup.json` (integrated to core schema, T1.67)
- `eks/archive/phase_1.3_initiation_harmonization_workplan.md` — stand-alone workplan archived

### Files Verified (no changes needed)
- All previous Phase 1 implementation files in `engine/core/`, `engine/parsers/`, `engine/logging/`
- `eks/config/schemas/eks_asset_*.json` (3 files)

---

## 10. Recommendations for Future Actions

1. **Phase 2 readiness**: All Phase 1 dependencies verified and ready for chunking/embedding/vector storage. Pipeline infrastructure (SchemaToDDL, FileScanner, ParserRouter, PipelineOrchestrator, ManualReviewManager) operational.
2. **Replace placeholder project data**: `eks_config.json` `project_rules_registry` and `discipline_registry` contain P123/P456 example entries (I005). Replace with actual WSD11 disciplines once confirmed by project team.
3. **Phase 3 parser stubs**: DGN and DWG parser stubs fixed to implement BaseParser interface; full implementations deferred to Phase 3.
4. **Bulk ingestion**: T1.35's document type, file type, and element type registries plus T1.37's FileScanner provide the routing framework for Phase 3 bulk document ingestion (I009).
5. **Pipeline testing**: Phase B (parse → detect → score) end-to-end testing requires real PDF documents. Use TWRP sample data in Phase 2.
6. **T1.32 integration testing**: Wire error/message/health/structure modules into the actual TWRP ingestion pipeline (Phase 2) to validate end-to-end error/message flow.
7. **Structure detector coverage**: Current regex-based detection works for test patterns; real TWRP PDFs may require pymupdf-based extraction.
8. **Health scorer calibration**: Default dimension scores may need tuning after Phase 3 ingestion on real documents.
9. **Document elements in UI**: Phase 5 Manual Verification UI should display `document_elements` for human review.

### 10.2 Data Challenges Identified

During analysis of `eks/data/twrp/` sample data, 7 challenges were identified and logged to `eks/log/issue_log.md` (I015–I021):

1. **DGN format gap** (I015): 48 DGN files in `design_doc/0363/DGN file/` (42), `design_doc/1992/2026 06 18 R1/DGN/` (6), and `project_spec/Volume 5/Part-II` (5). No parser implementation exists. All will be registered with `extract_status = 'failed'` and flagged for manual review. Resolution: Phase 3 CAD parser evaluation (OpenDesign SDK, LibreCAD, or commercial library).

2. **Revision folder inconsistency** (I016): R0 revisions use 3-subfolder structure (`Client Response/`, `Native/`, `Submission/`); R1+ revisions place files directly in revision folder with optional `DGN/` and `PDF/` sub-subfolders. Some submittals (e.g., 0363) have no revision folders. FileScanner recursive walk handles most cases; verify edge cases in Phase 2.

3. **Two project codes** (I019): `project_spec/` uses project code `131101`; `design_doc/` uses `131242`. Both are valid WSD11 project documents. FilenameParser must extract `project_code` dynamically from document number pattern, not hardcode.

4. **Datadrop column variability** (I020): 7 sheets range from 33 (Pipeline) to 112 (CONTROLVALVE) columns. CONTROLVALVE has dual manufacturer fields (valve + actuator). 13 asset schema fragments must cover all columns; unmapped columns silently dropped.

5. **Data incompleteness** (I021): Sheet3 shows 22–64% pending fields. Equipment 59.9%, Instrument 63.5% most incomplete. Health scoring will flag records; manual review workflow (T1.40) is critical for data quality.

**Status summary**: 2 resolved (I017, I018), 5 open (I015, I016, I019, I020, I021). See `eks/workplan/eks_system_workplan.md` §11 for phase assignments.

---

## 11. Lessons Learned

1. **Database Schema Evolution**: DuckDB `IF NOT EXISTS` for table creation does not handle column additions. Manual schema migration using `ALTER TABLE` was necessary to support existing databases.
2. **Schema Validation Rigor**: Strict `additionalProperties: false` in setup schemas requires config files to be strictly compliant, precluding descriptive notes or comments within the JSON.
3. **Structured Data in Relational DB**: Using the `JSON` data type for fields like `asset_tags` allows for flexible, multi-valued storage within a standard SQL table structure.
4. **Document Type Code Alignment**: Aligning document type codes (DWG/PI-PID/SPC/DS/MAN/OM/RPT) with ontology classes required adding `DataSheet` and `OpsManual` subclasses to the ontology, following the existing `Drawing→PID_Drawing` subclass pattern.
5. **Parser Import Validation**: Validating `parser_class` importability at load time catches misconfigured parsers early but requires stub modules for Phase 3 formats (DGN, DWG) to be present.
6. **DDL from Schema**: Auto-generating DDL from JSON schema requires handling `id` as a special PRIMARY KEY (not in schema definitions) and `ingested_at` as TIMESTAMP (schema says "string" with format "date-time"). Project metadata fields (project_title, project_number) are intentionally nullable for backward compatibility with minimal registration.
7. **Parser Interface Consistency**: DGN/DWG stubs originally had different `parse()` signatures than BaseParser. Fixed to match: `parse()` takes no args (uses `self.file_path`), `extract_metadata()` returns dict. All parsers must implement both abstract methods.
8. **Test Isolation**: Tests that register documents affect later tests' expected counts. Changed SQL injection test from `assertEqual(len, 4)` to `assertGreaterEqual(len, 4)` for resilience.
9. **Real data complexity**: Analysis of twrp sample data reveals revision folder patterns (flat vs subfoldered), mixed file types per submittal, and format gaps (DGN) not anticipated in initial schema design. FileScanner and ParserRouter handle most cases; DGN remains a gap requiring Phase 3 evaluation.
10. **Data quality variance**: Asset datadrop has high incompleteness rates (22–64% pending fields). Health scoring dimensions (completeness, consistency) surface these naturally through the existing pipeline. ManualReviewManager workflow becomes essential for data quality remediation.
11. **DuckDB compatibility (T1.32)**: Avoided auto-increment identity column for `document_elements` table (DuckDB uses `GENERATED ALWAYS AS IDENTITY` rather than `AUTOINCREMENT`); used composite index instead.
12. **Error code enumeration (T1.30)**: 65 codes is manageable; add code generation script if catalog grows beyond 200+.
13. **Cover type detection (T1.32)**: Test text patterns with exactly 60 chars for Type B correctly triggers `is_scanned=False`; 50-char threshold is the delimiter between scanned vs. non-scanned.
14. **Message template hydration (T1.31)**: Using `str.format(**kwargs)` for template variables is simple and sufficient; consider `string.Template` if variable names conflict with format specifiers.

---

---

## 13. Phase 1 Final Closure (T1.67)

The final Phase 1 task (T1.67) integrated the orphan `project_setup.json` schema into the core 3-layer pattern, resolving I046. This closes the last architectural gap in Phase 1.

### Summary of T1.67 Changes

| File | Action | Version |
| :--- | :----- | :------ |
| `eks/config/schemas/eks_base_schema.json` | Added 5 definitions: `required_folder_setup_def`, `required_engine_subfolder_setup_def`, `required_file_setup_def`, `environment_setup_def`, `validation_options_def` | v1.6.0 |
| `eks/config/schemas/eks_setup_schema.json` | Added `project_setup` property with `$ref` to base defs; added to `required` array | v1.3.0 |
| `eks/config/schemas/eks_config.json` | Added `project_setup` section with folder lists, file lists, environment config, validation options | v1.4.0 |
| `eks/archive/project_setup.json` | Original standalone schema archived here | — |
| `eks/engine/core/setup_validator.py` | Constructor accepts `config_registry` param; loads rules from config chain with backward-compatible fallback | v0.2 |
| `eks/test/test_phase1.py` | Added 2 tests: `test_base_schema_has_project_setup_defs`, `test_setup_schema_has_project_setup` | — |

### Phase 1 Final Statistics

| Metric | Value |
| :----- | :---- |
| Tasks completed | 67 (T1.1–T1.67) |
| Test count | 120 |
| Schema files | 23 (core: 3, asset: 3, doc: 3, ontology: 3, error: 3, message: 3, fragments: 4, project rules: 1) |
| Requirements met | 22 (R01, R02, R06–R09, R21, R22, R26, R29, R33–R36, R39, R44, R51–R58) |
| Issues resolved | 34 (I001–I014, I017–I018, I022–I034, I036–I046) |
| Issues deferred | 5 (I015 DGN gap, I016 folder hierarchy, I019 dual projects, I020 column coverage, I021 data incompleteness) |
| Phases fed | Phase 2 (chunking/embedding), Phase 1.2 (UI/sub-pipeline) |

## 15. Bootstrap Updates & Initiation Hardening (T1.68–T1.83)

All 16 Bootstrap and Initiation Integrity/Hardening tasks (T1.68–T1.83) are complete:

### 15.1 Bootstrap Completion (T1.68–T1.76)
- **T1.68 & T1.75**: ErrorManager and MessageManager wired into PipelineOrchestrator and constructed in server thread, activating error/message template catalog lookup and hydration in production.
- **T1.69**: Structured logging and correlation IDs implemented. `run_id` field in logger, threaded as `job_id` in server, prepended to all logs.
- **T1.70**: Security traversal guard added to file loading and pipeline start endpoints (403 on paths outside project root).
- **T1.71**: Registry updates use singleton DB connection and retry wrapper.
- **T1.72**: Contract enforcement implemented. Wraps orchestrator phases with ParserInput/Output and DiscoveryInput/Output contracts.
- **T1.73**: Checkpoints persisted as JSON per phase (`checkpoint_{job_id}_{A,B,C}.json`) in output directory to enable resume-from-failure.
- **T1.74**: Cross-platform gaps closed. Relative paths anchored, `Path.as_posix()` used.
- **T1.76**: Final status, messages catalog, and debug run artifacts persisted to JSON in output directory.

### 15.2 Initiation Integrity & Hardening (T1.77–T1.83)
- **T1.77**: ProjectSetupValidator gate wired into server thread start (fails fast if readiness != YES). Arguments (`data_dir` exists, `recursive` bool) validated before concurrency locks.
- **T1.78**: Closed 6 DCC initiation gaps: `eks.yml` path fix, readability check, dependency probe, output-path validation, `--skip-readiness` override, error code constants.
- **T1.79**: `P1-SETUP-*` error codes attached to validator results. Gate failures raised via ErrorManager.
- **T1.80**: Paths derived from `config.global_paths` and `registry` config (no hardcoding).
- **T1.81**: Fallback lists removed from `setup_validator.py` to enforce SSOT config.
- **T1.82**: Honored `validation_options` and defaults from config.
- **T1.83**: Package root `eks_root` schema-driven (enables package relocation).

### 15.3 T1.79–T1.83 Detailed Test Cases

The following detailed test-case tables are integrated from the archived `phase_1_t179_t183_report.md` (RP-EKS-P1-T179-001). All cases passed; full suite 215/215.

#### 15.3.1 T1.79 — Error Codes + ErrorManager into Readiness Gate

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| T1.79-a | `test_error_codes_summary_at_top_level` — `validate_all()` returns `error_codes` at root level | ✅ | New test |
| T1.79-b | `test_folder_missing_entries_carry_error_code` — each missing folder entry has `error_code` | ✅ | New test |
| T1.79-c | `test_file_missing_entries_carry_error_code` — each missing file entry has `error_code` | ✅ | New test |
| T1.79-d | `test_dependency_missing_entries_carry_error_code` — dependency entries carry `error_code` | ✅ | New test |
| T1.79-e | `test_environment_has_error_code_when_missing` — env entry has `error_code` | ✅ | New test |
| T1.79-f | `test_output_path_unwritable_entries_carry_error_code` — output entries carry `error_code` | ✅ | New test |
| T1.79-g | `test_pipeline_start_readable_data_dir` — server returns readable status (no blocked gate) | ✅ | Existing (T1.78) |
| T1.79-h | `test_pipeline_runs_to_completion` — full pipeline completes via `ErrorManager` (no RuntimeError) | ✅ | Existing |

#### 15.3.2 T1.80 — Paths from Schema Config

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| T1.80-a | `test_config_paths_endpoint` — returns `data_dir`, `output_dir` from config | ✅ | Existing |
| T1.80-b | `test_output_paths_validated` — output_dir derived from config, not hardcoded | ✅ | Validated via grep |
| T1.80-c | Pipeline runs produce checkpoint files in config-driven `output/` dir | ✅ | Integration test |

#### 15.3.3 T1.81 — Remove Hardcoded Fallback Lists (SSOT)

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| T1.81-a | `test_raises_value_error_without_config` — `setup_validator` raises when no config provided | ✅ | New test |
| T1.81-b | `test_config_registry_overrides_defaults` — config values used instead of hardcoded defaults | ✅ | Existing |

#### 15.3.4 T1.82 — Schema-Driven Input Defaults

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| T1.82-a | `test_validate_all_creates_missing_folders` — folder creation respects `auto_create` param | ✅ | Existing |
| T1.82-b | `test_data_dir_derived_from_config` — `data_dir` default from `global_paths.data_dir` | ✅ | Validated via grep |
| T1.82-c | `test_config_paths_endpoint` returns all keys from `global_paths` without hardcoded fallback | ✅ | Existing |

#### 15.3.5 T1.83 — `eks` Package Root Schema-Driven

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| T1.83-a | `eks_root` exists in `eks_base_schema.json` `global_paths_def` | ✅ | Schema grep |
| T1.83-b | `eks_root: "eks"` in `eks_config.json` | ✅ | Config grep |
| T1.83-c | Zero `PRJ_DIR / "eks"` code-level literals in `phase1_server.py` | ✅ | Project-wide grep confirms 0 |

#### 15.3.6 Regression

| ID | Test | Status | Notes |
| :- | :--- | :----: | :---- |
| REG-1 | Full 215-test suite | ✅ | 215/215 pass, 0 failures, 17.6s |

### 15.4 Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)

Flattened the `project_setup` wrapper in `eks_config.json` so EKS setup values (`folders` / `root_files` / `schema_files` / `environment` / `dependencies` / `project_metadata`) live **top-level**, matching DCC `project_config.json`. This lets the universal `ValidationManager` (and a future universal schema loader) serve both projects with **zero per-project branching**.

| Task | Description | Status |
| :--- | :---------- | :----: |
| T1.90 | Flatten `project_setup` in `eks_config.json` — 7 setup keys top-level; removed wrapper; fixed title note | ✅ |
| T1.91 | `eks_setup_schema.json` v1.5.0 — dropped `project_setup` wrapper; 7 setup keys declared top-level (reuse `eks_base_schema.json` defs); `additionalProperties:false` kept | ✅ |
| T1.92 | `setup_validator.py` — reads setup from top-level config (DCC pattern) with `project_setup` backward-compat fallback; API + P1-SETUP-* + ErrorManager unchanged | ✅ |
| T1.93 | `phase1_server.py` — `_cfg.get("project_setup", _cfg)` flatten-aware | ✅ |
| T1.94 | Deleted orphan `eks_project_setup_config.json` (archived per AGENTS.md §5.3); no dangling refs | ✅ |
| T1.95 | Tests updated (`test_setup_schema_has_project_setup`, new `test_config_setup_values_top_level`); full EKS suite **236/236 pass** | ✅ |

Resolves residual I086 (wrapper redundancy vs DCC). Logged U131.

---

## 16. Phase 1.3 Initiation Harmonization (T1.84–T1.89)

**Source workplan (archived)**: [phase_1.3_initiation_harmonization_workplan.md](../../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
**Status**: ✅ COMPLETE — T1.84–T1.89 implemented. 235/235 tests pass (19 validator tests + 20 universal-module tests added).

### 16.1 Scope
Harmonize EKS's `project_setup` schema and validation code with DCC's universal initiation pattern to achieve schema-design consistency and code-module universality.

| Task | Description | Status |
| :--- | :---------- | :----: |
| T1.84 | Create universal `ValidationManager` in `common/library/utility/validation/manager.py` — 6 DCC-aligned methods | ✅ |
| T1.85 | Reshape EKS `project_setup` schema: replace flat-array defs with 8 DCC-aligned object defs in `eks_base_schema.json` v1.7.0; reshape `project_setup` property in `eks_setup_schema.json` v1.4.0 | ✅ |
| T1.86 | Extract `project_setup` instance data to `eks_project_setup_config.json` v1.0.0 (20 folders, root files, schema files, environment, dependencies, project metadata) | ✅ |
| T1.87 | Refactor `setup_validator.py` v0.7 as thin adapter delegating to universal `ValidationManager`; preserves `P1-SETUP-*` codes and ErrorManager wiring | ✅ |
| T1.88 | Migrate `test_setup_validator.py` (19 tests); create `test_validation_manager.py` (20 tests). Full suite 235/235 green | ✅ |
| T1.89 | Update workplan, `knowledge.json` v2.3.0, `update_log` (U130), `issue_log` (I085 resolved), universal architecture doc | ✅ |

### 16.2 Test Results
- `test_validation_manager.py` — universal ValidationManager: 20 passed.
- `test_setup_validator.py` — ProjectSetupValidator adapter: 19 passed.
- All other EKS tests: 196 passed.
- **Total**: 235/235 passed.

### 16.3 Test Case Details

#### T1.84 — Universal ValidationManager (20 tests)
- `test_validate_folders_all_exist` — existing folder passes
- `test_validate_folders_missing_required` — missing required folder returns MISSING_FOLDER
- `test_validate_folders_auto_create` — folder created when `auto_created=True`
- `test_validate_folders_empty` — empty list returns all_exist=True
- `test_validate_named_files_found` — found file passes
- `test_validate_named_files_missing_required` — missing required file returns MISSING_FILE
- `test_validate_named_files_custom_name_key` — `filename` key for schema_files
- `test_validate_named_files_empty` — empty list returns all_exist=True
- `test_validate_environment_no_env_entries` — empty env valid
- `test_validate_environment_python_match` — current Python version matches
- `test_validate_environment_python_mismatch` — PYTHON_MISMATCH code for mismatched version
- `test_validate_dependencies_empty` — empty list passes
- `test_validate_dependencies_available` — stdlib modules `os`/`json` found
- `test_validate_dependencies_missing` — missing package returns MISSING_DEPENDENCY
- `test_validate_discovery_rules_empty` — empty rules valid
- `test_validate_discovery_rules_dir_exists` — existing dir passes
- `test_validate_discovery_rules_dir_missing` — missing dir returns DISCOVERY_DIR_MISSING
- `test_validate_project_setup_full_pass` — full config passes, readiness=YES
- `test_validate_project_setup_fail` — missing folder, readiness=NO, error_codes populated
- `test_validate_project_setup_empty` — empty config, readiness=YES

#### T1.87/T1.88 — ProjectSetupValidator Adapter (19 tests)
- `test_validate_all_returns_expected_structure` — result has folders/files/environment/readiness
- `test_validate_all_creates_missing_folders` — auto-create via adapter
- `test_readiness_no_when_missing_files` — missing required files → readiness=NO
- `test_readiness_yes_when_all_exist` — all present → readiness=YES
- `test_get_readiness_status_validates_on_demand` — lazy validate_all call
- `test_get_missing_items_returns_paths` — folders/files as string lists
- `test_config_registry_overrides_defaults` — config-driven validation
- `test_verbose_print_does_not_crash` — verbose=True safe
- `test_dependency_probe_returns_available` — deps result structure
- `test_output_paths_validated` — output_paths result structure
- `test_validate_all_includes_dependencies_and_output_paths` — full result
- `test_folder_missing_entries_carry_error_code` — P1-SETUP-F001 preserved
- `test_file_missing_entries_carry_error_code` — P1-SETUP codes on files
- `test_environment_has_error_code_when_missing` — P1-SETUP-F003 for missing eks.yml
- `test_dependency_missing_entries_carry_error_code` — P1-SETUP-D001
- `test_output_path_unwritable_entries_carry_error_code` — P1-SETUP-O001
- `test_error_codes_summary_at_top_level` — error_codes array in result
- `test_get_missing_items_backward_compat` — plain string paths
- `test_raises_value_error_without_config` — SSOT enforcement, raises ValueError

---

## 17. Schema Discovery & Registration — Discovery-Driven Loading (T1.96)

**Objective**: Replace 22 hardcoded filenames in `schema_loader.py` with config-driven loading using explicit `schema_files` + glob-based `discovery_rules`. Extract shared `discover_schema_files()` from DCC into `common/`.

### 17.1 Sub-task Results

| Sub-Task | Result | Details |
| :------- | :----- | :------ |
| T1.96.1 | ✅ PASS | `discover_schema_files()`, `safe_resolve()`, `find_schema_file()` extracted to `common/library/loader/schema_discovery.py`. Core glob-walk, exclude-filter, merge-with-explicit loop ported from DCC `ref_resolver.py:164-256`. |
| T1.96.2 | ✅ PASS | 5 discovery rules added to `eks_config.json`: `*_base_schema.json`, `*_base.json`, `*_setup_schema.json`, `*_config.json`, `*.json` (parsers). Directory paths use `eks/config/schemas/` prefix. |
| T1.96.3 | ✅ PASS | `schema_loader.py` refactored: bootstrap loads 3 files (base/setup/config), then reads `schema_files` + `discovery_rules` from config. Config-driven loop replaces 22 formerly hardcoded `_load_json()` calls. |
| T1.96.4 | ✅ PASS | `ValidationManager.validate_discovery_rules()` wired into `setup_validator.py` `validate_all()`. Four config-driven tests added to `test_validation_manager.py`. |
| T1.96.5 | ✅ PASS | `common/universal_pipeline_architecture_design.md` §3.16 already documented the pattern. Verified alignment with extracted `discover_schema_files()`. |
| T1.96.6 | ✅ PASS | **236/236 tests pass**. Root cause fix: `*_base.json` rule added to catch `eks_error_code_base.json` and `eks_message_base.json` (outlier filenames ending in `_base.json` not `_base_schema.json`). |

### 17.2 Files Modified

| File | Change |
| :--- | :----- |
| `common/library/loader/__init__.py` | New — exports `discover_schema_files`, `find_schema_file`, `safe_resolve` |
| `common/library/loader/schema_discovery.py` | New — extracted from DCC `ref_resolver.py:164-256` |
| `eks/config/schemas/eks_config.json` | Added 5 `discovery_rules` entries |
| `eks/engine/core/schema_loader.py` | Refactored `load_all()` for config-driven discovery; added `_project_root()` |
| `eks/engine/core/setup_validator.py` | Wired `validate_discovery_rules()` in `validate_all()` |
| `common/universal_pipeline_architecture_design.md` | §3.16 pattern alignment verified |

### 17.3 Test Summary

```
236 passed in 16.84s
```

All 71 Phase 1 tests, all 24 schema tests, all 20 validation manager tests, all 19 setup validator tests, and all integration server tests pass.

---

## 18. System Parameters — SSOT Centralization (T1.97/I088)

**Objective**: Resolve I088 by centralizing runtime behavior flags/timeouts/retry values in `eks_config.json -> system_parameters` and a reusable common helper.

### 18.1 Results

| Sub-Task | Result | Details |
| :------- | :----- | :------ |
| T1.97.1 | ✅ PASS | Added `common/library/config/__init__.py` with `normalize_system_parameters()` and `get_system_param()`. Supports EKS flat object, direct flat object, and DCC-style array entries with `value`, `default_value`, or `default`. |
| T1.97.2 | ✅ PASS | Added `system_parameters_def` to `eks_base_schema.json` v1.8.0 with 9 typed runtime settings. |
| T1.97.3 | ✅ PASS | Added optional `system_parameters` property to `eks_setup_schema.json` v1.6.0. |
| T1.97.4 | ✅ PASS | Added `system_parameters` block to `eks_config.json` v1.6.0 and removed standalone `registry.timeout`. |
| T1.97.5-h | ✅ PASS | Wired `phase1_server.py`, `error_manager.py`, `registry.py`, and `eks/server.py` to read T1.97 runtime knobs from config. |
| T1.97.9 | ✅ PASS | Added `test_system_parameters.py`; full EKS suite passed. |

### 18.2 Test Summary

```
conda run -n eks python -m pytest eks/test/test_system_parameters.py
7 passed in 1.67s

conda run -n eks python -m pytest eks/test/
243 passed, 8 warnings in 13.58s
```

The full suite required unsandboxed execution because Phase 1 server tests bind local sockets; the sandbox blocked socket creation with `PermissionError`.

### 18.3 Files Modified

| File | Change |
| :--- | :----- |
| `common/library/config/__init__.py` | New shared config helper module |
| `eks/config/schemas/eks_base_schema.json` | v1.8.0, added `system_parameters_def`, removed `registry.timeout` |
| `eks/config/schemas/eks_setup_schema.json` | v1.6.0, added `system_parameters` property |
| `eks/config/schemas/eks_config.json` | v1.6.0, added `system_parameters` values |
| `eks/engine/core/config_registry.py` | Added `get_system_param()` method |
| `eks/engine/core/error_manager.py` | Reads `fail_fast` from config |
| `eks/engine/core/registry.py` | Reads retry/db timeout parameters from config |
| `eks/ui/backend/phase1_server.py` | Reads debug/log/readiness/retry parameters from config |
| `eks/server.py` | Reads API/Ollama proxy timeouts from config |
| `eks/test/test_system_parameters.py` | New focused tests |

---

## 19. Universal Architecture Elevation (T1.97.10–14 / I091)

**Objective**: Resolve I091 by elevating `system_parameters` from a project-specific implementation to a formally defined universal pipeline feature (L15) in `common/universal_pipeline_architecture_design.md`, and register `config/` as an architecture-aligned sub-package in `common/library/__init__.py`.

### 19.1 Results

| Sub-Task | Result | Details |
| :------- | :----- | :------ |
| T1.97.10 | ✅ PASS | Registered `config/` as architecture-aligned sub-package in `common/library/__init__.py` (docstring, `from . import config`, `__all__`). |
| T1.97.11 | ✅ PASS | Added L15 — System Parameters / Runtime Behavior Config to `common/universal_pipeline_architecture_design.md` §2.2 inventory, §2.3 package structure, §2.4 per-library detail. |
| T1.97.12 | ✅ PASS | Added §3.17 System Parameters Pattern (schema-defined runtime behavior knobs, universal normalization, both flat-object and array-of-entries shapes). |
| T1.97.13 | ✅ PASS | Updated §4.1 When to Apply, §4.2 Implementation Order, §9 Appendix A checklist, §10 Appendix B success criteria; doc version → 1.6. |
| T1.97.14 | ✅ PASS | Updated `eks/knowledge.json` → v2.5.0 with L15 elevation status and revision entry. |

### 19.2 Test Summary

```
conda run -n eks python -m pytest eks/test/
243 passed, 8 warnings in 36.48s
```

`common.library.config` imports cleanly as a registered sub-package; `eks/knowledge.json` is valid JSON.

### 19.3 Files Modified

| File | Change |
| :--- | :----- |
| `common/library/__init__.py` | Registered `config` sub-package (docstring, import, `__all__`) |
| `common/universal_pipeline_architecture_design.md` | v1.6: L15 inventory/structure/detail, §3.17 pattern, §4.1/§4.2/§9/§10 updates |
| `eks/knowledge.json` | v2.5.0: L15 elevation status, revision entry |
| `eks/log/issue_log.md` | I091 marked ✅ Resolved |
| `eks/log/update_log.md` | U134 added |
| `eks/workplan/phase_1_foundation_workplan.md` | §19.3 tasks → ✅, §19.4 success criteria, version → 3.46 |

---

## 20. Universal Path Resolution & Schema-Driven Initialization (T1.98 / I089 / I090)

**Objective**: Resolve I089 by adopting EKS's `global_paths` as the universal canonical schema-driven path pattern and providing a shared `PathResolver` in `common/library/paths/` that normalizes both EKS and DCC path shapes. Resolve I090 by bringing EKS to DCC parity for `workflow_files`/`tool_files` (schema-driven initialization). `folder_creation` is satisfied by the resolver deriving the create-list from the canonical `global_paths` — EKS deliberately does **not** add a separate DCC-style `folder_creation` block.

### 20.1 Design Decision (I089 re-evaluation)

A re-audit of DCC's actual path code found its model weaker than EKS's:
- DCC `ProjectSetupValidator.validate_named_files()` and `validate_folders()` use hardcoded `project_root / base_path / "data"` literals and a `default_base_path()` that traverses `os.path.dirname(__file__)` to locate the repo root — both are anti-patterns.
- DCC `discovery_rules` are used only for **schema discovery**, not for general path resolution; `required_directories` live under `folder_creation`.

By contrast, EKS's `global_paths` (hardened by T1.80/T1.82/T1.83 — no hardcoded fallbacks) is genuinely schema-driven SSOT. Therefore the universal pattern adopts EKS `global_paths` as canonical, with a bidirectional `PathResolver` normalizing the DCC shape into it.

### 20.2 Results

| Sub-Task | Result | Details |
| :------- | :----- | :------ |
| T1.98.1 | ✅ PASS | Created `common/library/paths/resolver.py` with `resolve_paths(project_root, config) -> ResolvedPaths` and `ResolvedPaths` dataclass (data_dir, output_dir, archive_dir, config_dir, log_dir, schema_dir, eks_root, source). Handles EKS `global_paths` directly; normalizes DCC `folder_creation.required_directories` + `discovery_rules.directory` + native `base_path/"data"` default. |
| T1.98.2 | ✅ PASS | `common/library/paths/__init__.py` exports `resolve_paths`, `ResolvedPaths`. |
| T1.98.3 | ✅ PASS | `ConfigRegistry` routes all 6 path properties through `resolve_paths()`; `phase1_server.py` updated at 3 sites (`_handle_config_paths`, `_handle_pipeline_start`, `_run` closure) to use `resolve_paths()` instead of inline `PRJ_DIR / _eks_root / gp.get(...)`. |
| T1.98.4 | ✅ PASS | `common/universal_pipeline_architecture_design.md` v1.7: L16 — Path Resolution / Schema-Driven Paths (§2.2 inventory, §2.3 package structure, §2.4 detail); §3.18 Path Resolution Pattern (canonical = EKS `global_paths`); §4.1/§4.2 application guidelines, §9 checklist, §10 success criteria. |
| T1.98.5 | ✅ PASS | `eks/knowledge.json` → v2.6.0 with L16 elevation status and I089/I090 resolution entries. |
| T1.98.6 | ✅ PASS | `eks_base_schema.json` v1.9.0: added `workflow_file_entry_def`, `tool_file_entry_def`. `eks_setup_schema.json` v1.7.0: added `workflow_files`, `tool_files` properties. `eks_config.json` v1.7.0: added instance blocks (DCC parity). |
| T1.98.7 | ✅ PASS | `setup_validator.py` validates `workflow_files`/`tool_files` via `_validate_named_files()`; `ConfigRegistry` exposes them. Folder creation driven by canonical `global_paths`. |
| T1.98.8 | ✅ PASS | Added `eks/test/test_path_resolver.py` (9 tests); full EKS suite 252/252 pass. I089 + I090 closed. |

### 20.3 Test Summary

```
conda run -n eks python -m pytest eks/test/test_path_resolver.py -v
eks/test/test_path_resolver.py::TestPathResolver::test_resolve_dcc_shape PASSED
eks/test/test_path_resolver.py::TestPathResolver::test_resolve_eks_shape PASSED
eks/test/test_path_resolver.py::TestPathResolver::test_resolved_paths_absolute PASSED
eks/test/test_path_resolver.py::TestPathResolver::test_resolved_paths_dcc_absolute PASSED
eks/test/test_path_resolver.py::TestConfigRegistryPaths::test_eks_config_has_workflow_and_tool_files PASSED
eks/test/test_path_resolver.py::TestConfigRegistryPaths::test_path_properties_routed_through_resolver PASSED
eks/test/test_path_resolver.py::TestSetupValidatorPipelineFiles::test_workflow_and_tool_files_validated PASSED
eks/test/test_path_resolver.py::TestSchemaDeclaresPipelineFiles::test_base_schema_has_pipeline_file_defs PASSED
eks/test/test_path_resolver.py::TestSchemaDeclaresPipelineFiles::test_setup_schema_has_pipeline_file_properties PASSED
9 passed in 3.39s
```

```
conda run -n eks python -m pytest eks/test/
252 passed, 8 warnings in 15.64s
```

### 20.4 Files Modified

| File | Change |
| :--- | :----- |
| `common/library/paths/resolver.py` | NEW: `resolve_paths()`, `ResolvedPaths` normalizing EKS + DCC path shapes |
| `common/library/paths/__init__.py` | Exports `resolve_paths`, `ResolvedPaths` |
| `eks/engine/core/config_registry.py` | 6 path properties routed through `resolve_paths()`; `workflow_files`/`tool_files` exposed |
| `eks/ui/backend/phase1_server.py` | 3 sites use `resolve_paths()` instead of inline path construction |
| `eks/engine/core/setup_validator.py` | `_validate_named_files()` validates `workflow_files`/`tool_files`; legacy result includes them |
| `eks/config/schemas/eks_base_schema.json` | v1.9.0: `workflow_file_entry_def`, `tool_file_entry_def` |
| `eks/config/schemas/eks_setup_schema.json` | v1.7.0: `workflow_files`, `tool_files` properties |
| `eks/config/schemas/eks_config.json` | v1.7.0: `workflow_files`, `tool_files` instance blocks |
| `common/universal_pipeline_architecture_design.md` | v1.7: L16 inventory/structure/detail, §3.18 pattern, §4.1/§4.2/§9/§10 |
| `eks/knowledge.json` | v2.6.0: L16 elevation, I089/I090 resolution |
| `eks/test/test_path_resolver.py` | NEW: 9 tests (EKS + DCC shape normalization, schema wiring, validator) |
| `eks/log/issue_log.md` | I089, I090 marked ✅ Resolved |
| `eks/log/update_log.md` | U135 added |
| `eks/workplan/phase_1_foundation_workplan.md` | §20 T1.98.1–8 → ✅, §20.3 success criteria, version → 3.47 |

---

## 21. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (T1.99.1–7 / I092 / R60)

### 21.1 Objective

Resolve I092 by converging EKS Phase 1 pipeline entry points (CLI, web, HTTP backend) on a single shared `run_pipeline(context)` funnel — mirroring DCC's CLI + UI + web → one `run_engine_pipeline(context)` — and satisfy R60 / AGENTS.md §18.13 (each phase runs as an independent sub-pipeline with its own `phase{N}_server.py`). Phase 1 already had `phase1_server.py`; it needed the convergence cleanup. Phases 2–5 need the full backend + runner (logged as T2.25–T2.26, T3.36–T3.37, T4.26–T4.27, T5.21–T5.22 — 🔷 PLANNED).

### 21.2 Implementation Summary

| ID | Deliverable | Evidence |
| :-- | :---------- | :------- |
| T1.99.1 | Shared `bootstrap_pipeline()` / `run_pipeline(context)` helper | `eks/engine/eks_engine_pipeline.py` (relocated from `eks/engine/core/pipeline_runner.py`, archived in T1.99.11): ConfigRegistry → SchemaLoader.load_all → DocumentRegistry → ErrorManager/MessageManager → ProjectSetupValidator readiness gate → PipelineOrchestrator.run_full_pipeline → checkpoint (`output/checkpoints/{job_id}.json`) + `on_phase` callback |
| T1.99.2 | Unified end-to-end CLI + `console_scripts` | `eks/engine/eks_engine_pipeline.py` (relocated from `parsers/cli.py`); `eks/pyproject.toml` `[project.scripts] eks-pipeline = "eks.engine.eks_engine_pipeline:main"` |
| T1.99.3 | Wire `phase1_server._run` to `run_pipeline()` | `eks/ui/backend/phase1_server.py` `_run` calls `run_pipeline(...)`; 409 concurrency guard + `resolve_paths()` preserved |
| T1.99.4 | Remove orphan `engine_endpoints.py` | Archived to `archive/ui/backend/engine_endpoints.py` (no references remained) |
| T1.99.5 | Add `eks/serve.py` (§18.12) | `eks/serve.py` canonical launcher; `server.py` retained as thin re-export shim (`from eks.serve import *`) |
| T1.99.6 | `ConfigRegistry` SSOT at entry | `bootstrap_pipeline()` loads `ConfigRegistry` singleton and passes it (not a raw dict) to `ProjectSetupValidator`; singleton reset when a different `config_dir` is requested |
| T1.99.7 | Tests | New `eks/test/test_pipeline_runner.py` (CLI smoke + `run_pipeline` exercised); full suite 257/257 green |

### 21.3 Test Phases, Steps & Results

| Step | Test | Result |
| :--- | :--- | :----- |
| 1 | `TestRunPipeline.test_run_pipeline_calls_orchestrator` — `run_pipeline` invokes `PipelineOrchestrator.run_full_pipeline` and returns `summary`/`em`/`mm` | ✅ PASS |
| 2 | `TestRunPipeline.test_bootstrap_pipeline_builds_context` — `bootstrap_pipeline` builds ConfigRegistry → SchemaLoader → DocumentRegistry and returns a context dict | ✅ PASS |
| 3 | `TestCli.test_cli_runs_end_to_end` — `eks-pipeline --data-dir <dir>` runs the full pipeline, prints summary, exits 0 | ✅ PASS (after `project_root` depth fix) |
| 4 | `TestCli.test_cli_debug_and_level_flags` — `--debug`/`--level` parsed | ✅ PASS |
| 5 | `test_phase1_server.py::test_pipeline_cancel` — DELETE cancels a running job; status stays `cancelled` | ✅ PASS (after cancellation bug fix) |
| 6 | Full EKS suite (`pytest eks/test/`) | ✅ 257 passed, stable across repeated runs |

### 21.4 Bugs Found & Fixed

1. **`project_root` depth bug (T1.99.2/T1.99.6)**: the unified entry (`eks/engine/eks_engine_pipeline.py`, replacing `parsers/cli.py`/`pipeline_runner.py`) computed `project_root` as `parent × 3`, but it lives three directories deep under `eks/` (`eks/engine/`), so `parent × 3` resolved to `eks/`, not the repo root. Default config dir was therefore wrong and the CLI could not load schemas. Fixed to `parent × 4`.
2. **Cancellation status bug (T1.99.3)**: when a pipeline was cancelled mid-run, `run_pipeline` raised `RuntimeError("Pipeline cancelled")` which `_run` caught and used to overwrite the `"cancelled"` status with `"failed"` (race vs the DELETE handler). `phase1_server._run` now detects the `cancelled` status and preserves `"cancelled"`, logging as STATUS rather than ERROR.

### 21.5 Files Created / Modified / Archived

- **Created**: `eks/engine/eks_engine_pipeline.py`, `eks/pyproject.toml`, `eks/serve.py`, `eks/test/test_eks_engine_pipeline.py`
- **Modified**: `eks/ui/backend/phase1_server.py`, `eks/server.py` (shim), `eks/engine/core/discovery_cli.py`, `eks/engine/core/health_cli.py`, `eks/test/test_discovery_cli.py`, `eks/test/test_health_cli.py`
- **Deleted**: `eks/engine/parsers/cli.py`
- **Archived**: `eks/engine/core/pipeline_runner.py` → `eks/archive/engine/core/pipeline_runner.py`; `ui/backend/engine_endpoints.py` → `archive/ui/backend/engine_endpoints.py`

### 21.6 Recommendations

- Implement Phases 2–5 standalone backends + runners (T2.25–T2.26, T3.36–T3.37, T4.26–T4.27, T5.21–T5.22) reusing `eks/engine/eks_engine_pipeline.py` so each phase ships a `phase{N}_server.py` + `run_phase{N}_pipeline(context)` and `serve.py` proxies `/api/v{N}/*` (I092/R60 remaining work).

### 21.7 Entry-Point Relocation (I096 / T1.99.8–12) — 2026-07-14

Relocated the unified `eks-pipeline` main entry to `eks/engine/eks_engine_pipeline.py` (DCC-faithful, `main()` + `--phase {A,B,C,full}`), built on shared `common.library` building blocks — `BaseEngine`/`BasePipelineContext`/`EngineInput`/`EngineOutput`/`TelemetryHeartbeat`, `get_system_param`, `resolve_paths`, `BaseMessageManager`, `UniversalLogger`, `ValidationManager` (advances I078). Deleted `eks/engine/parsers/cli.py`; archived `eks/engine/core/pipeline_runner.py`; repointed 7 import sites. Extended `PipelineOrchestrator.run_full_pipeline` with `on_phase`/`checkpoint_dir`/`job_id` (single coordination loop). Also fixed a pre-existing over-indentation defect in `test_discovery_cli.py`/`test_health_cli.py`. Full EKS suite **264/264 green**. I096 → Resolved. U148.

| ID | Deliverable | Evidence |
| :-- | :---------- | :------- |
| T1.99.8 | Relocate main CLI entry to `eks/engine/eks_engine_pipeline.py` (reuse common.library) | `eks/engine/eks_engine_pipeline.py`; `pyproject.toml` `eks-pipeline = "eks.engine.eks_engine_pipeline:main"`; `parsers/cli.py` deleted |
| T1.99.9 | DCC-style `main()` + `--phase {A,B,C,full}` | `main()` sequence + per-phase selection (Appendix F §2.3.3/§2.3.5, R60) |
| T1.99.10 | Extend `run_full_pipeline` coordination loop | `on_phase`/`checkpoint_dir`/`job_id` params; `run_pipeline` delegates to `PipelineOrchestrator.run_full_pipeline` |
| T1.99.11 | Consolidate `pipeline_runner.py` + repoint imports | `pipeline_runner.py` archived → `eks/archive/engine/core/`; 7 sites repointed |
| T1.99.12 | Docs updated | §9 Mermaid/files, §30 tasks ✅, this report, appendix_f §2.3.3, common §8.2 |

---

## 22. References

1. [Phase 1 Foundation Workplan](../phase_1_foundation_workplan.md) — WP-EKS-P1-001 v3.47
2. [Phase 1.3 Initiation Harmonization Workplan (archived)](../../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
3. [Phase 1 T1.79–T1.83 Report (archived)](../../archive/phase_1_t179_t183_report.md) — RP-EKS-P1-T179-001 (detailed test cases integrated into §15.3)
4. [EKS Master Workplan](../eks_system_workplan.md) — WP-EKS-001 v1.5
5. [AGENTS.md](../../AGENTS.md) — Repository guidelines
6. [Issue Log](../../log/issue_log.md)
7. [Update Log](../../log/update_log.md)
8. [Test File — Phase 1](../../test/test_phase1.py)
9. [Test File — T1.32 Modules](../../test/test_t132_modules.py)
10. [Test File — Setup Validator](../../test/test_setup_validator.py)
11. [Test File — Validation Manager](../../test/test_validation_manager.py)
12. [Appendix A — Asset Schema](../appendix_a_asset_schema.md)
13. [Appendix B — Document Registry](../appendix_b_document_registry.md)
14. [Appendix C — Ontology](../appendix_c_ontology.md)
15. [Appendix D — Pipeline Messages & Errors](../appendix_d_pipeline_messages_errors.md)
16. [Appendix E — Schema Design](../appendix_e_schema_design.md)
17. [Appendix F — Pipeline Architecture Design](../appendix_f_pipeline_architecture_design.md)
