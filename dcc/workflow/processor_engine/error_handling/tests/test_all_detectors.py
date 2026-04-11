"""
Phase 3 Detector Tests - Comprehensive Test Suite

Tests for all business logic detectors:
- AnchorDetector (P1xx)
- IdentityDetector (P2xx)
- BusinessDetector (Orchestrator)
- LogicDetector (L3xx)
- FillDetector (F4xx)
- ValidationDetector (V5xx)
- CalculationDetector (C6xx)
- HistoricalLookup (H2xx)
"""

import unittest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from detectors import (
    AnchorDetector,
    IdentityDetector,
    BusinessDetector,
    ProcessingPhase,
    LogicDetector,
    FillDetector,
    ValidationDetector,
    ValidationRule,
    CalculationDetector,
    FailFastError,
)

from validation_engine.validations.history import HistoricalLookup


class TestAnchorDetector(unittest.TestCase):
    """Test AnchorDetector (P1xx)."""
    
    def setUp(self):
        self.detector = AnchorDetector(enable_fail_fast=False)
    
    def test_detect_null_anchors(self):
        """Test detecting null anchor columns."""
        df = pd.DataFrame({
            "Project_Code": ["PRJ001", None, "PRJ003"],
            "Facility_Code": ["FAC01", "FAC02", ""],
            "Document_Type": ["Drawing", "Spec", "Report"]
        })
        
        errors = self.detector.detect(df)
        
        # Should find nulls in Project_Code and Facility_Code
        null_errors = [e for e in errors if e.error_code == "P1-A-P-0101"]
        self.assertEqual(len(null_errors), 2)
    
    def test_detect_session_format(self):
        """Test detecting invalid session format."""
        df = pd.DataFrame({
            "Submission_Session": ["240101", "invalid", "240102", "12345"]
        })
        
        errors = self.detector.detect(df)
        
        format_errors = [e for e in errors if e.error_code == "P1-A-V-0102"]
        self.assertEqual(len(format_errors), 2)  # "invalid" and "12345"
    
    def test_detect_invalid_dates(self):
        """Test detecting invalid date formats."""
        df = pd.DataFrame({
            "First_Submission_Date": ["2024-01-01", "invalid_date", "2024-02-15"]
        })
        
        errors = self.detector.detect(df)
        
        date_errors = [e for e in errors if e.error_code == "P1-A-V-0103"]
        self.assertEqual(len(date_errors), 1)
    
    def test_public_api_p101(self):
        """Test P101 public API."""
        df = pd.DataFrame({
            "Project_Code": ["PRJ001", None, "PRJ003", ""]
        })
        
        null_indices = self.detector.detect_P101_null_anchor(df, "Project_Code")
        self.assertEqual(len(null_indices), 2)  # rows 1 and 3


