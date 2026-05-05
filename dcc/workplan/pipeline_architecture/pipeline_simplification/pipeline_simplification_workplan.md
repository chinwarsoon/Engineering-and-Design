# Pipeline Simplification Workplan

**Document ID**: WP-PIPE-SIMP-001  
**Current Version**: 0.2  
**Status**: 🟡 PENDING APPROVAL  
**Last Updated**: 2026-05-05  

---

## 1. Title and Description

This workplan defines a structured simplification of the DCC engine pipeline (`dcc_engine_pipeline.py`) and its supporting modules. The study identified concrete opportunities to reduce code volume, eliminate dead code, enforce the Single Source of Truth (SSOT) principle, and make the orchestrator a clean, readable sequence of engine calls — without changing any business logic or breaking any existing behavior.

The simplification is organized into three phases of increasing scope:
- **Phase A** — Quick wins: dead code removal, unused imports, shadow copies
- **Phase B** — Structural cleanup: Blueprint delegation, boilerplate absorption, error consistency
- **Phase C** — Architecture refinement: uniform engine interface, step registry, deprecated method removal

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 0.1 | 2026-05-05 | System | Initial workplan created from pipeline simplification study |
| 0.2 | 2026-05-05 | System | Added two new requirements: (1) full legacy/backward-compat code removal across all engines; (2) decouple error handling and messaging from `dcc_engine_pipeline.py` into dedicated handler. Scope expanded with items S17–S26. Phase A extended; Phase D added for legacy removal. |

---

## 3. Object

Simplify the DCC engine pipeline codebase by:
1. Removing dead code, legacy toggles, and unused imports that add noise without value
2. Enforcing SSOT — eliminating shadow copies of data already in `PipelineContext`
3. Delegating Blueprint population to the schema engine where it belongs
4. Absorbing repetitive boilerplate (timing, status, error handling) into existing helpers
5. Establishing a uniform engine interface to enable a clean step-registry orchestration pattern
6. **Removing all legacy/backward-compatibility code** — the pipeline has moved past its previous design; compatibility shims for the old `enhanced_schema` structure, `_data` suffix keys, `global_parameters.json`, and deprecated CLI args are no longer needed
7. **Decoupling error handling and messaging from the orchestrator** — `dcc_engine_pipeline.py` currently mixes pipeline coordination with error formatting, error printing, and result display; these responsibilities belong in a dedicated handler module

The goal is a pipeline orchestrator that reads as a clear, linear sequence of engine calls — easy to extend, easy to debug, and fully consistent in error handling.

---

## 4. Scope Summary

