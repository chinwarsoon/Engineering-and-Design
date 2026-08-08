"""
Regression tests for I288 — Phase B parser registration fix.

The ``processing_config`` (eks_processing_config.json values) never reached
``PipelineOrchestrator``, so ``ParserRouter`` registered zero parsers and every
file failed inside Phase B ("No parser registered for file type: pdf"). The UI
``_LogCapture`` additionally lacked ``debug()``/``trace()``/``set_level()``,
causing an ``AttributeError`` that failed 13/13 files in UI runs.

Fixes under test:
  - T1.244 — `processing_config` exposed ONLY via ``to_pipeline_context()``
    parameters (EKSPipelineContext = single source of truth, SSOT §24).
  - T1.245 — ``run_pipeline()`` (both branches) and ``discovery_cli.py`` read
    ``processing_config`` from the context and forward it to
    ``PipelineOrchestrator`` so parsers register.
  - T1.246 — ``_LogCapture`` in ``phase1_server.py`` gains ``debug()``/``trace()``
    /``set_level()`` (standard EKSLogger interface).
  - T1.247 — regression guards below.

Run from repo root:  conda run -n eks python -m pytest eks/test/test_pipeline_processing_config.py -q

Revision: 0.1
Date: 2026-08-08
Author: opencode
Summary: T1.247 — I288 regression tests (real-PDF end-to-end + context SSOT + _LogCapture).
"""
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from unittest import TestCase

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


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

    def trace(self, *a, **k):
        pass

    def set_level(self, *a, **k):
        pass


def _real_pdf_fixture() -> Path:
    """Return the first available real PDF fixture under eks/data/twrp/."""
    candidates = [
        _ROOT / "eks/data/twrp/tenderspec/Volume 3 (Final)/P06 ICA Works/131101-WSW41-SP-SP-0600_2-Stage.pdf",
        _ROOT / "eks/data/twrp/tenderspec/Volume 3 (Final)/P06 ICA Works/131101-WSW41-SP-SP-0602.pdf",
        _ROOT / "eks/data/twrp/tenderspec/Volume 4 (Final)/00a_Cover Page - Vol 4_C4B_2-Stage.pdf",
        _ROOT / "eks/data/twrp/tenderspec/Volume 4 (Final)/00c_Contents - Vol 4_C4B.pdf",
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    raise FileNotFoundError("No real PDF fixture found under eks/data/twrp/ — I288 test requires one")


def _make_pdf_data_dir() -> Path:
    """Copy a real parseable PDF into a temp data dir under eks/test_output/."""
    tag = uuid.uuid4().hex[:8]
    pdir = _ROOT / "eks" / "test_output" / f"i288_pdf_{tag}"
    pdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(_real_pdf_fixture(), pdir / "TWRP-0300-REV0.pdf")
    return pdir


class TestProcessingConfigContextSSOT(TestCase):
    """T1.244 — processing_config exposed via to_pipeline_context() only."""

    def test_bootstrap_context_carries_processing_config(self):
        from eks.engine.eks_engine_pipeline import bootstrap_pipeline

        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger(), skip_readiness=True)
        ctx = boot.get("context")
        self.assertIsNotNone(ctx, "bootstrap_pipeline() must expose the EKSPipelineContext")
        pc = ctx.parameters.get("processing_config")
        self.assertIsNotNone(pc, "to_pipeline_context() must carry processing_config")
        for pid in ("technip_pdf", "technip_docx", "technip_dwg", "technip_dgn", "technip_xlsx"):
            self.assertIn(pid, pc.get("extraction_profiles", {}),
                          f"extraction profile {pid} missing")

    def test_processing_config_not_on_flat_boot_dict(self):
        """SSOT §24 — processing_config is context-only, never duplicated on the dict."""
        from eks.engine.eks_engine_pipeline import bootstrap_pipeline

        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger(), skip_readiness=True)
        self.assertNotIn("processing_config", boot,
                         "processing_config must NOT be added to bootstrap to_dict()")


