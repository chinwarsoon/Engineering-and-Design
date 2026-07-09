# Universal Pipeline Architecture Design

**Document ID**: WP-UNIVERSAL-PIPELINE-ARCH-001  
**Current Version**: 1.4  
**Status**: 📋 Proposed for Review  
**Last Updated**: 2026-07-11  
**Purpose**: Universal design patterns for pipeline architecture applicable across all projects  

---

## Revision History

| Revision | Date | Author | Summary |
| :--- | :--- | :--- | :--- |
| 1.2 | 2026-07-11 | System | Added §3 Common Library Inventory — 14 universal modules/functions/engines identified across dcc/workflow and eks/engine with extraction priority ratings. Updated document index. Renumbered all subsequent sections. |
| 1.4 | 2026-07-11 | opencode | Review of EKS T1.77 vs DCC `initiation_engine` revealed gaps and one readiness-gate regression (`eks.yml` path). Marked T1.77 ✅ DONE in all pattern references; added T1.78 (Initiation Integrity Remediation) PLANNED to close gaps: input-file readability, env/dependency probe, readiness summary, ErrorManager wiring, output-path validation, schema-driven debug default, 6-category validator. Added §3.9.1 Initiation Integrity Layers. Updated §8.2, §2.2 L13, §7.5.2, §9, §10. |
| 1.3 | 2026-07-11 | opencode | Recorded EKS initiation integrity checks (T1.77, mirrors DCC `initiation_engine`) across patterns: §2.2 L13 (ValidationManager), §3.6 Multi-Stage Validation, §3.9 Project Setup Validation (EKS `ProjectSetupValidator` + T1.77 readiness gate; corrected DCC path), §7.5.2 Parameter Precedence (EKS `--debug`/`--level` + schema-default gap), §3.13 Security Baseline (EKS T1.70 traversal guard). Updated §8.2 EKS status to reflect T1.77 PLANNED. |
| 1.1 | 2026-06-26 | Cascade | Added 4 new patterns: Idempotency & Checkpointing, Structured Logging & Correlation IDs, Security Baseline, Concurrency Model. Added standardized I/O pattern for independent engine execution. Added lessons learned from DCC logs and workplans. |
| 1.0 | 2026-06-26 | Cascade | Initial version with 10 universal design patterns extracted from DCC pipeline architecture. |

---

## Document Index

