"""
Unit Tests for Phase 1 - Core JSON Loaders

Tests the following loaders:
- ErrorRegistry
- TaxonomyLoader
- StatusLoader
- AnatomyLoader
- RemediationLoader
- JSONSchemaValidator
- StructuredLogger
- Interceptor
"""

import unittest
import json
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.registry import ErrorRegistry
from core.taxonomy_loader import TaxonomyLoader
from core.status_loader import StatusLoader
from core.anatomy_loader import AnatomyLoader
from core.remediation_loader import RemediationLoader
from core.validator import JSONSchemaValidator
from core.logger import StructuredLogger
from core.interceptor import Interceptor, intercept


class TestErrorRegistry(unittest.TestCase):
    """Test ErrorRegistry loader."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - reset singletons."""
        # Reset singleton instances for testing
        ErrorRegistry._instance = None
        ErrorRegistry._registry_data = None
        ErrorRegistry._errors = {}
    
    def test_singleton_pattern(self):
        """Test that ErrorRegistry is a singleton."""
        reg1 = ErrorRegistry()
        reg2 = ErrorRegistry()
        self.assertIs(reg1, reg2)
    
    def test_load_registry(self):
        """Test loading the error registry."""
        registry = ErrorRegistry()
        self.assertIsNotNone(registry._registry_data)
        self.assertGreater(len(registry._errors), 0)
    
    def test_get_error(self):
        """Test getting a specific error."""
        registry = ErrorRegistry()
        error = registry.get_error("P-C-P-0101")
        self.assertIsNotNone(error)
        self.assertEqual(error["legacy_code"], "P101")
    
    def test_error_not_found(self):
        """Test getting non-existent error."""
        registry = ErrorRegistry()
        error = registry.get_error("X-X-X-9999")
        self.assertIsNone(error)
    
    def test_get_by_layer(self):
        """Test filtering by layer."""
        registry = ErrorRegistry()
        l3_errors = registry.get_by_layer("L3")
        self.assertGreater(len(l3_errors), 0)
        for error in l3_errors:
            self.assertEqual(error["layer"], "L3")
    
    def test_get_by_severity(self):
        """Test filtering by severity."""
        registry = ErrorRegistry()
        critical_errors = registry.get_by_severity("CRITICAL")
        self.assertGreater(len(critical_errors), 0)
        for error in critical_errors:
            self.assertEqual(error["severity"], "CRITICAL")
    
    def test_get_fail_fast_errors(self):
        """Test getting fail-fast errors."""
        registry = ErrorRegistry()
        ff_errors = registry.get_fail_fast_errors()
        self.assertIsInstance(ff_errors, list)
    
    def test_validate_code_format(self):
        """Test error code format validation."""
        registry = ErrorRegistry()
        self.assertTrue(registry.validate_code_format("P-C-P-0101"))
        self.assertFalse(registry.validate_code_format("invalid"))
        self.assertFalse(registry.validate_code_format("P-C-P-01"))  # Too short
    
    def test_get_statistics(self):
        """Test getting registry statistics."""
        registry = ErrorRegistry()
        stats = registry.get_statistics()
        self.assertIn("total_errors", stats)
        self.assertIn("by_layer", stats)
        self.assertIn("by_severity", stats)
        self.assertGreater(stats["total_errors"], 0)


