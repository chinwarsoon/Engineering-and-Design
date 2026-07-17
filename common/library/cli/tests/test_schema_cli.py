"""
Tests for the universal, schema-driven pipeline CLI parser (L18 / I099).

Validates the four review principles:
  1. schema-driven argument generation (build_parser_from_schema)
  2. root-folder-based schema retrieval (_load_schema_config)
  3. CLI > Schema > Native precedence via explicit-override detection
  4. structured CliResult returned to the pipeline (parse_cli_args)

Revision: 1.0
Date: 2026-07-15
Author: opencode
Summary: L18 — tests for common.library.cli.schema_cli (I099).
"""
import json
from pathlib import Path

import pytest

from common.library.cli import (
    CliResult,
    build_parser_from_schema,
    parse_cli_args,
)


SAMPLE_CONFIG = {
    "system_parameters": {
        "log_level": 1,
        "max_workers": 4,
        "app_name": "eks-test",
    },
    "global_paths": {
        "eks_root": "",
        "data_dir": "data",
        "output_dir": "output",
        "config_dir": "config",
        "log_dir": "log",
        "schema_dir": "config/schemas",
    },
}


def _write_config(root: Path) -> Path:
    cfg = root / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "eks_config.json").write_text(json.dumps(SAMPLE_CONFIG), encoding="utf-8")
    return cfg


def test_build_parser_from_schema_generates_schema_args():
    root = Path("/tmp/__noop__")  # schema passed directly; filesystem unused
    parser = build_parser_from_schema(root, SAMPLE_CONFIG)
    ns = parser.parse_args(["--max-workers", "8", "--app-name", "demo", "--json"])
    assert ns.max_workers == "8"
    assert ns.app_name == "demo"
    assert ns.json is True
    # universal core args always present
    assert ns.base_path is None


def test_parse_cli_args_override_precedence(tmp_path):
    _write_config(tmp_path)
    result = parse_cli_args(
        ["--max-workers", "8"], root=tmp_path, anchor="engine",
    )
    assert isinstance(result, CliResult)
    # principle 3 — explicit override detected
    assert result.overrides == {"max_workers": "8"}
    assert result.overrides_provided is True
    # principle 4 — pipeline_input merges schema default < override
    assert result.pipeline_input["schema_parameters"]["max_workers"] == "8"
    assert result.pipeline_input["schema_parameters"]["app_name"] == "eks-test"
    assert result.project_root == tmp_path


def test_parse_cli_args_no_override_uses_schema_default(tmp_path):
    _write_config(tmp_path)
    result = parse_cli_args([], root=tmp_path, anchor="engine")
    assert result.overrides == {}
    assert result.overrides_provided is False
    assert result.pipeline_input["schema_parameters"]["max_workers"] == 4


def test_parse_cli_args_resolves_paths(tmp_path):
    _write_config(tmp_path)
    result = parse_cli_args([], root=tmp_path, anchor="engine")
    assert result.resolved_paths["data_dir"] == tmp_path / "data"
    assert result.resolved_paths["output_dir"] == tmp_path / "output"
    assert result.config_dir == tmp_path / "config"


def test_parse_cli_args_discovers_root_via_l17(tmp_path):
    # principle 2 — root located via L17 entry sequence (anchor folder present)
    (tmp_path / "engine").mkdir()
    _write_config(tmp_path)
    result = parse_cli_args(
        ["--base-path", str(tmp_path)], anchor="engine",
    )
    assert result.project_root == tmp_path


def test_load_schema_config_finds_eks_config_in_schemas():
    """I100 / T1.99.31 — the universal parser must locate the EKS config where it
    actually lives (``eks/config/schemas/eks_config.json``), not mistake the shared
    root ``config/`` folder for a pipeline config. Regression guard for the 15
    pre-existing suite failures (ProjectSetupValidator config drift)."""
    from common.library.cli import schema_cli

    repo_root = Path(__file__).resolve().parents[4]
    cfg = schema_cli._load_schema_config(repo_root, None, None)
    assert "folders" in cfg, "EKS setup values not loaded from eks/config/schemas"
    assert cfg.get("global_paths", {}).get("eks_root") == "eks"


def test_parse_cli_args_resolves_eks_config_dir():
    """I100 / T1.99.31 — for the real EKS project, config_dir must resolve to
    ``<root>/eks/config`` (under eks_root), never the shared root ``config/``.
    This keeps the readiness gate's ConfigRegistry pointed at the right config."""
    repo_root = Path(__file__).resolve().parents[4]
    result = parse_cli_args([], root=repo_root, anchor="eks", pipeline_dir="engine")
    assert result.config_dir.parts[-2:] == ("eks", "config"), result.config_dir
    # the real EKS system parameters were loaded (config found, not empty)
    assert "log_level" in result.pipeline_input["schema_parameters"]


def test_common_library_exposes_no_project_specific_pipeline_dir_default():
    """I102 / T1.99.32 — the shared library must not bake in a project folder.

    A universal shared library (common.library) must not carry a project-specific
    ``pipeline_dir`` default (EKS "engine" / DCC "workflow"). The caller supplies
    it explicitly. This guards against regressions of the SSOT violation I102.
    """
    import inspect

    import common.library.paths.root_discovery as rd
    from common.library.cli import schema_cli

    # No project-specific module-level constant.
    assert not hasattr(rd, "DEFAULT_PIPELINE_DIR"), (
        "common.library must not expose a project-specific DEFAULT_PIPELINE_DIR"
    )

    # ``pipeline_dir`` has no project-specific default in any entry function.
    for fn in (
        rd.resolve_pipeline_base_path,
        rd.discover_project_root,
        schema_cli.parse_cli_args,
        schema_cli.build_parser_from_schema,
    ):
        default = inspect.signature(fn).parameters["pipeline_dir"].default
        assert default is None, (
            f"{fn.__module__}.{fn.__name__}.pipeline_dir default must be None "
            f"(not a project folder), got {default!r}"
        )
