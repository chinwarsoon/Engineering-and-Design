# Appendix P1.4 — Phase 1 Task Details

**Document ID**: WP-EKS-P1-A1.4

**Version**: 1.5

**Last Updated**: 2026-07-21

> **v1.5**: §1 replaced individual "Task Table 1" rows with Task Status Summary (mirrors `issue_log.md` Status Summary pattern). Per-section detail tables enriched with `Issues`, `Updated on`, `Files`, `Priority`, `Depends On` columns. Known status errors fixed (T1.99.50–61). Missing tasks T1.99.101–108 (I130–I132) added.


> All task breakdown tables relocated from the [Phase 1 Foundation Workplan](phase_1_foundation_workplan.md).

---

## 1. Task Status Summary

> Source: [§8](phase_1_foundation_workplan.md#8)
>
> Individual task detail rows are located exclusively in their per-section breakdown tables (§2–§23). This summary table mirrors the `issue_log.md` Status Summary pattern — counts only, no individual task rows.

### Task Status Summary

| Status | Marker | Count |
| :----- | :----: | ----: |
| Complete | ✅ | 260 |
| Planned | 🔷 | 36 |
| Won't Implement | ⛔ | 2 |
| **Total** | | **298** |

> **Counts as of 2026-07-21**. Must be refreshed whenever a task status changes. See per-section tables for canonical status of each task.


---

## 2. Foundation, Environment & Compliance (R99) Tasks


> Source: [§14](phase_1_foundation_workplan.md#14)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.1 | Create EKS folder structure | archive, config, data, output, engine, log, docs, workplan, test, ui | R99 | ✅ COMPLETE | — | — | folders | — | — |
| T1.2 | Create environment file `eks.yml` | Conda environment with all Phase 1–5 dependencies | R99 | ✅ COMPLETE | — | — | `eks/eks.yml` | — | — |
| T1.14 | Implement SSOT config registry | Global parameter access via schema-driven config; no hardcoding | R06, R35 | ✅ COMPLETE | — | — | `config_registry.py` | — | — |
| T1.15 | Write unit tests | Schema loader, document registry, revision management, parsers, logger | R99 | ✅ COMPLETE | — | — | `test/` | — | — |
| T1.16 | Create log files | `update_log.md`, `issue_log.md` under `eks/log/` | R99 | ✅ COMPLETE | — | — | `log/update_log.md`, `log/issue_log.md` | — | — |
| T1.33 | Migrate EKS schemas to config/schemas/ | Move core/asset/ontology config & schema files to `eks/config/schemas/`; update SchemaLoader, ErrorManager, MessageManager, tests, and documentation | R06, R99 | ✅ COMPLETE | — | — | `config/schemas/`, `schema_loader.py` | — | — |
| T1.48 | Schema audit — duplicates, inconsistencies, missing validations | Remove duplicate `revision_id` and `discipline_code`; Align parser import paths; Add dgn/dwg stub parsers; Log all issues (I022–I028). All 114 tests pass. | R06, R99 | ✅ COMPLETE | I022, I023, I024, I025, I026, I027, I028 | — | `eks_doc_base_schema.json`, `eks_config.json` | — | — |
| T1.49 | Cross-cutting workplan remediation | Fix `agent_rule.md` references → `AGENTS.md`; convert Linux absolute paths to relative; update stale statuses; reorder §10/§25; fill Phase 3 placeholders; add reranker criteria. | R99 | ✅ COMPLETE | — | — | `phase_1_foundation_workplan.md` | — | — |
| T1.52 | Implement EKSPipelineContext | Create `eks/engine/core/context.py` with nested dataclasses for centralized state management per Appendix F | R57 | ✅ COMPLETE | — | — | `engine/core/context.py` | — | — |
| T1.53 | Implement BaseEngine abstract class | Create `eks/engine/core/base.py` with standard execution flow (validate → execute → validate) per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/base.py` | — | — |
| T1.55 | Implement Multi-Stage Validation | Create `eks/engine/core/validator.py` with setup, schema, data, parser validation stages per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/validator.py` | — | — |
| T1.56 | Implement CLI Entry Points | Discovery CLI and Health CLI both call real engines via `bootstrap_pipeline()` funnel. I093 resolved. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py`, `engine/core/health_cli.py` | — | T1.52, T1.53 |
| T1.56.1 | Wire Discovery CLI to real engine (I093) | `discovery_cli.py` → `PipelineOrchestrator.run_phase_a()`; real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `engine/core/discovery_cli.py` | — | T1.56 |
| T1.56.2 | Wire Health Scorer CLI to real engine (I093) | `health_cli.py` → `HealthScorer.score()`/`score_batch()`; real scores/status. | R99 | ✅ COMPLETE | I093 | — | `engine/core/health_cli.py` | — | T1.56 |
| T1.56.3 | Add pytest for discovery_cli (I093) | Happy path + failure/edge case; assert real `EngineOutput`. | R99 | ✅ COMPLETE | I093 | — | `test/` | — | T1.56.1 |
| T1.56.4 | Add pytest for health_cli (I093) | Single + batch scoring + threshold boundary. | R99 | ✅ COMPLETE | I093 | — | `test/` | — | T1.56.2 |
| T1.56.5 | Close I093 records & reclassify T1.56 | Mark I093 resolved; flip T1.56 status. | R99 | ✅ COMPLETE | I093 | — | `update_log.md`, `issue_log.md` | — | T1.56.3–4 |
| T1.57 | Implement HTTP API Endpoints | Delivered as `eks/ui/backend/phase1_server.py` (standalone `--port 5001`). | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — |
| T1.65 | Implement Project Setup Validator | Create `eks/engine/core/setup_validator.py` with auto-creation of missing folders per Appendix F | R99 | ✅ COMPLETE | — | — | `engine/core/setup_validator.py` | — | T1.66 |
| T1.66 | Create Project Setup Schema | Create `eks/config/schemas/project_setup.json` for setup validation per Appendix F | R99 | ✅ COMPLETE | — | — | `config/schemas/project_setup.json` | — | — |
| T1.67 | Integrate project_setup into core 3-layer schemas (I046) | Refactor content into `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`. Delete orphan `project_setup.json`. Resolves I046. | R99 | ✅ COMPLETE | I046 | — | `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`, `setup_validator.py` | — | T1.66 |
| T1.70 | Add data_dir traversal guard to phase1_server.py | Resolve `data_dir` against `PRJ_DIR`, check `is_relative_to(PRJ_DIR)` — return HTTP 403 if outside project root. | R99 | ✅ COMPLETE | — | — | `ui/backend/phase1_server.py` | — | — |
| T1.74 | Cross-platform path compatibility | Fix 4 cross-platform gaps in `phase1_server.py`, `context.py`. Resolves I078–I081. | R99 | ✅ COMPLETE | I078, I079, I080, I081 | — | `phase1_server.py`, `engine/core/context.py` | — | T1.69, T1.70 |


---

## 3. Architectural Patterns — Context, Factories & Orchestration Hardening (Appendix F) Tasks


> Source: [§15](phase_1_foundation_workplan.md#15)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.54 | Implement TelemetryHeartbeat | Create `eks/engine/core/telemetry.py` for document processing checkpoints per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.58 | Implement Checkpoint State Serialization | Add checkpoint state serialization/deserialization for resume capability per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.59 | Implement ParserFactory | Create `eks/engine/core/factories.py` with file type routing per Appendix F | R26 | ✅ | 2026-06-30 |
| T1.60 | Implement HealthScorerFactory | Factory with config-driven dimensions per Appendix F | R51 | ✅ | 2026-06-30 |
| T1.61 | Implement StructureDetectorFactory | Factory for structure detector instantiation per Appendix F | R99 | ✅ | 2026-06-30 |
| T1.62 | Update Engines to Use Factories | Refactor existing engines to use factories instead of direct instantiation per Appendix F | R26 | ✅ | 2026-06-30 |
| T1.63 | Enhance PipelineOrchestrator with Checkpoints | Add 5 clear phases (A-E) with telemetry heartbeat integration per Appendix F | R57 | ✅ | 2026-06-30 |
| T1.64 | Implement Phase Rollback Capability | Add checkpoint restoration mechanism for failed phases per Appendix F | R57 | ✅ | 2026-06-30 |


---

## 4. Core Schema Suite (base/setup/config + fragment schemas) Tasks


> Source: [§16](phase_1_foundation_workplan.md#16)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.3 | Design canonical schema — base | **File**: `eks_base_schema.json`<br>**Layer**: Definitions (`$defs`) — Store reusable fragments and type definitions<br>**Standard**: Flat structure, array of objects, `additionalProperties: false`<br>**Key items**: `discipline_code` (enum), `revision_id` (regex `^[A-Z0-9]{1,2}$`), `ProjectMetadata`, `DocumentMetadata`, `EngineeringObject`, `SourceTraceability`; **Asset Schema Fragments (R36, R39)** — 13 fragments: `item_core_def`, `process_conditions_def`, `manufacturer_def`, `asset_lifecycle_def`, `control_system_def`, `piping_connection_def`, `valve_internals_def`, `actuator_def`, `rotating_equipment_def`, `instrumentation_def`, `pipeline_route_def`, `specialist_equipment_def`, `motor_control_def`; `conditional_fragments` for zero-code extensibility. | R06, R07, R08, R09 | ✅ COMPLETE | — | 2026-06-15 (U006) | `eks_base_schema.json` | — | — |
| T1.4 | Design canonical schema — setup | **File**: `eks_setup_schema.json`<br>**Layer**: Declarations (`properties`) — Define structure and metadata of system configuration<br>**Standard**: One-to-one match with `eks_base_schema.json` via `$ref`<br>**Sections**: `global_paths`, `registry`, `parsers`, `embedding`, `vector_store`, `graph_db`, `logging`, `asset_type_registry` | R06, R07, R08, R09 | ✅ COMPLETE | — | 2026-06-15 (U006) | `eks_setup_schema.json` | — | T1.3 |
| T1.5 | Design canonical schema — config | **File**: `eks_config.json`<br>**Layer**: Config (values) — Store actual runtime values used by the EKS engine<br>**Standard**: Validates strictly against `eks_setup_schema.json`<br>**Key values**: `registry.type`: "duckdb", `registry.connection`: "output/eks_registry.db", `embedding.active_provider`: "openai", `vector_store.collection_name`: "eks_chunks", `logging.default_level`: 1, `project_assets.WSD11.datadrop_path`: "data/twrp/datadrop/Datadrop Summary.xlsx" | R06, R07, R08, R09 | ✅ COMPLETE | — | 2026-06-15 (U006) | `eks_config.json` | — | T1.4 |
| T1.6 | Implement schema loader | Load and resolve base/setup/config with $ref support (reuse dcc pattern) | R06 | ✅ COMPLETE | — | 2026-06-15 (U008) | `schema_loader.py` | — | T1.5 |
| T1.42 | Project code fragment schema | Create `eks_project_code_schema.json` with valid project codes (131101, 131242, 999999). Follow DCC fragment pattern: draft-07, $id URI, allOf/$ref to base, additionalProperties: false. | R06 | ✅ | 2026-06-23 |
| T1.43 | Discipline fragment schema | Create `eks_discipline_schema.json` with 21 valid discipline codes (PI, EL, IN, CI, AR, ME, CL, BQ, QA, VI, M3, DR, DS, SP, RT, CD, CH, PP, IM, SG, NA). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.44 | Department fragment schema | Create `eks_department_schema.json` with 11 valid department codes (PRJ, QAQC, CNT, PRC, PIP, CSA, ELE, ICA, MEC, BIM, NA). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.45 | Facility fragment schema | Create `eks_facility_schema.json` with 12 valid facility prefixes (WSD11, WSW41, WST02, WIL00, WIL11, WIL12, WIL13, WIL22, WIL23, WSB01, WSE00, WST01). Follow DCC fragment pattern. | R06 | ✅ | 2026-06-23 |
| T1.46 | Update base schema, config, and setup for fragment integration | Add `project_entry_def`, `department_entry_def`, `facility_entry_def` to `eks_base_schema.json`. Replace P123/P456 with real WSD11 codes in `eks_config.json`. Add `$ref` to fragment schemas. Add property declarations for new registries in `eks_setup_schema.json`. Resolve I005. | R06 | ✅ | 2026-06-23 |
| T1.47 | Add fragment schema validation tests | Add 6 new tests: fragment files exist, base definitions exist, fragment required fields, no placeholder data, config has $ref, setup has new properties. Update test_project_scoped_config. 59/59 tests pass. | R06 | ✅ | 2026-06-23 |
| T1.50 | Base schema SSOT enforcement | (1) Strip `document_relationship_trigger_map` to shape-only — remove `properties`/`required` with hardcoded enum values (I031); (2) Move `revision_id` from `eks_base_schema.json` to `eks_doc_base_schema.json`, add `revision_validation` 3-layer chain to doc set, remove `revision_pattern` from `project_rules_def` (I032); (3) Update `ConfigRegistry` to resolve `$ref` entries on-the-fly; (4) Update `schema_inheritance_chain.md` v1.6. 114/114 tests pass. | R06, R35 | ✅ Complete | 2026-06-24 |
| T1.51 | Asset Context Fragment — Extensible Location & System Hierarchy + Explicit Relationship Schema | Add `asset_context` fragment to `eks_asset_base_schema.json` with: (1) `project_context` — project_code, phase, client, contractor; (2) `location_hierarchy` — **extensible** nested hierarchy (site→area→unit→building→floor→room) with `additionalProperties: true` for future levels (zone, bay, skid, module) without schema migration; unit is primary anchor. **Location is a context to be linked (LOCATED_IN edges), no specific location keytag generated**; (3) `system_hierarchy` — **extensible** functional decomposition (system_code→subsystem_code) with `additionalProperties: true` for future subsystem levels; discipline + utility_category enums; (4) `asset_relationships` — explicit asset-to-asset links (connects_to, flows_from, flows_to, controlled_by, energized_by, has_actuator, instrumented_by, references_dwg, governed_by_spec, installed_at, set_point_in, redundant_to, spare_for); (5) `document_relationships` — asset↔document links (references_documents, supersedes, produced_by, approved_by, inspected_by); (6) `lifecycle_context` — commissioning_status, operational_status, criticality, safety_class (SIL), redundancy_group, maintenance_strategy, regulatory_tag. Update `eks_asset_setup_schema.json` fragment enum + `fragment_category_registry` (functional). Populate `asset_context` for all 14 AT_ types in `eks_asset_config.json` with column normalization mappings. Version bumps: base→1.3.0, setup→1.3.0, config→1.4.0 per AGENTS.md §27. | R36 | ✅ | 2026-06-25 |




---

## 5. Asset Schema — Universal Plant Item (R36/R39) Tasks


> Source: [§17](phase_1_foundation_workplan.md#17)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.17 | Design asset schema — fragment definitions | Add 13 reusable asset fragments to `eks_asset_base_schema.json` (item_core, process_conditions, manufacturer, asset_lifecycle, control_system, piping_connection, valve_internals, actuator, rotating_equipment, instrumentation, pipeline_route, specialist_equipment, motor_control) | R36 | ✅ | — |
| T1.18 | Design asset schema — type registry | Add `asset_type_registry` to `eks_setup_schema.json`; map all 14 AT_ categories to their fragment compositions in `eks_config.json` | R36 | ✅ | — |
| T1.19 | Update config with asset source | Add project asset datadrop path and per-project config to `eks_config.json` | R36 | ✅ | — |
| T1.20 | Update asset schema files for R39 + gap analysis | (1) `eks_asset_base_schema.json`: add `specialist_equipment` and `motor_control` fragment `$defs`; expand `actuator`, `rotating_equipment`, `instrumentation`, `valve_internals` with gap analysis fields. (2) `eks_asset_setup_schema.json`: update fragment enum to 13 names; add `conditional_fragments` object structure to registry. (3) `eks_asset_config.json`: add `conditional_fragments` entries for AT_EQUIP and AT_MOTOR; add missing column normalization entries (manufacturer_fax, valve_internal_type, dual alarm TP columns) | R36, R39 | ✅ | — |


---

## 6. Ontology Integration (R44, ISO 15926) Tasks


> Source: [§18](phase_1_foundation_workplan.md#18)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.23 | Design ontology schema | `eks_ontology_schema.json`: validate classes, properties, and relationship types; include SHACL constraint definitions for data quality rules (e.g. every PumpTag must have unit and service) | R44 | ✅ | — |
| T1.24 | Create ontology config | `eks_ontology_config.json`: define classes, inheritance, and relationship properties (ISO 15926 aligned) | R44 | ✅ | — |
| T1.25 | Extend schema loader | Update `schema_loader.py` to validate and load the ontology registry dynamically at startup | R44 | ✅ | — |
| T1.26 | Write ontology unit tests | Test ontology schema validation and loading in `test_phase1.py` | R44 | ✅ | — |
| T1.27 | Plan alias-aware ontology mapping | Define alias support and `ontology_class_map` design for `eks_asset_config.json`; document AT_ code-to-ontology class mapping and alias-driven asset onboarding; hold actual schema/code updates pending approval | R44 | ✅ | — |
| T1.28 | Embedded Relationship Metadata | Update `eks_asset_base_schema.json` to annotate relationship-triggering fields; update `eks_asset_config.json` with `relationship_triggers` section mapping fields to graph edges (Flow, Power, Control, Governance, Set Points) | R44 | ✅ | — |
| T1.29 | Document Ontology & Mapping Metadata | Update `eks_ontology_config.json` with Document hierarchy (Drawing, Spec, Manual) and lifecycle relationships (SUPERSEDES, SUPPLEMENTS, REFERENCES_DOC); update `eks_asset_config.json` with `document_triggers` section mapping registry fields to graph edges. | R44 | ✅ | — |


---

## 7. Logging, Errors & Health Scoring (R33/R34/R51) Tasks


> Source: [§19](phase_1_foundation_workplan.md#19)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.13 | Implement tiered logger | `logger.py`: levels 0–3, debug object, trace table, depth counter | R33, R34 | ✅ | — |
| T1.30 | Error Code Taxonomy Schema | Create `eks/config/schemas/eks_error_code_base.json` (error code format definitions, severity levels, phase/module/function codes) and `eks/config/schemas/eks_error_config.json` (full system + data error catalog including structural error codes P3-E-E-0010–0017). Follow DCC pattern from `dcc/config/schemas/error_code_base.json`. | R51 | ✅ | — |
| T1.31 | Pipeline Message Catalog Schema | Create `eks/config/schemas/eks_message_base.json` (message ID format, verbosity levels, categories) and `eks/config/schemas/eks_message_config.json` (milestone, status, progress, warning, error message templates including structural messages). Follow DCC pattern from `dcc/config/schemas/pipeline_message_base.json`. | R51 | ✅ | — |
| T1.32 | Error & Message Manager Modules | Create `eks/engine/core/error_manager.py` (handle_system_error, handle_data_error, fail-fast check, error summary) and `eks/engine/core/message_manager.py` (catalog lookup, template hydration, verbosity control). Create `eks/engine/core/health_scorer.py` (6-dimension scoring: completeness, confidence, structural, source, xref, consistency) and `eks/engine/core/structure_detector.py` (PDF structural element detection). Add `document_elements` table to `registry.py`. Follow DCC pattern from `dcc/workflow/core_engine/errors/error_manager.py`. | R51 | ✅ | — |
| T1.41 | Fix error/message schemas 3-layer pattern | Create `eks_error_setup_schema.json` and `eks_message_setup_schema.json` (allOf + $ref to base). Clean config files (remove $schema/$id/title/description/version). Update `schema_loader.py` with error/message validation methods. Resolve I014. | R51 | ✅ | 2026-06-22 |
| T1.68 | Wire ErrorManager/MessageManager into pipeline orchestrator | Call `ErrorManager.handle_system_error()` and `ErrorManager.handle_data_error()` at runtime in `pipeline_orchestrator.py`: emit D4/D5 error codes on phase failures and per-file parse failures; call `MessageManager.format()` for D6 milestone messages at phase start/complete. Resolves AGENTS.md §6.9 violation. | R51 | ✅ Done | T1.70, T1.72 |
| T1.69 | Add run_id correlation ID to EKSLogger and _LogCapture | Add `run_id: Optional[str]` param to `EKSLogger.__init__`; prepend `[run_id]` to all log entries. In `phase1_server.py` `_handle_pipeline_start()`, pass `job_id` as `run_id` to `_LogCapture` and `PipelineOrchestrator` logger so all log entries for a job share a traceable ID (universal §4.12 Structured Logging & Correlation IDs). Persist per-run log to `eks/output/debug_log.json` (T1.76). | R33, R51 | ✅ | T1.76 |
| T1.71 | Replace raw duckdb.connect in _update_doc_status | Replace `__import__('duckdb').connect(str(self.registry.db_path))` in `pipeline_orchestrator.py` `_update_doc_status()` with a call to a new `registry.update_document_status(doc_id, status, confidence, notes)` method that uses the existing `_with_retry()` wrapper and the registry singleton connection. | R02 | ✅ Done | T1.68 |
| T1.75 | Activate ErrorManager/MessageManager in phase1_server | **Closes silent T1.68 gap**: `phase1_server.py` constructs `PipelineOrchestrator` WITHOUT passing `error_manager`/`message_manager`, so the T1.68 wiring is dead code in production. Construct `ErrorManager(registry.logger)` and `MessageManager(...)` loading `eks_error_config.json`/`eks_message_config.json`, and pass them to `PipelineOrchestrator(...)`. Verify D5/S-PIP error codes and D6 status messages appear in `GET /api/v1/pipeline/logs/{job_id}`. | R51, R99 | ✅ | T1.68, T1.76 |
| T1.76 | Persist debug/message/status JSON to eks/output | Per AGENTS.md §7/§19, generate machine-parseable run artifacts in `eks/output/`: (1) `debug_log.json` — pass `debug_file=eks/output/debug_log.json` to `EKSLogger("Phase1Server")` and call `save_debug_log()` at end of `_run()`; (2) `pipeline_status_{job_id}.json` — write final `_job_state[job_id]` summary; (3) `pipeline_messages_{job_id}.json` — write MessageManager/ErrorManager catalog output for the run. Mirrors DCC `dcc/output/` artifact convention. | R51, R99 | ✅ | T1.69, T1.75 |
| T1.99.35 | Harden universal `BaseMessageManager` as pipeline-messaging SSOT (I105) | In `common/library/core/messages/message_manager.py`: add optional `icon` support, keep `print()` fallback, keep verbosity clamp. Add protected hook `_make_default_logger()`. **10 new common tests pass.** | R51, R99 | ✅ COMPLETE | I078, I105 | — | `common/library/core/messages/message_manager.py` | — | — |
| T1.99.36 | Make `eks/engine/core/message_manager.py` a thin subclass of `BaseMessageManager` (I105) | `class MessageManager(BaseMessageManager)` with `_catalog_filename = "eks_message_config.json"`. Remove duplicated `get`/`show`/`get_message`/`set_verbosity`/`get_all_messages` logic. **All 7 EKS MessageManager tests green.** | R51, R99 | ✅ COMPLETE | I105 | — | `engine/core/message_manager.py` | — | T1.99.35 |
| T1.99.37 | Fix `eks_engine_pipeline.py:505` to use the EKS `MessageManager` subclass (I105) | Change line 505 from `BaseMessageManager(...)` to `MessageManager(...)`. Fixes silent wrong-catalog bug. **Wrong-catalog bug resolved.** | R51, R99 | ✅ COMPLETE | I105 | — | `eks_engine_pipeline.py` | — | T1.99.36 |
| T1.99.38 | Tests for universal message module + EKS regression (I105) | Common test: `BaseMessageManager` subclass with fake logger. Confirm EKS suite green. **10+7 gap tests green; 278/278 suite green.** | R51, R99 | ✅ COMPLETE | — | — | `common/library/core/messages/tests/`, `test/` | — | T1.99.35–36 |
| T1.99.39 | Knowledge base + logs update for messaging consolidation (I105) | Update `eks/knowledge.json`; add entry to `update_log.md`. **v3.74 recorded.** | R51, R99 | ✅ COMPLETE | I105 | — | `knowledge.json`, `update_log.md` | — | T1.99.35–38 |
| T1.99.40 | Make `EKSPipelineContext` extend `common.library.core.pipeline.BasePipelineContext` (L06) | Change `class EKSPipelineContext` to `class EKSPipelineContext(BasePipelineContext)`. Add `_from_dict()` / `_to_dict()`. **Implements abstract contract, removed duplicates.** | R99 | ✅ COMPLETE | I106 | — | `engine/core/context.py` | — | — |
| T1.99.41 | Populate context fields from `EngineInput`+bootstrap in orchestrator (I106) | `PipelineOrchestrator.initialize_context()`: accept `parameters`, `config_registry`, `schema_registry`. Route through `_populate_context_data()`. **Accepts parameters, config_registry, schema_registry, checkpoint_state.** | R99 | ✅ COMPLETE | I106 | — | `pipeline_orchestrator.py` | — | T1.99.40 |
| T1.99.42 | Surface `EKSPipelineContext` through `run_pipeline()` (I106) | `run_pipeline(...)` accepts optional `context` param; passes to orchestrator; includes context in return dict. **Backward compat preserved.** | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | — | T1.99.40–41 |
| T1.99.43 | `main()` builds + seeds `EKSPipelineContext` from `EngineInput` and threads through `run_pipeline()` (I106, DCC-faithful) | `main()` constructs `ctx = EKSPipelineContext()`; seeds from `ei`; passes `context=ctx` to `run_pipeline()`; extracts `EngineOutput` from returned context. | R99 | ✅ COMPLETE | I106 | — | `eks_engine_pipeline.py` | — | T1.99.42 |
| T1.99.44 | Tests + knowledge base + logs update for context threading (I106) | Integration test `test_run_pipeline_surfaces_context()`. Update `knowledge.json`, `update_log.md` (U163), `issue_log.md`. | R99 | ✅ COMPLETE | I106 | U163 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | — | T1.99.40–43 |
| T1.99.45 | I107: Fold OS detection + param/level/eks_root resolution into `bootstrap_pipeline()` | Move `detect_os()` into `bootstrap_pipeline()`, drop 2nd config load. **L133 OS detection, L136 CLI parse, L157–163 log-level, L160 eks_root.** | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | — |
| T1.99.46 | I107: Fold CLI parse + `data_dir` precedence into `bootstrap_pipeline()` | Accept `args`; run `parse_eks_cli()` internally; resolve `data_dir` with CLI>Schema>Native precedence. **L136 parse, L168–175 data_dir.** | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | T1.99.45 |
| T1.99.47 | I107: Single path resolution source (fix Defect A) | ONE `resolved_paths` dict; `main()` + `EKSPipelineContext.paths` both read from it. **L166 single resolve.** | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | T1.99.45–46 |
| T1.99.48 | I107: Single `MessageManager` instance (fix Defect B) | `mm = MessageManager(...)` created once in bootstrap; `main()` reuses `boot["mm"]`. **L178 creates mm, L559/569 reuses.** | R99 | ✅ COMPLETE | I107 | — | `eks_engine_pipeline.py` | — | T1.99.47 |
| T1.99.49 | I107: Tests + knowledge base + logs for bootstrap completeness | 4 integration tests added (`TestI107BootstrapCompleteness`). 23/23 pipeline tests pass. **`knowledge.json` v2.7.0, `update_log.md` U165.** | R99 | ✅ COMPLETE | I107 | U165 | `test/`, `knowledge.json`, `update_log.md`, `issue_log.md` | — | T1.99.45–48 |


---

## 8. Document Registry & Revision Management (R02/R21/R22/R29) Tasks


> Source: [§20](phase_1_foundation_workplan.md#20)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.7 | Implement document registry | CRUD interface for document metadata backed by DuckDB/PostgreSQL | R02, R29 | ✅ | — |
| T1.8 | Implement revision management | Preserve all revisions; is_latest flag; revision chain lookup | R21, R22 | ✅ | — |
| T1.21 | Document Registry Remediation (G1-G3) | Add `source_type` column (G1); implement column allowlist for `list_documents` (G2); migrate `get_revision_history` sorting to SQL `ORDER BY` (G3). Update schema files accordingly. | R02 | ✅ | — |
| T1.22 | Extended Document Metadata | Implement 11 new fields (Accountability, Quality, Technical groups); support `asset_tags` as JSON array; implement `ALTER TABLE` migration logic in `registry.py` for schema evolution. | R02 | ✅ | — |


---

## 9. Document Parsers — PDF/DOCX/XLSX (R01/R26) Tasks


> Source: [§21](phase_1_foundation_workplan.md#21)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.9 | Implement abstract base parser | `base_parser.py`: plug-in interface with parse(), extract_metadata() | R01, R26 | ✅ | — |
| T1.10 | Implement PDF parser | `pdf_parser.py`: extract text, metadata, page numbers | R01, R26 | ✅ | — |
| T1.11 | Implement XLSX parser | `xlsx_parser.py`: extract sheet data, metadata | R01, R26 | ✅ | — |
| T1.12 | Implement DOCX parser | `docx_parser.py`: extract text, metadata, sections | R01, R26 | ✅ | — |


---

## 10. Document Schema v2 — 3-Layer Reorganization (R52/R53) Tasks


> Source: [§22](phase_1_foundation_workplan.md#22)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.34 | Reorganize document schema (3-layer) | Create `eks_doc_base_schema.json` (document + element definitions), `eks_doc_setup_schema.json` (table declarations, extraction rules, health scoring schema), `eks_doc_config.json` (ontology triggers, health score tiers, element expectations). Move `document_metadata_def` and `project_metadata_def` from `eks_base_schema.json` to `eks_doc_base_schema.json`. Add `document_element_def` (7 columns) to doc base schema. Update `schema_loader.py` with doc schema loading and validation. Update `eks_base_schema.json` to remove doc defs. Add 6 new tests in `test_phase1.py`. Registry config stays in `eks_config.json` (pipeline-level setting). | R52 | ✅ | 2026-06-22 |
| T1.35.1 | Enhance doc base schema — enums & missing fields | Add `doc_id_format`, `document_type_code` enum (7 codes), `file_type_code` enum (5), `element_type_code` enum (8); add `file_path`, `ingested_at`, `file_type` to `document_metadata_def`; type `document_element_def.element_type` with enum ref | R53 | ✅ | 2026-06-22 |
| T1.35.2 | Enhance doc setup schema — registries | Add `document_type_registry`, `file_type_registry`, `element_type_registry` property declarations; update `element_expectations` key schema to use document type codes; add all three registries to `required` | R53 | ✅ | 2026-06-22 |
| T1.35.3 | Enhance doc config — registry values | Populate `document_type_registry` (7 entries with ontology class + expected file types), `file_type_registry` (5 entries with parser class + MIME), `element_type_registry` (8 entries with description + source + Phase 2/3 use); refactor `element_expectations` keys from A-E → DWG/PI-PID/SPC/RPT/MAN/DS/OM | R53 | ✅ | 2026-06-22 |
| T1.35.4 | Update schema loader — validate new registries | Add `_validate_doc_registries()` for enum value checks, registry completeness, file type parser class references in `load_all()` | R53 | ✅ | 2026-06-22 |
| T1.35.5 | Update tests — new validation tests | Add tests: `test_doc_type_enum`, `test_doc_type_registry`, `test_file_type_registry`, `test_element_type_registry`, `test_element_expectations_keys`, `test_doc_metadata_complete_fields` | R53 | ✅ | 2026-06-22 |
| T1.35.6 | Update appendix B — document registry schema | Add B3.2 Document Type Registry, B3.3 File Type Registry, B3.4 Element Type Registry sections; update B3 schema table with `file_type` column; version bump to v0.9 | R53 | ✅ | 2026-06-22 |


---

## 11. Pipeline Orchestration (R54–R58/R57) Tasks


> Source: [§23](phase_1_foundation_workplan.md#23)


### Task Breakdown

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.36 | Auto-DDL from schema | Create `eks/engine/core/schema_to_ddl.py`: read `document_metadata_def` + `project_metadata_def` + `document_element_def` from `eks_doc_base_schema.json` and generate `CREATE TABLE` / `ALTER TABLE` SQL. Refactor `registry.py` to use generated DDL instead of hard-coded DDL. Add `sync_schema()` method. | R54 | ✅ | 2026-06-22 |
| T1.37 | File scanner | Create `eks/engine/core/file_scanner.py`: walk project directory; match files to `file_type_registry[].extension`; validate against `document_type_registry[].expected_file_types`; register placeholder rows in `documents` table with `extract_status = 'pending'`, `file_path`, `file_type`, filename-parsed metadata. | R55 | ✅ | 2026-06-22 |
| T1.38 | Parser router | Create `eks/engine/parsers/parser_router.py`: map `file_type` → `file_type_registry[].parser_class`; instantiate parser; call `parse()`, `extract_metadata()`, `StructureDetector.detect()` in sequence; return structured results. | R56 | ✅ | 2026-06-22 |
| T1.39 | Pipeline orchestrator | Create `eks/engine/core/pipeline_orchestrator.py`: coordinate Phase A (scan → register placeholders), Phase B (route → parse → detect → score → update), Phase C (flag for review). Error handling, logging, batch processing. | R57 | ✅ | 2026-06-22 |
| T1.40 | Manual review workflow | Create review surface: query `documents` where `extract_status != 'success'` or `extraction_confidence < 0.70`. Support metadata correction, element confirmation, score recalculation, document lock. Update `test_phase1.py` with tests. | R58 | ✅ | 2026-06-22 |
| T1.72 | Enforce DiscoveryInput/Output and ParserInput/Output contracts in orchestrator | Wrap `run_phase_a()` to construct `DiscoveryInput` and validate `DiscoveryOutput`; wrap `_process_file()` to construct `ParserInput` and validate `ParserOutput` — enforcing the `BaseEngine.run()` contract defined in `base.py` and `io_contracts.py`. | R57 | ✅ | — |
| T1.73 | Persist checkpoint JSON to disk in _run() thread | In `phase1_server.py` `_run()`, after each `_set_phase()` call, invoke `orchestrator.save_checkpoint(phase, checkpoint_path=PRJ_DIR / "eks" / "output" / f"checkpoint_{job_id}.json")` so checkpoint state survives server restarts (universal §4.11 Idempotency & Checkpointing). Resume from last completed phase on re-run. | R57 | ✅ | — |


---

## 12. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89) Tasks


> Source: [§24](phase_1_foundation_workplan.md#24)


### Initiation Integrity (T1.77–T1.78)

> Relocated from [§24 — Initiation Integrity (T1.77–T1.78)](phase_1_foundation_workplan.md#24-initiation-integrity-hardening--harmonization-t177t189) of the main workplan. Canonical source is now here.

| ID | Task | Details | Scope | Status | Issues | Updated on | Files | Priority | Depends On |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| T1.77 | Wire ProjectSetupValidator into fail-fast gate | `ProjectSetupValidator.validate_all()` + `get_readiness_status()` wired into `phase1_server._run()` fail-fast gate; `--debug`/`--level` CLI flags with effective-level logic; `data_dir` existence + `recursive` bool validated before concurrency guard. 8 validator unit tests + 3 server integration tests. 202/202 pass. | R99 | ✅ COMPLETE | — | 2026-07-09 (U122) | `phase1_server.py`, `setup_validator.py`, `test/test_setup_validator.py` | — | T1.65 |
| T1.78 | DCC gap remediation (eks.yml path, input readability, dep probe) | Remediation of DCC gaps — `eks.yml`→`eks/eks.yml` path fix, input-file readability (G2), dependency probe + output-path validation (G3/G4), `--skip-readiness` override (G5), error code constants (G7); fixed pre-existing `_LogCapture.level` bug. 207/207 pass. | R99 | ✅ COMPLETE | I079 | 2026-07-09 (U124) | `phase1_server.py`, `setup_validator.py`, `eks.yml` | — | T1.77 |


### Initiation Schema-Driven Hardening (T1.79–T1.83)

| Task | I-Ref | Description | Status |
| :--- | :---- | :---------- | :----: |
| T1.79 | I079 | Wire `P1-SETUP-*` error codes into `validate_all()` results; raise readiness failure via `ErrorManager.handle_system_error("P1-SETUP-READINESS")` | ✅ |
| T1.80 | I080 | Derive output/eks.yml paths from `global_paths` + schema config | ✅ |
| T1.81 | I081 | Remove hardcoded fallback lists duplicating `eks_config.json` (SSOT) | ✅ |
| T1.82 | I082/I083 | Honor `validation_options.auto_create_folders` + schema-driven input defaults | ✅ |
| T1.83 | I084 | Make `eks` package root schema-driven via `global_paths.eks_root` (10× `PRJ_DIR/"eks"` literals replaced) | ✅ |


---

## 13. Initiation Schema & Validation Harmonization (T1.84–T1.89) Tasks

> **Relocated from [§25 — Phase 1.3 — Initiation Schema & Validation Harmonization (T1.84–T1.89)](phase_1_foundation_workplan.md#25-phase-13--initiation-schema--validation-harmonization-t184t189)** of the main workplan (v4.8). Canonical source is now here.

**Source workplan (archived)**: [phase_1.3_initiation_harmonization_workplan.md](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
**Status**: ✅ COMPLETE — T1.84–T1.89 all implemented. Universal `ValidationManager` in `common/library/utility/validation/`. EKS `project_setup` schema reshaped to DCC-aligned object model. DCC itself NOT modified (deferred follow-up).

### 13.1 Objective

Achieve **schema-design consistency** and **code-module universality** for project-setup validation, so that EKS and (later) DCC validate project structure through one shared, well-tested module and through schemas that follow the same shape. EKS's AGENTS.md §7-mandated folder names are preserved — only the *schema shape* (not the folder names) aligns with DCC.

### 13.2 Task Breakdown

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| R99 | Foundation & Compliance | Initiation Harmonization | Universal `ValidationManager` + EKS `project_setup` reshape to DCC object model | T1.84–T1.89 | T1.67, T1.77, T1.78, T1.79–T1.83 |
| T1.84 | Foundation | Universal ValidationManager | Create `common/library/utility/validation/manager.py` (path-agnostic) — `validate_folders`, `validate_named_files`, `validate_environment`, `validate_dependencies`, `validate_discovery_rules`, `validate_project_setup` | ✅ DONE | R99 |
| T1.85 | Schema | EKS schema reshape | Replace flat-array defs with DCC-aligned object defs (8 new defs) in `eks_base_schema.json` v1.7.0 + `eks_setup_schema.json` v1.4.0 | ✅ DONE | T1.84, T1.67 |
| T1.86 | Schema | Extract project_setup config | Create `eks_project_setup_config.json` v1.0.0; `eks_config.json` v1.5.0 references it | ✅ DONE | T1.85, T1.67 |
| T1.87 | Code | EKS validator adapter | `setup_validator.py` v0.7 thin adapter delegating to universal module; preserves `P1-SETUP-*` + ErrorManager wiring | ✅ DONE | T1.84, T1.86 |
| T1.88 | Testing | Test migration + coverage | `test_setup_validator.py` (19 tests) migrated; `test_validation_manager.py` (20 tests) created; full suite 235/235 green | ✅ DONE | T1.87 |
| T1.89 | Docs | Workplan/log/knowledge update | Workplan, `knowledge.json` v2.3.0, `update_log` (U130), `issue_log` (I085 resolved), universal architecture doc, foundation report | ✅ DONE | T1.84–T1.88 |

### 13.3 Files and Modules (T1.84–T1.89)

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

### 13.4 Success Criteria

- [x] EKS `project_setup` schema shape matches DCC's (object arrays with metadata; per-folder `auto_created`).
- [x] Reusable `ValidationManager` exists in `common/library/utility/validation/` and is path-agnostic (usable by EKS and later DCC).
- [x] EKS validation runs through the universal module; `phase1_server.py` readiness gate, `P1-SETUP-*` codes, and `ErrorManager` wiring behaviorally unchanged.
- [x] Full EKS test suite green (235/235); universal module has its own tests (20).
- [x] DCC left untouched (deferred follow-up).
- [x] Workplan, `knowledge.json`, `update_log`, `issue_log`, and universal architecture doc updated.

### 13.5 References

- [Phase 1.3 Initiation Harmonization Workplan (archived)](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
- [Phase 1 T1.79–T1.83 Report (archived)](../archive/phase_1_t179_t183_report.md) — RP-EKS-P1-T179-001
- [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md) — §4.9 Project Setup Validation, §4.9.1 Initiation Integrity Layers
- DCC reference (not modified): `dcc/config/schemas/project_setup_base.json`, `project_setup.json`, `project_config.json`; `dcc/workflow/initiation_engine/core/validator.py`; `dcc/utility_engine/validation/validation_manager.py`
- EKS issue: I085 (schema-design divergence between EKS and DCC `project_setup`)


---

## 14. Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95) Tasks

> **Relocated from [§26 — Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)](phase_1_foundation_workplan.md#26-initiation-config-flattening--dcc-project_config-pattern-t190t195)** of the main workplan (v4.8). Canonical source is now here.

**Objective**: Align EKS `eks_config.json` with DCC `project_config.json` — store the actual setup values (`folders` / `root_files` / `schema_files` / `environment` / `dependencies` / `project_metadata` / `discovery_rules`) at the **top level** instead of nested under a `project_setup` wrapper. This makes the universal `ValidationManager` (and a future universal schema loader) work for both projects with **zero per-project branching**, completing the Phase 1.3 universality goal, and removes the orphaned `eks_project_setup_config.json` (T1.86 artifact).

### 14.1 Task Breakdown

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.90 | Schema/Config | Flatten `project_setup` in `eks_config.json` | Move 7 setup keys to top level; remove `project_setup` wrapper; fix title note (drop "T1.86 extracted") | ✅ DONE | T1.67, T1.85, T1.86 |
| T1.91 | Schema | Update `eks_setup_schema.json` | Remove `project_setup` wrapper property; declare the 7 setup keys top-level (reuse `eks_base_schema.json` defs); bump v1.5.0 | ✅ DONE | T1.90 |
| T1.92 | Code | Update `setup_validator.py` adapter | Read setup from top-level config (DCC pattern) with `project_setup` fallback; keep public API, P1-SETUP-* codes, ErrorManager wiring | ✅ DONE | T1.91 |
| T1.93 | Code | Update `phase1_server.py` call site | `_cfg.get("project_setup", _cfg)` — flatten-aware | ✅ DONE | T1.92 |
| T1.94 | Cleanup | Delete orphan `eks_project_setup_config.json` | Archive first per AGENTS.md §5.3 | ✅ DONE | T1.86 |
| T1.95 | Testing | Tests + suite green | Update `test_setup_schema_has_project_setup`; run full EKS suite (236 pass) | ✅ DONE | T1.92–T1.94 |

### 14.2 Success Criteria
- [x] `eks_config.json` has setup values top-level (no `project_setup` wrapper), matching DCC `project_config.json`.
- [x] `eks_setup_schema.json` declares the 7 setup keys top-level (no `project_setup` property); `additionalProperties: false` preserved.
- [x] `setup_validator.py` reads setup from top-level config with backward-compat `project_setup` fallback; public API + P1-SETUP-* codes + ErrorManager wiring unchanged.
- [x] `phase1_server.py` is flatten-aware.
- [x] `eks_project_setup_config.json` removed (archived); no dangling references.
- [x] Full EKS suite green (236/236).


---

## 15. Schema Discovery & Registration — Discovery-Driven Loading (T1.96) Tasks

> **Relocated from [§27 — Schema Discovery & Registration — Discovery-Driven Loading (T1.96)](phase_1_foundation_workplan.md#27-schema-discovery--registration--discovery-driven-loading-t196)** of the main workplan (v4.8). Canonical source is now here.

**Objective**: Add discovery-driven schema registration to EKS by (1) extracting the shared `discover_schema_files()` function from DCC `ref_resolver.py:164-230` into the `common/` library, (2) adding `discovery_rules` data to `eks_config.json`, (3) refactoring `schema_loader.py` to use config-driven loading (explicit `schema_files` + `discovery_rules` glob), and (4) wiring `ValidationManager.validate_discovery_rules()` into `setup_validator.py`. Closes I087.

**Rationale**: Currently `schema_loader.py` hardcodes 22 filenames — adding a new schema set requires source code changes. DCC's `_extract_registered_schemas()` implements a reusable pattern: explicit `schema_files` merge with glob-based `discovery_rules`. Extracting this to `common/` makes it available to both projects and future phases.

### 15.1 Task Breakdown

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.96.1 | Common | Extract `discover_schema_files()` to `common/` | Extract the core discovery loop (glob walk + merge with explicit `schema_files`) from DCC `ref_resolver.py` into a standalone function in `common/library/loader/`. Function signature: `discover_schema_files(project_setup: dict, project_root: Path) -> dict`. Also extracted `safe_resolve()` and `find_schema_file()`. | ✅ COMPLETE | DCC `ref_resolver.py:164-230`, I087 |
| T1.96.2 | Schema/Config | Add `discovery_rules` to `eks_config.json` | Add 5 discovery rules matching existing schema file conventions (`*_base_schema.json`, `*_base.json`, `*_setup_schema.json`, `*_config.json` in `eks/config/schemas/`; `*.json` in `eks/engine/parsers/`). Update `eks_setup_schema.json` if needed. | ✅ COMPLETE | T1.96.1, I087 |
| T1.96.3 | Code | Refactor `schema_loader.py` for config-driven loading | Replace hardcoded 22-filename list: read `schema_files` from config (explicit registration), execute `discovery_rules`, merge results (explicit wins). Keep backward compat. | ✅ COMPLETE | T1.96.1, T1.96.2, I087 |
| T1.96.4 | Code | Wire `validate_discovery_rules()` in `setup_validator.py` | Call `ValidationManager.validate_discovery_rules()` when `discovery_rules` present in config — runs as pre-validation gate before schema loading. | ✅ COMPLETE | T1.96.2, I087 |
| T1.96.5 | Docs | Update `common/universal_pipeline_architecture_design.md` | §4.16 Schema Discovery and Registration Pattern already added. Verify alignment with extracted function. | ✅ COMPLETE | T1.96.1 |
| T1.96.6 | Testing | Tests + suite green | Fixed `*_base.json` pattern gap (missing `eks_error_code_base.json` and `eks_message_base.json`). Full EKS suite 236/236 green. | ✅ COMPLETE | T1.96.1–T1.96.5 |


### 15.2 DCC Function Reuse Mapping

| Sub-Task | Priority | DCC Function | DCC Location | Lines | Role |
| :------- | :------: | :----------- | :----------- | :---: | :--- |
| T1.96.1 | **P0** | `RefResolver._extract_registered_schemas()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 164–256 | Extract → `discover_schema_files()`. Core glob-walk, exclude-filter, merge-with-explicit loop. |
| T1.96.1 | **P0** | `safe_resolve()` | `dcc/workflow/schema_engine/utils/paths.py` | 10–12 | Resolve `project_root / directory_rel` to absolute path. Used at line 221 of `_extract_registered_schemas`. Also present in `dcc/workflow/core_engine/paths/path_core.py:29` and `dcc/workflow/utility_engine/paths/path_resolvers.py:71`. |
| T1.96.1 | P1 | `SchemaCache` (class) | `dcc/workflow/schema_engine/loader/schema_cache.py` | 41–250 | Multi-level cache (L1 mem, L2 disk, L3 session) with TTL + mtime validation. Load-after-discovery caching pattern. |
| T1.96.1 | P1 | `SchemaDependencyGraph.build_graph()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 83–102 | Build adjacency list from `$ref` links in registered schemas — load ordering post-discovery. |
| T1.96.1 | P2 | `SchemaPaths.list_available_schemas()` | `dcc/workflow/core_engine/paths/path_schema.py` | 99–111 | Simple `glob("*.json")` — fallback if full discovery not needed. |
| T1.96.3 | **P0** | `RefResolver._build_uri_registry()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 258–298 | Scan directories for JSON files, extract `$id`, build URI→Path map. Essential for `$ref` resolution post-discovery. |
| T1.96.3 | **P0** | `RefResolver._find_schema_file()` | `dcc/workflow/schema_engine/loader/ref_resolver.py` | 679–705 | Search multiple directories for schema file by name. Replaces EKS `schema_loader.py` two-location hardcoded search. |
| T1.96.3 | P1 | `SchemaLoader.load_schema()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 309–353 | Load by stem name from registered directories with caching — pattern for consuming discovery output. |
| T1.96.3 | P1 | `SchemaLoader._resolve_reference_path()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 282–307 | Multi-fallback path resolution (base → main → CWD). |
| T1.96.3 | P1 | `SchemaLoader.load_json_file()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 276–280 | Generic JSON file loader. |
| T1.96.3 | P1 | `SchemaLoader.set_main_schema_path()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 124–129 | Anchor base_path to schema's parent directory. |
| T1.96.3 | P1 | `SchemaDependencyGraph._extract_dependencies()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 140–184 | Recursive JSON walker extracting all `$ref` targets. |
| T1.96.3 | P1 | `SchemaDependencyGraph.detect_cycles()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 186–226 | DFS cycle detection for dependency graph. |
| T1.96.3 | P1 | `SchemaDependencyGraph.get_resolution_order()` | `dcc/workflow/schema_engine/loader/dependency_graph.py` | 228–262 | Topological sort for load ordering. |
| T1.96.3 | P2 | `SchemaLoader.load_recursive()` | `dcc/workflow/schema_engine/loader/schema_loader.py` | 172–228 | Full recursive load with dependency resolution. |
| T1.96.4 | already in `common/` | `ValidationManager.validate_discovery_rules()` | `common/library/utility/validation/manager.py` | 449–489 | Validates rule payload + directory existence. **Does NOT execute discovery** — validation gate only. |
| T1.96.2 | config only | `project_config.json` data pattern | `dcc/config/schemas/project_config.json` | 41–46 | 4 discovery rules as live example. Schema def already in `eks_base_schema.json:167`. |

### 15.3 Success Criteria
- [x] `discover_schema_files()` exists in `common/library/loader/schema_discovery.py` and returns unified registry dict.
- [x] `eks_config.json` has `discovery_rules` array with 5 rules matching existing schema conventions (incl. `*_base.json` for outlier files).
- [x] `schema_loader.py` reads `schema_files` + `discovery_rules` from config; 22 hardcoded filenames replaced with config-driven loop.
- [x] Path root inconsistency fixed: discovery rules use `eks/config/schemas/...` paths to match actual file locations.
- [x] `setup_validator.py` calls `validate_discovery_rules()` when rules present.
- [x] Full EKS suite 236/236 green.
- [x] `common/universal_pipeline_architecture_design.md` §4.16 references align with implementation.


---

## 16. System Parameters — SSOT Centralization (T1.97) Tasks

> **Relocated from [§28 — System Parameters — SSOT Centralization (T1.97)](phase_1_foundation_workplan.md#28-system-parameters--ssot-centralization-t197)** of the main workplan (v4.8). Canonical source is now here.

**Objective**: Centralize all runtime behavior knobs (`fail_fast`, `log_level`, `debug_mode`, `skip_readiness`, `retry_count`, `retry_delay`, `api_timeout`, `ollama_timeout`, `db_timeout`) into a schema-defined `system_parameters` block in `eks_config.json`. Create a universal `get_system_param()` function in `common/library/config/` that handles both EKS flat-object and DCC array-of-entries shapes. Remove hardcoded equivalents from `phase1_server.py`, `error_manager.py`, `registry.py`, `server.py`. Closes I088.

**Rationale**: Currently these values are scattered across global variables (`phase1_server.py:103-105`), constructor defaults (`error_manager.py:21`), function defaults (`registry.py:326`), and literal constants (`server.py:359,429`). I088 documents this as a SSOT violation versus DCC's `project_config.json → system_parameters` pattern. A universal `get_system_param()` in `common/` makes the fix reusable for DCC and future phases.

### 16.1 Task Breakdown

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.97.1 | Common | Create `common/library/config/__init__.py` | Implemented `normalize_system_parameters(config)` and `get_system_param(config, key, default)` for flat-object, direct-object, and array-of-entry shapes. Exported from `common/library/config/`. | ✅ COMPLETE | I088 |
| T1.97.2 | Schema | Add `system_parameters_def` to `eks_base_schema.json` | Added flat-object definition with typed properties: `fail_fast`, `log_level`, `debug_mode`, `skip_readiness`, `retry_count`, `retry_delay`, `api_timeout`, `ollama_timeout`, `db_timeout`. `eks_base_schema.json` v1.8.0. | ✅ COMPLETE | T1.97.1, I088 |
| T1.97.3 | Schema | Add `system_parameters` property to `eks_setup_schema.json` | Added optional `$ref` to base def. `additionalProperties: false` enforced by `system_parameters_def`. `eks_setup_schema.json` v1.6.0. | ✅ COMPLETE | T1.97.2, I088 |
| T1.97.4 | Config | Add `system_parameters` block to `eks_config.json` | Added instance data matching `system_parameters_def`; consolidated standalone `registry.timeout` into `system_parameters.db_timeout`. `eks_config.json` v1.6.0. | ✅ COMPLETE | T1.97.2, T1.97.3, I088 |
| T1.97.5 | Code | Replace hardcoded values in `phase1_server.py` | Runtime debug/log/readiness/retry globals now initialize from `system_parameters`, with CLI flags retained as explicit overrides. | ✅ COMPLETE | T1.97.1, T1.97.4, I088 |
| T1.97.6 | Code | Replace hardcoded values in `error_manager.py` | `ErrorManager` accepts config and reads `fail_fast` from `system_parameters`, defaulting through `get_system_param()`. | ✅ COMPLETE | T1.97.1, T1.97.4, I088 |
| T1.97.7 | Code | Replace hardcoded values in `registry.py` | `DocumentRegistry` reads `retry_count`, `retry_delay`, and `db_timeout` from `system_parameters`; `_with_retry()` uses instance-configured retry settings. | ✅ COMPLETE | T1.97.1, T1.97.4, I088 |
| T1.97.8 | Code | Replace hardcoded timeouts in `server.py` | `api_timeout` and `ollama_timeout` now read from EKS config via `get_system_param()`. Actual file is `eks/server.py`. | ✅ COMPLETE | T1.97.1, T1.97.4, I088 |
| T1.97.9 | Testing | Tests + suite green | Added `eks/test/test_system_parameters.py`; full EKS suite green. | ✅ COMPLETE | T1.97.1–T1.97.8 |

### 16.2 Success Criteria
- [x] `common/library/config/__init__.py` exports `get_system_param()` and `normalize_system_parameters()`.
- [x] `normalize_system_parameters()` handles EKS flat-object, DCC flat-object, and DCC array-of-entries shapes.
- [x] `eks_base_schema.json` has `system_parameters_def` with all 9 typed properties and defaults.
- [x] `eks_setup_schema.json` has `system_parameters` property with `additionalProperties: false` enforced through the referenced definition.
- [x] `eks_config.json` has `system_parameters` block; `registry.timeout` consolidated into block.
- [x] `phase1_server.py`, `error_manager.py`, `registry.py`, `eks/server.py` read from config via `get_system_param()` / `ConfigRegistry.get_system_param()` for the T1.97 runtime knobs.
- [x] Full EKS suite green; unit tests for normalize + get cover all 3 source shapes.
- [x] I088 closed.

### 16.3 Universal Architecture Elevation (I091)

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.97.10 | Common | Register `config` as architecture-aligned sub-package in `common/library/__init__.py` | Add `config/` to docstring sub-package list, `from . import config`, and `"config"` to `__all__`. | ✅ COMPLETE | I091 |
| T1.97.11 | Docs | Add L15 to universal pipeline architecture inventory | Add L15 row to §2.2 Inventory Table, `config/` to §2.3 Package Structure, and L15 per-library detail to §2.4 in `common/universal_pipeline_architecture_design.md`. | ✅ COMPLETE | I091 |
| T1.97.12 | Docs | Add §3.17 System Parameters Pattern | New design pattern documenting schema-defined runtime behavior knobs, universal normalization helper, and both flat-object and array-of-entries shapes. | ✅ COMPLETE | I091 |
| T1.97.13 | Docs | Update §4.1/§4.2/§9/§10 in universal architecture doc | Add System Parameters to pattern application guidelines, implementation order, checklist, and success criteria. | ✅ COMPLETE | I091 |
| T1.97.14 | Docs | Update EKS knowledge.json | Reflect L15 status and universal architecture alignment for system_parameters. | ✅ COMPLETE | I091 |

### 16.4 I091 Success Criteria
- [x] `common/library/__init__.py` registers `config` as architecture-aligned sub-package with docstring, import, and `__all__`.
- [x] `common/universal_pipeline_architecture_design.md` has L15 row in §2.2 Inventory Table, `config/` in §2.3, L15 detail in §2.4.
- [x] `common/universal_pipeline_architecture_design.md` has §3.17 System Parameters Pattern.
- [x] `common/universal_pipeline_architecture_design.md` updated §4.1/§4.2/§9/§10.
- [x] EKS knowledge.json updated with v2.5.0 and revision entry.
- [x] I091 closed in issue log.
- [x] Full EKS suite 243/243 green.


---

## 17. Universal Path Resolution & Schema-Driven Initialization (I089 + I090) Tasks

> **Relocated from [§29 — Universal Path Resolution & Schema-Driven Initialization (I089 + I090)](phase_1_foundation_workplan.md#29-universal-path-resolution--schema-driven-initialization-i089--i090)** of the main workplan (v4.8). Canonical source is now here.

**Objective**: (1) Adopt EKS's `global_paths` as the universal canonical schema-driven path pattern and provide a shared `PathResolver` in `common/library/paths/` that normalizes both EKS and DCC path shapes — closes **I089**. (2) Bring EKS to DCC parity for `workflow_files`/`tool_files`/`folder_creation` (schema-driven initialization) — closes **I090**.

**Rationale**: A re-audit of DCC's actual code (I089 re-evaluation) found its path model is weaker than EKS's:
- `base_path` is derived by **script-location traversal** (`default_base_path()` walks `Path(__file__).parents` to find `"workflow"`), not from config.
- `data`/`output` dirs are **hardcoded literals** (`base_path / "data"`, `base_path / "output"`).
- `discovery_rules[].directory` are used **only for schema discovery**, not working dirs.
- `folder_creation.required_directories[].name` is used only for auto-create checks.

By contrast, EKS's `global_paths` (hardened by T1.80/T1.82/T1.83 — no hardcoded fallbacks) is **genuinely schema-driven SSOT**. Therefore the universal pattern adopts EKS `global_paths` as canonical, with a bidirectional `PathResolver` normalizing DCC's shape into it. For I090, EKS gains `workflow_files`/`tool_files` blocks (currently absent), while `folder_creation` is satisfied by the resolver deriving the create-list from the canonical `global_paths` — EKS deliberately does **not** add a separate DCC-style `folder_creation` block (documented design decision).

### 17.1 Canonical `global_paths` Shape (adopted as universal)

```json
"global_paths": {
  "data_dir": "data", "output_dir": "output", "archive_dir": "archive",
  "config_dir": "config", "log_dir": "log", "eks_root": "eks"
}
```

DCC's `discovery_rules` + `folder_creation` + native `base_path/"data"` defaults are **normalized into this shape** by the resolver (e.g. `schema_dir` ← first schema-config `discovery_rules` directory; `data_dir` ← `folder_creation` entry named `data` or native default).

### 17.2 Task Breakdown

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| T1.98.1 | Common | Add `common/library/paths/resolver.py` | `resolve_paths(project_root, config) -> ResolvedPaths` + `ResolvedPaths` dataclass (data_dir, output_dir, archive_dir, config_dir, log_dir, schema_dir, eks_root). Handles EKS `global_paths` directly; normalizes DCC `discovery_rules`/`folder_creation`/native `base_path/"data"` defaults into the canonical shape. | ✅ COMPLETE | I089 |
| T1.98.2 | Common | Export resolver from `common/library/paths/__init__.py` | Add `resolve_paths`, `ResolvedPaths` to package exports. | ✅ COMPLETE | I089 |
| T1.98.3 | Code | Wire EKS `ConfigRegistry` to resolver | Route `data_dir`/`output_dir`/all 6 path properties through `resolve_paths()`; uniform path access; `global_paths` stays canonical config shape. Update `phase1_server.py` to use resolver instead of inline `PRJ_DIR / _eks_root / gp.get(...)`. | ✅ COMPLETE | I089, T1.80, T1.82, T1.83 |
| T1.98.4 | Docs | Universal architecture doc elevation | Add **L16 — Path Resolution / Schema-Driven Paths** to §2.2 Inventory, §2.3 Package Structure, §2.4 detail in `common/universal_pipeline_architecture_design.md`; add **§4.18 Path Resolution Pattern** (canonical = EKS `global_paths`); update §5.1/§10/§24. | ✅ COMPLETE | I089 |
| T1.98.5 | Docs | Update `eks/knowledge.json` | Reflect L16 status and universal path-resolution alignment. | ✅ COMPLETE | I089 |
| T1.98.6 | Schema/Config | Add `workflow_files` + `tool_files` to EKS schema + config | Add `workflow_files_def`/`tool_files_def` to `eks_base_schema.json`; add properties to `eks_setup_schema.json`; add instance blocks to `eks_config.json` (parallel to DCC `project_config.json`). Decision: folder creation driven by canonical `global_paths` (resolver derives create-list) — no separate DCC-style `folder_creation` block. | ✅ COMPLETE | I090 |
| T1.98.7 | Code | EKS loader/initializer for `workflow_files`/`tool_files` | Add logic to `setup_validator.py`/`config_registry.py` to register the file manifest and auto-create declared dirs from `global_paths` via resolver (mirrors DCC consumption). | ✅ COMPLETE | I090, T1.98.1 |
| T1.98.8 | Testing | Tests + suite green | Add `eks/test/test_path_resolver.py` (EKS + DCC shape normalization) and `workflow_files`/`tool_files` schema tests; full EKS suite 243/243 green. Close I089, I090. | ✅ COMPLETE | I089, I090 |

### 17.3 Success Criteria
- [x] `common/library/paths/resolver.py` exists with `resolve_paths()` + `ResolvedPaths`; handles EKS `global_paths` and DCC shape.
- [x] `common/library/paths/__init__.py` exports `resolve_paths`, `ResolvedPaths`.
- [x] EKS `ConfigRegistry` + `phase1_server.py` route path access through the resolver; all 6 paths uniform.
- [x] `common/universal_pipeline_architecture_design.md` has L16 (§2.2/§2.3/§2.4) + §4.18 Path Resolution Pattern + §5.1/§10/§24 updates.
- [x] `eks/knowledge.json` updated with L16 status.
- [x] `eks_base_schema.json`/`eks_setup_schema.json`/`eks_config.json` have `workflow_files`/`tool_files` blocks; `global_paths` drives folder creation (no separate `folder_creation` block).
- [x] `setup_validator.py`/`config_registry.py` consume `workflow_files`/`tool_files` and auto-create dirs via resolver.
- [x] `eks/test/test_path_resolver.py` + `workflow_files`/`tool_files` schema tests added; full EKS suite 252/252 green (243 + 9 new).
- [x] I089 closed, I090 closed in issue log.


---

## 18. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I092 / R60) Tasks

> **Relocated from [§30 — Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I092 / R60)](phase_1_foundation_workplan.md#30-pipeline-entry-point--per-phase-sub-pipeline-convergence-i092--r60)** of the main workplan (v4.8). Canonical source is now here.

**Objective**: Resolve I092 by converging EKS pipeline entry points on a shared `run_pipeline(context)` funnel (mirroring DCC's CLI + UI + web → one `run_engine_pipeline(context)`) and satisfying R60 / AGENTS.md §18.13 — every phase (1–5) runs as an independent sub-pipeline with its own `phase{N}_server.py` backend. Phase 1 already has `phase1_server.py`; it needs the convergence cleanup. Phases 2–5 need the full backend + runner.

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


> **Phase 2–5 convergence tasks are tracked in their respective phase workplans** (AGENTS.md §15 — Phase 1 is COMPLETE, no cross-phase tasks defined here): `phase_2_chunking_embedding_workplan.md` §8 (T2.25–T2.26), `phase_3_knowledge_graph_workplan.md` §8 (T3.36–T3.37), `phase_4_retrieval_pipeline_workplan.md` §8 (T4.26–T4.27), `phase_5_ui_integration_workplan.md` §8 (T5.21–T5.22). I092/R60 status for Phases 2–5 is reflected in those workplans.

### Success Criteria

- [x] Shared `run_pipeline(context)` helper exists and is called by Phase 1 CLI + `phase1_server`.
- [x] EKS CLI (`eks-pipeline`) runs the full pipeline end-to-end.
- [x] `phase1_server._run` calls `run_full_pipeline()` (no inline A→C); 409 + `resolve_paths()` preserved.
- [x] `engine_endpoints.py` removed; `eks/serve.py` present (§18.12).
- [x] `ConfigRegistry` SSOT passed at entry.
- [ ] Phases 2–5 each have a standalone `phase{N}_server.py` + `run_phase{N}_pipeline(context)`; `serve.py` proxies `/api/v{N}/*` — tasks tracked in respective phase workplans (phase_2/3/4/5 §8).
- [x] Full EKS suite green (275/275).
- [x] `resolve_pipeline_base_path()` walks `__file__.parents` for `engine/` anchor; falls back to `Path.cwd()` (T1.99.13).
- [x] `--data-dir` is optional; defaults to `global_paths.data_dir` from config (T1.99.14).
- [x] All path defaults route through resolved base path + `global_paths` schema (T1.99.15).
- [x] Path resolution tests exist; full suite green (T1.99.16).
- [x] `detect_os()` invoked at EKS entry; `os_info` captured (T1.99.17).
- [x] `default_base_path("eks")` returns parent of anchor; no hardcoded depth (T1.99.18).
- [x] `resolve_pipeline_base_path()` = `--base-path` else `cwd` (T1.99.19).
- [x] `discover_project_root()` + `--base-path` CLI + `==pipeline_dir` strip; deterministic root (T1.99.20).
- [x] Default `data_dir` → `project_root/eks/data` via `resolve_paths()` (T1.99.21).
- [x] Auto-create OS-gated; paths serialized via `safe_posix()` (T1.99.22).
- [x] Anchor-missing raises `FileNotFoundError` (T1.99.23).
- [x] Entry-point resolution tests green (T1.99.24).
- [x] EKS consumes common L12/L17 (I078 advanced) (T1.99.25).

> **Phase test report**: `workplan/reports/phase_1_foundation_entrypoint_discovery_report.md` (RP-EKS-P1-ENTRY-001, v1.0) covers I098 / T1.99.17–26 — 8 new entry-point tests, full EKS suite 275/275 green. U154 / I098 → Resolved.

### Universal Bootstrap Manager (I108–I111 / L19) Tasks — ✅ COMPLETE

> **Option A (library-first)**: Universal `BootstrapManager` in `common/library/bootstrap/` as L19, extracted from DCC's mature implementation. EKS delegates to it. Subsequent tasks (I109–I111) depend on it. All 14 tasks below are complete.

| ID | Task | Details | Status | Issues |
| :--- | :---- | :----- | :----: | :---- |
| T1.99.50 | Create universal `BootstrapManager` in `common/library/bootstrap/` (L19) | Extracted from DCC's mature implementation. Foundation for all subsequent EKS wiring tasks (I109–I111). | ✅ | I108 |
| T1.99.51 | Phase registry with configurable ordering | Phase registry supports custom sort order for bootstrap phases. | ✅ | I108 |
| T1.99.52 | `to_pipeline_context()` returns valid `BasePipelineContext` (L06) | Returns context object conforming to L06 schema. | ✅ | I108 |
| T1.99.53 | `bootstrap_for_ui()` dual-mode | Skips CLI, accepts UI params directly. | ✅ | I108 |
| T1.99.54 | Universal `BootstrapError` wired to L10 `BaseErrorManager` | Structured error handling across all bootstrap phases. | ✅ | I108 |
| T1.99.55 | Universal bootstrap tests green | Phase tracking, trace, dual-mode, errors — all pass. | ✅ | I108 |
| T1.99.56 | Update universal architecture doc with L19 + §3.19 | Document universal BootstrapManager design. | ✅ | I108 |
| T1.99.57 | EKS `BootstrapManager` subclass with project-specific hooks | Subclasses universal L19 with EKS-specific phase hooks. | ✅ | I109 |
| T1.99.58 | `bootstrap_pipeline()` thin wrapper; backward-compat preserved | Delegates to universal `BootstrapManager`. | ✅ | I109 |
| T1.99.59 | `main()` uses `manager.bootstrap_all().to_pipeline_context()` chain | Clean chain pattern in entry point. | ✅ | I109 |
| T1.99.60 | Manual context assembly (~30 lines) collapsed; `main()` is thin shell | Context now derived from bootstrap pipeline, not manually assembled. | ✅ | I110 |
| T1.99.61 | `EngineInput` derived from context | Engine input constructed from pipeline context. | ✅ | I110 |
| T1.99.62 | `P1-BOOT-*` codes registered in `eks_error_config.json` | All bootstrap error codes registered. | ✅ | I111 |
| T1.99.63 | `RuntimeError` replaced with structured `BootstrapError`; error-path tests green | Structured errors with registered codes; full EKS suite green. | ✅ | I111 |

### Error Code Alignment, Pre-Bootstrap Logger, and Environment Check Tasks (I112–I114)

> Cross-reference audit of 5 sources found 6 misalignments between bootstrap error codes and Appendix D (I112, 🔷 PLANNED). Pre-bootstrap logger sequencing gap vs DCC fixed (I113, ✅). Environment/dependency check added via L20 + lazy imports (I114, ✅).

| ID | Task | Details | Status | Issues |
| :--- | :---- | :----- | :----: | :---- |
| T1.99.64 | Update Appendix D: add Bootstrap category (`S-B-S-0600–0699`) | D3 updated; `P1-BOOT-*` format documented in D2. | 🔷 | I112 |
| T1.99.65 | Register 14 universal `B-*` codes in `eks_error_config.json` | Under new `bootstrap_universal` range; `eks_error_code_base.json` pattern updated. | 🔷 | I112 |
| T1.99.66 | Add bootstrap milestone/status messages to `eks_message_config.json` | `eks_message_base.json` + Appendix D D6 updated. | 🔷 | I112 |
| T1.99.67 | Decide and implement `P1-BOOT-*` format (A: migrate to `S-B-S-06xx` or B: keep hybrid) | Format decision made and implemented across all sources. | 🔷 | I112 |
| T1.99.68 | Ensure all EKS code paths use registered error codes | No unregistered `B-*` codes can fire in EKS context. | 🔷 | I112 |
| T1.99.69 | Tests + docs + close I112 | Verify all bootstrap codes resolve via `ErrorManager`; messages via `MessageManager`; Appendix D fully updated. | 🔷 | I112 |
| T1.99.70 | Early CLI parse for `--level`/`--debug` before bootstrap | `_parse_early_verbosity()` at L470–504. | ✅ | I113 |
| T1.99.71 | `UniversalLogger` created pre-bootstrap, passed to `EKSBootstrapManager(logger=logger)` | L548, L573. | ✅ | I113 |
| T1.99.72 | `TelemetryHeartbeat` created pre-bootstrap, covers all 8 phases | L552–553. | ✅ | I113 |
| T1.99.73 | Verify all EKS bootstrap hooks use `self.logger` | `_eks_error_factory`/`_eks_message_factory` pass through; `BootstrapManager._log()` wired. | ✅ | I113 |
| T1.99.74 | CLI + pipeline test suite passes; close I113 | Covered by existing test suite. | ✅ | I113 |
| T1.99.75 | **L20**: Create universal `test_environment()` in `common/library/core/system/` | Stdlib-only (`importlib`, `platform`, `pathlib`); `import_module()` loop; returns `{ready, errors, required_modules, ...}`. | ✅ | I114 |
| T1.99.76 | **L19**: Add `env_tester` strategy hook to universal `BootstrapManager` | P6 calls it after OS detection; backward-compat (not injected → OS-detection-only). | ✅ | I114 |
| T1.99.77 | **EKS**: Wire `_bootstrap_env()` to universal `test_environment()` via `env_tester` hook | `ready=False` → `BootstrapError("P1-BOOT-ENV", ...)` with "Run: conda activate eks" guidance. | ✅ | I114 |
| T1.99.78 | **EKS**: Register `P1-BOOT-ENV` in `eks_error_config.json`; update schemas | Error code + schema updates. | ✅ | I114 |
| T1.99.79 | Update `update_log.md` + `issue_log.md`; close I114 | I114 → Resolved. | ✅ | I114 |
| T1.99.80 v2 | **Lazy-import refactor**: ALL `common.library` imports deferred from module level to inside functions | Module-level now stdlib-only; no bare `ModuleNotFoundError` reaches user. | ✅ | I114 |

### Preload Infrastructure Guard (I117) Tasks — ✅ COMPLETE

> **Revision note (v3.86):** Chicken-and-egg problem — `main()` imports 4 `common.library` modules before bootstrap runs, but environment check lives inside bootstrap Phase 6. If `common.library` is not importable, a bare `ImportError` hits the user. These imports cannot be deferred (bootstrap itself needs them). **Solution**: `_preload_infrastructure()` — pure-stdlib guard function with individual `try/except ImportError`-guards on all 4 import groups (paths, root_discovery, logging, pipeline). Cannot live in `common.library` (circular); is a universal preload pattern (§3.23). `main()` simplified from ~20 lines of scattered imports to single `infra = _preload_infrastructure(...)` call with `infra["ready"]` gate. DCC does not have this issue (no external `common.library` dependency).

| ID | Task | Details | Status | Issues |
| :--- | :---- | :----- | :----: | :---- |
| T1.99.81 | Create `_preload_infrastructure()` pure-stdlib guard in `eks_engine_pipeline.py` | Individually try/except-guards all 4 `common.library` import groups (paths, root_discovery, logging, pipeline); collects errors into single dict `{ready, errors, logger, heartbeat, project_root, ...}`; `main()` gates on `infra["ready"]`, prints all errors with `FATAL:` prefix on failure; happy path preserved — if all imports succeed, `main()` proceeds identically. | ✅ | I117 |
| T1.99.82 | Update `eks/log/issue_log.md` | Log I117 with root-cause analysis (chicken-and-egg problem). | ✅ | I117 |
| T1.99.83 | Update workplan | Add T1.99.81–83 tasks, §30.3 section; document universal preload pattern. | ✅ | I117 |

### I130/I131/I132 Pipeline Defect Fixes Tasks — ✅ COMPLETE

> **Resolution note (U181):** I130 (bootstrap path-resolution rooting defect), I131 (KeyError 'revision' in register_placeholders), and I132 (.dwg file type orphan) were discovered during Phase 1 pipeline execution. All three were resolved in a single fix cycle (U181). These tasks were missing from the original P1.4 task registry; added here for completeness.

| ID | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
| :-- | :---- | :----- | :----: | :---- | :---- | :---- | :---: | :--- |
| T1.99.101 | **I130**: Fix bootstrap path-resolution rooting defect | One-line logic change in `bootstrap.py`: add `and self.config` guard — `if self._path_resolver is not None and self.config:` — skips resolver when config empty, uses else-branch correctly anchored under `pipeline_root_dir="eks"`. Prevents `engine/`, `archive/`, `test_output/` from being created at repo root. | ✅ COMPLETE | I130 | U181 | `bootstrap.py` | P0 | — |
| T1.99.102 | **I130**: Clean stale root-level directories | Remove incorrectly-created `engine/`, `archive/`, `test_output/` directories at repo root (artifacts of the path-resolution defect). | ✅ COMPLETE | I130 | U181 | — | P1 | T1.99.101 |
| T1.99.103 | **I130**: Verify zero new root-level directories after fix | Confirm no new root-level dirs are created after the guard fix. Pipeline output restricted to `eks/` sub-tree. | ✅ COMPLETE | I130 | U181 | — | P1 | T1.99.101–102 |
| T1.99.104 | **I131**: Fix `_parse_filename()` fallback to include `revision="00"` | L1 defense: `_parse_filename()` had 3 code paths; filename `131101-WSW41-SP-SG-0101.pdf` matched no revision pattern → fallback returned `{"document_number": stem}` only (no `revision` key). Fix: fallback now returns `revision="00"`. | ✅ COMPLETE | I131 | U181 | `file_scanner.py` | P0 | — |
| T1.99.105 | **I131**: Add `setdefault("revision", "00")` safety net in `build_placeholder_metadata()` | L2 defense: `build_placeholder_metadata()` now has `setdefault("revision", "00")` safety net — catches any upstream source that omits `revision`. | ✅ COMPLETE | I131 | U181 | `pipeline_orchestrator.py` | P1 | T1.99.104 |
| T1.99.106 | **I131**: Use `.get("revision", "00")` in `register_document()` | L3 defense: `register_document()` now uses `.get("revision", "00")` instead of direct dict access `metadata["revision"]`. Three-layer layered defense complete. | ✅ COMPLETE | I131 | U181 | `registry.py` | P1 | T1.99.105 |
| T1.99.107 | **I131**: Tests + logs update for revision KeyError fix | Verify Phase A→B→C pipeline runs (19 files, 7 flagged). All 3 layers applied. Update `update_log.md`. | ✅ COMPLETE | I131 | U181 | `test_t132_modules.py`, `update_log.md` | P2 | T1.99.104–106 |
| T1.99.108 | **I132**: Add CAD document type for `.dwg` files | `.dwg` was registered in `file_type_registry` but no document type listed `.dwg` in `expected_file_types` → files classified as `unknown`. Fix: added `"CAD"` document type to `eks_doc_base_schema.json` enum, `eks_doc_setup_schema.json` propertyNames pattern, and `eks_doc_config.json` document_type_registry + element_expectations. | ✅ COMPLETE | I132 | U181 | `eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json` | P1 | — |


---

## 19. Data Export — CSV/Excel Pipeline Output (I126 / L22) — 🔷 PLANNED Tasks


> Source: [§32](phase_1_foundation_workplan.md#32)


### Task Breakdown

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.153 | EKS registry | Add `db_path` param to `DocumentRegistry.__init__` | Optional `db_path` parameter bypasses config for explicit path control. Enables test-isolated databases. Bumped registry.py to v0.6. | ✅ COMPLETE |
| T1.99.154 | EKS export | Scope export to current-run docs (F2) | In `main()`: capture pre-run `document_number` set via `reg_pre.list_documents()`, filter post-run `all_docs` to only new docs. | ✅ COMPLETE |
| T1.99.155 | EKS export | Per-run output subdirectories (F3) | Write exports to `output/<run_id>/` (UUID subdirectory). `run_id` already generated in `main()` via `engine_in.run_id`. | ✅ COMPLETE |
| T1.99.156 | EKS test | Isolate export test DB + output (F4) | `test_main_export_both_runs` uses `mock.patch.object(registry_module, "DocumentRegistry", _IsolatedRegistry)` with temp DB path. | ✅ COMPLETE |


### Task Breakdown

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.153 | EKS registry | Add `db_path` param to `DocumentRegistry.__init__` | Optional `db_path` parameter bypasses config for explicit path control. Enables test-isolated databases. Bumped registry.py to v0.6. | ✅ COMPLETE |
| T1.99.154 | EKS export | Scope export to current-run docs (F2) | In `main()`: capture pre-run `document_number` set via `reg_pre.list_documents()`, filter post-run `all_docs` to only new docs. | ✅ COMPLETE |
| T1.99.155 | EKS export | Per-run output subdirectories (F3) | Write exports to `output/<run_id>/` (UUID subdirectory). `run_id` already generated in `main()` via `engine_in.run_id`. | ✅ COMPLETE |
| T1.99.156 | EKS test | Isolate export test DB + output (F4) | `test_main_export_both_runs` uses `mock.patch.object(registry_module, "DocumentRegistry", _IsolatedRegistry)` with temp DB path. | ✅ COMPLETE |


### Task Breakdown — L22 Universal DataExporter

> Source: §32.4 (originally mislabeled as §32.8.4 in original workplan)

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.87 | L22 | Create `common/library/export/` — universal `DataExporter` | Package: `__init__.py` re-exports `DataExporter`, `export_to_csv`, `export_to_excel`, `export_multi_sheet`. Core: `exporter.py` with `DataExporter` class — constructor accepts optional `overwrite=True` param. Follows `common/library/` facade pattern; add to `common/library/__init__.py` `__all__`. Error codes in `S-DE-*` range (S=System, DE=DataExport). | 🔷 PLANNED |
| T1.99.88 | L22 | Implement `export_to_csv()` | Uses `csv.DictWriter` (stdlib). Accepts `rows: list[dict]`, `path: Path`, optional `columns: list[str]` for column ordering. Writes BOM (`\ufeff`) for Excel UTF-8 compatibility. Returns `path`. No extra deps. | 🔷 PLANNED |
| T1.99.89 | L22 | Implement `export_to_excel()` + `export_multi_sheet()` | Uses `openpyxl.Workbook` (already in eks.yml/dcc.yml). Single-sheet: `export_to_excel(rows, path, sheet_name="Sheet1")`. Multi-sheet: `export_multi_sheet(sheets: dict[str, list[dict]], path)` — each key = sheet name. Auto-column-width, header row bold + frozen. Returns `path`. Reuses DCC's output pattern (`index=False`) but accepts `list[dict]` (no pandas dependency). | 🔷 PLANNED |
| T1.99.90 | L22 | Add universal tests | `common/library/export/tests/test_exporter.py`: csv round-trip (write→read→compare), excel round-trip (write→openpyxl read→compare), multi-sheet Excel, empty rows → empty file with headers only, Unicode/CJK characters, error paths (invalid path, read-only dir, empty rows list). | 🔷 PLANNED |
| T1.99.91 | L22 | Update universal architecture doc | Register L22 in `common/universal_pipeline_architecture_design.md` §2.2 Inventory Table; add §3.23 design pattern section (DataExporter); update §2.3 package structure diagram; bump module count 21→22; add to §4.1 and §4.2; add checklist item in §9 Appendix A. | 🔷 PLANNED |
| T1.99.92 | EKS CLI | Add `--export` flag to pipeline entry | Add `--export {csv,xlsx,both,none}` (default: `none`) to L18 schema-driven CLI parser in `parse_eks_cli()`. In `main()`, after `run_pipeline(context=ctx)`, if `--export` is set, query DB results and call `DataExporter` methods. Output to `resolve_paths() → output_dir`. | 🔷 PLANNED |
| T1.99.93 | EKS main() | Wire 3 export calls after pipeline returns | **Design decision (2026-07-18): Export stays in `main()`, not in `PipelineOrchestrator`** — export is output formatting, not pipeline processing. The orchestrator remains pure (no `export_config` parameter). In `eks_engine_pipeline.py` `main()`, after `run_pipeline()` returns: **(a)** Query `returned_ctx.registry.list_documents(extract_status='pending')` → `DataExporter().export_to_csv/excel(rows, output_dir / "discovery_inventory.{fmt}")`. **(b)** Query all documents + aggregate element counts from `returned_ctx.data` → `extraction_results.{fmt}`. **(c)** Query flagged documents (`extract_status!='success'` or `confidence<0.70`) → `review_flags.{fmt}`. All read-only DB queries via `returned_ctx.registry`. Output paths via `resolve_paths()` → `output_dir`. **Confirmed no changes to**: `_preload_infrastructure()` (L22 is not bootstrap infrastructure), `bootstrap.py` (openpyxl already in P6 `test_environment()` check), `run_pipeline()`, `PipelineOrchestrator`. | 🔷 PLANNED |
| T1.99.94 | EKS API + docs | Add export endpoint + update logs | Add `GET /api/v1/export/{phase}/{format}` to `phase1_server.py` — phases: `a`, `b`, `c`, `all`; formats: `csv`, `xlsx`. Returns `FileResponse` with correct Content-Type. Update `eks/log/update_log.md` (U183), `eks/log/issue_log.md` (I126→Resolved), `eks/log/test_log.md` (TL005). | 🔷 PLANNED |


### Task Breakdown — Post-Implementation Gap Fix (I188)

> Source: §32.7.4 (originally mislabeled as §32.8.4 in original workplan)

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.147 | EKS export | Fix `discovery_inventory` empty — remove `["pending"]` filter | Change L987 `_build_export_rows(all_docs, ["pending"], discovery_cols)` → `_build_export_rows(all_docs, None, discovery_cols)`. Discovery inventory reflects ALL documents registered in Phase A. | ✅ COMPLETE |
| T1.99.148 | EKS export | Fix `review_flags` empty — flag missing confidence unconditionally | Change L1126-1127 `elif status != "success"` → unconditional `else:` so `confidence=None` always generates `"Confidence: missing"` flag. Unblocks review_flags output. | ✅ COMPLETE |
| T1.99.149 | EKS export | Verify — run pipeline with `--export both` and assert 3 files | Manual verification: run `main(["--data-dir", "...", "--export", "both"])`, check `eks/output/` for `discovery_inventory.csv`, `extraction_results.csv`, `review_flags.csv` (and xlsx equivalents). | ✅ COMPLETE |
| T1.99.150 | EKS test | Add export-specific unit tests | In `test_eks_engine_pipeline.py`: test `_build_export_rows` (with/without status filter, column subset), test `_build_flagged_rows` (None-confidence + success, low confidence, non-success), test `main()` with `--export both` (assert output files exist). | ✅ COMPLETE |
| T1.99.151 | EKS docs | Update issue log + workplan | Set I188 → Resolved in `issue_log.md`; mark T1.99.147–150 as ✅ COMPLETE; update `update_log.md` U19x. | ✅ COMPLETE |


---

## 20. Schema-Driven Export Columns — Replace Hardcoded 11-Field Subset (I193) — ✅ COMPLETE Tasks


> Source: [§47](phase_1_foundation_workplan.md#47)


### Task Breakdown

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.157 | Schema | Add `x_export` boolean to every property in `document_metadata_def` | 48 properties in `document_metadata_def` (45 `true`, 3 `false`: `is_latest`, `supersedes`, `superseded_by`) + 5 properties in `project_metadata_def` (all `true`). Schema version bumped to 1.8.0. | ✅ COMPLETE |
| T1.99.158 | Schema | Add `export_artifact_def` definition | Enumerate `discovery_inventory`, `extraction_results`, `review_flags` artifact column sets with descriptions. Shape-only definition; actual columns derived from `x_export` at runtime. | ✅ COMPLETE |
| T1.99.159 | Pipeline | Create `resolve_export_columns()` helper | Read `x_export` flags from schema JSON, derive per-artifact column lists in schema-definition order (project fields → doc fields). Falls back to hardcoded 11-column defaults with `_fallback: True` flag on load failure. | ✅ COMPLETE |
| T1.99.160 | Pipeline | Replace hardcoded `_build_export_rows()` and column lists | `_build_export_rows()` → pass-through full doc dict (removed 11-field manual construction). `_build_flagged_rows()` → pass-through + `flag_reason`. `main()` → uses `resolve_export_columns()` with graceful fallback. | ✅ COMPLETE |
| T1.99.161 | Test | Add schema-validation tests for `x_export` and artifacts | (a) `test_x_export_flag_present_on_all_properties` — every doc/proj property has boolean `x_export`, internal fields verified `false`. (b) `test_export_artifact_def_exists_and_valid` — 3 artifacts defined, structure valid. (c) `test_export_artifacts_have_different_column_sets` — discovery ⊂ extraction, extraction-only = {page_count, extract_status, ...}, review has flag_reason. | ✅ COMPLETE |
| T1.99.162 | Pipeline | Verify full export with 50 columns | Pipeline run verified: `discovery_inventory`: 46 cols (was 6), `extraction_results`: 50 cols (was 10), `review_flags`: 12 cols (was 8). All 10 previously-missing fields present (project_title, embedded_title, file_size, file_hash, lifecycle_stage, created_by, vendor_name, originator_company, file_modified_at, security_class). | ✅ COMPLETE |


---

## 21. Appendix D vs. Actual Pipeline Cross-Source Audit — 🔷 PLANNED Tasks


> Source: [§48](phase_1_foundation_workplan.md#48)


### Priority 1 — Critical Bug Fixes (D1, D2)

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.163 | D1 | Health | Fix `HealthScorer.score()` caller — structural elements misrouted | `pipeline_orchestrator.py:640`: change `score(doc, elements)` → `score(doc, structural_elements=elements)`. `review_manager.py:129`: same fix. `test_t132_modules.py:101,112,131,133`: update test calls. | `pipeline_orchestrator.py`, `review_manager.py`, `test_t132_modules.py` | ✅ COMPLETE |
| T1.99.164 | D2 | Message | Add 9 missing message IDs to `eks_message_config.json` + align pipeline names | Add: `STATUS_PHASE_A_START`, `STATUS_PHASE_A_COMPLETE`, `STATUS_PHASE_B_START`, `STATUS_PHASE_B_COMPLETE`, `STATUS_PHASE_C_START`, `STATUS_PHASE_C_COMPLETE`, `STATUS_PIPELINE_START`, `STATUS_PIPELINE_COMPLETE`, `ERROR_FILE_PROCESSING`. Align all code call sites. Keep existing `MILESTONE_*` as aliases or migrate. | `eks_message_config.json`, `pipeline_orchestrator.py`, `eks_engine_pipeline.py` | ✅ COMPLETE |


### Priority 2 — Error Code Registration (D3)

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.165 | D3 | Error | Register 6 ad-hoc error codes in `eks_error_config.json` with correct severity | Map S-PIP-001/002/003 → system_errors S-R-S range (severity: ERROR, not FATAL). Map D5-REG-001 → data_logic_errors P1-D-P range. Map D5-DETECT-001, D5-SCORE-001 → data_logic_errors P3-E-E range. Update code references if code values change. | `eks_error_config.json`, `pipeline_orchestrator.py` | ✅ COMPLETE |


### Priority 3 — Health Score Accuracy (D5, D6, D7)

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.166 | D5 | Health | Add 15 new columns to `ALL_SCOABLE` tier sets | Tier assignments: T2 — `document_title`, `lifecycle_stage`, `revision_date`, `project_phase`, `contract_package`, `issued_date`, `responsible_engineer`, `total_sheets`, `supersedes`, `superseded_by`. T3 — `revision_description`, `embedded_revision_number`, `references_documents`, `language`, `vendor_name`. | `health_scorer.py` | ✅ COMPLETE |
| T1.99.167 | D6 | Health | Add `"F": 0.0` to `COVER_TYPE_SOURCE_SCORES` | Single-line addition. Type F = parse failed entirely → source quality score = 0.0. | `health_scorer.py` | ✅ COMPLETE |
| T1.99.168 | D7 | Pipeline | Wire `get_health_impact()` into `_process_file()` | After `self.scorer.score()`, call `penalty = self.error_manager.get_health_impact(doc_id)`, compute `adjusted = max(0.0, score + penalty / 100.0)`, store adjusted score in DB. | `pipeline_orchestrator.py` | ✅ COMPLETE |


### Priority 4 — Expected Elements Alignment (D8)

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.169 | D8 | Health/Schema | Sync `EXPECTED_ELEMENTS_BY_TYPE` with Appendix D | Add `table` to Type A/B expectations (change from 4→5 expected elements) OR evaluate that code's 4-element model is correct and document the deviation. Decision deferred to review. | `health_scorer.py` or `appendix_d_pipeline_messages_errors.md` | ✅ COMPLETE |


### Priority 5 — Documentation Sync (D4, D9–D13)

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.170 | D4 | Docs | Update Appendix D D3/D5 error taxonomy to reflect actual P1-D-P/P5-F/P3 codes | Remove aspirational P1-R-R/P1-V-V/P1-C-C taxonomy; document actual module codes `P1-D-P`, `P3-G-G`, `P5-F-V/S/PROP`. Add cross-reference to actual `eks_error_config.json` entries. | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |
| T1.99.171 | D9 | Docs | Update Appendix D D7.1 column catalog to 54+ columns | Replace 25-column table with current schema-derived 54-column catalog. Split T1/T2/T3 tiers to match `ALL_SCOABLE` after GAP-D5 fix (39 scorable). | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |
| T1.99.172 | D10 | Docs | Update Appendix D D8 status lifecycle to code's `extract_status` model | Replace `NEW→EXTRACTED→REGISTERED→VERIFIED` with `pending→success/partial/failed`. Document that document state is column-based, not a lifecycle FSM. | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |
| T1.99.173 | D11 | Docs | Update Appendix D D4 system error catalog names to match config | Swap mismatched names at S-E-S-0101–0105. Config values are SSOT. Add `ENVIRONMENT_NOT_READY` (S-E-S-0104), `DUCKDB_UNAVAILABLE` (S-E-S-0105). | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |
| T1.99.174 | D12 | Docs | Update Appendix D D4.3 range allocation — 05xx = AI, not Database | Document that range 05xx is now S-A (AI/Optional services). Note gap: Database errors (DuckDB/Neo4j) have no dedicated range; evaluate whether S-D 06xx should be allocated. | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |
| T1.99.175 | D13 | Docs | Update Appendix D D4 file I/O + config code ranges to actual config | Document actual ranges: file I/O 0201–0206 (not 0201–0212), config 0301–0308 (not 0301–0311). Note 10 missing aspirational codes may be added in future phase if needed. | `appendix_d_pipeline_messages_errors.md` | 🔷 PLANNED |


---

## 22. Appendix E+F vs. Pipeline Architecture Cross-Source Audit — Gap Remediation (I208–I225) Tasks


> Source: [§49](phase_1_foundation_workplan.md#49)


### Wave 1 — Critical Wiring Gaps (I212, I216, I224) — Must-Fix Before Phase 2

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.179 | I212 (G5) | Revision | Wire `RevisionManager` into Phase B for supersession detection | Implement `detect_supersession()` in `revision.py` — query existing documents by `document_number`, compare revisions, set `is_latest=False` on superseded docs, set `supersedes`/`superseded_by` chain. Integrate into `PipelineOrchestrator._process_file()` after `register_document()`. Add `revision_manager` field to orchestrator. Requires: `revision.py` method bodies (currently stubs), `registry.py` `set_not_latest()` + `set_superseded_by()`, orchestrator wiring, 2 test classes. | `revision.py`, `pipeline_orchestrator.py`, `registry.py`, `test_t132_modules.py` | 🔷 PLANNED |
| T1.99.180 | I216 (G9) | Pipeline | Restore checkpoint persistence with resume capability | Uncomment `save_checkpoint()` calls in `PipelineOrchestrator._after()` + `run_full_pipeline()`. Write checkpoints to `output/<run_id>/checkpoint_<phase>.json` with: `{phase, completed_doc_ids, context_state, timestamp}`. On resume: `initialize_context(checkpoint_state=...)` skips completed phases, continues from next. Add `--resume <run_id>` CLI flag to `eks_engine_pipeline.py`. Requires: orchestrator checkpoint write/read methods, CLI flag, 4 tests. | `pipeline_orchestrator.py`, `eks_engine_pipeline.py`, `test_eks_engine_pipeline.py` | 🔷 PLANNED |
| T1.99.181 | I224 (G17) | Review | Wire `ReviewManager` into Phase C for review status persistence | After Phase C query + export, iterate flagged docs: (1) apply auto-corrections via `correct_field()`, (2) expose remaining flags, (3) `approve_document()` persists `review_status`, `reviewed_by`, `reviewed_at` to registry. Add `POST /api/v1/review/approve` endpoint. Requires: `review_manager.py` method implementation, `registry.py` `update_review_status()`, orchestrator `run_phase_c()` wiring, `phase1_server.py` endpoint, 3 tests. | `review_manager.py`, `pipeline_orchestrator.py`, `registry.py`, `phase1_server.py`, `test_t132_modules.py` | 🔷 PLANNED |


### Wave 2 — Architecture Compliance (I209, I211, I215, I221) — Should-Fix

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.182 | I209 (G2) | Architecture | Refactor `FileScanner`, `HealthScorer`, `StructureDetector` to inherit from `BaseEngine` | Each engine gets `validate_input()` → `execute()` → `validate_output()` structure. Use `EngineInput`/`EngineOutput` dataclasses from `core/base.py` (post-I210 consolidation). `ParserRouter` already partially follows pattern — complete it. `PipelineOrchestrator` stays as coordinator (doesn't inherit). Requires: 4 engine refactors, test updates for new interfaces. | `file_scanner.py`, `health_scorer.py`, `structure_detector.py`, `parser_router.py`, `base.py`, `test_t132_modules.py` | 🔷 PLANNED |
| T1.99.183 | I211 (G4) | DI | Replace direct instantiation in `PipelineOrchestrator` with factory calls | Change `self.scanner = FileScanner(...)` → `self.scanner = EngineFactory.create("FileScanner", ...)`, same for `HealthScorer`, `StructureDetector`. `ParserRouter` already uses `ParserFactory` — verify consistency. Requires: `factories.py` class additions, orchestrator `__init__` changes, test DI injection verification. | `pipeline_orchestrator.py`, `factories.py`, `test_t132_modules.py` | 🔷 PLANNED |
| T1.99.184 | I215 (G8) | Telemetry | Unify dual telemetry into single heartbeat stream | `PipelineOrchestrator` accepts `telemetry: Optional[TelemetryHeartbeat]` parameter — when provided from `main()`, uses it instead of creating local instance. `run_full_pipeline()` forwards orchestrator checkpoints to main heartbeat. `DocumentProcessingHeartbeat` stays as subclass. Requires: orchestrator `__init__` parameter, `main()` wiring, 2 tests. | `pipeline_orchestrator.py`, `eks_engine_pipeline.py`, `telemetry.py`, `test_t132_modules.py` | 🔷 PLANNED |
| T1.99.185 | I221 (G14) | Safety | Guard `psutil` import in `telemetry.py` | Wrap `import psutil` in try/except ImportError; memory/CPU sampling becomes no-op when absent (log WARNING once). Add `psutil` to `eks.yml` as optional dependency with `# telemetry` comment. Prevents bare `ModuleNotFoundError` on restricted systems. | `telemetry.py`, `eks.yml` | 🔷 PLANNED |


### Wave 3 — IO Contracts & Data Flow (I210, I214, I218, I219) — Should-Fix

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.186 | I210 (G3) | Contracts | Consolidate dual `EngineInput`/`EngineOutput` — EKS versions subclass `common.library` versions | Option B: Keep EKS `core/base.py EngineInput`/`EngineOutput` as subclasses of `common.library.core.pipeline.EngineInput`/`EngineOutput`. EKS versions add domain-specific fields (`discovery_config`, `health_config`, `structural_config`). Delete EKS standalone definitions; re-export from `core/base.py`. Requires: `base.py` refactor, `eks_engine_pipeline.py` import path update, verify DCC isolation. | `base.py`, `eks_engine_pipeline.py`, `test_eks_engine_pipeline.py` | 🔷 PLANNED |
| T1.99.187 | I214 (G7) | Contracts | Wire `HealthInput`/`HealthOutput` + `DiscoveryInput`/`DiscoveryOutput` into pipeline calls | Phase A: construct `DiscoveryInput` from file list → `scanner.scan(discovery_input)` → unpack `DiscoveryOutput`. Phase B: construct `HealthInput(doc, extraction_results, structural_elements)` → `scorer.score(health_input)` → unpack `HealthOutput` for DB write. Requires: `pipeline_orchestrator.py` Phase A + `_process_file()` changes, `io_contracts.py` field alignment, 3 tests. | `pipeline_orchestrator.py`, `io_contracts.py`, `test_t132_modules.py` | 🔷 PLANNED |
| T1.99.188 | I218 (G11) | Data | Pass context-resolved paths into `ParserInput` defaults | Replace `ParserInput(config_file="", schema_dir="", output_dir="")` with `self.context.paths` values. Same for `DiscoveryInput` in Phase A. Requires: orchestrator `_process_file()` + `run_phase_a()` changes. | `pipeline_orchestrator.py` | 🔷 PLANNED |
| T1.99.189 | I219 (G12) | Data | Write parsed content to `context.data.extracted_content` during execution | After successful parse in `_process_file()`, store: `self.context.data.extracted_content[doc_id] = extraction_result`. Enables downstream engines to read extraction without re-querying registry. Also populates checkpoint data for resume. Requires: orchestrator `_process_file()` change. | `pipeline_orchestrator.py` | 🔷 PLANNED |


### Wave 4 — Folder Structure & Schema Wiring (I208, I220, I225) — Should-Fix

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.190 | I208+I220 (G1+G13) | Structure | Migrate to Appendix F domain subdirectory layout | Create 6 subdirectories: `engine/discovery/` (FileScanner), `engine/router/` (ParserRouter), `engine/registry/` (DocumentRegistry), `engine/revision/` (RevisionManager), `engine/health/` (HealthScorer), `engine/structure/` (StructureDetector). Keep `engine/core/` for shared: `base.py`, `context.py`, `factories.py`, `bootstrap.py`, `config_registry.py`, `schema_loader.py`, `io_contracts.py`, `telemetry.py`, `validator.py`, `__init__.py`. Move `parser_router.py` from `engine/parsers/` to `engine/router/`. Relocate test modules accordingly. **Project-wide grep for all import paths** — update every file referencing old locations. Run full test suite after migration. **This is the largest single task** — 7 modules moved, ~30 files updated. | `engine/discovery/__init__.py`, `engine/router/__init__.py`, `engine/registry/__init__.py`, `engine/revision/__init__.py`, `engine/health/__init__.py`, `engine/structure/__init__.py`, `pipeline_orchestrator.py`, `eks_engine_pipeline.py`, `phase1_server.py`, `test_*.py`, `__init__.py` files | 🔷 PLANNED |
| T1.99.191 | I225 (G18) | Bootstrap | Wire `SchemaToDDL` into bootstrap P4 for auto-DDL generation | In `EKSBootstrapManager._bootstrap_registry()`: call `SchemaToDDL.generate_ddl()` from `eks_doc_base_schema.json` → compare with existing table schema → apply `generate_migration_ddl()` if needed. On fresh DB: generate full CREATE TABLE DDL. Requires: `bootstrap.py` integration, `registry.py` `init_db(ddl=...)` parameter, schema version tracking in DB metadata table. | `bootstrap.py`, `schema_to_ddl.py`, `registry.py`, `test_t132_modules.py` | 🔷 PLANNED |


### Wave 5 — Documentation & UI Contracts (I217, I222) — Nice-to-Have

| ID | Gap | Scope | Task | Details | Status | Issues | Updated on | Files | Priority | Depends On |
|:---|:---|:---|:---|:---|:---:|:---|:---|:---|:---:|:---|
| T1.99.192 | I217 (G10) | UI | Implement `DocumentSelectionContract` + `PipelineConfigContract` per Appendix F | Add contract schemas to `contracts.py`, wire `ContractManager` to validate before pipeline execution. Add endpoints: `POST /api/v1/contracts/document-selection` (filter/sort/select docs), `POST /api/v1/contracts/pipeline-config` (per-run parameter override). Requires: `contracts.py` additions, `contract_manager.py` wiring, `phase1_server.py` endpoints, 3 tests. | `contracts.py`, `contract_manager.py`, `phase1_server.py` | 🔷 PLANNED |
| T1.99.193 | I222 (G15) | Docs | Cross-audit Appendix E schema versions vs. actual `version` fields | Read `"version"` from all 23 schema files, compare against Appendix E E5.1 table. Update stale entries. Add validation script `eks/test/verify_appendix_e_versions.py` to make this a repeatable gate. | `appendix_e_schema_design.md`, `test/verify_appendix_e_versions.py` | 🔷 PLANNED |


---

## 23. `str(5)` Bug Fix — Restore Exception Messages Across All Error Paths (I226) Tasks


> Source: [§50](phase_1_foundation_workplan.md#50)


### Task Breakdown

| # | Scope | Task | Details | Status |
| :--- | :--- | :--- | :--- | :---: |
| T1.99.194 | EKS workflow | Fix `pipeline_orchestrator.py` — 5 instances | Replace all `str(5)` with `str(e)` in 3 except blocks. Verified each `e` in scope. | ✅ COMPLETE |
| T1.99.195 | EKS workflow | Fix `discovery_cli.py` — 1 instance | Replace `str(5)` with `str(e)` in DiscoveryEngineError ErrorRecord. | ✅ COMPLETE |
| T1.99.196 | EKS UI | Fix `phase1_server.py` — 3 instances | L89 `_IMPORT_ERROR`, L525 `"detail"`, L666 `_job_state["error"]`. | ✅ COMPLETE |
| T1.99.197 | EKS UI | Fix `serve.py` — 4 instances | L404 ConnectionRefused check, L425 upstream err, L436 internal err, L481 Ollama err. | ✅ COMPLETE |


---

## Cross-Reference Index


| Appendix § | Main Workplan Source | Content |
|:---:|:---|:---|
| 1 | §8 | Task Status Summary (counts only; detail rows in §2–§23) |
| 2 | §14 | Foundation, Environment & Compliance (R99) |
| 3 | §15 | Architectural Patterns — Context, Factories & Orchestration Hardening (Appendix F) |
| 4 | §16 | Core Schema Suite (base/setup/config + fragment schemas) |
| 5 | §17 | Asset Schema — Universal Plant Item (R36/R39) |
| 6 | §18 | Ontology Integration (R44, ISO 15926) |
| 7 | §19 | Logging, Errors & Health Scoring (R33/R34/R51) |
| 8 | §20 | Document Registry & Revision Management (R02/R21/R22/R29) |
| 9 | §21 | Document Parsers — PDF/DOCX/XLSX (R01/R26) |
| 10 | §22 | Document Schema v2 — 3-Layer Reorganization (R52/R53) |
| 11 | §23 | Pipeline Orchestration (R54–R58/R57) |
| 12 | §24 | Initiation Integrity, Hardening & Harmonization (T1.77–T1.89) |
| 13 | §25 | Phase 1.3 — Initiation Schema & Validation Harmonization (T1.84–T1.89) |
| 14 | §26 | Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95) |
| 15 | §27 | Schema Discovery & Registration — Discovery-Driven Loading (T1.96) |
| 16 | §28 | System Parameters — SSOT Centralization (T1.97) |
| 17 | §29 | Universal Path Resolution & Schema-Driven Initialization (I089 + I090) |
| 18 | §30 | Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I092 / R60) |
| 19 | §32 | Data Export — CSV/Excel Pipeline Output (I126 / L22) — 🔷 PLANNED |
| 20 | §47 | Schema-Driven Export Columns — Replace Hardcoded 11-Field Subset (I193) — ✅ COMPLETE |
| 21 | §48 | Appendix D vs. Actual Pipeline Cross-Source Audit — 🔷 PLANNED |
| 22 | §49 | Appendix E+F vs. Pipeline Architecture Cross-Source Audit — Gap Remediation (I208–I225) |
| 23 | §50 | `str(5)` Bug Fix — Restore Exception Messages Across All Error Paths (I226) |
