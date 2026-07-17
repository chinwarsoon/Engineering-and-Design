"""
Unified main pipeline entry for the EKS pipeline (I092 / R60 / I096 / T1.99.8).

Single main entry mirroring DCC's ``dcc/workflow/dcc_engine_pipeline.py``. It
relocates the unified CLI + the shared ``bootstrap_pipeline``/``run_pipeline``
funnel to the engine root so the CLI, the HTTP backend, and (future) UI entries
converge on one code path — exactly like DCC's ``run_engine_pipeline(context)``.

Built ON TOP OF the universal pipeline architecture (``common.library``) rather
than EKS-local duplicates (AGENTS.md §10 SSOT; advances I078):
  - ``common.library.paths.resolve_paths`` (L16) — schema-driven base-path resolution
  - ``common.library.config.get_system_param`` (L15) — verbose/debug defaults
  - ``common.library.core.pipeline.EngineInput`` / ``EngineOutput`` (L08) — run contract
  - ``common.library.core.pipeline.TelemetryHeartbeat`` (L05) — entry-level heartbeat
   - ``eks.engine.core.message_manager.MessageManager`` (L11 subclass) — entry milestone printing
  - ``common.library.logging.UniversalLogger`` (L01) — tiered entry logging
The bootstrap readiness gate (L13) is delegated to ``ProjectSetupValidator``,
which already adapts ``common.library.utility.validation.ValidationManager`` (T1.87).

Per-phase separability (Appendix F §2.3.3 / §2.3.5, R60): ``--phase {A,B,C,full}``
lets each Phase 1 phase run independently for modular debugging / resume.

Path resolution (I097 / T1.99.13–15, L17 / T1.99.17–23): entry-point discovery now
follows the universal L17 contract — ``detect_os()`` [L12] -> ``--base-path``/cwd
resolver -> ``==pipeline_dir`` strip -> anchor-verified project root
(EKS anchor ``eks/``, ``--base-path`` aware) -> schema-driven ``resolve_paths()``
[L16] honouring ``eks_root``.  ``--data-dir`` is optional and defaults to
``global_paths.data_dir`` nested under ``eks_root`` (precedence CLI > Schema > Native).
Folder auto-create is gated by ``should_auto_create_folders(os_info)`` (I098).

Revision: 0.3
Date: 2026-07-15
Author: opencode
Summary: T1.99.17–23 — L17 entry-point discovery via common.library.paths.root_discovery;
detect_os at entry, --base-path CLI, eks_root-aware resolve_paths, OS-gated auto-create,
anchor-missing raises (no silent cwd fallback). Closes I098 sub-issues.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from eks.engine.core.schema_loader import SchemaLoader
from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
from eks.engine.core.error_manager import ErrorManager
from eks.engine.core.message_manager import MessageManager
from eks.engine.core.setup_validator import ProjectSetupValidator
from eks.engine.core.registry import DocumentRegistry
from common.library.paths import resolve_paths
from common.library.config import get_system_param
from common.library.core.pipeline import EngineInput, EngineOutput, TelemetryHeartbeat
from common.library.logging import UniversalLogger
from common.library.core.paths.path_utils import (
    detect_os,
    safe_posix,
    should_auto_create_folders,
)
from common.library.paths.root_discovery import discover_project_root
from common.library.cli import build_parser_from_schema, parse_cli_args

try:
    from .core.config_registry import ConfigRegistry
except Exception:  # pragma: no cover - ConfigRegistry is part of core
    ConfigRegistry = None

# ---------------------------------------------------------------------------
# L17 — Pipeline Entry-Point & Cross-Platform Discovery (I098 / T1.99.17–23)
# Faithful to DCC: cwd/--base-path -> ==pipeline_dir strip -> anchor-verified
# project root. EKS pipeline_root_dir = "eks" (pipeline root directory) and
# pipeline_dir = "engine" (main EKS pipeline entry folder) are declared locally
# inside main(). The shared resolver lives in
# common.library.paths.root_discovery (single source of truth, I078).
# ---------------------------------------------------------------------------

# EKS entry-point folder literals (pipeline_root_dir / pipeline_dir) are declared
# as literals locally inside main() (DCC-faithful, I104 / T1.99.34) and passed
# explicitly to parse_eks_cli / build_schema_driven_parser, which default to the
# same literals. The shared library (common.library) carries no project-specific
# default (I102). The import-time discovery below also uses the literals inline.


# Ensure repo root is importable when run as a script (import-time discovery).
_PRJ_DIR = discover_project_root(
    pipeline_root_dir="eks", pipeline_dir="engine", reference=Path(__file__)
)
if str(_PRJ_DIR) not in sys.path:
    sys.path.insert(0, str(_PRJ_DIR))

# Strip the script's own directory from sys.path so that eks/engine/logging/
# cannot shadow stdlib `logging` when openpyxl/PIL etc. do "import logging"
# (shadowed-stdlib anti-pattern, AGENTS.md §7.9.2).
_THIS = Path(__file__).resolve()
_SCRIPT_DIR = str(_THIS.parent)
while _SCRIPT_DIR in sys.path:
    sys.path.remove(_SCRIPT_DIR)


def bootstrap_pipeline(
    project_root: Path,
    args: Optional[list] = None,
    logger: Any = None,
    skip_readiness: bool = False,
    debug: bool = False,
    use_config_registry: bool = True,
    auto_create: bool = True,
) -> Dict[str, Any]:
    """Build config + managers and run the project-setup readiness gate.

    T1.99.45-46: I107 bootstrap completeness - now handles OS detection, CLI parsing,
    log-level precedence, and data-dir resolution internally (DCC-faithful).

    Args:
        project_root: Repository root (used to resolve schema-driven paths).
        args: Optional CLI argument list (``None`` -> ``sys.argv[1:]``).
        logger: Optional logger (UniversalLogger-compatible) for managers + telemetry.
        skip_readiness: Bypass the project-setup readiness gate (G5 override).
        debug: Enable verbose validator output.
        use_config_registry: Load config via the ``ConfigRegistry`` SSOT (T1.99.6).

    Returns:
        dict with keys: config, doc_config, config_registry, em, mm, resolved_paths,
        os_info, level, data_dir, project_root, config_dir, parsed (namespace)
    """
    project_root = Path(project_root)
    pipeline_root_dir = "eks"
    pipeline_dir = "engine"

    # T1.99.45: OS detection (DCC P6 env)
    os_info = detect_os()

    # T1.99.46: CLI parse (DCC P1) - L17 discovery + L18 schema-driven parse
    cli = parse_eks_cli(args, pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir)
    parsed = cli.namespace
    project_root = cli.project_root
    config_dir = cli.config_dir

    # T1.99.6: config loaded through the ConfigRegistry SSOT singleton
    config_registry = None
    if use_config_registry and ConfigRegistry is not None:
        _existing = ConfigRegistry._instance
        if _existing is not None:
            _existing_dir = getattr(getattr(_existing, "_loader", None), "config_dir", None)
            if _existing_dir is not None and Path(str(_existing_dir)).resolve() != Path(str(config_dir)).resolve():
                ConfigRegistry._instance = None
        config_registry = ConfigRegistry(str(config_dir))
        config = config_registry.config
    else:
        config = SchemaLoader(config_dir).load_all()

    loader = SchemaLoader(config_dir)
    doc_config = loader.doc_config

    # T1.99.45: CLI > Schema > Native precedence for log_level (DCC P8 params)
    # Use config from ConfigRegistry (already loaded above) - no 2nd load needed
    gp = config.get("global_paths", {}) if isinstance(config, dict) else {}
    eks_root = gp.get("eks_root", "eks")
    level = parsed.level if parsed.level is not None else int(gp.get("log_level", 1))
    if parsed.debug:
        level = 3

    # T1.99.46: L16 schema-driven canonical paths (single source, Defect A fix)
    resolved = resolve_paths(project_root, config).resolve(project_root)

    # T1.99.46: --data-dir precedence: CLI > Schema (resolve_paths) > Native; anchored under eks_root
    data_dir = resolved["data_dir"]
    if parsed.data_dir:
        cli_path = Path(parsed.data_dir)
        if cli_path.is_absolute():
            data_dir = cli_path
        else:
            data_dir = project_root / eks_root / parsed.data_dir

    em = ErrorManager(config_dir=config_dir, logger=logger, config=config)
    mm = MessageManager(config_dir=config_dir, logger=logger)

    if not skip_readiness:
        # T1.99.6: pass the ConfigRegistry singleton (not the raw config dict)
        validator = ProjectSetupValidator(
            project_root=project_root,
            config_registry=config_registry if config_registry is not None else config,
            verbose=debug,
        )
        setup_results = validator.validate_all(auto_create=auto_create)
        if setup_results["readiness"] != "YES":
            missing = validator.get_missing_items()
            error_codes = setup_results.get("error_codes", [])
            error_msg = (
                f"Project setup not ready (readiness={setup_results['readiness']}). "
                f"Missing folders: {len(missing['folders'])}, "
                f"Missing files: {len(missing['files'])}. "
                f"Error codes: {[ec['code'] for ec in error_codes]}"
            )
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
        "os_info": os_info,
        "level": level,
        "data_dir": data_dir,
        "project_root": project_root,
        "config_dir": config_dir,
        "parsed": parsed,
    }


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

    Returns:
        dict with keys: summary (depends on phase), em, mm, config_registry,
        resolved_paths, context (EKSPipelineContext instance)
    """
    # T1.99.42: if context is provided, skip bootstrap and use it directly
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
        # T1.99.45-48: bootstrap_pipeline now handles all init (OS, CLI, config, paths, level, data_dir, mm)
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
        
        # T1.99.41: populate context fields from bootstrap
        # Extract schema parameters from config (global_parameters + project_setup)
        params = {**config.get("global_parameters", {}), **config.get("project_setup", {})}
        
        orchestrator.initialize_context(
            data_dir=project_root / data_dir,
            schema_dir=resolved["schema_dir"],
            output_dir=resolved["output_dir"],
            archive_dir=resolved["archive_dir"],
            config_dir=resolved["config_dir"],
            log_dir=resolved["log_dir"],
            parameters=params,  # schema parameters from bootstrap
            config_registry=config_registry,  # ConfigRegistry SSOT
            schema_registry=config_registry,  # ConfigRegistry also provides schema access
            checkpoint_state=None,  # TODO: pass checkpoint_state from EngineInput for resume
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
    else:  # full — single coordination loop in the orchestrator (T1.99.10)
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
        "context": orchestrator.context,  # T1.99.42: surface context in return dict
    }


