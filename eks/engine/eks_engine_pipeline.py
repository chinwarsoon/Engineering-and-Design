"""
Thin entry-point shell for the EKS pipeline (I233).

The ``main()`` function is the single console_scripts entry point.  All
implementation is delegated to ``eks.engine.pipeline_engine.{cli,runner,exporter}``
— this file handles only import-time sys.path bootstrap and re-exports.

Revision: 2.0
Date: 2026-07-23
Author: opencode
Summary: 2.0: I233 — monolith split. CLI, runner, exporter extracted to
     pipeline_engine/ subfolder. Zero module-level globals.
"""
from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Import-time sys.path bootstrap — pure stdlib, runs before any
# common.library import.  Puts the repo root on sys.path so that
# eks.engine.pipeline_engine and common.library are importable.
# ---------------------------------------------------------------------------

def _stdlib_find_repo_root(start: Path, anchors=("eks", "common")) -> Path:
    """Return the first ancestor of *start* that contains all *anchors*."""
    candidate = start.resolve()
    for _ in range(10):
        if all((candidate / a).exists() for a in anchors):
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    return start.resolve()


_PRJ_DIR = _stdlib_find_repo_root(Path(__file__).parent)
if str(_PRJ_DIR) not in sys.path:
    sys.path.insert(0, str(_PRJ_DIR))

# Strip the script's own directory from sys.path so that eks/engine/logging/
# cannot shadow stdlib ``logging`` when openpyxl/PIL etc. do "import logging"
# (shadowed-stdlib anti-pattern, AGENTS.md §7.9.2).
_THIS = Path(__file__).resolve()
_SCRIPT_DIR = str(_THIS.parent)
while _SCRIPT_DIR in sys.path:
    sys.path.remove(_SCRIPT_DIR)

# ---------------------------------------------------------------------------
# Re-exports — backward-compatible with all existing callers:
#   phase1_server.py, discovery_cli.py, health_cli.py,
#   test_eks_engine_pipeline.py, test_phase1.py
# ---------------------------------------------------------------------------

from eks.engine.pipeline_engine.runner import (           # noqa: E402
    _preload_infrastructure,
    _read_system_params,
    _last_phase,
    _print_human_summary,
    bootstrap_pipeline,
    run_pipeline,
)
from eks.engine.pipeline_engine.cli import (              # noqa: E402
    _EKS_CORE_ARG_SPECS,
    _parse_early_verbosity,
    build_parser,
    build_schema_driven_parser,
    parse_eks_cli,
)
from eks.engine.pipeline_engine.exporter import (         # noqa: E402
    resolve_export_columns,
    _build_export_rows,
    _build_flagged_rows,
)

