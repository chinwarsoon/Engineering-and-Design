"""
Tests for the health-scorer CLI entry point (T1.56.2 / I093).

The CLI is wired to the real HealthScorer via the shared bootstrap funnel and
the DuckDB document registry. These tests mock the heavy machinery so no live
DuckDB connection is required.
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


class _FakeRegistry:
    def __init__(self, *a, **k):
        pass

    def get_document(self, doc_id, revision=None):
        return {"id": doc_id, "document_number": doc_id, "project_number": "P1"}

    def list_documents(self, latest_only=True):
        return [
            {"id": "D1", "document_number": "DOC-001", "project_number": "P1"},
            {"id": "D2", "document_number": "DOC-002", "project_number": "P1"},
        ]


class _FakeRegistryEmpty(_FakeRegistry):
    def get_document(self, doc_id, revision=None):
        return None

    def list_documents(self, latest_only=True):
        return []


class _FakeScorer:
    def __init__(self, *a, **k):
        pass

    def score(self, metadata, **kwargs):
        return {"health_score": 0.85, "extract_status": "success", "dimensions": {}}

    def score_batch(self, documents, **kwargs):
        return {
            "avg_document_health": 0.80,
            "total_documents": len(documents),
            "by_status": {"success": 2, "partial": 0, "failed": 0},
        }


class TestHealthCli(TestCase):
    def _run(self, argv, registry_cls=_FakeRegistry):
        from eks.engine.core.health_cli import HealthScorerEngineCLI
        with patch("eks.engine.eks_engine_pipeline.bootstrap_pipeline", _fake_bootstrap), \
             patch("eks.engine.core.registry.DocumentRegistry", registry_cls), \
             patch("eks.engine.core.health_scorer.HealthScorer", _FakeScorer):
            return HealthScorerEngineCLI().run(argv)

    def test_single_document_scoring(self):
        out = self._run(["--data-dir", "dummy", "--document-id", "DOC-001"])
        self.assertEqual(out.status, "SUCCESS")
        self.assertEqual(out.metadata["result"]["mode"], "single")
        self.assertEqual(out.metadata["result"]["score"]["health_score"], 0.85)

    def test_batch_scoring(self):
        out = self._run(["--data-dir", "dummy", "--batch"])
        self.assertEqual(out.status, "SUCCESS")
        self.assertEqual(out.metadata["result"]["mode"], "batch")
        self.assertEqual(out.metadata["result"]["total_documents"], 2)

    def test_missing_document_fails(self):
        out = self._run(["--data-dir", "dummy", "--document-id", "NOPE"], _FakeRegistryEmpty)
        self.assertEqual(out.status, "FAILED")
        self.assertEqual(len(out.errors), 1)

    def test_no_documents_fails(self):
        out = self._run(["--data-dir", "dummy", "--batch"], _FakeRegistryEmpty)
        self.assertEqual(out.status, "FAILED")
        self.assertEqual(len(out.errors), 1)
        self.assertIsInstance(out.errors[0], ErrorRecord)
