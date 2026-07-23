"""
Pipeline orchestration functions for the EKS pipeline.

Extracted from ``eks_engine_pipeline.py`` (I233).  Zero module-level runtime
globals — all paths received as explicit parameters.

Revision: 1.0
Date: 2026-07-23
Author: opencode
Summary: I233 split — pipeline runner functions extracted from eks_engine_pipeline.py.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from eks.engine.pipeline_engine.cli import _parse_early_verbosity


def _read_system_params(config_dir: Path) -> Dict[str, Any]:
    """Load config to resolve schema-driven system-parameter defaults (L15)."""
    try:
        from eks.engine.core.config_registry import ConfigRegistry
        if ConfigRegistry is not None:
            return ConfigRegistry(str(config_dir)).config
        from eks.engine.core.schema_loader import SchemaLoader
        return SchemaLoader(config_dir).load_all()
    except Exception:
        return {}


def _last_phase(phase: str) -> str:
    return {"A": "A", "B": "B", "C": "C", "full": "C"}.get(phase, "C")


def _print_human_summary(summary: Dict[str, Any]) -> None:
    pa = summary.get("phase_a", {}) or {}
    pb = summary.get("phase_b", {}) or {}
    pc = summary.get("phase_c", {}) or {}
    print(f"Phase A: discovered={pa.get('discovered')} valid={pa.get('valid')} "
          f"registered={pa.get('registered')}")
    print(f"Phase B: success={pb.get('success')} partial={pb.get('partial')} "
          f"failed={pb.get('failed')}")
    print(f"Phase C: flagged={pc.get('flagged')}")


def bootstrap_pipeline(
    project_root: Path,
    args: Optional[list] = None,
    logger: Any = None,
    skip_readiness: bool = False,
    debug: bool = False,
    use_config_registry: bool = True,
    auto_create: bool = True,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
) -> Dict[str, Any]:
    """Build config + managers and run the project-setup readiness gate.

    T1.99.58: I109 — thin wrapper that delegates to the universal
    ``EKSBootstrapManager`` (L19). Returns a backward-compatible dict
    so existing callers (``phase1_server.py``, tests) work unchanged.

    Args:
        project_root: Repository root (used to resolve schema-driven paths).
        args: Optional CLI argument list (``None`` -> ``sys.argv[1:]``).
        logger: Optional logger (UniversalLogger-compatible) for managers + telemetry.
        skip_readiness: Bypass the project-setup readiness gate (G5 override).
        debug: Enable verbose validator output.
        use_config_registry: Load config via the ``ConfigRegistry`` SSOT (T1.99.6).
        auto_create: Auto-create missing folders.
        pipeline_root_dir: Anchor directory name for project-root discovery
            (default ``"eks"``; I104 — DCC-faithful, caller owns the literal).
        pipeline_dir: Pipeline sub-directory name within pipeline_root_dir
            (default ``"engine"``; I104 — DCC-faithful, caller owns the literal).

    Returns:
        dict with keys: config, doc_config, config_registry, em, mm, resolved_paths,
        os_info, level, data_dir, project_root, config_dir, parsed (namespace)
    """
    from eks.engine.core.bootstrap import EKSBootstrapManager

    project_root = Path(project_root)

    mgr = EKSBootstrapManager(
        project_root=project_root,
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
        skip_readiness=skip_readiness,
        debug=debug,
        auto_create=auto_create,
        use_config_registry=use_config_registry,
        logger=logger,
    )
    mgr.bootstrap_all(args)

    if not skip_readiness:
        ready = mgr._run_readiness_gate()
        if not ready:
            from common.library.bootstrap import BootstrapError
            raise BootstrapError(
                "P1-BOOT-READINESS",
                "Bootstrap readiness gate failed — project setup not ready",
                "readiness",
            )

    return mgr.to_dict()


def run_pipeline(
    project_root: Path,
    data_dir: Path,
    recursive: bool = True,
    config_dir: Optional[Path] = None,
    logger: Any = None,
    skip_readiness: bool = False,
    debug: bool = False,
    phase: str = "full",
    checkpoint_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
    registry: Any = None,
    on_phase: Optional[Callable[[str], None]] = None,
    auto_create: bool = True,
    context: Optional[Any] = None,
    _PipelineOrchestrator_cls: Any = None,
    _DocumentRegistry_cls: Any = None,
) -> Dict[str, Any]:
    """Run the Phase 1 pipeline, optionally a single phase. Returns a result dict.

    Mirrors DCC's single ``run_engine_pipeline(context)`` funnel so the CLI,
    the HTTP backend, and a future UI entry share one implementation. The
    single A->B->C coordination loop lives in
    ``PipelineOrchestrator.run_full_pipeline`` (T1.99.10); this wrapper only
    dispatches per ``phase`` and forwards progress/checkpoint callbacks.

    Args:
        project_root: Repository root.
        data_dir: Data directory containing documents to process (relative to root).
        recursive: Recurse into subdirectories.
        config_dir: EKS config directory (default ``<root>/eks/config``).
        logger: Optional logger instance.
        skip_readiness: Bypass the readiness gate.
        debug: Verbose validator output.
        phase: ``A``, ``B``, ``C``, or ``full`` (default ``full``).
        checkpoint_dir: Directory for per-phase checkpoint JSON artifacts.
        job_id: Job id used to name checkpoint files.
        registry: Optional shared ``DocumentRegistry`` instance.
        on_phase: Optional callback invoked with phase letter after each phase.
        context: Optional pre-seeded EKSPipelineContext (T1.99.42). If provided,
            bootstrap is skipped and the context is used directly.
        _PipelineOrchestrator_cls: Preloaded PipelineOrchestrator class (I127).
        _DocumentRegistry_cls: Preloaded DocumentRegistry class (I127).

    Returns:
        dict with keys: summary (depends on phase), em, mm, config_registry,
        resolved_paths, context (EKSPipelineContext instance)
    """
    if _PipelineOrchestrator_cls is not None:
        PipelineOrchestrator = _PipelineOrchestrator_cls
    else:
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
    if _DocumentRegistry_cls is not None:
        DocumentRegistry = _DocumentRegistry_cls
    else:
        from eks.engine.core.registry import DocumentRegistry

    if context is not None:
        em = context.parameters.get("em")
        mm = context.parameters.get("mm")
        orchestrator = PipelineOrchestrator(
            context.parameters.get("config", {}),
            context.parameters.get("doc_config", {}),
            registry or DocumentRegistry(logger=logger),
            logger=logger,
            use_telemetry=False,
            error_manager=em,
            message_manager=mm,
        )
        orchestrator.context = context
        config = context.parameters.get("config", {})
        doc_config = context.parameters.get("doc_config", {})
        resolved = context.paths.to_dict()
        config_registry = context.config_registry
    else:
        boot = bootstrap_pipeline(
            project_root=project_root,
            args=[],
            logger=logger,
            skip_readiness=skip_readiness,
            debug=debug,
            auto_create=auto_create,
        )
        config = boot["config"]
        doc_config = boot["doc_config"]
        em = boot["em"]
        mm = boot["mm"]
        resolved = boot["resolved_paths"]
        config_registry = boot["config_registry"]

        if registry is None:
            registry = DocumentRegistry(logger=logger)

        orchestrator = PipelineOrchestrator(
            config, doc_config, registry, logger=logger,
            use_telemetry=False, error_manager=em, message_manager=mm,
        )

        params = {**config.get("global_parameters", {}), **config.get("project_setup", {})}

        orchestrator.initialize_context(
            data_dir=project_root / data_dir,
            schema_dir=resolved["schema_dir"],
            output_dir=resolved["output_dir"],
            archive_dir=resolved["archive_dir"],
            config_dir=resolved["config_dir"],
            log_dir=resolved["log_dir"],
            parameters=params,
            config_registry=config_registry,
            schema_registry=config_registry,
            checkpoint_state=None,
        )

    root = project_root / data_dir

    def _after(ph: str) -> None:
        if on_phase:
            on_phase(ph)
        if checkpoint_dir is not None and job_id is not None:
            orchestrator.save_checkpoint(
                ph, checkpoint_path=Path(checkpoint_dir) / f"checkpoint_{job_id}_{ph}.json"
            )

    if phase == "A":
        summary = {"phase_a": orchestrator.run_phase_a(root, recursive=recursive)}
        _after("A")
    elif phase == "B":
        summary = {"phase_b": orchestrator.run_phase_b(root, recursive=recursive)}
        _after("B")
    elif phase == "C":
        summary = {"phase_c": orchestrator.run_phase_c()}
        _after("C")
    else:
        summary = orchestrator.run_full_pipeline(
            root, recursive=recursive,
            on_phase=on_phase, checkpoint_dir=checkpoint_dir, job_id=job_id,
        )

    return {
        "summary": summary,
        "em": em,
        "mm": mm,
        "config_registry": config_registry,
        "resolved_paths": resolved,
        "context": orchestrator.context,
    }


def _preload_infrastructure(
    args: Optional[list] = None,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
) -> Dict[str, Any]:
    """T1.99.81 (I117): Pre-bootstrap infrastructure loader — pure-stdlib guard.

    Imports and discovers project-root BEFORE ``BootstrapManager``,
    collecting ALL errors into a single result dict so the caller can
    report them at once. No bare ``ImportError`` or ``ModuleNotFoundError``
    reaches the user — every ``common.library`` import is individually
    try/except-guarded.

    This function MUST remain at module level (not inside ``common.library``)
    because it protects the import of ``common.library`` itself — putting
    it inside the package would create a circular dependency.

    Design principle (I117 / universal pipeline §3.23 preload pattern):
    Every pipeline entry-point should have a stdlib-only preload function
    that gates all ``common.library`` imports. This is NOT a library function
    — it is a **pattern** that each project replicates with its own
    ``pipeline_root_dir`` / ``pipeline_dir`` literals.

    Args:
        args: Optional CLI argument list (None -> sys.argv[1:]).
        pipeline_root_dir: Anchor directory name for project-root discovery
            (e.g. ``"eks"`` for EKS, ``"dcc"`` for DCC).
        pipeline_dir: Pipeline sub-directory name within pipeline_root_dir
            (e.g. ``"engine"`` for EKS, ``"workflow"`` for DCC).

    Returns:
        dict with keys:
        - ``ready`` (bool): True if all infrastructure loaded successfully.
        - ``errors`` (List[str]): Collected error messages (empty if ready).
        - ``project_root`` (Path | None): Discovered project root.
        - ``early_level`` (int): Resolved verbosity level (0–3).
        - ``debug_mode`` (bool): Whether --debug flag was set.
        - ``safe_posix`` (Callable | None): Path serialization helper.
        - ``should_auto_create_folders`` (Callable | None): OS-gated folder creation guard.
        - ``_UniversalLogger`` (type | None): Imported class (not instantiated).
        - ``_TelemetryHeartbeat`` (type | None): Imported class (not instantiated).
        - ``_EKSBootstrapManager`` (type | None): Imported class (not instantiated).
        - ``_EngineInput`` (type | None): Imported class (T1.99.95/I127).
        - ``_EngineOutput`` (type | None): Imported class (T1.99.95/I127).
        - ``_parse_cli_args`` (Callable | None): Imported function (T1.99.96/I127).
        - ``_PipelineOrchestrator`` (type | None): Imported class (T1.99.97/I127).
        - ``_DocumentRegistry`` (type | None): Imported class (T1.99.98/I127).
        - ``_DataExporter`` (type | None): Imported class (T1.99.99/I127).
    """
    errors: list = []

    early_level = 1
    debug_mode = False
    _safe_posix = None
    _should_auto_create = None
    _discover_root = None
    _UniversalLogger = None
    _TelemetryHeartbeat = None
    _EKSBootstrapManager = None
    _EngineInput = None
    _EngineOutput = None
    _parse_cli_args = None
    _PipelineOrchestrator = None
    _DocumentRegistry = None
    _DataExporter = None

    
    try:
        early_verbosity = _parse_early_verbosity(args)
        early_level = 3 if early_verbosity["debug"] else (early_verbosity["level"] or 1)
        debug_mode = early_verbosity.get("debug", False)
    except Exception as e:
        msg = f"Verbosity parse failed: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.core.paths.path_utils import safe_posix as _sp, should_auto_create_folders as _sac
        _safe_posix, _should_auto_create = _sp, _sac
    except ImportError as e:
        msg = f"common.library.paths not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.paths.root_discovery import discover_project_root as _dr
        _discover_root = _dr
    except ImportError as e:
        msg = f"common.library.paths.root_discovery not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.logging import UniversalLogger as _UL
        _UniversalLogger = _UL
    except ImportError as e:
        msg = f"common.library.logging not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.core.pipeline import TelemetryHeartbeat as _TH
        from common.library.core.pipeline import EngineInput as _EI
        from common.library.core.pipeline import EngineOutput as _EO
        _TelemetryHeartbeat, _EngineInput, _EngineOutput = _TH, _EI, _EO
    except ImportError as e:
        msg = f"common.library.core.pipeline not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from eks.engine.core.bootstrap import EKSBootstrapManager as _BSM
        _EKSBootstrapManager = _BSM
    except ImportError as e:
        msg = f"eks.engine.core.bootstrap not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.cli import parse_cli_args as _PCA
        _parse_cli_args = _PCA
    except ImportError as e:
        msg = f"common.library.cli not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator as _PO
        _PipelineOrchestrator = _PO
    except ImportError as e:
        msg = f"eks.engine.core.pipeline_orchestrator not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from eks.engine.core.registry import DocumentRegistry as _DR
        _DocumentRegistry = _DR
    except ImportError as e:
        msg = f"eks.engine.core.registry not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    try:
        from common.library.export import DataExporter as _DE
        _DataExporter = _DE
    except ImportError as e:
        msg = f"common.library.export not available: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    if errors:
        print(f"FATAL: Preload infrastructure failed with {len(errors)} error(s)", file=sys.stderr)
        return {
            "ready": False, "errors": errors,
            "project_root": None, "early_level": early_level,
            "debug_mode": debug_mode,
            "safe_posix": None, "should_auto_create_folders": None,
            "_UniversalLogger": None, "_TelemetryHeartbeat": None,
            "_EKSBootstrapManager": None,
            "_EngineInput": None, "_EngineOutput": None,
            "_parse_cli_args": None, "_PipelineOrchestrator": None,
            "_DocumentRegistry": None, "_DataExporter": None,
        }

    try:
        prj = _discover_root(
            pipeline_root_dir=pipeline_root_dir,
            pipeline_dir=pipeline_dir,
            reference=Path(__file__),
        )
    except Exception as e:
        msg = f"Project root discovery failed: {e}"
        print(f"FATAL: {msg}", file=sys.stderr)
        return {
            "ready": False, "errors": [msg],
            "project_root": None, "early_level": early_level,
            "debug_mode": debug_mode,
            "safe_posix": _safe_posix, "should_auto_create_folders": _should_auto_create,
            "_UniversalLogger": _UniversalLogger, "_TelemetryHeartbeat": _TelemetryHeartbeat,
            "_EKSBootstrapManager": _EKSBootstrapManager,
            "_EngineInput": _EngineInput, "_EngineOutput": _EngineOutput,
            "_parse_cli_args": _parse_cli_args, "_PipelineOrchestrator": _PipelineOrchestrator,
            "_DocumentRegistry": _DocumentRegistry, "_DataExporter": _DataExporter,
        }

    return {
        "ready": True, "errors": [],
        "project_root": prj, "early_level": early_level,
        "debug_mode": debug_mode,
        "safe_posix": _safe_posix, "should_auto_create_folders": _should_auto_create,
        "_UniversalLogger": _UniversalLogger, "_TelemetryHeartbeat": _TelemetryHeartbeat,
        "_EKSBootstrapManager": _EKSBootstrapManager,
        "_EngineInput": _EngineInput, "_EngineOutput": _EngineOutput,
        "_parse_cli_args": _parse_cli_args, "_PipelineOrchestrator": _PipelineOrchestrator,
        "_DocumentRegistry": _DocumentRegistry, "_DataExporter": _DataExporter,
    }
