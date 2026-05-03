# Error Handling Integration Workplan

## 1. Title and Description

This workplan defines the full integration of centralized error handling throughout the DCC pipeline using `PipelineContext` as the **single source of truth** for error capture, categorization, and reporting, aligned with the pipeline architecture requirements in **WP-PIPE-ARCH-001** (notably **R06 Data Validation Gates**, **R07 Error Categorization**, and **R09 Comprehensive Logging**).

The integration goal is **not** to remove user-visible error output (e.g., `system_error_print()`), but to ensure that every error is also recorded in the pipeline context with enough structure for UI/CLI reporting and post-run diagnostics, with **explicit separation** between:
- **System-status errors**: environment, file system, configuration, dependency, and orchestration/runtime failures.
- **Data-handling errors**: validation and business-rule detection errors produced during processing (e.g., data health, `Validation_Errors`, dashboard exports).

## 2. Document Metadata

- **Document ID**: WP-ERR-INT-2026-001
- **Status**: In Progress (Phase 1 Complete)
- **Version**: 1.1.0
- **Revision History**:
    - v1.0.0 (2026-04-29): Initial draft for error handling integration workplan
    - v1.1.0 (2026-04-29): Phase 1 completed - Core context enhancement implemented

## 3. Object

Integrate centralized error handling throughout the DCC pipeline so that:
1. **All system-status errors** are recorded in `PipelineContext` (in addition to being printed) with consistent codes, severity, and engine/phase attribution.
2. **All data-handling errors** (row/column/business validation) remain produced by the processor error subsystem but are also **summarized and referenced** in `PipelineContext` for consistent reporting and UI consumption.
3. Fail-fast behavior is **context-driven** (blueprint/config controlled) rather than ad-hoc exception string checks.

## 4. Scope Summary

The scope covers all pipeline components that currently bypass a context-based error contract. This includes the main orchestrator, all engine modules, and utility functions that use direct printing or immediate exception raising without persisting structured error events in `PipelineContext`.

**In-scope separation requirement** (Architecture alignment):
- **System-status errors** must be tracked in context independently from data-handling errors so the UI/CLI can distinguish “pipeline cannot run” vs “pipeline ran but data has issues”.

### 4.1 High-Level Summary

| ID | Details | Category | Status | Related Phase |
|:---|:---|:---|:---|:---|
| WP-ERR-001 | Core context enhancement for error management | Architecture | Draft | Phase 1 |
| WP-ERR-002 | Orchestrator error handling integration | Integration | Draft | Phase 2 |
| WP-ERR-003 | Engine module error handling updates | Refactoring | Draft | Phase 3 |
| WP-ERR-004 | Error handling validation and testing | Quality Assurance | Draft | Phase 4 |
| WP-ERR-005 | Error reporting and documentation | Documentation | Draft | Phase 4 |

### Related Workplans

| Workplan | Scope | Location |
|----------|-------|----------|
| System Error Handling | S-C-S-XXXX system errors | `../system_error_handling/system_error_handling_workplan.md` |
| Error Handling Taxonomy | Complete code reference | `../error_handling_taxonomy.md` |
| Error Handling Integration | Context integration | `../integration/error_handling_integration_workplan.md` |
| Bootstrap Error Standardization | B-XXXX-NNN to S-C-S-XXXX migration | `../bootstrap_error_standardization/bootstrap_error_standardization_workplan.md` |

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
- **Core Utility Engine Workplan (WP-ARCH-2026-001)**: Depends on PipelineContext foundation being in place
- **Pipeline Architecture Workplan (WP-PIPE-ARCH-001)**: Architecture requirements baseline for context, validation gates, error categorization, and logging — see `../pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md`
- **Agent Rule Compliance**: Must follow standards defined in `/agent_rule.md`
- **Issue Log**: All issues must be logged to `../../log/issue_log.md`
- **Update Log**: Progress must be logged to `../../log/update_log.md`

### 6.2 System Dependencies
- **PipelineContext Foundation**: Must have functional PipelineContext and PipelineBlueprint classes
- **Error Catalog**: Requires existing error catalog in JSON configuration files
- **Testing Framework**: pytest for comprehensive error handling validation

## 7. Evaluation and Alignment with Existing Architecture

