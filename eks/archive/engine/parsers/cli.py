"""
Unified CLI entry point for the EKS pipeline (I092 / T1.99b).

Converges on the shared ``run_pipeline()`` funnel so the CLI, the HTTP
backend server, and (future) UI entry all call one implementation —
mirroring DCC's single ``run_engine_pipeline(context)`` funnel.

Revision: 0.2
Date: 2026-07-11
Author: opencode
Summary: T1.99b — replace the stub that returned a fake SUCCESS with a real
end-to-end run via ``eks.engine.core.pipeline_runner.run_pipeline()`` and add
the ``eks-pipeline`` console_scripts entry point (eks/pyproject.toml).
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Ensure repo root is importable when run as a script
_THIS = Path(__file__).resolve()
_PRJ_DIR = _THIS.parent.parent.parent.parent
if str(_PRJ_DIR) not in sys.path:
    sys.path.insert(0, str(_PRJ_DIR))


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the unified EKS pipeline CLI."""
    parser = argparse.ArgumentParser(
        prog="eks-pipeline",
        description="EKS — run the Phase 1 ingestion pipeline (discovery → parse → score → review).",
    )
    parser.add_argument(
        "--data-dir", required=True, type=str,
        help="Data directory containing documents to process (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--config-dir", type=str, default=None,
        help="EKS config directory (default <repo>/eks/config).",
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
        "--level", type=int, default=1, choices=[0, 1, 2, 3],
        help="Logging level (0=error, 1=info, 2=debug, 3=trace).",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the run summary as JSON to stdout.",
    )
    return parser


def run(args: Optional[list] = None) -> int:
    """Run the pipeline end-to-end via the shared funnel. Returns process exit code.

    Args:
        args: Optional argument list (None -> sys.argv).

    Returns:
        0 on success, 1 on failure.
    """
    parsed = build_parser().parse_args(args)
    from eks.engine.logging.logger import EKSLogger
    logger = EKSLogger("eks-pipeline", level=3 if parsed.debug else parsed.level)
    try:
        from eks.engine.eks_engine_pipeline import run_pipeline

        data_dir = Path(parsed.data_dir)
        if not data_dir.is_absolute():
            data_dir = _PRJ_DIR / data_dir
        config_dir = Path(parsed.config_dir) if parsed.config_dir else None

        result = run_pipeline(
            project_root=_PRJ_DIR,
            data_dir=data_dir,
            recursive=parsed.recursive,
            config_dir=config_dir,
            logger=logger,
            skip_readiness=parsed.skip_readiness,
            debug=parsed.debug,
        )
        summary = result["summary"]
        if parsed.json:
            print(json.dumps(summary, indent=2, default=str))
        else:
            pa = summary.get("phase_a", {})
            pb = summary.get("phase_b", {})
            pc = summary.get("phase_c", {})
            print(f"Phase A: discovered={pa.get('discovered')} valid={pa.get('valid')} "
                  f"registered={pa.get('registered')}")
            print(f"Phase B: success={pb.get('success')} partial={pb.get('partial')} "
                  f"failed={pb.get('failed')}")
            print(f"Phase C: flagged={pc.get('flagged')}")
        return 0
    except Exception as e:  # surfaced for the operator
        logger.error(f"Pipeline failed: {e}", context="eks-pipeline")
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def main():
    """console_scripts entry point."""
    sys.exit(run())


if __name__ == "__main__":
    main()
