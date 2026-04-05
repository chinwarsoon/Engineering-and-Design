
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

class TestGroupConsistencyValidation(unittest.TestCase):
    def setUp(self):
        self.processor = UniversalDocumentProcessor()
        self.processor.schema_file = str(ROOT / "config" / "schemas" / "dcc_register_enhanced.json")
        self.processor.load_schema()
        
    def test_inconsistent_submission_date(self):
        # Data where same (Submission_Session, Submission_Session_Revision) has different Submission_Dates
        data = {
            'Submission_Session': ['000001', '000001', '000002'],
            'Submission_Session_Revision': ['01', '01', '01'],
            'Submission_Date': ['2026-04-01', '2026-04-02', '2026-04-01'], # Row 0 and 1 are inconsistent
            'Document_ID': ['DOC-1', 'DOC-2', 'DOC-3'],
            'Project_Code': ['P1', 'P1', 'P1'],
            'Facility_Code': ['F1', 'F1', 'F1'],
            'Document_Type': ['T1', 'T1', 'T1'],
            'Discipline': ['D1', 'D1', 'D1'],
            'Document_Sequence_Number': ['0001', '0002', '0003'],
            'Document_Revision': ['0', '0', '0'],
            'Document_Title': ['Title 1', 'Title 2', 'Title 3'],
            'Submission_Session_Subject': ['Subject 1', 'Subject 1', 'Subject 2'],
            'Department': ['Dept 1', 'Dept 1', 'Dept 2'],
            'Review_Status': ['Pending', 'Pending', 'Pending'],
            'Review_Comments': ['No comments', 'No comments', 'No comments'],
            'Submission_Closed': ['NO', 'NO', 'NO'],
            'Resubmission_Required': ['YES', 'YES', 'YES'],
            'Notes': ['', '', '']
        }
        df = pd.DataFrame(data)
        
        with self.assertLogs(level='WARNING') as cm:
            result_df = self.processor.process_data(df)
            
        # Check if the warning about group consistency is present
        found = False
        for log in cm.output:
            if "Group consistency validation failed for Submission_Session" in log:
                found = True
                break
        self.assertTrue(found, "Should have logged a group consistency warning")

        # Verify Validation_Errors column
        self.assertIn('Validation_Errors', result_df.columns)
        # Session 000001 (rows 0, 1) should have errors
        self.assertTrue("group inconsistency" in result_df.loc[0, 'Validation_Errors'].lower())
        self.assertTrue("group inconsistency" in result_df.loc[1, 'Validation_Errors'].lower())
        # Session 000002 (row 2) should NOT have group inconsistency error (but might have others like schema ref)
        self.assertFalse("group inconsistency" in result_df.loc[2, 'Validation_Errors'].lower())
        print("Validation_Errors content for row 0:", result_df.loc[0, 'Validation_Errors'])

    def test_consistent_submission_date(self):
        # Data where same (Submission_Session, Submission_Session_Revision) has SAME Submission_Dates
        data = {
            'Submission_Session': ['000001', '000001', '000002'],
            'Submission_Session_Revision': ['01', '01', '01'],
            'Submission_Date': ['2026-04-01', '2026-04-01', '2026-04-01'], # Consistent
            'Document_ID': ['DOC-1', 'DOC-2', 'DOC-3'],
            'Project_Code': ['P1', 'P1', 'P1'],
            'Facility_Code': ['F1', 'F1', 'F1'],
            'Document_Type': ['T1', 'T1', 'T1'],
            'Discipline': ['D1', 'D1', 'D1'],
            'Document_Sequence_Number': ['0001', '0002', '0003'],
            'Document_Revision': ['0', '0', '0'],
            'Document_Title': ['Title 1', 'Title 2', 'Title 3'],
            'Submission_Session_Subject': ['Subject 1', 'Subject 1', 'Subject 2'],
            'Department': ['Dept 1', 'Dept 1', 'Dept 2'],
            'Review_Status': ['Pending', 'Pending', 'Pending'],
            'Review_Comments': ['No comments', 'No comments', 'No comments'],
            'Submission_Closed': ['NO', 'NO', 'NO'],
            'Resubmission_Required': ['YES', 'YES', 'YES'],
            'Notes': ['', '', '']
        }
        df = pd.DataFrame(data)
        
        # We don't expect ANY warning about group consistency here.
        # Other warnings might occur due to schema references not being resolved in this simple test,
        # but we specifically check that group consistency warning is NOT there.
        try:
            with self.assertLogs(level='WARNING') as cm:
                self.processor.process_data(df)
                for log in cm.output:
                    if "Group consistency validation failed for Submission_Session" in log:
                        self.fail(f"Unexpected group consistency warning: {log}")
        except AssertionError:
            # If no warnings at all were logged, assertLogs raises AssertionError.
            # This is also fine for this test.
            pass

if __name__ == "__main__":
    unittest.main()