| ID | Category | Requirement | Details | Status | Phase |
|:---|:---|:---|:---|:---:|:---:|
| S01 | Dead Code | Remove `_USE_DI_MODE` toggle | Always `True`; `else` branches are unreachable dead code | 🔵 PLANNED | A |
| S02 | Dead Code | Remove unused imports | 12+ symbols imported but never used in orchestrator | 🔵 PLANNED | A |
| S03 | SSOT | Remove `export_paths` shadow dict | `context.paths` already has all output paths | 🔵 PLANNED | A |
| S04 | SSOT | Remove `effective_parameters` pass-through | Already in `context.parameters`; engines should read from context | 🔵 PLANNED | A |
| S05 | Bug Fix | Fix `add_data_error()` appending to wrong list | Data errors appended to `system_status_errors` instead of separate list | 🔵 PLANNED | A |
| S06 | SSOT | Centralize `_schema_root` resolution | Same `if "columns" in schema_data else ...` guard duplicated in 3+ places | 🔵 PLANNED | B |
| S07 | Modularization | Move Blueprint population to `SchemaValidator` | Orchestrator step 2 manually builds Blueprint; belongs in schema engine | 🔵 PLANNED | B |
| S08 | Modularization | Use `wrap_engine_execution()` for all steps | Exists in `error_manager.py` but unused; absorbs timing + status boilerplate | 🔵 PLANNED | B |
| S09 | Error Handling | Add error handling to steps 5 and 6 | Reorder and export steps have no try/except; inconsistent with steps 1–4 | 🔵 PLANNED | B |
| S10 | Class Hierarchy | Consolidate duplicate `BaseProcessor` classes | Two `BaseProcessor` classes with same name in different modules | 🔵 PLANNED | B |
| S11 | Engine Interface | Add `run()` abstract method to `BaseEngine` | Engines have different entry point names; no uniform interface | 🔵 PLANNED | C |
| S12 | Modularization | Replace 7 manual step blocks with step registry | Orchestrator becomes a loop over `[(engine, name, phase)]` tuples | 🔵 PLANNED | C |
| S13 | Dead Code | Remove deprecated engine methods | `apply_null_handling()`, `apply_calculations()` marked deprecated but still present | 🔵 PLANNED | C |
| S14 | Dead Code | Remove legacy factory methods | `create_legacy()`, `create_calculation_engine_legacy()` only serve dead else branch | 🔵 PLANNED | C |
| S15 | Dead Code | Remove deprecated `--debug-mode` CLI arg | Marked DEPRECATED in parser; `--verbose debug` is the replacement | 🔵 PLANNED | C |
| S16 | Status Tracking | Align pipeline phase tracking with `BootstrapPhaseStatus` | Bootstrap has rich phase tracking; pipeline only stores flat string per engine | 🔵 PLANNED | C |
| S17 | Legacy Removal | Remove `enhanced_schema` fallback in schema root resolution | `enhanced_schema` was the old schema key; current schema uses top-level `columns` | 🔵 PLANNED | D |
| S18 | Legacy Removal | Remove `_data` suffix fallback in `BaseProcessor._resolve_schema_reference()` | Old schema used `approval_code_schema_data`; new schema uses top-level `approval_codes` | 🔵 PLANNED | D |
| S19 | Legacy Removal | Remove `_new_key_map` hardcoded lookup in `BaseProcessor` | Replace with schema-driven reference resolution; map belongs in schema, not code | 🔵 PLANNED | D |
| S20 | Legacy Removal | Remove `global_parameters.json` fallback in `BootstrapManager` | Replaced by `dcc_register_setup.json`; fallback path is dead for current deployments | 🔵 PLANNED | D |
| S21 | Legacy Removal | Remove `system_registry` / `dcc_registry` aliases in `BootstrapManager` | Both point to same unified `registry`; aliases add confusion with no value | 🔵 PLANNED | D |
| S22 | Legacy Removal | Remove `safe_resolve_legacy()` function | Explicit legacy wrapper; `safe_resolve()` is the current API | 🔵 PLANNED | D |
| S23 | Legacy Removal | Remove backward-compat section in `initiation_engine/utils/logging.py` | `debug_print()` and `set_debug_mode()` legacy wrappers; callers should use tiered logging directly | 🔵 PLANNED | D |
| S24 | Legacy Removal | Remove `_use_registry_validation()` feature toggle in `cli_parser.py` | Gradual migration toggle; registry validation is now the only path | 🔵 PLANNED | D |
| S25 | Decoupling | Extract error handling and messaging from `dcc_engine_pipeline.py` into `pipeline_result_handler.py` | `main()` contains ~60 lines of error formatting, error printing, and result display mixed with pipeline coordination | 🔵 PLANNED | B |
| S26 | Decoupling | Extract in-pipeline error display (step 6 validation summary) into result handler | Inline `status_print` error summary in step 6 belongs in reporting layer, not orchestrator | 🔵 PLANNED | B |