class TestTaxonomyLoader(unittest.TestCase):
    """Test TaxonomyLoader."""
    
    @classmethod
    def setUpClass(cls):
        """Reset singleton."""
        TaxonomyLoader._instance = None
        TaxonomyLoader._taxonomy_data = None
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        loader1 = TaxonomyLoader()
        loader2 = TaxonomyLoader()
        self.assertIs(loader1, loader2)
    
    def test_get_engine(self):
        """Test getting engine definition."""
        loader = TaxonomyLoader()
        engine = loader.get_engine("P")
        self.assertIsNotNone(engine)
        self.assertEqual(engine["name"], "Processor")
    
    def test_get_module(self):
        """Test getting module definition."""
        loader = TaxonomyLoader()
        module = loader.get_module("C")
        self.assertIsNotNone(module)
        self.assertEqual(module["name"], "Core")
    
    def test_get_function(self):
        """Test getting function definition."""
        loader = TaxonomyLoader()
        function = loader.get_function("P")
        self.assertIsNotNone(function)
        self.assertEqual(function["name"], "Process")
    
    def test_get_family(self):
        """Test getting family definition."""
        loader = TaxonomyLoader()
        family = loader.get_family("1")
        self.assertIsNotNone(family)
        self.assertEqual(family["name"], "Anchor")
    
    def test_get_layer(self):
        """Test getting layer definition."""
        loader = TaxonomyLoader()
        layer = loader.get_layer("L3")
        self.assertIsNotNone(layer)
        self.assertEqual(layer["name"], "Business Logic Validation")
    
    def test_parse_error_code(self):
        """Test parsing error code."""
        loader = TaxonomyLoader()
        parsed = loader.parse_error_code("P-C-P-0101")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["engine"], "P")
        self.assertEqual(parsed["module"], "C")
        self.assertEqual(parsed["function"], "P")
        self.assertEqual(parsed["unique_id"], "0101")
    
    def test_build_error_code(self):
        """Test building error code from components."""
        loader = TaxonomyLoader()
        code = loader.build_error_code("P", "C", "P", "0101")
        self.assertEqual(code, "P-C-P-0101")
    
    def test_is_valid_error_code(self):
        """Test error code validation."""
        loader = TaxonomyLoader()
        self.assertTrue(loader.is_valid_error_code("P-C-P-0101"))
        self.assertFalse(loader.is_valid_error_code("X-Y-Z-9999"))  # Invalid components
    
    def test_get_statistics(self):
        """Test getting statistics."""
        loader = TaxonomyLoader()
        stats = loader.get_statistics()
        self.assertIn("engines", stats)
        self.assertIn("modules", stats)
        self.assertIn("functions", stats)
        self.assertGreater(stats["engines"], 0)


class TestStatusLoader(unittest.TestCase):
    """Test StatusLoader."""
    
    @classmethod
    def setUpClass(cls):
        """Reset singleton."""
        StatusLoader._instance = None
        StatusLoader._status_data = None
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        loader1 = StatusLoader()
        loader2 = StatusLoader()
        self.assertIs(loader1, loader2)
    
    def test_get_all_states(self):
        """Test getting all states."""
        loader = StatusLoader()
        states = loader.get_all_states()
        self.assertIn("OPEN", states)
        self.assertIn("RESOLVED", states)
        self.assertIn("ARCHIVED", states)
    
    def test_is_valid_state(self):
        """Test state validation."""
        loader = StatusLoader()
        self.assertTrue(loader.is_valid_state("OPEN"))
        self.assertTrue(loader.is_valid_state("SUPPRESSED"))
        self.assertFalse(loader.is_valid_state("INVALID"))
    
    def test_is_terminal_state(self):
        """Test terminal state check."""
        loader = StatusLoader()
        self.assertTrue(loader.is_terminal_state("ARCHIVED"))
        self.assertFalse(loader.is_terminal_state("OPEN"))
    
    def test_can_transition(self):
        """Test transition validation."""
        loader = StatusLoader()
        self.assertTrue(loader.can_transition("OPEN", "RESOLVED"))
        self.assertTrue(loader.can_transition("OPEN", "SUPPRESSED"))
        self.assertFalse(loader.can_transition("ARCHIVED", "OPEN"))  # Must reopen first
    
    def test_get_state_description(self):
        """Test getting state description."""
        loader = StatusLoader()
        desc = loader.get_state_description("OPEN")
        self.assertIsNotNone(desc)
        self.assertIn("label", desc)
        self.assertIn("color", desc)
    
    def test_get_workflow(self):
        """Test getting workflow."""
        loader = StatusLoader()
        workflow = loader.get_workflow("standard_resolution")
        self.assertIsNotNone(workflow)
        self.assertIn("path", workflow)


class TestAnatomyLoader(unittest.TestCase):
    """Test AnatomyLoader."""
    
    @classmethod
    def setUpClass(cls):
        """Reset singleton."""
        AnatomyLoader._instance = None
        AnatomyLoader._schema_data = None
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        loader1 = AnatomyLoader()
        loader2 = AnatomyLoader()
        self.assertIs(loader1, loader2)
    
    def test_get_valid_engine_codes(self):
        """Test getting valid engine codes."""
        loader = AnatomyLoader()
        codes = loader.get_valid_engine_codes()
        self.assertIn("P", codes)
        self.assertIn("M", codes)
    
    def test_get_valid_module_codes(self):
        """Test getting valid module codes."""
        loader = AnatomyLoader()
        codes = loader.get_valid_module_codes()
        self.assertIn("C", codes)
        self.assertIn("V", codes)
    
    def test_is_valid_error_code_format(self):
        """Test format validation."""
        loader = AnatomyLoader()
        self.assertTrue(loader.is_valid_error_code_format("P-C-P-0101"))
        self.assertFalse(loader.is_valid_error_code_format("P-C-P-01"))  # Too short
        self.assertFalse(loader.is_valid_error_code_format("invalid"))
    
    def test_parse_error_code(self):
        """Test parsing."""
        loader = AnatomyLoader()
        parsed = loader.parse_error_code("P-C-P-0101")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["engine_code"], "P")
        self.assertEqual(parsed["family_code"], "0")


