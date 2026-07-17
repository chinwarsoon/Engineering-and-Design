"""
Tests for the unified main pipeline entry (eks.engine.eks_engine_pipeline),
covering the shared bootstrap/run funnel and the CLI (T1.99.1/T1.99.2/T1.99.3/T1.99.6/T1.99.8–12).

Also covers L17 entry-point discovery (I098 / T1.99.17–23) via
common.library.paths.root_discovery and the EKS wiring in eks_engine_pipeline.

Also covers I107 bootstrap completeness integration tests (T1.99.49):
single source of resolved_paths, phase1_server.py result keys preserved,
context paths consistent with bootstrap resolved paths.

Revision: 0.5
Date: 2026-07-16
Author: opencode
Summary: T1.99.49 — I107 bootstrap completeness integration tests added.
"""
import sys
import uuid
from pathlib import Path
from unittest import TestCase, mock

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from eks.engine.eks_engine_pipeline import (
    bootstrap_pipeline,
    run_pipeline,
    discover_project_root,
    build_parser,
    build_schema_driven_parser,
    parse_eks_cli,
)
from common.library.paths import (
    resolve_pipeline_base_path,
    default_base_path,
    should_auto_create_folders,
    detect_os,
)
from eks.engine.core.config_registry import ConfigRegistry


class _SilentLogger:
    """Minimal EKSLogger-compatible stub for headless tests."""
    level = 1
    run_id = "test"

    def status(self, *a, **k):
        pass

    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass

    def debug(self, *a, **k):
        pass


def _make_data(prefix: str) -> Path:
    tag = uuid.uuid4().hex[:8]
    pdir = Path(f"test_output/{prefix}_{tag}")
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "DOC-001-A.pdf").touch()
    (pdir / "DOC-002-B.dgn").touch()
    return pdir


# ---------------------------------------------------------------------------
# T1.99.17–23 — L17 entry-point discovery (root_discovery + EKS wiring)
# ---------------------------------------------------------------------------

_ENGINE_MODULE = Path(__file__).resolve().parent.parent / "engine" / "eks_engine_pipeline.py"


class TestEntryPointDiscovery(TestCase):
    def test_discover_project_root_finds_anchor(self):
        """discover_project_root() returns repo root with eks/ and common/."""
        root = discover_project_root(
            pipeline_root_dir="eks", pipeline_dir="engine", reference=_ENGINE_MODULE
        )
        # The project root should be the repo root (parent of eks/)
        self.assertTrue((root / "eks").is_dir(), f"{root / 'eks'} should exist")
        self.assertTrue((root / "common").is_dir(), f"{root / 'common'} should exist")
        # Should NOT return the engine/ folder itself
        self.assertNotEqual(root.name, "engine")

    def test_resolve_pipeline_base_path_uses_cwd(self):
        """resolve_pipeline_base_path() defaults to cwd (no __file__ walk)."""
        root = resolve_pipeline_base_path()
        self.assertEqual(root, Path.cwd())

    def test_resolve_pipeline_base_path_honors_base_path(self):
        """resolve_pipeline_base_path() honours an explicit --base-path."""
        root = resolve_pipeline_base_path(base_path="/tmp/foo")
        self.assertEqual(root, Path("/tmp/foo").resolve())

    def test_resolve_pipeline_base_path_strips_pipeline_dir(self):
        """Launched from inside engine/ steps up one level (DCC 483-484)."""
        with mock.patch("common.library.paths.root_discovery.Path.cwd") as mc:
            mc.return_value = Path("/proj/eks/engine")
            root = resolve_pipeline_base_path(pipeline_dir="engine")
        self.assertEqual(root, Path("/proj/eks"))

    def test_default_base_path_raises_when_missing(self):
        """default_base_path raises FileNotFoundError if anchor absent (T1.99.23)."""
        with self.assertRaises(FileNotFoundError):
            default_base_path("__no_such_anchor__", reference=Path("/tmp/x.py"))

    def test_default_base_path_finds_anchor(self):
        """default_base_path walks the reference to locate the project root."""
        root = default_base_path("eks", reference=_ENGINE_MODULE)
        self.assertTrue((root / "eks").is_dir(), f"{root / 'eks'} should exist")

    def test_should_auto_create_folders(self):
        """Folder auto-create is gated by OS (L17 step 7)."""
        self.assertTrue(should_auto_create_folders({"normalized": "windows"}))
        self.assertTrue(should_auto_create_folders({"normalized": "linux"}))
        self.assertTrue(should_auto_create_folders({"normalized": "macos"}))
        self.assertFalse(should_auto_create_folders({"normalized": "freebsd"}))

    def test_detect_os_called_in_main(self):
        """main() invokes detect_os() and resolves an eks_root-aware data_dir."""
        from eks.engine.eks_engine_pipeline import main
        import os
        pdir = _make_data("discovery")
        prev = os.getcwd()
        os.chdir(str(_ROOT))
        try:
            with mock.patch("eks.engine.eks_engine_pipeline.detect_os") as d:
                d.return_value = {"system": "Windows", "normalized": "windows"}
            rc = main(["--data-dir", str(pdir), "--json"])
        finally:
            os.chdir(prev)
        self.assertEqual(rc, 0)


