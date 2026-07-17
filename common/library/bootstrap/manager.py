"""
L19 — Universal ``BootstrapManager``.

Project-agnostic, stateful bootstrap orchestrator extracted from DCC's mature
implementation (~1223 lines, 8 phases).  Both EKS and DCC (and future projects)
delegate bootstrap to this shared manager.

Architecture
------------
- Phase tracking via ``BootstrapPhaseStatus`` (start/end/duration/error).
- Pre/post-load context traces via ``_build_preload_trace`` / ``_build_postload_trace``.
- Dual-mode: ``bootstrap_all(cli_args)`` and ``bootstrap_for_ui(**params)``.
- ``to_pipeline_context()`` returns an L06 ``BasePipelineContext``.
- Structured ``BootstrapError`` wired to L10 ``BaseErrorManager``.
- Configurable phase ordering via ``BootstrapPhaseRegistry``.

Project-specific hooks (anchor folder, config shape, readiness validator,
error catalog) are injected via constructor / strategy parameters so the
manager stays project-agnostic.

Source
------
dcc: ``workflow/utility_engine/bootstrap/boot_pipeline.py`` (BootstrapManager, ~1223 lines)

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.50 — Universal BootstrapManager extracted from DCC for L19.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .errors import BootstrapError
from .phases import BootstrapPhaseRegistry, BootstrapPhaseStatus

# ---------------------------------------------------------------------------
# Type aliases for project-specific hooks (injected via constructor)
# ---------------------------------------------------------------------------

# Callable that loads config from a config_dir and returns a dict.
ConfigLoader = Callable[[Path], Dict[str, Any]]

# Callable that parses CLI args (sys.argv) and returns a namespace-like object.
CliParser = Callable[[Optional[List[str]]], Any]

# Callable that resolves paths from project_root + config.
PathResolver = Callable[[Path, Dict[str, Any]], Dict[str, Path]]

# Callable that creates a readiness validator.
ReadinessValidatorFactory = Callable[..., Any]

# Callable that creates an ErrorManager.
ErrorManagerFactory = Callable[..., Any]

# Callable that creates a MessageManager.
MessageManagerFactory = Callable[..., Any]

# Callable that detects OS (returns str like "windows", "linux", "macos").
OsDetector = Callable[[], str]

# Callable that tests environment dependencies and returns a results dict.
# Signature: (dependencies: dict) -> dict with {ready, errors, required_modules, ...}
EnvTester = Callable[[Dict[str, Any]], Dict[str, Any]]


class BootstrapManager:
    """
    Universal, stateful bootstrap orchestrator.

    Usage (EKS, DCC-faithful)::

        manager = BootstrapManager(
            project_root=Path("..."),
            pipeline_root_dir="eks",
            pipeline_dir="engine",
            config_loader=load_eks_config,
            cli_parser=parse_eks_cli,
            path_resolver=resolve_paths,
            readiness_validator_factory=create_eks_validator,
            error_manager_factory=create_eks_error_manager,
            message_manager_factory=create_eks_message_manager,
            os_detector=detect_os,
        )
        ctx = manager.bootstrap_all(args).to_pipeline_context()
        result = run_pipeline(context=ctx)

    Attributes:
        project_root:   Resolved project root path.
        pipeline_root_dir: Pipeline root directory name (e.g. ``"eks"``, ``"dcc"``).
        pipeline_dir:   Pipeline entry folder name (e.g. ``"engine"``, ``"workflow"``).
        _bootstrapped:  Whether bootstrap has completed successfully.
        _phase_registry: Configurable phase registry.
        _phase_status:  Per-phase tracking dict.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        project_root: Path,
        *,
        pipeline_root_dir: str = "",
        pipeline_dir: str = "",
        # Strategy hooks — injected by the calling project
        config_loader: Optional[ConfigLoader] = None,
        cli_parser: Optional[CliParser] = None,
        path_resolver: Optional[PathResolver] = None,
        readiness_validator_factory: Optional[ReadinessValidatorFactory] = None,
        error_manager_factory: Optional[ErrorManagerFactory] = None,
        message_manager_factory: Optional[MessageManagerFactory] = None,
        os_detector: Optional[OsDetector] = None,
        env_tester: Optional[EnvTester] = None,
        # Phase registry (default = DCC 8-phase)
        phase_registry: Optional[BootstrapPhaseRegistry] = None,
        # Logger
        logger: Any = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.pipeline_root_dir = pipeline_root_dir
        self.pipeline_dir = pipeline_dir

        # Strategy hooks
        self._config_loader = config_loader
        self._cli_parser = cli_parser
        self._path_resolver = path_resolver
        self._readiness_validator_factory = readiness_validator_factory
        self._error_manager_factory = error_manager_factory
        self._message_manager_factory = message_manager_factory
        self._os_detector = os_detector
        self._env_tester = env_tester
        self.logger = logger

        # Phase tracking
        self._phase_registry = phase_registry or BootstrapPhaseRegistry()
        self._phase_status: Dict[str, BootstrapPhaseStatus] = self._phase_registry.build_phase_status()
        self._bootstrap_start_time: Optional[str] = None

        # State populated during bootstrap
        self._bootstrapped: bool = False
        self.cli_args: Dict[str, Any] = {}
        self.cli_overrides_provided: bool = False
        self.debug_mode: bool = False
        self.os_info: str = ""
        self.config: Dict[str, Any] = {}
        self.doc_config: Dict[str, Any] = {}
        self.config_dir: Path = project_root
        self.resolved_paths: Dict[str, Path] = {}
        self.effective_parameters: Dict[str, Any] = {}
        self.native_defaults: Dict[str, Any] = {}
        self.error_manager: Any = None
        self.message_manager: Any = None
        self.registry: Any = None
        self.validator: Any = None
        self._env_test_results: Dict[str, Any] = {}

        # Pre/post-load traces
        self._preload_trace: Optional[Dict[str, Any]] = None
        self._postload_trace: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Phase tracking
    # ------------------------------------------------------------------

    def _record_phase_start(self, phase_id: str) -> None:
        """Record phase start time and mark as running."""
        if phase_id in self._phase_status:
            self._phase_status[phase_id].status = "running"
            self._phase_status[phase_id].start_time = datetime.now().isoformat()

    def _record_phase_complete(self, phase_id: str) -> None:
        """Record phase completion and calculate duration."""
        if phase_id in self._phase_status:
            phase = self._phase_status[phase_id]
            phase.status = "complete"
            phase.end_time = datetime.now().isoformat()
            if phase.start_time:
                start = datetime.fromisoformat(phase.start_time)
                end = datetime.fromisoformat(phase.end_time)
                phase.duration_ms = (end - start).total_seconds() * 1000

    def _record_phase_failure(self, phase_id: str, error_code: str) -> None:
        """Record phase failure with error code."""
        if phase_id in self._phase_status:
            phase = self._phase_status[phase_id]
            phase.status = "failed"
            phase.end_time = datetime.now().isoformat()
            phase.error_code = error_code
            if phase.start_time:
                start = datetime.fromisoformat(phase.start_time)
                end = datetime.fromisoformat(phase.end_time)
                phase.duration_ms = (end - start).total_seconds() * 1000

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def bootstrap_summary(self) -> Dict[str, Any]:
        """Return dynamic summary of bootstrap status."""
        completed = sum(1 for p in self._phase_status.values() if p.status == "complete")
        failed = [p for p in self._phase_status.values() if p.status == "failed"]
        total = len(self._phase_status)

        if failed:
            status = "failed"
        elif completed == total:
            status = "complete"
        elif completed > 0:
            status = "partial"
        else:
            status = "in_progress"

        total_duration = None
        if self._bootstrap_start_time:
            start = datetime.fromisoformat(self._bootstrap_start_time)
            end = datetime.now()
            total_duration = (end - start).total_seconds() * 1000

        return {
            "status": status,
            "completed_count": completed,
            "total_count": total,
            "failed_phase": failed[0].phase_id if failed else None,
            "error_code": failed[0].error_code if failed else None,
            "total_duration_ms": total_duration,
        }

    @property
    def is_bootstrapped(self) -> bool:
        """Check if bootstrap has completed successfully."""
        return self._bootstrapped

    @property
    def preload_trace(self) -> Optional[Dict[str, Any]]:
        """Get preload trace data (available after bootstrap completes)."""
        if not self._bootstrapped:
            raise BootstrapError(
                "B-BOOT-0601",
                "Bootstrap must be completed before accessing preload trace",
                "traces",
            )
        return self._preload_trace

    @property
    def postload_trace(self) -> Optional[Dict[str, Any]]:
        """Get postload trace data (available after to_pipeline_context() called)."""
        return self._postload_trace

    @property
    def phase_status(self) -> Dict[str, BootstrapPhaseStatus]:
        """Return the per-phase tracking dict (read-only access)."""
        return self._phase_status

    # ------------------------------------------------------------------
    # bootstrap_all — CLI mode (all 8 phases)
    # ------------------------------------------------------------------

    def bootstrap_all(self, cli_args: Optional[List[str]] = None) -> BootstrapManager:
        """
        Run all bootstrap phases for CLI mode.

        Executes phases in the order defined by ``self._phase_registry``.
        Returns self for method chaining::

            ctx = BootstrapManager(root).bootstrap_all(args).to_pipeline_context()

        Args:
            cli_args: Optional CLI argument list (``None`` → ``sys.argv[1:]``).

        Returns:
            Self for method chaining.

        Raises:
            BootstrapError: If any phase fails validation.
        """
        self._bootstrap_start_time = datetime.now().isoformat()

        try:
            # Phase P1: CLI parsing
            self._run_phase("P1_cli", lambda: self._bootstrap_cli(cli_args))

            # Phase P2: Path validation
            self._run_phase("P2_paths", self._bootstrap_paths)

            # Phase P3: Registry loading
            self._run_phase("P3_registry", self._bootstrap_registry)

            # Phase P4: Native defaults
            self._run_phase("P4_defaults", self._bootstrap_defaults)

            # Phase P5: Fallback validation
            self._run_phase("P5_fallback", self._bootstrap_fallback)

            # Phase P6: Environment testing
            self._run_phase("P6_env", self._bootstrap_env)

            # Phase P7: Schema resolution
            self._run_phase("P7_schema", self._bootstrap_schema)

            # Phase P8: Parameters resolution
            self._run_phase("P8_params", self._bootstrap_params)

            # Mark as bootstrapped
            self._bootstrapped = True
            self._log("Bootstrap Complete: All phases completed successfully")

            return self

        except BootstrapError:
            raise
        except Exception as exc:
            raise BootstrapError("B-UNK-001", f"Unexpected bootstrap error: {exc}", "unknown")

    # ------------------------------------------------------------------
    # bootstrap_for_ui — UI mode (skips CLI parsing)
    # ------------------------------------------------------------------

    def bootstrap_for_ui(self, **ui_params: Any) -> BootstrapManager:
        """
        Run bootstrap phases for UI mode.

        Skips CLI parsing (P1) — uses UI-provided values directly.
        UI values take precedence over schema and native defaults.

        Args:
            **ui_params: UI-provided parameters (project-specific).

        Returns:
            Self for method chaining.

        Raises:
            BootstrapError: If any phase fails validation.
        """
        self._bootstrap_start_time = datetime.now().isoformat()

        try:
            # Set CLI args from UI-provided values
            self.cli_args = ui_params
            self.cli_overrides_provided = bool(ui_params)
            self.debug_mode = ui_params.get("debug_mode", False)

            self._log(f"Bootstrap UI Mode: Base: {self.project_root}")

            # Phase P2: Path validation
            self._run_phase("P2_paths", self._bootstrap_paths)

            # Phase P3: Registry loading
            self._run_phase("P3_registry", self._bootstrap_registry)

            # Phase P4: Native defaults
            self._run_phase("P4_defaults", self._bootstrap_defaults)

            # Phase P6: Environment testing (skip P5 fallback for UI)
            self._run_phase("P6_env", self._bootstrap_env)

            # Phase P7: Schema resolution
            self._run_phase("P7_schema", self._bootstrap_schema)

            # Phase P8: Parameters resolution with UI overrides
            self._run_phase("P8_params", lambda: self._bootstrap_params_for_ui(**ui_params))

            # Mark as bootstrapped
            self._bootstrapped = True
            self._log("Bootstrap Complete: UI mode - All phases completed")

            return self

        except BootstrapError:
            raise
        except Exception as exc:
            raise BootstrapError("B-UNK-002", f"Unexpected bootstrap error (UI): {exc}", "unknown")

    # ------------------------------------------------------------------
    # to_pipeline_context
    # ------------------------------------------------------------------

    def to_pipeline_context(self) -> Any:
        """
        Convert bootstrapped state to a pipeline context.

        Returns an L06 ``BasePipelineContext`` (or subclass) with validated
        paths and parameters.  Subclasses override this to return their own
        context types.

        Returns:
            A pipeline context object (implementation-specific).

        Raises:
            BootstrapError: If bootstrap has not been completed.
        """
        if not self._bootstrapped:
            raise BootstrapError(
                "B-CTX-001",
                "Must bootstrap before creating PipelineContext",
                "context",
            )

        # Default: return a simple dict-based context. Subclasses override.
        context = self._build_context()
        self._build_postload_trace(context)
        return context

    def _build_context(self) -> Any:
        """
        Build the pipeline context from bootstrapped state.

        Subclasses override this to return project-specific context types
        (e.g., EKSPipelineContext, DCC PipelineContext).
        """
        # Default: return a dict with resolved state
        return {
            "project_root": self.project_root,
            "config_dir": self.config_dir,
            "resolved_paths": self.resolved_paths,
            "parameters": self.effective_parameters,
            "config": self.config,
            "doc_config": self.doc_config,
            "error_manager": self.error_manager,
            "message_manager": self.message_manager,
            "os_info": self.os_info,
            "debug_mode": self.debug_mode,
        }

    # ------------------------------------------------------------------
    # to_dict — backward-compat for EKS bootstrap_pipeline() consumers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a backward-compatible dict matching EKS ``bootstrap_pipeline()`` return shape.

        This allows existing callers (``phase1_server.py``, tests) to consume
        the universal manager without changing their code.
        """
        return {
            "config": self.config,
            "doc_config": self.doc_config,
            "config_registry": getattr(self, "config_registry", None),
            "em": self.error_manager,
            "mm": self.message_manager,
            "resolved_paths": self.resolved_paths,
            "os_info": self.os_info,
            "level": self.effective_parameters.get("level", 1),
            "data_dir": self.resolved_paths.get("data_dir", self.project_root / "data"),
            "project_root": self.project_root,
            "config_dir": self.config_dir,
            "parsed": getattr(self, "parsed", None),
        }

    # ==========================================================================
    # Phase P1: CLI Parsing
    # ==========================================================================

    def _bootstrap_cli(self, cli_args: Optional[List[str]] = None) -> None:
        """
        Phase P1: Parse CLI args and determine debug mode.

        Args:
            cli_args: Optional pre-parsed CLI arguments.

        Raises:
            BootstrapError: If CLI parsing fails.
        """
        self._record_phase_start("P1_cli")
        try:
            if self._cli_parser is not None:
                result = self._cli_parser(cli_args)
                # Result may be a CliResult (L18) with namespace, or a plain namespace
                if hasattr(result, "namespace"):
                    self.cli_args = vars(result.namespace) if hasattr(result.namespace, "__dict__") else {}
                    self.parsed = result.namespace
                    if hasattr(result, "overrides_provided"):
                        self.cli_overrides_provided = result.overrides_provided
                    if hasattr(result, "project_root"):
                        self.project_root = result.project_root
                    if hasattr(result, "config_dir"):
                        self.config_dir = result.config_dir
                else:
                    # Plain namespace
                    self.cli_args = vars(result) if hasattr(result, "__dict__") else {}
                    self.parsed = result
                    self.cli_overrides_provided = bool(cli_args)

                # Determine debug mode
                verbose = self.cli_args.get("verbose", "") or self.cli_args.get("level", 1)
                self.debug_mode = verbose in ["debug", "trace"] or int(verbose) >= 2 if isinstance(verbose, int) else False

            self._record_phase_complete("P1_cli")
            self._log(f"Bootstrap Phase P1: CLI parsed, {len(self.cli_args)} args")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P1_cli", "B-CLI-001")
            raise BootstrapError("B-CLI-001", f"CLI parsing failed: {exc}", "cli")

    # ==========================================================================
    # Phase P2: Path Validation
    # ==========================================================================

    def _bootstrap_paths(self) -> None:
        """
        Phase P2: Validate project_root and resolve schema-driven paths.

        Uses the injected ``path_resolver`` to derive canonical paths
        from project_root + config.  Falls back to simple defaults if
        no resolver is provided.

        Raises:
            BootstrapError: If path validation fails.
        """
        self._record_phase_start("P2_paths")
        try:
            if not self.project_root.exists():
                raise BootstrapError(
                    "B-PATH-001",
                    f"Project root does not exist: {self.project_root}",
                    "paths",
                )

            # Resolve schema-driven paths
            if self._path_resolver is not None:
                self.resolved_paths = self._path_resolver(self.project_root, self.config)
            else:
                # Simple defaults
                eks_root = self.pipeline_root_dir or ""
                base = self.project_root / eks_root if eks_root else self.project_root
                self.resolved_paths = {
                    "data_dir": base / "data",
                    "output_dir": base / "output",
                    "archive_dir": base / "archive",
                    "config_dir": base / "config",
                    "log_dir": base / "log",
                    "schema_dir": base / "config" / "schemas",
                }

            self._record_phase_complete("P2_paths")
            self._log(f"Bootstrap Phase P2: Paths resolved: {len(self.resolved_paths)} paths")

        except BootstrapError:
            self._record_phase_failure("P2_paths", "B-PATH-001")
            raise
        except Exception as exc:
            self._record_phase_failure("P2_paths", "B-PATH-002")
            raise BootstrapError("B-PATH-002", f"Path validation failed: {exc}", "paths")

    # ==========================================================================
    # Phase P3: Registry Loading
    # ==========================================================================

    def _bootstrap_registry(self) -> None:
        """
        Phase P3: Load config registry and schema definitions.

        Uses the injected ``config_loader`` to load project config.
        Subclasses override for project-specific registry loading.

        Raises:
            BootstrapError: If registry loading fails.
        """
        self._record_phase_start("P3_registry")
        try:
            if self._config_loader is not None:
                self.config = self._config_loader(self.config_dir)
            else:
                self.config = {}

            self._record_phase_complete("P3_registry")
            self._log(f"Bootstrap Phase P3: Config loaded: {len(self.config)} keys")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P3_registry", "B-REG-001")
            raise BootstrapError("B-REG-001", f"Registry loading failed: {exc}", "registry")

    # ==========================================================================
    # Phase P4: Native Defaults Building
    # ==========================================================================

    def _bootstrap_defaults(self) -> None:
        """
        Phase P4: Build native defaults from schema/config.

        Subclasses override for project-specific defaults.
        """
        self._record_phase_start("P4_defaults")
        try:
            # Default: use global_paths from config
            gp = self.config.get("global_paths", {}) if isinstance(self.config, dict) else {}
            self.native_defaults = {
                "data_dir": gp.get("data_dir", "data"),
                "output_dir": gp.get("output_dir", "output"),
                "archive_dir": gp.get("archive_dir", "archive"),
                "config_dir": gp.get("config_dir", "config"),
                "log_dir": gp.get("log_dir", "log"),
            }
            self._record_phase_complete("P4_defaults")
            self._log(f"Bootstrap Phase P4: Native defaults: {len(self.native_defaults)} parameters")

        except Exception as exc:
            self._record_phase_failure("P4_defaults", "B-DEF-001")
            raise BootstrapError("B-DEF-001", f"Defaults building failed: {exc}", "defaults")

    # ==========================================================================
    # Phase P5: Fallback Validation
    # ==========================================================================

    def _bootstrap_fallback(self) -> None:
        """
        Phase P5: Validate native fallback files and directories.

        Subclasses override for project-specific fallback logic.
        """
        self._record_phase_start("P5_fallback")
        try:
            self._record_phase_complete("P5_fallback")
            self._log("Bootstrap Phase P5: Fallback validation passed")
        except Exception as exc:
            self._record_phase_failure("P5_fallback", "B-FALL-001")
            raise BootstrapError("B-FALL-001", f"Fallback validation failed: {exc}", "fallback")

    # ==========================================================================
    # Phase P6: Environment Testing
    # ==========================================================================

    def _bootstrap_env(self) -> None:
        """
        Phase P6: Detect OS and test environment dependencies.

        Uses the injected ``os_detector`` for OS detection, then
        calls ``env_tester`` (if provided) to verify required/optional
        packages via ``importlib.import_module()``.

        Subclasses typically override this to supply project-specific
        dependencies and error codes.
        """
        self._record_phase_start("P6_env")
        try:
            # 1. OS detection
            if self._os_detector is not None:
                self.os_info = self._os_detector()
            else:
                self.os_info = "unknown"

            # 2. Environment/dependency testing (L20 — universal test_environment)
            if self._env_tester is not None:
                deps = self.config.get("dependencies", {}) if isinstance(self.config, dict) else {}
                self._env_test_results = self._env_tester(deps)
                if not self._env_test_results.get("ready", True):
                    errors = self._env_test_results.get("errors", [])
                    missing = ", ".join(errors) if errors else "unknown packages"
                    raise BootstrapError(
                        "B-ENV-002",
                        f"Required dependencies missing: {missing}",
                        "env",
                    )

            self._record_phase_complete("P6_env")
            self._log(f"Bootstrap Phase P6: OS detected: {self.os_info}")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P6_env", "B-ENV-001")
            raise BootstrapError("B-ENV-001", f"Environment testing failed: {exc}", "env")

    # ==========================================================================
    # Phase P7: Schema Resolution
    # ==========================================================================

    def _bootstrap_schema(self) -> None:
        """
        Phase P7: Resolve schema paths and load schema definitions.

        Subclasses override for project-specific schema loading.
        """
        self._record_phase_start("P7_schema")
        try:
            self._record_phase_complete("P7_schema")
            self._log("Bootstrap Phase P7: Schema resolved")
        except Exception as exc:
            self._record_phase_failure("P7_schema", "B-SCH-001")
            raise BootstrapError("B-SCH-001", f"Schema resolution failed: {exc}", "schema")

    # ==========================================================================
    # Phase P8: Parameters Resolution
    # ==========================================================================

    def _bootstrap_params(self) -> None:
        """
        Phase P8: Merge CLI + Schema + Native into effective parameters.

        Subclasses override for project-specific parameter merging.
        """
        self._record_phase_start("P8_params")
        try:
            # Merge: native defaults < schema params < CLI overrides
            schema_params = self.config.get("system_parameters", {}) if isinstance(self.config, dict) else {}
            self.effective_parameters = {**self.native_defaults, **schema_params}
            if self.cli_overrides_provided:
                self.effective_parameters.update(self.cli_args)

            self._record_phase_complete("P8_params")
            self._log(f"Bootstrap Phase P8: Parameters resolved: {len(self.effective_parameters)}")

        except Exception as exc:
            self._record_phase_failure("P8_params", "B-PAR-001")
            raise BootstrapError("B-PAR-001", f"Parameters resolution failed: {exc}", "params")

    def _bootstrap_params_for_ui(self, **ui_params: Any) -> None:
        """
        Phase P8 (UI mode): Merge UI + Schema + Native into effective parameters.

        UI values take highest precedence.
        """
        self._record_phase_start("P8_params")
        try:
            schema_params = self.config.get("system_parameters", {}) if isinstance(self.config, dict) else {}
            self.effective_parameters = {**self.native_defaults, **schema_params, **ui_params}
            self._record_phase_complete("P8_params")
            self._log(f"Bootstrap Phase P8 (UI): Parameters resolved: {len(self.effective_parameters)}")

        except Exception as exc:
            self._record_phase_failure("P8_params", "B-PAR-002")
            raise BootstrapError("B-PAR-002", f"UI parameters resolution failed: {exc}", "params")

    # ==========================================================================
    # Readiness gate — subclasses override
    # ==========================================================================

    def _run_readiness_gate(self) -> bool:
        """
        Run the project-setup readiness gate.

        Returns True if the project is ready, False otherwise.
        Subclasses override for project-specific validation.
        """
        if self._readiness_validator_factory is not None:
            try:
                validator = self._readiness_validator_factory(
                    project_root=self.project_root,
                    config_registry=self.config,
                )
                results = validator.validate_all(auto_create=True)
                return results.get("readiness", "NO") == "YES"
            except Exception:
                return False
        return True

    # ==========================================================================
    # Trace building — subclasses override
    # ==========================================================================

    def _build_preload_trace(self) -> None:
        """Build preload trace before context creation."""
        self._preload_trace = {
            "project_root": str(self.project_root),
            "config_dir": str(self.config_dir),
            "phase_status": {k: v.status for k, v in self._phase_status.items()},
            "bootstrap_summary": self.bootstrap_summary,
        }

    def _build_postload_trace(self, context: Any) -> None:
        """Build postload trace after context creation."""
        self._postload_trace = {
            "context_type": type(context).__name__,
            "resolved_paths": {k: str(v) for k, v in self.resolved_paths.items()},
            "effective_parameters": self.effective_parameters,
        }

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _run_phase(self, phase_id: str, phase_fn: Callable[[], None]) -> None:
        """Execute a single phase with tracking."""
        self._record_phase_start(phase_id)
        try:
            phase_fn()
            self._record_phase_complete(phase_id)
        except BootstrapError as exc:
            self._record_phase_failure(phase_id, exc.code)
            raise
        except Exception as exc:
            self._record_phase_failure(phase_id, f"B-{phase_id}-ERR")
            raise BootstrapError(
                f"B-{phase_id}-ERR",
                f"Phase {phase_id} failed: {exc}",
                phase_id,
            ) from exc

    def _log(self, msg: str, level: int = 1) -> None:
        """Log a message through the injected logger (if available)."""
        if self.logger is not None:
            try:
                if hasattr(self.logger, "info"):
                    self.logger.info(msg)
                elif hasattr(self.logger, "log"):
                    self.logger.log(level, msg)
            except Exception:
                pass
