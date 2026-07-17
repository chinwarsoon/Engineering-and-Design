"""
Tests for BaseMessageManager: icon support, verbosity clamp, show() fallback.
"""
import json
import tempfile
import unittest
from pathlib import Path

from common.library.core.messages.message_manager import BaseMessageManager


class TestBaseMessageManager(unittest.TestCase):

    def setUp(self):
        self._tmpdir = Path(tempfile.mkdtemp())
        schemas = self._tmpdir / "schemas"
        schemas.mkdir(parents=True, exist_ok=True)
        config = {
            "messages": {
                "TEST_INFO": {
                    "template": "Hello {name}",
                    "level": 1,
                    "category": "info"
                },
                "TEST_WARN": {
                    "template": "Warning: {detail}",
                    "level": 2,
                    "category": "warning"
                },
                "TEST_ICON": {
                    "template": "Processed {n} items",
                    "level": 1,
                    "category": "milestone",
                    "icon": "✓"
                }
            }
        }
        (schemas / "test_catalog.json").write_text(json.dumps(config), encoding="utf-8")

        class TestMM(BaseMessageManager):
            _catalog_filename = "test_catalog.json"

        self.mm = TestMM(config_dir=str(self._tmpdir))

    def tearDown(self):
        import shutil
        shutil.rmtree(str(self._tmpdir), ignore_errors=True)

    def test_loads_catalog(self):
        msgs = self.mm._catalog.get("messages", {})
        self.assertGreaterEqual(len(msgs), 3)

    def test_get_hydrates_template(self):
        msg = self.mm.get("TEST_INFO", name="World")
        self.assertEqual(msg, "Hello World")

    def test_get_returns_none_for_unknown(self):
        self.assertIsNone(self.mm.get("UNKNOWN_ID"))

    def test_get_returns_none_when_verbosity_exceeded(self):
        self.mm.set_verbosity(1)
        msg = self.mm.get("TEST_WARN", detail="test")  # level 2
        self.assertIsNone(msg)

    def test_verbosity_clamp_upper(self):
        self.mm.set_verbosity(99)
        self.assertEqual(self.mm.verbosity, 3)

    def test_verbosity_clamp_lower(self):
        self.mm.set_verbosity(-1)
        self.assertEqual(self.mm.verbosity, 0)

    def test_get_with_missing_template_key(self):
        """Missing format key should not raise, returns template as-is."""
        msg = self.mm.get("TEST_INFO", nonexistent="x")
        self.assertEqual(msg, "Hello {name}")

    def test_show_without_logger_falls_back_to_print(self):
        """When logger is None, show() should print and not raise."""
        mm_no_logger = self.mm.__class__(config_dir=str(self._tmpdir), logger=None)
        # Should not raise, should print to stdout (capturable)
        import io
        import sys
        captured = io.StringIO()
        old = sys.stdout
        sys.stdout = captured
        try:
            mm_no_logger.show("TEST_INFO", name="test")
        finally:
            sys.stdout = old
        output = captured.getvalue().strip()
        self.assertEqual(output, "Hello test")

    def test_icon_prepended_when_present(self):
        """show() should prepend icon to text when msg_def has an icon key."""
        # We can't easily capture logger output, so check get() doesn't include icon
        # and then verify show() with our own logger mock.
        class MockLogger:
            def __init__(self):
                self.captured = []
            def status(self, text, context=None):
                self.captured.append(("status", text, context))
            def info(self, text, context=None):
                self.captured.append(("info", text, context))
            def warning(self, text, context=None):
                self.captured.append(("warning", text, context))
            def error(self, text, context=None):
                self.captured.append(("error", text, context))

        mock = MockLogger()
        mm_with_logger = self.mm.__class__(config_dir=str(self._tmpdir), logger=mock)
        mm_with_logger.show("TEST_ICON", n=42)
        self.assertEqual(len(mock.captured), 1)
        route, text, ctx = mock.captured[0]
        self.assertEqual(route, "status")
        self.assertEqual(text, "✓ Processed 42 items")
        self.assertEqual(ctx, "TEST_ICON")

    def test_show_without_icon_no_extra_space(self):
        """Messages without icon key should not get a leading space."""
        class MockLogger:
            def __init__(self):
                self.captured = []
            def info(self, text, context=None):
                self.captured.append(text)

        mock = MockLogger()
        mm = self.mm.__class__(config_dir=str(self._tmpdir), logger=mock)
        mm.show("TEST_INFO", name="noicon")
        self.assertEqual(mock.captured, ["Hello noicon"])


if __name__ == "__main__":
    unittest.main()