**Status Legend:** 🔵 PLANNED | 🟡 IN PROGRESS | ✅ COMPLETE | ❌ DEFERRED

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Object](#3-object)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Evaluation and Alignment](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies](#7-dependencies-with-other-tasks)
- [8. Implementation Phases](#8-implementation-phases-and-task-breakdown)
  - [Phase A — Quick Wins](#phase-a--quick-wins-low-risk-high-clarity)
  - [Phase B — Structural Cleanup](#phase-b--structural-cleanup-medium-effort-high-value)
  - [Phase C — Architecture Refinement](#phase-c--architecture-refinement-higher-effort-long-term-value)
  - [Phase D — Legacy Removal](#phase-d--legacy-removal-medium-effort-clean-break)
- [9. References](#9-references)

---

## 6. Evaluation and Alignment with Existing Architecture

### Alignment with agent_rule.md

| Rule | Requirement | Alignment |
|:---|:---|:---:|
| Section 4.1 | Module design for functions and classes | ✅ Phase C adds `run()` to `BaseEngine` |
| Section 4.2 | `__init__.py` only imports and version info | ✅ No changes to `__init__.py` files |
| Section 5.1 | Standardized docstrings and breadcrumb comments | ✅ All new/modified functions will include these |
| Section 6.7 | Fail-fast metadata in functions | ✅ Phase B ensures all steps have consistent error handling |
| Section 2 | Schema-driven logic | ✅ Phase B moves Blueprint population into schema engine |

### Alignment with Existing Architecture

| Component | Current State | Post-Simplification |
|:---|:---|:---|
| `PipelineContext` | SSOT declared but bypassed with shadow copies | Fully respected — no shadow copies |
| `BaseEngine` | Exists but has no lifecycle contract | Gets `run()` abstract method in Phase C |
| `wrap_engine_execution()` | Implemented but never called | Used for all 7 pipeline steps in Phase B |
| `BootstrapManager` | Rich phase tracking | Pipeline aligned in Phase C |
| `_USE_DI_MODE` | Always `True`, dead else branches | Removed in Phase A |
| Blueprint population | Done inline in orchestrator step 2 | Delegated to `SchemaValidator` in Phase B |
| Error handling in `main()` | ~60 lines of formatting/printing mixed with coordination | Extracted to `pipeline_result_handler.py` in Phase B |
| `enhanced_schema` fallback | Present in 6+ files across 3 engines | Removed in Phase D — current schema uses top-level `columns` |
| `_data` suffix fallback | In `BaseProcessor`, `mapper_engine`, `processor_engine` | Removed in Phase D — current schema uses top-level keys |
| `global_parameters.json` fallback | In `BootstrapManager` Phase 3 | Removed in Phase D — replaced by `dcc_register_setup.json` |
| Legacy logging wrappers | `debug_print()`, `set_debug_mode()` in `initiation_engine` | Removed in Phase D — callers use tiered logging directly |

### Impact Assessment

| Dimension | Lines Affected | Risk |
|:---|:---:|:---:|
| Phase A | ~50 lines removed | 🟢 None — dead code only |
| Phase B | ~120 lines refactored + new `pipeline_result_handler.py` | 🟡 Low — behavior-preserving refactor |
| Phase C | ~150 lines restructured | 🟡 Medium — interface change, requires engine updates |
| Phase D | ~80 lines removed across 8+ files | 🟡 Low-Medium — requires schema format verification first |

**Estimated orchestrator size reduction:**
- Current: ~683 lines
- After Phase A: ~630 lines
- After Phase B: ~400 lines (error handling extracted to handler module)
- After Phase C: ~180 lines
- After Phase D: net ~80 lines removed across supporting modules

---

## 7. Dependencies with Other Tasks

1. **WP-PIPE-ARCH-001** — [pipeline_architecture_design_workplan.md](pipeline_architecture_workplan/pipeline_architecture_design_workplan.md) — Prior architecture work; this workplan builds on its completed phases
2. **WP-CORE-UTIL-001** — [core_utility_engine_workplan/](core_utility_engine_workplan/) — `wrap_engine_execution()` lives in `core_engine/errors/error_manager.py`; Phase B depends on it
3. **Error Handling Workplan** — `dcc/workplan/error_handling/` — S05 (bug fix in `add_data_error()`) touches `context_pipeline.py` which is shared with error handling work
4. **Schema Processing Workplan** — `dcc/workplan/schema_processing/` — S07 (Blueprint delegation) touches `schema_engine/validator/schema_validator.py`
5. **agent_rule.md** — Section 8 (Workplan), Section 4 (Module Design), Section 6 (Debug/Logging)

---

## 8. Implementation Phases and Task Breakdown

---

### Phase A — Quick Wins (Low Risk, High Clarity)

**Timeline:** TBD (estimated 1 session)  
**Milestone:** Orchestrator cleaned of dead code and shadow copies  
**Risk Level:** 🟢 None — all changes are removals of unreachable or redundant code

#### Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| A1 | Remove `_USE_DI_MODE` toggle and dead `else` branches | `dcc_engine_pipeline.py` | Delete toggle + 2 `else` blocks (~15 lines) |
| A2 | Remove unused imports (12+ symbols) | `dcc_engine_pipeline.py` | Remove: `argparse`, `builtins`, `importlib`, `os`, `platform`, `Tuple`, `PathSelectionContract`, `ParameterOverrideContract`, `UIContractBundle`, `get_available_files`, `suggest_base_paths`, `validate_and_resolve`, `UIContractManager`, `UIRequest`, `UIResponse`, `build_native_defaults`, `resolve_effective_parameters`, `get_registry_for_cli`, `load_schema_parameters`, `default_schema_path`, `CalculationEngineFactory` |
| A3 | Remove `export_paths` shadow dict | `dcc_engine_pipeline.py` | Replace all `export_paths["x"]` references with `context.paths.x` |
| A4 | Remove explicit `effective_parameters` pass-through | `dcc_engine_pipeline.py` | Remove local variable; engines read from `context.parameters` |
| A5 | Fix `add_data_error()` bug | `core_engine/context/context_pipeline.py` | Append to separate `data_handling_errors` list, not `system_status_errors` |

#### Files Updated/Created

| File | Action | Purpose |
|:---|:---|:---|
| `dcc/workflow/dcc_engine_pipeline.py` | Update | Remove dead code, unused imports, shadow copies |
| `dcc/workflow/core_engine/context/context_pipeline.py` | Update | Fix `add_data_error()` list target |
| `dcc/workplan/pipeline_architecture/pipeline_simplification/reports/phase_A_quickwins_report.md` | Create | Phase A test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Removing an import that is actually used indirectly | Low | Medium | Verify each import with `grepSearch` before removal |
| `export_paths` dict used in a path not yet found | Low | Low | Search all usages before replacing |
| `add_data_error()` fix breaks existing callers | Low | Low | `get_data_handling_errors()` already filters by domain; fix is additive |

#### Potential Future Issues
- Some removed imports may be needed if new features are added — document what was removed and why
- `effective_parameters` pass-through removal requires engines to consistently use `context.parameters`

#### Success Criteria
- [ ] `_USE_DI_MODE` and all `else` branches removed
- [ ] Zero unused imports in `dcc_engine_pipeline.py`
- [ ] `export_paths` dict eliminated; `context.paths` used directly
- [ ] `effective_parameters` local variable removed from orchestrator
- [ ] `add_data_error()` appends to correct list
- [ ] Pipeline runs without regression

#### Deliverables
- Updated `dcc_engine_pipeline.py`
- Updated `context_pipeline.py`
- `reports/phase_A_quickwins_report.md`

---

### Phase B — Structural Cleanup (Medium Effort, High Value)

**Timeline:** TBD (estimated 2 sessions)  
**Milestone:** Orchestrator steps use shared helpers; Blueprint owned by schema engine  
**Risk Level:** 🟡 Low — behavior-preserving refactors with clear before/after

#### Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| B1 | Centralize `_schema_root` resolution | New utility in `schema_engine` or `core_engine` | Create `resolve_schema_root(schema_data)` function; replace 3+ inline duplicates |
| B2 | Move Blueprint population to `SchemaValidator.build_blueprint(context)` | `schema_engine/validator/schema_validator.py`, `dcc_engine_pipeline.py` | Add `build_blueprint()` method; orchestrator calls it after `validate()` |
| B3 | Use `wrap_engine_execution()` for all 7 steps | `dcc_engine_pipeline.py` | Replace manual `engine_status + try/except + telemetry` blocks with `wrap_engine_execution()` |
| B4 | Add error handling to steps 5 and 6 | `dcc_engine_pipeline.py` | Wrap reorder and export steps in consistent try/except |
| B5 | Consolidate duplicate `BaseProcessor` classes | `processor_engine/core/base.py` → `core_engine/base/base_processor.py` | Remove `processor_engine/core/base.py`; update `SchemaProcessor` to inherit from `core_engine.base.BaseProcessor` |
| B6 | Create `pipeline_result_handler.py` — decouple error handling and messaging | New `core_engine/pipeline_result_handler.py` | Extract all error formatting, error printing, and result display from `main()` and step 6 into dedicated handler |
| B7 | Decouple step 6 validation summary display | `dcc_engine_pipeline.py` → `pipeline_result_handler.py` | Move inline `status_print` error summary block (total_errors, health_kpi, affected rows) out of orchestrator |

#### Files Updated/Created

| File | Action | Purpose |
|:---|:---|:---|
| `dcc/workflow/dcc_engine_pipeline.py` | Update | Use `wrap_engine_execution()`, remove inline Blueprint code, remove error display logic |
| `dcc/workflow/schema_engine/validator/schema_validator.py` | Update | Add `build_blueprint(context)` method |
| `dcc/workflow/core_engine/errors/error_manager.py` | Update | Extend `wrap_engine_execution()` to absorb timing and status tracking |
| `dcc/workflow/core_engine/pipeline_result_handler.py` | Create | Dedicated handler for error formatting, error printing, and result display (decoupled from orchestrator) |
| `dcc/workflow/processor_engine/core/base.py` | Archive | Consolidate into `core_engine/base/base_processor.py` |
| `dcc/workflow/processor_engine/schema/processor.py` | Update | Inherit from `core_engine.base.BaseProcessor` |
| `dcc/workplan/pipeline_architecture/pipeline_simplification/reports/phase_B_structural_report.md` | Create | Phase B test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| `wrap_engine_execution()` signature doesn't fit all step patterns | Medium | Medium | Extend signature with optional pre/post hooks before applying |
| `build_blueprint()` in schema engine creates circular import | Low | Medium | Use `TYPE_CHECKING` guard or pass context as dict |
| `BaseProcessor` consolidation breaks `SchemaProcessor` | Low | Medium | Run existing tests after change; `SchemaProcessor` only uses `schema_data` from base |
| `pipeline_result_handler.py` needs access to context and results | Low | Low | Handler receives `context`, `results`, and `args` as parameters — no coupling to orchestrator internals |

#### Potential Future Issues
- `wrap_engine_execution()` may need async support if pipeline is ever parallelized
- `build_blueprint()` may need versioning if schema structure changes
- `pipeline_result_handler.py` may grow to include JSON serialization helpers — keep it focused on display/formatting only

#### Success Criteria
- [ ] `resolve_schema_root()` utility created and used in all 3+ locations
- [ ] Blueprint population removed from orchestrator; `schema_validator.build_blueprint(context)` called instead
- [ ] All 7 pipeline steps use `wrap_engine_execution()` or equivalent context manager
- [ ] Steps 5 and 6 have consistent error handling
- [ ] Single `BaseProcessor` class in `core_engine`
- [ ] `pipeline_result_handler.py` created with all error formatting and result display logic
- [ ] `main()` in orchestrator reduced to: bootstrap → run pipeline → call handler → return exit code
- [ ] Step 6 validation summary display moved to result handler
- [ ] Pipeline runs without regression

#### Deliverables
- Updated `dcc_engine_pipeline.py`
- Updated `schema_engine/validator/schema_validator.py`
- Updated `core_engine/errors/error_manager.py`
- New `core_engine/pipeline_result_handler.py`
- Archived `processor_engine/core/base.py`
- `reports/phase_B_structural_report.md`

---

### Phase C — Architecture Refinement (Higher Effort, Long-Term Value)

**Timeline:** TBD (estimated 2–3 sessions)  
**Milestone:** Uniform engine interface; orchestrator is a clean step registry loop  
**Risk Level:** 🟡 Medium — interface change touches all engine classes

#### Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| C1 | Add `run()` abstract method to `BaseEngine` | `core_engine/base/base_engine.py` | Add `@abstractmethod run(self) -> Dict[str, Any]` |
| C2 | Implement `run()` in each engine | All 5 engine core files | Wrap existing entry point (`validate()`, `map_dataframe()`, `process_data()`) in `run()` |
| C3 | Replace 7 manual step blocks with step registry | `dcc_engine_pipeline.py` | Define `PIPELINE_STEPS = [(EngineClass, name, phase), ...]`; loop with `wrap_engine_execution()` |
| C4 | Remove deprecated `apply_null_handling()` and `apply_calculations()` | `processor_engine/core/engine.py` | Archive methods; remove from class |
| C5 | Remove `create_legacy()` and `create_calculation_engine_legacy()` | `processor_engine/core/proc_factories.py` | Remove legacy factory methods |
| C6 | Remove deprecated `--debug-mode` CLI arg | `initiation_engine/utils/cli.py`, `utility_engine/cli/cli_parser.py` | Remove arg definition and any handling code |
| C7 | Align pipeline phase tracking with `BootstrapPhaseStatus` | `core_engine/context/context_pipeline.py` | Add `PipelinePhaseStatus` dataclass; replace flat `engine_status` string dict |

#### Files Updated/Created

| File | Action | Purpose |
|:---|:---|:---|
| `dcc/workflow/core_engine/base/base_engine.py` | Update | Add `run()` abstract method |
| `dcc/workflow/initiation_engine/core/validator.py` | Update | Implement `run()` wrapping `validate()` |
| `dcc/workflow/schema_engine/validator/schema_validator.py` | Update | Implement `run()` wrapping `validate()` |
| `dcc/workflow/mapper_engine/core/engine.py` | Update | Implement `run()` wrapping `map_dataframe()` |
| `dcc/workflow/processor_engine/core/engine.py` | Update | Implement `run()` wrapping `process_data()`; remove deprecated methods |
| `dcc/workflow/processor_engine/core/proc_factories.py` | Update | Remove legacy factory methods |
| `dcc/workflow/initiation_engine/utils/cli.py` | Update | Remove `--debug-mode` arg |
| `dcc/workflow/utility_engine/cli/cli_parser.py` | Update | Remove `--debug-mode` arg |
| `dcc/workflow/core_engine/context/context_pipeline.py` | Update | Add `PipelinePhaseStatus` dataclass |
| `dcc/workflow/dcc_engine_pipeline.py` | Update | Replace 7 step blocks with step registry loop |
| `dcc/workplan/pipeline_architecture/pipeline_simplification/reports/phase_C_architecture_report.md` | Create | Phase C test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| `run()` interface too rigid for engines with different signatures | Medium | Medium | `run()` returns `Dict[str, Any]`; engines store results in context before returning |
| Step registry loses per-step customization | Low | Medium | Registry entries can include optional pre/post hooks |
| Removing `--debug-mode` breaks existing user scripts | Low | Low | Arg already marked DEPRECATED; add deprecation warning before removal |
| Deprecated method removal breaks external callers | Low | Medium | Search all callers before removal; archive methods with `NotImplementedError` first |

#### Potential Future Issues
- Step registry pattern enables future parallel execution (async steps) — design `run()` to be async-compatible
- `PipelinePhaseStatus` alignment with `BootstrapPhaseStatus` may warrant a shared base class in `core_engine`

#### Success Criteria
- [ ] `BaseEngine.run()` abstract method defined
- [ ] All 5 engines implement `run()`
- [ ] Orchestrator uses step registry loop (≤ 80 lines for core execution)
- [ ] Deprecated methods removed from `CalculationEngine`
- [ ] Legacy factory methods removed
- [ ] `--debug-mode` CLI arg removed
- [ ] Pipeline phase tracking uses structured dataclass
- [ ] Pipeline runs without regression
- [ ] All existing tests pass

#### Deliverables
- Updated `base_engine.py`, all 5 engine core files
- Updated `dcc_engine_pipeline.py` (target: ~200 lines)
- Updated `context_pipeline.py`
- `reports/phase_C_architecture_report.md`

---

### Phase D — Legacy Removal (Medium Effort, Clean Break)

**Timeline:** TBD (estimated 2 sessions)  
**Milestone:** All backward-compatibility shims removed; codebase assumes current schema format only  
**Risk Level:** 🟡 Low-Medium — requires confirming no active data files use old schema format before removing fallbacks

#### Background

The pipeline evolved from an older schema design (`enhanced_schema.columns`, `_data` suffix keys, `global_parameters.json`) to the current flat top-level structure. Backward-compatibility code was added during migration and never removed. These shims now:
- Add conditional branches that obscure the real code path
- Imply the old format is still supported (it is not)
- Duplicate logic across `BaseProcessor`, `mapper_engine`, `processor_engine`, and `schema_engine`

**Pre-condition:** Before removing any fallback, verify that no active schema files in `dcc/config/schemas/` use the old format. This is a one-time check, not an ongoing concern.

#### Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| D1 | Remove `enhanced_schema` fallback from `_schema_root` resolution | `mapper_engine/core/engine.py`, `processor_engine/core/engine.py`, `processor_engine/schema/processor.py`, `dcc_engine_pipeline.py`, `schema_engine/validator/schema_validator.py`, `processor_engine/error_handling/detectors/identity.py` | After S06 (centralized `resolve_schema_root()`), remove the `enhanced_schema` branch entirely |
| D2 | Remove `_data` suffix fallback in `BaseProcessor._resolve_schema_reference()` | `core_engine/base/base_processor.py` | Remove `else` branch that reads `schema_name_data`; keep only top-level key lookup |
| D3 | Remove `_new_key_map` hardcoded dict in `BaseProcessor` | `core_engine/base/base_processor.py` | Replace with schema-driven lookup — reference resolution should use schema metadata, not a hardcoded Python dict |
| D4 | Remove `_data` suffix fallback in `mapper_engine/mappers/detection.py` | `mapper_engine/mappers/detection.py` | Remove `Legacy fallback: _data suffix` branch |
| D5 | Remove `global_parameters.json` fallback in `BootstrapManager` | `utility_engine/bootstrap/boot_pipeline.py` | Remove `legacy_path` fallback; raise `BootstrapError` if `dcc_register_setup.json` not found |
| D6 | Remove `system_registry` / `dcc_registry` aliases in `BootstrapManager` | `utility_engine/bootstrap/boot_pipeline.py` | Remove duplicate attributes; callers use `self.registry` directly |
| D7 | Remove `safe_resolve_legacy()` | `utility_engine/paths/path_resolvers.py`, `utility_engine/paths/__init__.py` | Archive function; remove from exports |
| D8 | Remove backward-compat logging wrappers | `initiation_engine/utils/logging.py` | Remove `BACKWARD COMPATIBILITY` section: `debug_print()` legacy wrapper and `set_debug_mode()` legacy wrapper |
| D9 | Remove `_use_registry_validation()` feature toggle | `utility_engine/cli/cli_parser.py`, `utility_engine/cli/__init__.py` | Remove toggle function and `try/except` import guard; registry validation is the only path |
| D10 | Remove `enhanced_schema` references from test files | `processor_engine/error_handling/tests/` | Update test fixtures to use current top-level schema format |

#### Files Updated/Created

| File | Action | Purpose |
|:---|:---|:---|
| `dcc/workflow/core_engine/base/base_processor.py` | Update | Remove `_new_key_map`, `_data` suffix fallback |
| `dcc/workflow/mapper_engine/core/engine.py` | Update | Remove `enhanced_schema` fallback (covered by S06 `resolve_schema_root()`) |
| `dcc/workflow/mapper_engine/mappers/detection.py` | Update | Remove `_data` suffix fallback |
| `dcc/workflow/processor_engine/core/engine.py` | Update | Remove `enhanced_schema` fallback (covered by S06) |
| `dcc/workflow/processor_engine/schema/processor.py` | Update | Remove `enhanced_schema` fallback (covered by S06) |
| `dcc/workflow/processor_engine/error_handling/detectors/identity.py` | Update | Remove `enhanced_schema` fallback |
| `dcc/workflow/schema_engine/validator/schema_validator.py` | Update | Remove `enhanced_schema` fallback |
| `dcc/workflow/utility_engine/bootstrap/boot_pipeline.py` | Update | Remove `global_parameters.json` fallback, `system_registry`/`dcc_registry` aliases |
| `dcc/workflow/utility_engine/paths/path_resolvers.py` | Update | Remove `safe_resolve_legacy()` |
| `dcc/workflow/utility_engine/paths/__init__.py` | Update | Remove `safe_resolve_legacy` from exports |
| `dcc/workflow/utility_engine/cli/cli_parser.py` | Update | Remove `_use_registry_validation()` toggle |
| `dcc/workflow/utility_engine/cli/__init__.py` | Update | Remove legacy function exports |
| `dcc/workflow/initiation_engine/utils/logging.py` | Update | Remove backward-compat section |
| `dcc/workflow/processor_engine/error_handling/tests/` | Update | Update test fixtures to current schema format |
| `dcc/workplan/pipeline_architecture/pipeline_simplification/reports/phase_D_legacy_removal_report.md` | Create | Phase D test and completion report |

#### Pre-Condition Checklist (must complete before D1–D4)

- [ ] Confirm no active schema files in `dcc/config/schemas/` use `enhanced_schema` key
- [ ] Confirm no active schema files use `*_data` suffix pattern (e.g., `approval_code_schema_data`)
- [ ] Confirm `dcc_register_setup.json` exists and is the active parameter schema
- [ ] Confirm `global_parameters.json` is not referenced by any active config or tool

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| An active schema file still uses `enhanced_schema` format | Low | High | Pre-condition checklist must pass before D1; if found, migrate schema file first |
| A test fixture uses old schema format and breaks | Medium | Low | D10 explicitly updates test fixtures; run tests after each file change |
| `safe_resolve_legacy()` called from an undiscovered location | Low | Medium | `grepSearch` all callers before removal |
| Removing `system_registry`/`dcc_registry` breaks external callers | Low | Low | Both are internal to `BootstrapManager`; no external callers found in study |

#### Potential Future Issues
- If a new schema migration is ever needed, the pattern for adding a temporary fallback is now documented here — add it, migrate, then remove it in the same workplan cycle
- `_new_key_map` removal (D3) requires the schema itself to carry reference resolution metadata — verify `dcc_register_enhanced.json` has the necessary `schema_references` section

#### Success Criteria
- [ ] Pre-condition checklist passed
- [ ] Zero `enhanced_schema` references in production code (test fixtures excluded until D10)
- [ ] Zero `_data` suffix fallback branches in production code
- [ ] `global_parameters.json` fallback removed from `BootstrapManager`
- [ ] `safe_resolve_legacy()` removed from exports
- [ ] Backward-compat logging section removed
- [ ] `_use_registry_validation()` toggle removed
- [ ] All tests pass with updated fixtures
- [ ] Pipeline runs without regression

#### Deliverables
- Updated files across 8+ modules (see table above)
- `reports/phase_D_legacy_removal_report.md`

---

## 9. References

1. [agent_rule.md](../../agent_rule.md)
2. [dcc_engine_pipeline.py](../../workflow/dcc_engine_pipeline.py)
3. [context_pipeline.py](../../workflow/core_engine/context/context_pipeline.py)
4. [base_engine.py](../../workflow/core_engine/base/base_engine.py)
5. [base_processor.py](../../workflow/core_engine/base/base_processor.py)
6. [error_manager.py](../../workflow/core_engine/errors/error_manager.py)
7. [boot_pipeline.py](../../workflow/utility_engine/bootstrap/boot_pipeline.py)
8. [schema_validator.py](../../workflow/schema_engine/validator/schema_validator.py)
9. [processor_engine.py](../../workflow/processor_engine/core/engine.py)
10. [proc_factories.py](../../workflow/processor_engine/core/proc_factories.py)
11. [detection.py](../../workflow/mapper_engine/mappers/detection.py)
12. [path_resolvers.py](../../workflow/utility_engine/paths/path_resolvers.py)
13. [cli_parser.py](../../workflow/utility_engine/cli/cli_parser.py)
14. [initiation_engine/utils/logging.py](../../workflow/initiation_engine/utils/logging.py)
15. [pipeline_architecture_design_workplan.md](pipeline_architecture_workplan/pipeline_architecture_design_workplan.md)
16. [issue_log.md](../issue_log.md)
