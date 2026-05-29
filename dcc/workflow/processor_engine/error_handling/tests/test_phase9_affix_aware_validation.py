#!/usr/bin/env python3
"""
Phase 9 Affix-Aware Validation Test
====================================

Tests the affix-aware composite validation logic for Document_ID segments.
This validates the Phase 9 implementation that distinguishes between:
- P2-I-V-0204-W: Affix-induced discrepancies (WARNING, -5 health score)
- P2-I-V-0204-C: Genuine segment mismatches (HIGH, -15 health score)

Test Cases:
1. Exact Match - ID segments match source columns perfectly
2. Affix Mismatch - ID segment + affix == source column (e.g., 5101 vs 5101_ST609)
3. Genuine Mismatch - Segment and column are totally different
"""

import sys
import pandas as pd
import unittest
from pathlib import Path

# Add workflow path for imports
workflow_root = Path(__file__).parent.parent.parent.parent.parent  # dcc folder
sys.path.insert(0, str(workflow_root / "workflow"))
sys.path.insert(0, str(workflow_root / "workflow" / "processor_engine" / "error_handling"))

from detectors.row_validator import RowValidator


class TestPhase9AffixAwareValidation(unittest.TestCase):
    """Test Phase 9 affix-aware composite validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = RowValidator(enable_fail_fast=False)
        # Mock schema data context with full error catalog entries
        self.context = {
            "schema_data": {
                "columns": {
                    "Document_ID": {
                        "calculation": {
                            "source_columns": [
                                "Project_Code",
                                "Facility_Code",
                                "Document_Type",
                                "Discipline",
                                "Document_Sequence_Number"
                            ]
                        }
                    }
                }
            },
            "error_catalog": {
                "P2-I-V-0204-W": {
                    "code": "P2-I-V-0204-W",
                    "name": "DOCUMENT_ID_AFFIX_MISMATCH",
                    "message": "Document_ID segment contains affix from source column",
                    "severity": "WARNING",
                    "health_score_impact": -5
                },
                "P2-I-V-0204-C": {
                    "code": "P2-I-V-0204-C",
                    "name": "DOCUMENT_ID_SEGMENT_MISMATCH",
                    "message": "Document_ID composite segment mismatch",
                    "severity": "HIGH",
                    "health_score_impact": -15
                }
            }
        }
    
    def test_exact_match(self):
        """Test Case 1: ID segments match source columns perfectly."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101"],
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should have no P2-I-V-0204 errors
        doc_id_errors = [e for e in errors if e.error_code.startswith("P2-I-V-0204")]
        self.assertEqual(len(doc_id_errors), 0, 
                        "Exact match should not raise any P2-I-V-0204 errors")
    
    def test_affix_mismatch_warning(self):
        """Test Case 2: ID segment + affix == source column (should raise WARNING)."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101_ST609"],  # Affix in source column
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should raise P2-I-V-0204-W (WARNING) for affix mismatch
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        self.assertEqual(len(affix_warnings), 1, 
                        "Affix mismatch should raise P2-I-V-0204-W warning")
        
        # Should NOT raise P2-I-V-0204-C (genuine mismatch error)
        genuine_errors = [e for e in errors if e.error_code == "P2-I-V-0204-C"]
        self.assertEqual(len(genuine_errors), 0, 
                        "Affix mismatch should not raise P2-I-V-0204-C error")
        
        # Verify severity is WARNING
        self.assertEqual(affix_warnings[0].severity, "WARNING")
    
    def test_genuine_mismatch_error(self):
        """Test Case 3: Segment and column are totally different (should raise ERROR)."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ999"],  # Totally different
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101"],
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should raise P2-I-V-0204-C (genuine mismatch error)
        genuine_errors = [e for e in errors if e.error_code == "P2-I-V-0204-C"]
        self.assertEqual(len(genuine_errors), 1, 
                        "Genuine mismatch should raise P2-I-V-0204-C error")
        
        # Should NOT raise P2-I-V-0204-W (affix warning)
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        self.assertEqual(len(affix_warnings), 0, 
                        "Genuine mismatch should not raise P2-I-V-0204-W warning")
        
        # Verify severity is HIGH
        self.assertEqual(genuine_errors[0].severity, "HIGH")
    
    def test_multiple_affixes(self):
        """Test multiple columns with affixes."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": ["FAC01_ST609"],  # Affix
            "Document_Type": ["DWG"],
            "Discipline": ["ARC_REPLY"],  # Affix
            "Document_Sequence_Number": ["5101"],
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should raise P2-I-V-0204-W for affix mismatches
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        self.assertGreater(len(affix_warnings), 0, 
                          "Multiple affixes should raise P2-I-V-0204-W warnings")
        
        # Verify warnings contain context about which columns have affixes
        for warning in affix_warnings:
            self.assertIn("warnings", warning.context)
    
    def test_mixed_affix_and_genuine(self):
        """Test mix of affix and genuine mismatches."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ999"],  # Genuine mismatch
            "Facility_Code": ["FAC01_ST609"],  # Affix
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101"],
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should raise both warning and error
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        genuine_errors = [e for e in errors if e.error_code == "P2-I-V-0204-C"]
        
        self.assertEqual(len(affix_warnings), 1, "Should raise affix warning")
        self.assertEqual(len(genuine_errors), 1, "Should raise genuine mismatch error")
    
    def test_health_score_impact(self):
        """Test health score impact difference between warning and error."""
        df_warning = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101_ST609"],  # Affix
        })
        
        df_error = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ999"],  # Genuine mismatch
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101"],
        })
        
        errors_warning = self.validator.detect(df_warning, context=self.context)
        errors_error = self.validator.detect(df_error, context=self.context)
        
        # Get error weights
        weights = self.validator.compute_row_health_weights()
        
        # Verify warning has lower impact than error
        self.assertEqual(weights.get("P2-I-V-0204-W", 0), 5, 
                        "Warning should have -5 health score impact")
        self.assertEqual(weights.get("P2-I-V-0204-C", 0), 15, 
                        "Error should have -15 health score impact")
    
    def test_null_handling(self):
        """Test that null segments are handled correctly."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-5101"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": [None],  # Null
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["5101"],
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Null segments should not trigger affix-aware logic
        # They should be caught by other validation (anchor null check)
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        genuine_errors = [e for e in errors if e.error_code == "P2-I-V-0204-C"]
        
        # Should not raise affix-aware errors for null segments
        self.assertEqual(len(affix_warnings), 0)
        self.assertEqual(len(genuine_errors), 0)
    
    def test_zero_padding_difference(self):
        """Test zero-padding difference (e.g., 1247 vs 01247)."""
        df = pd.DataFrame({
            "Document_ID": ["PRJ001-FAC01-DWG-ARC-01247"],
            "Project_Code": ["PRJ001"],
            "Facility_Code": ["FAC01"],
            "Document_Type": ["DWG"],
            "Discipline": ["ARC"],
            "Document_Sequence_Number": ["1247"],  # Unpadded vs Document_ID has 01247
        })
        
        errors = self.validator.detect(df, context=self.context)
        
        # Should raise P2-I-V-0204-W (WARNING) for zero-padding difference
        affix_warnings = [e for e in errors if e.error_code == "P2-I-V-0204-W"]
        self.assertEqual(len(affix_warnings), 1, 
                        "Zero-padding difference should raise P2-I-V-0204-W warning")
        
        # Should NOT raise P2-I-V-0204-C (genuine mismatch error)
        genuine_errors = [e for e in errors if e.error_code == "P2-I-V-0204-C"]
        self.assertEqual(len(genuine_errors), 0, 
                        "Zero-padding difference should not raise P2-I-V-0204-C error")


def main():
    """Run Phase 9 affix-aware validation tests."""
    print("=" * 80)
    print("🧪 PHASE 9 AFFIX-AWARE VALIDATION TEST")
    print("=" * 80)
    print("\nTesting affix-aware composite validation for Document_ID segments")
    print("Validates Phase 9 implementation:")
    print("- P2-I-V-0204-W: Affix-induced discrepancies (WARNING, -5 health score)")
    print("- P2-I-V-0204-C: Genuine segment mismatches (HIGH, -15 health score)")
    print("=" * 80)
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase9AffixAwareValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✅ ALL PHASE 9 TESTS PASSED")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    else:
        print("❌ PHASE 9 TESTS FAILED")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("=" * 80)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
