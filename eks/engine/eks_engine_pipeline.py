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

Lazy-import design (I114 / T1.99.80): ALL common.library imports are deferred to
inside functions so that ``test_environment()`` (stdlib-only, L20) runs first in
bootstrap and reports ALL missing dependencies with friendly guidance — no bare
``ModuleNotFoundError`` reaches the user. The only module-level common.library
import is a guarded try/except for early project-root discovery.

Preload infrastructure design (I117 / I118): ``_preload_infrastructure()`` is a
module-level **pure-stdlib** function that individually try/except-guards every
``common.library`` import. It returns imported **classes** (not instantiated
objects) so the function itself never depends on ``common.library`` at runtime.
``main()`` instantiates ``UniversalLogger`` + ``TelemetryHeartbeat`` after the
preload gate passes. All 6 failure points immediately print to stderr with
``FATAL:`` prefix — no error is ever silently collected.

Revision: 0.7
Date: 2026-07-17
Author: opencode
Summary: T1.99.84 (I118) — ``_preload_infrastructure()`` v2: true pure-stdlib.
(a) All 6 failure points print to stderr immediately (no silent errors).
(b) All variables pre-bound with safe defaults — no NameError possible.
(c) logger/heartbeat instantiation moved from preload to main() — preload
returns imported classes (_UniversalLogger, _TelemetryHeartbeat), not objects.
(d) Removed logger_name parameter (now hardcoded in main()).
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# ---------------------------------------------------------------------------
# Module-level imports — stdlib ONLY.
# ALL common.library imports are deferred to inside functions so that
# test_environment() (L20) can run first and report ALL missing deps before
# any ModuleNotFoundError occurs (I114 / T1.99.80).
# ---------------------------------------------------------------------------

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


# T1.99.80 (I114): Deferred import-time discovery.
# discover_project_root() is a lightweight common.library import (stdlib-only),
# but to keep ALL common.library imports deferred, we use a try/except with
# a deferred import. If discovery fails at import time, main() will resolve
# via discover_project_root() inside the function body.
_PRJ_DIR = Path.cwd()  # safe default; main() will re-resolve
try:
    from common.library.paths.root_discovery import discover_project_root as _dr
    _PRJ_DIR = _dr(
        pipeline_root_dir="eks", pipeline_dir="engine", reference=Path(__file__)
    )
    if str(_PRJ_DIR) not in sys.path:
        sys.path.insert(0, str(_PRJ_DIR))
