# Appendix H — Bootstrap Module Design Summary

**Document ID**: WP-EKS-P1-APX-H  
**Version**: 0.4  
**Status**: ✅ COMPLETE  
**Date**: 2026-07-17  
**Author**: opencode  
**Summary**: Comprehensive design summary for the universal L19 BootstrapManager and its EKS wiring (I108–I117 / T1.99.50–T1.99.83). v0.4 adds I117: `_preload_infrastructure()` pure-stdlib guard, §H.12.1 Preload Infrastructure Guard section, updated §H.1/H.3/H.12, universal preload pattern note.

---

## H.1 Index

- [H.1 Index](#h1-index)
- [H.2 Overview & Architecture](#h2-overview--architecture)
- [H.3 File Inventory](#h3-file-inventory)
- [H.4 The 8-Phase Bootstrap Sequence](#h4-the-8-phase-bootstrap-sequence)
- [H.5 Phase Registry (Configurable)](#h5-phase-registry-configurable)
- [H.6 BootstrapError — Structured Exception](#h6-bootstraperror--structured-exception)
- [H.7 Universal BootstrapManager (L19)](#h7-universal-bootstrapmanager-l19)
- [H.8 EKSBootstrapManager — EKS-Specific Subclass](#h8-eksbootstrapmanager--eks-specific-subclass)
- [H.9 Pipeline Context & to_pipeline_context()](#h9-pipeline-context--to_pipeline_context)
- [H.10 Dual-Mode Bootstrap](#h10-dual-mode-bootstrap)
- [H.11 Error Code Catalog](#h11-error-code-catalog)
- [H.12 main() Integration in EKS](#h12-main-integration-in-eks)
  - [H.12.1 Preload Infrastructure Guard (I117)](#h121-preload-infrastructure-guard-i117)
- [H.13 Trace Building](#h13-trace-building)
- [H.14 Parameter Precedence Model](#h14-parameter-precedence-model)
- [H.15 Strategy Pattern — Injected Hooks](#h15-strategy-pattern--injected-hooks)
- [H.16 Test Coverage](#h16-test-coverage)
- [H.17 Design Decisions & Rationale](#h17-design-decisions--rationale)
- [H.18 Function List & I/O Table](#h18-function-list--io-table)
- [H.19 Function Details](#h19-function-details)

---

## H.2 Overview & Architecture

The bootstrap module (L19) is a **project-agnostic, stateful bootstrap orchestrator** extracted from DCC's mature `BootstrapManager` (~1223 lines, 8 phases). It lives in `common/library/bootstrap/` and is shared by EKS, DCC, and any future projects.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    common/library/bootstrap/              │
│  ┌─────────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ BootstrapManager │  │BootstrapErr│  │BootstrapPhase │  │
│  │   (manager.py)   │  │ (errors.py)│  │  Registry     │  │
│  │                  │  │            │  │  (phases.py)  │  │
│  │  8-phase exec    │  │ code+msg+  │  │               │  │
│  │  phase tracking  │  │  phase     │  │ configurable  │  │
│  │  traces          │  │ to_sys_err │  │ P1–P8 default │  │
│  │  dual-mode       │  │ to_dict()  │  │ fluent API    │  │
│  └────────┬─────────┘  └────────────┘  └───────────────┘  │
│           │                                               │
└───────────┼───────────────────────────────────────────────┘
            │  extends
┌───────────▼───────────────────────────────────────────────┐
│                 eks/engine/core/bootstrap.py               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              EKSBootstrapManager                      │  │
│  │                                                      │  │
│  │  Hooks: ConfigRegistry, ProjectSetupValidator,       │  │
│  │         parse_eks_cli, resolve_paths, detect_os,     │  │
│  │         ErrorManager, MessageManager                  │  │
│  │                                                      │  │
│  │  Overrides: _bootstrap_env (P6), _bootstrap_params   │  │
│  │             (P8), _run_readiness_gate, to_dict(),    │  │
│  │             to_pipeline_context() → EKSPipelineCtx   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Key Design Principles

| Principle | Implementation |
|-----------|---------------|
| **SSOT** | Single universal `BootstrapManager` in `common/library/` — EKS and DCC delegate, not duplicate |
| **Strategy Pattern** | Project-specific behavior injected via constructor callables (config loader, CLI parser, path resolver, etc.) |
| **Phase Tracking** | Every phase records start/end/duration/error via `BootstrapPhaseStatus` |
| **Fail-Fast** | Any phase failure raises `BootstrapError` with structured `(code, message, phase)` |
| **Dual-Mode** | CLI mode (`bootstrap_all(args)`) and UI mode (`bootstrap_for_ui(**params)`) |
| **Backward Compat** | `to_dict()` returns the same shape as the legacy `bootstrap_pipeline()` dict |

---

## H.3 File Inventory

### Universal (common/library/bootstrap/)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 29 | Exports `BootstrapManager`, `BootstrapError`, `BootstrapPhaseRegistry`, `BootstrapPhaseStatus` |
| `manager.py` | 780 | Universal `BootstrapManager` — stateful orchestrator with 8 phases, dual-mode, traces |
| `errors.py` | 67 | `BootstrapError(Exception)` — structured exception with `code`, `message`, `phase` |
| `phases.py` | 156 | `BootstrapPhaseRegistry` — configurable phase ordering; `BootstrapPhaseStatus` — per-phase tracking |
| `tests/test_bootstrap_manager.py` | 405 | 37 unit tests covering all classes and phases |

### EKS-Specific (eks/engine/core/)

| File | Lines | Purpose |
|------|-------|---------|
| `bootstrap.py` | 360 | `EKSBootstrapManager(BootstrapManager)` — EKS hook injection + phase overrides |
| `context.py` | 230 | `EKSPipelineContext`, `EKSPaths`, `EKSData`, `EKSState`, `EKSTelemetry` — L06 pipeline context |

### EKS Pipeline Entry

| File | Lines | Purpose |
|------|-------|---------|
| `eks_engine_pipeline.py` | ~800 | `main()` — full pipeline orchestration using `EKSBootstrapManager` chain; includes `_preload_infrastructure()` (I117) pure-stdlib guard (~130 lines) |
| `eks_engine_pipeline.py` | (same file) | `bootstrap_pipeline()` — thin backward-compat wrapper around `EKSBootstrapManager` |

---

## H.4 The 8-Phase Bootstrap Sequence

The default phase order mirrors DCC's mature P1–P8 sequence:

| Order | Phase ID | Phase Name | Method | Description |
|-------|----------|------------|--------|-------------|
| 1 | `P1_cli` | CLI Parsing | `_bootstrap_cli` | Parse CLI args (`sys.argv` or provided list), determine debug mode, populate `cli_args` and `parsed` |
| 2 | `P2_paths` | Path Validation | `_bootstrap_paths` | Validate `project_root` exists, resolve schema-driven canonical paths via injected `path_resolver` |
| 3 | `P3_registry` | Registry Loading | `_bootstrap_registry` | Load project config via injected `config_loader` (e.g., `ConfigRegistry` SSOT) |
| 4 | `P4_defaults` | Native Defaults Building | `_bootstrap_defaults` | Build native defaults from `config.global_paths` (data_dir, output_dir, etc.) |
| 5 | `P5_fallback` | Fallback Validation | `_bootstrap_fallback` | Validate fallback files and directories (project-specific; no-op in base) |
| 6 | `P6_env` | Environment Testing | `_bootstrap_env` | Detect OS via injected `os_detector`; test dependencies via injected `env_tester` (L20) — if `ready=False`, raises `BootstrapError("P1-BOOT-ENV", ...)` with missing-package guidance |
| 7 | `P7_schema` | Schema Resolution | `_bootstrap_schema` | Resolve schema paths and load schema definitions (project-specific; no-op in base) |
| 8 | `P8_params` | Parameters Resolution | `_bootstrap_params` | Merge CLI + Schema + Native into `effective_parameters` with precedence: CLI > Schema > Native |

### Phase Execution Flow

```
bootstrap_all(args) / bootstrap_for_ui(**params)
  │
  ├── P1_cli (CLI only)          ── parse args, detect debug mode
  ├── P2_paths                   ── validate root, resolve paths
  ├── P3_registry                ── load config via SSOT
  ├── P4_defaults                ── build native defaults
  ├── P5_fallback (CLI only)     ── validate fallbacks
  ├── P6_env                     ── detect OS + test dependencies (L20)
  ├── P7_schema                  ── resolve schemas
  ├── P8_params                  ── merge effective params
  │
  └── _bootstrapped = True
      return self
```

### Phase Tracking

Every phase execution goes through `_run_phase(phase_id, phase_fn)` which:
1. Calls `_record_phase_start(phase_id)` → marks `status = "running"`, records `start_time` (ISO 8601)
2. Executes `phase_fn()`
3. On success: calls `_record_phase_complete(phase_id)` → `status = "complete"`, records `end_time`, calculates `duration_ms`
4. On `BootstrapError`: calls `_record_phase_failure(phase_id, error_code)` → `status = "failed"`, records `error_code`
5. On unexpected `Exception`: wraps in `BootstrapError` with code `B-{phase_id}-ERR`

### Bootstrap Summary

`bootstrap_summary` property returns a dynamic dict:
```python
{
    "status": "complete" | "partial" | "failed" | "in_progress",
    "completed_count": int,       # phases with status == "complete"
    "total_count": int,           # total registered phases
    "failed_phase": str | None,   # first failed phase_id
    "error_code": str | None,     # error code of first failed phase
    "total_duration_ms": float,   # from bootstrap start to now
}
```

---

## H.5 Phase Registry (Configurable)

`BootstrapPhaseRegistry` provides configurable phase ordering with a fluent API.

### Default Phases

```python
_DEFAULT_PHASES = [
    PhaseEntry("P1_cli",      "CLI Parsing",              1, "_bootstrap_cli"),
    PhaseEntry("P2_paths",    "Path Validation",           2, "_bootstrap_paths"),
    PhaseEntry("P3_registry", "Registry Loading",          3, "_bootstrap_registry"),
    PhaseEntry("P4_defaults", "Native Defaults Building",  4, "_bootstrap_defaults"),
    PhaseEntry("P5_fallback", "Fallback Validation",       5, "_bootstrap_fallback"),
    PhaseEntry("P6_env",      "Environment Testing",       6, "_bootstrap_env"),
    PhaseEntry("P7_schema",   "Schema Resolution",         7, "_bootstrap_schema"),
    PhaseEntry("P8_params",   "Parameters Resolution",     8, "_bootstrap_params"),
]
```

### Fluent API

```python
# Register a custom phase
registry.register("P9_custom", "Custom Phase", 9, "_bootstrap_custom")

# Remove a phase (e.g., skip fallback for UI mode)
registry.remove("P5_fallback")

# Override an existing phase
registry.register("P1_cli", "Custom CLI", 10, "_custom_cli")
```

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `register(phase_id, name, order, method)` | `self` | Add/replace a phase |
| `remove(phase_id)` | `self` | Remove a phase |
| `get(phase_id)` | `PhaseEntry \| None` | Retrieve phase entry |
| `get_phase_name(phase_id)` | `str` | Human-readable name |
| `get_method(phase_id)` | `str` | Method name for the phase |
| `iter_ordered()` | `Iterator[PhaseEntry]` | Yield phases in ascending order |
| `build_phase_status()` | `Dict[str, BootstrapPhaseStatus]` | Build initial tracking dict |
| `phase_count` | `int` | Number of registered phases |
| `to_list()` | `List[dict]` | Serialize all phases |

---

## H.6 BootstrapError — Structured Exception

Located in `common/library/bootstrap/errors.py`. A structured exception carrying full bootstrap failure context.

### Class Definition

```python
class BootstrapError(Exception):
    def __init__(self, code: str, message: str, phase: str = "unknown"):
        self.code = code       # e.g. "P1-BOOT-READINESS", "B-CLI-001"
        self.message = message  # Human-readable description
        self.phase = phase      # Bootstrap phase name

    def to_system_error(self) -> Tuple[str, str]:
        """Return (code, message) tuple for ErrorManager consumption."""

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dict."""

    @classmethod
    def from_system_error(cls, code, message, phase) -> BootstrapError:
        """Reconstruct from (code, message) pair."""
```

### Error Code Format (Project-Prefix-Aware)

| Project | Prefix | Example | Registered In |
|---------|--------|---------|---------------|
| **EKS** | `P1-BOOT-*` | `P1-BOOT-READINESS` | `eks_error_config.json` |
| **DCC** | `S-*-S-*` | `S-A-S-0001` | DCC error catalog (legacy) |
| **Universal** | `B-*` | `B-CLI-001`, `B-PATH-001`, `B-CTX-001` | Built into manager |

### EKS-Specific P1-BOOT-* Codes

| Code | Name | Phase | Message |
|------|------|-------|---------|
| `P1-BOOT-READINESS` | `BOOT_READINESS_FAILED` | readiness | Bootstrap readiness gate failed — project setup not ready |
| `P1-BOOT-CONFIG` | `BOOT_CONFIG_FAILED` | config | Bootstrap config loading failed — unable to load project configuration |
| `P1-BOOT-PATHS` | `BOOT_PATHS_FAILED` | paths | Bootstrap path resolution failed — invalid or missing project paths |
| `P1-BOOT-OS` | `BOOT_OS_DETECTION_FAILED` | env | Bootstrap OS detection failed — unable to determine operating system |
| `P1-BOOT-ENV` | `BOOT_ENVIRONMENT_FAILED` | env | Bootstrap environment check failed — required dependencies missing; run "conda activate eks" |
| `P1-BOOT-CTX` | `BOOT_CONTEXT_FAILED` | context | Bootstrap context creation failed — must bootstrap before creating PipelineContext |

All 6 codes are:
- Severity: `FATAL`
- Category: `Bootstrap`
- `stops_pipeline: true`
- `promote_detail: true`
- Registered in `eks_error_config.json` under the `bootstrap_p1` range

---

## H.7 Universal BootstrapManager (L19)

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_root` | `Path` | **required** | Resolved project root path |
| `pipeline_root_dir` | `str` | `""` | Pipeline root directory (e.g. `"eks"`, `"dcc"`) |
| `pipeline_dir` | `str` | `""` | Pipeline entry folder (e.g. `"engine"`, `"workflow"`) |
| `config_loader` | `ConfigLoader` | `None` | Callable: `(Path) -> Dict` |
| `cli_parser` | `CliParser` | `None` | Callable: `(List[str]?) -> Any` |
| `path_resolver` | `PathResolver` | `None` | Callable: `(Path, Dict) -> Dict[str, Path]` |
| `readiness_validator_factory` | `ReadinessValidatorFactory` | `None` | Callable: `(**kwargs) -> Any` |
| `error_manager_factory` | `ErrorManagerFactory` | `None` | Callable: `(**kwargs) -> Any` |
| `message_manager_factory` | `MessageManagerFactory` | `None` | Callable: `(**kwargs) -> Any` |
| `os_detector` | `OsDetector` | `None` | Callable: `() -> str` |
| `env_tester` | `EnvTester` | `None` | Callable: `(Dict) -> Dict[str, Any]` — dependency checker (L20). Called in P6 after OS detection; if `ready=False`, raises `BootstrapError("B-ENV-002", ...)` |
| `phase_registry` | `BootstrapPhaseRegistry` | `None` | Custom phase registry (default: 8-phase DCC) |
| `logger` | `Any` | `None` | Logger instance |

### Type Aliases for Hooks

```python
ConfigLoader              = Callable[[Path], Dict[str, Any]]
CliParser                 = Callable[[Optional[List[str]]], Any]
PathResolver              = Callable[[Path, Dict[str, Any]], Dict[str, Path]]
ReadinessValidatorFactory = Callable[..., Any]
ErrorManagerFactory       = Callable[..., Any]
MessageManagerFactory     = Callable[..., Any]
OsDetector                = Callable[[], str]
EnvTester                 = Callable[[Dict[str, Any]], Dict[str, Any]]
```

### State Attributes (Populated During Bootstrap)

| Attribute | Type | Populated In | Description |
|-----------|------|-------------|-------------|
| `_bootstrapped` | `bool` | After all phases | Whether bootstrap completed successfully |
| `cli_args` | `Dict[str, Any]` | P1 | Parsed CLI arguments |
| `cli_overrides_provided` | `bool` | P1 | Whether CLI overrides were supplied |
| `debug_mode` | `bool` | P1 | Whether debug/trace mode is active |
| `os_info` | `str` | P6 | OS string (`"windows"`, `"linux"`, `"macos"`) |
| `_env_test_results` | `Dict[str, Any]` | P6 | Results from `env_tester` call (`{ready, errors, required_modules, optional_modules, engine_modules, python_version, platform}`) |
| `config` | `Dict[str, Any]` | P3 | Loaded project configuration |
| `doc_config` | `Dict[str, Any]` | P3 | Document-specific config |
| `config_dir` | `Path` | Constructor | Config directory path |
| `resolved_paths` | `Dict[str, Path]` | P2 | Canonical paths (data_dir, output_dir, etc.) |
| `effective_parameters` | `Dict[str, Any]` | P8 | Merged parameters (CLI > Schema > Native) |
| `native_defaults` | `Dict[str, Any]` | P4 | Defaults from config.global_paths |
| `error_manager` | `Any` | Lazy | ErrorManager instance |
| `message_manager` | `Any` | Lazy | MessageManager instance |
| `registry` | `Any` | P3 | Config registry |
| `validator` | `Any` | Readiness gate | Project setup validator |
| `parsed` | `Any` | P1 | Raw parsed CLI namespace |

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_bootstrapped` | `bool` | Whether bootstrap completed successfully |
| `bootstrap_summary` | `Dict` | Dynamic summary (status, counts, failed phase, duration) |
| `phase_status` | `Dict[str, BootstrapPhaseStatus]` | Per-phase tracking (read-only) |
| `preload_trace` | `Dict \| None` | Pre-context trace data (raises `BootstrapError` if not bootstrapped) |
| `postload_trace` | `Dict \| None` | Post-context trace data |

### Core Public Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `bootstrap_all(cli_args?)` | `self` | Run all 8 phases in CLI mode |
| `bootstrap_for_ui(**params)` | `self` | Run phases 2–8 in UI mode (skips CLI parsing) |
| `to_pipeline_context()` | `Any` | Build pipeline context (raises `BootstrapError` if not bootstrapped) |
| `to_dict()` | `Dict` | Backward-compatible dict matching legacy `bootstrap_pipeline()` shape |
| `_run_readiness_gate()` | `bool` | Run project-setup readiness validation |

---

## H.8 EKSBootstrapManager — EKS-Specific Subclass

Located in `eks/engine/core/bootstrap.py`. Extends `BootstrapManager` with EKS-specific hook injection.

### Constructor

```python
EKSBootstrapManager(
    project_root: Path,
    pipeline_root_dir="eks",
    pipeline_dir="engine",
    skip_readiness=False,
    debug=False,
    auto_create=True,
    use_config_registry=True,
    logger=None,
)
```

### Hook Mappings

| Universal Hook | EKS Implementation | Source |
|---------------|-------------------|--------|
| `os_detector` | `detect_os` (L12) | `common.library.core.paths.path_utils` |
| `env_tester` | `test_environment` (L20) | `common.library.core.system` |
| `path_resolver` | `resolve_paths` (L16) | `common.library.paths` |
| `config_loader` | `ConfigRegistry` SSOT (with `SchemaLoader` fallback) | `eks.engine.core.config_registry` / `schema_loader` |
| `cli_parser` | `parse_eks_cli` (L18) | `eks.engine.eks_engine_pipeline` |
| `readiness_validator_factory` | `ProjectSetupValidator` | `eks.engine.core.setup_validator` |
| `error_manager_factory` | `ErrorManager` (L10) | `eks.engine.core.error_manager` |
| `message_manager_factory` | `MessageManager` (L11) | `eks.engine.core.message_manager` |

### Phase Overrides

| Phase | Override | Reason |
|-------|----------|--------|
| **P6 (`_bootstrap_env`)** | Uses `detect_os()` for OS detection; then calls L20 `test_environment(deps)` via `env_tester` hook to verify all schema-driven dependencies; raises `P1-BOOT-ENV` with missing-package guidance ("Run: conda activate eks") if `ready=False` | EKS-specific OS detection + dependency testing with project-prefix error codes |
| **P8 (`_bootstrap_params`)** | EKS precedence: `level` resolved as CLI > Schema > Native with debug override; `data_dir` resolved as CLI > Schema (`resolve_paths`) > Native, anchored under `eks_root` | EKS-specific parameter merging and path anchoring |
| **Readiness Gate** | Uses `ProjectSetupValidator` with `skip_readiness` flag; raises `P1-BOOT-READINESS` | EKS-specific project setup validation |
| **`to_dict()`** | Lazy-inits `ErrorManager`/`MessageManager`, resolves `data_dir` from effective params | Backward-compat with legacy `bootstrap_pipeline()` callers |
| **`to_pipeline_context()`** | Returns `EKSPipelineContext` (L06 subclass) with `EKSPaths`, `EKSData`, `EKSState`, `EKSTelemetry` | EKS-specific context with schema/config registries |

### ConfigRegistry Singleton Handling

`_eks_config_loader` handles the `ConfigRegistry` singleton pattern:
- Resets singleton if `config_dir` changes between calls
- Falls back to `SchemaLoader` if `ConfigRegistry` fails or `use_config_registry=False`

---

## H.9 Pipeline Context & to_pipeline_context()

### Context Data Classes (eks/engine/core/context.py)

```
EKSPipelineContext (extends BasePipelineContext, L06)
├── paths: EKSPaths
│   ├── data_dir: Path
│   ├── schema_dir: Path
│   ├── output_dir: Path
│   ├── archive_dir: Path
│   ├── config_dir: Path
│   └── log_dir: Path
├── data: EKSData
│   ├── documents: Dict
│   ├── extracted_content: Dict
│   └── metadata: Dict
├── parameters: Dict[str, Any]  (includes config, doc_config, em, mm)
├── state: EKSState
│   ├── status: str ("INITIALIZED" → "COMPLETE" / "FAILED")
│   ├── documents_processed/succeeded/failed: int
│   ├── current_phase: str
│   └── start_time / end_time: datetime
├── telemetry: EKSTelemetry
│   ├── checkpoints: Dict
│   ├── performance_metrics: Dict
│   └── error_counts: Dict
├── schema_registry: Optional[Any]
└── config_registry: Optional[Any]
```

### to_pipeline_context() Flow

```
EKSBootstrapManager.to_pipeline_context()
  │
  ├── Guard: _bootstrapped == True (else raise P1-BOOT-CTX)
  │
  ├── Build EKSPaths from resolved_paths
  ├── Build EKSData (empty)
  ├── Build EKSState (status="INITIALIZED", start_time=now)
  ├── Build EKSTelemetry (empty)
  ├── Build parameters from effective_parameters + config + managers
  ├── Lazy-init ErrorManager / MessageManager if not created
  │
  ├── Construct EKSPipelineContext
  ├── _build_postload_trace(ctx)
  └── return ctx
```

### Context Gating

- `to_pipeline_context()` raises `P1-BOOT-CTX` (EKS) / `B-CTX-001` (universal) if `_bootstrapped == False`
- `preload_trace` property raises `B-BOOT-0601` if not bootstrapped
- These gates enforce the contract: **bootstrap must complete before context is available**

---

## H.10 Dual-Mode Bootstrap

### CLI Mode: `bootstrap_all(cli_args?)`

```
bootstrap_all(args) → self
  Phases: P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8
  Use case: console_scripts entry point, CLI invocation
  P1 parses sys.argv or provided list
  P5 (fallback) is included
```

### UI Mode: `bootstrap_for_ui(**params)`

```
bootstrap_for_ui(debug_mode=True, upload_file="test.xlsx", ...) → self
  Phases: P2 → P3 → P4 → P6 → P7 → P8 (skips P1, P5)
  Use case: HTTP backend, interactive UI
  UI params set directly as cli_args (skip CLI parsing)
  P5 (fallback) is skipped
  P8 uses _bootstrap_params_for_ui(**ui_params) — UI values get highest precedence
```

### Differences

| Aspect | CLI Mode | UI Mode |
|--------|----------|---------|
| Entry method | `bootstrap_all(args)` | `bootstrap_for_ui(**params)` |
| CLI parsing (P1) | ✅ | ❌ Skipped |
| Fallback validation (P5) | ✅ | ❌ Skipped |
| Parameter source | `sys.argv` / provided list | `**kwargs` from caller |
| Precedence | CLI > Schema > Native | UI > Schema > Native |

---

## H.11 Error Code Catalog

### Universal Error Codes (B-*)

Built into `BootstrapManager` for any project:

| Code | Phase | Condition |
|------|-------|-----------|
| `B-CLI-001` | P1 (cli) | CLI parsing failed |
| `B-PATH-001` | P2 (paths) | Project root does not exist |
| `B-PATH-002` | P2 (paths) | Path validation failed (unexpected) |
| `B-REG-001` | P3 (registry) | Registry loading failed |
| `B-DEF-001` | P4 (defaults) | Defaults building failed |
| `B-FALL-001` | P5 (fallback) | Fallback validation failed |
| `B-ENV-001` | P6 (env) | Environment testing failed |
| `B-SCH-001` | P7 (schema) | Schema resolution failed |
| `B-PAR-001` | P8 (params) | Parameters resolution failed (CLI) |
| `B-PAR-002` | P8 (params) | Parameters resolution failed (UI) |
| `B-BOOT-0601` | traces | Accessing preload_trace before bootstrap |
| `B-CTX-001` | context | Calling to_pipeline_context() before bootstrap |
| `B-UNK-001` | unknown | Unexpected error in bootstrap_all() |
| `B-UNK-002` | unknown | Unexpected error in bootstrap_for_ui() |
| `B-{phase_id}-ERR` | any | Phase raised non-BootstrapError exception |

### EKS-Specific Error Codes (P1-BOOT-*)

Registered in `eks/config/schemas/eks_error_config.json` under `bootstrap_p1` range:

| Code | Name | Category | Severity | stops_pipeline |
|------|------|----------|----------|----------------|
| `P1-BOOT-READINESS` | `BOOT_READINESS_FAILED` | Bootstrap | FATAL | true |
| `P1-BOOT-CONFIG` | `BOOT_CONFIG_FAILED` | Bootstrap | FATAL | true |
| `P1-BOOT-PATHS` | `BOOT_PATHS_FAILED` | Bootstrap | FATAL | true |
| `P1-BOOT-OS` | `BOOT_OS_DETECTION_FAILED` | Bootstrap | FATAL | true |
| `P1-BOOT-ENV` | `BOOT_ENVIRONMENT_FAILED` | Bootstrap | FATAL | true |
| `P1-BOOT-CTX` | `BOOT_CONTEXT_FAILED` | Bootstrap | FATAL | true |

### Error Manager Integration

`BootstrapError.to_system_error()` returns `(code, message)` tuple, compatible with:
- DCC's `system_error_print(code, message)`
- L10 `BaseErrorManager.handle_system_error()`

---

## H.12 main() Integration in EKS

The `main()` function in `eks/engine/eks_engine_pipeline.py` implements the full DCC-faithful orchestration chain:

```
main(args?)
  │
  ├── 0. _preload_infrastructure(args, ...)           # T1.99.81 (I117) — pure-stdlib guard
  │      ├── _parse_early_verbosity(args)             # stdlib-only --level/--debug parse
  │      ├── try: import path_utils                   # → safe_posix, should_auto_create_folders
  │      ├── try: import root_discovery               # → discover_project_root (or cwd fallback)
  │      ├── try: import logging                      # → UniversalLogger
  │      ├── try: import core.pipeline                # → TelemetryHeartbeat
  │      └── return infra dict with "ready" gate      # all errors collected → stderr with FATAL:
  │
  ├── 1. UniversalLogger + TelemetryHeartbeat         # T1.99.71–72 — from infra dict (already loaded)
  │
  ├── 2. discover_project_root("eks", "engine")       # L17 entry-point discovery (from infra dict)
  │
  ├── 3. EKSBootstrapManager(project_root=prj, ...)   # Create EKS bootstrap
  ├── 4. mgr.bootstrap_all(args)                      # Run all 8 phases
  │      └── P6: detect_os() + test_environment()     # L20 — first common.library call path
  │
  ├── 5. Extract results from mgr:
  │      parsed, os_info, level, data_dir, project_root,
  │      config_dir, resolved, mm
  │
  ├── 6. mm.show("STATUS_PIPELINE_START")             # L11 entry milestone
  │
  ├── 7. ctx = mgr.to_pipeline_context()              # T1.99.60 — collapsed ~30 lines
  │
  ├── 8. EngineInput from ctx.paths                   # T1.99.61 — L08 run contract (deferred import)
  │
  ├── 9. result = run_pipeline(                       # T1.99.59 — pass context
  │         project_root, data_dir, recursive,
  │         config_dir, logger, skip_readiness=True,
  │         debug, phase, auto_create, context=ctx)
  │
  ├── 10. EngineOutput contract                       # L08 structured output
  │       - status: "SUCCESS" | "FAILED"
  │       - telemetry: resolved paths
  │       - checkpoint_state: last completed phase
  │
  ├── 11. Output: json (--json) or human summary
  │
  └── return 0 | 1 (sys.exit compatible)
```

### Lazy-Import Design (T1.99.80 v2)

Module-level imports are **stdlib only** (`argparse`, `json`, `sys`, `uuid`, `pathlib`, `typing`). ALL `common.library` imports are deferred to inside functions:
- `safe_posix`, `should_auto_create_folders`, `discover_project_root`, `UniversalLogger`, `TelemetryHeartbeat` → inside `main()`
- `EngineInput`, `EngineOutput` → inside `main()` try block
- `PipelineOrchestrator`, `DocumentRegistry` → inside `run_pipeline()`
- `build_parser_from_schema` → inside `build_schema_driven_parser()`
- `parse_cli_args` → inside `parse_eks_cli()`
- `ConfigRegistry`, `SchemaLoader` → inside `_read_system_params()`
- Module-level `_PRJ_DIR` discovery: guarded try/except with deferred import

The first `common.library` call path is `test_environment()` in bootstrap P6, ensuring all missing dependencies are reported with friendly guidance before any heavy imports are attempted.

### Error Handling in main()

- Bootstrap failures raise `BootstrapError` with `P1-BOOT-*` codes (propagated from `bootstrap_all()`)
- Top-level `except Exception` catches pipeline failures
- Errors logged via `UniversalLogger.error()` and printed to `stderr`
- Returns exit code 1 on failure

### H.12.1 Preload Infrastructure Guard (I117)

**Problem (Chicken-and-Egg)**: Before bootstrap's `test_environment()` (P6) runs, `main()` needs `UniversalLogger`, `TelemetryHeartbeat`, and `discover_project_root()` from `common.library`. If `common.library` isn't importable (missing from `PYTHONPATH`), the bare `ImportError` reaches the user before bootstrap's friendly dependency guidance. But `test_environment()` itself lives in `common.library` — circular dependency.

**Solution**: `_preload_infrastructure()` — a **module-level pure-stdlib function** in `eks/engine/eks_engine_pipeline.py` that individually try/except-guards all 4 `common.library` import groups:

```
_preload_infrastructure(args, pipeline_root_dir, pipeline_dir, logger_name)
  │
  ├── 1. _parse_early_verbosity(args)           # stdlib-only argparse (--level/--debug)
  │
  ├── 2. try: import common.library.core.paths  # → safe_posix, should_auto_create_folders
  │      except ImportError → collect error
  │
  ├── 3. try: import common.library.paths.root_discovery  # → discover_project_root
  │      except ImportError → collect error; project_root = Path.cwd()
  │
  ├── 4. try: import common.library.logging      # → UniversalLogger
  │      except ImportError → collect error
  │
  ├── 5. try: import common.library.core.pipeline # → TelemetryHeartbeat
  │      except ImportError → collect error
  │
  └── return {
        "ready": bool,          # all imports succeeded
        "errors": List[str],    # collected error messages (printed to stderr with FATAL: prefix)
        "logger": logger,       # UniversalLogger or None
        "heartbeat": hb,        # TelemetryHeartbeat or None
        "project_root": Path,   # resolved or Path.cwd() fallback
        "early_level": int,     # parsed verbosity level (0–3)
        "debug_mode": bool,     # --debug flag
        "safe_posix": fn,       # or None
        "should_auto_create_folders": fn,  # or None
      }
```

**main() Integration**:

```
main(args?)
  │
  ├── 0.   pipeline_root_dir = "eks"; pipeline_dir = "engine"   # locals (I104)
  │
  ├── 0.5. infra = _preload_infrastructure(args, ...)           # I117 — pure-stdlib guard
  ├── 0.6. if not infra["ready"]: print errors → return 1      # ALL errors reported at once
  │
  ├── 1.   logger = infra["logger"]; hb = infra["heartbeat"]    # pre-loaded infrastructure
  ├── 2.   project_root = infra["project_root"]                # resolved or cwd fallback
  │
  ├── 3.   EKSBootstrapManager(project_root=prj, logger=logger)
  ├── 4.   mgr.bootstrap_all(args)
  │        └── P6: test_environment()  ← first common.library call path after guard
  ...
```

**Key Properties**:
- **Pure stdlib**: No imports beyond `argparse`, `sys`, `pathlib`, `typing` — cannot itself fail to import
- **No circular dependency**: Lives in the pipeline file (not in `common.library`), so it can guard `common.library` imports
- **Universal preload pattern**: Each pipeline project replicates the same structure with its own `pipeline_root_dir`/`pipeline_dir` literals — NOT extracted to `common.library` (would be circular)
- **All errors at once**: Errors collected in a list and reported together with `FATAL:` prefix to stderr; exit code 1
- **Graceful degradation**: `project_root` falls back to `Path.cwd()` if `discover_project_root` fails; `logger`/`heartbeat`/`safe_posix`/`should_auto_create_folders` are `None` on failure

**DCC Comparison**: DCC does NOT have this pattern yet — it has module-level `from common.library.*` imports (same vulnerability). The universal preload pattern is documented for future DCC adoption.

---

## H.13 Trace Building

Two trace snapshots are captured for debugging and observability:

### Preload Trace (`_build_preload_trace()`)

Built after bootstrap completes, before context creation:
```python
{
    "project_root": str,
    "config_dir": str,
    "phase_status": {phase_id: status, ...},   # per-phase status
    "bootstrap_summary": {...},                 # full summary
}
```

### Postload Trace (`_build_postload_trace(context)`)

Built after `to_pipeline_context()`:
```python
{
    "context_type": "EKSPipelineContext" | "dict",
    "resolved_paths": {name: str_path, ...},
    "effective_parameters": {...},
}
```

Access via:
- `mgr.preload_trace` — raises `B-BOOT-0601` if not bootstrapped
- `mgr.postload_trace` — `None` if `to_pipeline_context()` not yet called

---

## H.14 Parameter Precedence Model

### Priority Chain (CLI Mode)

```
CLI args  >  Schema params (system_parameters)  >  Native defaults (global_paths)
```

### Priority Chain (UI Mode)

```
UI params  >  Schema params (system_parameters)  >  Native defaults (global_paths)
```

### EKS-Specific P8 Resolution

```
level:
  CLI --level      >  Schema log_level  >  Native (1)
  CLI --debug      →  level = 3 (trace)

data_dir:
  CLI --data-dir   >  Schema resolve_paths  >  Native data_dir
  CLI absolute     →  use as-is
  CLI relative     →  anchor under project_root / eks_root

Other params:
  CLI args  >  Schema system_parameters  >  Native defaults
```

---

## H.15 Strategy Pattern — Injected Hooks

The universal `BootstrapManager` stays project-agnostic by accepting all project-specific behavior as constructor callables:

```
┌─────────────────────────────────────────────────────────┐
│                   BootstrapManager                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ config_loader │  │  cli_parser  │  │ path_resolver │  │
│  │ (Path)→Dict   │  │ (List?)→Any  │  │ (Path,Dict)   │  │
│  │               │  │              │  │   →Dict[Path] │  │
│  └──────┬────────┘  └──────┬───────┘  └──────┬────────┘  │
│         │                  │                  │           │
│  ┌──────▼────────┐  ┌──────▼───────┐  ┌──────▼────────┐  │
│  │readiness_val  │  │error_mgr_fact│  │msg_mgr_factory│  │
│  │ (**kw)→Any    │  │ (**kw)→Any   │  │ (**kw)→Any    │  │
│  └───────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  ┌──────────────┐                                       │
│  │ os_detector  │                                       │
│  │ ()→str       │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
         ▲                              ▲
         │ EKS hooks                    │ DCC hooks
         │                              │
┌────────┴──────────────┐  ┌────────────┴──────────────┐
│ EKSBootstrapManager   │  │ DCC BootstrapManager       │
│                       │  │ (future)                   │
│ ConfigRegistry        │  │ DCC config loader          │
│ parse_eks_cli         │  │ DCC CLI parser             │
│ resolve_paths (L16)   │  │ DCC path resolver          │
│ ProjectSetupValidator │  │ DCC readiness validator    │
│ detect_os (L12)       │  │ DCC OS detector            │
│ ErrorManager (L10)    │  │ DCC error manager          │
│ MessageManager (L11)  │  │ DCC message manager        │
└───────────────────────┘  └────────────────────────────┘
```

---

## H.16 Test Coverage

### Universal Tests (37 tests in `common/library/bootstrap/tests/`)

| Test Class | Count | Coverage |
|-----------|-------|----------|
| `TestBootstrapError` | 4 | `__init__`, `to_system_error()`, `to_dict()`, `from_system_error()` |
| `TestBootstrapPhaseRegistry` | 9 | Default phases, get, register, remove, build_phase_status, phase_count, to_list, ordering |
| `TestBootstrapManager` | 16 | Constructor, phase tracking, bootstrap_all, bootstrap_summary, is_bootstrapped, preload_trace gate, to_pipeline_context gate, to_pipeline_context after bootstrap, to_dict backward-compat, mock hooks, bootstrap_for_ui, readiness gate, phase wrapping, phase_status read-only |
| `TestBootstrapManagerPhases` | 8 | P2 missing root, P2 with resolver, P3 with loader, P6 with detector, P8 precedence, bootstrap_all returns self, UI mode with/without params |

### EKS Pipeline Tests (29 tests in `eks/test/`)

Including 6 bootstrap-specific tests:
- `test_bootstrap_readiness_failure_raises_bootstrap_error`
- `test_bootstrap_error_has_code_and_phase`
- `test_bootstrap_error_to_system_error`
- `test_bootstrap_error_to_dict`
- `test_bootstrap_error_from_system_error`
- `test_bootstrap_error_registered_in_catalog`

**Total**: 66/66 tests pass (37 universal + 29 EKS pipeline)

---

## H.17 Design Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **Extract from DCC, don't rewrite** | DCC's `BootstrapManager` (~1223 lines) is mature and battle-tested. Extracting the universal core avoids regressions. |
| **Strategy pattern for hooks** | Each project (EKS, DCC) has different config loading, CLI parsing, and validation logic. Callable injection keeps the universal manager clean. |
| **Phase registry is configurable** | Projects can add, remove, or reorder phases. UI mode naturally skips P1 and P5. |
| **Dual-mode (CLI + UI)** | Both entry paths exist in production: `console_scripts` for CLI, HTTP backend for UI. They share the same bootstrap core. |
| **Backward-compatible `to_dict()`** | Existing callers (`phase1_server.py`, tests) depend on the legacy dict shape. `to_dict()` preserves this contract without breaking changes. |
| **Structured `BootstrapError`** | `(code, message, phase)` tuple provides full context for error managers. `to_system_error()` bridges to DCC's legacy `system_error_print()`. |
| **Project-prefix error codes** | EKS uses `P1-BOOT-*` registered in `eks_error_config.json`; universal codes use `B-*`. Each project's error catalog is the SSOT. |
| **Lazy manager initialization** | `ErrorManager` and `MessageManager` are created lazily (on first `to_dict()` or `to_pipeline_context()` call) to avoid circular imports and unnecessary instantiation. |
| **ConfigRegistry singleton reset** | When `config_dir` changes between bootstrap calls, the singleton is reset to avoid stale config. |
| **Traces for debugging** | Preload and postload traces capture system state at two critical points, enabling RCA without re-running bootstrap. |
| **`_bootstrapped` gate** | `to_pipeline_context()` and `preload_trace` raise if bootstrap hasn't completed — enforces the contract programmatically. |

---

## H.18 Function List & I/O Table

Per AGENTS.md §14.7–§14.8 and §17, this section catalogs every function across all bootstrap-related files with their signatures, parameters, return values, calling sequence, error handling, and dependencies.

### H.18.1 Module Map

| Module | File | Purpose |
|--------|------|---------|
| `common.library.bootstrap` | `__init__.py` | Package exports |
| `common.library.bootstrap.errors` | `errors.py` | `BootstrapError` exception class |
| `common.library.bootstrap.phases` | `phases.py` | `BootstrapPhaseRegistry` + `BootstrapPhaseStatus` |
| `common.library.bootstrap.manager` | `manager.py` | Universal `BootstrapManager` orchestrator |
| `eks.engine.core.bootstrap` | `bootstrap.py` | EKS-specific `EKSBootstrapManager` subclass |
| `eks.engine.core.context` | `context.py` | `EKSPipelineContext` + path/data/state/telemetry dataclasses |
| `eks.engine.eks_engine_pipeline` | `eks_engine_pipeline.py` | `main()` entry point + `bootstrap_pipeline()` wrapper |

### H.18.2 Function Index (by Module)

#### A. `common.library.bootstrap.errors` — BootstrapError

| # | Function | Type | Signature |
|---|----------|------|-----------|
| A1 | `BootstrapError.__init__` | method | `(self, code: str, message: str, phase: str = "unknown") -> None` |
| A2 | `BootstrapError.to_system_error` | method | `(self) -> Tuple[str, str]` |
| A3 | `BootstrapError.to_dict` | method | `(self) -> dict` |
| A4 | `BootstrapError.from_system_error` | classmethod | `(cls, code: str, message: str, phase: str = "unknown") -> BootstrapError` |

#### B. `common.library.bootstrap.phases` — BootstrapPhaseRegistry & BootstrapPhaseStatus

| # | Function | Type | Signature |
|---|----------|------|-----------|
| B1 | `BootstrapPhaseRegistry.__init__` | method | `(self) -> None` |
| B2 | `BootstrapPhaseRegistry.register` | method | `(self, phase_id: str, phase_name: str, order: int, method: str = "") -> BootstrapPhaseRegistry` |
| B3 | `BootstrapPhaseRegistry.remove` | method | `(self, phase_id: str) -> BootstrapPhaseRegistry` |
| B4 | `BootstrapPhaseRegistry.get` | method | `(self, phase_id: str) -> Optional[PhaseEntry]` |
| B5 | `BootstrapPhaseRegistry.get_phase_name` | method | `(self, phase_id: str) -> str` |
| B6 | `BootstrapPhaseRegistry.iter_ordered` | method | `(self) -> Iterator[PhaseEntry]` |
| B7 | `BootstrapPhaseRegistry.get_method` | method | `(self, phase_id: str) -> str` |
| B8 | `BootstrapPhaseRegistry.build_phase_status` | method | `(self) -> Dict[str, BootstrapPhaseStatus]` |
| B9 | `BootstrapPhaseRegistry.phase_count` | property | `-> int` |
| B10 | `BootstrapPhaseRegistry.to_list` | method | `(self) -> List[Dict[str, Any]]` |

#### C. `common.library.bootstrap.manager` — Universal BootstrapManager

| # | Function | Type | Visibility | Signature |
|---|----------|------|------------|-----------|
| C1 | `BootstrapManager.__init__` | method | public | `(self, project_root: Path, *, pipeline_root_dir="", pipeline_dir="", config_loader=None, cli_parser=None, path_resolver=None, readiness_validator_factory=None, error_manager_factory=None, message_manager_factory=None, os_detector=None, phase_registry=None, logger=None) -> None` |
| C2 | `BootstrapManager._record_phase_start` | method | internal | `(self, phase_id: str) -> None` |
| C3 | `BootstrapManager._record_phase_complete` | method | internal | `(self, phase_id: str) -> None` |
| C4 | `BootstrapManager._record_phase_failure` | method | internal | `(self, phase_id: str, error_code: str) -> None` |
| C5 | `BootstrapManager.bootstrap_summary` | property | public | `-> Dict[str, Any]` |
| C6 | `BootstrapManager.is_bootstrapped` | property | public | `-> bool` |
| C7 | `BootstrapManager.preload_trace` | property | public | `-> Optional[Dict[str, Any]]` |
| C8 | `BootstrapManager.postload_trace` | property | public | `-> Optional[Dict[str, Any]]` |
| C9 | `BootstrapManager.phase_status` | property | public | `-> Dict[str, BootstrapPhaseStatus]` |
| C10 | `BootstrapManager.bootstrap_all` | method | public | `(self, cli_args: Optional[List[str]] = None) -> BootstrapManager` |
| C11 | `BootstrapManager.bootstrap_for_ui` | method | public | `(self, **ui_params: Any) -> BootstrapManager` |
| C12 | `BootstrapManager.to_pipeline_context` | method | public | `(self) -> Any` |
| C13 | `BootstrapManager._build_context` | method | internal (override) | `(self) -> Any` |
| C14 | `BootstrapManager.to_dict` | method | public | `(self) -> Dict[str, Any]` |
| C15 | `BootstrapManager._bootstrap_cli` | method | internal (P1) | `(self, cli_args: Optional[List[str]] = None) -> None` |
| C16 | `BootstrapManager._bootstrap_paths` | method | internal (P2) | `(self) -> None` |
| C17 | `BootstrapManager._bootstrap_registry` | method | internal (P3) | `(self) -> None` |
| C18 | `BootstrapManager._bootstrap_defaults` | method | internal (P4) | `(self) -> None` |
| C19 | `BootstrapManager._bootstrap_fallback` | method | internal (P5) | `(self) -> None` |
| C20 | `BootstrapManager._bootstrap_env` | method | internal (P6) | `(self) -> None` |
| C21 | `BootstrapManager._bootstrap_schema` | method | internal (P7) | `(self) -> None` |
| C22 | `BootstrapManager._bootstrap_params` | method | internal (P8) | `(self) -> None` |
| C23 | `BootstrapManager._bootstrap_params_for_ui` | method | internal (P8-UI) | `(self, **ui_params: Any) -> None` |
| C24 | `BootstrapManager._run_readiness_gate` | method | internal (override) | `(self) -> bool` |
| C25 | `BootstrapManager._build_preload_trace` | method | internal | `(self) -> None` |
| C26 | `BootstrapManager._build_postload_trace` | method | internal | `(self, context: Any) -> None` |
| C27 | `BootstrapManager._run_phase` | method | internal | `(self, phase_id: str, phase_fn: Callable[[], None]) -> None` |
| C28 | `BootstrapManager._log` | method | internal | `(self, msg: str, level: int = 1) -> None` |

#### D. `eks.engine.core.bootstrap` — EKSBootstrapManager

| # | Function | Type | Visibility | Signature |
|---|----------|------|------------|-----------|
| D1 | `EKSBootstrapManager.__init__` | method | public | `(self, project_root: Path, *, pipeline_root_dir="eks", pipeline_dir="engine", skip_readiness=False, debug=False, auto_create=True, use_config_registry=True, logger=None) -> None` |
| D2 | `EKSBootstrapManager._eks_path_resolver` | method | internal | `(self, project_root: Path, config: Dict[str, Any]) -> Dict[str, Path]` |
| D3 | `EKSBootstrapManager._eks_config_loader` | method | internal | `(self, config_dir: Path) -> Dict[str, Any]` |
| D4 | `EKSBootstrapManager._eks_cli_parser` | method | internal | `(self, args: Optional[List[str]] = None) -> Any` |
| D5 | `EKSBootstrapManager._eks_readiness_factory` | method | internal | `(self, **kwargs) -> Any` |
| D6 | `EKSBootstrapManager._eks_error_factory` | method | internal | `(self, **kwargs) -> Any` |
| D7 | `EKSBootstrapManager._eks_message_factory` | method | internal | `(self, **kwargs) -> Any` |
| D8 | `EKSBootstrapManager._bootstrap_env` | method | internal (P6 override) | `(self) -> None` |
| D9 | `EKSBootstrapManager._bootstrap_params` | method | internal (P8 override) | `(self) -> None` |
| D10 | `EKSBootstrapManager._run_readiness_gate` | method | internal (override) | `(self) -> bool` |
| D11 | `EKSBootstrapManager.to_dict` | method | public (override) | `(self) -> Dict[str, Any]` |
| D12 | `EKSBootstrapManager.to_pipeline_context` | method | public (override) | `(self) -> Any` |

#### E. `eks.engine.core.context` — EKSPipelineContext

| # | Function | Type | Signature |
|---|----------|------|-----------|
| E1 | `EKSPaths.to_dict` | method | `(self) -> Dict[str, str]` |
| E2 | `EKSData.to_dict` | method | `(self) -> Dict[str, Any]` |
| E3 | `EKSState.to_dict` | method | `(self) -> Dict[str, Any]` |
| E4 | `EKSTelemetry.add_checkpoint` | method | `(self, phase: str, timestamp: datetime, details: Dict[str, Any]) -> None` |
| E5 | `EKSTelemetry.record_metric` | method | `(self, name: str, value: float) -> None` |
| E6 | `EKSTelemetry.record_error` | method | `(self, error_type: str) -> None` |
| E7 | `EKSTelemetry.to_dict` | method | `(self) -> Dict[str, Any]` |
| E8 | `EKSPipelineContext.__post_init__` | method | `(self) -> None` |
| E9 | `EKSPipelineContext.to_dict` | method | `(self) -> Dict[str, Any]` |
| E10 | `EKSPipelineContext._from_dict` | classmethod | `(cls, data: Dict[str, Any]) -> EKSPipelineContext` |
| E11 | `EKSPipelineContext.update_phase` | method | `(self, phase: str, status: str = "IN_PROGRESS") -> None` |
| E12 | `EKSPipelineContext.complete` | method | `(self) -> None` |
| E13 | `EKSPipelineContext.fail` | method | `(self, error_message: str) -> None` |

#### F. `eks.engine.eks_engine_pipeline` — Entry Points

| # | Function | Type | Signature |
|---|----------|------|-----------|
| F1 | `bootstrap_pipeline` | function | `(project_root: Path, args: Optional[list] = None, logger: Any = None, skip_readiness: bool = False, debug: bool = False, use_config_registry: bool = True, auto_create: bool = True) -> Dict[str, Any]` |
| F2 | `main` | function | `(args: Optional[list] = None) -> int` |

### H.18.3 Calling Sequence (Call Graph)

Per AGENTS.md §17, the function calling sequence for the two primary execution paths:

#### CLI Mode Call Chain

```
main(args)                                                    [F2, entry point]
  │
  ├── discover_project_root("eks", "engine", ...)             [L17, common.library.paths]
  │
  ├── EKSBootstrapManager.__init__(project_root, ...)         [D1]
  │     └── BootstrapManager.__init__(...)                    [C1, super().__init__]
  │           └── BootstrapPhaseRegistry()                    [B1, default 8-phase]
  │           └── BootstrapPhaseRegistry.build_phase_status() [B8]
  │
  ├── EKSBootstrapManager.bootstrap_all(args)                 [C10, inherited]
  │     │
  │     ├── _run_phase("P1_cli", _bootstrap_cli)              [C27]
  │     │     ├── _record_phase_start("P1_cli")               [C2]
  │     │     ├── _bootstrap_cli(cli_args)                    [C15]
  │     │     │     └── _eks_cli_parser(args)                 [D4] → parse_eks_cli() [L18]
  │     │     ├── _record_phase_complete("P1_cli")            [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P2_paths", _bootstrap_paths)          [C27]
  │     │     ├── _record_phase_start("P2_paths")             [C2]
  │     │     ├── _bootstrap_paths()                          [C16]
  │     │     │     └── _eks_path_resolver(root, config)      [D2] → resolve_paths() [L16]
  │     │     ├── _record_phase_complete("P2_paths")          [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P3_registry", _bootstrap_registry)    [C27]
  │     │     ├── _record_phase_start("P3_registry")          [C2]
  │     │     ├── _bootstrap_registry()                       [C17]
  │     │     │     └── _eks_config_loader(config_dir)        [D3] → ConfigRegistry / SchemaLoader
  │     │     ├── _record_phase_complete("P3_registry")       [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P4_defaults", _bootstrap_defaults)    [C27]
  │     │     ├── _record_phase_start("P4_defaults")          [C2]
  │     │     ├── _bootstrap_defaults()                       [C18]
  │     │     ├── _record_phase_complete("P4_defaults")       [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P5_fallback", _bootstrap_fallback)    [C27]
  │     │     ├── _record_phase_start("P5_fallback")          [C2]
  │     │     ├── _bootstrap_fallback()                       [C19] (no-op in base)
  │     │     ├── _record_phase_complete("P5_fallback")       [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P6_env", _bootstrap_env)              [C27]
  │     │     ├── _record_phase_start("P6_env")               [C2]
  │     │     ├── EKSBootstrapManager._bootstrap_env()        [D8, overrides C20]
  │     │     │     └── detect_os()                           [L12]
  │     │     ├── _record_phase_complete("P6_env")            [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P7_schema", _bootstrap_schema)        [C27]
  │     │     ├── _record_phase_start("P7_schema")            [C2]
  │     │     ├── _bootstrap_schema()                         [C21] (no-op in base)
  │     │     ├── _record_phase_complete("P7_schema")         [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _run_phase("P8_params", _bootstrap_params)        [C27]
  │     │     ├── _record_phase_start("P8_params")            [C2]
  │     │     ├── EKSBootstrapManager._bootstrap_params()     [D9, overrides C22]
  │     │     ├── _record_phase_complete("P8_params")         [C3]
  │     │     └── _log(...)                                   [C28]
  │     │
  │     ├── _bootstrapped = True
  │     └── return self
  │
  ├── EKSBootstrapManager.to_pipeline_context()               [D12]
  │     ├── guard: _bootstrapped == True                      (else → P1-BOOT-CTX)
  │     ├── EKSPaths(...)                                     [E dataclass]
  │     ├── EKSData()                                         [E dataclass]
  │     ├── EKSState(status="INITIALIZED", ...)               [E dataclass]
  │     │     └── EKSPipelineContext.__post_init__()          [E8]
  │     ├── EKSTelemetry()                                    [E dataclass]
  │     ├── _eks_error_factory(...)                           [D6] → ErrorManager
  │     ├── _eks_message_factory(...)                         [D7] → MessageManager
  │     ├── EKSPipelineContext(paths, data, params, ...)      [E dataclass]
  │     ├── _build_postload_trace(ctx)                        [C26]
  │     └── return ctx
  │
  ├── EngineInput(run_id, data_dir, config_file, ...)         [L08]
  │
  └── run_pipeline(context=ctx, ...)                          [pipeline orchestrator]
```

#### UI Mode Call Chain

```
bootstrap_for_ui(**ui_params)                                [C11]
  │
  ├── cli_args = ui_params, cli_overrides_provided = True
  │
  ├── _run_phase("P2_paths", _bootstrap_paths)               [C27 → C16]
  ├── _run_phase("P3_registry", _bootstrap_registry)         [C27 → C17]
  ├── _run_phase("P4_defaults", _bootstrap_defaults)         [C27 → C18]
  ├── _run_phase("P6_env", _bootstrap_env)                   [C27 → D8]
  ├── _run_phase("P7_schema", _bootstrap_schema)             [C27 → C21]
  ├── _run_phase("P8_params", _bootstrap_params_for_ui)      [C27 → C23]
  │     └── effective_parameters = native < schema < UI
  │
  ├── _bootstrapped = True
  └── return self
```

#### Backward-Compat (Legacy) Call Chain

```
bootstrap_pipeline(project_root, args, ...)                  [F1, legacy wrapper]
  │
  └── EKSBootstrapManager.__init__(project_root, ...)        [D1]
  └── EKSBootstrapManager.bootstrap_all(args)                [C10]
  └── EKSBootstrapManager.to_dict()                          [D11, backward-compat]
        ├── _eks_error_factory(...)                          [D6, lazy]
        ├── _eks_message_factory(...)                        [D7, lazy]
        └── return {config, em, mm, resolved_paths, ...}     (legacy dict shape)
```

### H.18.4 I/O Table

Per AGENTS.md §14.8, this table documents the primary inputs and outputs of each public/external function in the bootstrap module chain.

| Function | Input Source | Input | Output | Consumer |
|----------|-------------|-------|--------|----------|
| `BootstrapManager.__init__` [C1] | Caller | `project_root: Path`, 11 optional keyword hooks | Initialized manager with phase registry + status dict | `bootstrap_all()` / `bootstrap_for_ui()` |
| `bootstrap_all` [C10] | CLI / caller | `cli_args: List[str]?` | `self` (populated state: cli_args, config, paths, os_info, effective_parameters, _bootstrapped=True) | `to_pipeline_context()` / `to_dict()` |
| `bootstrap_for_ui` [C11] | HTTP / UI backend | `**ui_params` | `self` (populated state, skips P1/P5) | `to_pipeline_context()` / `to_dict()` |
| `to_pipeline_context` [C12/C13] | Internal state | `self._bootstrapped`, `self.resolved_paths`, `self.effective_parameters`, `self.config`, `self.error_manager`, `self.message_manager` | `BasePipelineContext` (dict or EKSPipelineContext) | `run_pipeline(context=ctx)` |
| `to_dict` [C14] | Internal state | All bootstrapped state | `Dict` with keys: `config`, `doc_config`, `config_registry`, `em`, `mm`, `resolved_paths`, `os_info`, `level`, `data_dir`, `project_root`, `config_dir`, `parsed` | Legacy callers (`phase1_server.py`, tests) |
| `bootstrap_summary` [C5] | Phase tracking | `_phase_status` dict | `Dict` with `status`, `completed_count`, `total_count`, `failed_phase`, `error_code`, `total_duration_ms` | Logging, debugging, UI status display |
| `_run_readiness_gate` [C24] | Project state | `self.project_root`, `self.config` | `bool` (True = ready) | `bootstrap_pipeline()` (legacy) / pre-bootstrap checks |
| `BootstrapError.__init__` [A1] | Phase handler | `code: str`, `message: str`, `phase: str` | Exception instance | `try/except` in `bootstrap_all()`, `main()` |
| `BootstrapError.to_system_error` [A2] | Exception instance | `self.code`, `self.message` | `(code: str, message: str)` tuple | L10 `BaseErrorManager.handle_system_error()` |
| `BootstrapError.to_dict` [A3] | Exception instance | `self.code`, `self.message`, `self.phase` | `{"code": ..., "message": ..., "phase": ...}` | JSON serialization, logging |
| `BootstrapError.from_system_error` [A4] | Error manager | `code: str`, `message: str`, `phase: str` | `BootstrapError` instance | Reconstructing errors from stored (code, message) pairs |
| `BootstrapPhaseRegistry.register` [B2] | Project config | `phase_id`, `phase_name`, `order`, `method` | `self` (fluent) | Custom phase setup |
| `BootstrapPhaseRegistry.build_phase_status` [B8] | Registry state | Registered phases | `Dict[str, BootstrapPhaseStatus]` | `BootstrapManager.__init__` |
| `EKSBootstrapManager.__init__` [D1] | `main()` / `bootstrap_pipeline()` | `project_root`, EKS-specific flags | Initialized EKS manager with injected hooks | `bootstrap_all()` |
| `EKSBootstrapManager.to_pipeline_context` [D12] | Bootstrapped state | All resolved state | `EKSPipelineContext` (L06 subclass) | `run_pipeline(context=ctx)` |
| `bootstrap_pipeline` [F1] | Legacy callers | `project_root`, `args`, `logger`, flags | `Dict` (backward-compat shape) | `phase1_server.py`, existing tests |
| `main` [F2] | `console_scripts` / `sys.argv` | `args: List[str]?` | `int` (0 = success, 1 = failure) | `sys.exit(main())` |

---

## H.19 Function Details

Per AGENTS.md §17, this section provides full details for each function: purpose, parameter flow, error handling, and tracing/status reporting.

### H.19.1 BootstrapError (A1–A4)

**A1. `BootstrapError.__init__(code, message, phase="unknown")`**
- **Purpose**: Structured exception constructor for bootstrap failures.
- **Parameter flow**: `code` → `self.code`; `message` → `self.message`; `phase` → `self.phase`. Calls `super().__init__()` with formatted string `[code] message (phase: phase)`.
- **Error handling**: None — pure data carrier.
- **Tracing**: Error code is project-prefix-aware (EKS: `P1-BOOT-*`, DCC: `S-*-S-*`, universal: `B-*`).

**A2. `BootstrapError.to_system_error()`**
- **Purpose**: Bridge to DCC's legacy `system_error_print()` / L10 `BaseErrorManager`.
- **Returns**: `(self.code, self.message)` tuple.
- **Dependencies**: Consumed by L10 `BaseErrorManager.handle_system_error()`.

**A3. `BootstrapError.to_dict()`**
- **Purpose**: JSON-safe serialization for logging/API responses.
- **Returns**: `{"code": str, "message": str, "phase": str}`.

**A4. `BootstrapError.from_system_error(cls, code, message, phase="unknown")`**
- **Purpose**: Reconstruct from stored `(code, message)` pair (round-trip with `to_system_error()`).
- **Returns**: New `BootstrapError` instance.

### H.19.2 BootstrapPhaseRegistry (B1–B10)

**B1. `BootstrapPhaseRegistry.__init__()`**
- **Purpose**: Initialize registry with the default 8-phase DCC sequence (P1_cli through P8_params).
- **State**: Populates `self._phases: Dict[str, PhaseEntry]` from `_DEFAULT_PHASES`.

**B2. `BootstrapPhaseRegistry.register(phase_id, phase_name, order, method="")`**
- **Purpose**: Register or replace a phase entry. Returns self for fluent chaining.
- **Parameter flow**: Creates/overwrites `PhaseEntry` in `self._phases[phase_id]`.

**B3. `BootstrapPhaseRegistry.remove(phase_id)`**
- **Purpose**: Remove a phase (e.g., skip P5_fallback for UI mode).
- **Error handling**: Silently ignores missing `phase_id` (`.pop(None)`).

**B4–B7. Query methods** (`get`, `get_phase_name`, `iter_ordered`, `get_method`)
- **Purpose**: Retrieve phase entries by ID, ordered by `order` field.
- **`get`**: Returns `PhaseEntry | None`.
- **`get_phase_name`**: Falls back to returning `phase_id` if not found.
- **`get_method`**: Returns `""` if not found.
- **`iter_ordered`**: Yields phases sorted by `order` (ascending).

**B8. `build_phase_status()`**
- **Purpose**: Build initial tracking dict for `BootstrapManager._phase_status`.
- **Returns**: `{phase_id: BootstrapPhaseStatus(phase_id, phase_name, status="pending")}` for all registered phases.

**B9. `phase_count` (property)**
- **Purpose**: Return number of registered phases.

**B10. `to_list()`**
- **Purpose**: Serialize all phases to list of dicts for debugging/UI.

### H.19.3 Universal BootstrapManager (C1–C28)

**C1. `BootstrapManager.__init__(project_root, *, 11 optional hooks)`**
- **Purpose**: Initialize the universal bootstrap orchestrator with project root, directory literals, and strategy hooks.
- **Parameter flow**: 12 parameters → 24 instance attributes. `project_root` → `Path(project_root)`. Hooks stored as private callables. Phase registry defaults to `BootstrapPhaseRegistry()` with 8 phases.
- **Error handling**: None during init — hooks are validated lazily during phase execution.
- **Tracing**: Pre/post-load traces initialized to `None`.

**C2–C4. Phase tracking** (`_record_phase_start`, `_record_phase_complete`, `_record_phase_failure`)
- **Purpose**: Record phase lifecycle events with ISO 8601 timestamps.
- **Parameter flow**: `phase_id` → looks up `self._phase_status[phase_id]` → updates status, start_time, end_time, duration_ms, error_code.
- **`_record_phase_start`**: status → `"running"`, start_time → `now()`.
- **`_record_phase_complete`**: status → `"complete"`, end_time → `now()`, duration_ms → `(end - start) * 1000`.
- **`_record_phase_failure`**: status → `"failed"`, end_time → `now()`, error_code recorded.

**C5. `bootstrap_summary` (property)**
- **Purpose**: Dynamic summary of all phase statuses.
- **Status logic**: All complete → `"complete"`; any failed → `"failed"`; some complete → `"partial"`; none → `"in_progress"`.
- **Returns**: `{status, completed_count, total_count, failed_phase, error_code, total_duration_ms}`.

**C6. `is_bootstrapped` (property)**
- **Purpose**: Gate for `to_pipeline_context()` and `preload_trace`.
- **Returns**: `self._bootstrapped` (set `True` only after all phases complete successfully).

**C7. `preload_trace` (property)**
- **Purpose**: Access pre-context trace snapshot.
- **Error handling**: Raises `BootstrapError("B-BOOT-0601", ...)` if not bootstrapped.

**C8. `postload_trace` (property)**
- **Purpose**: Access post-context trace snapshot. Returns `None` if `to_pipeline_context()` not yet called.

**C9. `phase_status` (property)**
- **Purpose**: Read-only access to per-phase tracking dict.

**C10. `bootstrap_all(cli_args=None)` — PRIMARY ENTRY POINT (CLI)**
- **Purpose**: Execute all 8 bootstrap phases in sequence. Returns self for chaining.
- **Parameter flow**: `cli_args` → P1 CLI parsing → populates `cli_args`, `parsed`, `debug_mode`, `cli_overrides_provided`, `project_root`, `config_dir`.
- **Calling sequence**: P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → set `_bootstrapped = True` → return self.
- **Error handling**: Each phase wrapped in `_run_phase()` which catches `BootstrapError` (re-raises) and generic `Exception` (wraps in `BootstrapError("B-UNK-001", ...)`).
- **Tracing**: `_bootstrap_start_time` recorded at entry. Each phase logs via `_log()`.

**C11. `bootstrap_for_ui(**ui_params)` — PRIMARY ENTRY POINT (UI)**
- **Purpose**: Run bootstrap skipping CLI parsing (P1) and fallback validation (P5). UI params set directly as `cli_args`.
- **Parameter flow**: `**ui_params` → `self.cli_args`, `self.cli_overrides_provided = bool(ui_params)`, `self.debug_mode = ui_params.get("debug_mode", False)`.
- **Calling sequence**: P2 → P3 → P4 → P6 → P7 → P8 (via `_bootstrap_params_for_ui`).
- **Error handling**: Same pattern as `bootstrap_all()`; unexpected errors wrapped in `BootstrapError("B-UNK-002", ...)`.

**C12. `to_pipeline_context()`**
- **Purpose**: Convert bootstrapped state to a pipeline context object.
- **Error handling**: Raises `BootstrapError("B-CTX-001", ...)` if `_bootstrapped == False`.
- **Returns**: Default is a dict with all resolved state. Subclasses (EKS) override to return typed context objects.

**C13. `_build_context()`**
- **Purpose**: Build the default dict-based context. Subclasses override for typed contexts.
- **Returns**: `{project_root, config_dir, resolved_paths, parameters, config, doc_config, error_manager, message_manager, os_info, debug_mode}`.

**C14. `to_dict()`**
- **Purpose**: Backward-compatible dict matching legacy `bootstrap_pipeline()` return shape.
- **Returns**: `{config, doc_config, config_registry, em, mm, resolved_paths, os_info, level, data_dir, project_root, config_dir, parsed}`.

**C15. `_bootstrap_cli(cli_args)` — Phase P1**
- **Purpose**: Parse CLI args via injected `_cli_parser`. Handles both `CliResult` (L18, with `.namespace`) and plain namespace returns.
- **Parameter flow**: `cli_args` → `_cli_parser(cli_args)` → extracts `cli_args` (via `vars()`), `parsed`, `cli_overrides_provided`, `project_root`, `config_dir`. Determines `debug_mode` from `verbose`/`level`.
- **Error handling**: Raises `BootstrapError("B-CLI-001", ...)` on failure.

**C16. `_bootstrap_paths(cli_args)` — Phase P2**
- **Purpose**: Validate `project_root` exists, resolve canonical paths via injected `_path_resolver`.
- **Parameter flow**: `project_root` → existence check → `_path_resolver(project_root, config)` → `self.resolved_paths`. Falls back to simple defaults if no resolver.
- **Error handling**: `BootstrapError("B-PATH-001")` if root missing; `BootstrapError("B-PATH-002")` for unexpected errors.

**C17. `_bootstrap_registry()` — Phase P3**
- **Purpose**: Load project config via injected `_config_loader`.
- **Error handling**: `BootstrapError("B-REG-001")` on failure.

**C18. `_bootstrap_defaults()` — Phase P4**
- **Purpose**: Build native defaults from `config.global_paths`.
- **Error handling**: `BootstrapError("B-DEF-001")` on failure.

**C19. `_bootstrap_fallback()` — Phase P5**
- **Purpose**: Validate fallback files (no-op in base; subclasses override).
- **Error handling**: `BootstrapError("B-FALL-001")` on failure.

**C20. `_bootstrap_env()` — Phase P6**
- **Purpose**: Detect OS via injected `_os_detector`.
- **Error handling**: `BootstrapError("B-ENV-001")` on failure.

**C21. `_bootstrap_schema()` — Phase P7**
- **Purpose**: Resolve schemas (no-op in base; subclasses override).
- **Error handling**: `BootstrapError("B-SCH-001")` on failure.

**C22. `_bootstrap_params()` — Phase P8 (CLI)**
- **Purpose**: Merge CLI + Schema + Native into `effective_parameters`. Precedence: CLI > Schema > Native.
- **Error handling**: `BootstrapError("B-PAR-001")` on failure.

**C23. `_bootstrap_params_for_ui(**ui_params)` — Phase P8 (UI)**
- **Purpose**: Merge UI + Schema + Native. UI values get highest precedence.
- **Error handling**: `BootstrapError("B-PAR-002")` on failure.

**C24. `_run_readiness_gate()`**
- **Purpose**: Run project-setup readiness validation via injected `_readiness_validator_factory`.
- **Returns**: `bool` — `True` if ready, `False` otherwise. Returns `True` if no factory is configured.
- **Error handling**: Catches exceptions from validator, returns `False`.

**C25. `_build_preload_trace()`**
- **Purpose**: Capture system state snapshot before context creation.
- **Captures**: `project_root`, `config_dir`, `phase_status` (status only), `bootstrap_summary`.

**C26. `_build_postload_trace(context)`**
- **Purpose**: Capture system state snapshot after context creation.
- **Captures**: `context_type`, `resolved_paths` (stringified), `effective_parameters`.

**C27. `_run_phase(phase_id, phase_fn)`**
- **Purpose**: Execute a single phase with tracking, timing, and error wrapping.
- **Parameter flow**: Records start → executes `phase_fn()` → records complete/failure.
- **Error handling**: `BootstrapError` → records failure with error code, re-raises. Generic `Exception` → wraps in `BootstrapError(f"B-{phase_id}-ERR", ...)`.

**C28. `_log(msg, level=1)`**
- **Purpose**: Log through injected logger. Gracefully handles missing or incompatible loggers.

### H.19.4 EKSBootstrapManager (D1–D12)

**D1. `EKSBootstrapManager.__init__(project_root, *, pipeline_root_dir="eks", pipeline_dir="engine", skip_readiness=False, debug=False, auto_create=True, use_config_registry=True, logger=None)`**
- **Purpose**: Initialize EKS-specific bootstrap with all hook injections.
- **Parameter flow**: Calls `super().__init__()` with 7 injected hooks (os_detector, path_resolver, config_loader, cli_parser, readiness_validator_factory, error_manager_factory, message_manager_factory). Stores EKS-specific flags (`_skip_readiness`, `_debug`, `_auto_create`, `_use_config_registry`).
- **Dependencies**: `detect_os` (L12), `resolve_paths` (L16), `parse_eks_cli` (L18), `ConfigRegistry`, `ProjectSetupValidator`, `ErrorManager` (L10), `MessageManager` (L11).

**D2. `_eks_path_resolver(project_root, config)`**
- **Purpose**: L16 — schema-driven canonical path resolution.
- **Returns**: `resolve_paths(project_root, config).resolve(project_root)`.

**D3. `_eks_config_loader(config_dir)`**
- **Purpose**: Load EKS config via `ConfigRegistry` SSOT with singleton reset on config_dir change. Falls back to `SchemaLoader`.
- **Error handling**: Silently falls back to `SchemaLoader` if `ConfigRegistry` fails.

**D4. `_eks_cli_parser(args)`**
- **Purpose**: L18 — parse EKS CLI args via `parse_eks_cli()`. Sets `self.parsed`, `self.project_root`, `self.config_dir`.
- **Returns**: `CliResult` with `.namespace`.

**D5–D7. Factory methods** (`_eks_readiness_factory`, `_eks_error_factory`, `_eks_message_factory`)
- **Purpose**: Create EKS-specific manager/validator instances on demand.
- **D5**: Creates `ProjectSetupValidator` with `project_root`, `config_registry`, `verbose`.
- **D6**: Creates `ErrorManager` (L10) with `config_dir`, `logger`, `config`.
- **D7**: Creates `MessageManager` (L11) with `config_dir`, `logger`.

**D8. `_bootstrap_env()` — P6 override**
- **Purpose**: EKS-specific OS detection via L12 `detect_os()` + dependency testing via L20 `test_environment()`.
- **Parameter flow**: 1) `detect_os()` → `self.os_info`. 2) Extract `dependencies` from `self.config` (from `eks_config.json`). 3) Call `test_environment(deps)` → `self._env_test_results`. 4) If `ready=False`, raise `BootstrapError("P1-BOOT-ENV", ...)` with missing-package names + "Run: conda activate eks" guidance.
- **Error handling**: Raises `BootstrapError("P1-BOOT-OS", ...)` on OS detection failure; raises `BootstrapError("P1-BOOT-ENV", ...)` on dependency failure.

**D9. `_bootstrap_params()` — P8 override**
- **Purpose**: EKS-specific parameter merging with `level` and `data_dir` resolution.
- **Parameter flow**:
  - `level`: CLI `--level` > Schema `log_level` > Native (1). CLI `--debug` → level = 3.
  - `data_dir`: CLI `--data-dir` > Schema `resolve_paths` > Native. CLI absolute → as-is; CLI relative → anchored under `project_root / eks_root`.
  - Other params: CLI > Schema > Native precedence.
- **Error handling**: Raises `BootstrapError("P1-BOOT-PARAMS", ...)` on failure.

**D10. `_run_readiness_gate()` — override**
- **Purpose**: EKS-specific readiness gate via `ProjectSetupValidator`.
- **Returns**: `bool`. Honors `_skip_readiness` flag.
- **Error handling**: Catches exceptions, logs, returns `False`.

**D11. `to_dict()` — override**
- **Purpose**: Backward-compatible dict with lazy manager initialization.
- **Lazy init**: Creates `ErrorManager` and `MessageManager` via factories if not already created.
- **Returns**: Dict with all legacy keys + `config_registry` and `parsed`.

**D12. `to_pipeline_context()` — override**
- **Purpose**: Build typed `EKSPipelineContext` (L06 subclass).
- **Returns**: `EKSPipelineContext` with `EKSPaths`, `EKSData`, `EKSState(status="INITIALIZED")`, `EKSTelemetry`, `config_registry`, `schema_registry`.
- **Lazy init**: Creates `ErrorManager`/`MessageManager` if needed, injects into `ctx_params`.
- **Error handling**: Raises `BootstrapError("P1-BOOT-CTX", ...)` if not bootstrapped.

### H.19.5 EKSPipelineContext (E1–E13)

**E1–E7. Dataclass serialization methods**
- **Purpose**: `to_dict()` on `EKSPaths`, `EKSData`, `EKSState`, `EKSTelemetry` for JSON serialization.
- **`EKSPaths.to_dict()`**: Uses `as_posix()` for cross-platform path strings.
- **`EKSState.to_dict()`**: Uses `isoformat()` for datetime fields.
- **`EKSTelemetry`**: `add_checkpoint(phase, timestamp, details)` — records phase checkpoint. `record_metric(name, value)` — records performance metric. `record_error(error_type)` — increments error counter.

**E8. `EKSPipelineContext.__post_init__()`**
- **Purpose**: Auto-set `state.start_time = datetime.now()` if not provided.

**E9. `EKSPipelineContext.to_dict()`**
- **Purpose**: Serialize entire context for logging/API responses.

**E10. `EKSPipelineContext._from_dict(cls, data)`**
- **Purpose**: Reconstruct context from dict (BasePipelineContext contract, L06).

**E11. `EKSPipelineContext.update_phase(phase, status="IN_PROGRESS")`**
- **Purpose**: Update current phase and add telemetry checkpoint.

**E12. `EKSPipelineContext.complete()`**
- **Purpose**: Mark pipeline as complete — sets `state.status = "COMPLETE"`, `state.end_time = now()`, adds telemetry checkpoint.

**E13. `EKSPipelineContext.fail(error_message)`**
- **Purpose**: Mark pipeline as failed — sets `state.status = "FAILED"`, `state.end_time = now()`, adds telemetry checkpoint with error message.

### H.19.6 Entry Points (F1–F2)

**F1. `bootstrap_pipeline(project_root, args, logger, skip_readiness, debug, use_config_registry, auto_create)`**
- **Purpose**: Thin backward-compatible wrapper around `EKSBootstrapManager`. Delegates all logic to L19.
- **Parameter flow**: Creates `EKSBootstrapManager` → `bootstrap_all(args)` → `to_dict()`.
- **Error handling**: Readiness gate failure raises `BootstrapError("P1-BOOT-READINESS", ...)`.
- **Status**: Thin wrapper — all logic delegated to universal manager (T1.99.58).

**F2. `main(args=None)`**
- **Purpose**: `console_scripts` entry point — full DCC-faithful pipeline orchestration.
- **Parameter flow**: 12-step chain (see §H.12): discover root → bootstrap → context → EngineInput → run_pipeline → EngineOutput → exit code.
- **Error handling**: Bootstrap failures propagate as `BootstrapError("P1-BOOT-*")`. Top-level `except Exception` logs via `UniversalLogger`, prints to `stderr`, returns exit code 1.
- **Returns**: `0` on success, `1` on failure (suitable for `sys.exit`).

### H.19.7 Error Handling Summary

| Function | Error Raised | Error Code | Trigger Condition |
|----------|-------------|------------|-------------------|
| `bootstrap_pipeline` [F1] | `BootstrapError` | `P1-BOOT-READINESS` | Readiness gate returns `False` |
| `_bootstrap_cli` [C15] | `BootstrapError` | `B-CLI-001` | CLI parsing fails |
| `_bootstrap_paths` [C16] | `BootstrapError` | `B-PATH-001` | `project_root` does not exist |
| `_bootstrap_paths` [C16] | `BootstrapError` | `B-PATH-002` | Unexpected path resolution error |
| `_bootstrap_registry` [C17] | `BootstrapError` | `B-REG-001` | Config loading fails |
| `_bootstrap_defaults` [C18] | `BootstrapError` | `B-DEF-001` | Defaults building fails |
| `_bootstrap_fallback` [C19] | `BootstrapError` | `B-FALL-001` | Fallback validation fails |
| `_bootstrap_env` [D8] (EKS) | `BootstrapError` | `P1-BOOT-OS` | OS detection fails |
| `_bootstrap_env` [D8] (EKS) | `BootstrapError` | `P1-BOOT-ENV` | Dependency check fails — required packages missing |
| `_bootstrap_env` [C20] (base) | `BootstrapError` | `B-ENV-001` | OS detection fails (universal) |
| `_bootstrap_schema` [C21] | `BootstrapError` | `B-SCH-001` | Schema resolution fails |
| `_bootstrap_params` [D9] (EKS) | `BootstrapError` | `P1-BOOT-PARAMS` | Parameter resolution fails |
| `_bootstrap_params` [C22] (base) | `BootstrapError` | `B-PAR-001` | Parameter resolution fails (universal) |
| `_bootstrap_params_for_ui` [C23] | `BootstrapError` | `B-PAR-002` | UI parameter resolution fails |
| `preload_trace` [C7] | `BootstrapError` | `B-BOOT-0601` | Accessed before bootstrap complete |
| `to_pipeline_context` [C12] | `BootstrapError` | `B-CTX-001` | Called before bootstrap (universal) |
| `to_pipeline_context` [D12] (EKS) | `BootstrapError` | `P1-BOOT-CTX` | Called before bootstrap (EKS) |
| `bootstrap_all` [C10] | `BootstrapError` | `B-UNK-001` | Unexpected exception in any phase |
| `bootstrap_for_ui` [C11] | `BootstrapError` | `B-UNK-002` | Unexpected exception in UI mode |
| `_run_phase` [C27] | `BootstrapError` | `B-{phase_id}-ERR` | Phase raises non-BootstrapError exception |

---

## Revision Control

| Revision | Date | Author | Summary |
|----------|------|--------|---------|
| 0.1 | 2026-07-17 | opencode | Initial appendix — comprehensive bootstrap module design summary for I108–I111 (T1.99.50–T1.99.63) |
| 0.2 | 2026-07-17 | opencode | Added §H.18 Function List & I/O Table (78 functions across 7 modules, call graphs for CLI/UI/legacy paths, I/O table) and §H.19 Function Details (purpose, parameter flow, error handling, tracing per function) per AGENTS.md §14.7–§14.8 and §17 |
| 0.3 | 2026-07-17 | opencode | I114 updates: §H.4 P6 description + env_tester; §H.7 constructor params + EnvTester type alias + _env_test_results state; §H.8 hook mappings + P6 override; §H.11 P1-BOOT-ENV error code; §H.12 lazy-import design + early verbosity parse in main() flow; §H.19.4 D8 + §H.19.7 error table. T1.99.80 v2 reflected throughout. |