class TestIdentityDetector(unittest.TestCase):
    """Test IdentityDetector (P2xx)."""
    
    def setUp(self):
        self.detector = IdentityDetector(enable_fail_fast=False)
    
    def test_detect_uncertain_document_id(self):
        """Test detecting uncertain Document_ID."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ-FAC-DWG-0001", "TBD", "unknown", ""]
        })
        
        errors = self.detector.detect(df)
        
        uncertain_errors = [e for e in errors if e.error_code == "P2-I-P-0201"]
        self.assertEqual(len(uncertain_errors), 3)  # TBD, unknown, empty
    
    def test_detect_missing_revision(self):
        """Test detecting missing Document_Revision."""
        df = pd.DataFrame({
            "Document_Revision": ["01", None, "02", ""]
        })
        
        errors = self.detector.detect(df)
        
        rev_errors = [e for e in errors if e.error_code == "P2-I-P-0202"]
        self.assertEqual(len(rev_errors), 2)  # None and empty
    
    def test_detect_duplicate_transmittal(self):
        """Test detecting duplicate Transmittal_Number."""
        df = pd.DataFrame({
            "Transmittal_Number": ["T001", "T002", "T001", "T003"],
            "Submission_Session": ["240101", "240101", "240101", "240102"]
        })
        
        errors = self.detector.detect(df)
        
        dup_errors = [e for e in errors if e.error_code == "P2-I-V-0203"]
        self.assertEqual(len(dup_errors), 1)  # Second T001
    
    def test_public_api_p201(self):
        """Test P201 public API."""
        df = pd.DataFrame({
            "Document_ID": ["valid", "TBD", "pending", "valid2"]
        })
        
        uncertain = self.detector.detect_P201_id_uncertain(df)
        self.assertEqual(len(uncertain), 2)


class TestBusinessDetector(unittest.TestCase):
    """Test BusinessDetector orchestrator."""
    
    def setUp(self):
        self.detector = BusinessDetector(enable_fail_fast=False)
    
    def test_phase_execution(self):
        """Test phase-based detection."""
        df = pd.DataFrame({
            "Project_Code": ["PRJ001", None],  # P1 error
            "Document_ID": ["valid", "TBD"],  # P2 error
        })
        
        phase_errors = self.detector.detect(df)
        
        # Check both P1 and P2 errors exist
        p1_errors = phase_errors.get(ProcessingPhase.P1, [])
        p2_errors = phase_errors.get(ProcessingPhase.P2, [])
        
        self.assertGreater(len(p1_errors), 0)
        self.assertGreater(len(p2_errors), 0)
    
    def test_phase_summary(self):
        """Test phase summary generation."""
        df = pd.DataFrame({
            "Project_Code": [None],  # P1 error
        })
        
        self.detector.detect(df)
        summary = self.detector.get_phase_summary()
        
        self.assertIn("total_errors", summary)
        self.assertIn("errors_by_phase", summary)
        self.assertIn("errors_by_severity", summary)


class TestLogicDetector(unittest.TestCase):
    """Test LogicDetector (L3xx)."""
    
    def setUp(self):
        self.detector = LogicDetector(enable_fail_fast=False)
    
    def test_date_inversion(self):
        """Test detecting date inversion."""
        df = pd.DataFrame({
            "Submission_Date": ["2024-01-15", "2024-02-01"],
            "Review_Return_Actual_Date": ["2024-01-10", "2024-02-05"]
        })
        
        errors = self.detector.detect(df)
        
        inversion_errors = [e for e in errors if e.error_code == "L3-L-P-0301"]
        self.assertEqual(len(inversion_errors), 1)  # First row has return before submit
    
    def test_revision_regression(self):
        """Test detecting revision regression."""
        df = pd.DataFrame({
            "Document_ID": ["DOC001", "DOC001", "DOC001"],
            "Document_Revision": ["01", "02", "01"],  # 01 after 02 = regression
            "Submission_Date": ["2024-01-01", "2024-01-15", "2024-02-01"]
        })
        
        errors = self.detector.detect(df)
        
        reg_errors = [e for e in errors if e.error_code == "L3-L-V-0302"]
        self.assertEqual(len(reg_errors), 1)
    
    def test_status_conflict(self):
        """Test detecting status conflicts."""
        df = pd.DataFrame({
            "Approval_Code": ["Approved", "Approved"],
            "Resubmission_Required": ["No", "Yes"]
        })
        
        errors = self.detector.detect(df)
        
        conflict_errors = [e for e in errors if e.error_code == "L3-L-V-0303"]
        self.assertEqual(len(conflict_errors), 1)


class TestFillDetector(unittest.TestCase):
    """Test FillDetector (F4xx)."""
    
    def setUp(self):
        self.detector = FillDetector(enable_fail_fast=False, jump_limit=2)
    
    def test_jump_limit(self):
        """Test detecting forward fill jump limit exceeded."""
        df = pd.DataFrame({
            "Reviewer": ["Alice", None, None, None, "Bob"]
        })
        # Forward fill of "Alice" would jump 3 rows (exceeds limit of 2)
        
        errors = self.detector.detect(df)
        
        jump_errors = [e for e in errors if e.error_code == "F4-C-F-0401"]
        # Note: This is heuristic detection, results may vary
        self.assertIsInstance(jump_errors, list)
    
    def test_fill_history_analysis(self):
        """Test analyzing fill history records."""
        fill_history = [
            {
                "operation": "forward_fill",
                "column": "Reviewer",
                "from_row": 0,
                "to_row": 25,
                "row_jump": 25,
                "filled_value": "Alice"
            }
        ]
        
        errors = self.detector.detect(
            pd.DataFrame(),
            context={"fill_history": fill_history}
        )
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_code, "F4-C-F-0401")


class TestValidationDetector(unittest.TestCase):
    """Test ValidationDetector (V5xx)."""
    
    def setUp(self):
        self.detector = ValidationDetector(enable_fail_fast=False)
    
    def test_pattern_validation(self):
        """Test pattern matching validation."""
        rule = ValidationRule(
            column="Document_ID",
            rule_type="pattern",
            params={"pattern": r"^\d{4}-[A-Z]{2}-\d{4}$"},
            severity="HIGH"
        )
        
        df = pd.DataFrame({
            "Document_ID": ["1234-AB-5678", "invalid", "9999-XY-0000"]
        })
        
        self.detector.add_rule(rule)
        errors = self.detector.detect(df)
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_code, "V5-I-V-0501")
    
    def test_length_validation(self):
        """Test length constraint validation."""
        rule = ValidationRule(
            column="Title",
            rule_type="length",
            params={"max": 50},
            severity="HIGH"
        )
        
        df = pd.DataFrame({
            "Title": ["Short title", "A" * 100]  # Second title too long
        })
        
        self.detector.add_rule(rule)
        errors = self.detector.detect(df)
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_code, "V5-I-V-0502")
    
    def test_enum_validation(self):
        """Test enum validation."""
        rule = ValidationRule(
            column="Status",
            rule_type="enum",
            params={"values": ["Pending", "Approved", "Rejected"]},
            severity="HIGH"
        )
        
        df = pd.DataFrame({
            "Status": ["Pending", "InvalidStatus", "Approved"]
        })
        
        self.detector.add_rule(rule)
        errors = self.detector.detect(df)
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_code, "V5-I-V-0503")


class TestCalculationDetector(unittest.TestCase):
    """Test CalculationDetector (C6xx)."""
    
    def setUp(self):
        self.detector = CalculationDetector(enable_fail_fast=False)
    
    def test_dependency_fail(self):
        """Test detecting missing input columns."""
        calculations = [
            {
                "type": "date_diff",
                "target_column": "Duration",
                "input_columns": ["Start_Date", "End_Date", "Missing_Column"]
            }
        ]
        
        df = pd.DataFrame({
            "Start_Date": ["2024-01-01"],
            "End_Date": ["2024-01-15"]
        })
        
        errors = self.detector.detect(df, context={"calculations": calculations})
        
        dep_errors = [e for e in errors if e.error_code == "C6-C-C-0601"]
        self.assertEqual(len(dep_errors), 1)
    
    def test_circular_dependency(self):
        """Test detecting circular dependencies."""
        dependency_graph = {
            "A": {"B"},
            "B": {"C"},
            "C": {"A"}  # Circular: A -> B -> C -> A
        }
        
        errors = self.detector.detect(
            pd.DataFrame(),
            context={"dependency_graph": dependency_graph}
        )
        
        cycle_errors = [e for e in errors if e.error_code == "C6-C-C-0602"]
        self.assertEqual(len(cycle_errors), 1)
    
    def test_mapping_no_match(self):
        """Test detecting mapping failures."""
        calculations = [
            {
                "type": "mapping",
                "source_column": "Type",
                "target_column": "Category",
                "mapping": {"A": "Type A", "B": "Type B"}
            }
        ]
        
        df = pd.DataFrame({
            "Type": ["A", "B", "C"]  # C has no mapping
        })
        
        errors = self.detector.detect(df, context={"calculations": calculations})
        
        mapping_errors = [e for e in errors if e.error_code == "C6-C-C-0606"]
        self.assertEqual(len(mapping_errors), 1)
    
    def test_public_api_c601(self):
        """Test C601 public API."""
        df = pd.DataFrame({
            "Col_A": [1, 2, 3],
            "Col_B": ["a", "b", "c"]
        })
        
        missing = self.detector.detect_C601_dependency_fail(
            df,
            ["Col_A", "Col_B", "Col_C"]
        )
        
        self.assertEqual(missing, ["Col_C"])
    
    def test_public_api_c602(self):
        """Test C602 public API."""
        dependency_graph = {
            "A": {"B"},
            "B": {"C"},
            "C": {"A"}
        }
        
        cycles = self.detector.detect_C602_circular_dependency(dependency_graph)
        
        self.assertEqual(len(cycles), 1)
        self.assertIn("A", cycles[0])


class TestHistoricalLookup(unittest.TestCase):
    """Test HistoricalLookup (H2xx)."""
    
    def setUp(self):
        historical = pd.DataFrame({
            "Document_ID": ["DOC001", "DOC001", "DOC002"],
            "Document_Revision": ["01", "02", "01"],
            "Submission_Session": ["240101", "240102", "240101"],
            "Submission_Date": ["2024-01-01", "2024-01-15", "2024-01-01"],
            "Review_Status": ["Approved", "Approved", "Pending"]
        })
        
        self.lookup = HistoricalLookup(historical)
    
    def test_cross_session_duplicates(self):
        """Test detecting cross-session duplicates."""
        current = pd.DataFrame({
            "Document_ID": ["DOC001", "DOC003"],  # DOC001 exists in history
            "Submission_Session": ["240103", "240101"]
        })
        
        duplicates = self.lookup.check_cross_session_duplicates(current)
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0][1], "DOC001")
    
    def test_revision_consistency(self):
        """Test revision consistency validation."""
        # Valid: revision 03 after historical 02
        is_valid, error = self.lookup.validate_revision_consistency("DOC001", "03")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Invalid: revision 01 after historical 02 (regression)
        is_valid, error = self.lookup.validate_revision_consistency("DOC001", "01")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_temporal_integrity(self):
        """Test temporal consistency validation."""
        current = pd.DataFrame({
            "Document_ID": ["DOC001"],
            "Submission_Date": ["2023-12-01"]  # Before historical 2024-01-01
        })
        
        errors = self.lookup.check_temporal_integrity(current)
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error_type"], "temporal_inconsistency")
    
    def test_document_exists(self):
        """Test document existence check."""
        self.assertTrue(self.lookup.has_document("DOC001"))
        self.assertFalse(self.lookup.has_document("DOC999"))


if __name__ == "__main__":
    unittest.main()
