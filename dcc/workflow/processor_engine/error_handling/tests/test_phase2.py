"""
Phase 2 Integration Tests

Tests for:
- Template Guard (L0)
- Exception handling (base.py, handler.py)
- Base detector
- Input detector (L1)
- Schema detector (L2)
- Fail-fast behavior
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from exceptions import (
    DCCError,
    DCCInputError,
    DCCSchemaError,
    ExceptionHandler,
    get_handler,
    handle_exceptions,
)

from detectors import (
    BaseDetector,
    InputDetector,
    SchemaDetector,
    FailFastError,
    DetectionResult,
)

from validation_engine.preflight.template import TemplateGuard, TemplateValidationResult


class TestTemplateGuard(unittest.TestCase):
    """Test TemplateGuard (L0)."""
    
    def setUp(self):
        """Create test files."""
        self.guard = TemplateGuard(expected_schema_version="1.0.0")
    
    def test_verify_schema_version_match(self):
        """Test version verification - exact match."""
        is_valid, error = self.guard.verify_schema_version("1.0.0", "1.0.0")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_verify_schema_version_minor_ahead(self):
        """Test version verification - minor version ahead."""
        is_valid, error = self.guard.verify_schema_version("1.0.0", "1.1.0")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_verify_schema_version_major_mismatch(self):
        """Test version verification - major version mismatch (fail-fast)."""
        is_valid, error = self.guard.verify_schema_version("1.0.0", "2.0.0")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertTrue(error.get("fail_fast", False))
        self.assertEqual(error.get("error_code"), "S0-I-F-0801")
    
    def test_calculate_signature(self):
        """Test signature calculation."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"test": "data"}')
            temp_path = f.name
        
        try:
            signature = self.guard.calculate_signature(temp_path)
            self.assertEqual(len(signature), 64)  # SHA-256 hex = 64 chars
            self.assertTrue(all(c in '0123456789abcdef' for c in signature))
        finally:
            os.unlink(temp_path)
    
    def test_validate_signature_missing_file(self):
        """Test signature validation - file not found."""
        is_valid, error = self.guard.validate_signature("/nonexistent/file.json")
        self.assertFalse(is_valid)
        self.assertEqual(error.get("error_code"), "S0-I-F-0802")
    
    def test_check_compatibility_missing_fields(self):
        """Test config compatibility check."""
        config = {}  # Missing required fields
        is_valid, errors = self.guard.check_compatibility(config)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)  # schema_version, template_name, columns
    
    def test_check_compatibility_valid(self):
        """Test config compatibility - valid config."""
        config = {
            "schema_version": "1.0.0",
            "template_name": "test",
            "columns": ["col1", "col2"]
        }
        is_valid, errors = self.guard.check_compatibility(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestDCCError(unittest.TestCase):
    """Test DCCError exception classes."""
    
    def test_dcc_error_creation(self):
        """Test basic DCCError creation."""
        error = DCCError(
            error_code="P-C-P-0101",
            message="Test error",
            row=5,
            column="Project_Code",
            severity="CRITICAL"
        )
        self.assertEqual(error.error_code, "P-C-P-0101")
        self.assertEqual(error.row, 5)
        self.assertEqual(error.column, "Project_Code")
        self.assertTrue(error.is_fail_fast())  # CRITICAL = fail-fast
    
    def test_dcc_error_to_dict(self):
        """Test error serialization to dict."""
        error = DCCError(
            error_code="P-C-P-0101",
            message="Test error",
            layer="L3",
            context={"extra": "info"}
        )
        d = error.to_dict()
        self.assertEqual(d["error_code"], "P-C-P-0101")
        self.assertEqual(d["layer"], "L3")
        self.assertIn("context", d)
    
    def test_dcc_error_to_json(self):
        """Test error serialization to JSON."""
        error = DCCError(
            error_code="P-C-P-0101",
            message="Test error"
        )
        json_str = error.to_json()
        self.assertIn("P-C-P-0101", json_str)
        self.assertIn("Test error", json_str)
    
    def test_dcc_error_str(self):
        """Test string representation."""
        error = DCCError(
            error_code="P-C-P-0101",
            message="Test",
            row=5,
            column="Col"
        )
        s = str(error)
        self.assertIn("P-C-P-0101", s)
        self.assertIn("Row: 5", s)
    
    def test_dcc_input_error(self):
        """Test DCCInputError."""
        error = DCCInputError("S1-I-F-0804", "File not found")
        self.assertEqual(error.layer, "L1")
        self.assertEqual(error.severity, "CRITICAL")
    
    def test_dcc_schema_error(self):
        """Test DCCSchemaError."""
        error = DCCSchemaError("S0-I-F-0801", "Version mismatch")
        self.assertEqual(error.layer, "L0")
        self.assertTrue(error.is_fail_fast())


class TestExceptionHandler(unittest.TestCase):
    """Test ExceptionHandler."""
    
    def setUp(self):
        """Reset handler."""
        self.handler = ExceptionHandler()
        self.handler.clear_errors()
    
    def test_singleton(self):
        """Test singleton pattern."""
        h1 = ExceptionHandler()
        h2 = ExceptionHandler()
        self.assertIs(h1, h2)
    
    def test_map_exception_to_error_code(self):
        """Test exception to error code mapping."""
        handler = ExceptionHandler()
        
        code = handler.map_exception_to_error_code(FileNotFoundError())
        self.assertEqual(code, "S0-I-F-0804")
        
        code = handler.map_exception_to_error_code(ValueError())
        self.assertEqual(code, "P-C-P-0301")
    
    def test_handle_exception_converts_to_dcc(self):
        """Test exception conversion."""
        handler = ExceptionHandler()
        original = FileNotFoundError("test.txt")
        
        dcc_error = handler.handle_exception(original, row=5)
        
        self.assertIsInstance(dcc_error, DCCError)
        self.assertEqual(dcc_error.error_code, "S0-I-F-0804")
        self.assertEqual(dcc_error.row, 5)
    
    def test_handle_decorator(self):
        """Test exception handling decorator."""
        handler = ExceptionHandler()
        handler.enable_fail_fast(False)
        
        @handler.handle(context={"phase": "P1"})
        def failing_function():
            raise ValueError("Something failed")
        
        try:
            failing_function()
            self.fail("Should have raised DCCError")
        except DCCError as e:
            self.assertEqual(e.context.get("phase"), "P1")


class TestBaseDetector(unittest.TestCase):
    """Test BaseDetector."""
    
    class TestDetector(BaseDetector):
        """Concrete detector for testing."""
        def detect(self, data, context=None):
            return self.get_errors()
    
    def test_detector_context(self):
        """Test context management."""
        detector = self.TestDetector(layer="L3")
        detector.set_context(project_code="TEST001")
        self.assertEqual(detector._context.get("project_code"), "TEST001")
    
    def test_detect_error_no_fail_fast(self):
        """Test error detection without fail-fast."""
        detector = self.TestDetector(layer="L3", enable_fail_fast=False)
        
        result = detector.detect_error(
            error_code="P-C-P-0101",
            message="Test error",
            row=5,
            severity="HIGH"
        )
        
        self.assertIsInstance(result, DetectionResult)
        self.assertEqual(detector.get_error_count(), 1)
        self.assertFalse(detector.has_fail_fast_errors())
    
    def test_detect_error_with_fail_fast(self):
        """Test error detection with fail-fast."""
        detector = self.TestDetector(layer="L3", enable_fail_fast=True)
        
        with self.assertRaises(FailFastError):
            detector.detect_error(
                error_code="S0-I-F-0801",
                message="Critical error",
                fail_fast=True,
                severity="CRITICAL"
            )
    
    def test_get_errors_by_severity(self):
        """Test filtering by severity."""
        detector = self.TestDetector(layer="L3", enable_fail_fast=False)
        
        detector.detect_error("P-C-P-0101", "High", severity="HIGH")
        detector.detect_error("P-C-P-0101", "High 2", severity="HIGH")
        detector.detect_error("P-C-P-0201", "Medium", severity="MEDIUM")
        
        high_errors = detector.get_errors_by_severity("HIGH")
        self.assertEqual(len(high_errors), 2)


class TestInputDetector(unittest.TestCase):
    """Test InputDetector (L1)."""
    
    def setUp(self):
        """Create test files."""
        self.detector = InputDetector(
            required_columns=["Project_Code", "Document_Type"],
            enable_fail_fast=False
        )
    
    def test_detect_missing_file(self):
        """Test detecting missing file."""
        errors = self.detector.detect("/nonexistent/file.csv")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_code, "S1-I-F-0804")
    
    def test_detect_invalid_format(self):
        """Test detecting invalid file format."""
        # Create temp file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            errors = self.detector.detect(temp_path)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].error_code, "S1-I-F-0805")
        finally:
            os.unlink(temp_path)
    
    def test_detect_missing_columns(self):
        """Test detecting missing columns."""
        # Create CSV with missing required columns
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Other_Column\nvalue1\n")
            temp_path = f.name
        
        try:
            errors = self.detector.detect(temp_path)
            col_errors = [e for e in errors if e.error_code == "S1-I-V-0502"]
            self.assertEqual(len(col_errors), 1)
            self.assertIn("Project_Code", col_errors[0].message)
        finally:
            os.unlink(temp_path)
    
    def test_detect_valid_csv(self):
        """Test detecting no errors in valid CSV."""
        # Create valid CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Project_Code,Document_Type\nPRJ001,Drawing\n")
            temp_path = f.name
        
        try:
            errors = self.detector.detect(temp_path)
            # Should have no column errors
            col_errors = [e for e in errors if e.error_code == "S1-I-V-0502"]
            self.assertEqual(len(col_errors), 0)
        finally:
            os.unlink(temp_path)


