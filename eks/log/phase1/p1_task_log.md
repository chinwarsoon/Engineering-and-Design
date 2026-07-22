# Phase 1 Task Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/phase1/p1_task_log.md`  
**Last Updated**: 2026-07-22

## Legend

### Task Status

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| ✅ | Complete | Task fully implemented and verified |
| 🔷 | Planned | Task defined but not yet implemented |
| ⛔ | Won't Implement | Explicitly rejected or out of scope |

### Column Format

All tables use the standard 12-column enriched format:

`ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section`

---

## Status Summary

| Status | Marker | Count |
| :----- | :----: | ----: |
| Complete | ✅ | 255 |
| Planned | 🔷 | 40 |
| Won't Implement | ⛔ | 0 |
| **Total** | | **295** |

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
| T1.99.64 | [Docs] Update Appendix D: add Bootstrap category (`S-B-S-0600–0699`) | D3 updated; `P1-BOOT-*` format documented in D2. | Docs | 🔷 PLANNED | I112 | — | `appendix_d_pipeline_messages_errors.md` | ← T1.99.63 | — | — | §30 |
| T1.99.65 | [Schema] Register 14 universal `B-*` codes in `eks_error_config.json` | Under new `bootstrap_universal` range; `eks_error_code_base.json` pattern updated. | Schema | 🔷 PLANNED | I112 | — | `eks/config/schemas/eks_error_config.json` | ← T1.99.64 | — | — | §30 |
| T1.99.66 | [Schema] Add bootstrap milestone/status messages to `eks_message_config.json` | `eks_message_base.json` + Appendix D D6 updated. | Schema | 🔷 PLANNED | I112 | — | `eks/config/schemas/eks_message_config.json` | ← T1.99.64 | — | — | §30 |
| T1.99.67 | [Config] Decide and implement `P1-BOOT-*` format (A: migrate to `S-B-S-06xx` or B: keep hybrid) | Format decision made and implemented across all sources. | Config | 🔷 PLANNED | I112 | — | — | ← T1.99.64–66 | — | — | §30 |
| T1.99.68 | [Code] Ensure all EKS code paths use registered error codes | No unregistered `B-*` codes can fire in EKS context. | EKS | 🔷 PLANNED | I112 | — | `eks/engine/` | ← T1.99.67 | — | — | §30 |
| T1.99.69 | [Testing] Tests + docs + close I112 | Verify all bootstrap codes resolve via `ErrorManager`; messages via `MessageManager`; Appendix D fully updated. | EKS | 🔷 PLANNED | I112 | — | — | ← T1.99.64–68 | — | — | §30 |
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
| T1.99.179 | [Code] G5: Wire `RevisionManager` into Phase B for supersession detection | Implement `detect_supersession()` in `revision.py` — query existing docs by document_number, compare revisions, set `is_latest=False`, set `supersedes`/`superseded_by` chain. Integrate into `PipelineOrchestrator._process_file()` after `register_document()`. | Revision | 🔷 PLANNED | I212 | — | `eks/engine/core/revision.py`, `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/registry.py` | — | — | — | §49 |
| T1.99.180 | [Code] G9: Restore checkpoint persistence with resume capability | Uncomment `save_checkpoint()` calls. Write checkpoints to `output/<run_id>/checkpoint_<phase>.json`. Add `--resume <run_id>` CLI flag. | Pipeline | 🔷 PLANNED | I216 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/eks_engine_pipeline.py` | ← T1.99.179 | — | — | §49 |
| T1.99.181 | [Code] G17: Wire `ReviewManager` into Phase C for review status persistence | Iterate flagged docs: apply auto-corrections, expose remaining flags, `approve_document()` persists to registry. Add `POST /api/v1/review/approve` endpoint. | Review | 🔷 PLANNED | I224 | — | `eks/engine/core/review_manager.py`, `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/registry.py`, `eks/ui/backend/phase1_server.py` | ← T1.99.179–180 | — | — | §49 |

### Wave 2 — Architecture Compliance (I209, I211, I215, I221) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.182 | [Code] G2: Refactor `FileScanner`, `HealthScorer`, `StructureDetector` to inherit from `BaseEngine` | Each engine gets `validate_input()` → `execute()` → `validate_output()`. Use `EngineInput`/`EngineOutput` from `core/base.py`. Complete `ParserRouter`. | Architecture | 🔷 PLANNED | I209 | — | `eks/engine/core/file_scanner.py`, `eks/engine/core/health_scorer.py`, `eks/engine/core/structure_detector.py`, `eks/engine/parsers/parser_router.py` | — | — | — | §49 |
| T1.99.183 | [Code] G4: Replace direct instantiation in `PipelineOrchestrator` with factory calls | Change `self.scanner = FileScanner(...)` → `self.scanner = EngineFactory.create("FileScanner", ...)` for all engines. Verify `ParserRouter` consistency. | DI | 🔷 PLANNED | I211 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/factories.py` | ← T1.99.182 | — | — | §49 |
| T1.99.184 | [Code] G8: Unify dual telemetry into single heartbeat stream | `PipelineOrchestrator` accepts `telemetry: Optional[TelemetryHeartbeat]` parameter; forwards checkpoints to main heartbeat. | Telemetry | 🔷 PLANNED | I215 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/eks_engine_pipeline.py`, `eks/engine/core/telemetry.py` | — | — | — | §49 |
| T1.99.185 | [Fix] G14: Guard `psutil` import in `telemetry.py` | Wrap `import psutil` in try/except ImportError; memory/CPU sampling becomes no-op when absent. Add `psutil` to `eks.yml` as optional dependency. | Safety | 🔷 PLANNED | I221 | — | `eks/engine/core/telemetry.py`, `eks/eks.yml` | ← T1.99.184 | — | — | §49 |

### Wave 3 — IO Contracts & Data Flow (I210, I214, I218, I219) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.186 | [Code] G3: Consolidate dual `EngineInput`/`EngineOutput` | EKS `core/base.py` versions subclass `common.library.core.pipeline` versions. Add domain-specific fields. Delete standalone definitions; re-export. | Contracts | 🔷 PLANNED | I210 | — | `eks/engine/core/base.py`, `eks/engine/eks_engine_pipeline.py` | — | — | — | §49 |
| T1.99.187 | [Code] G7: Wire `HealthInput`/`HealthOutput` + `DiscoveryInput`/`DiscoveryOutput` into pipeline | Phase A: `DiscoveryInput` → `scanner.scan()` → `DiscoveryOutput`. Phase B: `HealthInput` → `scorer.score()` → `HealthOutput` for DB write. | Contracts | 🔷 PLANNED | I214 | — | `eks/engine/pipeline_orchestrator.py`, `eks/engine/core/io_contracts.py` | ← T1.99.186 | — | — | §49 |
| T1.99.188 | [Code] G11: Pass context-resolved paths into `ParserInput` defaults | Replace `ParserInput(config_file="", schema_dir="", output_dir="")` with `self.context.paths` values. Same for `DiscoveryInput`. | Data | 🔷 PLANNED | I218 | — | `eks/engine/pipeline_orchestrator.py` | ← T1.99.187 | — | — | §49 |
| T1.99.189 | [Code] G12: Write parsed content to `context.data.extracted_content` during execution | After successful parse, store `self.context.data.extracted_content[doc_id] = extraction_result`. Enables downstream reads without re-querying registry. | Data | 🔷 PLANNED | I219 | — | `eks/engine/pipeline_orchestrator.py` | ← T1.99.188 | — | — | §49 |

### Wave 4 — Folder Structure & Schema Wiring (I208, I220, I225) — Should-Fix

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.190 | [Code] G1+G13: Migrate to Appendix F domain subdirectory layout | Create 6 subdirectories: `engine/discovery/`, `engine/router/`, `engine/registry/`, `engine/revision/`, `engine/health/`, `engine/structure/`. Move `parser_router.py` from `engine/parsers/` to `engine/router/`. Project-wide grep for all import paths. 7 modules moved, ~30 files updated. | Structure | 🔷 PLANNED | I208, I220 | — | Multiple — see Depends On for scope | ← T1.99.182–189 | — | — | §49 |
| T1.99.191 | [Code] G18: Wire `SchemaToDDL` into bootstrap P4 for auto-DDL generation | In `_bootstrap_registry()`: generate DDL from `eks_doc_base_schema.json`, compare with existing table schema, apply migration if needed. On fresh DB: full CREATE TABLE DDL. | Bootstrap | 🔷 PLANNED | I225 | — | `eks/engine/core/bootstrap.py`, `eks/engine/schema_to_ddl.py`, `eks/engine/core/registry.py` | ← T1.99.190 | — | — | §49 |

### Wave 5 — Documentation & UI Contracts (I217, I222) — Nice-to-Have

| ID | Task | Details | Scope | Status | Issues | Updated | Files | Dependencies | Tests | UpdateRef | Section |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| T1.99.192 | [Code] G10: Implement `DocumentSelectionContract` + `PipelineConfigContract` per Appendix F | Add contract schemas to `contracts.py`, wire `ContractManager` to validate before pipeline execution. Add `POST /api/v1/contracts/document-selection` and `POST /api/v1/contracts/pipeline-config` endpoints. | UI | 🔷 PLANNED | I217 | — | `eks/engine/core/contracts.py`, `eks/engine/core/contract_manager.py`, `eks/ui/backend/phase1_server.py` | ← T1.99.186–191 | — | — | §49 |
| T1.99.193 | [Docs] G15: Cross-audit Appendix E schema versions vs. actual `version` fields | Read `"version"` from all 23 schema files, compare against Appendix E E5.1 table. Update stale entries. Add validation script `eks/test/verify_appendix_e_versions.py`. | Docs | 🔷 PLANNED | I222 | — | `docs/appendix_e_schema_design.md`, `eks/test/verify_appendix_e_versions.py` | — | — | — | §49 |

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
