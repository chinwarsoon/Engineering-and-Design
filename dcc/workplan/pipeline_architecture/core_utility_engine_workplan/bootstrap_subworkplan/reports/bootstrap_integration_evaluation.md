# Bootstrap Integration Evaluation Report

**Date:** 2026-04-30  
**Workplan:** DCC-WP-UTIL-BOOTSTRAP-001  
**Status:** EVALUATION COMPLETE - Awaiting Approval  

---

## Executive Summary

This report evaluates which subfunctions in `dcc_engine_pipeline.py` can be integrated into the `BootstrapManager` class. The goal is to further simplify the main pipeline file by moving initialization-related helper functions into the bootstrap module where they logically belong.

---

## Current State Analysis

### Functions in `dcc_engine_pipeline.py`

| Function | Line Range | Purpose | Current Location |
|----------|-----------|---------|------------------|
| `_build_preload_context_data` | 114-144 | Build preload trace from raw values | `dcc_engine_pipeline.py` |
| `_validate_pre_context_gate` | 147-158 | Fail-fast validation before context creation | `dcc_engine_pipeline.py` |
| `_build_postload_context_data` | 161-175 | Build postload trace after context construction | `dcc_engine_pipeline.py` |
| `run_engine_pipeline` | 178-535 | Main 4-engine pipeline execution | `dcc_engine_pipeline.py` |
| `run_engine_pipeline_with_ui` | 538-605 | UI-friendly pipeline entry point | `dcc_engine_pipeline.py` |
| `main` | 608-714 | CLI entry point (now uses BootstrapManager) | `dcc_engine_pipeline.py` |

### BootstrapManager Current Capabilities

| Phase | Method | Status | Purpose |
|-------|--------|--------|---------|
| 1 | `_bootstrap_cli` | ✅ Implemented | CLI parsing, logging setup |
| 2 | `_bootstrap_paths` | ✅ Implemented | Base path, home directory validation |
| 3 | `_bootstrap_registry` | ✅ Implemented | ParameterTypeRegistry loading |
| 4 | `_bootstrap_defaults` | ✅ Implemented | Native defaults building |
| 5 | `_bootstrap_fallback_validation` | ✅ Implemented | Native fallback validation |
| 6 | `_bootstrap_environment` | ✅ Implemented | Environment testing |
| 7 | `_bootstrap_schema` | ✅ Implemented | Schema path resolution |
| 8 | `_bootstrap_parameters` | ✅ Implemented | Effective parameters resolution |
| 8b | `_bootstrap_pre_pipeline_validation` | ✅ Implemented | Pre-pipeline path validation |
| - | `to_pipeline_context` | ✅ Implemented | Convert state to PipelineContext |

---

## Integration Evaluation

### Category 1: HIGH PRIORITY - Should Integrate

These functions are pure initialization helpers that logically belong in BootstrapManager.

#### 1. `_build_preload_context_data` ✅ RECOMMENDED
```python
def _build_preload_context_data(
    *,
    base_path: Path,
    schema_path: Path,
    input_file_path: Path,
    export_paths: Dict[str, Path],
    effective_parameters: Dict[str, Any],
) -> Dict[str, ContextTraceItem]
```

**Analysis:**
- Builds trace data BEFORE context creation
- Uses values already available in BootstrapManager state
- No external dependencies beyond what's already in bootstrap.py
- Pure data transformation function

**Integration Plan:**
- Move to BootstrapManager as `_build_preload_trace()`
- Call at end of `_bootstrap_pre_pipeline_validation()`
- Store result in `self._preload_trace` attribute
- Expose via property `preload_trace`

**Benefits:**
- Keeps all initialization logic in one place
- Enables testing of preload trace building
- Makes `to_pipeline_context()` cleaner

---

#### 2. `_validate_pre_context_gate` ✅ RECOMMENDED
```python
def _validate_pre_context_gate(
    preload_data: Dict[str, ContextTraceItem],
    validation_result: Any,
) -> None
```

**Analysis:**
- Fail-fast validation gate
- Validates preload trace before context construction
- Currently called in main() before building PipelineContext
- BootstrapManager already has all validation results

**Integration Plan:**
- Move to BootstrapManager as `_validate_pre_context_gate()`
- Call at end of `_bootstrap_pre_pipeline_validation()`
- Raise BootstrapError instead of ValueError
- Add error code: B-GATE-001

**Benefits:**
- Centralized validation gate
- Consistent error handling with BootstrapError
- Removes validation logic from main()

---

#### 3. `_build_postload_context_data` ✅ RECOMMENDED
```python
def _build_postload_context_data(
    *,
    pipeline_paths: PipelinePaths,
    effective_parameters: Dict[str, Any],
) -> Dict[str, ContextTraceItem]
```

**Analysis:**
- Builds trace data AFTER context creation
- Uses values from PipelinePaths (which BootstrapManager creates)
- Currently called in main() after building PipelineContext
- Mirrors `_build_preload_context_data`

**Integration Plan:**
- Move to BootstrapManager as `_build_postload_trace()`
- Call at end of `to_pipeline_context()`
- Store result in `self._postload_trace` attribute
- Expose via property `postload_trace`

**Benefits:**
- Keeps all trace building in one place
- Enables testing of postload trace building
- Makes `to_pipeline_context()` a complete factory method

---

### Category 2: MEDIUM PRIORITY - Consider Integration

These functions have mixed concerns but could benefit from BootstrapManager integration.