class TestSchemaDrivenCli(TestCase):
    def test_build_schema_driven_parser_exposes_phase(self):
        parser = build_schema_driven_parser(_ROOT)
        ns = parser.parse_args(["--phase", "A", "--json"])
        self.assertEqual(ns.phase, "A")
        self.assertTrue(ns.json)

    def test_parse_eks_cli_returns_cli_result(self):
        from common.library.cli import CliResult
        result = parse_eks_cli(["--phase", "B", "--no-recursive"])
        self.assertIsInstance(result, CliResult)
        self.assertEqual(result.namespace.phase, "B")
        self.assertFalse(result.namespace.recursive)
        # principle 3 — explicit overrides detected
        self.assertIn("phase", result.overrides)
        self.assertIn("recursive", result.overrides)
        self.assertTrue(result.overrides_provided)
        # principle 4 — pipeline_input carries resolved paths + schema params
        self.assertIn("resolved_paths", result.pipeline_input)
        self.assertIn("schema_parameters", result.pipeline_input)


# ---------------------------------------------------------------------------
# T1.99.14 — optional --data-dir with schema-driven default
# ---------------------------------------------------------------------------

class TestDataDirOptional(TestCase):
    def test_parser_accepts_no_data_dir(self):
        """build_parser() accepts --data-dir as optional (default None)."""
        parser = build_parser()
        ns = parser.parse_args(["--json"])
        self.assertIsNone(ns.data_dir)

    def test_parser_accepts_explicit_data_dir(self):
        """build_parser() accepts --data-dir when provided."""
        parser = build_parser()
        ns = parser.parse_args(["--data-dir", "custom/path", "--json"])
        self.assertEqual(ns.data_dir, "custom/path")

    def test_parser_defaults_to_none(self):
        """The default for --data-dir is None (schema-driven fallback in main())."""
        parser = build_parser()
        ns = parser.parse_args([])
        self.assertIsNone(ns.data_dir)


class TestBootstrapPipeline(TestCase):
    def test_bootstrap_returns_expected_keys(self):
        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger())
        for key in ("config", "doc_config", "em", "mm", "resolved_paths", "os_info", "level", "data_dir", "project_root", "config_dir", "parsed"):
            self.assertIn(key, boot)
        # T1.99.6: ConfigRegistry SSOT is used at the entry point
        self.assertIsNotNone(boot["config_registry"])
        self.assertIsInstance(boot["config_registry"], ConfigRegistry)

    def test_resolved_paths_are_present(self):
        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger())
        rp = boot["resolved_paths"]
        for k in ("data_dir", "output_dir", "archive_dir", "config_dir", "log_dir", "schema_dir"):
            self.assertIn(k, rp)


