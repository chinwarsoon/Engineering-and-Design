"""
Tests for the shared pipeline entry funnel (T1.99a/b/c/f).

Revision: 0.1
Date: 2026-07-11
Author: opencode
"""
import sys
import uuid
from pathlib import Path
from unittest import TestCase

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from eks.engine.core.pipeline_runner import bootstrap_pipeline, run_pipeline
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


class TestBootstrapPipeline(TestCase):
    def test_bootstrap_returns_expected_keys(self):
        boot = bootstrap_pipeline(_ROOT, logger=_SilentLogger())
        for key in ("config", "doc_config", "em", "mm", "resolved_paths"):
            self.assertIn(key, boot)
        # T1.99f: ConfigRegistry SSOT is used at the entry point
        self.assertIsNotNone(boot["config_registry"])
        self.assertIsInstance(boot["config_registry"], ConfigRegistry)

    def test_resolved_paths_are_present(self):
        boot = bootstrap_pipeline(_ROOT, logger=_SilentLogger())
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


class TestCli(TestCase):
    def test_cli_runs_end_to_end(self):
        import os
        from eks.engine.parsers.cli import run
        pdir = _make_data("cli")
        # SchemaLoader resolves schema paths relative to cwd; pin to repo root
        prev = os.getcwd()
        os.chdir(str(_ROOT))
        try:
            rc = run(["--data-dir", str(pdir), "--json"])
        finally:
            os.chdir(prev)
        self.assertEqual(rc, 0)
