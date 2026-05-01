# Bootstrap Module — Function Reference & Call Graph

**Location:** `dcc/workflow/utility_engine/bootstrap.py`  
**Version:** Phase P4 Complete  
**Last Updated:** 2026-05-01

---

## 1. Module Overview

| Attribute | Value |
|:---|:---|
| **Module** | `utility_engine.bootstrap` |
| **Purpose** | Centralized pipeline initialization with phase tracking |
| **Classes** | `BootstrapError`, `BootstrapPhaseStatus`, `BootstrapManager` |
| **Total Functions** | 24 (3 public orchestrators, 17 private phases/helpers, 4 properties) |
| **Entry Points** | `bootstrap_all()`, `bootstrap_for_ui()` |
| **Exit Point** | `to_pipeline_context()` |

---

## 2. Function Table

### 2.1 Exception Class

| Function | Parameters (In) | Returns | Description | Error Handling |
|:---|:---|:---|:---|:---|
| `BootstrapError.__init__` | `code: str`, `message: str`, `phase: str` | `Exception` | Structured bootstrap error with phase context | Stores code, message, phase |
| `BootstrapError.to_system_error` | `self` | `Tuple[str, str]` | Returns (system_code, message) for `system_error_print()` | Converts to S-B-S format |

### 2.2 Data Class

| Function | Parameters (In) | Returns | Description | Error Handling |
|:---|:---|:---|:---|:---|
| `BootstrapPhaseStatus` (dataclass) | `phase_id: str`, `phase_name: str`, `status: str` (default), `start/end_time: Optional[str]`, `duration_ms: Optional[float]`, `error_code: Optional[str]` | `BootstrapPhaseStatus` | Immutable phase tracking record | None (dataclass) |

### 2.3 Public Orchestrator Methods

| Function | Parameters (In) | Returns | Description | Error Handling |
|:---|:---|:---|:---|:---|
| `BootstrapManager.__init__` | `base_path: Path` | `BootstrapManager` | Initialize with base path, init phase tracking | None (initialization) |
| `BootstrapManager.bootstrap_all` | `cli_args: Optional[Dict[str, Any]]` | `BootstrapManager` | CLI mode: Run all 8 phases P1-P8 | `BootstrapError` on failure |
| `BootstrapManager.bootstrap_for_ui` | `upload_file_name: str`, `output_folder: str`, `schema_file_name: Optional[str]`, `debug_mode: bool`, `nrows: Optional[int]`, `**additional_params` | `BootstrapManager` | UI mode: Run phases with UI overrides | `BootstrapError` on failure |
| `BootstrapManager.to_pipeline_context` | `self` | `PipelineContext` | Convert bootstrapped state to context | `BootstrapError` if not bootstrapped |

### 2.4 Phase Tracking Methods (Private)

| Function | Parameters (In) | Returns | Description | Called By |
|:---|:---|:---|:---|:---|
| `_initialize_phase_tracking` | `self` | `None` | Init 9 phase status objects | `__init__` |
| `_record_phase_start` | `phase_id: str` | `None` | Mark phase running, record start time | All phase methods |
| `_record_phase_complete` | `phase_id: str` | `None` | Mark complete, calc duration | All phase methods |
| `_record_phase_failure` | `phase_id: str`, `error_code: str` | `None` | Mark failed, store error | All phase methods on exception |

### 2.5 Bootstrap Phase Methods (Private)

| Function | Parameters (In) | Returns | Description | Error Codes |
|:---|:---|:---|:---|:---|
| `_bootstrap_cli` | `cli_args: Optional[Dict[str, Any]]` | `None` | Phase 1: Parse CLI, set debug mode | `B-CLI-001` |
| `_bootstrap_paths` | `self` | `None` | Phase 2: Validate base_path, home dir | `B-PATH-001`, `B-PATH-002` |
| `_bootstrap_registry` | `self` | `None` | Phase 3: Load ParameterTypeRegistry | `B-REG-001` (warning) |
| `_bootstrap_defaults` | `self` | `None` | Phase 4: Build native defaults | `B-DEFAULT-001` |
| `_bootstrap_fallback_validation` | `self` | `None` | Phase 5: Validate fallback files/dirs | `B-FALLBACK-001` (warning) |
| `_bootstrap_environment` | `self` | `None` | Phase 6: Test Python environment | `B-ENV-001`, `B-ENV-002` |
| `_bootstrap_schema` | `self` | `None` | Phase 7: Resolve schema path | `B-SCHEMA-001`, `B-SCHEMA-002` |
| `_bootstrap_parameters` | `self` | `None` | Phase 8a: Resolve effective params (CLI) | `B-PARAM-001` |
| `_bootstrap_parameters_for_ui` | `**ui_params` | `None` | Phase 8a (UI): Resolve params with overrides | `B-PARAM-002` |
| `_bootstrap_pre_pipeline_validation` | `self` | `None` | Phase 8b: Pre-pipeline input/output validation | `B-PRE-001` |

