"""
Tests for the discovery CLI entry point (T1.56.1 / I093).

The CLI is wired to the real PipelineOrchestrator.run_phase_a via the shared
bootstrap funnel. These tests mock the heavy engine/registry machinery so no
live DuckDB connection or filesystem scan is required.
"""
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from eks.engine.core.base import EngineOutput, ErrorRecord


def _fake_bootstrap(*a, **k):
    return {
        "config": {}, "doc_config": {}, "em": None, "mm": None,
        "resolved_paths": {}, "config_registry": None,
    }


class _FakeOrchestrator:
    def __init__(self, *a, **k):
        self.captured = (a, k)

    def run_phase_a(self, root_dir, recursive=True):
        return {"discovered": 3, "valid": 2, "unknown": 1, "registered": 2}


class _FakeOrchestratorBoom:
    def __init__(self, *a, **k):
        pass

    def run_phase_a(self, root_dir, recursive=True):
        raise RuntimeError("scan exploded")


class TestDiscoveryCli(TestCase):
    def _run(self, argv, orchestrator_cls=_FakeOrchestrator):
        from eks.engine.core.discovery_cli import DiscoveryEngineCLI
        with patch("eks.engine.eks_engine_pipeline.bootstrap_pipeline", _fake_bootstrap), \
             patch("eks.engine.core.pipeline_orchestrator.PipelineOrchestrator", orchestrator_cls), \
             patch("eks.engine.core.registry.DocumentRegistry"):
            return DiscoveryEngineCLI().run(argv)

    def test_discovery_runs_real_engine(self):
        out = self._run(["--data-dir", "dummy", "--scan"])
        self.assertIsInstance(out, EngineOutput)
        self.assertEqual(out.status, "SUCCESS")
        self.assertEqual(out.errors, [])
        self.assertEqual(out.metadata["summary"]["registered"], 2)

    def test_discovery_validate_flag(self):
        out = self._run(["--data-dir", "dummy", "--validate"])
        self.assertEqual(out.status, "SUCCESS")
        self.assertTrue(out.metadata["validate"])

    def test_discovery_engine_error_is_reported(self):
        out = self._run(["--data-dir", "dummy", "--scan"], _FakeOrchestratorBoom)
        self.assertEqual(out.status, "FAILED")
        self.assertEqual(len(out.errors), 1)
        self.assertIsInstance(out.errors[0], ErrorRecord)