# ---------------------------------------------------------------------------
# CLI entry point (mirrors DCC dcc_engine_pipeline.py main())
# ---------------------------------------------------------------------------

def _read_system_params(config_dir: Path) -> Dict[str, Any]:
    """Load config to resolve schema-driven system-parameter defaults (L15)."""
    try:
        if ConfigRegistry is not None:
            return ConfigRegistry(str(config_dir)).config
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


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the unified EKS pipeline CLI."""
    parser = argparse.ArgumentParser(
        prog="eks-pipeline",
        description="EKS — run the Phase 1 ingestion pipeline (discovery → parse → score → review).",
    )
    parser.add_argument(
        "--data-dir", required=False, type=str, default=None,
        help="Data directory containing documents to process (relative to repo root or absolute). "
             "Default: global_paths.data_dir from eks_config.json.",
    )
    parser.add_argument(
        "--base-path", required=False, type=str, default=None,
        help="Project root override (L17). Defaults to the current working directory, "
             "or the anchor-verified repo root when launched from within the project. "
             "Use this when running from a different working directory.",
    )
    parser.add_argument(
        "--config-dir", type=str, default=None,
        help="EKS config directory (default <repo>/eks/config).",
    )
    parser.add_argument(
        "--phase", type=str, default="full", choices=["A", "B", "C", "full"],
        help="Run a single Phase 1 phase or the full pipeline (R60 / Appendix F §2.3.3).",
    )
    parser.add_argument(
        "--recursive", action="store_true", default=True,
        help="Recurse into subdirectories (default: on).",
    )
    parser.add_argument(
        "--no-recursive", dest="recursive", action="store_false",
        help="Do not recurse into subdirectories.",
    )
    parser.add_argument(
        "--skip-readiness", action="store_true",
        help="Bypass the project-setup readiness gate (G5 override).",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Verbose logging (level 3).",
    )
    parser.add_argument(
        "--level", type=int, default=None, choices=[0, 1, 2, 3],
        help="Logging level (0=error, 1=info, 2=debug, 3=trace); default from "
             "eks_config.json system_parameters.log_level (L15).",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the run summary as JSON to stdout.",
    )
    return parser


# L18 — EKS-specific CLI args surfaced through the universal schema-driven
# parser (I099). ``--base-path`` / ``--config-dir`` / ``--json`` are owned by the
# universal core; everything pipeline-specific lives here so the parser stays
# generic (AGENTS.md §10 SSOT).
_EKS_CORE_ARG_SPECS = [
    {
        "opts": ["--data-dir"], "dest": "data_dir", "default": None, "type": str,
        "help": "Override the resolved data directory (relative to repo root under "
                "eks_root, or absolute). Default: global_paths.data_dir (L16).",
    },
    {
        "opts": ["--phase"], "dest": "phase", "choices": ["A", "B", "C", "full"],
        "default": "full",
        "help": "Run a single Phase 1 phase or the full pipeline (R60 / Appendix F §2.3.3).",
    },
    {
        "opts": ["--recursive"], "dest": "recursive", "action": "store_true",
        "default": True, "help": "Recurse into subdirectories (default: on).",
    },
    {
        "opts": ["--no-recursive"], "dest": "recursive", "action": "store_false",
        "help": "Do not recurse into subdirectories.",
    },
    {
        "opts": ["--skip-readiness"], "dest": "skip_readiness", "action": "store_true",
        "default": False, "help": "Bypass the project-setup readiness gate (G5 override).",
    },
    {
        "opts": ["--debug"], "dest": "debug", "action": "store_true", "default": False,
        "help": "Verbose logging (level 3).",
    },
    {
        "opts": ["--level"], "dest": "level", "type": int, "default": None,
        "choices": [0, 1, 2, 3],
        "help": "Logging level (0=error, 1=info, 2=debug, 3=trace); default from "
                "eks_config.json system_parameters.log_level (L15).",
    },
]


def build_schema_driven_parser(
    root=None,
    schema_config=None,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
) -> argparse.ArgumentParser:
    """L18 — build the EKS CLI from the resolved root's schema (I099).

    Delegates to the universal :func:`build_parser_from_schema`, supplying the
    EKS-specific core args. Replaces the bespoke ``build_parser()`` (kept for
    backward compatibility / tests). ``pipeline_root_dir`` / ``pipeline_dir``
    default to the EKS literals but can be passed explicitly (DCC-faithful I/O
    clarity, I104 / T1.99.34) so callers (e.g. ``main()``) own their folder
    literals.
    """
    root = Path(root) if root is not None else _PRJ_DIR
    return build_parser_from_schema(
        root, schema_config,
        pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir,
        core_arg_specs=_EKS_CORE_ARG_SPECS,
    )


def parse_eks_cli(
    args: Optional[list] = None,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
):
    """L18 — run the universal, schema-driven, precedence-aware EKS parse (I099).

    Returns a :class:`CliResult` whose ``namespace`` is consumed by :func:`main`
    and whose ``pipeline_input`` carries resolved paths + schema parameters.
    ``anchor`` / ``pipeline_dir`` default to the EKS literals but accept
    explicit values (I104 / T1.99.34) so the caller owns its folder literals.
    """
    return parse_cli_args(
        args,
        pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir,
        reference=Path(__file__),
        core_arg_specs=_EKS_CORE_ARG_SPECS,
    )


def main(args: Optional[list] = None) -> int:
    """console_scripts entry point — full pipeline orchestration (DCC-faithful).

    T1.99.45-48: I107 bootstrap completeness - main() now delegates all init logic
    to bootstrap_pipeline() (OS detection, CLI parse, config load, path resolution,
    log-level/data-dir precedence, MessageManager). Single source of truth for all
    bootstrap data (Defect A + B fixed).

    Mirrors DCC's ``dcc/workflow/dcc_engine_pipeline.py::main()``: every pipeline
    step lives in ``main()`` (no separate ``run()``). The shared ``run_pipeline()``
    funnel is the analogue of DCC's ``run_engine_pipeline(context)`` and stays a
    separate callable because ``phase1_server.py`` and the tests reuse it.

    Args:
        args: Optional argument list (None -> sys.argv).

    Returns:
        0 on success, 1 on failure (suitable for ``sys.exit``).
    """
    # EKS folder literals declared locally (DCC-faithful I/O clarity, I104 /
    # T1.99.34) — main() owns its inputs and passes them explicitly downstream.
    pipeline_root_dir = "eks"      # pipeline root directory
    pipeline_dir = "engine"        # main EKS pipeline entry folder

    # T1.99.45-48: bootstrap_pipeline now handles all init (OS, CLI, config, paths, level, data_dir, mm)
    # Discover project root locally (DCC-faithful: main() resolves base_path, passes to bootstrap)
    prj = discover_project_root(
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
        reference=Path(__file__),
    )
    boot = bootstrap_pipeline(
        project_root=prj,
        args=args,
        skip_readiness=False,
        debug=False,
        auto_create=True,
    )

    # Extract bootstrap results (single source of truth, Defect A fixed)
    config = boot["config"]
    config_registry = boot["config_registry"]
    resolved = boot["resolved_paths"]
    os_info = boot["os_info"]
    level = boot["level"]
    data_dir = boot["data_dir"]
    project_root = boot["project_root"]
    config_dir = boot["config_dir"]
    parsed = boot["parsed"]
    mm = boot["mm"]  # T1.99.48: single MessageManager from bootstrap (Defect B fixed)

    # Derive output paths from single resolved dict (Defect A fixed)
    output_dir = resolved["output_dir"]
    schema_dir = resolved["schema_dir"]
    config_file = config_dir / "eks_config.json"

    # L01 — tiered entry logger; L11 — entry milestone printing
    logger = UniversalLogger("eks-pipeline", level=level)
    # T1.99.48: reuse bootstrap's mm (no duplicate instantiation)
    mm.show("STATUS_PIPELINE_START", root_dir=safe_posix(data_dir))

    # L05 — entry-level telemetry heartbeat (gated by verbosity)
    hb = TelemetryHeartbeat(enabled=level >= 2)
    hb.start()

    try:
        # L08 — model the run via the common EngineInput contract
        engine_in = EngineInput(
            run_id=str(uuid.uuid4()),
            data_dir=Path(data_dir),
            config_file=Path(config_file),
            schema_dir=Path(schema_dir),
            output_dir=Path(output_dir),
            parameters={"phase": parsed.phase, "recursive": parsed.recursive},
        )
        
        # T1.99.43: build EKSPipelineContext seeded with EngineInput + bootstrap
        from .core.context import EKSPaths, EKSData, EKSState, EKSTelemetry, EKSPipelineContext
        from datetime import datetime
        
        ctx_paths = EKSPaths(
            data_dir=Path(data_dir),
            schema_dir=Path(schema_dir),
            output_dir=Path(output_dir),
            archive_dir=resolved["archive_dir"],
            config_dir=Path(config_dir),
            log_dir=resolved["log_dir"],
        )
        
        ctx_data = EKSData()
        ctx_state = EKSState(status="INITIALIZED", start_time=datetime.now())
        ctx_telemetry = EKSTelemetry()
        
        # Seed context with EngineInput parameters and bootstrap data
        ctx_params = {
            "config": config,
            "doc_config": boot["doc_config"],
            "em": boot["em"],
            "mm": boot["mm"],
            **engine_in.parameters,
        }
        
        ctx = EKSPipelineContext(
            paths=ctx_paths,
            data=ctx_data,
            parameters=ctx_params,
            state=ctx_state,
            telemetry=ctx_telemetry,
            config_registry=config_registry,
            schema_registry=config_registry,
        )
        
        # T1.99.43: pass seeded context to run_pipeline (skips bootstrap)
        result = run_pipeline(
            project_root=project_root,
            data_dir=data_dir,
            recursive=parsed.recursive,
            config_dir=config_dir,
            logger=logger,
            skip_readiness=True,  # already done in bootstrap above
            debug=parsed.debug,
            phase=parsed.phase,
            auto_create=should_auto_create_folders(os_info),
            context=ctx,  # T1.99.43: pass seeded context
        )
        summary = result["summary"]
        returned_ctx = result.get("context")  # T1.99.43: extract returned context

        hb.add_checkpoint("RUN", details={"phase": parsed.phase, "phases": list(summary.keys())})
        hb.stop()

        # L08 — wrap the run in the common EngineOutput contract for structured output
        # T1.99.43: extract EngineOutput from returned context
        engine_out = EngineOutput(
            run_id=engine_in.run_id,
            status="SUCCESS" if returned_ctx and returned_ctx.state.status == "COMPLETE" else "FAILED",
            output_files=[],
            metadata={"phase": parsed.phase, "summary": summary},
            errors=[],
            checkpoint_state={"last_completed_phase": _last_phase(parsed.phase)},
            # L17 — safe_posix() so emitted paths are cross-platform (T1.99.22)
            telemetry={k: safe_posix(v) for k, v in result.get("resolved_paths", {}).items()},
        )
        if parsed.json:
            print(json.dumps(engine_out.to_dict(), indent=2, default=str))
        else:
            _print_human_summary(summary)
        return 0
    except Exception as e:  # surfaced for the operator
        logger.error(f"Pipeline failed: {e}", context="eks-pipeline")
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