| § | Section | Description |
| :--- | :--- | :--- |
| 1 | [Executive Summary](#1-executive-summary) | Purpose and scope of this document |
| 2 | [Common Library Inventory](#2-common-library-inventory) | 14 universal modules identified across dcc/workflow and eks/engine |
| 3 | [Universal Design Patterns](#3-universal-design-patterns) | 15 architecture patterns with structure, benefits, and reference implementations |
| 4 | [Pattern Application Guidelines](#4-pattern-application-guidelines) | When to apply each pattern and recommended implementation order |
| 5 | [Benefits Summary](#5-benefits-summary) | Maintainability, testability, observability, flexibility, UX, security |
| 6 | [Risks and Mitigation](#6-risks-and-mitigation) | Known risks and mitigation strategies |
| 7 | [Lessons Learned and Best Practices](#7-lessons-learned-and-best-practices) | Implementation lessons, technical best practices, anti-patterns |
| 8 | [Reference Implementations](#8-reference-implementations) | DCC Pipeline (primary) and EKS Pipeline (secondary) |
| 9 | [Appendix A: Pattern Checklist](#9-appendix-a-pattern-checklist) | Checklist for new pipeline design |
| 10 | [Appendix B: Success Criteria](#10-appendix-b-success-criteria) | Compliance criteria for universal architecture |

---

## 1. Executive Summary

This document defines universal design patterns for pipeline architecture that can be applied across different data processing systems. These patterns have been validated through implementation in the DCC pipeline (achieving FULLY COMPLIANT status) and are recommended for adoption in other pipeline projects including EKS (Engineering Knowledge System). The patterns focus on centralized context management, dependency injection, schema-driven configuration, and comprehensive validation.

---

## 2. Common Library Inventory

The following 14 modules, functions, and engines have been identified as duplicated or near-identical implementations across `dcc/workflow` and `eks/engine`. All are candidates for extraction into `common/` as shared libraries. Extraction eliminates maintenance drift, enforces a single contract, and makes both projects immediately benefit from any improvement.

### 2.1 Extraction Priority Key

| Symbol | Priority | Criteria |
| :---: | :--- | :--- |
| 🔴 | High | Fully duplicated logic, both projects use it today, divergence already occurring |
| 🟠 | Medium | Substantially overlapping, one project has the more complete implementation |
| 🟡 | Low | Minor overlap or one project has a gap — lower immediate value |

---

### 2.2 Inventory Table

| # | Library | dcc/workflow | eks/engine | Priority |
| :--- | :--- | :--- | :--- | :---: |
| L01 | Tiered Logger + Debug Object | `core_engine/logging/log_handlers.py`, `log_state.py` | `engine/logging/logger.py` (`EKSLogger`) | 🔴 High |
| L02 | `@log_depth` / Call-Depth | `core_engine/logging/log_formatters.py` (`log_context` ctx mgr) | `engine/logging/logger.py` (`log_depth` decorator) | 🔴 High |
| L03 | Trace Parameter / Trace Step | `core_engine/logging/log_formatters.py` (`trace_parameter`, `track_global_param`) | `engine/logging/logger.py` (`EKSLogger.trace_step`) | 🟠 Medium |
| L04 | System Snapshot | `core_engine/logging/log_state.py` (`_get_system_snapshot`) | `engine/logging/logger.py` (`EKSLogger._get_system_snapshot`) | 🟡 Low |
| L05 | TelemetryHeartbeat | `core_engine/logging/log_telemetry.py` (`TelemetryHeartbeat`, `HeartbeatPayload`) | `engine/core/telemetry.py` (`TelemetryHeartbeat`, `DocumentProcessingHeartbeat`) | 🔴 High |
| L06 | PipelineContext Base | `core_engine/context/context_pipeline.py` (`PipelineContext` + nested dataclasses) | `engine/core/context.py` (`EKSPipelineContext` + nested dataclasses) | 🔴 High |
| L07 | BaseEngine / BaseProcessor | `core_engine/base/base_engine.py`, `base_processor.py` | `engine/core/base.py` (`BaseEngine`, `BaseProcessor`) | 🔴 High |
| L08 | EngineInput / EngineOutput Contracts | Not yet extracted — defined inline | `engine/core/base.py` + `engine/core/io_contracts.py` (reference impl) | 🟠 Medium |
| L09 | Factory / Dependency Injection | `processor_engine/core/proc_factories.py`, `core/registry.py` | `engine/core/factories.py` (`Factory`, `ParserFactory`, `EngineFactory`) | 🟠 Medium |
| L10 | ErrorManager + Catalog Loader | `core_engine/errors/error_manager.py` (functional helpers) | `engine/core/error_manager.py` (`ErrorManager` class) | 🟠 Medium |
| L11 | MessageManager / Catalog Loader | `utility_engine/console/console_output.py` (`_load_message_catalog`, `get_message`) | `engine/core/message_manager.py` (`MessageManager` class) | 🟠 Medium |
| L12 | OS Detection + Path Normalization | `core_engine/paths/path_core.py` + `utility_engine/paths/path_core.py` (duplicated) | `engine/core/context.py` (gap — T1.74) | 🔴 High |
| L13 | ValidationManager | `utility_engine/validation/validation_manager.py` (`ValidationManager` — mature) | `engine/core/setup_validator.py` + `engine/core/validator.py` (split) | 🟠 Medium |
| L14 | UI Contract (Request / Response) | `core_engine/ui/ui_contract.py` (`UIRequest`, `UIResponse`, `UIContractManager`) | `ui/backend/phase1_server.py` (inline Flask handlers — no formal contracts) | 🟡 Low |

---

### 2.3 Proposed `common/` Package Structure

All 14 libraries map to the following target layout under the existing `common/` folder:

```
common/
├── logging/
│   ├── __init__.py
│   ├── logger.py            # L01 — UniversalLogger (merges EKSLogger + log_handlers)
│   ├── depth.py             # L02 — log_depth decorator + log_context ctx manager
│   ├── trace.py             # L03 — trace_parameter, trace_step, track_global_param
│   └── snapshot.py          # L04 — get_system_snapshot()
├── telemetry/
│   ├── __init__.py
│   └── heartbeat.py         # L05 — TelemetryHeartbeat, HeartbeatPayload, Checkpoint
├── pipeline/
│   ├── __init__.py
│   ├── context.py           # L06 — BasePipelineContext, BasePaths, BaseState, BaseTelemetry
│   ├── base_engine.py       # L07 — BaseEngine, BaseProcessor, ValidationResult, ErrorRecord
│   └── io_contracts.py      # L08 — EngineInput, EngineOutput (reference from EKS)
├── factories/
│   ├── __init__.py
│   └── base_factory.py      # L09 — Factory ABC, config-driven create() pattern
├── errors/
│   ├── __init__.py
│   └── error_manager.py     # L10 — BaseErrorManager, catalog loader, severity logic
├── messages/
│   ├── __init__.py
│   └── message_manager.py   # L11 — BaseMessageManager, catalog loader, template hydration
├── paths/
│   ├── __init__.py
│   └── path_utils.py        # L12 — detect_os(), safe_posix(), resolve_anchored(), safe_cwd()
├── validation/
│   ├── __init__.py
│   └── validation_manager.py # L13 — ValidationManager (from DCC reference impl)
├── ui/
│   ├── __init__.py
│   └── contracts.py         # L14 — UIRequest, UIResponse, UIContractManager
├── universal_pipeline_architecture_design.md
├── universal_ui_design.css
├── universal_ui_design.js
└── universal_ui_design.md
```

### 2.4 Per-Library Detail

#### L01 — Tiered Logger + Debug Object
- **dcc**: Module-level functions `log_status/warning/error/trace()` + global `DEBUG_OBJECT` dict + `DEBUG_LEVEL` int
- **eks**: `EKSLogger` class with `.status/.warning/.error/.trace()` methods + per-instance `debug_object` dict
- **Divergence**: DCC uses a global singleton; EKS uses per-instance objects. Both support 4 levels (0–3), structured `logs/errors/trace_table` fields, and `save_debug_log()` to JSON.
- **Extraction target**: `UniversalLogger` class with optional global singleton accessor. DCC migrates to class; EKS renames.

#### L02 — `@log_depth` / Call-Depth
- **dcc**: `log_context(module, context)` context manager increments/decrements `CALL_DEPTH` global
- **eks**: `log_depth` decorator increments/decrements `_depth` global
- **Divergence**: Form only (context manager vs decorator). Both manage the same integer counter for indented output.
- **Extraction target**: Provide both forms from a single shared depth counter.

#### L03 — Trace Parameter / Trace Step
- **dcc**: `trace_parameter(name, value, source, status, duration_ms)` + `track_global_param(name, value, stage)` append to `DEBUG_OBJECT["trace_table"]`
- **eks**: `EKSLogger.trace_step(step, parameter, value, source, status, duration)` appends to `debug_object["trace_table"]`
- **Divergence**: Field naming only. Schema is identical: `timestamp`, `name/parameter`, `value`, `source`, `status`, `duration_ms`.
- **Extraction target**: Single `trace_step()` function/method with unified field names.

#### L04 — System Snapshot
- **dcc**: Captures `platform`, `platform_release`, `python_version`, `processor`, `hostname`
- **eks**: Captures `os`, `python_version`, `cpu_count`, `memory_total`, `cwd`
- **Extraction target**: `get_system_snapshot()` returning the union of both field sets.

#### L05 — TelemetryHeartbeat
- **dcc**: Row-oriented `tick(current_row, current_phase, total_rows)` → `HeartbeatPayload`; uses `psutil` for memory
- **eks**: Phase/document-oriented `add_checkpoint(phase, details, document_count)`; adds threading lock, CPU sampling, `DocumentProcessingHeartbeat` subclass
- **Divergence**: Orientation (rows vs documents/phases) and thread-safety. Core contract — periodic metric capture + `to_dict()` — is identical.
- **Extraction target**: `TelemetryHeartbeat` base class with `tick()` and `add_checkpoint()` both supported; `DocumentProcessingHeartbeat` subclass retained.

#### L06 — PipelineContext Base
- **dcc**: `PipelineContext(paths, parameters, blueprint, state, telemetry, data, load_state)` with `add_system_error()`, `add_data_error()`, `should_fail_fast()`, `get_error_summary()`
- **eks**: `EKSPipelineContext(paths, data, parameters, state, telemetry, schema_registry, config_registry)` with `to_dict()`, `from_dict()`, `save_checkpoint()`, `load_checkpoint()`, `update_phase()`, `complete()`, `fail()`
- **Divergence**: DCC has richer error API; EKS has richer serialization/checkpoint API. Both use nested `@dataclass` for sub-objects.
- **Extraction target**: `BasePipelineContext` abstract base providing serialization, checkpoint, and phase lifecycle. Both projects extend with domain-specific fields.

#### L07 — BaseEngine / BaseProcessor
- **dcc**: `BaseEngine(context: PipelineContext)` with abstract `run() -> Dict`; `BaseProcessor(context, schema_data)` with `_resolve_schema_reference()`
- **eks**: `BaseEngine(name)` with abstract `validate_input()`, `execute()`, `validate_output()` and concrete `run()` implementing validate→execute→validate flow
- **Divergence**: DCC passes context at construction; EKS passes `EngineInput` at `run()`. EKS has the more complete contract (Pattern 2.15).
- **Extraction target**: `BaseEngine[I, O]` generic ABC with EKS-style validate→execute→validate flow; DCC migrates to pass context via `EngineInput`.

#### L08 — EngineInput / EngineOutput Contracts
- **dcc**: Not yet extracted
- **eks**: `EngineInput(run_id, data_dir, config_file, schema_dir, output_dir, parameters, checkpoint_state)` + `EngineOutput(run_id, status, output_files, metadata, errors, checkpoint_state, telemetry)` + domain extensions `DiscoveryInput/Output`, `HealthInput/Output`
- **Extraction target**: Move base `EngineInput`/`EngineOutput`/`ValidationResult`/`ErrorRecord` to `common/pipeline/io_contracts.py`; domain extensions stay in each project.

#### L09 — Factory / Dependency Injection
- **dcc**: Direct-import factories in `proc_factories.py`; component registry in `core/registry.py`
- **eks**: `Factory` ABC with `create(**kwargs)` + `_get_config(key)`; `ParserFactory`, `HealthScorerFactory`, `EngineFactory` using `importlib` for dynamic loading
- **Extraction target**: `Factory` ABC and `importlib`-based dynamic loading pattern from EKS; DCC factories refactor to extend it.

#### L10 — ErrorManager + Catalog Loader
- **dcc**: Functional helpers `handle_system_error()`, `handle_data_error()`, `wrap_engine_execution()` wrapping `PipelineContext`
- **eks**: `ErrorManager` class loading `eks_error_config.json`, `handle_system_error()`, `handle_data_error()`, `get_error_summary()`, `get_health_impact()`, fail-fast support
- **Divergence**: DCC is stateless functions; EKS is a stateful class with catalog. EKS is the more complete reference.
- **Extraction target**: `BaseErrorManager` with catalog JSON loading, severity lookup, fail-fast, and `get_error_summary()`.

#### L11 — MessageManager / Catalog Loader
- **dcc**: Module-level `_load_message_catalog()`, `get_message(msg_id, **ctx)`, `status_print()`, `milestone_print()` backed by `pipeline_message_config.json`
- **eks**: `MessageManager` class loading `eks_message_config.json`, `get(msg_id, **kwargs)`, `show(msg_id)`, verbosity filtering
- **Divergence**: DCC is module-level functions; EKS is a class. Template hydration via `str.format(**kwargs)` is identical in both.
- **Extraction target**: `BaseMessageManager` class with catalog loading, template hydration, and verbosity filtering.

#### L12 — OS Detection + Path Normalization
- **dcc**: `detect_os()` duplicated verbatim in `core_engine/paths/path_core.py` AND `core_engine/system/system_environment.py`; `normalize_path_separators()` in `utility_engine/paths/path_core.py`; `safe_resolve()`, `safe_cwd()`, `get_homedir()` in `core_engine/paths/path_core.py`
- **eks**: `EKSPaths.to_dict()` uses `str()` not `.as_posix()` — the T1.74 cross-platform gap
- **Extraction target**: `common/paths/path_utils.py` with `detect_os()`, `safe_posix(path)`, `resolve_anchored(path, base)`, `safe_cwd()`, `get_homedir()`. Eliminates DCC duplication and fixes EKS T1.74 at source.

#### L13 — ValidationManager
- **dcc**: Mature `ValidationManager` with `validate_file_exists()`, `validate_directory_exists()`, `validate_parameter()`, `validate_paths_and_parameters()`, `validate_pipeline_prerequisites()`, folder-creation config support
- **eks**: Concerns split across `engine/core/setup_validator.py` (`ProjectSetupValidator` — folders/files/env) and `engine/core/validator.py` (schema validation). **T1.77 (✅ DONE)** invokes `ProjectSetupValidator.validate_all()` as a fail-fast readiness gate at pipeline-thread start (mirrors DCC `validate_pipeline_prerequisites()`). A review found a readiness-gate regression (`eks.yml` path) and missing DCC layers (input readability, env probe, readiness summary, ErrorManager wiring, output-path validation) — **T1.78 (🔷 PLANNED)** remediates these.
- **Extraction target**: DCC `ValidationManager` is the reference; EKS consolidates its validators to extend it.

#### L14 — UI Contract (Request / Response)
- **dcc**: `UIRequest`, `UIResponse` dataclasses with `from_json()`/`to_json()`; `UIContractManager` with `validate_selection()`, `run_pipeline()`, `run_from_ui_request()`
- **eks**: Inline Flask route handlers in `phase1_server.py` — no formal contract dataclasses
- **Extraction target**: `UIRequest`/`UIResponse`/`UIContractManager` from DCC as the base; EKS adopts for T1.72 (enforce I/O contracts).

---

## 3. Universal Design Patterns

### 3.1 PipelineContext Pattern

**Purpose**: Single source of truth for pipeline state and configuration, preventing "prop drilling"

**Description**: A centralized context object encapsulates all pipeline state, configuration, and data. This eliminates the need to pass individual variables through multiple function layers (prop drilling), reduces function signature complexity, and provides a consistent access pattern for all pipeline components.

**Structure**:
```python
@dataclass
class PipelineContext:
    paths: PipelinePaths              # Filesystem paths
    data: PipelineData                # Data containers (raw, processed, etc.)
    parameters: Dict[str, Any]        # Configuration parameters
    state: PipelineState              # Execution results and progress
    telemetry: PipelineTelemetry      # Performance tracking
    blueprint: PipelineBlueprint      # Immutable rules and schema
```

**Benefits**:
- Eliminates "prop drilling" (passing individual variables through multiple layers)
- Centralized state management
- Easy serialization for debugging
- Consistent parameter access
- Reduced function signatures (5-7 parameters → 1-2)

**Reference Implementation**: DCC Pipeline (dcc/workflow/core_engine/context.py)

---

### 3.2 Dependency Injection Pattern

**Purpose**: Swappable implementations, simplified testing, platform flexibility

**Description**: Components are created through factory methods rather than direct instantiation. This enables swappable implementations (e.g., different parsers for different file types), simplified testing with mocks, clear dependency graphs, and platform flexibility.

**Structure**:
```python
class ComponentFactory:
    @staticmethod
    def create_component(context: PipelineContext) -> Component:
        return Component(
            dependency1=DependencyFactory.create(context),
            dependency2=DependencyFactory.create(context),
            dependency3=DependencyFactory.create(context)
        )
```

**Benefits**:
- Swappable implementations (e.g., different parsers for different file types)
- Simplified testing with mocks
- Clear dependency graph
- Platform flexibility

**Reference Implementation**: DCC Pipeline (dcc/workflow/processor_engine/factories.py)

---

### 3.3 Phase-Based Orchestration Pattern

**Purpose**: Sequential processing phases with clear checkpoints

**Description**: Pipeline execution is divided into sequential phases with clear boundaries and checkpoints. Each phase performs a specific transformation, enabling clear processing sequence, easy debugging at each phase, progress tracking opportunities, and modular testing.

**Structure**:
```python
def apply_phased_processing(self, input_data) -> output_data:
    # Phase 1: Initial transformation
    data_phase1 = self.phase_1_transformation(input_data)
    
    # Phase 2: Secondary transformation
    data_phase2 = self.phase_2_transformation(data_phase1)
    
    # Phase 3: Tertiary transformation
    data_phase3 = self.phase_3_transformation(data_phase2)
    
    # Phase 4: Final transformation
    return self.phase_4_transformation(data_phase3)
```

**Benefits**:
- Clear processing sequence
- Easy debugging at each phase
- Progress tracking opportunities
- Modular testing

**Reference Implementation**: DCC Pipeline (dcc/workflow/processor_engine/core/engine.py)

---

### 3.4 Telemetry Heartbeat Pattern

**Purpose**: Periodic progress reporting with system metrics

**Description**: A heartbeat system emits periodic progress reports with system metrics (memory usage, processing count, current phase). This provides real-time progress visibility, performance monitoring, debugging support, and improved user experience.

**Structure**:
```python
class TelemetryHeartbeat:
    def tick(self, current_count: int, current_phase: str, 
             total_count: int, status_print_fn: Callable) -> HeartbeatPayload:
        payload = HeartbeatPayload(
            count_processed=current_count,
            current_phase=current_phase,
            memory_usage_mb=self._get_memory_usage(),
            timestamp=datetime.now(),
            total_count=total_count,
            percent_complete=(current_count / total_count) * 100
        )
        status_print_fn(f"⏳ Processing item {current_count} ({payload.percent_complete:.1f}%) | "
                       f"Phase: {current_phase} | Memory: {payload.memory_usage_mb:.1f} MB")
        return payload
```

**Benefits**:
- Real-time progress visibility
- Performance monitoring
- Debugging support
- User experience improvement

**Reference Implementation**: DCC Pipeline (dcc/workflow/core_engine/telemetry_heartbeat.py)

---

### 3.5 Schema-Driven Configuration Pattern

**Purpose**: External configuration files drive processing logic

**Description**: Processing logic is driven by external configuration files (JSON/YAML) rather than hardcoded values. This enables logic externalization, easy configuration changes, version control of rules, and business user ownership.

**Structure**:
```json
{
  "columns": {
    "Document_ID": {
      "calculation": "concat",
      "dependencies": ["Project_Code", "Document_Sequence_Number"],
      "null_handling": "skip_if_missing"
    }
  }
}
```

**Benefits**:
- Logic externalization
- Easy configuration changes
- Version control of rules
- Business user ownership

**Reference Implementation**: DCC Pipeline (dcc/config/schemas/), EKS Pipeline (eks/config/schemas/)

---

### 3.6 Multi-Stage Validation Pattern

**Purpose**: Validation at multiple processing stages

**Description**: Validation occurs at multiple processing stages (file/path validation, schema validation, data validation, parser validation). This enables early error detection, clear error categorization, progressive validation, and better user feedback.

**Structure**:
```python
def validate_pipeline(self, context: PipelineContext) -> ValidationResult:
    # Stage 1: File and path validation
    path_validation = self._validate_paths(context.paths)
    
    # Stage 2: Schema validation
    schema_validation = self._validate_schema(context.paths.schema_path)
    
    # Stage 3: Data validation
    data_validation = self._validate_data(context)
    
    return ValidationResult.merge(path_validation, schema_validation, data_validation)
```

**Benefits**:
- Early error detection
- Clear error categorization
- Progressive validation
- Better user feedback

**Reference Implementation**: DCC Pipeline (dcc/workflow/schema_engine/); EKS Pipeline applies this at phase boundaries via `DiscoveryInput`/`ParserInput` contracts (T1.72) and will add file-path + schema validation at initiation via T1.77.

---

### 3.7 Standardized Error Catalog Pattern

**Purpose**: Structured error codes with severity levels

**Description**: Errors are defined in a standardized catalog with hierarchical codes, severity levels, categories, messages, and resolution guidance. This enables consistent error handling, easy error tracking, clear resolution guidance, and automated error analysis.

**Structure**:
```python
class ErrorCatalog:
    P1_A_P_0101 = Error(
        code="P1-A-P-0101",
        severity="HIGH",
        category="VALIDATION",
        message="Required column missing: {column}",
        resolution="Add missing column to input data"
    )
```

**Benefits**:
- Consistent error handling
- Easy error tracking
- Clear resolution guidance
- Automated error analysis

**Reference Implementation**: DCC Pipeline (dcc/config/schemas/eks_error_config.json), EKS Pipeline (eks/config/schemas/eks_error_config.json)

---

### 3.8 UI Contract Pattern

**Purpose**: Backend contracts before frontend implementation

**Description**: Backend contracts are defined before frontend implementation, providing type safety, clear API contracts, centralized validation, and easy testing. Contracts include validation logic and serialization methods.

**Structure**:
```python
@dataclass
class PathSelectionContract:
    base_path: Path
    upload_file_name: str
    output_folder: str = "output"
    
    def validate(self) -> Dict[str, Any]:
        # Validation logic
        
    def to_paths(self) -> PipelinePaths:
        # Path resolution
```

**Benefits**:
- Type safety
- Clear API contracts
- Centralized validation
- Easy testing

**Reference Implementation**: DCC Pipeline (dcc/workflow/initiation_engine/overrides.py)

---

### 3.9 Project Setup Validation Pattern

**Purpose**: Project structure checker for workspace initialization

**Description**: A validator checks project structure (folders, files, environment) and can auto-create missing folders. This provides automated project setup verification, auto-creation of missing folders, clear readiness status, and a pre-pipeline validation gate.

**Structure**:
```python
class ProjectSetupValidator:
    def validate(self) -> Dict[str, Any]:
        # 1. Confirm project_setup.json exists
        # 2. Load project_setup configuration
        # 3. Validate folders
        # 4. Validate files
        # 5. Validate environment files
        # 6. Determine final readiness status
```

**Benefits**:
- Automated project setup verification
- Auto-creation of missing folders
- Clear readiness status
- Pre-pipeline validation gate

**EKS Status**: EKS implements `ProjectSetupValidator` (`eks/engine/core/setup_validator.py`) checking required folders, schema files, and environment, and **T1.77 (✅ DONE)** wires `validate_all()` as a fail-fast readiness gate at the start of the pipeline thread in `phase1_server._run()`, mirroring DCC. A review against DCC found (a) a **readiness-gate regression**: `project_setup.required_files` lists `eks.yml` (repo root) while the file is at `eks/eks.yml`, so the gate returns `readiness=NO` and blocks every run — tracked for fix in **T1.78 (🔷 PLANNED)**; and (b) several DCC initiation layers EKS has not yet implemented (input-file readability, env/dependency probe, readiness summary, ErrorManager wiring, output-path validation, schema-driven debug default, 6-category validator structure) — also covered by T1.78. See [EKS Phase 1 Workplan](eks/workplan/phase_1_foundation_workplan.md) T1.77 / T1.78.

#### 3.9.1 Initiation Integrity Layers (DCC reference)

DCC applies initiation integrity as **distinct layers**; the universal pattern should capture all of them, not only project-structure validation:

1. **Project Structure Validation** (§3.9) — required/optional folders + files + environment; auto-create; `readiness = YES/NO`.
2. **User-Input Contract Validation** — confirm the user-selected input exists **and is readable** (e.g. `PathSelectionContract` 1-byte read test) before processing.
3. **Environment / Dependency Probe** — `test_environment()` checks required (block) vs optional (warn) modules from `project_setup.dependencies`.
4. **Output / Export-Path Validation** — `validate_export_paths()` creates output dir and fails fast if outputs exist with overwrite disabled.
5. **Parameter Precedence** — CLI > UI > Schema > Native (§7.5.2).
6. **Fail-Fast Gating** — abort the pipeline *before any data is read* if integrity is not satisfied, with a structured error code (DCC: `S-C-S-0305`).

EKS currently implements layers 1 (partially) and 5 (partially); layers 2–4 and the structured-error part of 6 are the T1.78 scope.

**Reference Implementation**: DCC Pipeline (`dcc/workflow/initiation_engine/core/validator.py` — `ProjectSetupValidator`); EKS Pipeline (`eks/engine/core/setup_validator.py`, T1.77 pending wiring)

---

### 3.10 Foundation/Utility Separation Pattern

**Purpose**: Separate universal foundation logic from domain-specific processing

**Description**: Universal foundation logic (logging, paths, IO, context, base classes) is separated from domain-specific processing engines. Interface utilities (console, CLI, error management) are also separated. This provides clear separation of concerns, reusable foundation components, reduced code duplication, and easier maintenance.

**Structure**:
```
project/workflow/
├── core_engine/          # Foundation: logging, paths, IO, context, base classes
├── utility_engine/       # Interface: console, CLI, error management
├── domain_engine_1/      # Domain: specific processing logic
├── domain_engine_2/      # Domain: specific processing logic
└── domain_engine_3/      # Domain: specific processing logic
```

**Benefits**:
- Clear separation of concerns
- Reusable foundation components
- Reduced code duplication
- Easier maintenance

**Reference Implementation**: DCC Pipeline (dcc/workflow/core_engine/, dcc/workflow/utility_engine/)

---

### 3.11 Idempotency & Checkpointing Pattern

**Purpose**: Safe re-runs and resumability after partial failure

**Description**: Each phase should be safe to re-run on the same input without duplicating side effects — writes should be upserts/overwrites, not blind appends. Where phases are long-running, persist a checkpoint (last completed phase + relevant state) so a failed run can resume from the last good point rather than restarting from phase 1.

**Structure**:
```python
@dataclass
class CheckpointState:
    run_id: str
    last_completed_phase: str
    phase_timestamps: Dict[str, datetime]
    phase_state: Dict[str, Any]  # Minimal state needed for resume

class CheckpointManager:
    def save_checkpoint(self, context: PipelineContext, phase: str):
        state = CheckpointState(
            run_id=context.state.run_id,
            last_completed_phase=phase,
            phase_timestamps=context.state.phase_timestamps,
            phase_state=self._extract_minimal_state(context, phase)
        )
        self._persist_checkpoint(state)
    
    def load_checkpoint(self, run_id: str) -> Optional[CheckpointState]:
        return self._read_checkpoint(run_id)
    
    def should_resume_from(self, run_id: str) -> Optional[str]:
        checkpoint = self.load_checkpoint(run_id)
        return checkpoint.last_completed_phase if checkpoint else None
```

**Benefits**:
- Safe retries after transient failures
- No wasted reprocessing on resume
- Reduced blast radius of partial failures

**Relationship to Existing Patterns**: Builds directly on PipelineContext (3.1) and Phase-Based Orchestration (3.3) — the context's state field is a natural place to persist checkpoint data.

**Reference Implementation**: DCC Pipeline (partial — Phase-Based Orchestration exists, full checkpointing planned)

---

### 3.12 Structured Logging & Correlation IDs Pattern

**Purpose**: Machine-parseable, traceable logs across phases and components

**Description**: Logs should be structured (key-value or JSON) rather than free-text, with consistent severity levels. Each pipeline run should carry a correlation ID (a run ID) that's threaded through every log line, telemetry payload, and error record, so a single run can be reconstructed end-to-end from logs alone — especially important once a pipeline runs concurrently or at scale.

**Structure**:
```python
@dataclass
class LogEntry:
    run_id: str
    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    component: str
    phase: str
    message: str
    context: Dict[str, Any]  # Additional structured data

class StructuredLogger:
    def __init__(self, run_id: str):
        self.run_id = run_id
    
    def log(self, level: str, component: str, phase: str, 
            message: str, **context):
        entry = LogEntry(
            run_id=self.run_id,
            timestamp=datetime.now(),
            level=level,
            component=component,
            phase=phase,
            message=message,
            context=context
        )
        self._emit(entry)  # JSON or key-value format
    
    # Convenience methods
    def info(self, component: str, phase: str, message: str, **context):
        self.log("INFO", component, phase, message, **context)
    
    def error(self, component: str, phase: str, message: str, **context):
        self.log("ERROR", component, phase, message, **context)
```

**Benefits**:
- End-to-end traceability of a single run
- Logs are queryable/filterable, not just human-readable
- Easier correlation between telemetry (2.4), errors (2.7), and logs

**Relationship to Existing Patterns**: Extends Telemetry Heartbeat (3.4) and Error Catalog (3.7) — both should emit the same run ID.

**Reference Implementation**: DCC Pipeline (partial — multi-level logging exists, structured JSON logging planned)

---

### 3.13 Security Baseline Pattern

**Purpose**: Minimum security hygiene for any pipeline, regardless of domain

**Description**: Secrets (API keys, credentials, connection strings) are never hardcoded or committed — sourced from environment variables or a secrets manager. Inputs are validated/sanitized before use (especially anything that becomes a file path, SQL fragment, or shell argument). Access to data and infrastructure follows least privilege. Security-relevant events (who ran what, when, against what data) are logged as part of the audit trail.

**Structure**:
```python
class SecretsManager:
    def get_secret(self, key: str) -> str:
        # Source from environment variables or secrets manager
        # Never hardcode or commit secrets
        value = os.environ.get(key)
        if value is None:
            raise SecurityError(f"Secret not found: {key}")
        return value
    
    def validate_path(self, path: Path) -> Path:
        # Prevent path traversal attacks
        resolved = path.resolve()
        if not str(resolved).startswith(self.allowed_base):
            raise SecurityError(f"Path traversal attempt: {path}")
        return resolved

class SecurityAuditor:
    def log_security_event(self, event_type: str, user: str, 
                           resource: str, action: str):
        entry = {
            "event_type": event_type,
            "user": user,
            "resource": resource,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        self.audit_log.append(entry)
```

**Benefits**:
- Prevents credential leakage
- Reduces injection/path-traversal risk
- Auditable trail for compliance-sensitive pipelines

**Relationship to Existing Patterns**: Secrets and access config can live alongside Schema-Driven Config (3.5), but should be kept in a separate, access-restricted store rather than the same versioned config files as business rules.

**Reference Implementation**: DCC Pipeline (partial — environment variable usage exists, full security baseline planned); EKS Pipeline applies the path-traversal portion via `phase1_server._check_traversal()` (`is_relative_to(PRJ_DIR)` → HTTP 403) in T1.70, guarding `data_dir` on pipeline start and file-load.

---

### 3.14 Concurrency Model Pattern

**Purpose**: Explicit, documented choice of execution model

**Description**: Each pipeline should explicitly state whether it's single-threaded, multi-process, async, or distributed, since this materially affects how PipelineContext (2.1) and Telemetry Heartbeat (2.4) must be implemented — e.g. shared mutable context across threads needs locking or immutable snapshots, while distributed execution needs the checkpoint/correlation-ID mechanisms above to be backend-shared, not in-memory.

**Structure**:
```python
from enum import Enum

class ConcurrencyModel(Enum):
    SINGLE_THREADED = "single_threaded"
    MULTI_PROCESS = "multi_process"
    ASYNC = "async"
    DISTRIBUTED = "distributed"

@dataclass
class ConcurrencyConfig:
    model: ConcurrencyModel
    max_workers: int = 1
    context_sharing: str = "immutable"  # or "locked" or "isolated"
    checkpoint_backend: str = "local"  # or "shared" for distributed

class ConcurrencyAwareContext:
    def __init__(self, config: ConcurrencyConfig):
        self.config = config
        if config.model == ConcurrencyModel.MULTI_PROCESS:
            self._init_shared_state_locking()
        elif config.model == ConcurrencyModel.DISTRIBUTED:
            self._init_distributed_checkpoint_backend()
```

**Benefits**:
- Avoids race conditions/hidden shared-state bugs
- Makes scaling decisions deliberate rather than accidental
- Clarifies thread-safety requirements for context and telemetry

**Relationship to Existing Patterns**: A prerequisite design decision for PipelineContext (3.1) and Telemetry Heartbeat (3.4) — should be settled before either is implemented.

**Reference Implementation**: DCC Pipeline (single-threaded model documented, multi-process planned)

---

### 3.15 Standardized Engine I/O Pattern

**Purpose**: Each engine can be run independently with standardized input/output contracts, enabling modular testing, debugging, and reusability.

**Description**: All engines implement standardized input/output contracts with base classes defining the execution flow. This enables independent execution through multiple interfaces (CLI, Python API, HTTP API), engine chaining through checkpoint state, and clear validation boundaries.

**Structure**:
```python
@dataclass
class EngineInput:
    """Standard input contract for all pipeline engines"""
    run_id: str                      # Unique identifier for this execution
    data_dir: Path                   # Input data directory
    config_file: Path                # Configuration file path
    schema_dir: Path                 # Schema directory
    output_dir: Path                # Output directory
    parameters: Dict[str, Any]       # Engine-specific parameters
    checkpoint_state: Optional[Dict[str, Any]] = None  # For resume capability

@dataclass
class EngineOutput:
    """Standard output contract for all pipeline engines"""
    run_id: str                      # Matches input run_id
    status: str                      # SUCCESS, PARTIAL, FAILED
    output_files: List[Path]         # Generated output files
    metadata: Dict[str, Any]        # Execution metadata
    errors: List[ErrorRecord]        # Any errors encountered
    checkpoint_state: Dict[str, Any] # State for next engine or resume
    telemetry: Dict[str, Any]        # Performance metrics

class BaseEngine(ABC):
    """Abstract base class for all pipeline engines"""
    
    @abstractmethod
    def validate_input(self, input_data: EngineInput) -> ValidationResult:
        """Validate input before processing"""
        pass
    
    @abstractmethod
    def execute(self, input_data: EngineInput) -> EngineOutput:
        """Execute the engine logic"""
        pass
    
    @abstractmethod
    def validate_output(self, output: EngineOutput) -> ValidationResult:
        """Validate output before returning"""
        pass
    
    def run(self, input_data: EngineInput) -> EngineOutput:
        """Standard execution flow: validate → execute → validate"""
        # 1. Validate input
        input_validation = self.validate_input(input_data)
        if not input_validation.is_valid:
            return EngineOutput(
                run_id=input_data.run_id,
                status="FAILED",
                output_files=[],
                metadata={},
                errors=[input_validation.to_error()],
                checkpoint_state={},
                telemetry={}
            )
        
        # 2. Execute
        output = self.execute(input_data)
        
        # 3. Validate output
        output_validation = self.validate_output(output)
        if not output_validation.is_valid:
            output.status = "FAILED"
            output.errors.append(output_validation.to_error())
        
        return output
```

**Benefits**:
- Independent Testing: Each engine can be tested in isolation
- Modular Debugging: Failed engines can be re-run without reprocessing entire pipeline
- Reusability: Engines can be reused in different pipelines or workflows
- Parallel Execution: Independent engines can run in parallel where possible
- Clear Contracts: Input/output validation ensures data quality between engines
- Resume Capability: Checkpoint state enables resumption from any phase

**Relationship to Existing Patterns**: Builds on PipelineContext (3.1), Phase-Based Orchestration (3.3), and Idempotency & Checkpointing (3.11) — checkpoint state flows through standardized I/O.

**Reference Implementation**: EKS Pipeline (planned in Appendix F, Section 3.3)

---

## 4. Pattern Application Guidelines

### 4.1 When to Apply Each Pattern

| Pattern | When to Apply | Priority |
| :--- | :--- | :---: |
| PipelineContext | Pipeline has >3 components passing state | 🟠 High |
| Dependency Injection | Components need swappable implementations | 🟠 High |
| Phase-Based Orchestration | Pipeline has >2 sequential transformations | 🟠 High |
| Telemetry Heartbeat | Pipeline processes >100 items or takes >10 seconds | 🟡 Medium |
| Schema-Driven Config | Business rules change frequently | 🟠 High |
| Multi-Stage Validation | Pipeline has multiple input sources or stages | 🟡 Medium |
| Error Catalog | Pipeline has >10 error conditions | 🟡 Medium |
| UI Contracts | Pipeline has UI or API interface | 🟠 High |
| Project Setup Validation | Pipeline requires specific folder structure | 🟡 Medium |
| Foundation/Utility Separation | Pipeline has >2 domain engines | 🟢 Low |
| Idempotency & Checkpointing | Pipeline phases take >5 minutes or process >1000 items | 🟠 High |
| Structured Logging & Correlation IDs | Pipeline runs concurrently or at scale | 🟠 High |
| Security Baseline | Pipeline handles sensitive data or credentials | 🟠 High |
| Concurrency Model | Pipeline may scale beyond single-threaded execution | 🟠 High |
| Standardized Engine I/O | Pipeline has multiple engines that need independent execution | 🟠 High |

### 4.2 Implementation Order

Recommended implementation order for new pipelines:

1. **Concurrency Model** — Decide execution model first (prerequisite for context/telemetry)
2. **Foundation/Utility Separation** — Establish structure first
3. **Security Baseline** — Establish security hygiene early
4. **PipelineContext** — Centralize state management (respecting concurrency model)
5. **Schema-Driven Config** — Externalize configuration (separate secrets from business rules)
6. **Multi-Stage Validation** — Add validation gates
7. **Phase-Based Orchestration** — Define processing phases
8. **Standardized Engine I/O** — Define engine contracts for independent execution
9. **Idempotency & Checkpointing** — Add resumability (builds on phases)
10. **Structured Logging & Correlation IDs** — Add traceability (builds on telemetry)
11. **Dependency Injection** — Enable swappable components
12. **Error Catalog** — Standardize error handling
13. **Telemetry Heartbeat** — Add observability (include correlation IDs)
14. **Project Setup Validation** — Add setup verification
15. **UI Contracts** — Define API contracts (if applicable)

---

## 5. Benefits Summary

### 5.1 Maintainability

- **Reduced Complexity**: Centralized context management reduces function signature complexity
- **Clear Separation**: Foundation/utility separation makes code easier to navigate
- **Consistent Patterns**: Uniform patterns across components reduce cognitive load
- **Resumability**: Checkpointing enables recovery from partial failures without full re-runs

### 5.2 Testability

- **Dependency Injection**: Easy mocking for unit tests
- **Phase-Based Testing**: Each phase can be tested independently
- **Contract Validation**: UI contracts enable automated API testing
- **Idempotency**: Safe re-runs simplify test isolation and debugging

### 5.3 Observability

- **Telemetry**: Real-time progress tracking and performance monitoring
- **Error Catalog**: Structured error tracking with resolution guidance
- **Validation**: Multi-stage validation provides early error detection
- **Structured Logging**: Machine-parseable logs enable queryable, traceable execution history
- **Correlation IDs**: End-to-end traceability across all components and phases

### 5.4 Flexibility

- **Swappable Components**: Factory pattern enables easy component replacement
- **Schema-Driven**: Configuration changes without code modifications
- **Platform Independence**: Cross-platform path handling
- **Concurrency Model**: Explicit execution model enables deliberate scaling decisions

### 5.5 User Experience

- **Progress Visibility**: Heartbeat system provides real-time feedback
- **Clear Errors**: Standardized error codes with resolution guidance
- **Setup Validation**: Automated project setup verification
- **Safe Retries**: Idempotency enables safe re-runs after transient failures

### 5.6 Security

- **Credential Protection**: Secrets never hardcoded or committed
- **Input Validation**: Sanitization prevents injection and path traversal attacks
- **Audit Trail**: Security events logged for compliance and accountability
- **Least Privilege**: Access controls follow principle of least privilege

---

## 6. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :---: | :---: | :--- |
| Refactoring breaks existing functionality | Medium | High | Maintain backward compatibility layer; comprehensive testing |
| Performance overhead from new abstractions | Low | Medium | Performance monitoring; optimize hot paths |
| Context object becomes too large | Medium | Medium | Use nested dataclasses; validate context size |
| Factory pattern adds complexity | Low | Low | Document factories thoroughly; provide examples |
| Telemetry adds runtime overhead | Low | Low | Configurable heartbeat intervals; lightweight payload |
| Checkpointing adds storage overhead | Low | Medium | Use minimal state; implement checkpoint rotation |
| Structured logging increases log volume | Medium | Low | Configurable log levels; log rotation/compression |
| Security measures add complexity | Low | High | Document security requirements; automate security checks |
| Concurrency model misalignment | Medium | High | Document model clearly; validate before implementation |
| Race conditions in concurrent execution | Medium | High | Use immutable context; implement proper locking |

---

## 7. Lessons Learned and Best Practices

### 7.1 Architecture Implementation Lessons

#### 7.1.1 Phased Implementation Approach

**Lesson**: Incremental, phase-based implementation enables focused testing and early detection of architectural limitations.

**Evidence from DCC**:
- Phase 3 revealed heartbeat interval limitation early
- Each phase had clear success criteria and validation
- Issues were contained within specific phases

**Best Practice**:
```
When implementing complex architecture changes:
1. Break into logical phases with clear boundaries
2. Define success criteria for each phase
3. Test thoroughly before proceeding to next phase
4. Document limitations and decisions as they emerge
```

#### 7.1.2 Backward Compatibility is Critical

**Lesson**: Maintaining backward compatibility during major architecture changes prevents disruption to existing workflows.

**Evidence from DCC**:
- Phase 2 DI implementation maintained legacy interfaces
- Zero disruption to existing pipeline operations
- Gradual migration path for consumers

**Best Practice**:
```
For major architecture changes:
1. Design compatibility layers alongside new implementations
2. Provide migration guides and deprecation timelines
3. Test both old and new interfaces thoroughly
4. Document breaking changes clearly
```

#### 7.1.3 Test-Driven Architecture Development

**Lesson**: Comprehensive testing at each phase ensures confidence in implementations and prevents regressions.

**Evidence from DCC**:
- 100% test pass rates across all phases
- Production validation confirmed implementations
- Tests served as living documentation

**Best Practice**:
```
For architecture development:
1. Write tests before or alongside implementation
2. Include unit, integration, and end-to-end tests
3. Test with real production data
4. Maintain high test coverage (>90%)
```

#### 7.1.4 Contract-Based UI Integration

**Lesson**: Defining backend contracts before frontend implementation creates clean separation of concerns and type safety.

**Evidence from DCC**:
- Phase 4 UI contracts enabled clean API design
- Type-safe request/response handling
- Centralized validation logic

**Best Practice**:
```
For UI integration:
1. Define backend contracts first
2. Include validation in contracts
3. Use serialization for API communication
4. Document contracts comprehensively
```

### 7.2 Technical Architecture Best Practices

#### 7.2.1 Dependency Injection Best Practices

- Use factory classes for complex object creation
- Inject dependencies through constructors
- Keep factories stateless
- Document dependency contracts

#### 7.2.2 Centralized Context Best Practices

- Use dataclasses for immutable state
- Include validation in context creation
- Provide clear access patterns
- Document context fields thoroughly

#### 7.2.3 Phase-Based Orchestration Best Practices

- Define clear phase boundaries
- Include validation at each phase
- Provide progress reporting
- Make phases independently testable

#### 7.2.4 Telemetry Heartbeat Best Practices

- Include relevant metrics (memory, time, progress)
- Use appropriate logging levels
- Consider performance impact
- Provide configurable intervals

### 7.3 Configuration and Validation Best Practices

#### 7.3.1 Schema-Driven Configuration Best Practices

- Use JSON/YAML for configuration
- Include validation schemas
- Provide default values
- Document configuration options

#### 7.3.2 Multi-Stage Validation Best Practices

- Validate at logical boundaries
- Use standardized error codes
- Provide clear error messages
- Aggregate validation results

### 7.4 Error Handling and Observability Best Practices

#### 7.4.1 Standardized Error Catalog Best Practices

- Use hierarchical error codes
- Include severity levels
- Provide resolution guidance
- Maintain error documentation

#### 7.4.2 Multi-Level Logging Best Practices

- Use consistent log formats
- Include timestamps
- Provide log levels
- Consider log rotation

### 7.5 UI Integration Best Practices

#### 7.5.1 Contract-First API Design Best Practices

- Use dataclasses for contracts
- Include validation methods
- Provide serialization support
- Document contracts thoroughly

#### 7.5.2 Parameter Precedence Rules Best Practices

- Document precedence clearly
- Apply precedence consistently
- Provide override indicators
- Log parameter resolution

**Precedence (highest to lowest)**:
1. CLI Arguments
2. UI Overrides
3. Schema Configuration
4. Hardcoded Defaults

**EKS Status**: **T1.77 (✅ DONE)** added a `--debug`/`--level` CLI flag to `phase1_server.py` and validates `data_dir` exists + `recursive` is bool before spawning the run thread — aligning with this precedence rule and the §3.9 readiness gate. The **schema-driven default debug level** (resolving `level` from `eks_config.json` rather than the current hardcoded `1`) is **deferred to T1.78 (🔷 PLANNED)**; DCC's full CLI > Schema > Native resolution chain is the reference. See [EKS Phase 1 Workplan](eks/workplan/phase_1_foundation_workplan.md) T1.77 / T1.78.

### 7.6 Performance and Scalability Best Practices

#### 7.6.1 Vectorized Operations Best Practices

- Prefer vectorized operations
- Avoid row-by-row processing
- Use appropriate data types
- Monitor memory usage

#### 7.6.2 Memory Management Best Practices

- Monitor memory usage
- Use appropriate data types
- Clean up unused objects
- Consider chunked processing for large datasets

### 7.7 Testing Strategies Best Practices

#### 7.7.1 Comprehensive Test Coverage Best Practices

- Test at multiple levels (unit, integration, end-to-end)
- Use realistic test data
- Maintain high coverage (>90%)
- Automate test execution

#### 7.7.2 Production Validation Best Practices

- Test with production data
- Validate performance metrics
- Test in target environments
- Monitor production runs

### 7.8 Documentation Practices Best Practices

#### 7.8.1 Comprehensive Documentation Best Practices

- Document decisions and rationale
- Keep documentation current
- Use consistent formats
- Include examples

#### 7.8.2 Living Documentation Best Practices

- Document code as you write
- Use documentation generators
- Include examples in docs
- Review documentation regularly

### 7.9 Common Pitfalls and Anti-Patterns

#### 7.9.1 Hardcoded Defaults in Code

**Anti-Pattern**: Hardcoded default values in provider code that ignore schema-driven configuration.

**Lesson from DCC Issue LOG-003**: Hardcoded `_DEFAULT_MODEL = "llama3.1:8b"` in Ollama provider ignored schema-driven `ai_model` parameter.

**Best Practice**: Never hardcode configuration values that should be schema-driven. Use schema as SSOT.

#### 7.9.2 Stale Import Copies

**Anti-Pattern**: Using `from module import name` creates local copies that become stale when the source changes.

**Lesson from DCC Issue LOG-002**: `set_debug_level()` rebinds local copy but not other modules' stale imports.

**Best Practice**: Use getter functions for mutable global state, or import the module and access `module.variable`.

#### 7.9.3 Missing Runtime Validation

**Anti-Pattern**: No runtime checks before resource-intensive operations.

**Lesson from DCC Issue LOG-003**: No memory check before model invocation caused hangs on under-resourced hosts.

**Best Practice**: Add runtime validation for resource constraints (memory, disk, network) before expensive operations.

---

## 8. Reference Implementations

### 8.1 DCC Pipeline (Primary Reference)

- **Location**: `dcc/workflow/`
- **Status**: FULLY COMPLIANT (19 PASS / 2 PARTIAL / 0 FAIL)
- **Key Documents**:
  - [Pipeline Architecture Design Workplan](dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md)
  - [Lessons Learned and Best Practices](dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/lessons_learned_best_practices.md)
  - [Core Utility Engine Workplan](dcc/workplan/pipeline_architecture/core_utility_engine_workplan/core_utility_engine_workplan.md)
  - [Project Setup Validation Guide](dcc/workplan/initiation_engine/project-setup-validation-guide.md)

### 8.2 EKS Pipeline (Secondary Reference)

- **Location**: `eks/`
- **Status**: Phase 1 Bootstrap COMPLETE (T1.1–T1.77 ✅); **T1.77 (Initiation Integrity Checks, mirrors DCC `initiation_engine`) ✅ DONE**. T1.78 (Initiation Integrity Remediation) 🔷 PLANNED — see [Phase 1 Foundation Workplan](eks/workplan/phase_1_foundation_workplan.md) T1.77 / T1.78. Phase 1.2 Proposed.
- **Pattern Coverage**:
  - ✅ Schema-Driven Config (§3.5), Standardized Engine I/O + I/O contracts (§3.15, T1.72), Structured Logging & Correlation IDs (§3.12, T1.69), Idempotency & Checkpointing (§3.11, T1.73)
  - ✅ Project Setup Validation (§3.9, L13) — `ProjectSetupValidator` wired as fail-fast readiness gate (T1.77); **regression + DCC-layer gaps tracked in T1.78** (§3.9.1)
  - ✅ Multi-Stage / Parameter Precedence (§3.6, §7.5.2) — `data_dir`/`recursive` validation + `--debug`/`--level` flag (T1.77); schema-driven debug default deferred to T1.78
  - ✅ Security Baseline path-traversal portion (§3.13, T1.70)
- **Key Documents**:
  - [Phase 1 Foundation Workplan](eks/workplan/phase_1_foundation_workplan.md)
  - [Phase 1.2 Interactive UI Workplan](eks/workplan/phase_1.2_interactive_ui_workplan.md)
  - [Appendix F: EKS Pipeline Architecture Design](eks/workplan/appendix_f_pipeline_architecture_design.md) — See Appendix F for EKS-specific application

---

## 9. Appendix A: Pattern Checklist

Use this checklist when designing a new pipeline:

- [ ] **PipelineContext**: Centralized state management implemented
- [ ] **Dependency Injection**: Factory pattern for component creation
- [ ] **Phase-Based Orchestration**: Clear phase boundaries defined
- [ ] **Telemetry Heartbeat**: Progress tracking with metrics
- [ ] **Schema-Driven Config**: External configuration files
- [ ] **Multi-Stage Validation**: Validation at multiple stages
- [ ] **Error Catalog**: Standardized error codes
- [ ] **UI Contracts**: Backend contracts defined (if applicable)
- [ ] **Project Setup Validation**: Setup verification implemented
- [ ] **Initiation Integrity Layers (§3.9.1)**: User-input contract (file readable), environment/dependency probe, output-path validation, structured fail-fast error code
- [ ] **Foundation/Utility Separation**: Clear separation of concerns
- [ ] **Idempotency & Checkpointing**: Safe re-runs and resumability
- [ ] **Structured Logging & Correlation IDs**: Machine-parseable, traceable logs
- [ ] **Security Baseline**: Secrets management and input validation
- [ ] **Concurrency Model**: Explicit execution model documented
- [ ] **Standardized Engine I/O**: Independent engine execution with contracts

---

## 10. Appendix B: Success Criteria

A pipeline is considered to follow universal architecture when:

- ✅ PipelineContext implemented and integrated
- ✅ Dependency injection factories for key components
- ✅ Phase-based orchestration with clear checkpoints
- ✅ Telemetry heartbeat for progress tracking
- ✅ Schema-driven configuration externalized
- ✅ Multi-stage validation implemented
- ✅ Standardized error catalog with resolution guidance
- ✅ UI contracts defined (if applicable)
- ✅ Project setup validator implemented
- ✅ Initiation integrity layers present (user-input readability, env probe, output-path validation, structured fail-fast code) — see §3.9.1
- ✅ Foundation/utility separation established
- ✅ Idempotency & checkpointing for safe re-runs
- ✅ Structured logging with correlation IDs
- ✅ Security baseline (secrets management, input validation)
- ✅ Concurrency model documented and implemented
- ✅ Standardized engine I/O for independent execution
- ✅ Test coverage >90% for new components
- ✅ Performance impact <5% overhead
- ✅ Documentation updated with patterns

---

**End of Universal Pipeline Architecture Design**
