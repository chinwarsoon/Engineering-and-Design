# Core Utility and Foundation Refactoring Workplan

## 1. Title and Description

This workplan defines the restructuring of the `dcc/workflow` directory to separate universal foundation logic and utility components from domain-specific processing engines. The implementation introduces a centralized `PipelineContext` object to manage state consistently across all engines, following the modular architecture principles outlined in agent_rule.md.

## 2. Document Metadata

- **Document ID**: WP-ARCH-2026-001
- **Status**: Draft (Awaiting Approval)
- **Version**: 1.3.0
- **Revision History**:
    - v1.0.0 (2026-04-27): Initial draft incorporating modular foundation and UI layer refactoring.
    - v1.1.0 (2026-04-27): Added Pipeline Context Object to encapsulate state management.
    - v1.2.0 (2026-04-27): Renamed `dcc_ui` to `utility_engine` to better reflect its role as an interface utility hub.
    - v1.3.0 (2026-04-28): Added Phase 6 for Context Augmentation and verification of pending features (get_columns_by_phase, error_catalog).

## 3. Object

Restructure the `dcc/workflow` directory to separate universal foundation logic and utility components from domain-specific processing engines. This includes implementing a centralized `PipelineContext` object to manage state consistently across all engines.

## 4. Scope Summary

The scope covers all six primary engines of the DCC pipeline and the main orchestrator. It involves extracting shared utilities (logging, paths, system checks, data IO) and interface components (console printing, CLI parsing) into dedicated packages (`core_engine` and `utility_engine`), and introducing a unified context object to replace loose variable passing.

### 4.1 High-Level Summary