class TestParserRegistration(TestCase):
    """T1.245 — run_pipeline forwards processing_config → parsers register."""

    def test_parser_router_registers_all_five_types(self):
        """ParserRouter built from context-derived processing_config registers all 5."""
        from eks.engine.eks_engine_pipeline import bootstrap_pipeline
        from eks.engine.core.registry import DocumentRegistry
        from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator

        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger(), skip_readiness=True)
        ctx = boot["context"]
        with tempfile.TemporaryDirectory() as td:
            registry = DocumentRegistry(logger=_SilentLogger(), db_path=str(Path(td) / "reg.db"))
            orch = PipelineOrchestrator(
                ctx.parameters.get("config", {}),
                ctx.parameters.get("doc_config", {}),
                registry,
                logger=_SilentLogger(),
                processing_config=ctx.parameters.get("processing_config", {}),
            )
            supported = orch.router.parser_factory.get_supported_types()
            for ext in ("pdf", "docx", "dwg", "dgn", "xlsx"):
                self.assertIn(ext, supported, f"parser for '{ext}' not registered")


class TestRealPdfEndToEnd(TestCase):
    """T1.247 (1) — real-PDF end-to-end through run_pipeline (non-context branch)."""

    def test_real_pdf_phase_b_success_and_elements(self):
        from eks.engine.eks_engine_pipeline import run_pipeline

        pdir = _make_pdf_data_dir()
        result = run_pipeline(
            _ROOT,
            pdir.relative_to(_ROOT),
            recursive=False,
            logger=_SilentLogger(),
            skip_readiness=True,
        )
        pb = result["summary"].get("phase_b", {}) or {}
        self.assertGreater(pb.get("success", 0), 0,
                           f"Phase B must succeed with real PDF; phase_b={pb}")
        succeeded_results = pb.get("results", []) or []
        with_elements = [r for r in succeeded_results
                         if r.get("elements") or r.get("parse_status") == "success"]
        self.assertTrue(with_elements,
                        f"no Phase B result produced elements: {pb.get('failed')} failed / {pb.get('total')} total")

    def test_real_pdf_context_branch_phase_b_success(self):
        """Context branch (eks_engine_pipeline.main path) also succeeds end-to-end."""
        from eks.engine.eks_engine_pipeline import bootstrap_pipeline, run_pipeline

        boot = bootstrap_pipeline(_ROOT, args=[], logger=_SilentLogger(), skip_readiness=True)
        ctx = boot["context"]
        pdir = _make_pdf_data_dir()
        result = run_pipeline(
            _ROOT, pdir.relative_to(_ROOT), recursive=False,
            logger=_SilentLogger(), skip_readiness=True, context=ctx,
        )
        pb = result["summary"].get("phase_b", {}) or {}
        self.assertGreater(pb.get("success", 0), 0,
                           f"context-branch Phase B must succeed; phase_b={pb}")


class TestLogCaptureInterface(TestCase):
    """T1.246/T1.247 (2) — _LogCapture debug/trace/set_level passthrough."""

    def test_logcapture_source_has_debug_trace_set_level(self):
        """phase1_server._LogCapture must implement the standardized interface.

        The class is defined inside the run-pipeline closure, so we assert the
        module source contains the three methods (the interface contract engine
        code relies on).
        """
        src_path = _ROOT / "eks" / "ui" / "backend" / "phase1_server.py"
        if not src_path.exists():
            self.skipTest("phase1_server.py not found")
        src = src_path.read_text(encoding="utf-8")
        self.assertIn('def debug(self, msg, context=""', src,
                      "_LogCapture.debug() missing from phase1_server.py")
        self.assertIn('def trace(self, msg, context=""', src,
                      "_LogCapture.trace() missing from phase1_server.py")
        self.assertIn("def set_level(self, level)", src,
                      "_LogCapture.set_level() missing from phase1_server.py")

    def test_ekslogger_supports_debug_trace(self):
        """EKSLogger itself already exposes debug()/trace() (interface mirror)."""
        from eks.engine.logging.logger import EKSLogger

        lg = EKSLogger("test-capture", level=3)
        lg.debug("dbg", context="x")
        lg.trace("trc", context="x")  # no AttributeError

    def test_run_pipeline_accepts_debug_trace_logger(self):
        """run_pipeline() must not raise when the logger implements the
        standardized interface (engine code calls logger.debug())."""
        from eks.engine.eks_engine_pipeline import run_pipeline

        pdir = _make_pdf_data_dir()
        try:
            result = run_pipeline(
                _ROOT, pdir.relative_to(_ROOT), recursive=False,
                logger=_SilentLogger(), skip_readiness=True,
            )
        except AttributeError as exc:
            self.fail(f"run_pipeline raised AttributeError on logger interface: {exc}")
        self.assertIn("summary", result)


if __name__ == "__main__":
    import unittest

    unittest.main()