class TestSchemaDetector(unittest.TestCase):
    """Test SchemaDetector (L2)."""
    
    def setUp(self):
        """Set up detector."""
        self.detector = SchemaDetector(enable_fail_fast=False)
    
    def test_register_pattern(self):
        """Test pattern registration."""
        self.detector.register_pattern(
            "Document_ID",
            r"^\d{4}-[A-Z]{2}-\d{4}$",
            "4-digit prefix, 2-letter type, 4-digit sequence"
        )
        
        self.assertIn("Document_ID", self.detector._patterns)
    
    def test_validate_length_max(self):
        """Test max length validation."""
        is_valid = self.detector.validate_length(
            value="a" * 100,
            column="Title",
            row_index=5,
            max_length=50
        )
        self.assertFalse(is_valid)
        self.assertEqual(self.detector.get_error_count(), 1)
        self.assertEqual(self.detector.get_errors()[0].error_code, "V5-I-V-0502")
    
    def test_validate_length_min(self):
        """Test min length validation."""
        is_valid = self.detector.validate_length(
            value="ab",
            column="Title",
            row_index=5,
            min_length=5
        )
        self.assertFalse(is_valid)
    
    def test_validate_enum_valid(self):
        """Test enum validation - valid value."""
        is_valid = self.detector.validate_enum(
            value="Drawing",
            column="Type",
            row_index=5,
            allowed_values=["Drawing", "Spec", "Report"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(self.detector.get_error_count(), 0)
    
    def test_validate_enum_invalid(self):
        """Test enum validation - invalid value."""
        is_valid = self.detector.validate_enum(
            value="Invalid",
            column="Type",
            row_index=5,
            allowed_values=["Drawing", "Spec", "Report"]
        )
        self.assertFalse(is_valid)
        self.assertEqual(self.detector.get_error_count(), 1)
        self.assertEqual(self.detector.get_errors()[0].error_code, "V5-I-V-0503")
    
    def test_validate_type_mismatch(self):
        """Test type validation - mismatch."""
        is_valid = self.detector.validate_type(
            value="not an int",
            column="Count",
            row_index=5,
            expected_type=int
        )
        self.assertFalse(is_valid)
        self.assertEqual(self.detector.get_error_count(), 1)
        self.assertEqual(self.detector.get_errors()[0].error_code, "V5-I-V-0504")


class TestFailFastBehavior(unittest.TestCase):
    """Test fail-fast behavior across components."""
    
    class FailingDetector(BaseDetector):
        def detect(self, data, context=None):
            # Trigger fail-fast
            self.detect_error(
                error_code="S0-I-F-0801",
                message="Critical",
                fail_fast=True,
                severity="CRITICAL"
            )
            return []
    
    def test_fail_fast_raises_exception(self):
        """Test that fail-fast raises FailFastError."""
        detector = self.FailingDetector(layer="L0", enable_fail_fast=True)
        
        with self.assertRaises(FailFastError) as context:
            detector.detect(None)
        
        self.assertEqual(context.exception.result.error_code, "S0-I-F-0801")
    
    def test_fail_fast_disabled(self):
        """Test that fail-fast can be disabled."""
        detector = self.FailingDetector(layer="L0", enable_fail_fast=False)
        
        # Should not raise, error should be stored
        detector.detect(None)
        errors = detector.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].fail_fast)


if __name__ == "__main__":
    unittest.main()