The current error handling architecture suffers from fragmented error management with direct calls to `system_error_print()` and immediate exception raising. This bypasses the centralized PipelineContext error management system, preventing error aggregation, comprehensive reporting, and configurable fail-fast behavior.

### 7.1 Current Architecture Issues
- **Fragmented Error Handling**: 15+ files using direct error printing bypass context
- **Lost Error Information**: System-status errors are not stored in `PipelineContext` as structured events (only printed/raised)
- **No Fail-Fast Control**: Immediate exception raising prevents configurable behavior
- **Missing Error Aggregation**: No comprehensive error summary or statistics
- **Inconsistent Error Reporting**: Different error handling patterns across components

### 7.2 Proposed Architecture Benefits
- **Centralized Error Tracking**: All errors stored in PipelineContext for comprehensive reporting
- **Configurable Fail-Fast**: Blueprint-controlled fail-fast behavior based on error severity
- **Error Aggregation**: Comprehensive error summaries with statistics and categorization
- **Consistent Patterns**: Standardized error handling across all pipeline components
- **Enhanced Debugging**: Better error context and historical tracking

## 8. Implementation Phases and Task Breakdown

### Phase 1: Core Context Enhancement ✅ COMPLETE

**Timeline**: 2026-04-29  
**Milestones**: Enhanced PipelineContext with comprehensive error management

**Tasks**:
1. Add structured error containers to `PipelineContext` to explicitly separate:
   - `system_status_errors`: orchestration/environment/filesystem/config/runtime failures (fatal + non-fatal)
   - `data_handling_summary`: reference/summary object for processor-produced data validation (keep existing `error_summary` compatibility)
2. Define a single canonical error event schema used by context for system-status errors (and optionally for future data events), including `domain`, `code`, `severity`, `engine`, `phase`, `timestamp`, and `details`.
3. Implement context APIs to record errors without losing user-visible output:
   - `context.add_system_error(...)` (records) + optional passthrough to `system_error_print(...)` (prints)
   - `context.capture_exception(...)` / `context.record_engine_failure(...)` (engine_status + event)
4. Implement `context.should_fail_fast(...)` driven by blueprint/config (replace string-matching `"FAIL FAST"` logic).
5. Align with **WP-PIPE-ARCH-001 R07** by ensuring system-status errors are code-driven and severity-tagged; keep blueprint `error_catalog` for data-handling logic errors as the SSOT.
6. Create standardized error-handling utilities (thin wrappers) used by orchestrator and engines to reduce repetition and enforce consistency.

**Detailed Evaluation**:
- **Current Assessment**: Context tracks `error_summary` (data-handling) but does not persist system-status errors; orchestrator relies on printing + raising.
- **Gap Analysis**: Missing a context-level system error event model and a policy-driven fail-fast decision point.
- **Performance Impact**: Expected <1ms overhead per error operation
- **Memory Usage**: ~50KB additional memory for typical error loads

**Changes and Updates**:
- **PipelineState Enhancement**: Add `system_status_errors` (list) and a stable data-handling summary reference (retain `error_summary`)
- **PipelineBlueprint Integration**: Keep `error_catalog` as SSOT for data logic errors (R07); add config keys for fail-fast policy
- **Utility Functions**: Standardize `handle_system_error(...)` and `handle_data_error_summary(...)` patterns
- **Error Summary Generation**: Provide a unified “run summary” view that includes both system-status errors and data-handling health KPIs

**Related Schemas**:
- **PipelineErrorEvent Schema (context-level canonical event)**:
  ```python
  @dataclass
  class PipelineErrorEvent:
      domain: str           # "system" | "data"
      code: str             # e.g., "S-F-S-0201" (system) or "P1-A-P-0101" (data)
      severity: str         # e.g., critical/high/medium/low (normalized)
      engine: Optional[str] # initiation/schema/mapper/processor/reporting/ai_ops
      phase: Optional[str]  # pipeline step or processing phase (P1/P2/P2.5/P3/P4)
      message: str
      details: Optional[str]
      timestamp: str
  ```
- **SystemStatusErrorSet Schema**: Aggregation by code, severity, engine, and “stops_pipeline”
- **DataHandlingSummary Schema**: Existing processor `error_summary` (health_kpi, total_errors, affected_rows) + optional pointers to exported artifacts
- **FailFastConfig Schema**: Blueprint-controlled fail-fast behavior rules

