"""
Shared pipeline entry funnel (I092 / R60).

Consolidates the bootstrap + full-pipeline run so the unified CLI, the
Phase 1 backend server, and (future) UI entries all converge on one code
path — mirroring DCC's single ``run_engine_pipeline(context)`` funnel.

Revision: 0.1
Date: 2026-07-11
Author: opencode
Summary: T1.99a — extract bootstrap_pipeline()/run_pipeline() shared funnel
used by the CLI (T1.99b) and every phase backend (T1.99c, T2.25, T3.36,
T4.26, T5.21). Uses ConfigRegistry SSOT (T1.99f).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Ensure repo root is importable when run as a script (mirrors phase1_server.py)
_THIS = Path(__file__).resolve()
_PRJ_DIR = _THIS.parent.parent.parent.parent
if str(_PRJ_DIR) not in sys.path:
    sys.path.insert(0, str(_PRJ_DIR))

from .schema_loader import SchemaLoader
from .pipeline_orchestrator import PipelineOrchestrator
from .error_manager import ErrorManager
from .message_manager import MessageManager
from .setup_validator import ProjectSetupValidator
from .registry import DocumentRegistry
from common.library.paths import resolve_paths
from common.library.config import get_system_param

try:
    from .config_registry import ConfigRegistry
except Exception:  # pragma: no cover - ConfigRegistry is part of core
    ConfigRegistry = None


def bootstrap_pipeline(
    project_root: Path,
    config_dir: Optional[Path] = None,
    logger: Any = None,
    skip_readiness: bool = False,
    debug: bool = False,
    use_config_registry: bool = True,
) -> Dict[str, Any]:
    """Build config + managers and run the project-setup readiness gate.

    Args:
        project_root: Repository root (used to resolve schema-driven paths).
        config_dir: Directory holding the EKS ``*.json`` config (default ``<root>/eks/config``).
        logger: Optional logger (EKSLogger-compatible) for managers + telemetry.
        skip_readiness: Bypass the project-setup readiness gate (G5 override).
        debug: Enable verbose validator output.
        use_config_registry: Load config via the ``ConfigRegistry`` SSOT (T1.99f).

    Returns:
        dict with keys: config, doc_config, config_registry, em, mm, resolved_paths
    """
    project_root = Path(project_root)
    if config_dir is None:
        config_dir = project_root / "eks" / "config"
    config_dir = Path(config_dir)

    # T1.99f: config loaded through the ConfigRegistry SSOT singleton
    config_registry = None
    if use_config_registry and ConfigRegistry is not None:
        # Defensive: the singleton may have been created earlier with a *different*
        # config dir (e.g. by a test). Reset it so the requested config dir wins
        # while still keeping a single instance per config dir (SSOT).
        _existing = ConfigRegistry._instance
        if _existing is not None:
            _existing_dir = getattr(getattr(_existing, "_loader", None), "config_dir", None)
            if _existing_dir is not None and Path(str(_existing_dir)).resolve() != Path(str(config_dir)).resolve():
                ConfigRegistry._instance = None
        config_registry = ConfigRegistry(str(config_dir))
        config = config_registry.config
    else:
        config = SchemaLoader(config_dir).load_all()

    # doc_config is a SchemaLoader artifact; load it independently (cheap)
    loader = SchemaLoader(config_dir)
    doc_config = loader.doc_config

    # T1.98a/I089: schema-driven, cross-project path resolution
    resolved = resolve_paths(project_root, config).resolve(project_root)

    em = ErrorManager(config_dir=config_dir, logger=logger, config=config)
    mm = MessageManager(config_dir=config_dir, logger=logger)

    if not skip_readiness:
        # T1.99f: pass the ConfigRegistry singleton (not the raw config dict)
        validator = ProjectSetupValidator(
            project_root=project_root,
            config_registry=config_registry if config_registry is not None else config,
            verbose=debug,
        )
        setup_results = validator.validate_all(auto_create=True)
        if setup_results["readiness"] != "YES":
            missing = validator.get_missing_items()
            error_codes = setup_results.get("error_codes", [])
            error_msg = (
                f"Project setup not ready (readiness={setup_results['readiness']}). "
                f"Missing folders: {len(missing['folders'])}, "
                f"Missing files: {len(missing['files'])}. "
                f"Error codes: {[ec['code'] for ec in error_codes]}"
            )
            # Mirrors phase1_server: the readiness gate is a soft warning — log the
            # structured error (recorded in the error summary) but do NOT abort the run,
            # even when fail_fast is enabled in config.
            try:
                em.handle_system_error("P1-SETUP-READINESS", detail=error_msg)
            except RuntimeError:
                if logger:
                    logger.warning(error_msg, context="bootstrap_pipeline.readiness")

    return {
        "config": config,
        "doc_config": doc_config,
        "config_registry": config_registry,
        "em": em,
        "mm": mm,
        "resolved_paths": resolved,
    }


def run_pipeline(
    project_root: Path,
    data_dir: Path,
    recursive: bool = True,
    config_dir: Optional[Path] = None,
    logger: Any = None,
    skip_readiness: bool = False,
    debug: bool = False,
    checkpoint_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
    registry: Any = None,
    on_phase: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Run the Phase 1 full pipeline A→C. Returns a result dict.

    Mirrors DCC's single ``run_engine_pipeline(context)`` funnel so the CLI,
    the HTTP backend, and a future UI entry share one implementation.

    Args:
        project_root: Repository root.
        data_dir: Data directory containing documents to process (relative to root).
        recursive: Recurse into subdirectories.
        config_dir: EKS config directory (default ``<root>/eks/config``).
        logger: Optional logger instance.
        skip_readiness: Bypass the readiness gate.
        debug: Verbose validator output.
        checkpoint_dir: Directory for per-phase checkpoint JSON artifacts.
        job_id: Job id used to name checkpoint files.
        registry: Optional shared ``DocumentRegistry`` instance.
        on_phase: Optional callback invoked with phase letter ("A"/"B"/"C")
            after each phase completes (used by servers to update progress).

    Returns:
        dict with keys: summary (phase_a/phase_b/phase_c), em, mm,
        config_registry, resolved_paths
    """
    boot = bootstrap_pipeline(project_root, config_dir, logger, skip_readiness, debug)
    config = boot["config"]
    doc_config = boot["doc_config"]
    em = boot["em"]
    mm = boot["mm"]
    resolved = boot["resolved_paths"]

    if registry is None:
        registry = DocumentRegistry(logger=logger)

    orchestrator = PipelineOrchestrator(
        config, doc_config, registry, logger=logger,
        use_telemetry=False, error_manager=em, message_manager=mm,
    )
    orchestrator.initialize_context(
        data_dir=project_root / data_dir,
        schema_dir=resolved["schema_dir"],
        output_dir=resolved["output_dir"],
        archive_dir=resolved["archive_dir"],
        config_dir=resolved["config_dir"],
        log_dir=resolved["log_dir"],
    )

    root = project_root / data_dir

    def _cp(phase: str):
        if on_phase:
            on_phase(phase)
        if checkpoint_dir is not None and job_id is not None:
            orchestrator.save_checkpoint(
                phase, checkpoint_path=Path(checkpoint_dir) / f"checkpoint_{job_id}_{phase}.json"
            )

    # T1.99c: single funnel replaces the inline A→B→C re-implementation
    phase_a = orchestrator.run_phase_a(root, recursive=recursive)
    _cp("A")
    phase_b = orchestrator.run_phase_b(root, recursive=recursive)
    _cp("B")
    phase_c = orchestrator.run_phase_c()
    _cp("C")

    return {
        "summary": {"phase_a": phase_a, "phase_b": phase_b, "phase_c": phase_c},
        "em": em,
        "mm": mm,
        "config_registry": boot["config_registry"],
        "resolved_paths": resolved,
    }
