# Pipeline Architecture Design Workplan

## 1. Title and Description
This workplan defines architecture compliance, gap closure, and execution phases for the DCC pipeline architecture across initiation, schema, mapper, processor, reporting, and AI ops modules.

## 2. Document Control
- Workplan ID: `WP-PIPE-ARCH-001`
- Version: `v0.4`
- Status: `Active`
- Last Updated: `2026-04-28`
- Revision Summary: Phase 1 completed with requirement traceability report and log updates.

## 3. Revision History
1. `v0.1` - Initial requirement capture for pipeline architecture.
2. `v0.2` - Added compliance checklist and evidence-based status.
3. `v0.3` - Full workplan restructure per `agent_rule.md`, phase/checklist execution model added.
4. `v0.4` - Phase 1 closed; report and logs updated.

## 4. Objective
Deliver a fully traceable, phase-driven architecture workplan that measures current compliance and closes remaining gaps to achieve full alignment with the pipeline architecture requirements.

## 5. Scope Summary (Requirements In Scope)
Important note: always keep the following requirements as checking points for completion of pipeline architecture design.

### 5.1 Modularity and Decoupling
The architecture should separate the "how" (logic) from the "what" (data/rules).
1. `Engine Separation`: Logic should be divided into specialized, independent units, such as initiation, mapping, and processing.
2. `Centralized Context`: A single "Source of Truth" object (like a PipelineContext) should be used to pass state between engines, preventing "prop drilling" where dozens of individual variables are passed manually.
3. `Stateless Utilities`: Shared functions (date math, string cleaning) should reside in a separate core or utility layer to avoid circular dependencies between engines.
4. `Dependency Injection (DI)`: an architectural pattern for engines where a component does not create its own dependencies (like the CalculationEngine). Instead, the dependencies are "injected" or provided to it from the outside. This will allow `swappable logic`, `simplified testing` and `platform flexibility`.

### 5.2 Configuration and Data Health
A robust pipeline must handle varied data quality without crashing.
1. `Schema-Driven Logic`: Processing rules (like the 48-column blueprint or P1–P4 phases) should be stored in external files (JSON/Markdown) rather than hard-coded in Python.
2. `Data Validation Gates`: The pipeline should implement multi-stage validation, checking project structure and schema integrity before attempting data calculations. Data Health Score Matrix should be considered.
3. `Error Categorization`: Requirements should include a standardized error catalog to report issues with consistent codes (e.g., P1-A-P-0101) and severity levels.

### 5.3 Execution Control and Diagnostics
The system needs to provide transparency into its internal operations.
1. `Phase-Aware Orchestration`: The design must support sequential processing phases, ensuring that "Anchor" data is validated before dependent calculations are performed.
2. `Comprehensive Logging`: Architectural requirements should include multi-level logging (Status, Milestone, Debug) and the ability to export a "Data Health" dashboard for end-users.
3. `Platform Independence`: The code must handle environment-specific constraints, such as normalizing file paths for Windows vs. Linux environments.

### 5.4 Scalability and Extensibility
The design should allow for future growth without requiring a full rewrite.
1. `Non-Blocking Operations`: Secondary tasks, such as AI-driven risk analysis or reporting, should be integrated as modular "plug-ins" that do not block the primary data flow.
2. `Performance Optimization`: Requirements should include efficient data handling (such as using DuckDB or optimized Pandas operations) to maintain fast execution times even as row counts grow, while considering pandas still appropriate for this pipeline.
3. `RefResolver Support`: The system should be able to resolve complex dependencies between different schema files dynamically.

### 5.5 User Interface (UI)
The UI should not be treated as a separate "skin," but rather as a specialized consumer of the PipelineContext. Since pipeline can handle 11,099 rows and 1,238 total errors, the UI must prioritize clarity and exception handling over raw data display.
1. The "Health-First" Dashboard:
- `KPI Visualization`: Use the calculated Health KPI (e.g., 98.5%) to give users a high-level "Go/No-Go" decision point.
- `Severity Categorization`: The UI should pull from the error_catalog to display a breakdown of Critical, High, and Medium errors.
2. Live Progress Tracking:
- `Milestone Tracking / Step-by-Step Status`: UI should show current log_context in P1–P4 lifecycle.
- `Dynamic Counts`: UI should update folder/file validation counts.
- `Telemetry Module`: emit heartbeat logs every 1,000 rows (`rows_processed`, `current_phase`, `memory_usage`).
3. Exception Navigation:
- `Error Deep-Linking`: filter rows where `Validation_Errors` is non-empty.
- `AI Insight Display`: show non-blocking AI suggestions/risk alerts.
4. Configuration and Overrides:
- `Path Pickers`: set `base_path` and `upload_file_name` visually.
- `Parameter Overrides`: toggle `debug_mode` and set `nrows` via UI.

## 6. Content Index
1. Title and Description
2. Document Control
3. Revision History
4. Objective
5. Scope Summary (Requirements In Scope)
6. Content Index
7. Evaluation and Alignment with Existing Architecture
8. Dependencies with Other Tasks
9. Files and Modules to Update/Create
10. Implementation Phases and Task Breakdown
11. Timeline, Milestones, and Deliverables
12. Risks and Mitigation
13. Potential Future Issues
14. Success Criteria
15. References

## 7. Evaluation and Alignment with Existing Architecture
Current compliance status:
- Total requirements checked: `18`
- `PASS`: `13`
- `PARTIAL`: `5`
- `FAIL`: `0`
- Overall status: `PARTIALLY COMPLIANT`

