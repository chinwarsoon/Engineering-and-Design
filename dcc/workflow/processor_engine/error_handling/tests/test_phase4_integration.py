
import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from dcc.workflow.processor_engine.core.engine import CalculationEngine

def test_engine_integration():
    # Mock schema data
    schema_data = {
        "enhanced_schema": {
            "columns": {
                "Project_Code": {
                    "processing_phase": "P1",
                    "required": True,
                    "validation": {"pattern": "^[A-Z0-9]+$"}
                },
                "Submission_Session": {
                    "processing_phase": "P1",
                    "validation": {"pattern": "^[0-9]{6}$"}
                },
                "Document_ID": {
                    "processing_phase": "P2",
                    "is_calculated": True,
                    "calculation": {"type": "concat", "method": "basic", "columns": ["Project_Code", "Document_Type"]}
                },
                "Document_Type": {
                    "processing_phase": "P1"
                },
                "Validation_Errors": {
                    "processing_phase": "P4"
                }
            },
            "column_sequence": ["Project_Code", "Submission_Session", "Document_Type", "Document_ID", "Validation_Errors"]
        }
    }
    
    # Create engine
    engine = CalculationEngine(schema_data)
    
    # Create test data with errors
    df = pd.DataFrame([
        # Row 0: Valid
        {
            "Project_Code": "PRJ001", 
            "Submission_Session": "240101", 
            "Document_Type": "DRAW", 
            "Facility_Code": "FAC01", 
            "Document_Sequence_Number": "0001", 
            "Discipline": "ARC",
            "First_Submission_Date": "2024-01-01"
        },
        # Row 1: Invalid Session (too short) - HIGH error, but not CRITICAL fail-fast
        {
            "Project_Code": "PRJ002", 
            "Submission_Session": "123", 
            "Document_Type": "SPEC", 
            "Facility_Code": "FAC01", 
            "Document_Sequence_Number": "0002", 
            "Discipline": "STR",
            "First_Submission_Date": "2024-01-01"
        }
    ])
    
    print("Initial DataFrame:")
    print(df)
    
    try:
        # Process data
        df_out = engine.process_data(df)
        
        print("\nProcessed DataFrame:")
        print(df_out)
        
        if "Validation_Errors" in df_out.columns:
            print("\nValidation Errors Column Content:")
            for i, val in enumerate(df_out["Validation_Errors"]):
                print(f"Row {i}: {val}")
        else:
            print("\nERROR: Validation_Errors column missing!")
            
    except Exception as e:
        print(f"\nProcessing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_engine_integration()