# ---------------------------------------------------------------------------
# Main entry point (unchanged body from pre-split version)
# ---------------------------------------------------------------------------

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
    pipeline_root_dir = "eks"
    pipeline_dir = "engine"

    infra = _preload_infrastructure(
        args=args,
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
    )
    if not infra["ready"]:
        for err in infra["errors"]:
            print(f"FATAL: {err}", file=sys.stderr)
        return 1

    prj = infra["project_root"]
    early_level = infra["early_level"]
    debug_mode = infra["debug_mode"]
    safe_posix = infra["safe_posix"]
    should_auto_create_folders = infra["should_auto_create_folders"]
    _UniversalLogger = infra["_UniversalLogger"]
    _TelemetryHeartbeat = infra["_TelemetryHeartbeat"]
    EKSBootstrapManager = infra["_EKSBootstrapManager"]
    _EngineInput = infra["_EngineInput"]
    _EngineOutput = infra["_EngineOutput"]
    _parse_cli_args_fn = infra["_parse_cli_args"]
    _PipelineOrchestrator = infra["_PipelineOrchestrator"]
    _DocumentRegistry = infra["_DocumentRegistry"]
    _DataExporter = infra["_DataExporter"]

    logger = _UniversalLogger("eks-pipeline", level=early_level)
    hb = _TelemetryHeartbeat(enabled=early_level >= 2)
    hb.start()

    mgr = EKSBootstrapManager(
        project_root=prj,
        pipeline_root_dir=pipeline_root_dir,
        pipeline_dir=pipeline_dir,
        skip_readiness=False,
        debug=debug_mode,
        auto_create=True,
        logger=logger,
    )
    mgr._preloaded_parse_cli_args = _parse_cli_args_fn
    mgr.bootstrap_all(args)

    parsed = mgr.parsed
    os_info = mgr.os_info
    level = mgr.effective_parameters.get("level", early_level)
    data_dir = mgr.effective_parameters.get("data_dir", mgr.resolved_paths.get("data_dir", prj / "data"))
    project_root = mgr.project_root
    config_dir = mgr.config_dir
    resolved = mgr.resolved_paths
    mm = mgr.message_manager
    export_fmt = parsed.export_format if parsed else "none"

    if mm is not None:
        mm.show("STATUS_PIPELINE_START", root_dir=safe_posix(data_dir))

    if level != early_level:
        hb = _TelemetryHeartbeat(enabled=level >= 2)
        hb.start()

    try:
        EngineInput = _EngineInput
        EngineOutput = _EngineOutput

        ctx = mgr.to_pipeline_context()

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

        result = run_pipeline(
            project_root=project_root,
            data_dir=data_dir,
            recursive=parsed.recursive if parsed else True,
            config_dir=config_dir,
            logger=logger,
            skip_readiness=True,
            debug=parsed.debug if parsed else False,
            phase=parsed.phase if parsed else "full",
            auto_create=should_auto_create_folders(os_info),
            context=ctx,
            _PipelineOrchestrator_cls=_PipelineOrchestrator,
            _DocumentRegistry_cls=_DocumentRegistry,
        )
        summary = result["summary"]
        returned_ctx = result.get("context")

        hb.add_checkpoint("RUN", details={
            "phase": parsed.phase if parsed else "full",
            "phases": list(summary.keys()),
        })
        hb.stop()

        exported_files: list = []
        if export_fmt != "none" and returned_ctx is not None:
            DataExporter = _DataExporter
            DocumentRegistry = _DocumentRegistry
            if DataExporter is None or DocumentRegistry is None:
                logger.warning("Export module not available — skipping export", context="main")
            else:
                try:
                    exporter = DataExporter()
                    output_dir = Path(resolved.get("output_dir",
                        project_root / "eks" / "output"))

                    run_output_dir = output_dir / engine_in.run_id
                    run_output_dir.mkdir(parents=True, exist_ok=True)

                    reg = DocumentRegistry(logger=logger)
                    all_docs = reg.list_documents(latest_only=True, order_by="document_number")

                    run_docs = list(all_docs)
                    logger.info(
                        f"Export: {len(run_docs)} docs total", context="main"
                    )

                    export_config = resolve_export_columns(Path(safe_posix(config_dir)) / "schemas")
                    if export_config.get("_fallback"):
                        logger.warning(
                            "Schema-driven export columns unavailable — using hardcoded 11-field fallback",
                            context="main",
                        )
                    discovery_cols = export_config["discovery_inventory"]
                    extraction_cols = export_config["extraction_results"]
                    review_cols = export_config["review_flags"]

                    discovery_rows = _build_export_rows(run_docs, None, discovery_cols)
                    extraction_rows = _build_export_rows(run_docs, None, extraction_cols)
                    flagged_rows = _build_flagged_rows(run_docs, review_cols)

                    if export_fmt in ("csv", "both"):
                        if discovery_rows:
                            p = exporter.export_to_csv(discovery_rows, run_output_dir / "discovery_inventory.csv", columns=discovery_cols)
                            exported_files.append(str(p))
                        if extraction_rows:
                            p = exporter.export_to_csv(extraction_rows, run_output_dir / "extraction_results.csv", columns=extraction_cols)
                            exported_files.append(str(p))
                        if flagged_rows:
                            p = exporter.export_to_csv(flagged_rows, run_output_dir / "review_flags.csv", columns=review_cols)
                            exported_files.append(str(p))
                    if export_fmt in ("xlsx", "both"):
                        if discovery_rows:
                            p = exporter.export_to_excel(discovery_rows, run_output_dir / "discovery_inventory.xlsx", sheet_name="Discovery", columns=discovery_cols)
                            exported_files.append(str(p))
                        if extraction_rows:
                            p = exporter.export_to_excel(extraction_rows, run_output_dir / "extraction_results.xlsx", sheet_name="Extraction", columns=extraction_cols)
                            exported_files.append(str(p))
                        if flagged_rows:
                            p = exporter.export_to_excel(flagged_rows, run_output_dir / "review_flags.xlsx", sheet_name="Review Flags", columns=review_cols)
                            exported_files.append(str(p))

                    if exported_files:
                        logger.status(f"Exported {len(exported_files)} file(s) to {run_output_dir}", context="main")

                        try:
                            for src in run_output_dir.iterdir():
                                if src.is_file():
                                    dst_tmp = output_dir / f".{src.name}.tmp"
                                    dst_final = output_dir / src.name
                                    shutil.copy2(src, dst_tmp)
                                    dst_tmp.replace(dst_final)
                            logger.status(
                                f"Copied {len(exported_files)} file(s) to {output_dir}",
                                context="main",
                            )
                        except Exception as copy_err:
                            logger.warning(
                                f"Root-level copy failed (per-run exports unaffected): {copy_err}",
                                context="main",
                            )

                except Exception as e:
                    logger.warning(f"Export failed: {e}", context="main")

        engine_out = EngineOutput(
            run_id=engine_in.run_id,
            status="SUCCESS" if returned_ctx and returned_ctx.state.status == "COMPLETE" else "FAILED",
            output_files=exported_files,
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
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", context="eks-pipeline")
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