### 2.6 Trace Building Methods (Private)

| Function | Parameters (In) | Returns | Description | Error Codes |
|:---|:---|:---|:---|:---|
| `_build_preload_trace` | `self` | `None` | Build pre-context trace with phase data | `S-B-S-0603` |
| `_validate_pre_context_gate` | `self` | `None` | Validate trace before context creation | `S-B-S-0604` |
| `_build_postload_trace` | `paths: PipelinePaths` | `None` | Build post-context trace | Warning on failure |

### 2.7 Property Getters

| Property | Type | Description | Dependencies |
|:---|:---|:---|:---|
| `bootstrap_summary` | `Dict[str, Any]` | Dynamic status: phases complete, status, duration | `_phase_status`, `_bootstrap_start_time` |
| `is_bootstrapped` | `bool` | Check if bootstrap completed | `_bootstrapped` |
| `preload_trace` | `Dict[str, ContextTraceItem]` | Pre-context state trace | `_preload_trace` |
| `postload_trace` | `Optional[Dict[str, ContextTraceItem]]` | Post-context state trace | `_postload_trace` |

---

## 3. Function Call Graph (Mermaid)

### 3.1 Entry Points & Orchestration

```mermaid
flowchart TD
    subgraph Entry["Entry Points"]
        MAIN["main() in dcc_engine_pipeline.py"]
        UI["UI Entry Point"]
    end

    subgraph Init["Initialization"]
        BM["BootstrapManager(base_path)"]
        INIT["__init__()"]
        PHASE_INIT["_initialize_phase_tracking()"]
        P1_STATUS["P1_cli: BootstrapPhaseStatus"]
        P2_STATUS["P2_paths: BootstrapPhaseStatus"]
        P3_STATUS["P3_registry: BootstrapPhaseStatus"]
        P4_STATUS["P4_defaults: BootstrapPhaseStatus"]
        P5_STATUS["P5_fallback: BootstrapPhaseStatus"]
        P6_STATUS["P6_env: BootstrapPhaseStatus"]
        P7_STATUS["P7_schema: BootstrapPhaseStatus"]
        P8_STATUS["P8_params: BootstrapPhaseStatus"]
        P9_STATUS["P3_trace: BootstrapPhaseStatus"]
    end

    subgraph Orchestrate["Orchestrator Methods"]
        BOOT_ALL["bootstrap_all(cli_args)"]
        BOOT_UI["bootstrap_for_ui(...)"]
        TO_CTX["to_pipeline_context()"]
    end

    MAIN --> BM
    UI --> BM
    BM --> INIT
    INIT --> PHASE_INIT
    PHASE_INIT --> P1_STATUS & P2_STATUS & P3_STATUS & P4_STATUS & P5_STATUS & P6_STATUS & P7_STATUS & P8_STATUS & P9_STATUS
    
    MAIN --> BOOT_ALL
    UI --> BOOT_UI
    BOOT_ALL --> TO_CTX
    BOOT_UI --> TO_CTX
```

### 3.2 CLI Bootstrap Flow (bootstrap_all)

