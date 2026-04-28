# Core Utility and Foundation Refactoring Workplan

## 1. Document Metadata
- **Document ID**: WP-ARCH-2026-001
- **Status**: Draft (Awaiting Approval)
- **Version**: 1.3.0
- **Revision History**:
    - v1.0.0 (2026-04-27): Initial draft incorporating modular foundation and UI layer refactoring.
    - v1.1.0 (2026-04-27): Added Pipeline Context Object to encapsulate state management.
    - v1.2.0 (2026-04-27): Renamed `dcc_ui` to `utility_engine` to better reflect its role as an interface utility hub.
    - v1.3.0 (2026-04-28): Added Phase 6 for Context Augmentation and verification of pending features (get_columns_by_phase, error_catalog).

## 2. Objective
Restructure the `dcc/workflow` directory to separate universal foundation logic and utility components from domain-specific processing engines. This includes implementing a centralized `PipelineContext` object to manage state consistently across all engines.

### 2.1 Feature Verification Status

| Feature | Requirement | Status | Note |
| :--- | :--- | :--- | :--- |
| Path Normalization | Manage Win/Linux paths | ✅ | Implemented in `core_engine/paths` |
| DataFrame Container | Store Raw/Mapped/Processed | ✅ | Implemented in `PipelineContext.data` |
| Parameters/State | Store resolved settings/results | ✅ | Implemented in `PipelineContext.parameters/state` |
| Phase Helper | `get_columns_by_phase()` | ✅ | Implemented in `PipelineBlueprint` |
| Error Catalog | Centralized error lookup | ✅ | Integrated into `PipelineBlueprint` |
| Performance | Fast load times (<10ms) | ✅ | Integrated `PipelineTelemetry` tracking |

**Pending changes to be verified:**
(rest of the section remains same but shifted to 2.2)

## 2.2 Pipeline Context Design Goals
`pipelineContext` acts as the "central nervous system" of dcc_engine_pipeline...
- Normalizes and manages all file system paths for both Windows and Linux, ensuring consistent access to input Excel files, JSON schemas, and output directories.
- Stores the 48-column blueprint and error catalogs loaded from your JSON files, allowing engines to look up P1–P4 phase logic and standardized error messages without repeated disk reads.
- Tracks the real-time progress of the run, including setup readiness, schema validation results, and the Data Health Score.
- Acts as a container for the DataFrames (Raw, Mapped, and Processed), ensuring data integrity as it moves from the Mapper Engine to the Processor Engine.
- It separates business logic (the code) from business rules (the schemas), allowing to update rules like the 4-digit zero-padding or P3 date logic without touching the Python scripts.
- It provides helpers like get_columns_by_phase(), which ensures that such as Phase P1 (Anchors) are validated before Phase P3 (Calculations) begin, preventing errors like the negative delay values.
- By centralizing the error_catalog, it ensures that all total errors found in the pipeline are reported with consistent codes and severity levels across all rows of data.
- It loads context once, it maintains the high-speed performance (e.g., 6.14ms schema load time) required for analytical processing.

## 3. Scope Summary
The scope covers all six primary engines of the DCC pipeline and the main orchestrator. It involves extracting shared utilities (logging, paths, system checks, data IO) and interface components (console printing, CLI parsing) into dedicated packages (`core_engine` and `utility_engine`), and introducing a unified context object to replace loose variable passing.

