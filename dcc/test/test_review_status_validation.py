
import pandas as pd
import unittest
import logging
import sys
from pathlib import Path

# Add workflow to path
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflow"
if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

from universal_document_processor import UniversalDocumentProcessor

class TestReviewStatusValidation(unittest.TestCase):
    def setUp(self):
        self.processor = UniversalDocumentProcessor()
        self.processor.schema_file = str(ROOT / "config" / "schemas" / "dcc_register_enhanced.json")
        self.processor.load_schema()
        
    def test_invalid_review_status(self):
        # Data where Review_Status is NOT in approval_code_schema statuses
        # Valid statuses are e.g. "Approved", "Awaiting S.O.'s response"
        # "Pending" should now be invalid because it is an alias, not the canonical status field
        data = {
            'Submission_Session': ['000001'],
            'Submission_Session_Revision': ['01'],
            'Submission_Date': ['2026-04-01'],
            'Project_Code': ['131242'],
            'Facility_Code': ['F1'],
            'Document_Type': ['T1'],
            'Discipline': ['D1'],
            'Document_Sequence_Number': ['0001'],
            'Document_Revision': ['0'],
            'Document_Title': ['Title 1'],
            'Submission_Session_Subject': ['Subject 1'],
            'Department': ['Project'],
            'Review_Status': ['Pending'], # This should fail as it's not the canonical status
            'Review_Comments': ['No comments'],
            'Submission_Closed': ['NO'],
            'Resubmission_Required': ['YES'],
            'Notes': ['']
        }
        df = pd.DataFrame(data)
        
        with self.assertLogs('universal_document_processor', level='WARNING') as cm:
            result_df = self.processor.process_data(df)
            
        found = False
        for log in cm.output:
            if "Schema reference validation failed for Review_Status" in log:
                found = True
                break
        self.assertTrue(found, "Should have logged a schema reference validation warning for Review_Status")
        self.assertIn("Review_Status not in approval_code_schema", result_df.loc[0, 'Validation_Errors'])

    def test_valid_review_status(self):
        # Data where Review_Status IS the canonical status "Awaiting S.O.'s response"
        data = {
            'Submission_Session': ['000001'],
            'Submission_Session_Revision': ['01'],
            'Submission_Date': ['2026-04-01'],
            'Project_Code': ['131242'],
            'Facility_Code': ['F1'],
            'Document_Type': ['T1'],
            'Discipline': ['D1'],
            'Document_Sequence_Number': ['0001'],
            'Document_Revision': ['0'],
            'Document_Title': ['Title 1'],
            'Submission_Session_Subject': ['Subject 1'],
            'Department': ['Project'],
            'Review_Status': ["Awaiting S.O.'s response"],
            'Review_Comments': ['No comments'],
            'Submission_Closed': ['NO'],
            'Resubmission_Required': ['YES'],
            'Notes': ['']
        }
        df = pd.DataFrame(data)
        
        # Should not have any Review_Status validation error
        result_df = self.processor.process_data(df)
        val_errors = result_df.loc[0, 'Validation_Errors']
        self.assertNotIn("Review_Status not in approval_code_schema", val_errors)

if __name__ == "__main__":
    unittest.main()