```mermaid
flowchart TD
    subgraph CLI_Phases["CLI Bootstrap Phases"]
        P1["_bootstrap_cli(cli_args)"]
        P2["_bootstrap_paths()"]
        P3["_bootstrap_registry()"]
        P4["_bootstrap_defaults()"]
        P5["_bootstrap_fallback_validation()"]
        P6["_bootstrap_environment()"]
        P7["_bootstrap_schema()"]
        P8["_bootstrap_parameters()"]
        P8B["_bootstrap_pre_pipeline_validation()"]
    end

    subgraph Trace_Building["Trace Building"]
        P3A["_build_preload_trace()"]
        P3B["_validate_pre_context_gate()"]
        P3C["_build_postload_trace(paths)"]
    end

    subgraph External["External Dependencies"]
        CLI["parse_cli_args()"]
        VAL["ValidationManager"]
        REG["get_parameter_registry()"]
        DEF["build_native_defaults()"]
        ENV["test_environment()"]
        SCH["default_schema_path()"]
        PARAM["resolve_effective_parameters()"]
        PLATFORM["resolve_platform_paths()"]
    end

    START(["bootstrap_all()"]) --> P1
    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P8B
    
    P1 -.->|calls| CLI
    P2 -.->|uses| VAL
    P3 -.->|calls| REG
    P4 -.->|calls| DEF
    P5 -.->|uses| VAL
    P6 -.->|calls| ENV
    P7 -.->|uses| VAL
    P8 -.->|calls| PARAM
    P8 -.->|calls| PLATFORM
    P8 -.->|uses| SCH
    
    P8B --> P3A --> P3B --> P3C
    P3C --> END(["return self"])
```

### 3.3 Phase Tracking Sequence

```mermaid
sequenceDiagram
    participant Caller as Phase Method
    participant PhaseStatus as BootstrapPhaseStatus
    participant Summary as bootstrap_summary
    participant Banner as Framework Banner

    Caller->>PhaseStatus: _record_phase_start(phase_id)
    PhaseStatus->>PhaseStatus: status = "running"
    PhaseStatus->>PhaseStatus: start_time = now()
    
    Note over Caller,PhaseStatus: Phase execution...
    
    alt Success
        Caller->>PhaseStatus: _record_phase_complete(phase_id)
        PhaseStatus->>PhaseStatus: status = "complete"
        PhaseStatus->>PhaseStatus: end_time = now()
        PhaseStatus->>PhaseStatus: duration_ms = calculated
    else Failure
        Caller->>PhaseStatus: _record_phase_failure(phase_id, error_code)
        PhaseStatus->>PhaseStatus: status = "failed"
        PhaseStatus->>PhaseStatus: end_time = now()
        PhaseStatus->>PhaseStatus: error_code = stored
        PhaseStatus->>PhaseStatus: duration_ms = calculated
    end
    
    Caller->>Summary: Access bootstrap_summary property
    Summary->>PhaseStatus: Read all phase statuses
    Summary->>Summary: Count complete/failed phases
    Summary->>Summary: Calculate total duration
    Summary-->>Caller: Return status dict
    
    Caller->>Banner: print_framework_banner(...)
    Banner->>Summary: Use summary["status"], summary["completed_count"]
    Banner-->>User: Display: "Bootstrap: 9 phases COMPLETE"
```

### 3.4 Phase Recording Timing

```mermaid
gantt
    title Bootstrap Phase Execution Timeline
    dateFormat HH:mm:ss.SSS
    axisFormat %S.%L
    
    section P1
    P1_cli           :a1, 00:00:00.000, 00:00:00.050
    
    section P2
    P2_paths         :a2, after a1, 00:00:00.120
    
    section P3
    P3_registry      :a3, after a2, 00:00:00.200
    
    section P4
    P4_defaults      :a4, after a3, 00:00:00.350
    
    section P5
    P5_fallback      :a5, after a4, 00:00:00.420
    
    section P6
    P6_env           :a6, after a5, 00:00:00.580
    
    section P7
    P7_schema        :a7, after a6, 00:00:00.650
    
    section P8
    P8_params        :a8, after a7, 00:00:00.800
    
    section Trace
    P3_trace         :a9, after a8, 00:00:00.900
```

### 3.5 Error Handling Flow

```mermaid
flowchart TD
    subgraph Phase_Method["Any Phase Method"]
        TRY["try block"]
        RECORD_START["_record_phase_start(phase_id)"]
        EXEC["Phase execution logic"]
        RECORD_COMPLETE["_record_phase_complete(phase_id)"]
        EXCEPT_BOOTSTRAP["except BootstrapError"]
        EXCEPT_GENERIC["except Exception"]
        RECORD_FAIL["_record_phase_failure(phase_id, error_code)"]
        RAISE["raise BootstrapError"]
        RERAISE["raise"]
    end

    subgraph Error_Types["Error Types"]
        E1["BootstrapError<br/>(phase-specific)"]
        E2["Unexpected Exception<br/>(wrap in BootstrapError)"]
    end

    START(["Method called"]) --> TRY
    TRY --> RECORD_START
    RECORD_START --> EXEC
    
    EXEC -->|Success| RECORD_COMPLETE
    EXEC -->|BootstrapError| EXCEPT_BOOTSTRAP
    EXEC -->|Other Exception| EXCEPT_GENERIC
    
    EXCEPT_BOOTSTRAP --> RECORD_FAIL
    EXCEPT_GENERIC --> RECORD_FAIL
    EXCEPT_GENERIC --> RAISE
    
    RECORD_FAIL --> RERAISE
    RECORD_COMPLETE --> END(["Return"])
    RERAISE --> END
    RAISE --> END
```

