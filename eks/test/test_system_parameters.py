"""Tests for T1.97/I088 system parameter centralization.

Revision: 0.1
Date: 2026-07-11
Author: Codex
Summary: Cover shared system parameter normalization and EKS config lookup.
"""

import unittest
from pathlib import Path

from common.library.config import get_system_param, normalize_system_parameters
from eks.engine.core.config_registry import ConfigRegistry
from eks.engine.core.schema_loader import SchemaLoader


class TestSystemParameters(unittest.TestCase):
    """Verify universal system parameter lookup shapes."""

    def test_normalize_flat_full_config(self):
        """Full config with flat system_parameters normalizes to key/value pairs."""
        config = {"system_parameters": {"retry_count": 4, "debug_mode": True}}

        params = normalize_system_parameters(config)

        self.assertEqual(params["retry_count"], 4)
        self.assertTrue(params["debug_mode"])

    def test_normalize_direct_flat_object(self):
        """Direct flat object is accepted for simple callers."""
        params = normalize_system_parameters({"api_timeout": 90})

        self.assertEqual(params["api_timeout"], 90)

    def test_normalize_array_entries(self):
        """DCC-style array entries support value and default_value fields."""
        config = {
            "system_parameters": [
                {"key": "fail_fast", "type": "boolean", "value": False},
                {"key": "log_level", "type": "integer", "default_value": 2},
            ]
        }

        params = normalize_system_parameters(config)

        self.assertFalse(params["fail_fast"])
        self.assertEqual(params["log_level"], 2)

    def test_normalize_empty_and_malformed(self):
        """Missing or malformed system parameter payloads produce an empty mapping."""
        self.assertEqual(normalize_system_parameters({}), {})
        self.assertEqual(normalize_system_parameters({"system_parameters": "bad"}), {})
        self.assertEqual(normalize_system_parameters({"system_parameters": [{"type": "integer"}]}), {})

    def test_get_system_param_default(self):
        """Lookup returns caller default when key is absent."""
        self.assertEqual(get_system_param({"system_parameters": {}}, "missing", "fallback"), "fallback")

    def test_config_registry_reads_real_eks_system_parameters(self):
        """Real EKS config exposes schema-driven runtime knobs."""
        ConfigRegistry._instance = None
        registry = ConfigRegistry(Path("eks/config"))

        self.assertEqual(registry.get_system_param("retry_count"), 3)
        self.assertEqual(registry.get_system_param("api_timeout"), 120)
        self.assertFalse(registry.get_system_param("debug_mode"))

    def test_schema_loader_validates_system_parameters(self):
        """Updated config validates through the existing schema loader."""
        loader = SchemaLoader(Path("eks/config"))
        config = loader.load_all()

        self.assertIn("system_parameters", config)
        self.assertEqual(config["system_parameters"]["db_timeout"], 30)
        self.assertNotIn("timeout", config.get("registry", {}))


if __name__ == "__main__":
    unittest.main()
