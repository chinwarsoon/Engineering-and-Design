
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

class TestDocumentIDStartsWithValidation(unittest.TestCase):
    def setUp(self):
        self.processor = UniversalDocumentProcessor()
        self.processor.schema_file = str(ROOT / "config" / "schemas" / "dcc_register_enhanced.json")
        self.processor.load_schema()
        
    def test_invalid_document_id_prefix(self):
        # Data where Document_ID does NOT start with a valid project code (valid is 131242)
        data = {
            'Submission_Session': ['000001'],
            'Submission_Session_Revision': ['01'],
            'Submission_Date': ['2026-04-01'],
            'Document_ID': ['999999-F1-T1-0001'], # 999999 is not in project_schema
            'Project_Code': ['131242'],
            'Facility_Code': ['F1'],
            'Document_Type': ['T1'],
            'Discipline': ['D1'],
            'Document_Sequence_Number': ['0001'],
            'Document_Revision': ['0'],
            'Document_Title': ['Title 1'],
            'Submission_Session_Subject': ['Subject 1'],
            'Department': ['Dept 1'],
            'Review_Status': ['Pending'],
            'Review_Comments': ['No comments'],
            'Submission_Closed': ['NO'],
            'Resubmission_Required': ['YES'],
            'Notes': ['']
        }
        df = pd.DataFrame(data)
        
        # Note: Document_ID is calculated, so we need to ensure it's not overwritten 
        # or we test the validation of the PROVIDED Document_ID if fallback is used.
        # Actually, if is_calculated is True, it will be recalculated.
        # Let's check if we can force an invalid ID through calculation by using invalid Project_Code
        
        data_invalid_calc = data.copy()
        data_invalid_calc['Project_Code'] = ['999999']
        df_invalid = pd.DataFrame(data_invalid_calc)
        
        with self.assertLogs('universal_document_processor', level='WARNING') as cm:
            result_df = self.processor.process_data(df_invalid)
            
        found = False
        for log in cm.output:
            if "Starts-with validation failed for Document_ID" in log:
                found = True
                break
        self.assertTrue(found, "Should have logged a starts-with validation warning for Document_ID")
        self.assertIn("does not start with valid code from project_schema", result_df.loc[0, 'Validation_Errors'])

    def test_valid_document_id_prefix(self):
        # Data where Document_ID starts with a valid project code (131242)
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
            'Department': ['Dept 1'],
            'Review_Status': ['Pending'],
            'Review_Comments': ['No comments'],
            'Submission_Closed': ['NO'],
            'Resubmission_Required': ['YES'],
            'Notes': ['']
        }
        df = pd.DataFrame(data)
        
        # We check that there is NO "starts with" error in Validation_Errors
        result_df = self.processor.process_data(df)
        val_errors = result_df.loc[0, 'Validation_Errors']
        self.assertNotIn("does not start with valid code from project_schema", val_errors)

if __name__ == "__main__":
    unittest.main()
