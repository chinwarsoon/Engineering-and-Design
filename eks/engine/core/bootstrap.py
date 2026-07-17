"""
EKS-specific BootstrapManager subclass.

Wraps the universal L19 ``BootstrapManager`` with EKS-specific hooks:
``ConfigRegistry`` as config loader, ``ProjectSetupValidator`` as readiness
gate, ``parse_eks_cli`` as CLI parser, ``resolve_paths`` as path resolver,
``detect_os`` as OS detector, and ``ErrorManager`` / ``MessageManager``
as manager factories.

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.57 — EKS BootstrapManager subclass for L19 delegation.
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
        except Exception:
            pass

        # Fallback: SchemaLoader
        from .schema_loader import SchemaLoader
        return SchemaLoader(config_dir).load_all()

    def _eks_cli_parser(self, args: Optional[List[str]] = None):
        """L18 — parse EKS CLI args via the universal schema-driven parser."""
        from eks.engine.eks_engine_pipeline import parse_eks_cli
        result = parse_eks_cli(
            args,
            pipeline_root_dir=self.pipeline_root_dir,
            pipeline_dir=self.pipeline_dir,
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
    # Override phases for EKS-specific behavior
    # ------------------------------------------------------------------

    def _bootstrap_env(self) -> None:
        """P6 (EKS): OS detection + dependency testing via universal L20 test_environment().

        Calls the universal ``_bootstrap_env()`` which:
        1. Detects OS via L12 ``detect_os()``
        2. Tests dependencies via L20 ``test_environment()`` using
           ``dependencies`` from ``eks_config.json``

        On failure, raises ``BootstrapError("P1-BOOT-ENV", ...)`` with the
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
                    "P1-BOOT-ENV",
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
            self._record_phase_failure("P6_env", "P1-BOOT-ENV")
            raise BootstrapError(
                "P1-BOOT-ENV",
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
                    data_dir = self.project_root / eks_root / str(self.cli_args["data_dir"])
            self.effective_parameters["data_dir"] = data_dir

            self._record_phase_complete("P8_params")
            self._log(f"Bootstrap Phase P8 (EKS): Parameters resolved: {len(self.effective_parameters)}")

        except BootstrapError:
            raise
        except Exception as exc:
            self._record_phase_failure("P8_params", "P1-BOOT-PARAMS")
            raise BootstrapError("P1-BOOT-PARAMS", f"Parameters resolution failed: {exc}", "params")

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
            except Exception:
                pass

        if self.message_manager is None and self._message_manager_factory is not None:
            try:
                self.message_manager = self._message_manager_factory(
                    config_dir=self.config_dir, logger=self.logger,
                )
            except Exception:
                pass

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
                "P1-BOOT-CTX",
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

        # Lazy-init managers if needed
        if self.error_manager is None and self._error_manager_factory is not None:
            try:
                self.error_manager = self._error_manager_factory(
                    config_dir=self.config_dir, logger=self.logger, config=self.config,
                )
                ctx_params["em"] = self.error_manager
            except Exception:
                pass

        if self.message_manager is None and self._message_manager_factory is not None:
            try:
                self.message_manager = self._message_manager_factory(
                    config_dir=self.config_dir, logger=self.logger,
                )
                ctx_params["mm"] = self.message_manager
            except Exception:
                pass

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
