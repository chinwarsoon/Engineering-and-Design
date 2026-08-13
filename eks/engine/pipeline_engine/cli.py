"""
CLI argument parsing for the EKS pipeline.

Extracted from ``eks_engine_pipeline.py`` (I233).  Zero module-level runtime
globals — all paths flow from callers.

Revision: 1.2
Date: 2026-08-12
Author: opencode
Summary: 1.2: I311/T1.298 — added --db-check/--db-apply(--yes)/--db-force
     flags + resolve_db_migration_mode() + add_db_migration_args() for the
     migration gate.
1.1: I234/T1.113 — --export default changed to None (schema-driven);
     runtime resolution from system_parameters.export_default.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Optional


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
    {
        "opts": ["--export"], "dest": "export_format", "type": str,
        "choices": ["csv", "xlsx", "both", "none"], "default": None,
        "help": "Export pipeline results as CSV/Excel spreadsheets (default: from system_parameters.export_default in eks_config.json; use 'none' to disable).",
    },
    {
        "opts": ["--db-check"], "dest": "db_check", "action": "store_true",
        "default": False,
        "help": "I311: print the DB migration plan only (read-only) and exit 0.",
    },
    {
        "opts": ["--db-apply", "--yes"], "dest": "db_apply", "action": "store_true",
        "default": False,
        "help": "I311: confirm and apply the migration plan, permitting non-protected destructive operations.",
    },
    {
        "opts": ["--db-force"], "dest": "db_force", "action": "store_true",
        "default": False,
        "help": "I311: TOTAL override — apply incl. protected tables (documents/document_elements); mandates a timestamped backup of eks_registry.db to output/archive/ before any destructive change.",
    },
]


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
    parser.add_argument(
        "--export", dest="export_format", type=str, default=None,
        choices=["csv", "xlsx", "both", "none"],
        help="Export pipeline results as CSV/Excel spreadsheets (default: from system_parameters.export_default in eks_config.json; use 'none' to disable).",
    )
    return parser


def build_schema_driven_parser(
    root: Path,
    schema_config=None,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
) -> argparse.ArgumentParser:
    """L18 — build the EKS CLI from the resolved root's schema (I099).

    Delegates to the universal :func:`build_parser_from_schema`, supplying the
    EKS-specific core args. ``root`` is a required parameter (no module-level
    global fallback — SSOT compliance, I233).

    Args:
        root: The project root directory.
        schema_config: Optional schema configuration dict.
        pipeline_root_dir: Anchor directory for project-root discovery.
        pipeline_dir: Pipeline sub-directory within pipeline_root_dir.
    """
    from common.library.cli import build_parser_from_schema
    return build_parser_from_schema(
        root, schema_config,
        pipeline_dir=pipeline_dir,
        core_arg_specs=_EKS_CORE_ARG_SPECS,
    )


def parse_eks_cli(
    args: Optional[list] = None,
    pipeline_root_dir: str = "eks",
    pipeline_dir: str = "engine",
    _parse_cli_args_fn: Any = None,
):
    """L18 — run the universal, schema-driven, precedence-aware EKS parse (I099).

    Returns a :class:`CliResult` whose ``namespace`` is consumed by :func:`main`
    and whose ``pipeline_input`` carries resolved paths + schema parameters.
    ``pipeline_root_dir`` / ``pipeline_dir`` default to the EKS literals but accept
    explicit values (I104 / T1.99.34) so the caller owns its folder literals.
    """
    if _parse_cli_args_fn is not None:
        parse_cli_args = _parse_cli_args_fn
    else:
        from common.library.cli import parse_cli_args
    return parse_cli_args(
        args,
        pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir,
        reference=Path(__file__),
        core_arg_specs=_EKS_CORE_ARG_SPECS,
    )


def resolve_db_migration_mode(ns: Any) -> Optional[str]:
    """I311/T1.298 — resolve the migration-gate mode from a parsed namespace.

    Precedence: ``--db-check`` (plan only, exit 0) > ``--db-force`` (TOTAL
    override incl. protected tables + mandatory backup) > ``--db-apply``
    (``--yes``, non-protected destructive). Returns None when no flag is set —
    the schema-driven ``system_parameters.migration_policy`` then governs.
    """
    if ns is None:
        return None
    if getattr(ns, "db_check", False):
        return "check"
    if getattr(ns, "db_force", False):
        return "force"
    if getattr(ns, "db_apply", False):
        return "apply"
    return None


def add_db_migration_args(parser: "argparse.ArgumentParser") -> None:
    """I311/T1.298 — add the migration-gate flags to a standalone CLI parser.

    Used by discovery_cli.py / health_cli.py (which own local parsers) so all
    DocumentRegistry entry points expose the same --db-check/--db-apply/
    --db-force surface as the main pipeline CLI (U292 transfer requirement).
    """
    parser.add_argument(
        "--db-check", dest="db_check", action="store_true", default=False,
        help="I311: print the DB migration plan only (read-only) and exit 0.",
    )
    parser.add_argument(
        "--db-apply", "--yes", dest="db_apply", action="store_true", default=False,
        help="I311: confirm and apply the migration plan, permitting non-protected "
             "destructive operations.",
    )
    parser.add_argument(
        "--db-force", dest="db_force", action="store_true", default=False,
        help="I311: TOTAL override — apply incl. protected tables "
             "(documents/document_elements); mandates a timestamped backup of "
             "eks_registry.db to output/archive/ before any destructive change.",
    )


def run_db_check_only(db_path: Any, config_dir: Optional[Any] = None,
                      logger: Any = None) -> int:
    """I311/T1.298 — run the migration gate in check mode (plan only).

    Returns 0 when the plan is built and printed (read-only, exit 0), 1 on a
    fatal gate failure. Used by the main pipeline CLI and the standalone
    DocumentRegistry entry points (discovery_cli / health_cli) so ``--db-check``
    behaves identically everywhere (U292).
    """
    from eks.engine.core.migration_gate import MigrationGate
    gate = MigrationGate(db_path=db_path, config_dir=config_dir, logger=logger, mode="check")
    try:
        gate.run(include_drift=True)
    except Exception as exc:  # nocv — fatal check failure
        print(f"DB check failed: {exc}", file=sys.stderr)
        return 1
    return 0


def _parse_early_verbosity(
    args: Optional[list] = None,
) -> dict:
    """T1.99.70 (I113): Lightweight early parse for --level / --debug only.

    Parses only the verbosity-relevant flags from raw ``sys.argv`` (or
    ``args``) **before** bootstrap, so ``UniversalLogger`` and
    ``TelemetryHeartbeat`` can be created pre-bootstrap. No schema/config
    dependency — pure argparse with the same dest/type/choices as
    ``_EKS_CORE_ARG_SPECS`` entries for ``--level`` and ``--debug``.

    Args:
        args: Optional argument list (None -> sys.argv[1:]).

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