#### 4. `run_engine_pipeline_with_ui` ⚠️ PARTIALLY INTEGRATED
```python
def run_engine_pipeline_with_ui(
    base_path: Path,
    upload_file_name: str,
    output_folder: str = "output",
    schema_file_name: Optional[str] = None,
    debug_mode: bool = False,
    nrows: Optional[int] = None,
) -> Dict[str, Any]
```

**Analysis:**
- Already refactored to use `BootstrapManager.bootstrap_for_ui()`
- Contains pipeline execution logic that shouldn't move to BootstrapManager
- Current implementation is clean (~30 lines)
- **RECOMMENDATION:** Keep as-is - good separation of concerns

---

### Category 3: LOW PRIORITY - Do Not Integrate

These functions are core pipeline execution logic, not initialization.

#### 5. `run_engine_pipeline` ❌ DO NOT INTEGRATE
```python
def run_engine_pipeline(context: PipelineContext) -> Dict[str, Any]
```

**Analysis:**
- Contains the 4-engine pipeline execution logic
- Not initialization - this IS the pipeline
- Would violate single responsibility principle
- BootstrapManager handles setup, not execution
- **RECOMMENDATION:** Keep in dcc_engine_pipeline.py

---

## Proposed Integration Plan

### Phase A: Move Context Trace Functions (Priority: HIGH)

**Files to Modify:**
1. `utility_engine/bootstrap.py` - Add 3 new methods
2. `dcc_engine_pipeline.py` - Remove 3 helper functions, update main()

**Implementation Steps:**

```python
# In BootstrapManager class (bootstrap.py)

# 1. Add new attributes in __init__
self._preload_trace: Optional[Dict[str, ContextTraceItem]] = None
self._postload_trace: Optional[Dict[str, ContextTraceItem]] = None

# 2. Add property accessors
@property
def preload_trace(self) -> Optional[Dict[str, ContextTraceItem]]:
    """Get preload trace data (available after bootstrap)."""
    return self._preload_trace

@property
def postload_trace(self) -> Optional[Dict[str, ContextTraceItem]]:
    """Get postload trace data (available after to_pipeline_context)."""
    return self._postload_trace

# 3. Add _build_preload_trace() method
# 4. Add _validate_pre_context_gate() method  
# 5. Add _build_postload_trace() method
# 6. Update _bootstrap_pre_pipeline_validation() to call trace building
# 7. Update to_pipeline_context() to call postload trace building
```

**Estimated Lines Changed:**
- bootstrap.py: +80 lines (new methods)
- dcc_engine_pipeline.py: -60 lines (removed helpers), main() simplified by ~20 lines

---

### Phase B: Simplify main() Further (Priority: MEDIUM)

After Phase A, `main()` would be further simplified:

```python
def main() -> int:
    args, cli_args, cli_overrides_provided = parse_cli_args()
    
    try:
        manager = BootstrapManager(Path(args.base_path)).bootstrap_all(cli_args)
        context = manager.to_pipeline_context()
        context.nrows = args.nrows
        context.debug_mode = (DEBUG_LEVEL >= 2)
        
        # Preload/postload traces now available from manager
        context.set_preload_state(manager.preload_trace)
        context.set_postload_state(manager.postload_trace)
        
        print_framework_banner(...)
        results = run_engine_pipeline(context)
        
    except BootstrapError as e:
        ...
    return 0
```

**Benefits:**
- No manual trace building in main()
- No manual validation gate in main()
- All initialization encapsulated in BootstrapManager

---

## Integration Benefits Summary

| Function | Integration Benefit | Lines Saved in dcc_engine_pipeline.py |
|----------|---------------------|--------------------------------------|
| `_build_preload_context_data` | Centralized trace building | ~30 lines |
| `_validate_pre_context_gate` | Centralized validation gate | ~12 lines |
| `_build_postload_context_data` | Centralized trace building | ~15 lines |
| **TOTAL** | | **~57 lines** |

**Final main() size estimate:** ~60 lines → ~45 lines (additional 25% reduction)

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing tests | Medium | Maintain backward compatibility, add deprecation warnings |
| Context trace format changes | Low | Keep exact same return format |
| Error code changes | Low | Map ValueError to BootstrapError with same messages |
| Dependencies on external modules | Low | All dependencies already in bootstrap.py |

---

## Decision Matrix

| Function | Integrate? | Priority | Effort | Impact |
|----------|-----------|----------|--------|--------|
| `_build_preload_context_data` | ✅ YES | HIGH | Low | High |
| `_validate_pre_context_gate` | ✅ YES | HIGH | Low | High |
| `_build_postload_context_data` | ✅ YES | HIGH | Low | High |
| `run_engine_pipeline_with_ui` | ❌ NO | - | - | - |
| `run_engine_pipeline` | ❌ NO | - | - | - |

---

## Recommendation

**APPROVE Phase A integration** of the three context trace functions:
1. `_build_preload_context_data` → `_build_preload_trace()`
2. `_validate_pre_context_gate` → `_validate_pre_context_gate()`
3. `_build_postload_context_data` → `_build_postload_trace()`

This will:
- Further simplify `main()` by ~15 lines
- Centralize all initialization logic in BootstrapManager
- Enable independent testing of trace building
- Maintain clean separation between initialization and execution

---

## Awaiting Approval

**Next Steps (Pending Approval):**
1. Implement Phase A integration
2. Run full pipeline test
3. Update documentation
4. Create completion report

**Approver:** User confirmation required before proceeding.