## 4. Index of Content
- [1. Document Metadata](#1-document-metadata)
- [2. Objective](#2-objective)
- [3. Scope Summary](#3-scope-summary)
- [4. Index of Content](#4-index-of-content)
- [5. Evaluation and Alignment](#5-evaluation-and-alignment)
- [6. Dependencies](#6-dependencies)
- [7. Proposed Changes (Updated/Created)](#7-proposed-changes-updatedcreated)
- [8. Implementation Phases](#8-implementation-phases)
- [9. Timeline and Milestones](#9-timeline-and-milestones)
- [10. Risks and Mitigation](#10-risks-and-mitigation)
- [11. Success Criteria](#11-success-criteria)
- [12. References](#12-references)

## 5. Evaluation and Alignment
The current architecture suffers from "God Module" syndrome and "Prop Drilling" where numerous individual variables (paths, parameters, dataframes) are passed through multiple function layers. Implementing a `PipelineContext` object aligns with modern software design patterns (State Pattern/Context Pattern), reducing function signature complexity and improving traceability.

## 6. Dependencies
- **Task Dependencies**: Requires a full freeze on engine logic modifications during the migration to avoid merge conflicts.
- **System Dependencies**: Relies on existing Python 3.x environment and standard libraries (`dataclasses`, `pathlib`, `logging`, `argparse`).

## 7. Proposed Changes (Updated/Created)

### 7.1 Object Definition & Purpose

| Object | Status | Purpose | Source Schema |
| :--- | :--- | :--- | :--- |
| **`PipelinePaths`** | ✅ Complete | Centralized resolution of all filesystem paths (Input, Output, Config, Logs). | N/A |
| **`PipelineBlueprint`** | 🏗️ **NEW** | **The Rulebook**: Immutable storage for the 48-column schema, phase maps, and error catalogs. | `dcc_register_config.json`, `data_error_config.json`, `system_error_config.json` |
| **`PipelineState`** | ✅ Complete | **The Scoreboard**: Mutable storage for execution results, validation errors, and progress. | N/A |
| **`PipelineTelemetry`** | 🏗️ **NEW** | **Performance Trace**: Tracking execution time, row counts, and data health metrics. | N/A |
| **`PipelineContext`** | ✅ Complete | **The SSOT**: Unified container passing Blueprint, State, Path, and Data objects. | `project_config.json` |
| **`PipelineData`** | ✅ Complete | Container for DataFrames (Raw, Mapped, Processed). | N/A |

### 7.2 Comparison: Current vs. Proposed Architecture

| Feature | Current State (v1.2) | Proposed State (v1.3) |
| :--- | :--- | :--- |
| **Structure** | Nested dicts inside `PipelineState`. | Split into `Blueprint` (Rules) and `State` (Results). |
| **Column Rules** | Mixed with state in `resolved_schema`. | Dedicated `Blueprint.columns` (Immutable). |
| **Phases** | Recalculated locally in engines. | Pre-calculated `Blueprint.phase_map` (Cached). |
| **Error Definitions** | Loaded per engine from disk. | Centralized `Blueprint.error_catalog`. |
| **Performance** | Not tracked. | Integrated `PipelineTelemetry` (Timing/KPIs). |
| **Environment** | Loose checks in `main()`. | Persisted `PipelineState.environment` snapshot. |
| **SSOT Status** | Partial (Prop-drilling still exists). | Full (Engines only receive `PipelineContext`). |

### 7.3 Detailed Object Schema

#### [NEW] `PipelineBlueprint` (Static Rules)
- `columns`: Detailed definition of all 48 blueprint columns.
- `error_catalog`: Full registry of S-C-S and L-M-F codes.
- `phase_map`: Dict mapping phases (`P1`, `P2`, etc.) to column lists.
- `validation_rules`: Global logic flags (e.g., `fail_fast`).

#### [UPDATE] `PipelineState` (Mutable Results)
- `mapping_summary`: Results of the fuzzy matching process.
- `validation_errors`: Collection of errors found during processing.
- `environment`: Snapshot of OS, Python version, and dependency status.
- `engine_status`: Registry of completed vs. pending pipeline stages.

#### [NEW] `PipelineTelemetry` (Metrics)
- `execution_times`: Dict of `engine_name: duration_seconds`.
- `data_metrics`: Row counts, null rates, and health score averages.
- `memory_usage`: Peak memory consumption during processing.

## 8. Implementation Phases

### Phase 1: Analysis & Identification
- [x] Evaluate all engines for cross-engine imports.
- [x] Catalog "Universal" functions (e.g., `status_print`, `load_excel_data`, `DEBUG_OBJECT`).
- [x] Map all variables currently passed between stages to define the `PipelineContext` schema.

### Phase 2: Foundation Layer (`core_engine`)
- [x] Migrate Logging & Debug Object logic to `core_engine/logging`.
- [x] Migrate Path resolution and OS detection to `core_engine/paths`.
- [x] Migrate Universal Data IO to `core_engine/io`.
- [x] **Implement `PipelineContext`**: Define a dataclass in `core_engine/context.py` to hold execution state.
- [x] Implement `BaseEngine` and `BaseProcessor` in `core_engine/base`.

### Phase 3: Utility Layer (`utility_engine`)
- [x] Migrate Console UI functions to `utility_engine/console`.
- [x] Migrate CLI argument parsing to `utility_engine/cli`.
- [x] Migrate System Error registry to `utility_engine/errors`.

### Phase 4: Domain Engine Refactoring
- [x] Update engines to utilize `core_engine` and `utility_engine`.
- [x] **Refactor Engine Signatures**: Update engine methods to accept `PipelineContext` instead of individual arguments.
- [x] Remove redundant internal utility folders.

### Phase 5: Orchestrator Alignment
- [x] Finalize `dcc_engine_pipeline.py` with the new hierarchy and context management.
- [x] Conduct end-to-end integration testing.

### Phase 6: Context Augmentation & Verification ✅
- [x] **Implement `PipelineBlueprint`**: Create immutable rule container in `core_engine/context.py`.
- [x] **Implement `PipelineTelemetry`**: Create performance tracking container in `core_engine/context.py`.
- [x] **Centralize Error Catalog**: Migrate `data_error_config.json` loading to `PipelineBlueprint`.
- [x] **Centralize Phase Helper**: Implement `Blueprint.get_columns_by_phase(phase: str)`.
- [x] **Refactor CalculationEngine**: Update to use `context.blueprint` for rules and `context.telemetry` for timing.
- [x] **Verify Environment Snapshot**: Ensure `PipelineState.environment` captures full system context during initiation.

## 9. Timeline and Milestones
- **Milestone 1**: Phase 1 Analysis Report and `PipelineContext` definition completed.
- **Milestone 2**: `core_engine` (including Context) and `utility_engine` packages established.
- **Milestone 3**: All engines refactored to use `PipelineContext`.
- **Milestone 4**: Final integration test pass and version v1.2.0 release.
- **Milestone 5**: Phase 6 Context Augmentation and verification of pending features completed. ✅

## 10. Risks and Mitigation
- **Risk**: `PipelineContext` becomes a "God Object" if not strictly defined.
- **Mitigation**: Use typed dataclasses and clear property grouping (e.g., `context.paths`, `context.data`, `context.results`).
- **Risk**: Regression in path resolution on Windows/Linux environments.
- **Mitigation**: Use existing test suite to validate cross-platform path handling after migration.

## 11. Success Criteria
- Zero circular dependencies (no lazy imports required).
- Function signatures in `run_engine_pipeline` reduced to primarily passing the context.
- `initiation_engine` contains only setup validation logic.
- All engines use standardized `BaseEngine` or `BaseProcessor`.
- Successful end-to-end execution of the pipeline with consistent log output.

## 12. References
- [dcc_engine_pipeline.py](file:///home/franklin/dsai/Engineering-and-Design/dcc/workflow/dcc_engine_pipeline.py)
- [agent_rule.md](file:///home/franklin/dsai/Engineering-and-Design/agent_rule.md)
- [initiation_engine/__init__.py](file:///home/franklin/dsai/Engineering-and-Design/dcc/workflow/initiation_engine/__init__.py)
- [Phase 1 Analysis Report](file:///home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/reports/phase_1_analysis.md)
- [Phase 2 & 3 Implementation Report](file:///home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/reports/phase_2_3_implementation.md)
- [Phase 4 & 5 Implementation Report](file:///home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/reports/phase_4_5_implementation.md)
- [Phase 6 Implementation Report](file:///home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/reports/phase_6_implementation.md)

---

## Appendix A: Catalog of Shared Functions & Resources

| Function / Resource | Current Provider | Consumer Engines | Target Package |
| :--- | :--- | :--- | :--- |
| **`status_print`**, **`milestone_print`** | `initiation_engine` | All Engines | `utility_engine/console` |
| **`debug_print`**, **`DEBUG_LEVEL`** | `initiation_engine` | All Engines | `utility_engine/console` & `core_engine/logging` |
| **`log_error`**, **`log_context`** | `initiation_engine` | Mapper, Processor, Schema, AI Ops | `core_engine/logging` |
| **`get_debug_object`** | `initiation_engine` | Processor, Reporting | `core_engine/logging` |
| **`system_error_print`** | `initiation_engine` | All Engines | `utility_engine/errors` |
| **`safe_resolve`** | `schema_engine` | Pipeline, Initiation, Schema | `core_engine/paths` |
| **`resolve_platform_paths`** | `initiation_engine` | Pipeline, Initiation | `core_engine/paths` |
| **`parse_cli_args`** | `initiation_engine` | Main Orchestrator | `utility_engine/cli` |
| **`load_excel_data`** | `processor_engine` | Pipeline, Processor | `core_engine/io` |
| **`PipelineContext`** | N/A | All Engines | `core_engine/context` |

## Appendix B: Reconsolidation Strategy

1. **Extraction**: Identify functions in `initiation_engine/utils` and `processor_engine/utils` that meet the "universal" criteria.
2. **Standardization**: Move these to `core_engine` (foundation) or `utility_engine` (interface).
3. **State Management**: Implement the `PipelineContext` to replace individual variable passing in `run_engine_pipeline`.
4. **Specialization**: Refactor `initiation_engine` to remove its utility role and focus only on Step 1 validation logic.
5. **UI Consistency**: Ensure all engines use `utility_engine/console` for all terminal output to provide a unified user experience.
