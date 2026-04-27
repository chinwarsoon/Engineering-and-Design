# Core Utility and Foundation Refactoring Workplan

## 1. Document Metadata
- **Document ID**: WP-ARCH-2026-001
- **Status**: Draft (Awaiting Approval)
- **Version**: 1.2.0
- **Revision History**:
    - v1.0.0 (2026-04-27): Initial draft incorporating modular foundation and UI layer refactoring.
    - v1.1.0 (2026-04-27): Added Pipeline Context Object to encapsulate state management.
    - v1.2.0 (2026-04-27): Renamed `dcc_ui` to `dcc_utility` to better reflect its role as an interface utility hub.

## 2. Objective
Restructure the `dcc/workflow` directory to separate universal foundation logic and utility components from domain-specific processing engines. This includes implementing a centralized `PipelineContext` object to manage state consistently across all engines.

## 3. Scope Summary
The scope covers all six primary engines of the DCC pipeline and the main orchestrator. It involves extracting shared utilities (logging, paths, system checks, data IO) and interface components (console printing, CLI parsing) into dedicated packages (`dcc_core` and `dcc_utility`), and introducing a unified context object to replace loose variable passing.

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
### [NEW] Packages & Objects
- `dcc_core/`: Foundation layer for universal utilities.
- **`PipelineContext`**: A centralized state object to store parameters, resolved paths, schemas, and processing results.
- `dcc_utility/`: Interface layer for user interaction and general utilities.

### [MODIFY] Existing Engines
- `initiation_engine/`: Remove utility subfolders; specialize on setup validation.
- `processor_engine/`: Update to use `dcc_utility` for internal step logging and accept `PipelineContext`.
- `reporting_engine/`: Consolidate all summary and diagnostic reporting using `PipelineContext`.
- `dcc_engine_pipeline.py`: Update to initialize and pass the `PipelineContext` object.

## 8. Implementation Phases

### Phase 1: Analysis & Identification
- [x] Evaluate all engines for cross-engine imports.
- [x] Catalog "Universal" functions (e.g., `status_print`, `load_excel_data`, `DEBUG_OBJECT`).
- [x] Map all variables currently passed between stages to define the `PipelineContext` schema.

### Phase 2: Foundation Layer (`dcc_core`)
- [x] Migrate Logging & Debug Object logic to `dcc_core/logging`.
- [x] Migrate Path resolution and OS detection to `dcc_core/paths`.
- [x] Migrate Universal Data IO to `dcc_core/io`.
- [x] **Implement `PipelineContext`**: Define a dataclass in `dcc_core/context.py` to hold execution state.
- [x] Implement `BaseEngine` and `BaseProcessor` in `dcc_core/base`.

### Phase 3: Utility Layer (`dcc_utility`)
- [x] Migrate Console UI functions to `dcc_utility/console`.
- [x] Migrate CLI argument parsing to `dcc_utility/cli`.
- [x] Migrate System Error registry to `dcc_utility/errors`.

### Phase 4: Domain Engine Refactoring
- Update engines to utilize `dcc_core` and `dcc_utility`.
- **Refactor Engine Signatures**: Update engine methods to accept `PipelineContext` instead of individual arguments.
- Remove redundant internal utility folders.

### Phase 5: Orchestrator Alignment
- Finalize `dcc_engine_pipeline.py` with the new hierarchy and context management.
- Conduct end-to-end integration testing.

## 9. Timeline and Milestones
- **Milestone 1**: Phase 1 Analysis Report and `PipelineContext` definition completed.
- **Milestone 2**: `dcc_core` (including Context) and `dcc_utility` packages established.
- **Milestone 3**: All engines refactored to use `PipelineContext`.
- **Milestone 4**: Final integration test pass and version v1.2.0 release.

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

---

## Appendix A: Catalog of Shared Functions & Resources

| Function / Resource | Current Provider | Consumer Engines | Target Package |
| :--- | :--- | :--- | :--- |
| **`status_print`**, **`milestone_print`** | `initiation_engine` | All Engines | `dcc_utility/console` |
| **`debug_print`**, **`DEBUG_LEVEL`** | `initiation_engine` | All Engines | `dcc_utility/console` & `dcc_core/logging` |
| **`log_error`**, **`log_context`** | `initiation_engine` | Mapper, Processor, Schema, AI Ops | `dcc_core/logging` |
| **`get_debug_object`** | `initiation_engine` | Processor, Reporting | `dcc_core/logging` |
| **`system_error_print`** | `initiation_engine` | All Engines | `dcc_utility/errors` |
| **`safe_resolve`** | `schema_engine` | Pipeline, Initiation, Schema | `dcc_core/paths` |
| **`resolve_platform_paths`** | `initiation_engine` | Pipeline, Initiation | `dcc_core/paths` |
| **`parse_cli_args`** | `initiation_engine` | Main Orchestrator | `dcc_utility/cli` |
| **`load_excel_data`** | `processor_engine` | Pipeline, Processor | `dcc_core/io` |
| **`PipelineContext`** | N/A | All Engines | `dcc_core/context` |

## Appendix B: Reconsolidation Strategy

1. **Extraction**: Identify functions in `initiation_engine/utils` and `processor_engine/utils` that meet the "universal" criteria.
2. **Standardization**: Move these to `dcc_core` (foundation) or `dcc_utility` (interface).
3. **State Management**: Implement the `PipelineContext` to replace individual variable passing in `run_engine_pipeline`.
4. **Specialization**: Refactor `initiation_engine` to remove its utility role and focus only on Step 1 validation logic.
5. **UI Consistency**: Ensure all engines use `dcc_utility/console` for all terminal output to provide a unified user experience.