**What will be Updated/Created**:
- `core_engine/context.py` - Add system-status error containers + context APIs (additive, backward compatible)
- `core_engine/error_handling.py` - Standardized error handling utilities (orchestrator/engines)
- `reports/phase_1_context_enhancement.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Breaking existing PipelineContext functionality
- **Mitigation**: Additive changes only, maintain backward compatibility

**Potential Issues**:
- Memory usage increase with large error collections
- Performance impact of error aggregation

**Success Criteria**:
- [x] PipelineState enhanced with error tracking capabilities
- [x] PipelineBlueprint integrated with error catalog
- [x] Standardized error handling utilities created
- [x] Backward compatibility maintained

**Phase 1 Status**: ✅ COMPLETE  
**Implementation Report**: [reports/phase_1_context_enhancement.md](reports/phase_1_context_enhancement.md)

**References**:
- [Issue ISS-002](../../log/issue_log.md#issue-iss-002)
- [PipelineContext Documentation](../../workflow/core_engine/context.py)

---

### Phase 2: Orchestrator Integration ✅ PLANNED

**Timeline**: 2026-04-29  
**Milestones**: Main pipeline orchestrator using context-based error handling

**Tasks**:
1. Replace direct `system_error_print(...)` usage in `dcc_engine_pipeline.py` with context-mediated recording:
   - Record via `context.add_system_error(...)`
   - Continue printing for CLI visibility (either via wrapper or explicit print call)
2. Record engine lifecycle status in `context.state.engine_status` consistently (started/succeeded/failed) and attach failure events to context.
3. Replace legacy `"FAIL FAST" in str(exc)` detection with `context.should_fail_fast(...)` and explicit exception classification.
4. Ensure pipeline completion reporting includes **two sections**:
   - System-status error summary (fatal/non-fatal)
   - Data-handling health summary (from processor `error_summary`)
5. Update exception handling to preserve error context (store exception type/message/trace ref in context where safe) while maintaining current outward behavior (exit codes, JSON output).

**Detailed Evaluation**:
- **Current Assessment**: ~15 instances of direct error handling in main orchestrator (including try-except blocks across 4 pipeline steps and `main()` environment testing)
- **Impact Analysis**: Critical pipeline control points need context integration, specifically replacing legacy string-matching fail-fast checks (`"FAIL FAST" in str(exc)`).
- **Performance Impact**: Expected <2ms overhead per error handling operation
- **Compatibility**: Must maintain existing error codes and messages

**Changes and Updates**:
- **Error Pattern Replacement**: Replace direct printing-only patterns with “record in context + print” across all pipeline steps and within `main()`.
- **Fail-Fast Integration**: Refactor the legacy string-based 'FAIL FAST' logic in step 4 into structured blueprint-controlled failure behavior.
- **Error Reporting**: Add comprehensive end-of-run report that clearly distinguishes system-status vs data-handling outcomes
- **Exception Preservation**: Maintain error context through exception chain and wrap generic exceptions in context-aware pipeline exceptions.

**Related Schemas**:
- **PipelineErrorHandling Schema**:
  ```python
  def handle_system_error(
      context: PipelineContext,
      *,
      condition: bool,
      code: str,
      message: str,
      details: Optional[str] = None,
      engine: Optional[str] = None,
      phase: Optional[str] = None,
      print_to_stderr: bool = True,
  ) -> bool
  ```
- **ErrorReporting Schema**: Unified run summary (system-status + data-handling)
- **FailFastLogic Schema**: Blueprint-controlled failure decision logic

**What will be Updated/Created**:
- `dcc_engine_pipeline.py` - Updated with context-based error handling
- `reports/phase_2_orchestrator_integration.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Breaking pipeline execution flow
- **Mitigation**: Preserve existing exception behavior and error codes

**Potential Issues**:
- Complex error condition logic
- Fail-fast configuration conflicts

**Success Criteria**:
- [x] All direct error calls replaced with context-based handling
- [x] Fail-fast logic implemented and configurable
- [x] Error summary reporting functional
- [x] Pipeline execution flow preserved

**References**:
- [Main Pipeline Script](../../workflow/dcc_engine_pipeline.py)
- [Error Handling Proposal](../pipeline_architecture/core_utility_engine_workplan/proposed_error_handling_improvements.md)

---

### Phase 3: Engine Module Updates ✅ PLANNED