Gap focus:
1. Dependency Injection depth in processor engine.
2. Core heartbeat telemetry every 1,000 rows.
3. UI-facing progress/exception contracts beyond backend artifact exports.

## 8. Dependencies with Other Tasks
1. [core_utility_engine_workplan.md](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/core_utility_engine_workplan.md)
2. Engine-level implementation documents under `dcc/workflow/*/readme.md`
3. Logging and reporting obligations from `agent_rule.md` Section 8 and Section 9

## 9. Files and Modules to Update/Create
Planned target areas:
1. `dcc/workflow/dcc_engine_pipeline.py`
2. `dcc/workflow/core_engine/context.py`
3. `dcc/workflow/processor_engine/core/engine.py`
4. `dcc/workflow/ai_ops_engine/streaming/event_stream.py`
5. `dcc/workflow/reporting_engine/error_reporter.py`
6. `dcc/workplan/reports/` (phase reports)
7. `dcc/workplan/issue_log.md` (issue logging)
8. `dcc/log/update_log.md` (project log updates)

## 10. Implementation Phases and Task Breakdown

### Phase 1: Workplan and Traceability Baseline
Tasks:
1. Lock scope requirements and preserve baseline list.
2. Build requirement-to-evidence mapping with status.
3. Confirm report/log locations.

Checklist:
- [x] Requirements retained in scope summary.
- [x] Compliance status captured (`PASS/PARTIAL/FAIL`).
- [x] Requirement trace matrix exported as report artifact.

Phase 1 report:
1. [phase_1_traceability_report.md](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/reports/phase_1_traceability_report.md)

### Phase 2: DI and Orchestration Hardening
Tasks:
1. Define injectable interfaces/factories for processor dependencies.
2. Refactor internal direct instantiation where needed.
3. Validate behavior parity.

Checklist:
- [ ] DI entry points defined.
- [ ] Core dependencies injectable without behavior regression.
- [ ] Unit/integration tests updated.

### Phase 3: Telemetry and Progress Contract
Tasks:
1. Implement row heartbeat every 1,000 rows.
2. Include `rows_processed`, `current_phase`, `memory_usage`.
3. Standardize progress event contract for UI consumption.

Checklist:
- [ ] Heartbeat emitted at required interval.
- [ ] Payload fields complete and validated.
- [ ] Progress events integrated into pipeline flow.

### Phase 4: UI Consumer Contract and Overrides
Tasks:
1. Define backend contract for error deep-link/filter on `Validation_Errors`.
2. Define backend interface for path and parameter overrides.
3. Validate AI insight artifact integration in UI contract.

Checklist:
- [ ] Error navigation contract documented.
- [ ] Override contract documented (`base_path`, `upload_file_name`, `debug_mode`, `nrows`).
- [ ] AI insight linkage documented and testable.

### Phase 5: Validation, Reporting, and Closure
Tasks:
1. Run architecture compliance reassessment.
2. Publish phase reports and update logs.
3. Close open gaps or mark deferred items with rationale.

Checklist:
- [ ] All phase reports created under `dcc/workplan/reports/`.
- [ ] `issue_log.md` and `dcc/log/update_log.md` updated.
- [ ] Final compliance summary updated in this workplan.

## 11. Timeline, Milestones, and Deliverables
1. Milestone M1: Phase 1 complete with traceability baseline.
2. Milestone M2: Phase 2 and 3 implemented and verified.
3. Milestone M3: Phase 4 contract finalized.
4. Milestone M4: Phase 5 closure report issued.

Deliverables:
1. Updated architecture workplan (this file).
2. Phase reports in `dcc/workplan/reports/`.
3. Updated issue and update logs.
4. Final compliance matrix and closure summary.

## 12. Risks and Mitigation
1. Risk: DI refactor may break existing processor flows.
Mitigation: Introduce interfaces incrementally and keep compatibility wrapper.
2. Risk: Telemetry heartbeat may add runtime overhead.
Mitigation: Fixed interval emission and lightweight payload generation.
3. Risk: UI contract drift from backend outputs.
Mitigation: Versioned contract notes and regression checks with sample artifacts.

## 13. Potential Future Issues
1. Cross-module contract versioning between workflow and UI may require schema governance.
2. Performance thresholds may need dataset-tiered tuning beyond current row profile.
3. Future plugin expansion may require standardized event bus patterns.

## 14. Success Criteria
1. Every requirement in Scope Summary has a current status (`PASS/PARTIAL/FAIL`) with evidence.
2. Phase completion is checklist-driven: a phase is complete only when all checklist items are checked.
3. Workplan structure remains compliant with `agent_rule.md` Section 8 requirements.
4. Required logs and reports are generated and linked.
5. Final architecture status reaches `FULLY COMPLIANT` or documents approved deferred exceptions.

## 15. References
1. [agent_rule.md](/home/franklin/dsai/Engineering-and-Design/agent_rule.md)
2. [dcc_engine_pipeline.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/dcc_engine_pipeline.py)
3. [context.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/core_engine/context.py)
4. [engine.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/processor_engine/core/engine.py)
5. [ref_resolver.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/schema_engine/loader/ref_resolver.py)
6. [error_reporter.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/reporting_engine/error_reporter.py)
7. [core_utility_engine_workplan.md](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/core_utility_engine_workplan.md)
