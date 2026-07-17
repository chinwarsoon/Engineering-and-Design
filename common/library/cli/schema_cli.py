"""
L18 — Universal, schema-driven CLI argument parser for pipelines.

A single, project-agnostic feature that satisfies the four CLI-parsing
principles (review of EKS vs DCC parsers):

  1. Universal + schema-driven.
       Argument *definitions* (names, defaults, help, types) are sourced from
       the pipeline configuration schema (``system_parameters`` for EKS,
       ``parameters`` for DCC), not hardcoded in each project. A fixed core set
       of truly universal flags (``--base-path``, ``--config-dir``, ``--json``)
       is always present. This replaces the bespoke ``build_parser()`` in EKS
       and the duplicated ``create_parser`` / ``create_parser_from_registry`` in
       DCC (AGENTS.md §10 SSOT; advances I078 / I099).
  2. Root-folder-based schema retrieval.
       The parser is built *from* the resolved pipeline root: the entry sequence
       (L17) runs first to locate the project root, then the schema is loaded
       from ``<root>/<config_dir>`` so defaults reflect the real configuration
       (not silently-fallback native defaults).
  3. Precedence check (CLI > Schema > Native).
       Explicit CLI values are detected by scanning the raw argv (faithful to
       DCC ``parse_cli_args``'s ``cli_overrides_provided`` flag) and returned as
       an explicit-only ``overrides`` dict. ``pipeline_input`` then merges
       schema defaults with those overrides.
  4. Return values for the pipeline.
       Parsing returns a :class:`CliResult` carrying the namespace, the explicit
       ``overrides``, an ``overrides_provided`` flag, and a ``pipeline_input``
       dict (resolved paths + schema parameters + overrides) ready for the
       pipeline funnel — no ad-hoc re-derivation inside ``run()``.

Revision: 1.0
Date: 2026-07-15
Author: opencode
Summary: L18 — universal schema-driven pipeline CLI parser (I099). Implements
the four review principles: schema-driven args, root-based schema retrieval,
CLI>Schema>Native precedence via explicit-override detection, and a structured
CliResult returned to the pipeline.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from common.library.config import normalize_system_parameters
from common.library.paths.resolver import resolve_paths
from common.library.paths.root_discovery import discover_project_root


# Universal core arguments every pipeline understands, regardless of schema
# (principle 1 — universal feature). Project-specific flags are supplied via
# ``core_arg_specs`` (e.g. EKS ``--phase`` / ``--recursive``).
_UNIVERSAL_CORE_ARGS: List[Dict[str, Any]] = [
    {
        "opts": ["--base-path"],
        "dest": "base_path",
        "default": None,
        "help": "Project root override (operator-controlled start). Defaults to "
                "cwd / pipeline_root_dir discovery (L17).",
    },
    {
        "opts": ["--config-dir"],
        "dest": "config_dir",
        "default": None,
        "help": "Config directory; defaults to the schema-derived config path (L16).",
    },
    {
        "opts": ["--json"],
        "action": "store_true",
        "dest": "json",
        "default": False,
        "help": "Emit the run summary as JSON to stdout.",
    },
]

# Schema parameter keys that are surfaced through dedicated core args instead of
# being auto-generated (avoids duplicate ``--log-level`` vs the EKS ``--level``).
_RESERVED_SCHEMA_KEYS = {"log_level"}


@dataclass
class CliResult:
    """Schema-driven CLI parse result (principle 4 — return values for pipeline).

    Attributes:
        namespace: The populated ``argparse.Namespace``.
        overrides: Explicit-only CLI values (principle 3).
        overrides_provided: Whether any CLI override was supplied.
        pipeline_input: Resolved, pipeline-ready values (schema defaults merged
            with explicit overrides) plus resolved canonical paths.
        project_root: Verified project root (L17).
        config_dir: Resolved config directory.
        resolved_paths: Absolute canonical paths (L16 ``ResolvedPaths.resolve``).
    """

    namespace: argparse.Namespace
    overrides: Dict[str, Any]
    overrides_provided: bool
    pipeline_input: Dict[str, Any]
    project_root: Path
    config_dir: Path
    resolved_paths: Dict[str, Path]


def _is_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))


def _add_arg(parser: argparse.ArgumentParser, spec: Dict[str, Any]) -> None:
    opts = spec["opts"]
    kwargs = {k: v for k, v in spec.items() if k != "opts"}
    if "dest" not in kwargs:
        kwargs["dest"] = opts[0].lstrip("-").replace("-", "_")
    parser.add_argument(*opts, **kwargs)


def _schema_config_candidates(root: Path, config_dir: Optional[Path]) -> List[Path]:
    """Candidate paths for the pipeline's primary config file (principle 2).

    Projects keep their config under ``<root>/<project>/config/schemas/`` (EKS:
    ``eks/config/schemas/eks_config.json``; DCC: ``dcc/config/schemas/...``). The
    shared root ``config/`` folder (repo-level schemas such as
    ``knowledge_base_schema.json``) is NOT a pipeline config and must not be
    mistaken for one — doing so loads an empty/foreign config and the readiness
    gate (ProjectSetupValidator) then fails to find setup values (I100).
    """
    cfg_dir = config_dir or (Path(root) / "config")
    return [
        cfg_dir / "eks_config.json",
        cfg_dir / "config_folders" / "eks_config.json",
        cfg_dir / "schemas" / "eks_config.json",
        Path(root) / "eks" / "config" / "schemas" / "eks_config.json",
        Path(root) / "eks" / "config" / "eks_config.json",
        Path(root) / "dcc" / "config" / "schemas" / "project_config.json",
        cfg_dir / "global_parameters.json",
    ]


def _load_schema_config(
    root: Path,
    config_dir: Optional[Path],
    schema_config: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Principle 2 — retrieve schema values from the pipeline root folder."""
    if schema_config is not None:
        return schema_config
    for candidate in _schema_config_candidates(Path(root), config_dir):
        if candidate.exists():
            try:
                with open(candidate, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception:
                continue
    return {}


def build_parser_from_schema(
    root: Path,
    schema_config: Optional[Dict[str, Any]] = None,
    *,
    pipeline_dir: Optional[str] = None,
    core_arg_specs: Optional[Sequence[Dict[str, Any]]] = None,
) -> argparse.ArgumentParser:
    """Build an ``ArgumentParser`` from the pipeline root's schema (principles 1 & 2).

    Args:
        root: Resolved pipeline root (used to load the schema for defaults).
        schema_config: Optional pre-loaded config dict; when ``None`` it is loaded
            from ``<root>/<config_dir>``.
        pipeline_dir: Module folder used for the ``== pipeline_dir`` strip (L17). Required — the shared library has no project-specific default (I102).
        core_arg_specs: Project-specific argument specs (each a dict with ``opts``
            plus ``add_argument`` kwargs).

    Returns:
        A configured ``argparse.ArgumentParser``.
    """
    config = _load_schema_config(Path(root), None, schema_config)
    parser = argparse.ArgumentParser(
        description="Universal schema-driven pipeline CLI (L18).",
        allow_abbrev=False,
    )

    core_opts: set = set()
    for spec in _UNIVERSAL_CORE_ARGS:
        _add_arg(parser, spec)
        core_opts.update(spec["opts"])
    for spec in (core_arg_specs or []):
        _add_arg(parser, spec)
        core_opts.update(spec["opts"])

    # Principle 1 — schema-driven args from system_parameters / parameters.
    params = normalize_system_parameters(config)
    for name, value in params.items():
        if name in _RESERVED_SCHEMA_KEYS:
            continue
        opt = "--" + name.replace("_", "-")
        if opt in core_opts:
            continue
        if not _is_scalar(value):
            continue
        parser.add_argument(
            opt,
            dest=name,
            default=value,
            type=str,
            help=f"Schema parameter '{name}' (default: {value!r}).",
        )
    return parser


def _detect_overrides(
    raw: List[str],
    parser: argparse.ArgumentParser,
) -> Dict[str, Any]:
    """Principle 3 — detect explicit CLI overrides by scanning raw argv.

    Faithful to DCC ``parse_cli_args``'s ``cli_overrides_provided`` detection:
    a value is an override only if its option string appeared on the command
    line (so schema defaults are never mistaken for overrides).
    """
    overrides: Dict[str, Any] = {}
    opt_to_dest: Dict[str, Any] = {}
    for action in parser._actions:
        for opt in action.option_strings:
            opt_to_dest[opt] = action

    for idx, token in enumerate(raw):
        if not token.startswith("--"):
            continue
        key = token.split("=", 1)[0]
        if key not in opt_to_dest:
            continue
        action = opt_to_dest[key]
        if action.const is not None and action.nargs == 0:
            # store_true / store_false
            overrides[action.dest] = action.const
        else:
            if "=" in token:
                overrides[action.dest] = token.split("=", 1)[1]
            elif idx + 1 < len(raw):
                overrides[action.dest] = raw[idx + 1]
    return overrides


def parse_cli_args(
    args: Optional[Sequence[str]] = None,
    *,
    pipeline_root_dir: str,
    pipeline_dir: Optional[str] = None,
    reference: Optional[Path] = None,
    schema_config: Optional[Dict[str, Any]] = None,
    root: Optional[Path] = None,
    core_arg_specs: Optional[Sequence[Dict[str, Any]]] = None,
) -> CliResult:
    """Run the full L17-ordered, schema-driven, precedence-aware parse.

    Args:
        args: Optional argument list (``None`` -> ``sys.argv[1:]``).
        pipeline_root_dir: Project anchor folder name (L17).
        pipeline_dir: Module folder for the ``== pipeline_dir`` strip (L17). Required — the shared library has no project-specific default (I102).
        reference: Entry module ``__file__`` for the anchor-walk fallback.
        schema_config: Optional pre-loaded config dict.
        root: Pre-resolved project root; when ``None`` the L17 discovery sequence
            runs (using ``--base-path`` if supplied).
        core_arg_specs: Project-specific argument specs.

    Returns:
        A :class:`CliResult` with the namespace, overrides, and ``pipeline_input``.
    """
    raw = list(args) if args is not None else list(sys.argv[1:])

    # Pass 1 — extract --base-path / --config-dir to locate the root (L17 step 3-4).
    pre = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    pre.add_argument("--base-path", dest="base_path", default=None)
    pre.add_argument("--config-dir", dest="config_dir", default=None)
    known, _ = pre.parse_known_args(raw)
    base_path = known.base_path
    config_dir_arg = known.config_dir

    if root is None:
        root = discover_project_root(
            pipeline_root_dir=pipeline_root_dir, pipeline_dir=pipeline_dir,
            base_path=base_path, reference=reference,
        )
    root = Path(root)

    # Principle 2 — load schema from the resolved root.
    config = _load_schema_config(root, Path(config_dir_arg) if config_dir_arg else None, schema_config)
    parser = build_parser_from_schema(
        root, config, pipeline_dir=pipeline_dir,
        core_arg_specs=core_arg_specs,
    )
    namespace = parser.parse_args(raw)  # strict (catches typos, like EKS)

    # Principle 3 — explicit-only override detection + precedence merge.
    overrides = _detect_overrides(raw, parser)
    overrides_provided = bool(overrides)

    # Principle 4 — assemble pipeline-ready values.
    resolved = resolve_paths(root, config).resolve(root)
    cfg_dir = Path(config_dir_arg) if config_dir_arg else resolved["config_dir"]
    pipeline_input: Dict[str, Any] = {
        "project_root": root,
        "base_path": base_path,
        "config_dir": cfg_dir,
        "resolved_paths": resolved,
        "schema_parameters": {**normalize_system_parameters(config), **overrides},
        "overrides": overrides,
    }
    for attr, value in vars(namespace).items():
        if attr not in pipeline_input:
            pipeline_input[attr] = value

    return CliResult(
        namespace=namespace,
        overrides=overrides,
        overrides_provided=overrides_provided,
        pipeline_input=pipeline_input,
        project_root=root,
        config_dir=cfg_dir,
        resolved_paths=resolved,
    )