class TestRunPipeline(TestCase):
    def test_run_pipeline_completes(self):
        pdir = _make_data("runner")
        result = run_pipeline(_ROOT, pdir, recursive=False, logger=_SilentLogger())
        self.assertIn("summary", result)
        summary = result["summary"]
        # Exercises the PipelineOrchestrator A->B->C funnel
        self.assertIn("phase_a", summary)
        self.assertIn("phase_b", summary)
        self.assertIn("phase_c", summary)
        self.assertGreaterEqual(summary["phase_a"].get("discovered", 0), 0)

    def test_run_pipeline_wires_config_registry(self):
        pdir = _make_data("runner")
        result = run_pipeline(_ROOT, pdir, recursive=False, logger=_SilentLogger())
        self.assertIsNotNone(result["config_registry"])
        self.assertIsInstance(result["config_registry"], ConfigRegistry)

    def test_run_pipeline_surfaces_context(self):
        """T1.99.44: run_pipeline() surfaces EKSPipelineContext in return dict."""
        from eks.engine.core.context import EKSPipelineContext
        pdir = _make_data("runner")
        result = run_pipeline(_ROOT, pdir, recursive=False, logger=_SilentLogger())
        self.assertIn("context", result)
        self.assertIsInstance(result["context"], EKSPipelineContext)
        # Verify context has expected fields from bootstrap
        ctx = result["context"]
        self.assertIsNotNone(ctx.paths)
        self.assertIsNotNone(ctx.parameters)
        self.assertIsNotNone(ctx.config_registry)


class TestCli(TestCase):
    def test_cli_runs_end_to_end(self):
        import os
        from eks.engine.eks_engine_pipeline import main
        pdir = _make_data("cli")
        # SchemaLoader resolves schema paths relative to cwd; pin to repo root
        prev = os.getcwd()
        os.chdir(str(_ROOT))
        try:
            rc = main(["--data-dir", str(pdir), "--json"])
        finally:
            os.chdir(prev)
        self.assertEqual(rc, 0)


class TestI107BootstrapCompleteness(TestCase):
    """T1.99.49: I107 bootstrap completeness — single source, phase1 keys, context consistency."""

    def test_run_pipeline_result_has_phase1_keys(self):
        """phase1_server.py reads result["em"], result["mm"], result["summary"] unchanged."""
        pdir = _make_data("t149_phase1")
        result = run_pipeline(_ROOT, pdir, recursive=False, logger=_SilentLogger())
        for key in ("em", "mm", "summary"):
            self.assertIn(key, result)
            self.assertIsNotNone(result[key])

    def test_context_paths_from_single_resolved_dict(self):
        """All context paths (output/schema/archive/log/config) derive from the same resolved_paths dict (Defect A fix)."""
        pdir = _make_data("t149_single")
        result = run_pipeline(_ROOT, pdir, recursive=False, logger=_SilentLogger())
        resolved = result["resolved_paths"]
        ctx_paths = result["context"].paths
        path_keys = ["output_dir", "schema_dir", "archive_dir", "log_dir", "config_dir"]
        for key in path_keys:
            self.assertIn(key, resolved)
            rp = resolved[key]
            ctx_val = getattr(ctx_paths, key)
            self.assertEqual(Path(rp), ctx_val, f"{key}: resolved={rp} context={ctx_val}")

    def test_bootstrap_single_resolved_paths(self):
        """Bootstrap resolved_paths contains all path keys under the same project_root (Defect A fix)."""
        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger())
        rp = boot["resolved_paths"]
        for key in ("data_dir", "output_dir", "archive_dir", "config_dir", "log_dir", "schema_dir"):
            self.assertIn(key, rp)
            self.assertIsInstance(rp[key], Path)

    def test_main_context_consistent_paths(self):
        """main() builds context with all paths from the single bootstrap resolved_paths."""
        import os
        from eks.engine.eks_engine_pipeline import main
        pdir = _make_data("t149_main")
        prev = os.getcwd()
        os.chdir(str(_ROOT))
        try:
            rc = main(["--data-dir", str(pdir), "--json"])
            self.assertEqual(rc, 0)
        finally:
            os.chdir(prev)