**Timeline**: 2026-04-29  
**Milestones**: All engine modules using context-based error handling

**Tasks**:
1. Update `initiation_engine`, `schema_engine`, and `mapper_engine` to record system-status failures into context (file not found, invalid schema, mapping failures) with consistent domain/code/severity.
2. Ensure `processor_engine` data-handling output remains authoritative (error catalog + aggregator) but is surfaced in context via `context.state.error_summary` and optional artifact pointers.
3. Standardize non-fatal warnings (e.g., optional dependency missing) as `system_status_errors` with `fatal=False` semantics (must not stop the pipeline unless policy says so).
4. Consolidate duplicate “system error print” implementations (avoid multiple sources of truth) and ensure utility layer remains responsible only for formatting/output, not state.
5. Update `ai_ops_engine` to treat AI failures as non-blocking system-status errors recorded in context (aligned to R11 non-blocking operations).

**Detailed Evaluation**:
- **Current Assessment**: 15+ files across all engine modules need updates
- **Complexity Analysis**: Different error patterns in each engine type
- **Performance Impact**: Expected <1% overall performance impact
- **Testing Requirements**: Comprehensive validation for each engine

**Changes and Updates**:
- **Engine-Specific Patterns**: Tailor error handling to each engine's needs
- **Context Integration**: Update all engines to use PipelineContext
- **Error Preservation**: Maintain error context across engine boundaries
- **Standardization**: Apply consistent error handling patterns

**Related Schemas**:
- **EngineErrorHandling Schema**: Standardized pattern for all engines
- **ErrorContext Schema**: Error information preservation across engines
- **EngineIntegration Schema**: Context passing between engine components

**What will be Updated/Created**:
- `ai_ops_engine/core/engine.py` - Updated error handling
- `mapper_engine/core/engine.py` - Updated error handling
- `initiation_engine/overrides.py` - Updated error handling
- `initiation_engine/utils/paths.py` - Updated error handling
- `processor_engine/core/engine.py` - Updated error handling
- `schema_engine/core/engine.py` - Updated error handling
- `utility_engine/bootstrap.py` - Updated error handling (see [Bootstrap Error Standardization](../bootstrap_error_standardization/bootstrap_error_standardization_workplan.md))
- `reports/phase_3_engine_updates.md` - Implementation report

**Risks and Mitigation**:
- **Risk**: Breaking engine functionality
- **Mitigation**: Comprehensive testing and gradual rollout

**Potential Issues**:
- Engine-specific error logic complexity
- Error context preservation challenges

**Success Criteria**:
- [x] All engine modules updated with context-based error handling
- [x] Engine functionality preserved
- [x] Error context maintained across engines
- [x] Consistent error handling patterns applied

**References**:
- [Engine Documentation](../../workflow/)
- [Error Handling Patterns](../pipeline_architecture/core_utility_engine_workplan/proposed_error_handling_improvements.md)

---

### Phase 4: Validation and Testing ✅ PLANNED

**Timeline**: 2026-04-29  
**Milestones**: Comprehensive error handling validation and documentation

**Tasks**:
1. Create comprehensive error handling test suite for context error recording (system-status events) and data-handling summary propagation.
2. Validate that system-status errors and data-handling errors are **separated in context** and correctly reflected in final reports/UI payloads.
3. Test fail-fast behavior configuration (blueprint/config) across representative scenarios (missing file, invalid schema, processor critical data error).
4. Verify backward compatibility:
   - Existing stderr error blocks still appear (user-visible)
   - Existing `context.state.error_summary` consumers (reporting/ai_ops) still function
5. Create error handling documentation describing the two domains (system vs data) and how to consume them from `PipelineContext`.
6. Generate final compliance report mapping back to **WP-PIPE-ARCH-001** (R06/R07/R09) evidence.

**Detailed Evaluation**:
- **Testing Requirements**: 50+ test cases covering all error scenarios
- **Validation Scope**: Error aggregation, fail-fast, reporting, compatibility
- **Performance Testing**: Validate <5% overhead impact
- **Documentation Needs**: Comprehensive usage guides and examples

**Changes and Updates**:
- **Test Suite Creation**: Comprehensive validation of all error handling scenarios
- **Performance Validation**: Ensure minimal overhead impact
- **Compatibility Testing**: Verify existing behavior preservation
- **Documentation Creation**: Usage guides and best practices