### 3.6 Complete Call Chain

```mermaid
flowchart LR
    subgraph Main_Pipeline["Main Pipeline"]
        M1["main()"]
        M2["setup_logger()"]
        M3["parse_cli_args()"]
        M4["print_framework_banner()"]
        M5["run_engine_pipeline()"]
    end

    subgraph Bootstrap_Module["Bootstrap Module"]
        B1["BootstrapManager"]
        B2["bootstrap_all()"]
        B3["bootstrap_for_ui()"]
        B4["to_pipeline_context()"]
        B5["Phase Methods"]
        B6["Phase Tracking"]
        B7["Trace Building"]
    end

    subgraph External_Modules["External Modules"]
        E1["utility_engine.cli"]
        E2["utility_engine.validation"]
        E3["core_engine.system"]
        E4["core_engine.paths"]
        E5["schema_engine"]
        E6["core_engine.context"]
    end

    M1 --> M2
    M1 --> M3
    M3 -->|cli_args| B1
    B1 --> B2
    B2 -->|phases| B5
    B5 -->|track| B6
    B5 -->|use| E1 & E2 & E3 & E4 & E5
    B2 -->|after phases| B7
    B2 --> B4
    B4 -->|create| E6
    B4 -->|uses| E4
    
    B2 -.->|summary| M4
    B4 -.->|context| M5
    
    B1 -.->|UI entry| B3
    B3 -->|phases| B5
```

---

## 4. External Dependencies

| Function | External Module | External Function | Purpose |
|:---|:---|:---|:---|
| `_bootstrap_cli` | `utility_engine.cli` | `parse_cli_args()` | Parse command line |
| `_bootstrap_paths` | `utility_engine.validation` | `ValidationManager` | Path validation |
| `_bootstrap_registry` | `utility_engine.validation` | `get_parameter_registry()` | Load registry |
| `_bootstrap_defaults` | `utility_engine.cli` | `build_native_defaults()` | Build defaults |
| `_bootstrap_fallback_validation` | `utility_engine.validation` | `ValidationManager.validate_paths_and_parameters()` | Validate files/dirs |
| `_bootstrap_environment` | `core_engine.system` | `test_environment()` | Check dependencies |
| `_bootstrap_schema` | `schema_engine` | `default_schema_path()` | Get default schema |
| `_bootstrap_parameters` | `utility_engine.cli` | `resolve_effective_parameters()` | Merge parameters |
| `_bootstrap_parameters` | `core_engine.paths` | `resolve_platform_paths()` | Resolve paths |
| `_build_preload_trace` | `core_engine.paths` | `resolve_output_paths()` | Get output paths |
| `to_pipeline_context` | `core_engine.context` | `PipelineContext.__init__()` | Create context |

---

## 5. File Cross-References

| This Module | Referenced By | Purpose |
|:---|:---|:---|
| `BootstrapManager` | `dcc_engine_pipeline.py` | CLI pipeline initialization |
| `BootstrapManager` | `run_engine_pipeline_with_ui()` | UI pipeline initialization |
| `BootstrapError` | `dcc_engine_pipeline.py` | Error handling in main() |
| `bootstrap_summary` | `print_framework_banner()` | Dynamic status display |

---

## 6. Version History

| Version | Date | Changes | Author |
|:---|:---|:---|:---|
| P1 | 2026-04-28 | Initial module creation | - |
| P2 | 2026-04-30 | Pipeline integration | - |
| P3 | 2026-05-01 | Context trace integration | - |
| P4 | 2026-05-01 | Phase tracking & dynamic summary | - |
| P4.1 | 2026-05-01 | Logger cleanup, function reference | - |

---

*Generated per agent_rule.md Section 10 — Function Table and Call Graph*
