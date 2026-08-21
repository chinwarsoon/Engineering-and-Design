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

Revision: 0.2
Date: 2026-08-21
Author: opencode
Summary: T1.315/I317 — real-PDF fixture resolver rewritten: glob eks/test/data/*.pdf as
  primary (committed TWRP samples), non-fatal local fallback repointed to
  eks/data/twrp/project_spec/Volume 5, recorded SkipTest (warn) when no fixture exists.
"""
import shutil
import sys
import tempfile
import uuid
import warnings
from pathlib import Path
from unittest import TestCase, SkipTest

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
    """Locate a real PDF fixture for the I288 real-PDF regression tests (I317).

    Resolution order (non-fatal — returns ``None`` if nothing is found):
      1. Committed sample PDFs under ``eks/test/data/*.pdf`` — a curated subset of
         real TWRP documents tracked in git (3 samples covering 3 projects / 3
         doc-types SG·DR·DS / 3 disciplines). PRIMARY, CI-safe source.
      2. Optional local fallback to the real (gitignored) TWRP corpus at
         ``eks/data/twrp/project_spec/Volume 5`` — only present on developer
         machines that checked out the full corpus; never required in CI. (The
         stale ``tenderspec/Volume 3 (Final)|Volume 4 (Final)`` paths were
         removed — the real corpus lives under ``project_spec/Volume 5``.)
    """
    primary = sorted(_ROOT.glob("eks/test/data/*.pdf"))
    if primary:
        return primary[0]
    for d in (_ROOT / "eks/data/twrp/project_spec/Volume 5",):
        if d.exists():
            hits = sorted(d.rglob("*.pdf"))
            if hits:
                return hits[0]
    return None


def _make_pdf_data_dir() -> Path:
    """Copy a real parseable PDF into a temp data dir under eks/test_output/.

    Skips (never hard-fails) when no real PDF fixture is available — see I317:
    CI without the committed samples stays green while the gap is still surfaced.
    """
    src = _real_pdf_fixture()
    if src is None:
        warnings.warn(
            "I317: no real PDF fixture available (eks/test/data/*.pdf absent and no "
            "local eks/data/twrp/project_spec/Volume 5 corpus) — skipping real-PDF "
            "regression tests so CI stays green.",
            stacklevel=2,
        )
        raise SkipTest("no real PDF fixture available (I317)")
    tag = uuid.uuid4().hex[:8]
    pdir = _ROOT / "eks" / "test_output" / f"i288_pdf_{tag}"
    pdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, pdir / "TWRP-0300-REV0.pdf")
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