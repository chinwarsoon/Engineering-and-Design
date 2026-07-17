"""
Tests for L19 — Universal BootstrapManager.

Covers: phase tracking, pre/post-load traces, to_pipeline_context(),
bootstrap_for_ui() dual-mode, BootstrapError raising + to_system_error(),
phase registry ordering, is_bootstrapped gate, bootstrap_summary.

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.55 — Universal BootstrapManager tests for L19.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from common.library.bootstrap import (
    BootstrapError,
    BootstrapManager,
    BootstrapPhaseRegistry,
    BootstrapPhaseStatus,
)


class TestBootstrapError(unittest.TestCase):
    """T1.99.54: Universal BootstrapError."""

    def test_error_creation(self):
        """BootstrapError carries code, message, and phase."""
        err = BootstrapError("P1-BOOT-READINESS", "Readiness gate failed", "readiness")
        self.assertEqual(err.code, "P1-BOOT-READINESS")
        self.assertEqual(err.message, "Readiness gate failed")
        self.assertEqual(err.phase, "readiness")
        self.assertIn("[P1-BOOT-READINESS]", str(err))
        self.assertIn("(phase: readiness)", str(err))

    def test_to_system_error(self):
        """to_system_error() returns (code, message) tuple."""
        err = BootstrapError("B-CLI-001", "CLI parsing failed", "cli")
        code, msg = err.to_system_error()
        self.assertEqual(code, "B-CLI-001")
        self.assertEqual(msg, "CLI parsing failed")

    def test_to_dict(self):
        """to_dict() serializes error to JSON-safe dict."""
        err = BootstrapError("B-PATH-001", "Path not found", "paths")
        d = err.to_dict()
        self.assertEqual(d["code"], "B-PATH-001")
        self.assertEqual(d["message"], "Path not found")
        self.assertEqual(d["phase"], "paths")

    def test_from_system_error(self):
        """from_system_error() reconstructs from (code, message) pair."""
        err = BootstrapError.from_system_error("B-ENV-001", "OS detection failed", "env")
        self.assertEqual(err.code, "B-ENV-001")
        self.assertEqual(err.message, "OS detection failed")
        self.assertEqual(err.phase, "env")


class TestBootstrapPhaseRegistry(unittest.TestCase):
    """T1.99.51: BootstrapPhaseRegistry."""

    def test_default_phases(self):
        """Default registry has 8 phases in correct order."""
        reg = BootstrapPhaseRegistry()
        phases = list(reg.iter_ordered())
        self.assertEqual(len(phases), 8)
        self.assertEqual(phases[0].phase_id, "P1_cli")
        self.assertEqual(phases[7].phase_id, "P8_params")

    def test_get_phase(self):
        """get() retrieves a phase entry."""
        reg = BootstrapPhaseRegistry()
        entry = reg.get("P1_cli")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.phase_name, "CLI Parsing")
        self.assertEqual(entry.order, 1)

    def test_get_phase_name(self):
        """get_phase_name() returns human-readable name."""
        reg = BootstrapPhaseRegistry()
        self.assertEqual(reg.get_phase_name("P1_cli"), "CLI Parsing")
        self.assertEqual(reg.get_phase_name("NONEXISTENT"), "NONEXISTENT")

    def test_get_method(self):
        """get_method() returns method name."""
        reg = BootstrapPhaseRegistry()
        self.assertEqual(reg.get_method("P1_cli"), "_bootstrap_cli")
        self.assertEqual(reg.get_method("NONEXISTENT"), "")

    def test_register_custom_phase(self):
        """register() adds a custom phase."""
        reg = BootstrapPhaseRegistry()
        reg.register("P9_custom", "Custom Phase", 9, "_bootstrap_custom")
        entry = reg.get("P9_custom")
        self.assertEqual(entry.phase_name, "Custom Phase")
        self.assertEqual(entry.order, 9)
        self.assertEqual(entry.method, "_bootstrap_custom")

    def test_register_replaces_existing(self):
        """register() replaces an existing phase."""
        reg = BootstrapPhaseRegistry()
        reg.register("P1_cli", "Custom CLI", 10, "_custom_cli")
        entry = reg.get("P1_cli")
        self.assertEqual(entry.phase_name, "Custom CLI")
        self.assertEqual(entry.order, 10)

    def test_remove_phase(self):
        """remove() deletes a phase."""
        reg = BootstrapPhaseRegistry()
        reg.remove("P5_fallback")
        self.assertIsNone(reg.get("P5_fallback"))
        phases = list(reg.iter_ordered())
        self.assertEqual(len(phases), 7)

    def test_build_phase_status(self):
        """build_phase_status() creates tracking dict."""
        reg = BootstrapPhaseRegistry()
        status = reg.build_phase_status()
        self.assertEqual(len(status), 8)
        self.assertIsInstance(status["P1_cli"], BootstrapPhaseStatus)
        self.assertEqual(status["P1_cli"].status, "pending")

    def test_phase_count(self):
        """phase_count returns the number of phases."""
        reg = BootstrapPhaseRegistry()
        self.assertEqual(reg.phase_count, 8)
        reg.remove("P5_fallback")
        self.assertEqual(reg.phase_count, 7)

    def test_to_list(self):
        """to_list() serializes all phases."""
        reg = BootstrapPhaseRegistry()
        lst = reg.to_list()
        self.assertEqual(len(lst), 8)
        self.assertEqual(lst[0]["phase_id"], "P1_cli")


class TestBootstrapManager(unittest.TestCase):
    """T1.99.50: Universal BootstrapManager."""

    def setUp(self):
        self.tmp = Path(__file__).parent / "_test_bootstrap_tmp"
        self.tmp.mkdir(exist_ok=True)
        self.project_root = self.tmp / "test_project"
        self.project_root.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _basic_manager(self, **kwargs):
        """Create a minimal BootstrapManager with no project-specific hooks."""
        return BootstrapManager(
            project_root=self.project_root,
            pipeline_root_dir="eks",
            pipeline_dir="engine",
            **kwargs,
        )

    def test_constructor_defaults(self):
        """BootstrapManager initializes with defaults."""
        mgr = self._basic_manager()
        self.assertEqual(mgr.project_root, self.project_root)
        self.assertEqual(mgr.pipeline_root_dir, "eks")
        self.assertEqual(mgr.pipeline_dir, "engine")
        self.assertFalse(mgr.is_bootstrapped)
        self.assertEqual(len(mgr._phase_status), 8)

    def test_phase_tracking_start_complete(self):
        """_record_phase_start + _record_phase_complete track timing."""
        mgr = self._basic_manager()
        mgr._record_phase_start("P1_cli")
        self.assertEqual(mgr._phase_status["P1_cli"].status, "running")
        self.assertIsNotNone(mgr._phase_status["P1_cli"].start_time)
        mgr._record_phase_complete("P1_cli")
        self.assertEqual(mgr._phase_status["P1_cli"].status, "complete")
        self.assertIsNotNone(mgr._phase_status["P1_cli"].end_time)
        self.assertIsNotNone(mgr._phase_status["P1_cli"].duration_ms)

    def test_phase_tracking_failure(self):
        """_record_phase_failure marks phase as failed with error code."""
        mgr = self._basic_manager()
        mgr._record_phase_start("P2_paths")
        mgr._record_phase_failure("P2_paths", "B-PATH-001")
        self.assertEqual(mgr._phase_status["P2_paths"].status, "failed")
        self.assertEqual(mgr._phase_status["P2_paths"].error_code, "B-PATH-001")

    def test_bootstrap_all_no_hooks(self):
        """bootstrap_all() completes even without project hooks (uses defaults)."""
        mgr = self._basic_manager()
        result = mgr.bootstrap_all()
        self.assertIs(result, mgr)  # returns self for chaining
        self.assertTrue(mgr.is_bootstrapped)
        summary = mgr.bootstrap_summary
        self.assertEqual(summary["status"], "complete")
        self.assertEqual(summary["completed_count"], 8)

    def test_bootstrap_summary_partial(self):
        """bootstrap_summary reports partial when some phases complete."""
        mgr = self._basic_manager()
        mgr._record_phase_start("P1_cli")
        mgr._record_phase_complete("P1_cli")
        summary = mgr.bootstrap_summary
        self.assertEqual(summary["status"], "partial")
        self.assertEqual(summary["completed_count"], 1)

    def test_bootstrap_summary_failed(self):
        """bootstrap_summary reports failed when a phase fails."""
        mgr = self._basic_manager()
        mgr._record_phase_start("P1_cli")
        mgr._record_phase_complete("P1_cli")
        mgr._record_phase_start("P2_paths")
        mgr._record_phase_failure("P2_paths", "B-PATH-001")
        summary = mgr.bootstrap_summary
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["failed_phase"], "P2_paths")
        self.assertEqual(summary["error_code"], "B-PATH-001")

    def test_is_bootstrapped_gate(self):
        """is_bootstrapped is False before bootstrap, True after."""
        mgr = self._basic_manager()
        self.assertFalse(mgr.is_bootstrapped)
        mgr.bootstrap_all()
        self.assertTrue(mgr.is_bootstrapped)

    def test_preload_trace_requires_bootstrap(self):
        """preload_trace raises BootstrapError before bootstrap."""
        mgr = self._basic_manager()
        with self.assertRaises(BootstrapError) as ctx:
            _ = mgr.preload_trace
        self.assertIn("B-BOOT-0601", ctx.exception.code)

    def test_to_pipeline_context_requires_bootstrap(self):
        """to_pipeline_context() raises if not bootstrapped."""
        mgr = self._basic_manager()
        with self.assertRaises(BootstrapError) as ctx:
            mgr.to_pipeline_context()
        self.assertIn("B-CTX-001", ctx.exception.code)

    def test_to_pipeline_context_after_bootstrap(self):
        """to_pipeline_context() returns a context dict after bootstrap."""
        mgr = self._basic_manager()
        mgr.bootstrap_all()
        ctx = mgr.to_pipeline_context()
        self.assertIsInstance(ctx, dict)
        self.assertIn("project_root", ctx)
        self.assertIn("resolved_paths", ctx)
        self.assertIn("parameters", ctx)

    def test_to_dict_backward_compat(self):
        """to_dict() returns backward-compatible dict matching EKS shape."""
        mgr = self._basic_manager()
        mgr.bootstrap_all()
        d = mgr.to_dict()
        self.assertIn("config", d)
        self.assertIn("em", d)
        self.assertIn("mm", d)
        self.assertIn("resolved_paths", d)
        self.assertIn("os_info", d)
        self.assertIn("data_dir", d)
        self.assertIn("project_root", d)
        self.assertIn("config_dir", d)

    def test_bootstrap_all_with_mock_hooks(self):
        """bootstrap_all() uses injected hooks when provided."""
        mock_os = MagicMock(return_value="linux")
        mock_config = MagicMock(return_value={"global_paths": {"data_dir": "mydata"}})
        mock_cli = MagicMock()

        mgr = BootstrapManager(
            project_root=self.project_root,
            os_detector=mock_os,
            config_loader=mock_config,
            cli_parser=mock_cli,
        )
        mgr.bootstrap_all(["test_arg"])
        mock_cli.assert_called_once_with(["test_arg"])
        mock_os.assert_called_once()
        self.assertEqual(mgr.os_info, "linux")

    def test_bootstrap_for_ui_mode(self):
        """bootstrap_for_ui() skips CLI parsing, uses UI params."""
        mgr = self._basic_manager()
        mgr.bootstrap_for_ui(debug_mode=True, upload_file="test.xlsx")
        self.assertTrue(mgr.is_bootstrapped)
        self.assertTrue(mgr.cli_overrides_provided)
        self.assertEqual(mgr.cli_args.get("debug_mode"), True)
        self.assertEqual(mgr.cli_args.get("upload_file"), "test.xlsx")

    def test_bootstrap_for_ui_with_no_params(self):
        """bootstrap_for_ui() works with empty params."""
        mgr = self._basic_manager()
        mgr.bootstrap_for_ui()
        self.assertTrue(mgr.is_bootstrapped)
        self.assertFalse(mgr.cli_overrides_provided)

    def test_run_readiness_gate_no_factory(self):
        """_run_readiness_gate returns True when no validator factory."""
        mgr = self._basic_manager()
        self.assertTrue(mgr._run_readiness_gate())

    def test_run_phase_wraps_exception(self):
        """_run_phase wraps unexpected exceptions in BootstrapError."""
        mgr = self._basic_manager()

        def _failing():
            raise ValueError("unexpected")

        with self.assertRaises(BootstrapError) as ctx:
            mgr._run_phase("P1_cli", _failing)
        self.assertIn("P1_cli", ctx.exception.code)
        self.assertIn("unexpected", ctx.exception.message)

    def test_phase_status_read_only(self):
        """phase_status property returns the tracking dict."""
        mgr = self._basic_manager()
        status = mgr.phase_status
        self.assertEqual(len(status), 8)
        self.assertEqual(status["P1_cli"].phase_name, "CLI Parsing")


class TestBootstrapManagerPhases(unittest.TestCase):
    """Individual phase tests."""

    def setUp(self):
        self.tmp = Path(__file__).parent / "_test_bootstrap_phases_tmp"
        self.tmp.mkdir(exist_ok=True)
        self.project_root = self.tmp / "test_project"
        self.project_root.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _manager(self, **kwargs):
        return BootstrapManager(
            project_root=self.project_root,
            pipeline_root_dir="eks",
            pipeline_dir="engine",
            **kwargs,
        )

    def test_p2_paths_fails_on_missing_root(self):
        """P2 raises BootstrapError when project_root doesn't exist."""
        mgr = BootstrapManager(
            project_root=self.tmp / "nonexistent",
        )
        with self.assertRaises(BootstrapError) as ctx:
            mgr.bootstrap_all()
        self.assertIn("B-PATH-001", ctx.exception.code)

    def test_p2_paths_with_resolver(self):
        """P2 uses path_resolver hook when provided."""
        mock_resolver = MagicMock(return_value={
            "data_dir": self.project_root / "data",
            "output_dir": self.project_root / "output",
        })
        mgr = self._manager(path_resolver=mock_resolver)
        mgr.bootstrap_all()
        mock_resolver.assert_called_once()
        self.assertIn("data_dir", mgr.resolved_paths)

    def test_p3_registry_with_loader(self):
        """P3 uses config_loader hook when provided."""
        mock_loader = MagicMock(return_value={"key": "value"})
        mgr = self._manager(config_loader=mock_loader)
        mgr.bootstrap_all()
        mock_loader.assert_called_once()
        self.assertEqual(mgr.config, {"key": "value"})

    def test_p6_env_with_detector(self):
        """P6 uses os_detector hook when provided."""
        mock_os = MagicMock(return_value="windows")
        mgr = self._manager(os_detector=mock_os)
        mgr.bootstrap_all()
        mock_os.assert_called_once()
        self.assertEqual(mgr.os_info, "windows")

    def test_p8_params_precedence(self):
        """P8 merges native < schema < CLI precedence."""
        mgr = self._manager(
            config_loader=MagicMock(return_value={
                "system_parameters": {"log_level": 2},
                "global_paths": {"data_dir": "mydata"},
            }),
        )
        mgr.bootstrap_all()
        # Native defaults include data_dir from global_paths
        self.assertEqual(mgr.effective_parameters.get("log_level"), 2)

    def test_bootstrap_all_returns_self(self):
        """bootstrap_all() returns self for method chaining."""
        mgr = self._manager()
        ctx = mgr.bootstrap_all().to_pipeline_context()
        self.assertIsInstance(ctx, dict)


if __name__ == "__main__":
    unittest.main()