except Exception:
    pass  # _PRJ_DIR stays at Path.cwd(); main() handles real discovery

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
    from .core.bootstrap import EKSBootstrapManager

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

    # Run EKS-specific readiness gate if not skipped
    if not skip_readiness:
        ready = mgr._run_readiness_gate()
        if not ready:
            # T1.99.63: use structured BootstrapError (I111)
            # P1-BOOT-READINESS is registered in eks_error_config.json (T1.99.62)
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
    # T1.99.80 (I114): Deferred heavy imports
    from .core.pipeline_orchestrator import PipelineOrchestrator
    from .core.registry import DocumentRegistry

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
        from .core.config_registry import ConfigRegistry
        if ConfigRegistry is not None:
            return ConfigRegistry(str(config_dir)).config
        from .core.schema_loader import SchemaLoader
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
    from common.library.cli import build_parser_from_schema
    root = Path(root) if root is not None else _PRJ_DIR
    return build_parser_from_schema(
        root, schema_config,
        pipeline_dir=pipeline_dir,
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
    from common.library.cli import parse_cli_args
    return parse_cli_args(
        args,
        pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir,
        reference=Path(__file__),
        core_arg_specs=_EKS_CORE_ARG_SPECS,
    )


def _parse_early_verbosity(
    args: Optional[list] = None,
) -> Dict[str, Any]:
    """T1.99.70 (I113): Lightweight early parse for --level / --debug only.

    Parses only the verbosity-relevant flags from raw ``sys.argv`` (or
    ``args``) **before** bootstrap, so ``UniversalLogger`` and
    ``TelemetryHeartbeat`` can be created pre-bootstrap. This mirrors DCC's
    ``parse_cli_args()`` → ``set_debug_level()`` before
    ``BootstrapManager.bootstrap_all()``.

    No schema/config dependency — pure argparse with the same dest/type/choices
    as ``_EKS_CORE_ARG_SPECS`` entries for ``--level`` and ``--debug``.

    Args:
        args: Optional argument list (None → sys.argv[1:]).

    Returns:
        dict with keys ``level`` (int, default 1) and ``debug`` (bool).
    """
    import argparse as _argparse

    _parser = _argparse.ArgumentParser(add_help=False)
    _parser.add_argument(
        "--level", dest="level", type=int, default=None,
        choices=[0, 1, 2, 3],
    )
    _parser.add_argument(
        "--debug", dest="debug", action="store_true", default=False,
    )
    _parsed, _ = _parser.parse_known_args(args)
    return {
        "level": _parsed.level,
        "debug": _parsed.debug,
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
    it inside the package would create a circular dependency (the guard
    cannot live in the package it guards).

    Design principle (I117 / universal pipeline §3.23 preload pattern):
    Every pipeline entry-point should have a stdlib-only preload function
    that gates all ``common.library`` imports. This is NOT a library function
    — it is a **pattern** that each project replicates with its own
    ``pipeline_root_dir`` / ``pipeline_dir`` literals.

    Args:
        args: Optional CLI argument list (None → sys.argv[1:]).
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
    """
    errors: list = []

    # All fallback defaults — every variable is pre-bound so a failure in any
    # step never causes a NameError in a later step.
    early_level = 1
    debug_mode = False
    _safe_posix = None
    _should_auto_create = None
    _discover_root = None
    _UniversalLogger = None
    _TelemetryHeartbeat = None

    # print message the preload will start
    print("Preload Reference Labraries now:")

    # Step 0: early verbosity (stdlib-only argparse, always safe)
    try:
        early_verbosity = _parse_early_verbosity(args)
        early_level = 3 if early_verbosity["debug"] else (early_verbosity["level"] or 1)
        debug_mode = early_verbosity.get("debug", False)
    except Exception as e:
        msg = f"Verbosity parse failed: {e}"
        errors.append(msg)
        print(f"FATAL: {msg}", file=sys.stderr)

    # Step 1: common.library imports — each individually guarded.
    # These are all wrapped in try/except so failure in one does not affect
    # the others.  The pre-bound defaults (None) above guarantee that even
    # if *every* import fails the function still returns a valid dict.
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
        _TelemetryHeartbeat = _TH
    except ImportError as e:
        msg = f"common.library.core.pipeline not available: {e}"
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
        }

    # Step 2: discover project root (stdlib-only — Path + the already-imported
    # _discover_root callable)
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
        }

    return {
        "ready": True, "errors": [],
        "project_root": prj, "early_level": early_level,
        "debug_mode": debug_mode,
        "safe_posix": _safe_posix, "should_auto_create_folders": _should_auto_create,
        "_UniversalLogger": _UniversalLogger, "_TelemetryHeartbeat": _TelemetryHeartbeat,
    }


def main(args: Optional[list] = None) -> int:
    """console_scripts entry point — full pipeline orchestration (DCC-faithful).

    Orchestration chain (T1.99.59–61, I113 pre-bootstrap logger, I117 preload guard):
      0. ``_preload_infrastructure(args)`` — pure-stdlib guard that loads
         logger, heartbeat, and project-root discovery BEFORE bootstrap.
         ALL ``common.library`` imports are individually try/except-guarded;
         errors collected and reported at once (I117 / T1.99.81).
      1. ``EKSBootstrapManager(logger=logger, ...).bootstrap_all(args)`` —
         universal L19 bootstrap (readiness gate, config, paths, OS detection,
         CLI parse, context assembly).
      2. ``mgr.to_pipeline_context()`` — collapses ~30 lines of manual assembly.
      3. ``EngineInput`` derived from context, ``run_pipeline(context=ctx)`` invoked.
      4. ``EngineOutput`` contract wraps the result for structured output (json/human).

    Error handling (T1.99.62–63, I117):
      - Preload failures (I117): collected in ``infra["errors"]``, printed to
        stderr with ``FATAL:`` prefix, exit code 1 — no bare ImportError.
      - Bootstrap failures raise ``BootstrapError`` with ``P1-BOOT-*`` codes
        (READINESS, CONFIG, PATHS, OS, CTX), all registered in the EKS error
        catalog under the ``bootstrap_p1`` range.
      - Top-level ``except Exception`` catches pipeline failures, logs via
        ``UniversalLogger``, prints to stderr, and returns exit code 1.

    Args:
        args: Optional argument list (None -> sys.argv).

    Returns:
        0 on success, 1 on failure (suitable for ``sys.exit``).
    """
    # EKS folder literals declared locally (DCC-faithful I/O clarity, I104 /
    # T1.99.34) — main() owns its inputs and passes them explicitly downstream.
    pipeline_root_dir = "eks"      # pipeline root directory
    pipeline_dir = "engine"        # main EKS pipeline entry folder

    # T1.99.81 (I117): Preload all infrastructure in one guarded call.
    # All common.library imports are individually try/except-guarded inside
    # _preload_infrastructure(); errors collected and reported at once.
    infra = _preload_infrastructure(
        args=args,
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
    )
    if not infra["ready"]:
        for err in infra["errors"]:
            print(f"FATAL: {err}", file=sys.stderr)
        return 1

    # Extract preloaded infrastructure — imports succeeded, now instantiate.
    prj = infra["project_root"]
    early_level = infra["early_level"]
    debug_mode = infra["debug_mode"]
    safe_posix = infra["safe_posix"]
    should_auto_create_folders = infra["should_auto_create_folders"]
    _UniversalLogger = infra["_UniversalLogger"]
    _TelemetryHeartbeat = infra["_TelemetryHeartbeat"]

    # T1.99.71 (I113): create logger + heartbeat (warm before bootstrap).
    # These are instantiated here in main() — NOT inside _preload_infrastructure()
    # which is pure-stdlib and must never depend on common.library.
    logger = _UniversalLogger("eks-pipeline", level=early_level)
    hb = _TelemetryHeartbeat(enabled=early_level >= 2)
    hb.start()

    # T1.99.59 + T1.99.71 (I113): use EKSBootstrapManager chain with pre-created
    # logger — mirrors DCC exactly (logger warm before bootstrap_all).
    from .core.bootstrap import EKSBootstrapManager
    mgr = EKSBootstrapManager(
        project_root=prj,
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
        skip_readiness=False,
        debug=debug_mode,
        auto_create=True,
        logger=logger,
    )
    mgr.bootstrap_all(args)

    # Extract bootstrap results from the manager
    parsed = mgr.parsed
    os_info = mgr.os_info
    level = mgr.effective_parameters.get("level", early_level)
    data_dir = mgr.effective_parameters.get("data_dir", mgr.resolved_paths.get("data_dir", prj / "data"))
    project_root = mgr.project_root
    config_dir = mgr.config_dir
    resolved = mgr.resolved_paths
    mm = mgr.message_manager

    # L11 — entry milestone printing (logger already created pre-bootstrap)
    if mm is not None:
        mm.show("STATUS_PIPELINE_START", root_dir=safe_posix(data_dir))

    # Reconcile heartbeat level if bootstrap resolved a different level
    if level != early_level:
        hb = TelemetryHeartbeat(enabled=level >= 2)
        hb.start()

    try:
        # T1.99.80 (I114): Deferred heavy imports — only after bootstrap
        # (which includes test_environment()) has succeeded.
        from common.library.core.pipeline import EngineInput, EngineOutput

        # T1.99.60–61: collapse manual context assembly — use to_pipeline_context()
        ctx = mgr.to_pipeline_context()

        # T1.99.61: derive EngineInput from context
        engine_in = EngineInput(
            run_id=str(uuid.uuid4()),
            data_dir=ctx.paths.data_dir,
            config_file=ctx.paths.config_dir / "eks_config.json",
            schema_dir=ctx.paths.schema_dir,
            output_dir=ctx.paths.output_dir,
            parameters={
                "phase": parsed.phase if parsed else "full",
                "recursive": parsed.recursive if parsed else True,
            },
        )

        # T1.99.59: pass context to run_pipeline (skips bootstrap, DCC pattern)
        result = run_pipeline(
            project_root=project_root,
            data_dir=data_dir,
            recursive=parsed.recursive if parsed else True,
            config_dir=config_dir,
            logger=logger,
            skip_readiness=True,  # already done in bootstrap above
            debug=parsed.debug if parsed else False,
            phase=parsed.phase if parsed else "full",
            auto_create=should_auto_create_folders(os_info),
            context=ctx,
        )
        summary = result["summary"]
        returned_ctx = result.get("context")

        hb.add_checkpoint("RUN", details={
            "phase": parsed.phase if parsed else "full",
            "phases": list(summary.keys()),
        })
        hb.stop()

        # L08 — wrap the run in the common EngineOutput contract for structured output
        engine_out = EngineOutput(
            run_id=engine_in.run_id,
            status="SUCCESS" if returned_ctx and returned_ctx.state.status == "COMPLETE" else "FAILED",
            output_files=[],
            metadata={"phase": parsed.phase if parsed else "full", "summary": summary},
            errors=[],
            checkpoint_state={"last_completed_phase": _last_phase(parsed.phase if parsed else "full")},
            telemetry={k: safe_posix(v) for k, v in result.get("resolved_paths", {}).items()},
        )
        if parsed and parsed.json:
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
