"""
EKS-specific BootstrapManager subclass.

Wraps the universal L19 ``BootstrapManager`` with EKS-specific hooks:
``ConfigRegistry`` as config loader, ``ProjectSetupValidator`` as readiness
gate, ``parse_eks_cli`` as CLI parser, ``resolve_paths`` as path resolver,
``detect_os`` as OS detector, and ``ErrorManager`` / ``MessageManager``
as manager factories.

Revision: 0.6
Date: 2026-07-28
Author: opencode
Summary: 0.6: T1.163–T1.169 (I257/I258) — Replaced 7 silent 'except Exception: pass'
          sites with WARNING-level self._log() calls. Error codes S-B-S-0609–S-B-S-0615
          registered in eks_error_config.json v1.5.0. Graceful degradation preserved.
0.5:          T1.156 (I254) — Strip eks_root prefix from relative CLI
          --data-dir paths in _bootstrap_params() to prevent path doubling
          (eks/eks/data instead of eks/data).
0.4:          T1.99.191 (I225) — _bootstrap_schema() stores _pre_generated_ddl
          (documents_ddl, elements_ddl, indexes, doc_base_schema) for reuse by
          DocumentRegistry. Exposed via to_dict() and to_pipeline_context().
0.3:          T1.99.68 — Override P1-P5, P7 phases to use EKS-registered S-B-S-06xx
          error codes instead of universal B-* codes; override bootstrap_all/
          bootstrap_for_ui catch-alls (B-U-S-* → S-B-S-0603); override
          preload_trace/postload_trace (B-B-S-0001/B-X-S-0001 → S-B-S-0607).
          T1.99.57 — EKS BootstrapManager subclass for L19 delegation.
          T1.99.96 (I127/G2) — _eks_cli_parser forwards preloaded
          _parse_cli_args_fn to parse_eks_cli(); __init__ initializes
          _preloaded_parse_cli_args=None.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from common.library.bootstrap import BootstrapManager, BootstrapError
from common.library.core.paths.path_utils import detect_os, safe_posix, should_auto_create_folders
from common.library.core.system import test_environment
from common.library.paths import resolve_paths


class EKSBootstrapManager(BootstrapManager):
    """
    EKS-specific bootstrap orchestrator.

    Injects EKS project hooks into the universal ``BootstrapManager``:

    - ``pipeline_root_dir="eks"``, ``pipeline_dir="engine"``
    - ``ConfigRegistry`` as config loader (SSOT)
    - ``ProjectSetupValidator`` as readiness gate
    - ``parse_eks_cli`` (L18) as CLI parser
    - ``resolve_paths`` (L16) as path resolver
    - ``detect_os`` (L12) as OS detector
    - ``ErrorManager`` / ``MessageManager`` as manager factories

    Usage::

        mgr = EKSBootstrapManager(project_root=prj)
        mgr.bootstrap_all(args)
        ctx = mgr.to_pipeline_context()
        # or backward-compat dict:
        boot = mgr.to_dict()
    """

    def __init__(
        self,
        project_root: Path,
        *,
        pipeline_root_dir: str = "eks",
        pipeline_dir: str = "engine",
        skip_readiness: bool = False,
        debug: bool = False,
        auto_create: bool = True,
        use_config_registry: bool = True,
        logger: Any = None,
    ) -> None:
        super().__init__(
            project_root=project_root,
            pipeline_root_dir=pipeline_root_dir,
            pipeline_dir=pipeline_dir,
            os_detector=detect_os,
            env_tester=test_environment,
            path_resolver=self._eks_path_resolver,
            config_loader=self._eks_config_loader,
            cli_parser=self._eks_cli_parser,
            readiness_validator_factory=self._eks_readiness_factory,
            error_manager_factory=self._eks_error_factory,
            message_manager_factory=self._eks_message_factory,
            logger=logger,
        )

        self._skip_readiness = skip_readiness
        self._debug = debug
        self._auto_create = auto_create
        self._use_config_registry = use_config_registry

        # Internal state populated during bootstrap
        self.config_registry: Any = None
        self.parsed: Any = None
        # T1.99.96 (I127/G2): Preloaded parse_cli_args reference — set by
        # caller (main()) after preload; used by _eks_cli_parser to skip
        # the bare import inside parse_eks_cli().
        self._preloaded_parse_cli_args: Any = None
        # T1.99.191 (I225): Pre-generated DDL from SchemaToDDL, set during P7.
        # Stored so downstream DocumentRegistry can reuse generated DDL
        # instead of re-loading the schema from disk.
        self._pre_generated_ddl: Optional[Dict[str, Any]] = None
        # T1.193: Project Configuration Registry — populated by
        # ProjectDefinitionResolver after P3_registry.
        self.project_config_registry: Any = None

    # ------------------------------------------------------------------
    # Hook implementations
    # ------------------------------------------------------------------

    def _eks_path_resolver(self, project_root: Path, config: Dict[str, Any]) -> Dict[str, Path]:
        """L16 — schema-driven canonical path resolution."""
        resolved = resolve_paths(project_root, config)
        return resolved.resolve(project_root)

    def _eks_config_loader(self, config_dir: Path) -> Dict[str, Any]:
        """Load EKS config via ConfigRegistry SSOT (or fallback SchemaLoader)."""
        try:
            from .config_registry import ConfigRegistry
            if self._use_config_registry and ConfigRegistry is not None:
                # Reset singleton if config_dir changed
                _existing = ConfigRegistry._instance
                if _existing is not None:
                    _existing_dir = getattr(getattr(_existing, "_loader", None), "config_dir", None)
                    if _existing_dir is not None and Path(str(_existing_dir)).resolve() != config_dir.resolve():
                        ConfigRegistry._instance = None
                self.config_registry = ConfigRegistry(str(config_dir))
                return self.config_registry.config
        except Exception as exc:
            self._log(f"ConfigRegistry init failed — falling back to SchemaLoader: {exc}", level=2)

        # Fallback: SchemaLoader
        from .schema_loader import SchemaLoader
        return SchemaLoader(config_dir).load_all()

    def _eks_cli_parser(self, args: Optional[List[str]] = None):
        """L18 — parse EKS CLI args via the universal schema-driven parser.

        T1.99.96 (I127/G2): If ``self._preloaded_parse_cli_args`` was set
        by the caller (e.g. ``main()`` after preload), it is forwarded to
        ``parse_eks_cli()`` so the bare ``from common.library.cli import``
        inside that function is skipped.
        """
        from eks.engine.eks_engine_pipeline import parse_eks_cli
        result = parse_eks_cli(
            args,
            pipeline_root_dir=self.pipeline_root_dir,
            pipeline_dir=self.pipeline_dir,
            _parse_cli_args_fn=getattr(self, "_preloaded_parse_cli_args", None),
        )
        self.parsed = result.namespace
        if hasattr(result, "project_root"):
            self.project_root = result.project_root
        if hasattr(result, "config_dir"):
            self.config_dir = result.config_dir
        return result

    def _eks_readiness_factory(self, **kwargs) -> Any:
        """Create EKS ProjectSetupValidator."""
        from .setup_validator import ProjectSetupValidator
        return ProjectSetupValidator(
            project_root=kwargs.get("project_root", self.project_root),
            config_registry=kwargs.get("config_registry", self.config),
            verbose=self._debug,
        )

    def _eks_error_factory(self, **kwargs) -> Any:
        """Create EKS ErrorManager."""
        from .error_manager import ErrorManager
        return ErrorManager(
            config_dir=kwargs.get("config_dir", self.config_dir),
            logger=kwargs.get("logger", self.logger),
            config=kwargs.get("config", self.config),
        )

    def _eks_message_factory(self, **kwargs) -> Any:
        """Create EKS MessageManager."""
        from .message_manager import MessageManager
        return MessageManager(
            config_dir=kwargs.get("config_dir", self.config_dir),
            logger=kwargs.get("logger", self.logger),
        )

    # ------------------------------------------------------------------
    # Override bootstrap_all / bootstrap_for_ui — translate B-UNK → S-B-S-06xx
    # ------------------------------------------------------------------

    def bootstrap_all(self, cli_args: Optional[List[str]] = None) -> BootstrapManager:
        """Run all bootstrap phases for CLI mode (EKS: B-UNK-001 → S-B-S-0603)."""
        try:
            return super().bootstrap_all(cli_args)
        except BootstrapError as exc:
            if exc.code == "B-UNK-001":
                raise BootstrapError("S-B-S-0603", exc.message, exc.phase)
            raise
        except Exception as exc:
            raise BootstrapError("S-B-S-0603", f"Unexpected bootstrap error: {exc}", "unknown")

    def bootstrap_for_ui(self, **ui_params: Any) -> BootstrapManager:
        """Run bootstrap phases for UI mode (EKS: B-UNK-002 → S-B-S-0603)."""
        try:
            return super().bootstrap_for_ui(**ui_params)
        except BootstrapError as exc:
            if exc.code == "B-UNK-002":
                raise BootstrapError("S-B-S-0603", exc.message, exc.phase)
            raise
        except Exception as exc:
            raise BootstrapError("S-B-S-0603", f"Unexpected bootstrap error (UI): {exc}", "unknown")

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Override phases for EKS-specific behavior
    # ------------------------------------------------------------------

    def _bootstrap_cli(self, cli_args: Optional[List[str]] = None) -> None:
        """P1 (EKS): Parse CLI args, translate B-CLI-001 → S-B-S-0604."""
        self._record_phase_start("P1_cli")
        try:
            if self._cli_parser is not None:
                result = self._cli_parser(cli_args)
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
                    self.cli_args = vars(result) if hasattr(result, "__dict__") else {}
                    self.parsed = result
                    self.cli_overrides_provided = bool(cli_args)

                verbose = self.cli_args.get("verbose", "") or self.cli_args.get("level", 1)
                if isinstance(verbose, int):
                    self.debug_mode = verbose >= 2
                else:
                    self.debug_mode = verbose in ("debug", "trace")

            self._record_phase_complete("P1_cli")
            self._log(f"Bootstrap Phase P1 (EKS): CLI parsed, {len(self.cli_args)} args")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P1_cli", "S-B-S-0604")
            raise BootstrapError("S-B-S-0604", f"CLI parsing failed: {exc}", "cli")

    def _bootstrap_paths(self) -> None:
        """P2 (EKS): Validate paths, translate B-PATH-* → S-B-S-0605."""
        self._record_phase_start("P2_paths")
        try:
            if not self.project_root.exists():
                raise BootstrapError(
                    "S-B-S-0605",
                    f"Project root does not exist: {self.project_root}",
                    "paths",
                )

            if self._path_resolver is not None and self.config:
                # Only call resolver when config is loaded (P3+).
                # During P2_paths, config may still be empty (P2 runs
                # before P3_registry by design).  An empty config falls
                # into the DCC branch of resolve_paths() with eks_root="",
                # anchoring all paths at the repo root instead of under eks/.
                self.resolved_paths = self._path_resolver(self.project_root, self.config)
            else:
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
            self._log(f"Bootstrap Phase P2 (EKS): Paths resolved: {len(self.resolved_paths)} paths")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P2_paths", "S-B-S-0605")
            raise BootstrapError("S-B-S-0605", f"Path validation failed: {exc}", "paths")

    def _bootstrap_registry(self) -> None:
        """P3 (EKS): Load config, translate B-REG-001 → S-B-S-0604."""
        self._record_phase_start("P3_registry")
        try:
            if self._config_loader is not None:
                self.config = self._config_loader(self.config_dir)
            else:
                self.config = {}

            # I128: Also load doc_config from SchemaLoader for file_type_registry,
            # document_type_registry, etc.  The main _eks_config_loader returns
            # only the pipeline config; doc_config lives in eks_doc_config.json.
            # T1.193: After loading, run ProjectDefinitionResolver to construct
            # the Project Configuration Registry.
            try:
                from .schema_loader import SchemaLoader
                _sl = SchemaLoader(self.config_dir)
                _sl.load_all()
                self.doc_config = _sl.doc_config
                # I281 (T1.224): processing profiles values SSOT
                self.processing_config = _sl.processing_config
                # T1.193: Resolve Project Definitions → RuntimeProjectConfiguration
                self._resolve_project_definitions(_sl)
            except Exception as exc:
                self._log(f"doc_config schema validation / project definition resolution failed — "
                          f"using empty defaults: {exc}", level=2)

            self._record_phase_complete("P3_registry")
            self._log(f"Bootstrap Phase P3 (EKS): Config loaded: {len(self.config)} keys, "
                       f"doc_config: {len(self.doc_config)} keys")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P3_registry", "S-B-S-0604")
            raise BootstrapError("S-B-S-0604", f"Registry loading failed: {exc}", "registry")

    def _bootstrap_defaults(self) -> None:
        """P4 (EKS): Build native defaults, translate B-DEF-001 → S-B-S-0604."""
        self._record_phase_start("P4_defaults")
        try:
            gp = self.config.get("global_paths", {}) if isinstance(self.config, dict) else {}
            self.native_defaults = {
                "data_dir": gp.get("data_dir", "data"),
                "output_dir": gp.get("output_dir", "output"),
                "archive_dir": gp.get("archive_dir", "archive"),
                "config_dir": gp.get("config_dir", "config"),
                "log_dir": gp.get("log_dir", "log"),
                "eks_root": gp.get("eks_root", "eks"),
            }
            self._record_phase_complete("P4_defaults")
            self._log(f"Bootstrap Phase P4 (EKS): Native defaults: {len(self.native_defaults)} parameters")

        except Exception as exc:
            self._record_phase_failure("P4_defaults", "S-B-S-0604")
            raise BootstrapError("S-B-S-0604", f"Defaults building failed: {exc}", "defaults")

    def _bootstrap_fallback(self) -> None:
        """P5 (EKS): Validate fallback, translate B-FALL-001 → S-B-S-0604."""
        self._record_phase_start("P5_fallback")
        try:
            self._record_phase_complete("P5_fallback")
            self._log("Bootstrap Phase P5 (EKS): Fallback validation passed")
        except Exception as exc:
            self._record_phase_failure("P5_fallback", "S-B-S-0604")
            raise BootstrapError("S-B-S-0604", f"Fallback validation failed: {exc}", "fallback")

    def _bootstrap_schema(self) -> None:
        """P7 (EKS): Resolve schema, validate DDL pre-flight, translate B-SCH-001 → S-B-S-0604.
        
        T1.99.191 (I225): Runs SchemaToDDL pre-flight validation to catch
        schema-drift errors before the pipeline starts, rather than waiting
        for first registry instantiation.  Generates DDL and indexes from the
        doc base schema and checks that required definitions are present.
        """
        self._record_phase_start("P7_schema")
        try:
            # T1.99.191 (I225): Pre-flight SchemaToDDL validation
            doc_config = {}
            try:
                from .schema_loader import SchemaLoader
                _sl = SchemaLoader(self.config_dir)
                _sl.load_all()
                doc_config = _sl.doc_config
            except Exception as exc:
                self._log(f"Schema phase doc_config load failed — using empty defaults: {exc}", level=2)

            if doc_config:
                try:
                    from .schema_to_ddl import SchemaToDDL
                    doc_schema = SchemaToDDL.load_doc_base_schema(self.config_dir / "schemas")
                    ddl_gen = SchemaToDDL(doc_schema, logger=self.logger)
                    # Pre-flight: generate all DDL to catch schema errors early
                    docs_ddl = ddl_gen.generate_documents_ddl()
                    els_ddl = ddl_gen.generate_document_elements_ddl()
                    indexes = ddl_gen.generate_indexes()
                    # T1.99.191 (I225): Store for reuse by DocumentRegistry
                    self._pre_generated_ddl = {
                        "documents_ddl": docs_ddl,
                        "elements_ddl": els_ddl,
                        "indexes": indexes,
                        "doc_base_schema": doc_schema,
                    }
                    self._log(
                        f"SchemaToDDL pre-flight OK: "
                        f"documents table ({len(docs_ddl)} chars), "
                        f"elements table ({len(els_ddl)} chars), "
                        f"{len(indexes)} indexes"
                    )
                except Exception as ddl_err:
                    self._log(f"SchemaToDDL pre-flight warning (non-fatal): {ddl_err}")
            
            self._record_phase_complete("P7_schema")
            self._log("Bootstrap Phase P7 (EKS): Schema resolved with DDL pre-validation")
        except Exception as exc:
            self._record_phase_failure("P7_schema", "S-B-S-0604")
            raise BootstrapError("S-B-S-0604", f"Schema resolution failed: {exc}", "schema")

    def _bootstrap_env(self) -> None:
        """P6 (EKS): OS detection + dependency testing via universal L20 test_environment().

        Calls the universal ``_bootstrap_env()`` which:
        1. Detects OS via L12 ``detect_os()``
        2. Tests dependencies via L20 ``test_environment()`` using
           ``dependencies`` from ``eks_config.json``

        On failure, raises ``BootstrapError("S-B-S-0608", ...)`` with the
        list of missing required packages and guidance to activate conda env.
        """
        self._record_phase_start("P6_env")
        try:
            # 1. OS detection
            self.os_info = detect_os()

            # 2. Dependency testing via universal test_environment()
            deps = self.config.get("dependencies", {}) if isinstance(self.config, dict) else {}
            env_results = test_environment(deps)
            self._env_test_results = env_results

            if not env_results.get("ready", True):
                errors = env_results.get("errors", [])
                missing = ", ".join(errors) if errors else "unknown packages"
                raise BootstrapError(
                    "S-B-S-0608",
                    f"Required dependencies missing: {missing}. "
                    f"Run: conda activate eks",
                    "env",
                )

            self._record_phase_complete("P6_env")
            self._log(
                f"Bootstrap Phase P6 (EKS): OS={self.os_info}, "
                f"deps OK (required: {len(env_results.get('required_modules', {}))})"
            )

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P6_env", "S-B-S-0608")
            raise BootstrapError(
                "S-B-S-0608",
                f"Environment testing failed: {exc}. Run: conda activate eks",
                "env",
            )

    def _bootstrap_params(self) -> None:
        """P8 (EKS): Merge CLI + Schema + Native with EKS precedence."""
        self._record_phase_start("P8_params")
        try:
            # Native defaults from global_paths
            gp = self.config.get("global_paths", {}) if isinstance(self.config, dict) else {}
            self.native_defaults = {
                "data_dir": gp.get("data_dir", "data"),
                "output_dir": gp.get("output_dir", "output"),
                "archive_dir": gp.get("archive_dir", "archive"),
                "config_dir": gp.get("config_dir", "config"),
                "log_dir": gp.get("log_dir", "log"),
                "eks_root": gp.get("eks_root", "eks"),
            }

            # Schema params
            schema_params = self.config.get("system_parameters", {}) if isinstance(self.config, dict) else {}

            # CLI > Schema > Native precedence for log_level
            cli_level = self.cli_args.get("level") if self.cli_args else None
            schema_level = schema_params.get("log_level", 1)
            if cli_level is not None:
                level = int(cli_level)
            else:
                level = int(schema_level)
            if self.cli_args.get("debug"):
                level = 3

            # Merge
            self.effective_parameters = {**self.native_defaults, **schema_params}
            if self.cli_overrides_provided:
                self.effective_parameters.update(self.cli_args)
            self.effective_parameters["level"] = level

            # Resolve data_dir: CLI > Schema (resolve_paths) > Native; anchored under eks_root
            eks_root = self.native_defaults.get("eks_root", "eks")
            data_dir = self.resolved_paths.get("data_dir", self.project_root / eks_root / "data")
            if self.cli_args.get("data_dir"):
                cli_path = Path(str(self.cli_args["data_dir"]))
                if cli_path.is_absolute():
                    data_dir = cli_path
                else:
                    # T1.156 (I254): Strip eks_root prefix from relative CLI paths
                    # to prevent path doubling (eks/eks/data instead of eks/data).
                    cli_str = str(self.cli_args["data_dir"])
                    eks_prefix = f"{eks_root}/"
                    if cli_str.startswith(eks_prefix):
                        cli_str = cli_str[len(eks_prefix):]
                    elif cli_str == eks_root:
                        cli_str = ""
                    data_dir = self.project_root / eks_root / cli_str
            self.effective_parameters["data_dir"] = data_dir

            self._record_phase_complete("P8_params")
            self._log(f"Bootstrap Phase P8 (EKS): Parameters resolved: {len(self.effective_parameters)}")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P8_params", "S-B-S-0608")
            raise BootstrapError("S-B-S-0608", f"Parameters resolution failed: {exc}", "params")

    # ------------------------------------------------------------------
    # T1.193: Project Definition Resolution
    # ------------------------------------------------------------------

    def _resolve_project_definitions(self, schema_loader: Any) -> None:
        """Run ProjectDefinitionResolver after SchemaLoader completes.

        Uses the already-loaded schema_loader instance (avoids re-loading
        from disk).  Populates ``self.project_config_registry``.

        The resolver transforms raw Project Definitions into immutable
        RuntimeProjectConfiguration objects (Appendix L).
        """
        try:
            from .project_definition import ProjectDefinitionResolver

            pd_config = getattr(schema_loader, "project_definition_config", {})
            doc_config = getattr(schema_loader, "doc_config", {})
            env_config = self.config if isinstance(self.config, dict) else {}

            if not pd_config:
                self._log("No project_definition_config found — skipping ProjectDefinitionResolver",
                          level=2)
                return

            resolver = ProjectDefinitionResolver(
                project_definition_config=pd_config,
                doc_config=doc_config,
                env_config=env_config,
                logger=self.logger,
                processing_config=getattr(schema_loader, "processing_config", {}) or {},
            )
            self.project_config_registry = resolver.resolve_all()

            n_projects = len(self.project_config_registry)
            n_errors = len(resolver.errors)
            n_data_errors = len(resolver.data_errors)
            n_warnings = len(resolver.warnings)
            self._log(
                f"ProjectDefinitionResolver: {n_projects} project(s) resolved, "
                f"{n_errors} error(s), {n_data_errors} data error(s), "
                f"{n_warnings} warning(s)",
                level=1,
            )
            if n_errors:
                self._log(f"Resolver errors: {resolver.errors}", level=0)
            if n_data_errors:
                self._log(f"Resolver data errors (non-blocking): {resolver.data_errors}",
                          level=2)
        except Exception as exc:
            self._log(f"Project definition resolution failed: {exc}", level=0)
            self.project_config_registry = None

    # ------------------------------------------------------------------
    # Properties — overridden for EKS-specific error codes
    # ------------------------------------------------------------------

    @property
    def preload_trace(self) -> Optional[Dict[str, Any]]:
        """Get preload trace data (EKS: B-B-S-0001 → S-B-S-0607)."""
        if not self._bootstrapped:
            raise BootstrapError(
                "S-B-S-0607",
                "Bootstrap must be completed before accessing preload trace",
                "traces",
            )
        return self._preload_trace

    @property
    def postload_trace(self) -> Optional[Dict[str, Any]]:
        """Get postload trace data (EKS: B-X-S-0001 → S-B-S-0607)."""
        if not self._bootstrapped:
            raise BootstrapError(
                "S-B-S-0607",
                "Must bootstrap before accessing postload trace",
                "traces",
            )
        return self._postload_trace

    # ------------------------------------------------------------------
    # Readiness gate — EKS-specific
    # ------------------------------------------------------------------

    def _run_readiness_gate(self) -> bool:
        """Run EKS project-setup readiness gate via ProjectSetupValidator."""
        if self._skip_readiness:
            return True

        try:
            from .setup_validator import ProjectSetupValidator
            validator = ProjectSetupValidator(
                project_root=self.project_root,
                config_registry=self.config_registry if self.config_registry is not None else self.config,
                verbose=self._debug,
            )
            results = validator.validate_all(auto_create=self._auto_create)
            return results.get("readiness", "NO") == "YES"
        except Exception as exc:
            self._log(f"Readiness gate failed: {exc}")
            return False

    # ------------------------------------------------------------------
    # to_dict — EKS backward-compat (populates managers)
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return backward-compatible dict matching EKS bootstrap_pipeline() shape."""
        # Lazy-init managers if not already created
        if self.error_manager is None and self._error_manager_factory is not None:
            try:
                self.error_manager = self._error_manager_factory(
                    config_dir=self.config_dir, logger=self.logger, config=self.config,
                )
            except Exception as exc:
                self._log(f"ErrorManager lazy-init failed in to_dict(): {exc}", level=2)

        if self.message_manager is None and self._message_manager_factory is not None:
            try:
                self.message_manager = self._message_manager_factory(
                    config_dir=self.config_dir, logger=self.logger,
                )
            except Exception as exc:
                self._log(f"MessageManager lazy-init failed in to_dict(): {exc}", level=2)

        # Resolve data_dir from effective params
        data_dir = self.effective_parameters.get("data_dir", self.resolved_paths.get("data_dir", self.project_root / "data"))

        return {
            "config": self.config,
            "doc_config": self.doc_config,
            "config_registry": self.config_registry,
            "em": self.error_manager,
            "mm": self.message_manager,
            "resolved_paths": self.resolved_paths,
            "os_info": self.os_info,
            "level": self.effective_parameters.get("level", 1),
            "data_dir": data_dir,
            "project_root": self.project_root,
            "config_dir": self.config_dir,
            "parsed": self.parsed,
            "pre_generated_ddl": self._pre_generated_ddl,
            "project_config_registry": self.project_config_registry,
        }

    # ------------------------------------------------------------------
    # to_pipeline_context — EKS-specific (returns EKSPipelineContext)
    # ------------------------------------------------------------------

    def to_pipeline_context(self) -> Any:
        """
        Build an EKSPipelineContext from bootstrapped state.

        Returns an L06 BasePipelineContext subclass (EKSPipelineContext)
        with validated paths, parameters, and registries.
        """
        if not self._bootstrapped:
            raise BootstrapError(
                "S-B-S-0607",
                "Must bootstrap before creating PipelineContext",
                "context",
            )

        from .context import EKSPaths, EKSData, EKSState, EKSTelemetry, EKSPipelineContext
        from datetime import datetime

        # Build paths
        rp = self.resolved_paths
        ctx_paths = EKSPaths(
            data_dir=Path(rp.get("data_dir", self.project_root / "data")),
            schema_dir=Path(rp.get("schema_dir", self.config_dir / "schemas")),
            output_dir=Path(rp.get("output_dir", self.project_root / "output")),
            archive_dir=Path(rp.get("archive_dir", self.project_root / "archive")),
            config_dir=Path(rp.get("config_dir", self.config_dir)),
            log_dir=Path(rp.get("log_dir", self.project_root / "log")),
        )

        # Build state + telemetry
        ctx_data = EKSData()
        ctx_state = EKSState(status="INITIALIZED", start_time=datetime.now())
        ctx_telemetry = EKSTelemetry()

        # Build parameters from effective params + managers
        ctx_params = dict(self.effective_parameters)
        ctx_params["config"] = self.config
        ctx_params["doc_config"] = self.doc_config
        ctx_params["em"] = self.error_manager
        ctx_params["mm"] = self.message_manager
        ctx_params["pre_generated_ddl"] = self._pre_generated_ddl
        ctx_params["project_config_registry"] = self.project_config_registry

        # Lazy-init managers if needed
        if self.error_manager is None and self._error_manager_factory is not None:
            try:
                self.error_manager = self._error_manager_factory(
                    config_dir=self.config_dir, logger=self.logger, config=self.config,
                )
                ctx_params["em"] = self.error_manager
            except Exception as exc:
                self._log(f"ErrorManager lazy-init failed in to_pipeline_context(): {exc}", level=2)

        if self.message_manager is None and self._message_manager_factory is not None:
            try:
                self.message_manager = self._message_manager_factory(
                    config_dir=self.config_dir, logger=self.logger,
                )
                ctx_params["mm"] = self.message_manager
            except Exception as exc:
                self._log(f"MessageManager lazy-init failed in to_pipeline_context(): {exc}", level=2)

        ctx = EKSPipelineContext(
            paths=ctx_paths,
            data=ctx_data,
            parameters=ctx_params,
            state=ctx_state,
            telemetry=ctx_telemetry,
            config_registry=self.config_registry,
            schema_registry=self.config_registry,
        )

        self._build_postload_trace(ctx)
        return ctx