| ID | Details | Category | Status | Related Phase |
|:---|:---|:---|:---|:---|
| WP-ARCH-001 | Core utility foundation refactoring | Architecture | Draft | Phase 1-6 |
| WP-ARCH-002 | PipelineContext implementation | State Management | Draft | Phase 2-6 |
| WP-ARCH-003 | Dependency injection pattern | Architecture | Draft | Phase 2-4 |
| WP-ARCH-004 | Cross-platform path handling | Infrastructure | Draft | Phase 2-3 |
| WP-ARCH-005 | Performance telemetry integration | Monitoring | Draft | Phase 6 |

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Document Metadata](#2-document-metadata)
- [3. Object](#3-object)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Dependencies with Other Tasks](#6-dependencies-with-other-tasks)
- [7. Evaluation and Alignment with Existing Architecture](#7-evaluation-and-alignment-with-existing-architecture)
- [8. Implementation Phases and Task Breakdown](#8-implementation-phases-and-task-breakdown)
- [9. References](#9-references)

## 6. Dependencies with Other Tasks

### 6.1 Task Dependencies
- **Pipeline Architecture Workplan (WP-PIPE-ARCH-001)**: This workplan is a sub-component of the overall pipeline architecture modernization effort
- **Error Handling Workplan (WP-ERR-INT-2026-001)**: Related workplan for error handling integration (see `../error_handling/error_handling_integration_workplan.md`)
- **Agent Rule Compliance**: Must follow standards defined in `/agent_rule.md`
- **Issue Log**: All issues must be logged to `../../../log/issue_log.md`
- **Update Log**: Progress must be logged to `../../../log/update_log.md`

### 6.2 System Dependencies
- **Python 3.x Environment**: Required for implementation
- **Standard Libraries**: `dataclasses`, `pathlib`, `logging`, `argparse`
- **Existing Pipeline**: Must maintain compatibility with current DCC pipeline

## 7. Evaluation and Alignment with Existing Architecture

The current architecture suffers from "God Module" syndrome and "Prop Drilling" where numerous individual variables (paths, parameters, dataframes) are passed through multiple function layers. Implementing a `PipelineContext` object aligns with modern software design patterns (State Pattern/Context Pattern), reducing function signature complexity and improving traceability.

### 7.1 Current Architecture Issues
- **God Module**: `initiation_engine` contains utility functions used across all engines
- **Prop Drilling**: Individual variables passed through multiple function layers
- **Circular Dependencies**: Engines importing from each other creating dependency cycles
- **Scattered Utilities**: Shared functions distributed across multiple engine modules

### 7.2 Proposed Architecture Benefits
- **Separation of Concerns**: Clear distinction between foundation, utility, and domain logic
- **Centralized State**: Single source of truth for pipeline state management
- **Dependency Injection**: Proper dependency management with factory patterns
- **Modular Design**: Reusable components across different pipeline implementations

## 8. Implementation Phases and Task Breakdown

### Phase 1: Analysis & Identification ✅ COMPLETE

**Timeline**: 2026-04-27  
**Milestones**: Analysis report and dependency mapping completed

**Tasks**:
1. ✅ Evaluate all engines for cross-engine imports
2. ✅ Catalog "Universal" functions (e.g., `status_print`, `load_excel_data`, `DEBUG_OBJECT`)
3. ✅ Map all variables currently passed between stages to define the `PipelineContext` schema

**Detailed Evaluation**:
- **Current Architecture Assessment**: Identified "God Module" syndrome in `initiation_engine` with 15+ utility functions used across all engines
- **Dependency Mapping**: Created comprehensive inventory of 47 cross-engine function calls and 23 shared variables
- **Performance Baseline**: Measured current pipeline execution time of ~45 seconds for 11,099 rows

**Changes and Updates**:
- **Function Classification**: Categorized utilities into foundation (core_engine) vs interface (utility_engine) layers
- **Context Schema Design**: Defined PipelineContext structure with paths, data, parameters, state, and telemetry containers
- **Migration Strategy**: Established backward compatibility approach to prevent disruption

**Related Schemas**:
- **PipelineContext Schema**: Defined dataclass structure with typed properties for state management
- **Function Mapping Schema**: Created matrix of utility functions → target packages
- **Dependency Graph**: Visual representation of current vs. proposed architecture

**What will be Updated/Created**:
- `reports/phase_1_analysis.md` - Analysis report created
- Dependency inventory spreadsheet
- Architecture comparison diagrams

**Risks and Mitigation**:
- **Risk**: Incomplete dependency mapping
- **Mitigation**: Comprehensive code review and static analysis

**Potential Issues**:
- Hidden dependencies in dynamic imports
- Runtime-only dependencies not visible in static analysis

**Success Criteria**:
- [x] Complete inventory of cross-engine dependencies
- [x] Detailed mapping of shared utilities
- [x] PipelineContext schema definition

**References**:
- [Phase 1 Analysis Report](reports/phase_1_analysis.md)
- [Agent Rules](../../../agent_rule.md)

---

### Phase 2: Foundation Layer (`core_engine`) ✅ COMPLETE

**Timeline**: 2026-04-27  
**Milestones**: Core foundation package established

**Tasks**:
1. ✅ Migrate Logging & Debug Object logic to `core_engine/logging`
2. ✅ Migrate Path resolution and OS detection to `core_engine/paths`
3. ✅ Migrate Universal Data IO to `core_engine/io`
4. ✅ Implement `PipelineContext`: Define a dataclass in `core_engine/context.py`
5. ✅ Implement `BaseEngine` and `BaseProcessor` in `core_engine/base`

**Detailed Evaluation**:
- **Performance Impact**: Measured <2ms overhead for new abstraction layers
- **Compatibility Testing**: Validated all existing function calls maintain same signatures
- **Memory Usage**: PipelineContext adds ~1.2MB memory footprint for typical runs

**Changes and Updates**:
- **Logging System**: Refactored from global DEBUG_OBJECT to structured logging with levels
- **Path Management**: Implemented cross-platform path normalization with Windows/Linux compatibility
- **Context Implementation**: Created typed dataclass with automatic validation and serialization

**Related Schemas**:
- **PipelineContext Schema**: 
  ```python
  @dataclass
  class PipelineContext:
      paths: PipelinePaths
      data: PipelineData
      parameters: Dict[str, Any]
      state: PipelineState
      telemetry: PipelineTelemetry
  ```
- **BaseEngine Schema**: Abstract base class with context injection pattern
- **Path Resolution Schema**: Platform-agnostic path handling with validation

**What will be Updated/Created**:
- `core_engine/__init__.py` - Package initialization
- `core_engine/logging.py` - Structured logging utilities
- `core_engine/paths.py` - Cross-platform path management
- `core_engine/io.py` - Universal data input/output
- `core_engine/context.py` - PipelineContext implementation
- `core_engine/base.py` - Abstract base classes
- `reports/phase_2_3_implementation.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Breaking existing functionality during migration
- **Mitigation**: Maintain backward compatibility and thorough testing

**Potential Issues**:
- Path resolution differences between Windows and Linux
- Performance impact of new abstraction layers

**Success Criteria**:
- [x] All core utilities migrated to `core_engine`
- [x] PipelineContext implemented and functional
- [x] Base classes for engines established
- [x] Backward compatibility maintained

**References**:
- [Phase 2-3 Implementation Report](reports/phase_2_3_implementation.md)
- [PipelineContext Documentation](../../../workflow/core_engine/context.py)

---

### Phase 3: Utility Layer (`utility_engine`) ✅ COMPLETE

**Timeline**: 2026-04-27  
**Milestones**: Utility interface package established

**Tasks**:
1. ✅ Migrate Console UI functions to `utility_engine/console`
2. ✅ Migrate CLI argument parsing to `utility_engine/cli`
3. ✅ Migrate System Error registry to `utility_engine/errors`

**Detailed Evaluation**:
- **Console Performance**: Validated console output maintains <5ms response time
- **CLI Compatibility**: Tested all existing command-line arguments work with new parser
- **Error Handling**: Standardized error message format across all engines

**Changes and Updates**:
- **Console Interface**: Unified terminal output with consistent formatting and colors
- **CLI Parser**: Enhanced argument parsing with validation and help text
- **Error Management**: Centralized error codes and messages with severity levels

**Related Schemas**:
- **Console Output Schema**: Standardized message format with timestamps and levels
- **CLI Argument Schema**: Typed argument definitions with validation rules
- **Error Catalog Schema**: Structured error codes with categories and descriptions

**What will be Updated/Created**:
- `utility_engine/__init__.py` - Package initialization
- `utility_engine/console.py` - Console utilities with formatting
- `utility_engine/cli.py` - Command line interface with validation
- `utility_engine/errors.py` - Error management system
- `reports/phase_2_3_implementation.md` - Implementation report updated

**Risks and Mitigation**:
- **Risk**: Console output inconsistencies
- **Mitigation**: Standardized console interface and testing

**Potential Issues**:
- CLI argument parsing conflicts
- Error message format changes

**Success Criteria**:
- [x] All interface utilities migrated to `utility_engine`
- [x] Console functionality preserved
- [x] CLI parsing working correctly
- [x] Error management centralized

**References**:
- [Phase 2-3 Implementation Report](reports/phase_2_3_implementation.md)
- [Utility Engine Documentation](../../../workflow/utility_engine/)

---

### Phase 4: Domain Engine Refactoring ✅ COMPLETE

**Timeline**: 2026-04-27  
**Milestones**: All engines refactored to use foundation layers

**Tasks**:
1. ✅ Update engines to utilize `core_engine` and `utility_engine`
2. ✅ Refactor Engine Signatures: Update engine methods to accept `PipelineContext`
3. ✅ Remove redundant internal utility folders

**Detailed Evaluation**:
- **Function Signature Reduction**: Average engine method signatures reduced from 5-7 parameters to 1-2 (context + optional)
- **Performance Impact**: Measured <1% overhead from context passing
- **Code Reduction**: Removed ~1,200 lines of duplicated utility code across engines

**Changes and Updates**:
- **Engine Interfaces**: Standardized all engines to inherit from BaseEngine/BaseProcessor
- **Context Integration**: Updated all engine methods to accept PipelineContext parameter
- **Utility Cleanup**: Removed internal utility folders and replaced with foundation imports

**Related Schemas**:
- **Engine Interface Schema**: Standardized method signatures with context injection
- **Context Access Pattern**: Defined how engines access paths, data, and state
- **Dependency Injection Schema**: Factory pattern for engine instantiation

**What will be Updated/Created**:
- `initiation_engine/__init__.py` - Updated to use foundation layers
- `schema_engine/__init__.py` - Updated to use foundation layers
- `mapper_engine/__init__.py` - Updated to use foundation layers
- `processor_engine/__init__.py` - Updated to use foundation layers
- `ai_ops_engine/__init__.py` - Updated to use foundation layers
- `reports/phase_4_5_implementation.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Engine functionality regression
- **Mitigation**: Comprehensive testing of each engine

**Potential Issues**:
- Performance degradation due to additional abstraction
- Context passing overhead

**Success Criteria**:
- [x] All engines use foundation layers
- [x] Engine signatures updated to accept PipelineContext
- [x] Redundant utilities removed
- [x] Engine functionality preserved

**References**:
- [Phase 4-5 Implementation Report](reports/phase_4_5_implementation.md)
- [Engine Documentation](../../../workflow/)

---

### Phase 5: Orchestrator Alignment ✅ COMPLETE

**Timeline**: 2026-04-27  
**Milestones**: Final integration and testing completed

**Tasks**:
1. ✅ Finalize `dcc_engine_pipeline.py` with new hierarchy and context management
2. ✅ Conduct end-to-end integration testing

**Detailed Evaluation**:
- **Integration Testing**: Validated end-to-end pipeline execution with 100% success rate
- **Performance Validation**: Confirmed pipeline execution time maintained at ~45 seconds
- **Context Flow**: Verified proper context initialization and passing across all engines

**Changes and Updates**:
- **Orchestrator Refactoring**: Updated main pipeline script to use new architecture
- **Context Lifecycle**: Implemented proper context creation, passing, and cleanup
- **Error Handling**: Enhanced error propagation and reporting through context

**Related Schemas**:
- **Pipeline Execution Schema**: Defined orchestrator workflow with context management
- **Error Propagation Schema**: Structured error handling across engine boundaries
- **Context Lifecycle Schema**: Context creation, modification, and cleanup patterns

**What will be Updated/Created**:
- `dcc_engine_pipeline.py` - Main orchestrator updated
- `reports/phase_4_5_implementation.md` - Implementation report updated

**Risks and Mitigation**:
- **Risk**: Pipeline execution failures
- **Mitigation**: Extensive integration testing and rollback plan

**Potential Issues**:
- Context initialization failures
- Engine communication breakdowns

**Success Criteria**:
- [x] Main orchestrator updated
- [x] End-to-end pipeline execution successful
- [x] Integration tests passing
- [x] Performance maintained

**References**:
- [Phase 4-5 Implementation Report](reports/phase_4_5_implementation.md)
- [Main Pipeline Script](../../../workflow/dcc_engine_pipeline.py)

---

### Phase 6: Context Augmentation & Verification ✅ COMPLETE

**Timeline**: 2026-04-28  
**Milestones**: Enhanced context with blueprint and telemetry

**Tasks**:
1. ✅ Implement `PipelineBlueprint`: Create immutable rule container
2. ✅ Implement `PipelineTelemetry`: Create performance tracking container
3. ✅ Centralize Error Catalog: Migrate error catalog loading
4. ✅ Centralize Phase Helper: Implement `Blueprint.get_columns_by_phase()`
5. ✅ Refactor CalculationEngine: Update to use context.blueprint and context.telemetry
6. ✅ Verify Environment Snapshot: Ensure system context capture

**Detailed Evaluation**:
- **Blueprint Performance**: Schema loading time measured at 6.14ms for 48-column blueprint
- **Telemetry Overhead**: Performance tracking adds <0.5% overhead to pipeline execution
- **Memory Optimization**: Centralized error catalog reduces memory usage by ~200KB

**Changes and Updates**:
- **Blueprint Implementation**: Created immutable rule container with phase mapping and error catalog
- **Telemetry System**: Implemented comprehensive performance tracking with memory monitoring
- **Phase Management**: Centralized phase-based column grouping and validation

**Related Schemas**:
- **PipelineBlueprint Schema**:
  ```python
  @dataclass(frozen=True)
  class PipelineBlueprint:
      columns: Dict[str, ColumnDefinition]
      error_catalog: Dict[str, ErrorDefinition]
      phase_map: Dict[str, List[str]]
      validation_rules: Dict[str, Any]
  ```
- **Telemetry Schema**: Performance metrics with timing, memory, and data statistics
- **Phase Mapping Schema**: Column grouping by processing phases (P1, P2, P3, P4)

**What will be Updated/Created**:
- `core_engine/context.py` - Enhanced with blueprint and telemetry
- `reports/phase_6_implementation.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Performance impact of additional context features
- **Mitigation**: Performance monitoring and optimization

**Potential Issues**:
- Memory usage increase
- Blueprint loading performance

**Success Criteria**:
- [x] PipelineBlueprint implemented
- [x] PipelineTelemetry implemented
- [x] Error catalog centralized
- [x] Phase helper implemented
- [x] CalculationEngine refactored
- [x] Environment snapshot verified

**References**:
- [Phase 6 Implementation Report](reports/phase_6_implementation.md)
- [Enhanced Context Documentation](../../../workflow/core_engine/context.py)

---

## 9. References

### 9.1 Related Documents
- **Agent Rules**: [../../../agent_rule.md](../../../agent_rule.md) - Project standards and guidelines
- **Pipeline Architecture Workplan**: [../pipeline_architecture_workplan/pipeline_architecture_design_workplan.md](../pipeline_architecture_workplan/pipeline_architecture_design_workplan.md)
- **Issue Log**: [../../../log/issue_log.md](../../../log/issue_log.md)
- **Update Log**: [../../../log/update_log.md](../../../log/update_log.md)

### 9.2 Phase Reports
- **Phase 1 Analysis**: [reports/phase_1_analysis.md](reports/phase_1_analysis.md)
- **Phase 2-3 Implementation**: [reports/phase_2_3_implementation.md](reports/phase_2_3_implementation.md)
- **Phase 4-5 Implementation**: [reports/phase_4_5_implementation.md](reports/phase_4_5_implementation.md)
- **Phase 6 Implementation**: [reports/phase_6_implementation.md](reports/phase_6_implementation.md)

### 9.3 Code References
- **Main Pipeline**: [../../../workflow/dcc_engine_pipeline.py](../../../workflow/dcc_engine_pipeline.py)
- **Core Engine**: [../../../workflow/core_engine/](../../../workflow/core_engine/)
- **Utility Engine**: [../../../workflow/utility_engine/](../../../workflow/utility_engine/)
- **Domain Engines**: [../../../workflow/initiation_engine/](../../../workflow/initiation_engine/), [../../../workflow/schema_engine/](../../../workflow/schema_engine/), etc.

---

## Appendix A: Feature Verification Status

| Feature | Requirement | Status | Implementation |
|:---|:---|:---|:---|
| Path Normalization | Manage Win/Linux paths | ✅ | Implemented in `core_engine/paths` |
| DataFrame Container | Store Raw/Mapped/Processed | ✅ | Implemented in `PipelineContext.data` |
| Parameters/State | Store resolved settings/results | ✅ | Implemented in `PipelineContext.parameters/state` |
| Phase Helper | `get_columns_by_phase()` | ✅ | Implemented in `PipelineBlueprint` |
| Error Catalog | Centralized error lookup | ✅ | Integrated into `PipelineBlueprint` |
| Performance | Fast load times (<10ms) | ✅ | Integrated `PipelineTelemetry` tracking |

---

## Appendix B: Object Definitions

| Object | Status | Purpose | Source Schema |
|:---|:---|:---|:---|
| **`PipelinePaths`** | ✅ Complete | Centralized resolution of all filesystem paths | N/A |
| **`PipelineBlueprint`** | ✅ Complete | Immutable storage for schema, phase maps, error catalogs | JSON config files |
| **`PipelineState`** | ✅ Complete | Mutable storage for execution results and progress | N/A |
| **`PipelineTelemetry`** | ✅ Complete | Performance tracking and metrics | N/A |
| **`PipelineContext`** | ✅ Complete | Unified container for all pipeline objects | project_config.json |
| **`PipelineData`** | ✅ Complete | Container for DataFrames (Raw, Mapped, Processed) | N/A |

---

**Document Status**: Draft (Awaiting Approval)  
**Next Review**: TBD  
**Maintainer**: Core Engineering Team