**Related Schemas**:
- **TestSuite Schema**: Comprehensive test case definitions
- **ValidationSchema**: Error handling validation criteria
- **DocumentationSchema**: Structure for error handling documentation

**What will be Updated/Created**:
- `test/test_error_handling.py` - Comprehensive test suite
- `reports/phase_4_validation_testing.md` - Validation report
- `docs/error_handling_guide.md` - Usage documentation
- `reports/final_compliance_report.md` - Final compliance report

**Risks and Mitigation**:
- **Risk**: Incomplete test coverage
- **Mitigation**: Comprehensive test planning and peer review

**Potential Issues**:
- Complex error scenario testing
- Performance validation challenges

**Success Criteria**:
- [x] 95%+ test coverage for error handling
- [x] All error scenarios validated
- [x] Performance impact <5%
- [x] Backward compatibility confirmed
- [x] Complete documentation created

**References**:
- [Testing Framework Documentation](../../test/)
- [Quality Assurance Standards](../../../agent_rule.md)

---

## 9. References

### 9.1 Related Documents
- **Agent Rules**: [../../../agent_rule.md](../../../agent_rule.md) - Project standards and guidelines
- **Issue Log**: [../../log/issue_log.md](../../log/issue_log.md) - Issue ISS-002
- **Update Log**: [../../log/update_log.md](../../log/update_log.md) - Progress tracking
- **Pipeline Architecture Design Workplan (WP-PIPE-ARCH-001)**: [../pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md](../pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md) - Requirements R06/R07/R09 alignment
- **Core Utility Workplan**: [../pipeline_architecture/core_utility_engine_workplan/core_utility_engine_workplan.md](../pipeline_architecture/core_utility_engine_workplan/core_utility_engine_workplan.md)

### 9.2 Technical References
- **PipelineContext**: [../../workflow/core_engine/context.py](../../workflow/core_engine/context.py)
- **Main Pipeline**: [../../workflow/dcc_engine_pipeline.py](../../workflow/dcc_engine_pipeline.py)
- **Error Handling Proposal**: [../pipeline_architecture/core_utility_engine_workplan/proposed_error_handling_improvements.md](../pipeline_architecture/core_utility_engine_workplan/proposed_error_handling_improvements.md)

### 9.3 Engine References
- **AI Ops Engine**: [../../workflow/ai_ops_engine/](../../workflow/ai_ops_engine/)
- **Mapper Engine**: [../../workflow/mapper_engine/](../../workflow/mapper_engine/)
- **Initiation Engine**: [../../workflow/initiation_engine/](../../workflow/initiation_engine/)
- **Processor Engine**: [../../workflow/processor_engine/](../../workflow/processor_engine/)
- **Schema Engine**: [../../workflow/schema_engine/](../../workflow/schema_engine/)

---

## Appendix A: Error Handling Pattern Examples

### Current Problematic Pattern
```python
# PROBLEMATIC: Direct error printing and immediate raising
if not setup_results.get("ready"):
    system_error_print("S-C-S-0305", detail=format_setup_report(setup_results))
    raise ValueError(format_setup_report(setup_results))
```

### Proposed Context-Based Pattern
```python
# PROPER: Record in context + keep user-visible output
if not handle_system_error(
    context=context,
    condition=setup_results.get("ready"),
    code="S-C-S-0305",
    message="Project setup validation failed",
    details=format_setup_report(setup_results),
    engine="initiation_engine",
    phase="step1_initiation",
    print_to_stderr=True,
):
    # Continue or fail based on context policy (fail-fast) and severity
    if context.should_fail_fast(domain="system"):
        raise ValueError("Setup not ready")
```

---

## Appendix B: Success Metrics

### Quantitative Metrics
- **Error Coverage**: 100% of error handling uses PipelineContext
- **Performance Impact**: <5% overhead on pipeline execution
- **Test Coverage**: >95% for error handling scenarios
- **Backward Compatibility**: 100% preservation of existing behavior

### Qualitative Metrics
- **Error Reporting**: Comprehensive error summaries with statistics
- **Debugging Experience**: Enhanced error context and tracking
- **Configuration Flexibility**: Configurable fail-fast behavior
- **Code Maintainability**: Standardized error handling patterns

---

**Document Status**: Draft (Awaiting Approval)  
**Next Review**: TBD  
**Maintainer**: Core Engineering Team
