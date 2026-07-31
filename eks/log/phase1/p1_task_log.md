# Phase 1 Task Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/phase1/p1_task_log.md`  
**Last Updated**: 2026-07-31 (T1.197 ✅ — I265 complete; T1.200–T1.202 🔷 Planned added for I274 Option A — COLUMN_ALLOWLIST SSOT, awaiting approval; empty file_type fix done via I273)

## Legend

### Task Status

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| ✅ | Complete | Task fully implemented and verified |
| ⏳ | In Progress | Task currently being implemented |
| 🔷 | Planned | Task defined but not yet implemented |
| ⛔ | Won't Implement | Explicitly rejected or out of scope |

### Column Format

All tables use the standard 12-column enriched format:

`ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section`

---

## Status Summary

| Status | Marker | Count |
| :----- | :----: | ----: |
| Complete | ✅ | 365 |
| In Progress | ⏳ | 0 |
| Planned | 🔷 | 30 |
| Won't Implement | ⛔ | 3 |
| Open | 🔴 | 1 |
| **Total** | | **399** |

---

## 2. Foundation, Environment & Compliance (R99) Tasks

> Source: [§14](phase_1_foundation_workplan.md#14)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.1 | [Init] Create EKS folder structure | archive, config, data, output, engine, log, docs, workplan, test, ui | R99 | ✅ COMPLETE | — | — | folders | — | — | — | §14 |
| T1.2 | [Init] Create environment file `eks.yml` | Conda environment with all Phase 1–5 dependencies | R99 | ✅ COMPLETE | — | — | `eks/eks.yml` | — | — | — | §14 |
| T1.14 | [Code] Implement SSOT config registry | Global parameter access via schema-driven config; no hardcoding | R06, R35 | ✅ COMPLETE | — | — | `config_registry.py` | — | — | — | §14 |
| T1.15 | [Testing] Write unit tests | Schema loader, document registry, revision management, parsers, logger | R99 | ✅ COMPLETE | — | — | `test/` | — | — | — | §14 |
| T1.16 | [Docs] Create log files | `update_log.md`, `issue_log.md` under `eks/log/` | R99 | ✅ COMPLETE | — | — | `log/update_log.md`, `log/issue_log.md` | — | — | — | §14 |
| T1.33 | [Schema] Migrate EKS schemas to config/schemas/ | Move core/asset/ontology config & schema files to `eks/config/schemas/`; update SchemaLoader, ErrorManager, MessageManager, tests, and documentation | R06, R99 | ✅ COMPLETE | — | — | `config/schemas/`, `schema_loader.py` | — | — | — | §14 |
| T1.48 | [Schema] Schema audit — duplicates, inconsistencies, missing validations | Remove duplicate `revision_id` and `discipline_code`; Align parser import paths; Add dgn/dwg stub parsers; Log all issues (I022–I028). All 114 tests pass. | R06, R99 | ✅ COMPLETE | I022, I023, I024, I025, I026, I027, I028 | — | `eks_doc_base_schema.json`, `eks_config.json` | — | — | — | §14 |
| T1.49 | [Docs] Cross-cutting workplan remediation | Fix `agent_rule.md` references → `AGENTS.md`; convert Linux absolute paths to relative; update stale statuses; reorder §10/§25; fill Phase 3 placeholders; add reranker criteria. | R99 | ✅ COMPLETE | — | — | `phase_1_foundation_workplan.md` | — | — | — | §14 |
| T1.52 | [Code] Implement EKSPipelineContext | Create `eks/engine/core/context.py` with nested dataclasses for centralized state management per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/context.py` | — | — | — | §14 |
| T1.53 | [Code] Implement BaseEngine abstract class | Create `eks/engine/core/base.py` with standard execution flow (validate → execute → validate) per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/base.py` | — | — | — | §14 |
| T1.55 | [Code] Implement Multi-Stage Validation | Create `eks/engine/core/validator.py` with setup, schema, data, parser validation stages per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/validator.py` | — | — | — | §14 |
| T1.56 | [Code] Implement CLI Entry Points | Discovery CLI and Health CLI both call real engines via `bootstrap_pipeline()` funnel. I093 resolved. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py`, `engine/core/health_cli.py` | — | — | — | §14 |
| T1.56.1 | [Code] Wire Discovery CLI to real engine (I093) | `discovery_cli.py` → `PipelineOrchestrator.run_phase_a()`; real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py` | ← T1.56 | — | — | §14 |
| T1.56.2 | [Code] Wire Health Scorer CLI to real engine (I093) | `health_cli.py` → `HealthScorer.score()`/`score_batch()`; real scores/status. | R99 | ✅ COMPLETE | I093 | — | `engine/core/health_cli.py` | ← T1.56 | — | — | §14 |
| T1.56.3 | [Testing] Add pytest for discovery_cli (I093) | Happy path + failure/edge case; assert real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `test/` | ← T1.56.1 | — | — | §14 |
| T1.56.4 | [Testing] Add pytest for health_cli (I093) | Single + batch scoring + threshold boundary. | R99 | ✅ COMPLETE | I093 | — | `test/` | ← T1.56.2 | — | — | §14 |
| T1.56.5 | [Docs] Close I093 records & reclassify T1.56 | Mark I093 resolved; flip T1.56 status. | R99 | ✅ COMPLETE | I093 | — | `update_log.md`, `issue_log.md` | ← T1.56.3–4 | — | — | §14 |
| T1.57 | [Code] Implement HTTP API Endpoints | Delivered as `eks/ui/backend/phase1_server.py` (standalone `--port 5001`). | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — | — | §14 |
| T1.65 | [Code] Implement Project Setup Validator | Create `eks/engine/core/setup_validator.py` with auto-creation of missing folders per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/setup_validator.py` | ← T1.66 | — | — | §14 |
| T1.66 | [Schema] Create Project Setup Schema | Create `eks/config/schemas/project_setup.json` for setup validation per Appendix F | R99 | ✅ COMPLETE | — | — | `config/schemas/project_setup.json` | — | — | — | §14 |
| T1.67 | [Schema] Integrate project_setup into core 3-layer schemas (I046) | Refactor content into `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`. Delete orphan `project_setup.json`. Resolves I046. | R99 | ✅ COMPLETE | I046 | — | `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`, `setup_validator.py` | ← T1.66 | — | — | §14 |
| T1.70 | [Code] Add data_dir traversal guard to phase1_server.py | Resolve `data_dir` against `PRJ_DIR`, check `is_relative_to(PRJ_DIR)` — return HTTP 403 if outside project root. | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — | — | §14 |
| T1.74 | [Code] Cross-platform path compatibility | Fix 4 cross-platform gaps in `phase1_server.py`, `context.py`. Resolves I078–I081. | R99 | ✅ COMPLETE | I078, I079, I080, I081 | — | `phase1_server.py`, `engine/core/context.py` | ← T1.69, T1.70 | — | — | §14 |

---

## 3. Architectural Patterns — Context, Factories & Orchestration Hardening (Appendix F) Tasks

> Source: [§15](phase_1_foundation_workplan.md#15)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.54 | [Code] Implement TelemetryHeartbeat | Create `eks/engine/core/telemetry.py` for document processing checkpoints per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/telemetry.py` | — | — | — | §15 |
| T1.58 | [Code] Implement Checkpoint State Serialization | Add checkpoint state serialization/deserialization for resume capability per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/context.py` | — | — | — | §15 |
| T1.59 | [Code] Implement ParserFactory | Create `eks/engine/core/factories.py` with file type routing per Appendix F | R26 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
| T1.60 | [Code] Implement HealthScorerFactory | Factory with config-driven dimensions per Appendix F | R51 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
| T1.61 | [Code] Implement StructureDetectorFactory | Factory for structure detector instantiation per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/factories.py` | — | — | — | §15 |
| T1.62 | [Code] Update Engines to Use Factories | Refactor existing engines to use factories instead of direct instantiation per Appendix F | R26 | ✅ COMPLETE | — | — | `engine/` | ← T1.59–61 | — | — | §15 |
| T1.63 | [Code] Enhance PipelineOrchestrator with Checkpoints | Add 5 clear phases (A-E) with telemetry heartbeat integration per Appendix F | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | — | — | — | §15 |
| T1.64 | [Code] Implement Phase Rollback Capability | Add checkpoint restoration mechanism for failed phases per Appendix F | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.63 | — | — | §15 |
| T1.182.1 | [Code] Remove duplicate Factory base class from EKS factories.py | Remove lines 22-41 (duplicate Factory class); add import from common.library.utility.factories.base_factory | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | — | TL010 | U203 | §15 |
| T1.182.2 | [Code] Refactor ParserFactory to inherit from common.Factory | Ensure ParserFactory inherits from common.Factory; replace manual _load_class() with self._load_class(); verify _get_config() uses common version | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
| T1.182.3 | [Code] Refactor HealthScorerFactory to inherit from common.Factory | Ensure HealthScorerFactory inherits from common.Factory; replace manual import with self._load_class() if applicable; verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
| T1.182.4 | [Code] Refactor StructureDetectorFactory to inherit from common.Factory | Ensure StructureDetectorFactory inherits from common.Factory; replace manual _load_class() logic (lines 205-208) with self._load_class(); verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
| T1.182.5 | [Code] Refactor EngineFactory to inherit from common.Factory | Ensure EngineFactory inherits from common.Factory; replace manual _load_class() logic (lines 272-275) with self._load_class(); verify config access uses common._get_config() | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1 | TL010 | U203 | §15 |
| T1.182.6 | [Docs] Update factories.py revision metadata | Update revision header in factories.py to document SSOT compliance fix; reference I211 and T1.99.182 | R99 | ✅ COMPLETE | I211 | TL010 | `engine/core/factories.py` | ← T1.182.1–5 | TL010 | U203 | §15 |
| T1.182.7 | [Testing] Run EKS test suite for factory SSOT compliance | Run EKS test suite to verify no breaking changes; focus on tests that use factories; verify dynamic class loading still works | R99 | ✅ COMPLETE | I211 | TL010 | `test/` | ← T1.182.1–5 | TL010 | U203 | §15 |
| T1.182.8 | [Docs] Update I211 status in p1_issue_log.md | Update I211 resolution note to reflect completion; change status from "Deferred for further study" to "Resolved"; update last updated version | R99 | ✅ COMPLETE | I211 | TL010 | `log/phase1/p1_issue_log.md` | ← T1.182.1–7 | TL010 | U203 | §15 |

---

## 4. Core Schema Suite (base/setup/config + fragment schemas) Tasks

> Source: [§16](phase_1_foundation_workplan.md#16)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.3 | [Schema] Design canonical schema — base | File: `eks_base_schema.json`. Layer: Definitions ($defs). 13 asset schema fragments + conditional_fragments for zero-code extensibility. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_base_schema.json` | — | — | — | §16 |
| T1.4 | [Schema] Design canonical schema — setup | File: `eks_setup_schema.json`. Layer: Declarations (properties). One-to-one match with base via $ref. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_setup_schema.json` | ← T1.3 | — | — | §16 |
| T1.5 | [Schema] Design canonical schema — config | File: `eks_config.json`. Layer: Config values. Validates strictly against setup schema. | R06, R07, R08, R09 | ✅ COMPLETE | — | U006 | `eks_config.json` | ← T1.4 | — | — | §16 |
| T1.6 | [Code] Implement schema loader | Load and resolve base/setup/config with $ref support (reuse DCC pattern) | R06 | ✅ COMPLETE | — | U008 | `schema_loader.py` | ← T1.5 | — | — | §16 |
| T1.42 | [Schema] Project code fragment schema | Create `eks_project_code_schema.json` with valid codes (131101, 131242, 999999). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_project_code_schema.json` | — | — | — | §16 |
| T1.43 | [Schema] Discipline fragment schema | Create `eks_discipline_schema.json` with 21 discipline codes (PI, EL, IN, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_discipline_schema.json` | — | — | — | §16 |
| T1.44 | [Schema] Department fragment schema | Create `eks_department_schema.json` with 11 department codes (PRJ, QAQC, CNT, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_department_schema.json` | — | — | — | §16 |
| T1.45 | [Schema] Facility fragment schema | Create `eks_facility_schema.json` with 12 facility prefixes (WSD11, WSW41, ...). DCC fragment pattern. | R06 | ✅ COMPLETE | — | — | `eks_facility_schema.json` | — | — | — | §16 |
| T1.46 | [Schema] Update base/config/setup for fragment integration | Add defs to base; replace P123/P456 with real WSD11 codes in config; add $ref to fragments. Resolve I005. | R06 | ✅ COMPLETE | I005 | — | `eks_base_schema.json`, `eks_config.json`, `eks_setup_schema.json` | ← T1.42–45 | — | — | §16 |
| T1.47 | [Testing] Add fragment schema validation tests | 6 new tests: fragment existence, base defs, required fields, no placeholders, config $ref, setup properties. | R06 | ✅ COMPLETE | — | — | `test/` | ← T1.46 | — | — | §16 |
| T1.50 | [Schema] Base schema SSOT enforcement | Strip trigger map to shape-only (I031); move revision_id to doc base (I032); update ConfigRegistry; update schema_inheritance_chain.md. 114/114 tests pass. | R06, R35 | ✅ COMPLETE | I031, I032 | — | `eks_base_schema.json`, `eks_doc_base_schema.json`, `ConfigRegistry` | — | — | — | §16 |
| T1.51 | [Schema] Asset Context Fragment — hierarchy + relationships | Extensible location/system hierarchy + asset/document relationships + lifecycle context for all 14 AT_ types. Version bumps: base 1.3.0, setup 1.3.0, config 1.4.0. | R36 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` | — | — | — | §16 |

---

## 5. Asset Schema — Universal Plant Item (R36/R39) Tasks

> Source: [§17](phase_1_foundation_workplan.md#17)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.17 | [Schema] Design asset schema — fragment definitions | Add 13 reusable asset fragments to `eks_asset_base_schema.json` (item_core, process_conditions, manufacturer, ...) | R36 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json` | — | — | — | §17 |
| T1.18 | [Schema] Design asset schema — type registry | Add `asset_type_registry` to setup schema; map all 14 AT_ categories to fragment compositions in config | R36 | ✅ COMPLETE | — | — | `eks_setup_schema.json`, `eks_config.json` | — | — | — | §17 |
| T1.19 | [Config] Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | R36 | ✅ COMPLETE | — | — | `eks_config.json` | — | — | — | §17 |
| T1.20 | [Schema] Update asset schema files for R39 + gap analysis | Add specialist_equipment/motor_control fragments; expand actuator/rotating/instrumentation/valve with gap fields; update fragment enum to 13; add conditional_fragments entries | R36, R39 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_setup_schema.json`, `eks_asset_config.json` | — | — | — | §17 |

---
## 6. Ontology Integration (R44, ISO 15926) Tasks

> Source: [§18](phase_1_foundation_workplan.md#18)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.23 | [Schema] Design ontology schema | Validate classes, properties, and relationship types; SHACL constraint definitions for data quality rules | R44 | ✅ COMPLETE | — | — | `eks_ontology_schema.json` | — | — | — | §18 |
| T1.24 | [Config] Create ontology config | Define classes, inheritance, and relationship properties (ISO 15926 aligned) | R44 | ✅ COMPLETE | — | — | `eks_ontology_config.json` | — | — | — | §18 |
| T1.25 | [Code] Extend schema loader | Update `schema_loader.py` to validate and load the ontology registry dynamically at startup | R44 | ✅ COMPLETE | — | — | `schema_loader.py` | — | — | — | §18 |
| T1.26 | [Testing] Write ontology unit tests | Test ontology schema validation and loading in `test_phase1.py` | R44 | ✅ COMPLETE | — | — | `test/` | — | — | — | §18 |
| T1.27 | [Docs] Plan alias-aware ontology mapping | Define alias support and `ontology_class_map` design; document AT_ code-to-ontology mapping; hold schema/code updates pending approval | R44 | ✅ COMPLETE | — | — | `eks_asset_config.json` | — | — | — | §18 |
| T1.28 | [Schema] Embedded Relationship Metadata | Update base schema with relationship-triggering fields; update config with relationship_triggers mapping to graph edges | R44 | ✅ COMPLETE | — | — | `eks_asset_base_schema.json`, `eks_asset_config.json` | — | — | — | §18 |
| T1.29 | [Schema] Document Ontology & Mapping Metadata | Update ontology config with Document hierarchy + lifecycle relationships; update asset config with document_triggers | R44 | ✅ COMPLETE | — | — | `eks_ontology_config.json`, `eks_asset_config.json` | — | — | — | §18 |

---

## 7. Logging, Errors & Health Scoring (R33/R34/R51) Tasks

> Source: [§19](phase_1_foundation_workplan.md#19)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.13 | [Code] Implement tiered logger | logger.py: levels 0–3, debug object, trace table, depth counter | R33, R34 | ✅ COMPLETE | — | — | `logger.py` | — | — | — | §19 |
| T1.30 | [Schema] Error Code Taxonomy Schema | Create error code base + config schemas with full system/data error catalog. Follow DCC pattern. | R51 | ✅ COMPLETE | — | — | `eks_error_code_base.json`, `eks_error_config.json` | — | — | — | §19 |
| T1.31 | [Schema] Pipeline Message Catalog Schema | Create message base + config schemas with milestone/status/progress/warning templates. Follow DCC pattern. | R51 | ✅ COMPLETE | — | — | `eks_message_base.json`, `eks_message_config.json` | — | — | — | §19 |
| T1.32 | [Code] Error & Message Manager Modules | Create error_manager.py, message_manager.py, health_scorer.py (6-dimension), structure_detector.py. Add document_elements table. | R51 | ✅ COMPLETE | — | — | `error_manager.py`, `message_manager.py`, `health_scorer.py`, `structure_detector.py` | — | — | — | §19 |
| T1.41 | [Schema] Fix error/message schemas 3-layer pattern | Create error/message setup schemas (allOf + $ref); clean config files; update SchemaLoader. Resolve I014. | R51 | ✅ COMPLETE | I014 | — | `eks_error_setup_schema.json`, `eks_message_setup_schema.json` | — | — | — | §19 |
| T1.68 | [Code] Wire ErrorManager/MessageManager into pipeline orchestrator | Emit D4/D5 error codes on phase failures; call MessageManager.format() for D6 milestone messages | R51 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.70, T1.72 | — | — | §19 |
| T1.69 | [Code] Add run_id correlation ID to EKSLogger and _LogCapture | Prepend [run_id] to all log entries; pass job_id as run_id from phase1_server | R33, R51 | ✅ COMPLETE | — | — | `logger.py`, `phase1_server.py` | ← T1.76 | — | — | §19 |
| T1.71 | [Code] Replace raw duckdb.connect in _update_doc_status | Route through registry.update_document_status() with _with_retry() wrapper | R02 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | ← T1.68 | — | — | §19 |
| T1.75 | [Code] Activate ErrorManager/MessageManager in phase1_server | Construct and pass managers to PipelineOrchestrator (closes silent T1.68 gap) | R51, R99 | ✅ COMPLETE | — | — | `phase1_server.py` | ← T1.68, T1.76 | — | — | §19 |
| T1.76 | [Code] Persist debug/message/status JSON to eks/output | Generate debug_log.json, pipeline_status, pipeline_messages artifacts per AGENTS.md §7/§19 | R51, R99 | ✅ COMPLETE | — | — | `eks/output/` | ← T1.69, T1.75 | — | — | §19 |
| T1.99.35 | [Code] Harden universal BaseMessageManager as SSOT (I105) | Add optional icon support, print() fallback, verbosity clamp, _make_default_logger() hook. 10 new common tests pass. | R51, R99 | ✅ COMPLETE | I078, I105 | — | `common/library/core/messages/message_manager.py` | — | — | — | §19 |
| T1.99.36 | [Code] Make EKS MessageManager thin subclass (I105) | EKS MessageManager extends BaseMessageManager with _catalog_filename. Remove duplicated logic. All 7 EKS tests green. | R51, R99 | ✅ COMPLETE | I105 | — | `engine/core/message_manager.py` | ← T1.99.35 | — | — | §19 |
| T1.99.37 | [Fix] Fix eks_engine_pipeline.py:505 to use EKS subclass (I105) | Change BaseMessageManager → MessageManager. Fixes silent wrong-catalog bug. | R51, R99 | ✅ COMPLETE | I105 | — | `eks_engine_pipeline.py` | ← T1.99.36 | — | — | §19 |
| T1.99.38 | [Testing] Tests for universal message + EKS regression (I105) | Common BaseMessageManager subclass test + EKS suite green. 10+7 gap tests; 278/278 green. | R51, R99 | ✅ COMPLETE | — | — | `common/library/core/messages/tests/`, `test/` | ← T1.99.35–36 | — | — | §19 |
| T1.99.39 | [Docs] Knowledge base + logs update (I105) | Update knowledge.json, update_log.md (v3.74 recorded) | R51, R99 | ✅ COMPLETE | I105 | — | `knowledge.json`, `update_log.md` | ← T1.99.35–38 | — | — | §19 |
| T1.99.40 | [Code] Make EKSPipelineContext extend BasePipelineContext (L06) | Change class to extend common BasePipelineContext; add _from_dict() / _to_dict() | R99 | ✅ COMPLETE | I106 | — | `engine/core/context.py` | — | — | — | §19 |
| T1.99.41 | [Code] Populate context fields from EngineInput+bootstrap (I106) | initialize_context() accepts parameters, config_registry, schema_registry, checkpoint_state | R99 | ✅ COMPLETE | I106 | — | `pipeline_orchestrator.py` | ← T1.99.40 | — | — | §19 |
| T1.99.42 | [Code] Surface EKSPipelineContext through run_pipeline() (I106) | Accept optional context param; include context in return dict. Backward compat preserved. | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | ← T1.99.40–41 | — | — | §19 |
| T1.99.43 | [Code] main() builds + seeds EKSPipelineContext (I106) | Construct ctx from EngineInput; pass to run_pipeline(); extract EngineOutput from returned context | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | ← T1.99.42 | — | — | §19 |
| T1.99.44 | [Testing] Tests + knowledge base + logs for context threading (I106) | Integration test test_run_pipeline_surfaces_context(); update knowledge.json (U163), issue_log.md | R99 | ✅ COMPLETE | I106 | U163 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | ← T1.99.40–43 | — | — | §19 |
| T1.99.45 | [Code] Fold OS detection + params into bootstrap_pipeline() (I107) | Move detect_os(), CLI parse, log-level, eks_root into bootstrap_pipeline() | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | — | — | §19 |
| T1.99.46 | [Code] Fold CLI parse + data_dir precedence (I107) | Internal parse_eks_cli(); CLI>Schema>Native data_dir resolution | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.45 | — | — | §19 |
| T1.99.47 | [Fix] Single path resolution source (I107 Defect A) | One resolved_paths dict; main() + EKSPipelineContext.paths both read from it | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.45–46 | — | — | §19 |
| T1.99.48 | [Fix] Single MessageManager instance (I107 Defect B) | mm created once in bootstrap; main() reuses boot["mm"] | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | ← T1.99.47 | — | — | §19 |
| T1.99.49 | [Testing] Tests + knowledge base for bootstrap completeness (I107) | 4 integration tests (TestI107BootstrapCompleteness). 23/23 pass. knowledge.json v2.7.0, update_log U165. | R99 | ✅ COMPLETE | I107 | U165 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | ← T1.99.45–48 | — | — | §19 |

---

## 8. Document Registry & Revision Management (R02/R21/R22/R29) Tasks

> Source: [§20](phase_1_foundation_workplan.md#20)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.7 | [Code] Implement document registry | CRUD interface for document metadata backed by DuckDB/PostgreSQL | R02, R29 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |
| T1.8 | [Code] Implement revision management | Preserve all revisions; is_latest flag; revision chain lookup | R21, R22 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |
| T1.21 | [Code] Document Registry Remediation (G1-G3) | Add source_type column; column allowlist for list_documents; SQL ORDER BY for revision history | R02 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |
| T1.22 | [Code] Extended Document Metadata | Implement 11 new fields (Accountability, Quality, Technical); asset_tags JSON array; ALTER TABLE migration logic | R02 | ✅ COMPLETE | — | — | `registry.py` | — | — | — | §20 |

---

## 9. Document Parsers — PDF/DOCX/XLSX (R01/R26) Tasks

> Source: [§21](phase_1_foundation_workplan.md#21)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.9 | [Code] Implement abstract base parser | base_parser.py: plug-in interface with parse(), extract_metadata() | R01, R26 | ✅ COMPLETE | — | — | `base_parser.py` | — | — | — | §21 |
| T1.10 | [Code] Implement PDF parser | pdf_parser.py: extract text, metadata, page numbers | R01, R26 | ✅ COMPLETE | — | — | `pdf_parser.py` | — | — | — | §21 |
| T1.11 | [Code] Implement XLSX parser | xlsx_parser.py: extract sheet data, metadata | R01, R26 | ✅ COMPLETE | — | — | `xlsx_parser.py` | — | — | — | §21 |
| T1.12 | [Code] Implement DOCX parser | docx_parser.py: extract text, metadata, sections | R01, R26 | ✅ COMPLETE | — | — | `docx_parser.py` | — | — | — | §21 |

---

## 10. Document Schema v2 — 3-Layer Reorganization (R52/R53) Tasks

> Source: [§22](phase_1_foundation_workplan.md#22)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.34 | [Schema] Reorganize document schema (3-layer) | Create eks_doc_base/setup/config 3-layer; move doc defs from eks_base; add document_element_def (7 cols); update schema_loader; add 6 tests | R52 | ✅ COMPLETE | — | — | `eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json` | — | — | — | §22 |
| T1.35.1 | [Schema] Enhance doc base schema — enums & missing fields | Add doc_id_format, document_type_code (7), file_type_code (5), element_type_code (8); add file_path/ingested_at/file_type | R53 | ✅ COMPLETE | — | — | `eks_doc_base_schema.json` | — | — | — | §22 |
| T1.35.2 | [Schema] Enhance doc setup schema — registries | Add document/file/element type registry property declarations; update element_expectations key schema | R53 | ✅ COMPLETE | — | — | `eks_doc_setup_schema.json` | — | — | — | §22 |
| T1.35.3 | [Config] Enhance doc config — registry values | Populate 3 registries with 7/5/8 entries; refactor element_expectations keys from A-E → document type codes | R53 | ✅ COMPLETE | — | — | `eks_doc_config.json` | — | — | — | §22 |
| T1.35.4 | [Code] Update schema loader — validate new registries | Add _validate_doc_registries() for enum checks, registry completeness, parser class references | R53 | ✅ COMPLETE | — | — | `schema_loader.py` | — | — | — | §22 |
| T1.35.5 | [Testing] Update tests — new validation tests | 6 tests: doc_type_enum, doc_type_registry, file_type_registry, element_type_registry, expectations_keys, metadata_fields | R53 | ✅ COMPLETE | — | — | `test/` | — | — | — | §22 |
| T1.35.6 | [Docs] Update appendix B — document registry schema | Add B3.2/B3.3/B3.4 registry sections; update B3 schema table with file_type column; bump v0.9 | R53 | ✅ COMPLETE | — | — | `appendix_b_document_registry.md` | — | — | — | §22 |

---

## 11. Pipeline Orchestration (R54–R58/R57) Tasks

> Source: [§23](phase_1_foundation_workplan.md#23)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.36 | [Code] Auto-DDL from schema | Create schema_to_ddl.py; read schema defs, generate CREATE/ALTER TABLE SQL; refactor registry.py; add sync_schema() | R54 | ✅ COMPLETE | — | — | `schema_to_ddl.py`, `registry.py` | — | — | — | §23 |
| T1.37 | [Code] File scanner | Walk directory; match files to file_type_registry; validate against expected_file_types; register placeholder rows | R55 | ✅ COMPLETE | — | — | `file_scanner.py` | — | — | — | §23 |
| T1.38 | [Code] Parser router | Map file_type → parser_class; instantiate parser; call parse() + extract_metadata() + StructureDetector.detect() | R56 | ✅ COMPLETE | — | — | `parser_router.py` | — | — | — | §23 |
| T1.39 | [Code] Pipeline orchestrator | Coordinate Phase A (scan→register), Phase B (route→parse→detect→score→update), Phase C (flag for review) | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | — | — | — | §23 |
| T1.40 | [Code] Manual review workflow | Query flagged docs; support correction, confirmation, score recalculation, document lock | R58 | ✅ COMPLETE | — | — | `review_manager.py` | — | — | — | §23 |
| T1.72 | [Code] Enforce DiscoveryInput/Output + ParserInput/Output contracts | Wrap run_phase_a() and _process_file() with input/output contracts from base.py | R57 | ✅ COMPLETE | — | — | `pipeline_orchestrator.py` | — | — | — | §23 |
| T1.73 | [Code] Persist checkpoint JSON to disk in _run() | After each _set_phase(), save checkpoint to output/checkpoint_{job_id}.json; support resume | R57 | ✅ COMPLETE | — | — | `phase1_server.py` | — | — | — | §23 |

---

## 12. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89) Tasks

> Source: [§24](phase_1_foundation_workplan.md#24)

### Initiation Integrity (T1.77–T1.78)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.77 | [Code] Wire ProjectSetupValidator into fail-fast gate | validate_all() + get_readiness_status() wired into phase1_server._run(); --debug/--level CLI; data_dir existence checked. 8+3 tests, 202/202 pass. | R99 | ✅ COMPLETE | — | U122 | `phase1_server.py`, `setup_validator.py`, `test/test_setup_validator.py` | ← T1.65 | — | — | §24 |
| T1.78 | [Code] DCC gap remediation (eks.yml path, input readability, dep probe) | Fix eks.yml path, input readability (G2), dep probe (G3/G4), --skip-readiness (G5), error code constants (G7); fix _LogCapture.level bug. 207/207 pass. | R99 | ✅ COMPLETE | I079 | U124 | `phase1_server.py`, `setup_validator.py`, `eks.yml` | ← T1.77 | — | — | §24 |

### Initiation Schema-Driven Hardening (T1.79–T1.83)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.79 | [Code] Wire P1-SETUP-* error codes into validate_all() | Raise readiness failure via ErrorManager.handle_system_error("P1-SETUP-READINESS") | R99 | ✅ COMPLETE | I079 | — | `setup_validator.py`, `error_manager.py` | — | — | — | §24 |
| T1.80 | [Code] Derive output/eks.yml paths from global_paths | Schema-driven paths replacing hardcoded literals | R99 | ✅ COMPLETE | I080 | — | `setup_validator.py`, `phase1_server.py` | — | — | — | §24 |
| T1.81 | [Code] Remove hardcoded fallback lists (SSOT) | Remove 4 hardcoded fallback lists duplicating eks_config.json | R99 | ✅ COMPLETE | I081 | — | `setup_validator.py` | — | — | — | §24 |
| T1.82 | [Code] Honor validation_options.auto_create_folders | Schema-driven input defaults; honor auto_create from config | R99 | ✅ COMPLETE | I082, I083 | — | `setup_validator.py`, `eks_config.json` | — | — | — | §24 |
| T1.83 | [Code] Make eks package root schema-driven | Replace 10× PRJ_DIR/"eks" literals with global_paths.eks_root | R99 | ✅ COMPLETE | I084 | — | `phase1_server.py`, `context.py` | — | — | — | §24 |

---

## 13. Initiation Schema & Validation Harmonization (T1.84–T1.89) Tasks

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.84 | [Code] Universal ValidationManager | Create common/library/utility/validation/manager.py — validate_folders, validate_named_files, validate_environment, validate_dependencies, validate_discovery_rules, validate_project_setup | R99 | ✅ COMPLETE | I085 | — | `common/library/utility/validation/manager.py` | — | — | — | §25 |
| T1.85 | [Schema] EKS schema reshape | Replace flat-array defs with DCC-aligned object defs (8 new defs) in eks_base_schema.json v1.7.0 + eks_setup_schema.json v1.4.0 | R06 | ✅ COMPLETE | I085 | — | `eks_base_schema.json`, `eks_setup_schema.json` | ← T1.84, T1.67 | — | U130 | §25 |
| T1.86 | [Schema] Extract project_setup config | Create eks_project_setup_config.json v1.0.0; eks_config.json v1.5.0 references it | R06 | ✅ COMPLETE | I085 | — | `eks_project_setup_config.json`, `eks_config.json` | ← T1.85, T1.67 | — | U130 | §25 |
| T1.87 | [Code] EKS validator adapter | setup_validator.py v0.7 thin adapter delegating to universal module; preserves P1-SETUP-* + ErrorManager wiring | R99 | ✅ COMPLETE | I085 | — | `setup_validator.py` | ← T1.84, T1.86 | — | U130 | §25 |
| T1.88 | [Testing] Test migration + coverage | test_setup_validator.py (19 tests) + test_validation_manager.py (20 tests); full suite 235/235 green | R99 | ✅ COMPLETE | I085 | — | `test/test_setup_validator.py`, `test/test_validation_manager.py` | ← T1.87 | — | U130 | §25 |
| T1.89 | [Docs] Workplan/log/knowledge update | knowledge.json v2.3.0, update_log U130, issue_log I085 resolved | R99 | ✅ COMPLETE | I085 | U130 | `knowledge.json`, `update_log.md`, `issue_log.md` | ← T1.84–88 | — | U130 | §25 |

---

## 14. Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95) Tasks

### 14.1 Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.90 | [Schema/Config] Flatten project_setup in eks_config.json | Move 7 setup keys to top level; remove project_setup wrapper | R99 | ✅ COMPLETE | — | — | `eks_config.json` | ← T1.67, T1.85, T1.86 | — | — | §26 |
| T1.91 | [Schema] Update eks_setup_schema.json | Remove wrapper property; declare 7 keys top-level; bump v1.5.0 | R06, R35 | ✅ COMPLETE | — | — | `eks_setup_schema.json` | ← T1.90 | — | — | §26 |
| T1.92 | [Code] Update setup_validator.py adapter | Read from top-level config with backward-compat fallback; keep P1-SETUP-* codes | R99 | ✅ COMPLETE | — | — | `setup_validator.py` | ← T1.91 | — | — | §26 |
| T1.93 | [Code] Update phase1_server.py call site | _cfg.get("project_setup", _cfg) flatten-aware | R99 | ✅ COMPLETE | — | — | `phase1_server.py` | ← T1.92 | — | — | §26 |
| T1.94 | [Cleanup] Delete orphan eks_project_setup_config.json | Archive per AGENTS.md §5.3 | R99 | ✅ COMPLETE | — | — | `eks_project_setup_config.json` | ← T1.86 | — | — | §26 |
| T1.95 | [Testing] Tests + suite green | Update test assertion; full suite 236/236 | R99 | ✅ COMPLETE | — | — | `test/` | ← T1.92–94 | — | — | §26 |

---

## 15. Schema Discovery & Registration — Discovery-Driven Loading (T1.96) Tasks

### 15.1 Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.96.1 | [Code] Extract discover_schema_files() to common/ | Extract core discovery loop from DCC ref_resolver.py into common/library/loader/ | R99 | ✅ COMPLETE | I087 | — | `common/library/loader/schema_discovery.py` | — | — | — | §27 |
| T1.96.2 | [Schema/Config] Add discovery_rules to eks_config.json | Add 5 discovery rules matching existing schema conventions | R06 | ✅ COMPLETE | I087 | — | `eks_config.json`, `eks_setup_schema.json` | ← T1.96.1 | — | — | §27 |
| T1.96.3 | [Code] Refactor schema_loader.py for config-driven loading | Replace 22-filename hardcoded list with config-driven loop + discovery merge | R06 | ✅ COMPLETE | I087 | — | `schema_loader.py` | ← T1.96.1–2 | — | — | §27 |
| T1.96.4 | [Code] Wire validate_discovery_rules() in setup_validator.py | Call ValidationManager.validate_discovery_rules() when discovery_rules present | R99 | ✅ COMPLETE | I087 | — | `setup_validator.py` | ← T1.96.2 | — | — | §27 |
| T1.96.5 | [Docs] Update universal architecture doc | Verify §4.16 Schema Discovery pattern alignment with extracted function | R99 | ✅ COMPLETE | I087 | — | `common/universal_pipeline_architecture_design.md` | ← T1.96.1 | — | — | §27 |
| T1.96.6 | [Testing] Tests + suite green | Fix *_base.json pattern gap; full EKS suite 236/236 green | R99 | ✅ COMPLETE | I087 | — | `test/` | ← T1.96.1–5 | — | — | §27 |

---

## 16. System Parameters — SSOT Centralization (T1.97) Tasks

### 16.1 Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.97.1 | [Code] Create common/library/config/__init__.py | normalize_system_parameters() + get_system_param() for flat-object, direct-object, array-of-entry shapes | R99 | ✅ COMPLETE | I088 | — | `common/library/config/__init__.py` | — | — | — | §28 |
| T1.97.2 | [Schema] Add system_parameters_def to eks_base_schema.json | Flat-object definition with 9 typed properties; base v1.8.0 | R06 | ✅ COMPLETE | I088 | — | `eks_base_schema.json` | ← T1.97.1 | — | — | §28 |
| T1.97.3 | [Schema] Add system_parameters property to eks_setup_schema.json | Optional $ref to base def; additionalProperties: false; setup v1.6.0 | R06 | ✅ COMPLETE | I088 | — | `eks_setup_schema.json` | ← T1.97.2 | — | — | §28 |
| T1.97.4 | [Config] Add system_parameters block to eks_config.json | Instance data; consolidate registry.timeout into db_timeout; config v1.6.0 | R06 | ✅ COMPLETE | I088 | — | `eks_config.json` | ← T1.97.2–3 | — | — | §28 |
| T1.97.5 | [Code] Replace hardcoded values in phase1_server.py | Debug/log/readiness/retry globals from system_parameters; CLI flags as overrides | R99 | ✅ COMPLETE | I088 | — | `phase1_server.py` | ← T1.97.1, T1.97.4 | — | — | §28 |
| T1.97.6 | [Code] Replace hardcoded values in error_manager.py | ErrorManager reads fail_fast from system_parameters via get_system_param() | R51 | ✅ COMPLETE | I088 | — | `error_manager.py` | ← T1.97.1, T1.97.4 | — | — | §28 |
| T1.97.7 | [Code] Replace hardcoded values in registry.py | DocumentRegistry reads retry_count/delay/timeout from system_parameters | R02 | ✅ COMPLETE | I088 | — | `registry.py` | ← T1.97.1, T1.97.4 | — | — | §28 |
| T1.97.8 | [Code] Replace hardcoded timeouts in server.py | api_timeout, ollama_timeout from EKS config via get_system_param() | R99 | ✅ COMPLETE | I088 | — | `eks/server.py` | ← T1.97.1, T1.97.4 | — | — | §28 |
| T1.97.9 | [Testing] Tests + suite green | Add test_system_parameters.py; full suite green | R99 | ✅ COMPLETE | I088 | — | `test/test_system_parameters.py` | ← T1.97.1–8 | — | — | §28 |

### 16.3 Universal Architecture Elevation (I091)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.97.10 | [Code] Register config as L15 sub-package | Add config/ to docstring, from . import config, and "config" to __all__ | R99 | ✅ COMPLETE | I091 | — | `common/library/__init__.py` | — | — | — | §28 |
| T1.97.11 | [Docs] Add L15 to universal architecture inventory | Add L15 row to §2.2, config/ to §2.3, L15 detail to §2.4 | R99 | ✅ COMPLETE | I091 | — | `common/universal_pipeline_architecture_design.md` | — | — | — | §28 |
| T1.97.12 | [Docs] Add §3.17 System Parameters Pattern | Document schema-defined runtime behavior knobs, normalizer, shapes | R99 | ✅ COMPLETE | I091 | — | `common/universal_pipeline_architecture_design.md` | — | — | — | §28 |
| T1.97.13 | [Docs] Update §4.1/§4.2/§9/§10 in universal doc | Add System Parameters to guidelines, order, checklist, criteria | R99 | ✅ COMPLETE | I091 | — | `common/universal_pipeline_architecture_design.md` | — | — | — | §28 |
| T1.97.14 | [Docs] Update EKS knowledge.json | Reflect L15 status and universal architecture alignment | R99 | ✅ COMPLETE | I091 | — | `eks/knowledge.json` | — | — | — | §28 |

---

## 17. Universal Path Resolution & Schema-Driven Initialization (I089 + I090) Tasks

### 17.2 Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| T1.98.1 | [Code] Add common/library/paths/resolver.py | resolve_paths() + ResolvedPaths dataclass (6 dirs). Handles EKS global_paths; normalizes DCC shapes. | R99 | ✅ COMPLETE | I089 | — | `common/library/paths/resolver.py` | — | — | — | §29 |
| T1.98.2 | [Code] Export resolver from paths/__init__.py | Add resolve_paths, ResolvedPaths to package exports | R99 | ✅ COMPLETE | I089 | — | `common/library/paths/__init__.py` | ← T1.98.1 | — | — | §29 |
| T1.98.3 | [Code] Wire EKS ConfigRegistry to resolver | Route all 6 path properties through resolve_paths(); uniform access; replace PRJ_DIR inline lookups | R99 | ✅ COMPLETE | I089 | — | `config_registry.py`, `phase1_server.py` | ← T1.98.1 | — | — | §29 |
| T1.98.4 | [Docs] Universal architecture doc elevation | Add L16 to §2.2/§2.3/§2.4; add §4.18 Path Resolution Pattern; update §5.1/§10/§24 | R99 | ✅ COMPLETE | I089 | — | `common/universal_pipeline_architecture_design.md` | — | — | — | §29 |
| T1.98.5 | [Docs] Update eks/knowledge.json | Reflect L16 status and universal path-resolution alignment | R99 | ✅ COMPLETE | I089 | — | `eks/knowledge.json` | — | — | — | §29 |
| T1.98.6 | [Schema/Config] Add workflow_files + tool_files | Add defs to base, properties to setup, instance blocks to config (parallel to DCC project_config) | R06 | ✅ COMPLETE | I090 | — | `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json` | — | — | — | §29 |
| T1.98.7 | [Code] EKS loader/initializer for workflow/tool files | Register file manifest; auto-create declared dirs from global_paths via resolver | R99 | ✅ COMPLETE | I090 | — | `setup_validator.py`, `config_registry.py` | ← T1.98.1 | — | — | §29 |
| T1.98.8 | [Testing] Tests + suite green | test_path_resolver.py + workflow_files/tool_files schema tests; full suite 252/252 green | R99 | ✅ COMPLETE | I089, I090 | — | `test/test_path_resolver.py` | ← T1.98.1–7 | — | — | §29 |

---

## 18. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I092 / R60) Tasks

### Task Breakdown

| ID | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
| :-- | :---- | :----- | :----: | :---- | :---- | :---- | :---: | :--- |
| **T1.99.1–7** | **Entry-point convergence (I092)** | Shared `run_pipeline(context)` funnel, unified CLI, `phase1_server` wiring, orphan cleanup, `serve.py`, SSOT config, tests | **✅ COMPLETE** | I092 | — | — | — | — |
| T1.99.1 | Extract shared `bootstrap_pipeline()` / `run_pipeline(context)` helper | New `eks/engine/eks_engine_pipeline.py` (relocated from `eks/engine/core/pipeline_runner.py`, archived in T1.99.11): builds `ConfigRegistry` → `SchemaLoader.load_all()` → `DocumentRegistry` → `ErrorManager`/`MessageManager` → `ProjectSetupValidator` readiness gate → `PipelineOrchestrator.run_full_pipeline()`. Universal funnel reused by CLI and every phase server. | ✅ COMPLETE | I092 | — | `eks_engine_pipeline.py` | — | — |
| T1.99.2 | Unified end-to-end CLI | `eks/engine/eks_engine_pipeline.py` `main()` using the helper; register `pyproject` `console_scripts` (`eks-pipeline = "eks.engine.eks_engine_pipeline:main"`). | ✅ COMPLETE | I092 | — | `eks_engine_pipeline.py` | — | T1.99.1 |
| T1.99.3 | Wire `phase1_server._run` to `run_pipeline()` | Replace inline A→C with shared `run_pipeline()`; keep 409 guard + `resolve_paths()` (T1.98). | ✅ COMPLETE | I092 | — | `phase1_server.py` | — | T1.99.1, T1.98 |
| T1.99.4 | Delete orphan `engine_endpoints.py` | Dead stubbed FastAPI app (returns fake SUCCESS, unwired) archived to `archive/ui/backend/engine_endpoints.py` (AGENTS.md §4 archive-before-delete; no references remained). | ✅ COMPLETE | I092 | — | `archive/ui/backend/engine_endpoints.py` | — | T1.99.1 |
| T1.99.5 | Add `eks/serve.py` | Per AGENTS.md §18.12 (canonical launcher created; `server.py` retained as thin re-export shim). | ✅ COMPLETE | I092 | — | `eks/serve.py` | — | — |
| T1.99.6 | Use `ConfigRegistry` SSOT at entry | Pass the singleton (not raw config dict) to `ProjectSetupValidator`. | ✅ COMPLETE | I092 | — | `eks_engine_pipeline.py` | — | — |
| T1.99.7 | Tests | CLI smoke run + assert `run_full_pipeline` exercised; full suite green (257/257). | ✅ COMPLETE | I092 | — | `test_eks_engine_pipeline.py` | — | T1.99.1–6 |
| **T1.99.8–12** | **CLI relocation & main() sequence (I096)** | DCC-style main(), --phase selection, run_full_pipeline coordination, pipeline_runner consolidation, docs update | **✅ COMPLETE** | I096, I092, I078 | — | — | — | — |
| T1.99.8 | Relocate main CLI entry to `eks/engine/eks_engine_pipeline.py` | Create `eks/engine/eks_engine_pipeline.py` at the engine root (mirrors DCC `dcc/workflow/dcc_engine_pipeline.py`); build on `common.library.core.pipeline` (`BaseEngine`/`BasePipelineContext`/`EngineInput`/`EngineOutput`) + `common.library.paths.resolve_paths` (anchor/base path) — advances I078. Move `bootstrap_pipeline()` + `run_pipeline()` funnel here and define `main()` as the `eks-pipeline` console_scripts entry. Delete `eks/engine/parsers/cli.py`. Resolves naming/location confusion (I096). | ✅ COMPLETE | I096, I092, I078 | — | `eks_engine_pipeline.py`, `pyproject.toml` | — | T1.99.1–7 |
| T1.99.9 | DCC-style `main()` sequence + `--phase` selection | Implement `main()` following DCC's ordered sequence — project anchor → resolve base path (L16) → CLI args → messaging logger (L01/L11) → verbose/debug (L15) → `bootstrap_pipeline()` (L13) → orchestrator + `initialize_context()` → milestone → run. Add `--phase {A,B,C,full}` (default `full`). Advances I078. | ✅ COMPLETE | I096, I078 | — | `eks_engine_pipeline.py` | — | T1.99.8 |
| T1.99.10 | Extend `run_full_pipeline` coordination loop | Add `on_phase=None, checkpoint_dir=None, job_id=None` params to `PipelineOrchestrator.run_full_pipeline(root, recursive)`. Align to common `EngineInput`/`EngineOutput` + `checkpoint_state` contract (L08) and emit `TelemetryHeartbeat`/`DocumentProcessingHeartbeat` per phase (L05). | ✅ COMPLETE | I096, I092, I078 | — | `pipeline_orchestrator.py` | — | T1.99.9 |
| T1.99.11 | Consolidate `pipeline_runner.py` + repoint imports | Move `bootstrap_pipeline()`/`run_pipeline()` from `eks/engine/core/pipeline_runner.py` into `eks_engine_pipeline.py`; archive `pipeline_runner.py`; repoint 7 import sites. | ✅ COMPLETE | I096, I078 | — | `eks_engine_pipeline.py`, `phase1_server.py`, `discovery_cli.py`, `health_cli.py` | — | T1.99.8–10 |
| T1.99.12 | Update docs to new entry path | Update workplan §9 Mermaid ECLI + ERUN nodes, §9 files table, `reports/phase_1_foundation_report.md`, `appendix_f_pipeline_architecture_design.md` §2.3.3, `common/universal_pipeline_architecture_design.md` §8.2. Bump workplan → v3.62. | ✅ COMPLETE | I096, I078 | U148 | `phase_1_foundation_workplan.md`, `appendix_f_pipeline_architecture_design.md`, `universal_pipeline_architecture_design.md` | — | T1.99.8–11 |
| **T1.99.13–16** | **Anchor-folder path resolution (I097)** | resolve_pipeline_base_path, schema-driven data_dir default, global_paths routing, tests | **✅ COMPLETE** | I097 | — | — | — | — |
| T1.99.13 | Implement `resolve_pipeline_base_path()` with DCC-style anchor-folder walk (`engine/` anchor) | Walk `__file__.parents` looking for `engine/` folder (anchor), return parent as EKS project root. Fall back to `Path.cwd()`. Replace hardcoded `PRJ_DIR`. | ✅ COMPLETE | I097 | — | `eks_engine_pipeline.py` | — | — |
| T1.99.14 | Make `--data-dir` optional with schema-driven default from `global_paths.data_dir` | Change `--data-dir` from `required=True` to `required=False`. Precedence: CLI > Schema (global_paths) > Native (cwd). | ✅ COMPLETE | I097 | — | `eks_engine_pipeline.py` | — | T1.99.13 |
| T1.99.15 | Route all pipeline path defaults through resolved base path + global_paths schema | All directory defaults through `global_paths` schema fields: `output_dir`, `config_dir`, `log_dir`, `archive_dir`. Eliminates all 5+ hardcoded path literals. | ✅ COMPLETE | I097 | — | `eks_engine_pipeline.py`, `resolve_paths()` | — | T1.99.13–14 |
| T1.99.16 | Tests + docs update for anchor-folder path resolution | 5 path resolution tests. Bump workplan to v3.65. | ✅ COMPLETE | I097 | U149 | `test_eks_engine_pipeline.py` | — | T1.99.13–15 |
| **T1.99.17–26** | **L17 cross-platform entry-point discovery (I098)** | OS detection, default_base_path anchor walk, --base-path resolver, discover_project_root, global_paths routing, safe_posix, anchor-missing raise, tests, docs | **✅ COMPLETE** | I098, I078 | — | — | — | — |
| T1.99.17 | OS detection at pipeline entry (`detect_os`, L12) | Call `detect_os()` at top of `eks/engine/eks_engine_pipeline.py` entry before any path op. Closes I098 #7. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | — |
| T1.99.18 | Rename `__file__` walk → `default_base_path("eks")` returning parent of anchor | DCC-faithful: walk `__file__.parents` for `eks` anchor, return `parent.parent`. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | T1.99.17 |
| T1.99.19 | Add cwd/`--base-path` resolver `resolve_pipeline_base_path()` | `--base-path` (expanduser + resolve) else `Path.cwd()`. Execution-context resolver distinct from `__file__` walk. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | T1.99.18 |
| T1.99.20 | Add `discover_project_root()` + `--base-path` CLI + `==pipeline_dir` strip | `pipeline_dir = "eks"`; strip pipeline_dir from root if present; add `--base-path`/`--root` CLI arg. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | T1.99.19 |
| T1.99.21 | Route all sub-paths via `resolve_paths()` honoring `eks_root` (fix default `data_dir`) | Fix `data_dir` default → `project_root/eks/data`. Remove manual `gp.get()` duplication for all paths. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | T1.99.20 |
| T1.99.22 | OS-gated auto-create + `safe_posix()` serialization | Gate auto-create on `should_auto_create_folders(os_info)`; use `safe_posix()` for JSON/HTTP paths. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py`, `phase1_server.py` | — | T1.99.17 |
| T1.99.23 | Raise (not silent cwd) if anchor missing | `default_base_path` raises `FileNotFoundError` with guidance to use `--base-path`. | ✅ COMPLETE | I098 | — | `eks_engine_pipeline.py` | — | T1.99.18 |
| T1.99.24 | Entry-point resolution tests | 6 tests: cwd, --base-path, strip, default data_dir, detect_os, anchor-missing raise. | ✅ COMPLETE | I098 | — | `test_eks_engine_pipeline.py` | — | T1.99.17–23 |
| T1.99.25 | Wire common L12/L17 into EKS runtime (advances I078) | Replace EKS-local `.as_posix()` with `common.library` `detect_os`/`safe_posix`/`resolve_anchored`. | ✅ COMPLETE | I078 | — | `eks_engine_pipeline.py` | — | T1.99.17–22 |
| T1.99.26 | Docs / update logs / knowledge.json for I098 remediation | Update docstrings, §30 status, `eks_system_workplan.md`. I098 → Resolved. | ✅ COMPLETE | I098 | U152 | `eks_engine_pipeline.py`, `knowledge.json` | — | T1.99.17–25 |
| **T1.99.27–29** | **L18 schema-driven CLI parser (I099)** | Universal schema_cli.py, EKS wiring, tests + docs | **✅ COMPLETE** | I099 | — | — | — | — |
| T1.99.27 | Universal schema-driven CLI parser (L18) — `common/library/cli/schema_cli.py` | Schema-driven argument generation; L17 root-folder-based schema retrieval; CLI>Schema>Native overrides; structured `CliResult`. Replaces bespoke `build_parser()`. | ✅ COMPLETE | I099 | — | `common/library/cli/schema_cli.py` | — | T1.99.13 |
| T1.99.28 | Wire EKS to the universal L18 parser | Add `_EKS_CORE_ARG_SPECS`, `build_schema_driven_parser()`, `parse_eks_cli()`; refactor `run()` to consume `parse_eks_cli()`. | ✅ COMPLETE | I099 | — | `eks_engine_pipeline.py` | — | T1.99.27 |
| T1.99.29 | Tests + docs for L18 | 15 new tests + `TestSchemaDrivenCli`. Report RP-EKS-P1-CLI-001. | ✅ COMPLETE | I099 | U155 | `common/library/cli/tests/`, `test_eks_engine_pipeline.py`, `universal_pipeline_architecture_design.md` | — | T1.99.27–28 |
| **T1.99.30** | **DCC L18 wiring (excluded)** | DCC-related issues within EKS pipeline — tracked in DCC workplan | **⛔ Won't Implement** | I099, I101 | — | — | — | — |
| T1.99.30 | Wire DCC to universal L18 CLI parser (I101 follow-up) | **NOT TO BE IMPLEMENTED** — DCC-related issues within the EKS pipeline are not to be implemented. | ⛔ Won't Implement | I099, I101 | — | — | — | — |
| **T1.99.31–34** | **Per-issue fixes (I100–I104)** | ConfigRegistry drift fix, DEFAULT_PIPELINE_DIR removal, run()→main() merge, anchor/pipeline_dir locals | **✅ COMPLETE** | I100, I102, I103, I104, I092, I096, I099 | — | — | — | — |
| T1.99.31 | Fix EKS `project_setup` / ConfigRegistry config drift (I100) | `_schema_config_candidates` now probes `eks/config/schemas/eks_config.json`; `ConfigRegistry.__new__` promotes singleton only after successful `load_all()`. 277/277 green. | ✅ COMPLETE | I100 | — | `common/library/cli/schema_cli.py`, `config_registry.py` | — | T1.99.27–28 |
| T1.99.32 | Remove EKS-specific `DEFAULT_PIPELINE_DIR` from common.library (I102) | Neutral sentinel forces caller to pass `pipeline_dir` explicitly. EKS declares literals locally in `main()`. | ✅ COMPLETE | I102 | — | `common/library/paths/root_discovery.py`, `common/library/cli/schema_cli.py`, `eks_engine_pipeline.py` | — | — |
| T1.99.33 | Merge `run()` into `main()` (DCC-faithful entry point, I103) | Move `run()` body into `main(args) -> int`; delete separate `run()`; `if __name__ == "__main__": sys.exit(main())`. | ✅ COMPLETE | I103, I092, I096, I099 | — | `eks_engine_pipeline.py` | — | T1.99.32 |
| T1.99.34 | Declare `anchor`/`pipeline_dir` as locals in `main()` + pass explicitly (I104) | DCC-faithful I/O clarity: declare `pipeline_root_dir = "eks"` and `pipeline_dir = "engine"` locally in `main()` and pass explicitly. Module-level constants removed. | ✅ COMPLETE | I104, I092, I096, I099, I102 | — | `eks_engine_pipeline.py` | — | T1.99.33 |

### Universal Bootstrap Manager (I108–I111 / L19) Tasks

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.50 | [Code] Create universal `BootstrapManager` in `common/library/bootstrap/` (L19) | Extracted from DCC's mature implementation. Foundation for all subsequent EKS wiring tasks (I109–I111). | L19 | ✅ COMPLETE | I108 | — | `common/library/bootstrap/` | — | — | — | §30 |
| T1.99.51 | [Code] Phase registry with configurable ordering | Phase registry supports custom sort order for bootstrap phases. | L19 | ✅ COMPLETE | I108 | — | `common/library/bootstrap/` | ← T1.99.50 | — | — | §30 |
| T1.99.52 | [Code] `to_pipeline_context()` returns valid `BasePipelineContext` (L06) | Returns context object conforming to L06 schema. | L19 | ✅ COMPLETE | I108 | — | `common/library/bootstrap/` | ← T1.99.50 | — | — | §30 |
| T1.99.53 | [Code] `bootstrap_for_ui()` dual-mode | Skips CLI, accepts UI params directly. | L19 | ✅ COMPLETE | I108 | — | `common/library/bootstrap/` | ← T1.99.50 | — | — | §30 |
| T1.99.54 | [Code] Universal `BootstrapError` wired to L10 `BaseErrorManager` | Structured error handling across all bootstrap phases. | L19 | ✅ COMPLETE | I108 | — | `common/library/bootstrap/` | ← T1.99.50 | — | — | §30 |
| T1.99.55 | [Testing] Universal bootstrap tests green | Phase tracking, trace, dual-mode, errors — all pass. | L19 | ✅ COMPLETE | I108 | — | `test/` | ← T1.99.50–54 | TL002 | — | §30 |
| T1.99.56 | [Docs] Update universal architecture doc with L19 + §3.19 | Document universal BootstrapManager design. | L19 | ✅ COMPLETE | I108 | — | `common/universal_pipeline_architecture_design.md` | ← T1.99.50 | — | — | §30 |
| T1.99.57 | [Code] EKS `BootstrapManager` subclass with project-specific hooks | Subclasses universal L19 with EKS-specific phase hooks. | L19, EKS | ✅ COMPLETE | I109 | — | `eks/engine/core/bootstrap.py` | ← T1.99.50 | — | — | §30 |
| T1.99.58 | [Code] `bootstrap_pipeline()` thin wrapper; backward-compat preserved | Delegates to universal `BootstrapManager`. | EKS | ✅ COMPLETE | I109 | — | `eks/engine/core/bootstrap.py` | ← T1.99.57 | — | — | §30 |
| T1.99.59 | [Code] `main()` uses `manager.bootstrap_all().to_pipeline_context()` chain | Clean chain pattern in entry point. | EKS | ✅ COMPLETE | I109 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.58 | — | — | §30 |
| T1.99.60 | [Code] Manual context assembly (~30 lines) collapsed; `main()` is thin shell | Context now derived from bootstrap pipeline, not manually assembled. | EKS | ✅ COMPLETE | I110 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.59 | — | — | §30 |
| T1.99.61 | [Code] `EngineInput` derived from context | Engine input constructed from pipeline context. | EKS | ✅ COMPLETE | I110 | — | `eks/engine/core/base.py` | ← T1.99.60 | — | — | §30 |
| T1.99.62 | [Schema] `P1-BOOT-*` codes registered in `eks_error_config.json` | All bootstrap error codes registered. | EKS | ✅ COMPLETE | I111 | — | `eks/config/schemas/eks_error_config.json` | ← T1.99.57 | — | — | §30 |
| T1.99.63 | [Code] `RuntimeError` replaced with structured `BootstrapError`; error-path tests green | Structured errors with registered codes; full EKS suite green. | EKS | ✅ COMPLETE | I111 | — | `eks/engine/core/bootstrap.py` | ← T1.99.62 | TL002 | — | §30 |

### Error Code Alignment, Pre-Bootstrap Logger, and Environment Check Tasks (I112–I114)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.64 | [Docs] Update Appendix D: add Bootstrap category (`S-B-S-0600–0699`) | D3 updated; `P1-BOOT-*` format documented in D2. | Docs | ✅ COMPLETE | I112 | U181 | `appendix_d_pipeline_messages_errors.md` | ← T1.99.63 | — | U181 | §30 |
| T1.99.65 | [Schema] Register 14 universal `B-*` codes in `eks_error_config.json` | Under new `bootstrap_universal` range; `eks_error_code_base.json` pattern updated. | Schema | ✅ COMPLETE | I112 | U181 | `eks/config/schemas/eks_error_config.json` | ← T1.99.64 | — | U181 | §30 |
| T1.99.66 | [Schema] Add bootstrap milestone/status messages to `eks_message_config.json` | `eks_message_base.json` + Appendix D D6 updated. | Schema | ✅ COMPLETE | I112 | U181 | `eks/config/schemas/eks_message_config.json` | ← T1.99.64 | — | U181 | §30 |
| T1.99.67 | [Config] Decide and implement `P1-BOOT-*` format (A: migrate to `S-B-S-06xx` or B: keep hybrid) | Format decision made and implemented across all sources. | Config | ✅ COMPLETE | I112 | U181 | — | ← T1.99.64–66 | — | U181 | §30 |
| T1.99.68 | [Code] Ensure all EKS code paths use registered error codes | No unregistered `B-*` codes can fire in EKS context. | EKS | ✅ COMPLETE | I112 | U181 | `eks/engine/` | ← T1.99.67 | — | U181 | §30 |
| T1.99.69 | [Testing] Tests + docs + close I112 | Verify all bootstrap codes resolve via `ErrorManager`; messages via `MessageManager`; Appendix D fully updated. | EKS | ✅ COMPLETE | I112 | U181 | — | ← T1.99.64–68 | — | U181 | §30 |
| T1.99.70 | [Code] Early CLI parse for `--level`/`--debug` before bootstrap | `_parse_early_verbosity()` at L470–504. | EKS | ✅ COMPLETE | I113 | — | `eks/engine/eks_engine_pipeline.py` | — | — | — | §30 |
| T1.99.71 | [Code] `UniversalLogger` created pre-bootstrap, passed to `EKSBootstrapManager(logger=logger)` | L548, L573. | EKS | ✅ COMPLETE | I113 | — | `eks/engine/eks_engine_pipeline.py`, `common/library/logger/` | ← T1.99.70 | — | — | §30 |
| T1.99.72 | [Code] `TelemetryHeartbeat` created pre-bootstrap, covers all 8 phases | L552–553. | EKS | ✅ COMPLETE | I113 | — | `eks/engine/core/telemetry.py` | ← T1.99.71 | — | — | §30 |
| T1.99.73 | [Code] Verify all EKS bootstrap hooks use `self.logger` | `_eks_error_factory`/`_eks_message_factory` pass through; `BootstrapManager._log()` wired. | EKS | ✅ COMPLETE | I113 | — | `eks/engine/core/bootstrap.py` | ← T1.99.72 | — | — | §30 |
| T1.99.74 | [Testing] CLI + pipeline test suite passes; close I113 | Covered by existing test suite. | EKS | ✅ COMPLETE | I113 | — | — | ← T1.99.70–73 | TL002, TL003, TL004 | — | §30 |
| T1.99.75 | [Code] **L20**: Create universal `test_environment()` in `common/library/core/system/` | Stdlib-only (`importlib`, `platform`, `pathlib`); `import_module()` loop; returns `{ready, errors, required_modules, ...}`. | L20 | ✅ COMPLETE | I114 | — | `common/library/core/system/tester.py` | — | — | — | §30 |
| T1.99.76 | [Code] **L19**: Add `env_tester` strategy hook to universal `BootstrapManager` | P6 calls it after OS detection; backward-compat (not injected → OS-detection-only). | L19 | ✅ COMPLETE | I114 | — | `common/library/bootstrap/` | ← T1.99.75 | — | — | §30 |
| T1.99.77 | [Code] **EKS**: Wire `_bootstrap_env()` to universal `test_environment()` via `env_tester` hook | `ready=False` → `BootstrapError("P1-BOOT-ENV", ...)` with "Run: conda activate eks" guidance. | EKS | ✅ COMPLETE | I114 | — | `eks/engine/core/bootstrap.py` | ← T1.99.76 | — | — | §30 |
| T1.99.78 | [Schema] **EKS**: Register `P1-BOOT-ENV` in `eks_error_config.json`; update schemas | Error code + schema updates. | EKS | ✅ COMPLETE | I114 | — | `eks/config/schemas/eks_error_config.json` | ← T1.99.77 | — | — | §30 |
| T1.99.79 | [Docs] Update `update_log.md` + `issue_log.md`; close I114 | I114 → Resolved. | EKS | ✅ COMPLETE | I114 | U179 | `p1_update_log.md`, `p1_issue_log.md` | ← T1.99.75–78 | — | U179 | §30 |
| T1.99.80 v2 | [Fix] **Lazy-import refactor**: ALL `common.library` imports deferred from module level to inside functions | Module-level now stdlib-only; no bare `ModuleNotFoundError` reaches user. | EKS | ✅ COMPLETE | I114 | U179 | `eks/engine/eks_engine_pipeline.py` | ← T1.99.79 | TL002, TL003 | U179 | §30 |

### Preload Infrastructure Guard (I117) Tasks

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.81 | [Code] Create `_preload_infrastructure()` pure-stdlib guard in `eks_engine_pipeline.py` | Individually try/except-guards all 4 `common.library` import groups (paths, root_discovery, logging, pipeline); collects errors into single dict `{ready, errors, logger, heartbeat, project_root, ...}`; `main()` gates on `infra["ready"]`, prints all errors with `FATAL:` prefix on failure; happy path preserved — if all imports succeed, `main()` proceeds identically. | EKS | ✅ COMPLETE | I117 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.80 | TL002, TL003 | — | §30 |
| T1.99.82 | [Docs] Update `p1_issue_log.md` | Log I117 with root-cause analysis (chicken-and-egg problem). | EKS | ✅ COMPLETE | I117 | — | `p1_issue_log.md` | ← T1.99.81 | — | — | §30 |
| T1.99.83 | [Docs] Update workplan | Add T1.99.81–83 tasks, §30.3 section; document universal preload pattern. | EKS | ✅ COMPLETE | I117 | — | `eks/workplan/phase_1_foundation_workplan.md` | ← T1.99.81–82 | — | — | §30 |

### I130/I131/I132 Pipeline Defect Fixes Tasks

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.101 | [Fix] **I130**: Fix bootstrap path-resolution rooting defect | One-line logic change in `bootstrap.py`: add `and self.config` guard — `if self._path_resolver is not None and self.config:` — skips resolver when config empty, uses else-branch correctly anchored under `pipeline_root_dir="eks"`. Prevents `engine/`, `archive/`, `test_output/` from being created at repo root. | EKS | ✅ COMPLETE | I130 | U181 | `eks/engine/core/bootstrap.py` | — | — | U181 | §30 |
| T1.99.102 | [Cleanup] **I130**: Clean stale root-level directories | Remove incorrectly-created `engine/`, `archive/`, `test_output/` directories at repo root (artifacts of the path-resolution defect). | EKS | ✅ COMPLETE | I130 | U181 | — | ← T1.99.101 | — | U181 | §30 |
| T1.99.103 | [Testing] **I130**: Verify zero new root-level directories after fix | Confirm no new root-level dirs are created after the guard fix. Pipeline output restricted to `eks/` sub-tree. | EKS | ✅ COMPLETE | I130 | U181 | — | ← T1.99.101–102 | TL003 | U181 | §30 |
| T1.99.104 | [Fix] **I131**: Fix `_parse_filename()` fallback to include `revision="00"` | L1 defense: `_parse_filename()` had 3 code paths; filename `131101-WSW41-SP-SG-0101.pdf` matched no revision pattern → fallback returned `{"document_number": stem}` only (no `revision` key). Fix: fallback now returns `revision="00"`. | EKS | ✅ COMPLETE | I131 | U181 | `eks/engine/core/file_scanner.py` | — | — | U181 | §30 |
| T1.99.105 | [Fix] **I131**: Add `setdefault("revision", "00")` safety net in `build_placeholder_metadata()` | L2 defense: `build_placeholder_metadata()` now has `setdefault("revision", "00")` safety net — catches any upstream source that omits `revision`. | EKS | ✅ COMPLETE | I131 | U181 | `eks/engine/pipeline_orchestrator.py` | ← T1.99.104 | — | U181 | §30 |
| T1.99.106 | [Fix] **I131**: Use `.get("revision", "00")` in `register_document()` | L3 defense: `register_document()` now uses `.get("revision", "00")` instead of direct dict access `metadata["revision"]`. Three-layer layered defense complete. | EKS | ✅ COMPLETE | I131 | U181 | `eks/engine/core/registry.py` | ← T1.99.105 | — | U181 | §30 |
| T1.99.107 | [Testing] **I131**: Tests + logs update for revision KeyError fix | Verify Phase A→B→C pipeline runs (19 files, 7 flagged). All 3 layers applied. Update `update_log.md`. | EKS | ✅ COMPLETE | I131 | U181 | `eks/test/test_t132_modules.py`, `p1_update_log.md` | ← T1.99.104–106 | TL003 | U181 | §30 |
| T1.99.108 | [Fix] **I132**: Add CAD document type for `.dwg` files | `.dwg` was registered in `file_type_registry` but no document type listed `.dwg` in `expected_file_types` → files classified as `unknown`. Fix: added `"CAD"` document type to `eks_doc_base_schema.json` enum, `eks_doc_setup_schema.json` propertyNames pattern, and `eks_doc_config.json` document_type_registry + element_expectations. | EKS | ✅ COMPLETE | I132 | U181 | `eks/config/schemas/eks_doc_base_schema.json`, `eks/config/schemas/eks_doc_setup_schema.json`, `eks/config/schemas/eks_doc_config.json` | — | TL003 | U181 | §30 |

---

## 19. Data Export — CSV/Excel Pipeline Output (I126 / L22) Tasks

> Source: [§32](phase_1_foundation_workplan.md#32)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.153 | [Code] Add `db_path` param to `DocumentRegistry.__init__` | Optional `db_path` parameter bypasses config for explicit path control. Enables test-isolated databases. Bumped registry.py to v0.6. | EKS registry | ✅ COMPLETE | I126 | — | `eks/engine/core/registry.py` | — | — | — | §32 |
| T1.99.154 | [Code] Scope export to current-run docs (F2) | In `main()`: capture pre-run `document_number` set via `reg_pre.list_documents()`, filter post-run `all_docs` to only new docs. | EKS export | ✅ COMPLETE | I126 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.153 | — | — | §32 |
| T1.99.155 | [Code] Per-run output subdirectories (F3) | Write exports to `output/<run_id>/` (UUID subdirectory). `run_id` already generated in `main()` via `engine_in.run_id`. | EKS export | ✅ COMPLETE | I126 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.154 | — | — | §32 |
| T1.99.156 | [Testing] Isolate export test DB + output (F4) | `test_main_export_both_runs` uses `mock.patch.object(registry_module, "DocumentRegistry", _IsolatedRegistry)` with temp DB path. | EKS test | ✅ COMPLETE | I126 | — | `eks/test/` | ← T1.99.153–155 | TL002 | — | §32 |

### Task Breakdown — L22 Universal DataExporter

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.87 | [Code] Create `common/library/export/` — universal `DataExporter` | Package: `__init__.py` re-exports `DataExporter`, `export_to_csv`, `export_to_excel`, `export_multi_sheet`. Core: `exporter.py` with `DataExporter` class — constructor accepts optional `overwrite=True` param. Follows `common/library/` facade pattern; add to `common/library/__init__.py` `__all__`. Error codes in `S-DE-*` range (S=System, DE=DataExport). | L22 | 🔷 PLANNED | I126 | — | `common/library/export/` | — | — | — | §32.4 |
| T1.99.88 | [Code] Implement `export_to_csv()` | Uses `csv.DictWriter` (stdlib). Accepts `rows: list[dict]`, `path: Path`, optional `columns: list[str]` for column ordering. Writes BOM (`\ufeff`) for Excel UTF-8 compatibility. Returns `path`. No extra deps. | L22 | 🔷 PLANNED | I126 | — | `common/library/export/exporter.py` | ← T1.99.87 | — | — | §32.4 |
| T1.99.89 | [Code] Implement `export_to_excel()` + `export_multi_sheet()` | Uses `openpyxl.Workbook` (already in eks.yml/dcc.yml). Single-sheet: `export_to_excel(rows, path, sheet_name="Sheet1")`. Multi-sheet: `export_multi_sheet(sheets: dict[str, list[dict]], path)` — each key = sheet name. Auto-column-width, header row bold + frozen. Returns `path`. Reuses DCC's output pattern (`index=False`) but accepts `list[dict]` (no pandas dependency). | L22 | 🔷 PLANNED | I126 | — | `common/library/export/exporter.py` | ← T1.99.88 | — | — | §32.4 |
| T1.99.90 | [Testing] Add universal tests | `common/library/export/tests/test_exporter.py`: csv round-trip (write→read→compare), excel round-trip (write→openpyxl read→compare), multi-sheet Excel, empty rows → empty file with headers only, Unicode/CJK characters, error paths (invalid path, read-only dir, empty rows list). | L22 | 🔷 PLANNED | I126 | — | `common/library/export/tests/test_exporter.py` | ← T1.99.87–89 | — | — | §32.4 |
| T1.99.91 | [Docs] Update universal architecture doc | Register L22 in `common/universal_pipeline_architecture_design.md` §2.2 Inventory Table; add §3.23 design pattern section (DataExporter); update §2.3 package structure diagram; bump module count 21→22; add to §4.1 and §4.2; add checklist item in §9 Appendix A. | L22 | 🔷 PLANNED | I126 | — | `common/universal_pipeline_architecture_design.md` | ← T1.99.87 | — | — | §32.4 |
| T1.99.92 | [Code] Add `--export` flag to pipeline entry | Add `--export {csv,xlsx,both,none}` (default: `none`) to L18 schema-driven CLI parser in `parse_eks_cli()`. In `main()`, after `run_pipeline(context=ctx)`, if `--export` is set, query DB results and call `DataExporter` methods. Output to `resolve_paths() → output_dir`. | EKS CLI | 🔷 PLANNED | I126 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.87–91 | — | — | §32.4 |
| T1.99.93 | [Code] Wire 3 export calls after pipeline returns | **Design decision (2026-07-18): Export stays in `main()`, not in `PipelineOrchestrator`** — export is output formatting, not pipeline processing. The orchestrator remains pure (no `export_config` parameter). In `eks_engine_pipeline.py` `main()`, after `run_pipeline()` returns: **(a)** Query `returned_ctx.registry.list_documents(extract_status='pending')` → `DataExporter().export_to_csv/excel(rows, output_dir / "discovery_inventory.{fmt}")`. **(b)** Query all documents + aggregate element counts from `returned_ctx.data` → `extraction_results.{fmt}`. **(c)** Query flagged documents (`extract_status!='success'` or `confidence<0.70`) → `review_flags.{fmt}`. | EKS main() | 🔷 PLANNED | I126 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.92 | — | — | §32.4 |
| T1.99.94 | [Code] Add export endpoint + update logs | Add `GET /api/v1/export/{phase}/{format}` to `phase1_server.py` — phases: `a`, `b`, `c`, `all`; formats: `csv`, `xlsx`. Returns `FileResponse` with correct Content-Type. Update logs. | EKS API | 🔷 PLANNED | I126 | — | `eks/ui/backend/phase1_server.py` | ← T1.99.87–93 | TL005 | — | §32.4 |

### Task Breakdown — Post-Implementation Gap Fix (I188)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.147 | [Fix] Fix `discovery_inventory` empty — remove `["pending"]` filter | Change L987 `_build_export_rows(all_docs, ["pending"], discovery_cols)` → `_build_export_rows(all_docs, None, discovery_cols)`. Discovery inventory reflects ALL documents registered in Phase A. | EKS export | ✅ COMPLETE | I188 | U19x | `eks/engine/eks_engine_pipeline.py` | — | — | U19x | §32.7 |
| T1.99.148 | [Fix] Fix `review_flags` empty — flag missing confidence unconditionally | Change L1126-1127 `elif status != "success"` → unconditional `else:` so `confidence=None` always generates `"Confidence: missing"` flag. Unblocks review_flags output. | EKS export | ✅ COMPLETE | I188 | U19x | `eks/engine/eks_engine_pipeline.py` | ← T1.99.147 | — | U19x | §32.7 |
| T1.99.149 | [Testing] Verify — run pipeline with `--export both` and assert 3 files | Manual verification: run `main(["--data-dir", "...", "--export", "both"])`, check `eks/output/` for `discovery_inventory.csv`, `extraction_results.csv`, `review_flags.csv` (and xlsx equivalents). | EKS export | ✅ COMPLETE | I188 | U19x | — | ← T1.99.147–148 | — | U19x | §32.7 |
| T1.99.150 | [Testing] Add export-specific unit tests | In `test_eks_engine_pipeline.py`: test `_build_export_rows` (with/without status filter, column subset), test `_build_flagged_rows` (None-confidence + success, low confidence, non-success), test `main()` with `--export both` (assert output files exist). | EKS test | ✅ COMPLETE | I188 | U19x | `eks/test/test_eks_engine_pipeline.py` | ← T1.99.147–149 | — | U19x | §32.7 |
| T1.99.151 | [Docs] Update issue log + workplan | Set I188 → Resolved in `issue_log.md`; mark T1.99.147–150 as ✅ COMPLETE; update `update_log.md` U19x. | EKS docs | ✅ COMPLETE | I188 | U19x | `p1_issue_log.md`, `p1_update_log.md` | ← T1.99.147–150 | — | U19x | §32.7 |

---

## 20. Schema-Driven Export Columns — Replace Hardcoded 11-Field Subset (I193) Tasks

> Source: [§47](phase_1_foundation_workplan.md#47)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.157 | [Schema] Add `x_export` boolean to every property in `document_metadata_def` | 48 properties in `document_metadata_def` (45 `true`, 3 `false`: `is_latest`, `supersedes`, `superseded_by`) + 5 properties in `project_metadata_def` (all `true`). Schema version bumped to 1.8.0. | Schema | ✅ COMPLETE | I193 | — | `eks/config/schemas/eks_doc_base_schema.json` | — | — | — | §47 |
| T1.99.158 | [Schema] Add `export_artifact_def` definition | Enumerate `discovery_inventory`, `extraction_results`, `review_flags` artifact column sets with descriptions. Shape-only definition; actual columns derived from `x_export` at runtime. | Schema | ✅ COMPLETE | I193 | — | `eks/config/schemas/eks_doc_base_schema.json` | ← T1.99.157 | — | — | §47 |
| T1.99.159 | [Code] Create `resolve_export_columns()` helper | Read `x_export` flags from schema JSON, derive per-artifact column lists in schema-definition order (project fields → doc fields). Falls back to hardcoded 11-column defaults with `_fallback: True` flag on load failure. | Pipeline | ✅ COMPLETE | I193 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.157–158 | — | — | §47 |
| T1.99.160 | [Code] Replace hardcoded `_build_export_rows()` and column lists | `_build_export_rows()` → pass-through full doc dict (removed 11-field manual construction). `_build_flagged_rows()` → pass-through + `flag_reason`. `main()` → uses `resolve_export_columns()` with graceful fallback. | Pipeline | ✅ COMPLETE | I193 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.99.159 | — | — | §47 |
| T1.99.161 | [Testing] Add schema-validation tests for `x_export` and artifacts | (a) `test_x_export_flag_present_on_all_properties` — every doc/proj property has boolean `x_export`, internal fields verified `false`. (b) `test_export_artifact_def_exists_and_valid` — 3 artifacts defined, structure valid. (c) `test_export_artifacts_have_different_column_sets` — discovery ⊂ extraction, extraction-only = {page_count, extract_status, ...}, review has flag_reason. | Test | ✅ COMPLETE | I193 | — | `eks/test/` | ← T1.99.157–160 | TL002 | — | §47 |
| T1.99.162 | [Testing] Verify full export with 50 columns | Pipeline run verified: `discovery_inventory`: 46 cols (was 6), `extraction_results`: 50 cols (was 10), `review_flags`: 12 cols (was 8). All 10 previously-missing fields present (project_title, embedded_title, file_size, file_hash, lifecycle_stage, created_by, vendor_name, originator_company, file_modified_at, security_class). | Pipeline | ✅ COMPLETE | I193 | — | — | ← T1.99.157–161 | TL002 | — | §47 |

---

## 21. Appendix D vs. Actual Pipeline Cross-Source Audit Tasks

> Source: [§48](phase_1_foundation_workplan.md#48)

### Priority 1 — Critical Bug Fixes (D1, D2)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.163 | [Fix] D1: Fix `HealthScorer.score()` caller — structural elements misrouted | Change `score(doc, elements)` → `score(doc, structural_elements=elements)` in `pipeline_orchestrator.py:640` and `review_manager.py:129`. Update test calls. | Health | ✅ COMPLETE | — | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/review_manager.py` | — | TL003 | — | §48 |
| T1.99.164 | [Fix] D2: Add 9 missing message IDs to `eks_message_config.json` + align pipeline names | Add `STATUS_PHASE_A_START/COMPLETE`, `STATUS_PHASE_B_START/COMPLETE`, `STATUS_PHASE_C_START/COMPLETE`, `STATUS_PIPELINE_START/COMPLETE`, `ERROR_FILE_PROCESSING`. Align all code call sites. | Message | ✅ COMPLETE | — | — | `eks/config/schemas/eks_message_config.json` | ← T1.99.163 | — | — | §48 |

### Priority 2 — Error Code Registration (D3)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.165 | [Schema] D3: Register 6 ad-hoc error codes in `eks_error_config.json` with correct severity | Map S-PIP-001/002/003 → S-R-S (ERROR). Map D5-REG-001 → P1-D-P. Map D5-DETECT-001, D5-SCORE-001 → P3-E-E. | Error | ✅ COMPLETE | — | — | `eks/config/schemas/eks_error_config.json` | ← T1.99.163–164 | — | — | §48 |

### Priority 3 — Health Score Accuracy (D5, D6, D7)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.166 | [Code] D5: Add 15 new columns to `ALL_SCOABLE` tier sets | T2: document_title, lifecycle_stage, revision_date, project_phase, contract_package, issued_date, responsible_engineer, total_sheets, supersedes, superseded_by. T3: revision_description, embedded_revision_number, references_documents, language, vendor_name. | Health | ✅ COMPLETE | — | — | `eks/engine/core/health_scorer.py` | — | TL003 | — | §48 |
| T1.99.167 | [Code] D6: Add `"F": 0.0` to `COVER_TYPE_SOURCE_SCORES` | Single-line addition. Type F = parse failed entirely → source quality score = 0.0. | Health | ✅ COMPLETE | — | — | `eks/engine/core/health_scorer.py` | ← T1.99.166 | — | — | §48 |
| T1.99.168 | [Code] D7: Wire `get_health_impact()` into `_process_file()` | After `self.scorer.score()`, call `penalty = self.error_manager.get_health_impact(doc_id)`, compute `adjusted = max(0.0, score + penalty / 100.0)`, store adjusted score in DB. | Pipeline | ✅ COMPLETE | — | — | `eks/engine/pipeline_orchestrator.py` | ← T1.99.166–167 | — | — | §48 |

### Priority 4 — Expected Elements Alignment (D8)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.169 | [Config] D8: Sync `EXPECTED_ELEMENTS_BY_TYPE` with Appendix D | Add `table` to Type A/B expectations (change from 4→5 expected elements) OR evaluate that code's 4-element model is correct and document the deviation. Decision deferred to review. | Health/Schema | ✅ COMPLETE | — | — | `eks/engine/core/health_scorer.py` or `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.166–168 | — | — | §48 |

### Priority 5 — Documentation Sync (D4, D9–D13)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.170 | [Docs] D4: Update Appendix D D3/D5 error taxonomy to reflect actual P1-D-P/P5-F/P3 codes | Remove aspirational P1-R-R/P1-V-V/P1-C-C taxonomy; document actual module codes `P1-D-P`, `P3-G-G`, `P5-F-V/S/PROP`. Add cross-reference to actual `eks_error_config.json` entries. | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.165 | — | — | §48 |
| T1.99.171 | [Docs] D9: Update Appendix D D7.1 column catalog to 54+ columns | Replace 25-column table with current schema-derived 54-column catalog. Split T1/T2/T3 tiers to match `ALL_SCOABLE` after GAP-D5 fix (39 scorable). | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.166 | — | — | §48 |
| T1.99.172 | [Docs] D10: Update Appendix D D8 status lifecycle to code's `extract_status` model | Replace `NEW→EXTRACTED→REGISTERED→VERIFIED` with `pending→success/partial/failed`. Document that document state is column-based, not a lifecycle FSM. | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | — | — | — | §48 |
| T1.99.173 | [Docs] D11: Update Appendix D D4 system error catalog names to match config | Swap mismatched names at S-E-S-0101–0105. Config values are SSOT. Add `ENVIRONMENT_NOT_READY` (S-E-S-0104), `DUCKDB_UNAVAILABLE` (S-E-S-0105). | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.165 | — | — | §48 |
| T1.99.174 | [Docs] D12: Update Appendix D D4.3 range allocation — 05xx = AI, not Database | Document that range 05xx is now S-A (AI/Optional services). Note gap: Database errors (DuckDB/Neo4j) have no dedicated range; evaluate whether S-D 06xx should be allocated. | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.165 | — | — | §48 |
| T1.99.175 | [Docs] D13: Update Appendix D D4 file I/O + config code ranges to actual config | Document actual ranges: file I/O 0201–0206 (not 0201–0212), config 0301–0308 (not 0301–0311). Note 10 missing aspirational codes may be added in future phase if needed. | Docs | 🔷 PLANNED | — | — | `docs/appendix_d_pipeline_messages_errors.md` | ← T1.99.165 | — | — | §48 |

---

## 22. Appendix E+F vs. Pipeline Architecture Cross-Source Audit — Gap Remediation (I208–I225) Tasks

> Source: [§49](phase_1_foundation_workplan.md#49)

### Wave 1 — Critical Wiring Gaps (I212, I216, I224) — Must-Fix Before Phase 2

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.179 | [Code] G5: Wire `RevisionManager` into Phase B for supersession detection | Implement `detect_supersession()` in `revision.py` — query existing docs by document_number, compare revisions with `_compare_revisions()` supporting numeric/alphabetic; wired into `PipelineOrchestrator._process_file()` after successful parse+score, using parsed revision from metadata. 5 tests covering all supersession cases. 296/305 pass, 0 regressions. | Revision | ✅ COMPLETE | I212 | — | `eks/engine/core/revision.py`, `eks/engine/pipeline_orchestrator.py` | — | TL012 | U205 | §49 |
| T1.99.180 | [Code] G9: Restore checkpoint persistence with resume capability | Uncomment `save_checkpoint()` calls. Write checkpoints to `output/<run_id>/checkpoint_<phase>.json`. Add `--resume <run_id>` CLI flag. | Pipeline | 🔷 PLANNED | I216 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/eks_engine_pipeline.py` | ← T1.99.179 | — | — | §49 |
| T1.99.181 | [Code] G17: Wire `ReviewManager` into Phase C for review status persistence | Iterate flagged docs: apply auto-corrections, expose remaining flags, `approve_document()` persists to registry. Add `POST /api/v1/review/approve` endpoint. | Review | 🔷 PLANNED | I224 | — | `eks/engine/core/review_manager.py`, `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/registry.py`, `eks/ui/backend/phase1_server.py` | ← T1.99.179–180 | — | — | §49 |

### Wave 2 — Architecture Compliance (I209, I211, I215, I221) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.182 | [Code] G2: Refactor `FileScanner`, `HealthScorer`, `StructureDetector` to inherit from `BaseEngine` | Each engine gets `validate_input()` → `execute()` → `validate_output()`. Use `EngineInput`/`EngineOutput` from `core/base.py`. Complete `ParserRouter`. | Architecture | 🔷 PLANNED | I209 | — | `eks/engine/core/file_scanner.py`, `eks/engine/core/health_scorer.py`, `eks/engine/core/structure_detector.py`, `eks/engine/parsers/parser_router.py` | — | — | — | §49 |
| T1.99.183 | [Code] G4: Replace direct instantiation in `PipelineOrchestrator` with factory calls | Change `self.scanner = FileScanner(...)` → `self.scanner = EngineFactory.create("FileScanner", ...)` for all engines. Verify `ParserRouter` consistency. | DI | ✅ COMPLETE | I211 | TL010 | `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/factories.py` | ← T1.99.182, T1.182.1–5 | TL010 | U203 | §49 |
| T1.99.184 | [Code] G8: Unify dual telemetry into single heartbeat stream | `PipelineOrchestrator` accepts `telemetry: Optional[TelemetryHeartbeat]` parameter; forwards checkpoints to main heartbeat. | Telemetry | 🔷 PLANNED | I215 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/eks_engine_pipeline.py`, `eks/engine/core/telemetry.py` | — | — | — | §49 |
| T1.99.185 | [Fix] G14: Guard `psutil` import in `telemetry.py` | Wrap `import psutil` in try/except ImportError; memory/CPU sampling becomes no-op when absent. Add `psutil` to `eks.yml` as optional dependency. | Safety | 🔷 PLANNED | I221 | — | `eks/engine/core/telemetry.py`, `eks/eks.yml` | ← T1.99.184 | — | — | §49 |

### Wave 3 — IO Contracts & Data Flow (I210, I214, I218, I219) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.186 | [Code] G3: Consolidate dual `EngineInput`/`EngineOutput` | EKS `core/base.py` versions subclass `common.library.core.pipeline` versions. Add domain-specific fields. Delete standalone definitions; re-export. | Contracts | 🔷 PLANNED | I210 | — | `eks/engine/core/base.py`, `eks/engine/eks_engine_pipeline.py` | — | — | — | §49 |
| T1.99.187 | [Code] G7: Wire `HealthInput`/`HealthOutput` + `DiscoveryInput`/`DiscoveryOutput` into pipeline | Phase A: `DiscoveryInput` → `scanner.scan()` → `DiscoveryOutput`. Phase B: `HealthInput` → `scorer.score()` → `HealthOutput` for DB write. | Contracts | 🔷 PLANNED | I214 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/io_contracts.py` | ← T1.99.186 | — | — | §49 |
| T1.99.199 | [Code] G7b: Activate `score_from_input()` contract wrapper in `_process_file()` | Replace direct `self.scorer.score(doc, structural_elements=elements)` with `HealthInput(...)` → `self.scorer.score_from_input(health_input)` → `HealthOutput` consumption. Downstream code reads `hout.metadata` (full score dict) and `hout.overall` for backward compatibility. | Contracts | ✅ COMPLETE | I214 | TL011 | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/io_contracts.py` | ← T1.99.187 | TL011 | U204 | §49 |
| T1.99.188 | [Code] G11: Pass context-resolved paths into `ParserInput` defaults | Replace `ParserInput(config_file="", schema_dir="", output_dir="")` with `self.context.paths` values. Same for `DiscoveryInput`. | Data | 🔷 PLANNED | I218 | — | `eks/engine/pipeline_orchestrator.py` | ← T1.99.187 | — | — | §49 |
| T1.99.189 | [Code] G12: Write parsed content to `context.data.extracted_content` during execution | After successful parse, store `self.context.data.extracted_content[doc_id] = extraction_result`. Enables downstream reads without re-querying registry. | Data | 🔷 PLANNED | I219 | — | `eks/engine/pipeline_orchestrator.py` | ← T1.99.188 | — | — | §49 |

### Wave 4 — Folder Structure & Schema Wiring (I208, I220, I225) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.190 | [Code] G1+G13: Migrate to Appendix F domain subdirectory layout | Create 6 subdirectories: `engine/discovery/`, `engine/router/`, `engine/registry/`, `engine/revision/`, `engine/health/`, `engine/structure/`. Move `parser_router.py` from `engine/parsers/` to `engine/router/`. Project-wide grep for all import paths. 7 modules moved, ~30 files updated. | Structure | 🔷 PLANNED | I208, I220 | — | Multiple — see Depends On for scope | ← T1.99.182–189 | — | — | §49 |
| T1.99.191 | [Code] G18: Wire `SchemaToDDL` into bootstrap P4 for auto-DDL generation | Bootstrap P7 stores pre-generated DDL (documents_ddl, elements_ddl, indexes, doc_base_schema). DocumentRegistry accepts pre_generated_ddl param to skip schema re-load. _ensure_schema_version() tracks DDL hash in _eks_schema_meta table. runner.py + CLI tools pass DDL through. 4 new tests. 88/88 pass, no regressions. | Bootstrap | ✅ COMPLETE | I225 | — | `eks/engine/core/bootstrap.py`, `eks/engine/core/registry.py`, `eks/engine/pipeline_engine/runner.py`, `eks/engine/core/discovery_cli.py`, `eks/engine/core/health_cli.py` | — | TL013 | U206 | §49 |

### Wave 5 — Documentation & UI Contracts (I217, I222) — Nice-to-Have

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.192 | [Code] G10: Implement `DocumentSelectionContract` + `PipelineConfigContract` per Appendix F | Add contract schemas to `contracts.py`, wire `ContractManager` to validate before pipeline execution. Add `POST /api/v1/contracts/document-selection` and `POST /api/v1/contracts/pipeline-config` endpoints. | UI | 🔷 PLANNED | I217 | — | `eks/engine/core/contracts.py`, `eks/engine/core/contract_manager.py`, `eks/ui/backend/phase1_server.py` | ← T1.99.186–191 | — | — | §49 |
| T1.99.193 | [Docs] G15: Cross-audit Appendix E schema versions vs. actual `version` fields | Read `"version"` from all 23 schema files, compare against Appendix E E5.1 table. Update stale entries. Add validation script `eks/test/verify_appendix_e_versions.py`. | Docs | 🔷 PLANNED | I222 | — | `docs/appendix_e_schema_design.md`, `eks/test/verify_appendix_e_versions.py` | — | — | — | §49 |

### Wave 6 — Residual Cleanup & Contract Wiring (I211 residual, I214)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.198 | [Cleanup] Remove dead `HealthScorerFactory` and `StructureDetectorFactory` from `factories.py` | Audit revealed ParserFactory IS actively used by ParserRouter — retained. HealthScorerFactory and StructureDetectorFactory had zero instantiation sites. Both class definitions removed from factories.py. Dead `_engine_map` / `_parser_map` declarations also removed. Project-wide grep: zero remaining imports of removed classes. | Cleanup | ✅ COMPLETE | I211 (residual), I214 | TL011 | `eks/engine/core/factories.py` | ← T1.99.183 | TL011 | U204 | §49 |

---

## 23. `str(5)` Bug Fix — Restore Exception Messages Across All Error Paths (I226) Tasks

> Source: [§50](phase_1_foundation_workplan.md#50)

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.194 | [Fix] Fix `pipeline_orchestrator.py` — 5 instances | Replace all `str(5)` with `str(e)` in 3 except blocks. Verified each `e` in scope. | EKS workflow | ✅ COMPLETE | I226 | — | `eks/engine/pipeline_orchestrator.py` | — | — | — | §50 |
| T1.99.195 | [Fix] Fix `discovery_cli.py` — 1 instance | Replace `str(5)` with `str(e)` in DiscoveryEngineError ErrorRecord. | EKS workflow | ✅ COMPLETE | I226 | — | `eks/engine/core/discovery_cli.py` | ← T1.99.194 | — | — | §50 |
| T1.99.196 | [Fix] Fix `phase1_server.py` — 3 instances | L89 `_IMPORT_ERROR`, L525 `"detail"`, L666 `_job_state["error"]`. | EKS UI | ✅ COMPLETE | I226 | — | `eks/ui/backend/phase1_server.py` | ← T1.99.195 | — | — | §50 |
| T1.99.197 | [Fix] Fix `serve.py` — 4 instances | L404 ConnectionRefused check, L425 upstream err, L436 internal err, L481 Ollama err. | EKS UI | ✅ COMPLETE | I226 | — | `eks/serve.py` | ← T1.99.196 | — | — | §50 |

---

## 24. Scan Redundancy — Eliminate Phase B Re-Scan via DuckDB SSOT (I227) Tasks

> Source: I227 — Phase B re-scans entire directory tree despite Phase A having already written all file metadata to DuckDB.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.100 | [Code] Eliminate redundant Phase B filesystem scan — read file list from DuckDB | In `pipeline_orchestrator.py:run_phase_b()`, replace `self.scanner.scan(root_dir)` + `validate_file_types()` with `self.registry.list_documents(latest_only=False)` to read files already registered by Phase A. Map DuckDB columns (`file_path`, `file_type`) to the `file_info` dict expected by `_process_file()`. Preserve `self.scanner.scan()` as fallback if registry returns empty. See I227 resolution for detailed rationale. | I227 | ✅ COMPLETE | I227 | 2026-07-23 | `eks/engine/core/pipeline_orchestrator.py` | — | TL005 | U198 | §51 |
| T1.101 | [Testing] Add regression test — Phase B does not re-scan filesystem when DuckDB has data | Assert that `FileScanner.scan()` is NOT called during `run_phase_b()` when DuckDB has pre-populated rows from Phase A. Verify `registry.list_documents()` is called instead. Test fallback path when DB is empty. | I227 | ✅ COMPLETE | I227 | 2026-07-23 | `eks/test/test_phase1.py` | TL005 | — | U198 | §51 |

---

## 25. Phase B Telemetry — Batch-Level Checkpoints (I229) Tasks

> Source: I229 — Phase B emits per-file telemetry checkpoint for every document (7000+), overwhelming storage.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.102 | [Code] Replace per-file telemetry with batch-level checkpoints in `run_phase_b()` | In `pipeline_orchestrator.py:run_phase_b()`, replace the per-file `telemetry.track(...)` inside the `_process_file()` loop with a batch accumulator. Emit checkpoints at 25%/50%/75%/100% milestones using BATCH_MILESTONES + last_milestone_pct tracker. Keep per-file error logging via `self.error_manager.log_error()` — only progress telemetry becomes coarse. | EKS pipeline | ✅ COMPLETE | I229 | 2026-07-23 | `eks/engine/core/pipeline_orchestrator.py` | — | TL007 | U200 | §53 |
| T1.103 | [Testing] Add dedicated test — batch milestone firing count, order, and no-duplicate guard | **Scope updated (I235)**: Mock `_forward_telemetry` via `unittest.mock.patch`. (1) 4-file batch: assert exactly 5 `_forward_telemetry` calls (4 milestone + 1 end-of-phase "B" summary); assert milestone call order is strictly `25% → 50% → 75% → 100%`. (2) 1-file batch: assert 4 calls in same order with no duplicates. (3) 2-file batch: assert `75%` fires **before** `100%`, not after. Verifies both T1.102 logic and T1.116 ordering fix. Prerequisite: T1.116 must be applied before this test can pass. | EKS test | ✅ COMPLETE | I229, I235 | 2026-07-27 | `eks/test/test_phase1.py` | ← T1.116 | TL015 | U211 | §53 |

## 26. Cross-Phase Validation Gates (I230) Tasks

> Source: I230 — No cross-phase data consistency checks exist. Nothing verifies discovered_files non-empty before Phase B, or scored docs before Phase C.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.104 | [Code] Add `validate_phase_transition()` to `PipelineOrchestrator` | Method called at each A→B and B→C boundary. A→B gate checks registry has documents with file_path; B→C gate checks extraction_confidence scores exist. Returns `{"passed": bool, "warnings": list, "errors": list}`. Wired into `run_full_pipeline()` — non-blocking by default, results in summary["gates"]. | EKS pipeline | ✅ COMPLETE | I230 | 2026-07-23 | `eks/engine/core/pipeline_orchestrator.py` | — | TL007 | U200 | §54 |
| T1.105 | [Testing] Add test — phase transition gates catch empty states | Mock empty registry → assert A→B fails with clear error. Mock no scored docs → assert B→C fails. Verify happy path passes through. | EKS test | 🔷 PLANNED | I230 | — | `eks/test/test_phase1.py` | ← T1.104 | — | — | §54 |

## 27. Legacy `doc_id` Fallback Removal (I232) Tasks

> Source: I232 — `_update_doc_status()` has legacy filename-based fallback that diverges from `RevisionManager`-based `_process_file()` path.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.106 | [Code] Remove legacy filename-based fallback — resolve doc_id once at top of `_process_file()` via `registry.get_document_by_file_path()` | Added `registry.get_document_by_file_path()` for SSOT lookup. `_process_file()` resolves `doc`/`doc_id` once at entry, replaces stem-based fallback (removed L721-724). `_update_doc_status()` now requires `doc_id: str` — legacy path removed. Updated both call sites. Bumped pipeline_orchestrator.py rev 0.5, registry.py rev 0.7. | EKS pipeline | ✅ COMPLETE | I232 | 2026-07-23 | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/registry.py` | — | T1.107 | — | §51 |
| T1.107 | [Testing] 3 tests — file_path lookup found/not-found + synthetic key roundtrip proving stem divergence eliminated | `test_get_document_by_file_path_found`, `test_get_document_by_file_path_not_found`, `test_get_document_by_file_path_synthetic_key_roundtrip`. Full test suite 79/79 passes. | EKS test | ✅ COMPLETE | I232 | 2026-07-23 | `eks/test/test_phase1.py` | ← T1.106 | — | — | §51 |

## 28. Version SSOT (I231) Tasks

> Source: I231 — Three sources disagree: knowledge.json v2.6.0, `__init__.py` v1.4.0, `bootstrap.py` rev 0.3.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.108 | [Code] Declare single `__version__` in `eks/__init__.py`; all 8 subpackages import from `eks` | `eks/__init__.py` now canonical with `__version__ = "2.6.0"`. All 8 subpackage `__init__.py` files import `__version__` from `eks` instead of hardcoding. pyproject.toml and knowledge.json already at 2.6.0. Full test suite 291/305 pass (14 pre-existing rdflib env failures). | EKS pipeline | ✅ COMPLETE | I231 | 2026-07-23 | `eks/__init__.py`, `eks/engine/__init__.py`, `eks/engine/core/__init__.py`, `eks/engine/parsers/__init__.py`, `eks/config/schemas/__init__.py`, `eks/test/__init__.py`, `eks/ui/__init__.py`, `eks/ui/backend/__init__.py`, `eks/log/phase1/__init__.py` | — | TL008 | U201 | §55 |

## 29. Pipeline Entry-Point Monolith Split (I233) Tasks

> Source: I233 — `eks_engine_pipeline.py` is 1,284 lines mixing CLI parsing, pipeline orchestration, export helpers, and preload infrastructure in a single file. Per AGENTS.md §10 (SSOT) and §15 (Path Resolution), split into focused modules under `eks/engine/pipeline_engine/` following DCC `workflow/*_engine/` convention.

### Design Summary

| Aspect | Decision |
|--------|----------|
| Subfolder | `eks/engine/pipeline_engine/` (matches DCC `*_engine/` pattern) |
| Modules | `cli.py` (parsers), `runner.py` (preload/bootstrap/run), `exporter.py` (export helpers) |
| Module-level globals | **Zero** — `_PRJ_DIR`, `_THIS`, `_SCRIPT_DIR` removed from extracted modules; all paths flow from `main()` via `_preload_infrastructure()` returned `project_root` |
| Entry shell | `eks_engine_pipeline.py` ~50 lines — import-time sys.path bootstrap + `main()` + re-exports |
| Backward compat | All public functions re-exported; `pyproject.toml` console_scripts unchanged |

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.109 | [Code] Create `pipeline_engine/` with `cli.py`, `runner.py`, `exporter.py` | **`cli.py`**: Extract `build_parser()`, `_EKS_CORE_ARG_SPECS`, `build_schema_driven_parser(root, schema_config)` — `root` becomes **required** parameter (no `_PRJ_DIR` fallback), `parse_eks_cli()`, `_parse_early_verbosity()` — zero module-level globals. **`runner.py`**: Extract `_preload_infrastructure()` (imports `_parse_early_verbosity` from `cli.py`), `bootstrap_pipeline(project_root, ...)`, `run_pipeline(project_root, ...)`, `_read_system_params(config_dir)`, `_last_phase()`, `_print_human_summary()` — all paths received as explicit parameters, no `_PRJ_DIR`/`_THIS`/`_SCRIPT_DIR` module-level globals. **`exporter.py`**: Extract `resolve_export_columns(schema_dir)`, `_build_export_rows()`, `_build_flagged_rows()` — pure functions, zero pipeline dependencies. | EKS pipeline | ✅ COMPLETE | I233 | 2026-07-23 | `eks/engine/pipeline_engine/__init__.py`, `eks/engine/pipeline_engine/cli.py`, `eks/engine/pipeline_engine/runner.py`, `eks/engine/pipeline_engine/exporter.py` | — | TL009 | U202 | §56 |
| T1.110 | [Code] Rewrite `eks_engine_pipeline.py` as thin entry-point shell | Keep: import-time sys.path bootstrap (`_stdlib_find_repo_root()` + `sys.path.insert`), `main()` with folder literals declared locally, `__main__` guard. Add: re-exports of `bootstrap_pipeline`, `run_pipeline`, `build_parser`, `parse_eks_cli`, `resolve_export_columns` from `pipeline_engine/` modules. Remove: all extracted function bodies, `_PRJ_DIR` module-level global reassignment (L128-135, now done inside `_preload_infrastructure()`), `_THIS`/`_SCRIPT_DIR` sys.path cleanup (moved into `main()`). `main()` must discover project root via `infra["project_root"]` returned by `_preload_infrastructure()` and pass explicitly to all downstream calls — no fallback to `_PRJ_DIR`. | EKS pipeline | ✅ COMPLETE | I233 | 2026-07-23 | `eks/engine/eks_engine_pipeline.py` | ← T1.109 | TL009 | U202 | §56 |
| T1.111 | [Testing] Verify backward compatibility and full test suite | Full regression suite: `python -m pytest eks/test/` → must pass 291/305 (14 pre-existing rdflib failures unchanged). Verify all 4 public functions importable from `eks.engine.eks_engine_pipeline`. Verify `pyproject.toml` console_scripts entry `eks-pipeline = eks.engine.eks_engine_pipeline:main` resolves correctly. | EKS test | ✅ COMPLETE | I233 | 2026-07-23 | `eks/test/test_eks_engine_pipeline.py`, `eks/test/test_phase1.py` | ← T1.109, T1.110 | TL009 | U202 | §56 |

---

## 30. CLI Default Pipeline Output — pipeline_output.json + Default-On CSV/Excel Export (I234) Tasks

> Source: I234 — CLI pipeline generates zero output files by default. `pipeline_output.json` is server-only; `--export` defaults to `none`; no `debug_log.json` in CLI path. Per §25.1, write-only files use single-overwrite pattern.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| T1.112 | [Code] Write `pipeline_output.json` to CLI `main()` after pipeline completes | After `run_pipeline()` returns, build a human-readable summary dict (job_id, timestamp, status, summary, exported_files) and write to `output/pipeline_output.json` (single-overwrite). Pattern matches `phase1_server.py:635`. | EKS CLI | ✅ COMPLETE | I234 | — | `eks/engine/eks_engine_pipeline.py` | — | — | U207 | §57 |
| T1.113 | [Schema/Code] Schema-driven `--export` default — register in config, CLI reads at runtime | [Schema] Added `export_default` to `system_parameters_def` in `eks_base_schema.json` with `"enum": ["csv", "xlsx", "both", "none"], "default": "both"`. Added `"export_default": "both"` to `eks_config.json`. [Code] Removed hardcoded `default="none"` from `_EKS_CORE_ARG_SPECS` and `build_parser()` — uses `None`; `main()` resolves from `mgr.effective_parameters.get("export_default", "both")` at runtime. Per §16 hardcoded fallback removal. | EKS CLI + Schema | ✅ COMPLETE | I234 | — | `eks/config/schemas/eks_base_schema.json`, `eks/config/schemas/eks_config.json`, `eks/engine/pipeline_engine/cli.py`, `eks/engine/eks_engine_pipeline.py` | — | — | U207 | §57 |
| T1.114 | [Code] Write `debug_log.json` from CLI `main()` | After pipeline completes, serialize `logger.debug_object` to `output/debug_log.json` (single-overwrite). Replaces the per-run `debug_log` pattern removed in U180. | EKS CLI | ✅ COMPLETE | I234 | — | `eks/engine/eks_engine_pipeline.py` | ← T1.112 | — | U207 | §57 |
| T1.115 | [Testing] Verify CLI generates 5 output files by default | Run `main()` with default args (no `--export` flag). Assert `output/pipeline_output.json`, `output/debug_log.json`, `output/discovery_inventory.csv`, `output/extraction_results.csv`, `output/review_flags.csv` exist and are non-empty. | EKS test | ✅ COMPLETE | I234 | — | `eks/test/` | ← T1.112–114 | — | U207 | §57 |

---

## 31. Batch Telemetry Logic Order Fix (I235) Tasks

> Source: I235 — In `run_phase_b()` (`pipeline_orchestrator.py` lines 395–408), the `pct >= 1.0` block fires the 100% checkpoint BEFORE the `BATCH_MILESTONES` loop executes. For small batches (total ≤ 3), intermediate milestones (25%/50%/75%) fire after 100% in the wrong order — up to 4 redundant out-of-order checkpoints on the final file. `last_milestone_pct` is also never updated to `1.0` after the 100% block, leaving the tracker stale. Discovered during I229 code evaluation 2026-07-24.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.116 | [Code] Fix milestone ordering — fold `1.0` into `BATCH_MILESTONES`, remove separate `pct >= 1.0` block | **Root cause**: `BATCH_MILESTONES = {0.25, 0.50, 0.75}` — the 100% checkpoint is emitted in a separate `if pct >= 1.0:` block (line 397) that runs before the sorted milestone loop, so for batches where the last file jumps straight to 100%, all uncrossed intermediate milestones fire after 100%. **Fix (3 changes to `pipeline_orchestrator.py`)**: (1) Change line 365: `BATCH_MILESTONES = {0.25, 0.50, 0.75, 1.0}`. (2) Remove lines 397–401 (`if pct >= 1.0:` block) entirely. (3) Inside the sorted loop (line 402–408), update label: `"milestone": "100%" if m == 1.0 else f"{int(m*100)}%"` and `"files": idx + 1`. `last_milestone_pct` is now set to `1.0` inside the loop on the last milestone — no stale tracker. Zero change to per-file `ErrorManager` logging or end-of-phase `_forward_telemetry("B", ...)`. | `eks/engine/core/pipeline_orchestrator.py` | ✅ COMPLETE | I235 | 2026-07-27 | `eks/engine/core/pipeline_orchestrator.py` | — | T1.103, T1.117 | U211 | §58 |
| T1.117 | [Testing] Run full test suite after T1.116 and implement T1.103 milestone-order assertions | After applying T1.116: (1) Run `python -m pytest eks/test/ -v` — assert suite passes at same baseline (291/305; 14 pre-existing rdflib failures unchanged). (2) Confirm `test_phase_b_reads_from_registry_instead_of_rescan` and `test_phase_b_falls_back_to_scan_when_registry_empty` still pass (I227 regression guard). (3) Implement T1.103 three-case assertions (4-file, 1-file, 2-file batches). All three T1.103 assertions must be green before I235 can be closed. | EKS test | ✅ COMPLETE | I235 | 2026-07-27 | `eks/test/test_phase1.py` | ← T1.116 | T1.103 | U211 | §58 |

---

## 32. ERROR_FILE_PROCESSING Kwarg Mismatch Fix (I236) Tasks

> Source: I236 — In `run_phase_b()` (`pipeline_orchestrator.py` line 378), `mm.show("ERROR_FILE_PROCESSING", filename=file_path, error=str(e))` passes kwarg key `error` but the `eks_message_config.json` template `"Error processing {filename}: {detail}"` expects `detail`. `BaseMessageManager.show()` catches the `KeyError` silently and falls back to the raw template string — every file-processing error prints `"Error processing <path>: {detail}"` literally. Level=0 means this broken output fires at all verbosity levels. Discovered during messaging audit 2026-07-24.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.118 | [Code] Fix `ERROR_FILE_PROCESSING` kwarg — rename `error=` to `detail=` at call site | **Option A (preferred — fix call site, keep template)**: Change `pipeline_orchestrator.py` line 378 from `mm.show("ERROR_FILE_PROCESSING", filename=file_path, error=str(e))` to `mm.show("ERROR_FILE_PROCESSING", filename=file_path, detail=str(e))`. Template `"Error processing {filename}: {detail}"` already correct — only the call-site kwarg key is wrong. **Do NOT change the template** (it is the SSOT in the schema). Grep project-wide for all `mm.show("ERROR_FILE_PROCESSING"` call sites to confirm this is the only occurrence before closing. Verify no other `show()` calls pass `error=` where a different placeholder is expected. | `eks/engine/core/pipeline_orchestrator.py` line 378, `eks/config/schemas/eks_message_config.json` | ✅ COMPLETE | I236 | 2026-07-27 | `eks/engine/core/pipeline_orchestrator.py` | — | T1.119 | U212 | §59 |
| T1.119 | [Testing] Add test asserting `ERROR_FILE_PROCESSING` emits actual exception message, not raw template literal | Mock `MessageManager.show()` via `unittest.mock.patch` on `_forward_telemetry` path, or directly instrument `mm.get("ERROR_FILE_PROCESSING", filename=..., detail=str(e))` and assert the returned string **contains the actual exception text** and **does not contain the literal substring `"{detail}"`**. Use a test orchestrator with a forced `_process_file()` failure (e.g., mock raises `RuntimeError("test error")`). Assert the resulting message string equals `"Error processing <path>: test error"`. Run full suite — assert 291/305 baseline unchanged. | EKS test | ✅ COMPLETE | I236 | 2026-07-27 | `eks/test/test_t132_modules.py` | ← T1.118 | — | U212 | §59 |

---
## 33. Schema-Driven Telemetry Verbosity (I237) Tasks

> Source: I237 — `TelemetryHeartbeat` created with `verbose=False` (hardcoded literal at `pipeline_orchestrator.py:135`). `add_checkpoint()` only prints via `if self.verbose` guard (`heartbeat.py:268`). No `telemetry` or `verbose` key exists in any EKS schema/config JSON — violates §15 (SSOT) and §16 (hardcoded fallback removal). Resolution: add `telemetry_verbose` to `system_parameters` schema chain, pass through bootstrap → PipelineOrchestrator → TelemetryHeartbeat, default `true` so 25/50/75/100% milestones visible at default `--level 1`.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.120 | [Schema] Add `telemetry_verbose` to `system_parameters_def` in `eks_base_schema.json` | Add property: `"telemetry_verbose": { "type": "boolean", "default": true, "description": "Emit milestone checkpoints (25/50/75/100%) to console during Phase B (I237)" }`. Add to `required` array. Increment base schema version to 1.11.0. | `eks/config/schemas/eks_base_schema.json` | ✅ COMPLETE | I237 | 2026-07-27 | `eks/config/schemas/eks_base_schema.json` | — | T1.121 | U214 | §60 |
| T1.121 | [Config] Add `telemetry_verbose: true` to `eks_config.json` `system_parameters` | Add `"telemetry_verbose": true` to the `system_parameters` object. Increment config version to 1.9.0. | `eks/config/schemas/eks_config.json` | ✅ COMPLETE | I237 | 2026-07-27 | `eks/config/schemas/eks_config.json` | ← T1.120 | T1.122 | U214 | §60 |
| T1.122 | [Code] Pass `telemetry_verbose` through bootstrap → runner → PipelineOrchestrator → TelemetryHeartbeat | (a) `pipeline_orchestrator.py`: added `telemetry_verbose: bool = True` param to `__init__`, passed to `TelemetryHeartbeat(verbose=telemetry_verbose)`. (b) `runner.py`: both call sites (context and non-context paths) extract from config and pass as kwarg. (c) `discovery_cli.py`: same extraction pattern. | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/pipeline_engine/runner.py`, `eks/engine/core/discovery_cli.py` | ✅ COMPLETE | I237 | 2026-07-27 | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/pipeline_engine/runner.py`, `eks/engine/core/discovery_cli.py` | ← T1.121 | T1.123 | U214 | §60 |
| T1.123 | [Testing] Add test verifying milestone `[TELEMETRY]` prints when `telemetry_verbose=True` and suppresses when `False` | Added 2 tests in `test_phase1.py`: `test_telemetry_verbose_true_prints_milestones` (patches `builtins.print`, captures `[TELEMETRY]` output, asserts `B-progress` checkpoint appears) and `test_telemetry_verbose_false_suppresses_milestones` (patches `builtins.print`, asserts zero `[TELEMETRY]` lines). Both pass alongside 3 existing I235 milestone-order tests. Full suite: 321/321 pass. | EKS test | ✅ COMPLETE | I237 | 2026-07-27 | `eks/test/test_phase1.py` | ← T1.122 | — | U214 | §60 |

---

## 34. Phase A Batch Milestones (I238) Tasks

> Source: I238 — Phase A `register_placeholders()` emits `logger.status("Document {doc_id} registered successfully.")` once per document via `registry.register_document()` (registry.py:629). For 42 registrations in a real run, this produces 42 STATUS-level lines at default `--level 1` — flooding the CLI. Phase B solved the same problem via 4 batch milestones (25/50/75/100%) at STATUS level with per-file details at INFO only. Resolution: downgrade per-document STATUS to INFO; add batch milestone progress in the registration loop matching Phase B pattern; add regression tests.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.124 | [Code] Downgrade per-document STATUS to INFO in `registry.register_document()` | Change `registry.py:629` from `self.logger.status(f"Document {doc_id} registered successfully.")` to `self.logger.info(...)`. Per-document messages move to level 2+ (visible with `--debug` or `--level 2`). | `eks/engine/core/registry.py` | ✅ COMPLETE | I238 | 2026-07-27 | `eks/engine/core/registry.py` | — | T1.126 | U215 | §61 |
| T1.125 | [Code] Add batch milestone progress in `register_placeholders()` loop | In `file_scanner.py:register_placeholders()`, after each document is registered, compute `pct = count / total` and emit `logger.status(f"[TELEMETRY] A-registration: milestone={int(m*100)}% files={files}")` at 25%/50%/75%/100% thresholds (same `BATCH_MILESTONES = {0.25, 0.50, 0.75, 1.0}` pattern as Phase B). Track `last_milestone_pct` to avoid duplicates. Final `"Registered N new..."` summary at loop end retained at STATUS. | `eks/engine/core/file_scanner.py` | ✅ COMPLETE | I238 | 2026-07-27 | `eks/engine/core/file_scanner.py` | ← T1.124 | T1.126 | U215 | §61 |
| T1.126 | [Testing] Add regression tests for Phase A milestone behavior | 2 tests in `test_phase1.py`: `test_phase_a_batch_milestones_emitted` — mock registry, call register_placeholders() with 8 files, assert `[TELEMETRY] A-registration` appears at 25%/50%/75%/100%. `test_phase_a_per_document_info_not_status` — register document, assert `registered successfully` appears at INFO but not STATUS. | EKS test | ✅ COMPLETE | I238 | 2026-07-27 | `eks/test/test_phase1.py` | ← T1.124, T1.125 | — | U215 | §61 |

---

## 35. ERROR_FILE_PROCESSING Level Fix (I242) Tasks

> Source: I242 — `eks_message_config.json` defines `ERROR_FILE_PROCESSING` with `"level": 0`, firing at ALL verbosity levels including silent `--level 0`. With 738/753 Phase B file failures, this produces ~740 visible error lines at default `--level 1`. Resolution: change level to 1 (fires at `--level 1+`, silent at `--level 0`).

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.127 | [Config] Change ERROR_FILE_PROCESSING level from 0 to 1 in `eks_message_config.json` | Change `"level": 0` to `"level": 1` for the `ERROR_FILE_PROCESSING` message entry. Error messages now show at default `--level 1` but are suppressed in silent `--level 0` mode. | `eks/config/schemas/eks_message_config.json` | ✅ COMPLETE | I242 | 2026-07-27 | `eks/config/schemas/eks_message_config.json` | — | T1.128 | — | §62 |
| T1.128 | [Testing] Add test verifying ERROR_FILE_PROCESSING suppressed at --level 0 | Add test that creates a MessageManager with verbosity=0, calls get("ERROR_FILE_PROCESSING", ...), and asserts None is returned. | EKS test | ✅ COMPLETE | I242 | 2026-07-27 | `eks/test/test_t132_modules.py` | ← T1.127 | — | — | §62 |
| T1.131 | [Code] Escalate ERROR_FILE_PROCESSING level 1→2; replace bare logger.error() with MessageManager | Change level from 1 to 2 in `eks_message_config.json`. Replace bare `logger.error()` at `pipeline_orchestrator.py:916` with `message_manager.show("ERROR_FILE_PROCESSING")` so it routes through MessageManager level gate. | `eks/config/schemas/eks_message_config.json`, `eks/engine/core/pipeline_orchestrator.py` | ✅ COMPLETE | I242 | 2026-07-27 | `eks/config/schemas/eks_message_config.json`, `eks/engine/core/pipeline_orchestrator.py` | ← T1.127 | T1.134 | TL005 | §62 |

## 36. STATUS_PHASE_B_COMPLETE Kwarg Fix (I243) Tasks

> Source: I243 — `STATUS_PHASE_B_COMPLETE` template `"{success}/{total} success, {partial} partial, {failed} failed"` has `{total}` placeholder but call site at `pipeline_orchestrator.py:437` passes `success=, partial=, failed=` but NOT `total=`. `KeyError` is caught silently in `BaseMessageManager.show()` — all 4 placeholders appear literally: `"✓ Phase B complete — {success}/{total} success, ..."`. Same bug pattern as I236.

### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.129 | [Code] Add `total=` kwarg to STATUS_PHASE_B_COMPLETE call site | In `pipeline_orchestrator.py:437`, change `show("STATUS_PHASE_B_COMPLETE", success=success, partial=partial, failed=failed)` to include `total=total`. | `eks/engine/core/pipeline_orchestrator.py` | ✅ COMPLETE | I243 | 2026-07-27 | `eks/engine/core/pipeline_orchestrator.py` | — | T1.130 | — | §63 |
| T1.130 | [Testing] Add test verifying STATUS_PHASE_B_COMPLETE hydrates correctly | Add test that gets STATUS_PHASE_B_COMPLETE with success=15, total=753, partial=0, failed=738, and asserts no literal placeholders remain. | EKS test | ✅ COMPLETE | I243 | 2026-07-27 | `eks/test/test_t132_modules.py` | ← T1.129 | — | — | §63 |

## 37. Default-Level Verbosity Noise (I244) — Tasks

> Source: I244 — Post-I242 noise audit identified 4 per-document `logger.info()` sites at level 1 (`file_scanner.py:222`, `registry.py:444,483,799`), 3 error codes with severity WARNING that route to `logger.info()` (not `logger.warning()`) via `handle_data_error()`, and MessageManager verbosity hardcoded to 1. Tasks T1.132–T1.133 completed during initial audit; remaining work tracked in T1.135–T1.137.

> **Status**: 🔶 Partial — 2 tasks complete, 3 pending. See [Issue Log §52](../../issue_log.md#52--default-level-verbosity-noise-audit-i244).

### Completed Tasks

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.132 | [Code] Downgrade 4 per-document logger.info()→logger.debug() | Change `logger.info()` to `logger.debug()` at `file_scanner.py:222` (Content unchanged — skipping) and `registry.py:444` (Stored {n} elements), `registry.py:483` (Deleted {n} elements), `registry.py:799` (Updated status for {doc_id}). | `eks/engine/core/file_scanner.py`, `eks/engine/core/registry.py` | ✅ COMPLETE | I244 | 2026-07-27 | `eks/engine/core/file_scanner.py`, `eks/engine/core/registry.py` | — | — | TL005 | §64 |
| T1.133 | [Config] Change S-R-S-0409 severity FATAL→HIGH, stops_pipeline true→false | Per-file system errors should not halt the pipeline. Change `severity` from `FATAL` to `HIGH` and `stops_pipeline` from `true` to `false` in `eks_error_config.json`. | `eks/config/schemas/eks_error_config.json` | ✅ COMPLETE | I244 | 2026-07-27 | `eks/config/schemas/eks_error_config.json` | — | — | TL005 | §64 |

### §64 — Default-Level Verbosity Noise — ✅ ALL RESOLVED (I244)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.134 | [Testing] Add test for ERROR_FILE_PROCESSING suppressed at default --level 1 | Add test that creates MessageManager with verbosity=1, calls get("ERROR_FILE_PROCESSING", ...), and asserts None is returned (level 2 suppressed at default verbosity 1). | EKS test | 🔴 Open | I242 | 2026-07-27 | — | ← T1.131 | — | — | §62 |
| T1.135 | [Config] Bump P3-E-E-0018, P3-E-E-0019, P5-R-P-0003 severity to HIGH | Change severity WARNING→HIGH for these 3 error codes so `handle_data_error()` routes through `logger.warning()` (level 2) instead of `logger.info()` (level 1). | `eks/config/schemas/eks_error_config.json` | ✅ COMPLETE | I244 | — | — | — | — | — | §64 |
| T1.136 | [Code] Reconcile MessageManager verbosity after bootstrap | Add `mm.set_verbosity(level)` call after level reconcile in `eks_engine_pipeline.py::main()`. Also add `logger.set_level(level)` for logger consistency. | `eks/engine/eks_engine_pipeline.py` | ✅ COMPLETE | I244 | — | — | — | — | — | §64 |
| T1.137 | [Code] file_scanner.py:222 info→debug | Change per-document `logger.info("Content unchanged — skipping")` to `logger.debug()` so it's suppressed at default --level 1. | `eks/engine/core/file_scanner.py` | ✅ COMPLETE | I244 | — | — | — | — | — | §64 |
| T1.138 | [Code] Fix UniversalLogger._log() record-before-gate | Reorder `_log()` to append to `debug_object["logs"]` before the level gate, so all entries are saved regardless of verbosity. | `common/library/core/logging/logger.py` | ✅ COMPLETE | I244 | — | — | — | — | — | §64 |

### §65 — Error Code Standardization to X-X-X-XXXX (I112)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.139 | [Testing] Verify DuckDB-first path + close I227 | Run full pipeline against TWRP data; confirm Phase B reads from registry via `list_documents()`, not from filesystem `scan()`. Update I227 → ✅ Resolved. | EKS test | ✅ COMPLETE | I227 | — | — | — | — | — | §65 |
| T1.140 | [Schema] Migrate 6 `P1-BOOT-*` → `S-B-S-0603`–`S-B-S-0608` | Replace codes in `eks_error_config.json`. Update `system_error_ranges`: remove `bootstrap_p1`, merge into existing `bootstrap` range (start 0601, end 0608). | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | — | — | — | §65 |
| T1.141 | [Schema] Migrate 7 `P1-SETUP-*` → existing `S-E`/`S-F`/`S-R` ranges | Absorb by category: 3× F→`S-F-S-0207/0208/0209`, 1× D→`S-E-S-0106`, 1× O→`S-F-S-0210`, 1× E→`S-E-S-0107`, 1× READINESS→`S-R-S-0410`. Remove `setup_validation` range. | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | T1.140 | — | — | §65 |
| T1.142 | [Schema] Migrate 15 `B-*` → `B-{cat}-S-{id4}` with single-letter categories | Map CLI→C, PATH→H, REG→R, DEF→D, FALL→A, ENV→E, SCH→K, PAR→M, BOOT→B, CTX→X, UNK→U. Update codes and sequential IDs. | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | T1.140 | — | — | §65 |
| T1.143 | [Schema] Update `system_format` metadata + remove hybrid ranges | Remove `P1-SETUP-{type}{id}` and `P1-BOOT-{reason}` from `system_format`. Remove `setup_validation` and `bootstrap_p1` ranges. | Config | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_config.json` | T1.140–T1.142 | — | — | §65 |
| T1.144 | [Schema] Update `eks_error_setup_schema.json` ranges | Remove `setup_validation` and `bootstrap_p1` from `system_error_ranges.properties`. | Schema | ✅ COMPLETE | I112 | — | `eks/config/schemas/eks_error_setup_schema.json` | T1.143 | — | — | §65 |
| T1.145 | [Code] Update EKS call sites with new codes | Update `bootstrap.py` (40× `P1-BOOT-*` → `S-B-S-06xx`). Update `setup_validator.py` (18× `P1-SETUP-*` → `S-E`/`S-F`/`S-R`). | Code | ✅ COMPLETE | I112 | — | `eks/engine/core/bootstrap.py`, `eks/engine/core/setup_validator.py` | T1.140–T1.144 | — | — | §65 |
| T1.146 | [Docs] Update Appendix D — remove hybrid formats, document new codes | Remove `P1-SETUP-{type}{id}` and `P1-BOOT-{reason}` from D2 format table. Update D3/D4 ranges. | Docs | ✅ COMPLETE | I112 | — | `eks/workplan/appendix_d_pipeline_messages_errors.md` | T1.145 | — | — | §65 |
| T1.147 | [Testing] Full suite + grep for stale non-standard code references | Run project-wide grep for `P1-BOOT` and `P1-SETUP` — zero matches. Verify tests pass. | Test | ✅ COMPLETE | I112 | — | — | T1.145–T1.146 | — | — | §65 |

### §66 — Pipeline Batch Health Scoring (I248)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.148 | [Code] Wire `score_batch()` into `run_phase_b()` | After processing loop in `run_phase_b()`, query `registry.list_documents()` and call `self.scorer.score_batch(all_docs)`. Append `avg_document_health` and full `batch_health` dict to Phase B summary. Wrap in try/except with logger.warning on failure. | `eks/engine/core/pipeline_orchestrator.py` | ✅ COMPLETE | I248 | — | `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §66 |

### §67 — Document Type Schema Extraction (I250)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.149 | [Schema] Extract document type registry to standalone schema | Follow facility/discipline/department pattern. Add `document_type_entry_def` to `eks_doc_base_schema.json`. Create `eks_document_type_schema.json` with 15 valid codes plus metadata (label, ontology_class, description, expected_file_types). Update `eks_doc_setup_schema.json` to validate against new definition. | Config + Schema | ✅ COMPLETE | I250 | — | `eks/config/schemas/eks_doc_base_schema.json`, `eks/config/schemas/eks_document_type_schema.json`, `eks/config/schemas/eks_doc_config.json`, `eks/config/schemas/eks_doc_setup_schema.json` | — | — | — | §67 |

### §68 — Document Type Schema Pipeline Wiring (I251)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.150 | [Schema] Register `eks_document_type_schema.json` in SchemaLoader load chain | Add the new schema file to `SchemaLoader.load_all()` so `$ref` resolution works. Register with `Registry().with_resources()`. | Schema | ✅ COMPLETE | I251 | — | `eks/engine/core/schema_loader.py` | T1.149 | — | — | §68 |
| T1.151 | [Config] Update `eks_doc_setup_schema.json` to `$ref` new definition | Replace inline item properties with `$ref` to `document_type_entry_def` from the base schema. | Config | ✅ COMPLETE | I251 | — | `eks/config/schemas/eks_doc_setup_schema.json` | T1.149 | — | — | §68 |
| T1.152 | [Code] Update FilenameParser `_doc_type_codes` to use schema-sourced registry | Currently `_doc_type_codes` is built from the inline config array. After I250, this will come from schema `$ref`. Ensure `FilenameParser._precompile_validators()` reads from the schema-resolved config. | Code | ✅ COMPLETE | I251 | — | `eks/engine/core/filename_parser.py` | T1.150–T1.151 | — | — | §68 |

### §69 — Phase B Identity Field Write-Back (I252)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.153 | [Code] Extract project_number, area, discipline, document_type from PDF parser metadata in Phase B | PDFParser returns `parse_result["metadata"]` which may contain cover sheet fields. Extract identity fields from this dict and pass them to `_update_doc_status()` via `extra_properties`. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §69 |
| T1.154 | [Code] Add identity fields to `_update_doc_status()` extra_properties pass-through | Ensure `project_number`, `area`, `discipline`, `document_type` are included in the `extra_properties` dict passed to `registry.update_document_status()`. Verify COLUMN_ALLOWLIST in registry.py includes these four fields. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/registry.py` | T1.153 | — | — | §69 |
| T1.155 | [Code] Add `document_type` priority chain: cover sheet > filename > extension inference | `_infer_doc_type()` previously unconditionally overrode filename-derived document_type. Made conditional. Phase B write-back uses priority: parser metadata > Phase A filename value > UNKNOWN. | Code | ✅ COMPLETE | I252 | — | `eks/engine/core/pipeline_orchestrator.py`, `eks/engine/core/file_scanner.py` | T1.153–T1.154 | — | — | §69 |

### §70 — Path Doubling Fix (I254)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.156 | [Fix] Strip `eks_root` prefix from relative CLI `--data-dir` in bootstrap path resolution | In `bootstrap.py:_bootstrap_params()` line 488, before combining `self.project_root / eks_root / cli_path`, strip the `eks_root` prefix from `cli_path` if present. E.g., `"eks/data"` → strip `"eks/"` → `"data"` → resolves to `.../eks/data` (correct). Absolute paths unchanged. 3 regression tests added (test_path_doubling_prevents_eks_eks_data_dir, test_path_doubling_handles_bare_data, test_path_doubling_handles_absolute_path). bootstrap.py rev 0.4→0.5. | Code | ✅ COMPLETE | I254 | TL019 | `eks/engine/core/bootstrap.py` | — | — | — | §70 |

### §71 — FilenameParser Auto-Pattern Detection (I255)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.157 | [Code] Make FilenameParser auto-detect project code pattern per filename — try all registered project codes, use first match, fall back to `"*"` (0 segments) | Removed `project_code` param from `FilenameParser.__init__()`. Added `project_code_registry: Optional[List[str]]` param. New `_detect_pattern(stem)` method: splits stem by common separator, iterates all registered codes, checks first segment against each code — uses matching pattern or returns `"*"` fallback. Called per-filename in `parse()`. Both call sites updated: `FileScanner` and `PipelineOrchestrator` derive `project_code_registry` from `filename_patterns` keys (excluding `"*"`). Also fixed pre-existing finalization bug in `parse()` where 0-segment `"*"` pattern resulted in `parse_status="ok"` instead of `"unresolvable"`. `filename_parser.py` rev 1.0.0→1.1.0, `file_scanner.py` rev 1.5.0→1.6.0, `pipeline_orchestrator.py` rev 0.7→0.8. | Code | ✅ COMPLETE | I255 | TL020 | `eks/engine/core/filename_parser.py`, `eks/engine/core/file_scanner.py`, `eks/engine/core/pipeline_orchestrator.py` | — | — | — | §71 |
| T1.158 | [Testing] Add regression tests for FilenameParser auto-pattern-detection: matching pattern case, non-matching pattern → `"*"` fallback | Added 2 tests in `eks/test/test_phase1.py`: (1) `test_filename_parser_auto_detects_131101_pattern` — supply `project_code_registry=["131101"]`, parse `"131101-AREA-SPC-CV-0001_rev01.pdf"`, assert `project_number="131101"`, `area="AREA"`, `document_type="SPC"`, `discipline="CV"`, `sequence_number="0001"`, `document_number="131101-AREA-SPC-CV-0001"`, `revision="01"`, `parse_status="ok"`. (2) `test_filename_parser_falls_back_to_star_pattern` — parse `"random_name.pdf"`, assert all 5 identity fields are `None`, `document_number="random_name"` (full_stem fallback), `revision="00"`, `parse_status="unresolvable"`. Both pass. | Testing | ✅ COMPLETE | I255 | TL020 | `eks/test/test_phase1.py` | T1.157 | — | — | §71 |

### §72 — project_title Population from project_number (I256)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.159 | [Schema] Register eks_project_code_schema.json in SchemaLoader._STEM_TO_ATTR | Option A implemented: Added `"eks_project_code_schema": "project_code_schema"` to `_STEM_TO_ATTR` in `schema_loader.py`. Added `self.project_code_schema` attribute. In post-load, injects `project_code_titles` dict into `doc_config` from `projects[].code→description`. Updated `eks_doc_setup_schema.json` `additionalProperties` to allow `project_code_titles`. | Schema | ✅ COMPLETE | I256 | U223 | `eks/engine/core/schema_loader.py`, `eks/config/schemas/eks_doc_setup_schema.json` | — | TL021 | U223 | §72 |
| T1.160 | [Code] Accept project_code→title mapping in FilenameParser; populate project_title in FilenameParseResult when project_number extracted | Added `project_title: Optional[str]` to `FilenameParseResult`. Added to `to_metadata_dict()`. Added `project_code_titles: Optional[Dict[str, str]]` to `__init__`. In `_extract_segments()`, after `setattr(result, "project_number", raw_value)`, looks up title from map. Call sites (`FileScanner`, `PipelineOrchestrator`) pass `project_code_titles` from `doc_config`. `parse_filename()` wrapper updated. | Code | ✅ COMPLETE | I256 | U224, U225, U226 | `eks/engine/core/filename_parser.py`, `eks/engine/core/file_scanner.py`, `eks/engine/core/pipeline_orchestrator.py` | T1.159 | TL021 | U224–U226 | §72 |
| T1.161 | [Code] Extend I252 Phase B identity write-back to include cover-sheet-derived project_title | Extended I252 block with 3-tier `project_title` priority: (1) cover sheet metadata → (2) code→title lookup from `project_code_titles` → (3) Phase A existing value. Added after existing `for id_field in ...` loop. | Code | ✅ COMPLETE | I256 | U226 | `eks/engine/core/pipeline_orchestrator.py` | T1.159 | — | U226 | §72 |
| T1.162 | [Testing] Add regression test: filename with known project_code → project_title populated correctly | Added `test_filename_parser_populates_project_title` in `test_phase1.py`. Three sub-tests: (1) `131101`→`WSD11 — Project Specifications`, (2) `999999`→`Unknown Project`, (3) fallback→`None`. All pass. | Testing | ✅ COMPLETE | I256 | U227 | `eks/test/test_phase1.py` | T1.160 | TL021 | U227 | §72 |

### §73 — Silent doc_config Validation Failure (I257)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.163 | [Code] Replace silent `except Exception: pass` with logged exception in `_bootstrap_registry()` using S-B-S-0609 | In `bootstrap.py:305`, change `except Exception: pass` to `except Exception as exc:` with `self._log(f"doc_config schema validation failed — using empty defaults: {exc}", level=2)`. Error code `S-B-S-0609` `BOOT_CONFIG_DEGRADED` (WARNING, `stops_pipeline: false`). Fail-fast does NOT apply — inner try/except is intentionally non-fatal; outer P3 handler catches fatal errors. Pipeline continues with `doc_config = {}`. | Code | ✅ COMPLETE | I257 | U228 | `eks/engine/core/bootstrap.py`, `eks/config/schemas/eks_error_config.json` | T1.165 | TL022 | U228 | §73 |
| T1.164 | [Testing] Add test verifying doc_config load failure produces WARNING entry with S-B-S-0609 | Add test case that injects a broken schema/config pair into a `SchemaLoader` instance, triggers `_bootstrap_registry()` path, and asserts `debug_object["logs"]` contains a WARNING-level entry mentioning the schema error and code S-B-S-0609. Implemented as `TestBootstrapDegradation.test_257_doc_config_failure_logged`. | Testing | ✅ COMPLETE | I257 | U228 | `eks/test/test_phase1.py` | T1.163 | TL022 | U228 | §73 |

### §74 — Six Remaining Silent Bootstrap Swallows (I258)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.165 | [Schema] Register 7 new error codes S-B-S-0609–S-B-S-0615 in eks_error_config.json (I257 + I258) | All WARNING severity, `stops_pipeline: false`. **S-B-S-0609** `BOOT_CONFIG_DEGRADED` — P3 doc_config validation failed (I257). **S-B-S-0610** `BOOT_CONFIGREGISTRY_FAILED` — ConfigRegistry init failed (I258#1). **S-B-S-0611** `BOOT_SCCONFIG_DEGRADED` — P7 doc_config load failed (I258#2). **S-B-S-0612** `BOOT_ERRORMGR_TODICT_FAILED` — ErrorManager in `to_dict()` (I258#3). **S-B-S-0613** `BOOT_MSGMGR_TODICT_FAILED` — MessageManager in `to_dict()` (I258#4). **S-B-S-0614** `BOOT_ERRORMGR_CTX_FAILED` — ErrorManager in `to_pipeline_context()` (I258#5). **S-B-S-0615** `BOOT_MSGMGR_CTX_FAILED` — MessageManager in `to_pipeline_context()` (I258#6). Update bootstrap range: end_id `S-B-S-0608`→`S-B-S-0615`, count `8`→`15`. Bump version to 1.5.0. | Schema | ✅ COMPLETE | I257, I258 | U228 | `eks/config/schemas/eks_error_config.json` | — | TL022 | U228 | §74 |
| T1.166 | [Code] Fix ConfigRegistry silent swallow in _eks_config_loader() (#1) using S-B-S-0610 | `bootstrap.py:128` — change `except Exception: pass` to `except Exception as exc: self._log(f"ConfigRegistry init failed, falling back to SchemaLoader: {exc}", level=2)` referencing code `S-B-S-0610`. Preserves graceful fallback to SchemaLoader. Fail-fast does NOT apply — inner try/except is non-fatal; phase outer handler catches fatals separately. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
| T1.167 | [Code] Fix P7 SchemaLoader silent swallow in _bootstrap_schema() (#2) using S-B-S-0611 | `bootstrap.py:365` — same pattern as T1.163 (I257) but for the P7 duplicate site. Replace `except Exception: pass` with `self._log(f"Schema phase doc_config load failed — using empty defaults: {exc}", level=2)` using code `S-B-S-0611`. Non-fatal — SchemaToDDL pre-flight is skipped but schema validation proceeds. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
| T1.168 | [Code] Fix ErrorManager/MessageManager silent swallows in to_dict() (#3, #4) using S-B-S-0612, S-B-S-0613 | `bootstrap.py:568,576` — replace both `except Exception: pass` with `self._log(f"ErrorManager/MessageManager lazy-init failed in to_dict(): {exc}", level=2)` using codes `S-B-S-0612`, `S-B-S-0613`. Both remain `None` — existing callers check for None and degrade gracefully (bare print/log). | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
| T1.169 | [Code] Fix ErrorManager/MessageManager silent swallows in to_pipeline_context() (#5, #6) using S-B-S-0614, S-B-S-0615 | `bootstrap.py:650,659` — same pattern as T1.168 using codes `S-B-S-0614`, `S-B-S-0615`. Pipeline context passes None managers; consumers degrade gracefully. | Code | ✅ COMPLETE | I258 | U228 | `eks/engine/core/bootstrap.py` | T1.165 | TL022 | U228 | §74 |
| T1.170 | [Testing] Add regression tests for all 7 logged bootstrap degradation paths (I257 + I258) | Add test cases to `test_phase1.py` that: (1) inject a broken schema/config pair triggering S-B-S-0609 (via I257 T1.163), (2) inject a broken config/registry triggering S-B-S-0610, (3) inject a broken schema for P7 triggering S-B-S-0611, (4–5) mock ErrorManager/MessageManager in to_dict() to raise and assert S-B-S-0612/S-B-S-0613 in logs, (6–7) same for to_pipeline_context() with S-B-S-0614/S-B-S-0615. Each test asserts the WARNING entry exists in `debug_object["logs"]` with the correct error code or descriptive text. Implemented as `class TestBootstrapDegradation` with 5 test methods covering all 7 paths. 105/106 pass (1 pre-existing unrelated failure). | Testing | ✅ COMPLETE | I257, I258 | U228 | `eks/test/test_phase1.py` | T1.163, T1.166–T1.169 | TL022 | U228 | §74 |

### §75 — Tier 3 Discovery, Bootstrap Schema Strategy & 4-Stage Lifecycle (I259–I263)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.171 | [Code] Add discover_schema_files_tier3() to common/library/loader/schema_discovery.py (I259) | Scans _search_dirs for known _STEM_TO_ATTR stems not matched by glob patterns. Returns dict of newly discovered entries. Exported from __init__.py. | Code | ✅ COMPLETE | I259 | 2026-07-29 | common/library/loader/schema_discovery.py, common/library/loader/__init__.py | — | TL024 | U230 | §75 |
| T1.172 | [Code] Wire Tier 3 fallback in SchemaLoader.load_all() → _discover() (I259) | Call discover_schema_files_tier3() inside _discover() with all _STEM_TO_ATTR keys and _search_dirs; merge results into registry before _load() iterates. | Code | ✅ COMPLETE | I259 | 2026-07-29 | eks/engine/core/schema_loader.py | T1.171 | TL024 | U230 | §75 |
| T1.173 | [Testing] Add Tier 3 fallback regression test (I259) | Test discover_schema_files_tier3() finds eks_project_code_schema.json when present in _search_dirs but not in existing registry. | Testing | ✅ COMPLETE | I259 | 2026-07-29 | eks/test/test_schema_discovery.py | T1.171 | TL023 | U230 | §75 |
| T1.174 | [Schema] Add 3 missing _STEM_TO_ATTR entries — department, discipline, facility (I260) | Add eks_department_schema, eks_discipline_schema, eks_facility_schema to _STEM_TO_ATTR mapping; add self.department_schema, self.discipline_schema, self.facility_schema to __init__. | Schema | ✅ COMPLETE | I260 | 2026-07-29 | eks/engine/core/schema_loader.py | — | TL024 | U230 | §75 |
| T1.175 | [Code] Implement _bootstrap_schema() with schema_loader strategy hook in BootstrapManager (I261) | Add SchemaLoader callable type; accept in __init__; invoke in _bootstrap_schema() during P7 phase. Raise S-B-S-0616 if empty, S-B-S-0617 on exception. | Code | ✅ COMPLETE | I261 | 2026-07-29 | common/library/bootstrap/manager.py | — | TL024 | U230 | §75 |
| T1.176 | [Schema] Register S-B-S-0616 (empty discovery) and S-B-S-0617 (cross-ref failure) in error config (I261) | Add both codes to eks_error_config.json system_errors; update bootstrap range count 15→18, end_id 0615→0618; bump version to 1.6.0. | Schema | ✅ COMPLETE | I261 | 2026-07-29 | eks/config/schemas/eks_error_config.json | — | TL024 | U230 | §75 |
| T1.177 | [Code] Add validate_schema_conformance() to ValidationManager (I261) | New method using jsonschema.validate() with optional $ref resolution via base_schemas dict. Returns ValidationItem PASS/FAIL. | Code | ✅ COMPLETE | I261 | 2026-07-29 | common/library/utility/validation/manager.py | — | TL024 | U230 | §75 |
| T1.178 | [Code] Extract build_uri_registry() to common/library/loader/ref_resolver.py (I262) | New file with build_uri_registry() function scanning directories for $id declarations with duplicate detection. Exported from __init__.py. | Code | ✅ COMPLETE | I262 | 2026-07-29 | common/library/loader/ref_resolver.py, common/library/loader/__init__.py | — | TL024 | U230 | §75 |
| T1.179 | [Code] Add validate_schema_conformance() to ValidationManager (I263) | Same as T1.177 — shared with I261. Added conformance validation with jsonschema. | Code | ✅ COMPLETE | I263 | 2026-07-29 | common/library/utility/validation/manager.py | — | TL024 | U230 | §75 |
| T1.180 | [Code] Refactor SchemaLoader.load_all() into 4 stage methods (I263) | Split into _discover() (bootstrap + Tier 1-3 discovery), _load() (schema loading from registry), _validate() (all validation calls), _extract() (post-load indexes). load_all() calls in sequence. | Code | ✅ COMPLETE | I263 | 2026-07-29 | eks/engine/core/schema_loader.py | — | TL024 | U230 | §75 |
| T1.181 | [Schema] Register S-B-S-0618 (conformance failure) in error config (I263) | Add code to eks_error_config.json v1.6.0. FATAL, stops_pipeline: true. | Schema | ✅ COMPLETE | I263 | 2026-07-29 | eks/config/schemas/eks_error_config.json | — | TL024 | U230 | §75 |

## 39. Column Processing Metadata — Schema-Driven Registry Column Definitions (I264)

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.182 | [Schema] Add 6 column-processing definitions to eks_doc_base_schema.json | Add column_type_enum (12 role types), processing_phase_enum (A/B/C/D/bootstrap), calculation_strategy_def (priority_chain/filename_segment/file_property/parser_metadata/cover_page_element/code_to_title_lookup/health_score/auto_increment), handler_def (which module handles this calculation type), validation_rule_def (pattern/min_length/enum_reference/schema_reference_check), column_processing_entry_def (full entry schema referencing all above). | Schema | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_base_schema.json | — | — | U232 | §75 |
| T1.183 | [Schema] Add column_processing property to eks_doc_setup_schema.json | New property: "column_processing" — object with additionalProperties pointing to column_processing_entry_def. propertyNames: ^[a-z_]+$. DCC-aligned key-as-name pattern per T1.184 review. | Schema | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_setup_schema.json | T1.182 | — | U232 | §75 |
| T1.184 | [Config] Add column_processing entries for all 42 document registry columns to eks_doc_config.json | One entry per column in documents table, keyed by column name (DCC-aligned object pattern). Each: column_type, is_calculated, calculation, schema_ref, validation, processing_phase, required, description. 42 entries: 9 Phase A, 33 Phase B. | Config | ✅ COMPLETE | I264 | 2026-07-29 | eks/config/schemas/eks_doc_config.json | T1.183 | — | U232 | §75 |
| T1.185 | [Code] Build BaseColumnProcessor in common/library/ + EKSColumnProcessor | New package common/library/column_processor/ with HandlerRegistry + BaseColumnProcessor (generic phase dispatch). New class eks/engine/core/column_processor.py — EKSColumnProcessor(BaseColumnProcessor) with 9 pre-registered handler stubs: priority_chain, filename_segment, file_property, parser_metadata, cover_page_element, code_to_title_lookup, health_score, auto_increment, existing_record. Factory method from_doc_config(). | Code | ✅ COMPLETE | I264 | 2026-07-29 | common/library/column_processor/{__init__.py,base.py,registry.py}, eks/engine/core/column_processor.py | T1.184 | — | U233 | §75 |
| T1.186 | [Code] Wire EKSColumnProcessor handler stubs with real logic | Enhance 9 handler functions in eks/engine/core/column_processor.py: priority_chain (resolve project_title/document_title/total_sheets from cover_page → parser_metadata → code_to_title → existing_record), filename_segment (delegate to already-parsed data dict from Phase A FilenameParser), file_property (lookup from context.file_properties), parser_metadata (lookup from context.metadata), cover_page_element (extract field from cover_page content + asset_tags comma-split), code_to_title_lookup (project_code_titles registry), health_score (context.score), auto_increment (UUID), existing_record (preserve from data dict). | Code | ✅ COMPLETE | I264 | 2026-07-29 | eks/engine/core/column_processor.py | T1.185 | TL025 | U233 | §75 |
| T1.187 | [Code] Wire ColumnProcessor into PipelineOrchestrator phases | Replace hardcoded blocks in run_phase_a (filename identity fields), run_phase_b (project_title chain, identity write-back, file properties, elements, health score), and run_phase_c (review flags) with a single ColumnProcessor.process(phase) call per phase. Fix bare `doc_config` bug in _process_file. Fix `position` schema type (int→int null for separator-based revision). Fix `min_length` schema minimum (1→0 for zero-threshold). | Code | ✅ COMPLETE | I264 | 2026-07-29 | eks/engine/core/pipeline_orchestrator.py, eks/config/schemas/eks_doc_base_schema.json | T1.186 | TL026 | U234 | §75 |
| T1.188 | [Testing] Add regression tests for ColumnProcessor central orchestrator | Tests: (a) ColumnProcessor dispatches each calculation.type to correct handler, (b) priority_chain resolves project_title correctly across all 4 sources, (c) validation rules fire on mismatch, (d) fallback to leave_null works, (e) 42 column entries validate against setup schema, (f) end-to-end: ColumnProcessor.process("B") produces expected output. | Testing | ✅ COMPLETE | I264 | 2026-07-29 | eks/test/test_column_processing.py (new) | T1.187 | TL027 | U235 | §75 |

## 40. Project Definition Schema Refactoring (I265)

## Revised Implementation Tasks

## Implementation Tasks

| #          | Date       | Phase   | Task                                             | Description                                                                                                                                                                                                                                                                                                                                                                                                     | Dependencies           | Author   |   Status   |
| :--------- | :--------- | :------ | :----------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------- | :------- | :--------: |
| **T1.189** | 2026-07-30 | Phase 1 | Define Project Definition Architecture           | Define architecture, ownership boundaries, runtime lifecycle, bootstrap sequence, RuntimeProjectConfiguration model, and interactions between SchemaLoader, ProjectDefinitionResolver, FilenameParser, ColumnProcessor, and runtime modules.                                                                                                                                                                                            | —                      | Franklin | ✅ COMPLETE |
| **T1.190** | 2026-07-30 | Phase 1 | Implement Project Definition Schema              | Add 11 definitions to `eks_base_schema.json` (project_identity_def, engineering_convention_def, document_profile_selection_def, asset_profile_ref_def, ontology_profile_ref_def, retrieval_profile_ref_def, pipeline_config_def, security_config_def, integration_config_def, project_definition_entry_def, project_definition_registry_def). Add `project_definition` property to `eks_setup_schema.json`. Create `eks_project_definition_config.json` with per-project entries (131101, 131242). Migrate data from `eks_project_rules_config.json`. Update `eks_config.json` with `project_definition.$ref`. | T1.189                 | Franklin | ✅ COMPLETE |
| **T1.191** | 2026-07-30 | Phase 1 | Refactor Reusable Configuration Libraries        | Refactor `eks_doc_config.json` to retain only reusable profiles. Removed `revision_validation` (per-project) and `filename_patterns` (per-project) — moved to `eks_project_definition_config.json`. Added `filename_profiles` as reusable profile-keyed section. Added backward-compat injection in SchemaLoader._extract() to reconstruct `filename_patterns` from Project Definition. Updated `eks_doc_setup_schema.json` (v1.8.0), `eks_base_schema.json` (v1.14.0), `eks_project_definition_config.json` (v1.2.0). 364/368 tests pass (4 pre-existing failures).                                                                                                                                                                                       | T1.190                 | Franklin | ✅ COMPLETE |
| **T1.192** | 2026-07-30 | Phase 1 | Verify SchemaLoader Compatibility                | Verified SchemaLoader 4-stage lifecycle (_discover → _load → _validate → _extract) handles Project Definition schema. Added `eks_project_definition_config` to `_STEM_TO_ATTR` mapping. Added `self.project_definition_config` attr. Added `_validate_project_definition()` validation stage. Added project_definition `$ref` resolution in `_discover()` (before _validate_config). Documented contract boundary: SchemaLoader returns raw validated schema objects; RuntimeProjectConfiguration assembly deferred to ProjectDefinitionResolver. schema_loader.py v1.1.0→1.2.0.                                                                                                                                                               | I261, I263             | Franklin | ✅ COMPLETE |
| **T1.193** | 2026-07-31 | Phase 1 | Implement ProjectDefinitionResolver              | Implement the common EKS pipeline module that loads all Project Definitions from `eks_project_definition_config.json`, resolves reusable profile references, applies runtime environment profiles, validates each project configuration, merges configuration, constructs a RuntimeProjectConfiguration per project, and registers all in the Project Configuration Registry during pipeline bootstrap. The resolver shall not determine which project a document belongs to — project identification is a pipeline responsibility. | T1.190, T1.191, T1.192 | Franklin | ✅ COMPLETE |
| **T1.194** | 2026-07-31 | Phase 1 | Migrate Runtime Modules                          | Replace direct schema consumption and multiple configuration dictionaries with RuntimeProjectConfiguration across Phase 1 runtime modules. Preserve I255 auto-detection while replacing `project_code_registry` with Project Definition (`registry.project_codes`) as the authoritative project registry. **Approved design decisions (2026-07-31)**: **(D1 — Caller-injection contract)** Caller (FileScanner / PipelineOrchestrator) is constructed with the injected ProjectConfigurationRegistry; caller resolves the project code (Phase A: auto-detect; Phase B: committed identity) and fetches the config slice; caller passes `project_code` + resolved slice to the module at call time. Modules never hold the registry, self-fetch configuration, or identify projects (satisfies L.8.7 + L.9.5 + L.9.7). **(D2 — Phase A registration)** Phase A stays project-agnostic for assignment (L.9.3): FileScanner keeps FilenameParser in auto-detect mode over `registry.project_codes`; no committed project assignment in Phase A; authoritative assignment in Phase B. Requires L.9.3 wording amendment — recorded in T1.197 alignment pass. **Scope**: existing Phase 1 modules only — FileScanner, FilenameParser, PipelineOrchestrator (Pipeline), ColumnProcessor, FilePropertyParser, ParserRouter, RevisionManager. P3–P5 modules (AssetExtractor, GraphBuilder, Retriever, PromptEngine, OCRProcessor) deferred to their phases. **Backward-compat**: keep dict-based params as optional fallback per L.14.7 until T1.196 Stage 5 removal. **Tests**: TL029 — 21/21 slice-injection tests + full suite 413 passed (5 pre-existing). Update: U240. | T1.193, I255, I264     | Franklin | ✅ COMPLETE |
| **T1.195** | 2026-07-30 | Phase 1 | Implement Configuration Validation               | Validate project completeness, reusable profile references, project-to-profile mappings, duplicate definitions, unused profiles, schema consistency, and RuntimeProjectConfiguration construction during ProjectDefinitionResolver execution. **Approved design decisions (2026-07-31)**: **(V1 — Failure semantics)** System errors (schema violations, missing mandatory sections, unknown profile IDs, unknown runtime profiles, duplicate project codes/profiles, runtime construction failure) hard-fail pipeline initialization via `resolver.errors` → bootstrap raises. Data-related errors (L.13.6 capability consistency, L.13.7 metadata gaps, L.13.10 unused profiles) are logged via new `resolver.data_errors` and never fail the pipeline. **(V2 — Capability-driven consistency, no hardcode)** L.13.6 implemented with NO hardcoded pairs and NO central compatibility matrix: each profile declares its capabilities in its owning schema — `parsing_profile_def` with `supported_document_profiles`/`supported_extensions`/`requires_ocr` (doc schema set), chunking `supported_document_types`, embedding `supported_retrieval_strategies`, ontology `supported_asset_profiles`, validation `supported_engineering_conventions`; ProjectDefinitionResolver extracts these during `_resolve_profile()` (exact-key lookup, not substring match) and a single generic `_evaluate_capability_compat()` compares resolved profiles. Adds `parsing_profiles` section to `eks_doc_config.json`. **(V3 — Error codes)** System errors: `S-C-S-{id}` (category `Config` — e.g. `S-C-S-0901` missing mandatory section, `S-C-S-0902` unknown profile ref, `S-C-S-0903` duplicate project code, `S-C-S-0904` runtime construction failure). Data errors: `P1-C-V-{id}` (layer P1, module C=Config, function V=Validate — e.g. `P1-C-V-0001` capability consistency violation, `P1-C-V-0002` metadata-policy gap, `P1-C-V-0003` unused profile). Both patterns already satisfy `eks_error_code_base.json` regexes (system `S-[A-Z]-S-[0-9]{4}`, data `P[0-9]-[A-Z]-[A-Z]+-[0-9]{4}`) — registration only in `eks_error_config.json` (system + data sections) + `eks_message_config.json` + Appendix D + cross-source audit per §24. **Scope**: split `_validate_resolved()` into per-category validators (project completeness, profile refs, environment refs, capability consistency, metadata policy, duplicate detection, unused config, runtime module L.13.11, runtime constructible L.13.8); extend `validation_report` to L.13.12 content (resolved profiles, runtime profiles, checksum, schema version, RPC version); 30+ tests per category incl. ErrorManager code resolution. **Implementation (2026-07-31)**: schemas (doc base v1.10.0 `parsing_profile_def`, setup v1.9.0 `parsing_profiles`, config v1.8.0 profiles), error registry v1.7.0 (S-C-S-0901..0904, P1-C-V-0001..0003, 2 new ranges), message catalog v1.2.0 (4 PDEF messages), resolver rev 1.1.0 (V1 data_errors, V2 exact-key + `_evaluate_capability_compat`, L.13.3/.4/.5/.6/.7/.9/.10 validators, L.13.12 report, `_known_runtime_profiles`), bootstrap surfaces data_errors. **Tests**: TL030 — 75/75 (test_project_definition.py, 47 new) + 65/65 (test_t132_modules.py, 12 new); full suite 472 passed / 5 pre-existing. Update: U242. Appendix D v2.1 re-synced (D4 75/75, D5 53/53, D6 52/52). | T1.193                 | Franklin | ✅ COMPLETE |
| **T1.196** | 2026-07-30 | Phase 1 | Migrate Existing Configuration                   | **Scope (revised 2026-07-31 to cover I266–I272 — L.11 Stage 4 + Stage 5)**: **(1) $ref consumers (I267)** — remove `project_rules_registry` from `eks_setup_schema.json` (property + required) and `eks_config.json` ($ref); remove `project_rules_def` from `eks_base_schema.json`; archive `eks_project_rules_config.json`. **(2) Runtime consumers (I266)** — repoint `config_registry.py` `get_project_rules` / `get_fragment_required_fields` / `resolve_required_fields` to the Project Definition; expose `fragment_required_fields` via resolver / AssetExtractor slice. **(3) Stage 5 compat-layer removal (I268)** — drop the dead `legacy_project_rules` flag; remove `_validate_project_rules()` and the dead `revision_validation` reconstruction; keep the functional `filename_patterns` reconstruction (T1.191) until the filename_parser slice carries resolved patterns. **(4) Tests** — legacy assertions repointed to the Project Definition; regression tests with zero legacy presence. **(5) Cross-source audit (§24) + naming/doc alignment (I269–I272)** — naming reconciliation, L.6.2 note, L.13 V1/V2/V3 wording, L.10.6 ColumnProcessor, knowledge.json, eks_system_workplan, Appendix E. **Implementation (2026-07-31)**: schemas — `eks_setup_schema.json` v1.9.0, `eks_config.json` v1.10.0, `eks_base_schema.json` v1.15.0, `eks_project_definition_config.json` v1.3.0; `eks_project_rules_config.json` archived to `eks/archive/config/`. schema_loader.py rev 1.3.0, config_registry.py rev 0.3, project_definition.py rev 1.2.0 (fragment_required_fields → AssetExtractor slice). Tests: TL031 — full suite 473 passed / 5 pre-existing (unchanged); test_project_definition.py 76/76 (1 new I266 regression test). Docs updated per I269–I272. Update: U244. | T1.194, T1.195         | Franklin | ✅ COMPLETE |
| **T1.197** | 2026-07-30 | Phase 1 | Documentation, Traceability & Regression Testing | Update architecture documentation, Phase 1 implementation index, issue traceability, migration guide, dependency references, runtime lifecycle documentation, and verify regression across document ingestion, metadata extraction, column processing, asset processing, graph construction, retrieval, and RAG workflows. Perform cross-workplan alignment audit: verify architecture diagrams (P1.1), scope tables (P1.2), pipeline architecture (Appendix F), bootstrap design (Appendix H), interface architecture (Appendix G), and knowledge.json all reflect the RuntimeProjectConfiguration model and updated ownership boundaries. Flag any discrepancies as follow-up issues. Cross-phase module mapping: FileScanner (P1), FilenameParser (P1), RevisionValidator (P1), DocumentParser (P1), OCRProcessor (P1), MetadataExtractor (P1), ColumnProcessor (P1), Pipeline (P1), AssetExtractor (P3), GraphBuilder (P3), Retriever (P4), PromptEngine (P4/P5), ValidationEngine (cross-phase). **Implementation (2026-07-31)**: L.9.3 wording amendment (T1.194 D2 — Phase A auto-detect over registry.project_codes, no committed assignment). Cross-workplan audit — P1.1 (load_all output → project_definition_config; module inventory + ProjectDefinitionResolver row), Appendix F/G/H (I265 alignment notes), knowledge.json (key_modules + data_flows). Migration guide created — `docs/project_definition_migration_guide.md`. Regression cleanup — `test_config_version_bumped` stale assertions fixed (doc config v1.8.0, doc base v1.10.0) — pre-existing failure count 5→4. Task log status summary recounted (365 ✅ / 27 🔷 / 3 ⛔ / 1 🔴 = 396). I265 closed → 📐 Aligned. Tests: TL032 — full suite 474 passed / 4 pre-existing. Update: U246. | T1.196                 | Franklin | ✅ COMPLETE |
| **T1.198** | 2026-07-30 | Phase 1 | Align Project Definition Schema with Appendix L   | Add 8 missing sections to `project_definition_entry_def` in `eks_base_schema.json` (project_lifecycle, engineering_standards, parsing_profile, chunking_profile, embedding_profile, metadata_policy, prompt_profile, validation_profile). Add `runtime_profiles` (profile references only — no URIs). Rename `security_config` → `security_profile`. Remove `integration_config_def` and `pipeline_config_def` (deployment details removed per L.6.3). Update `eks_project_definition_config.json`. | T1.190                 | Franklin | ✅ COMPLETE |
| **T1.199** | 2026-07-30 | Phase 1 | ~~Create Environment Configuration~~                     | ⛔ **Cancelled** — `eks_config.json` already serves as environment configuration (holds `vector_store`, `embedding`, `registry`, `global_paths`, `logging`, `system_parameters`, etc.). The principle of L.6.3 (deployment config separate from Project Definition) is satisfied. Remaining scope (add `graph_db`, `storage`, `messaging` properties) absorbed into T1.196.                                                                                                                                         | —                      | Franklin | ⛔ Cancelled |
| **T1.200** | 2026-07-31 | Phase 1 | [Fix] COLUMN_ALLOWLIST SSOT — remove hardcoded static fallback (I274 Option A) | Remove the hardcoded 54-column fallback set in `registry.py::_get_column_allowlist()`; the schema-derived set (`document_metadata_def` + `project_metadata_def` properties) becomes the sole source of the column allowlist per AGENTS.md §16. On genuine schema absence, raise a descriptive error — never silently fall back. **NOTE — empty file_type fix already done (I273/U247, 2026-07-31)**: `file_type` added to the fallback allowlist + Phase B path-derived `_resolve_phase_b_files()` applied; this task removes the fallback itself (execute after T1.201 so the schema path is CWD-independent first). | T1.201                 | Franklin | 🔷 Planned |
| **T1.201** | 2026-07-31 | Phase 1 | [Fix] CWD-independent doc base schema path for allowlist derivation (I274) | `_get_column_allowlist()` loads the doc base schema via hardcoded `Path("eks/config")`, which fails from a non-root working directory and triggered the I273/I274 fallback. Resolve through schema-driven `global_paths`/`resolve_paths()` (or the already-resolved `SchemaLoader.config_dir`) so derivation works from any CWD (AGENTS.md §15 — no hardcoded path literals). | —                      | Franklin | 🔷 Planned |
| **T1.202** | 2026-07-31 | Phase 1 | [Testing] Allowlist drift-guard regression tests (I274) | Assert `_get_column_allowlist()` equals the schema-derived set and works from a non-root CWD (simulating the CLI scenario that caused I273); assert a descriptive error is raised when the schema is genuinely absent. Extends `test_register_document_persists_file_type` (I273). | T1.200, T1.201         | Franklin | 🔷 Planned |