class TestRemediationLoader(unittest.TestCase):
    """Test RemediationLoader."""
    
    @classmethod
    def setUpClass(cls):
        """Reset singleton."""
        RemediationLoader._instance = None
        RemediationLoader._remediation_data = None
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        loader1 = RemediationLoader()
        loader2 = RemediationLoader()
        self.assertIs(loader1, loader2)
    
    def test_get_type(self):
        """Test getting remediation type."""
        loader = RemediationLoader()
        r_type = loader.get_type("AUTO_FIX")
        self.assertIsNotNone(r_type)
        self.assertEqual(r_type["name"], "Auto Fix")
    
    def test_is_auto_eligible(self):
        """Test auto eligibility."""
        loader = RemediationLoader()
        self.assertTrue(loader.is_auto_eligible("AUTO_FIX"))
        self.assertFalse(loader.is_auto_eligible("MANUAL_FIX"))
    
    def test_requires_approval(self):
        """Test approval requirement."""
        loader = RemediationLoader()
        self.assertTrue(loader.requires_approval("SUPPRESS"))
        self.assertFalse(loader.requires_approval("AUTO_FIX"))
    
    def test_suggest_remediation_types(self):
        """Test remediation suggestion."""
        loader = RemediationLoader()
        suggestions = loader.suggest_remediation_types(
            severity="HIGH",
            layer="L3",
            family="Anchor"
        )
        self.assertIsInstance(suggestions, list)


class TestJSONSchemaValidator(unittest.TestCase):
    """Test JSONSchemaValidator."""
    
    def test_validate_error_code_structure(self):
        """Test structure validation."""
        validator = JSONSchemaValidator()
        error_data = {
            "layer": "L3",
            "severity": "CRITICAL",
            "taxonomy": {
                "engine": "Processor",
                "engine_code": "P",
                "module": "Core",
                "module_code": "C",
                "function": "Process",
                "function_code": "P",
                "family": "Anchor",
                "family_code": "1"
            },
            "message_key": "error.test",
            "action_key": "action.test"
        }
        self.assertTrue(validator.validate_error_code_structure("P-C-P-0101", error_data))
    
    def test_validate_json_file(self):
        """Test JSON file validation."""
        validator = JSONSchemaValidator()
        # Test with a known existing file
        config_path = Path(__file__).parent.parent / "config" / "error_codes.json"
        self.assertTrue(validator.validate_json_file(config_path))
    
    def test_validate_json_file_not_found(self):
        """Test validation of non-existent file."""
        validator = JSONSchemaValidator()
        self.assertFalse(validator.validate_json_file("/nonexistent/path.json"))


class TestStructuredLogger(unittest.TestCase):
    """Test StructuredLogger."""
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        logger1 = StructuredLogger()
        logger2 = StructuredLogger()
        self.assertIs(logger1, logger2)
    
    def test_set_context(self):
        """Test context setting."""
        logger = StructuredLogger()
        logger.set_context(project_code="TEST001")
        self.assertEqual(logger._context.get("project_code"), "TEST001")
        logger.clear_context()


class TestInterceptor(unittest.TestCase):
    """Test Interceptor framework."""
    
    def test_singleton_pattern(self):
        """Test singleton pattern."""
        int1 = Interceptor()
        int2 = Interceptor()
        self.assertIs(int1, int2)
    
    def test_intercept_decorator(self):
        """Test intercept decorator."""
        interceptor = Interceptor()
        
        @interceptor.intercept(layer="L3", phase="P1")
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        self.assertEqual(result, 10)
    
    def test_handler_registration(self):
        """Test handler registration."""
        interceptor = Interceptor()
        interceptor.clear_handlers()
        
        @interceptor.before
        def before_handler(ctx):
            pass
        
        counts = interceptor.get_handler_count()
        self.assertEqual(counts["before"], 1)
        
        interceptor.clear_handlers()


if __name__ == "__main__":
    unittest.main()
