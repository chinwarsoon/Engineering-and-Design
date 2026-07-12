"""
Schema-driven path resolution — universal PathResolver.

Revision: 1.0
Date: 2026-07-11
Author: opencode
Summary: T1.98a — adopt EKS global_paths as the universal canonical path pattern (I089).
Normalizes both EKS (global_paths) and DCC (folder_creation + discovery_rules) config
shapes into a single canonical ResolvedPaths model.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_DATA_DIR = "data"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_ARCHIVE_DIR = "archive"
DEFAULT_CONFIG_DIR = "config"
DEFAULT_LOG_DIR = "log"
DEFAULT_SCHEMA_DIR = "config/schemas"
DEFAULT_EKS_ROOT = ""


@dataclass
class ResolvedPaths:
    """Canonical, schema-driven project paths (relative strings).

    ``source`` records which config shape produced the result
    (``"eks"`` for a ``global_paths`` block, ``"dcc"`` for the DCC
    ``folder_creation`` + ``discovery_rules`` shape).
    """

    data_dir: str = DEFAULT_DATA_DIR
    output_dir: str = DEFAULT_OUTPUT_DIR
    archive_dir: str = DEFAULT_ARCHIVE_DIR
    config_dir: str = DEFAULT_CONFIG_DIR
    log_dir: str = DEFAULT_LOG_DIR
    schema_dir: str = DEFAULT_SCHEMA_DIR
    eks_root: str = DEFAULT_EKS_ROOT
    source: str = "unknown"

    def resolve(self, project_root) -> Dict[str, Path]:
        """Return absolute Paths anchored at *project_root*.

        For EKS (non-empty ``eks_root``) every path is nested under
        ``project_root / eks_root``; for DCC (empty ``eks_root``) paths
        live directly under ``project_root``.
        """
        root = Path(project_root)
        anchor = root / self.eks_root if self.eks_root else root
        return {
            "data_dir": anchor / self.data_dir,
            "output_dir": anchor / self.output_dir,
            "archive_dir": anchor / self.archive_dir,
            "config_dir": anchor / self.config_dir,
            "log_dir": anchor / self.log_dir,
            "schema_dir": anchor / self.schema_dir,
            "eks_root": (root / self.eks_root) if self.eks_root else root,
        }


def _derive_schema_dir(config: Dict[str, Any], config_dir: str) -> str:
    """Infer ``schema_dir`` from ``discovery_rules`` or fall back to default."""
    rules = config.get("discovery_rules") or []
    if isinstance(rules, list):
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            directory = rule.get("directory", "")
            category = rule.get("category", "")
            pattern = rule.get("pattern", "")
            if category in ("base_schema", "validation_schema", "config_data", "schema") \
                    or "schema" in pattern \
                    or "schema" in directory:
                if directory:
                    return directory
    return f"{config_dir}/schemas"


def resolve_paths(project_root: Optional[Any], config: Dict[str, Any]) -> ResolvedPaths:
    """Resolve canonical project paths from a pipeline configuration.

    Supports two config shapes and normalizes both into the EKS
    ``global_paths`` canonical shape:

    * EKS shape — config has a top-level ``global_paths`` object.
    * DCC shape — config has ``folder_creation.required_directories`` plus
      ``discovery_rules`` (no ``global_paths``); data/output dirs are derived
      from ``folder_creation`` entries or native defaults.

    Parameters:
        project_root: Repository/project root (str or Path) used only for
            absolute resolution via :meth:`ResolvedPaths.resolve`.
        config: Loaded pipeline configuration dictionary.

    Returns:
        ResolvedPaths dataclass with canonical relative path strings.
    """
    config = config or {}
    gp = config.get("global_paths")
    if isinstance(gp, dict):
        config_dir = gp.get("config_dir", DEFAULT_CONFIG_DIR)
        return ResolvedPaths(
            data_dir=gp.get("data_dir", DEFAULT_DATA_DIR),
            output_dir=gp.get("output_dir", DEFAULT_OUTPUT_DIR),
            archive_dir=gp.get("archive_dir", DEFAULT_ARCHIVE_DIR),
            config_dir=config_dir,
            log_dir=gp.get("log_dir", DEFAULT_LOG_DIR),
            schema_dir=_derive_schema_dir(config, config_dir),
            eks_root=gp.get("eks_root", DEFAULT_EKS_ROOT),
            source="eks",
        )

    # DCC shape — normalize into the canonical EKS global_paths shape.
    fc = config.get("folder_creation") or {}
    req_dirs: Dict[str, Dict[str, Any]] = {}
    if isinstance(fc, dict):
        for entry in fc.get("required_directories", []) or []:
            if isinstance(entry, dict) and entry.get("name"):
                req_dirs[entry["name"]] = entry

    def _pick(name: str, default: str) -> str:
        return req_dirs.get(name, {}).get("name", default)

    return ResolvedPaths(
        data_dir="data",  # DCC native default (base_path / "data")
        output_dir=_pick("output", DEFAULT_OUTPUT_DIR),
        archive_dir=DEFAULT_ARCHIVE_DIR,
        config_dir=DEFAULT_CONFIG_DIR,
        log_dir=_pick("Log", DEFAULT_LOG_DIR),
        schema_dir=_derive_schema_dir(config, DEFAULT_CONFIG_DIR),
        eks_root=DEFAULT_EKS_ROOT,
        source="dcc",
    )
