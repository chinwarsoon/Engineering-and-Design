"""
Tests for initiation_engine paths utilities.
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.utils.paths import normalize_path, default_base_path, get_schema_path


class TestNormalizePath(unittest.TestCase):
    """Test normalize_path function."""

    def test_normalizes_string_path(self):
        """Test that string path is converted to absolute Path."""
        result = normalize_path(".")
        self.assertIsInstance(result, Path)
        self.assertTrue(result.is_absolute())

    def test_normalizes_path_object(self):
        """Test that Path object is converted to absolute."""
        input_path = Path("some/relative/path")
        result = normalize_path(input_path)
        self.assertTrue(result.is_absolute())

    def test_preserves_absolute_path(self):
        """Test that absolute path remains unchanged."""
        absolute = Path("/absolute/path")
        result = normalize_path(absolute)
        self.assertEqual(str(result), str(absolute.absolute()))


class TestDefaultBasePath(unittest.TestCase):
    """Test default_base_path function."""

    def test_returns_path_object(self):
        """Test that function returns a Path object."""
        result = default_base_path()
        self.assertIsInstance(result, Path)

    def test_returns_absolute_path(self):
        """Test that returned path is absolute."""
        result = default_base_path()
        self.assertTrue(result.is_absolute())

    def test_returns_existing_path(self):
        """Test that returned path exists."""
        result = default_base_path()
        self.assertTrue(result.exists())


class TestGetSchemaPath(unittest.TestCase):
    """Test get_schema_path function."""

    def test_returns_path_object(self):
        """Test that function returns a Path object."""
        base = Path("/some/base")
        result = get_schema_path(base)
        self.assertIsInstance(result, Path)

    def test_constructs_correct_path(self):
        """Test that path is constructed correctly."""
        base = Path("/project")
        result = get_schema_path(base)
        expected = Path("/project/config/schemas/project_setup.json")
        self.assertEqual(result, expected)

    def test_uses_config_schemas_subdir(self):
        """Test that path includes config/schemas subdirectory."""
        base = Path("/home/user/dcc")
        result = get_schema_path(base)
        self.assertIn("config/schemas", str(result))
        self.assertIn("project_setup.json", str(result))


class TestPathIntegration(unittest.TestCase):
    """Integration tests for paths module."""

    def test_normalize_then_get_schema(self):
        """Test chaining normalize_path with get_schema_path."""
        raw_path = "."
        normalized = normalize_path(raw_path)
        schema_path = get_schema_path(normalized)
        self.assertTrue(schema_path.is_absolute())

    def test_default_base_with_schema(self):
        """Test using default_base_path with get_schema_path."""
        base = default_base_path()
        schema_path = get_schema_path(base)
        # Should be a valid-looking path even if file doesn't exist
        self.assertIn("config", str(schema_path))
        self.assertIn("schemas", str(schema_path))
        self.assertIn("project_setup.json", str(schema_path))


if __name__ == "__main__":
    unittest.main()
