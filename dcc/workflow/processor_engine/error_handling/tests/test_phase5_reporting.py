"""
Phase 5 Integration Test

Verifies:
1. Data_Health_Score column population
2. Error summary generation
3. Processing summary report enhancement
"""

import pandas as pd
import json
from pathlib import Path
from dcc.workflow.processor_engine.core.engine import CalculationEngine
from dcc.workflow.reporting_engine.summary import write_processing_summary

def test_phase5_reporting():
    # Mock schema
    schema = {
        "parameters": {},
        "enhanced_schema": {
            "columns": {
                "Project_Code": {"processing_phase": "P1", "null_handling": {"strategy": "leave_null"}},
                "Submission_Session": {"processing_phase": "P1", "null_handling": {"strategy": "leave_null"}},
                "Validation_Errors": {"processing_phase": "P3", "is_calculated": True},
                "Data_Health_Score": {"processing_phase": "P3", "is_calculated": True}
            },
            "column_sequence": ["Project_Code", "Submission_Session", "Validation_Errors", "Data_Health_Score"]
        }
    }
    
    # Mock data with errors
    df = pd.DataFrame([
        # Row 0: Perfect
        {
            "Project_Code": "PRJ001", 
            "Submission_Session": "240101",
            "Facility_Code": "FAC01",
            "Document_Type": "DRAW",
            "Document_Sequence_Number": "0001",
            "Discipline": "ARC",
            "First_Submission_Date": "2024-01-01"
        },
        # Row 1: High Error (Session format)
        {
            "Project_Code": "PRJ002", 
            "Submission_Session": "123",
            "Facility_Code": "FAC01",
            "Document_Type": "SPEC",
            "Document_Sequence_Number": "0002",
            "Discipline": "STR",
            "First_Submission_Date": "2024-01-01"
        }
    ])
    
    print("Initializing Engine...")
    engine = CalculationEngine(schema)
    
    print("Processing Data...")
    df_processed = engine.process_data(df)
    
    print("\nProcessed DataFrame Columns:")
    print(df_processed.columns.tolist())
    
    print("\nData Health Scores:")
    for i, score in enumerate(df_processed["Data_Health_Score"]):
        print(f"Row {i}: {score}")
        
    # Verify summary
    summary = engine.get_error_summary()
    print("\nError Summary KPI:")
    print(json.dumps(summary, indent=2))
    
    # Test summary file writing
    summary_file = Path("test_summary.txt")
    write_processing_summary(
        summary_path=summary_file,
        input_file=Path("test.xlsx"),
        main_schema_path=Path("schema.json"),
        schema_results={"error_summary": summary},
        raw_columns=["Project_Code", "Submission_Session"],
        mapped_columns=["Project_Code", "Submission_Session"],
        processed_columns=df_processed.columns.tolist(),
        raw_shape=(3, 2),
        mapped_shape=(3, 2),
        processed_shape=df_processed.shape,
        df_raw=df,
        df_mapped=df,
        df_processed=df_processed,
        mapping_result={"match_rate": 1.0, "total_headers": 2, "matched_count": 2, "missing_required": []},
        schema_reference_count=0,
        csv_path=Path("test.csv"),
        excel_path=Path("test.xlsx")
    )
    
    print(f"\nSummary report written to {summary_file}")
    print("Contents snippet:")
    with open(summary_file, "r") as f:
        content = f.read()
        if "Data Health Diagnostics" in content:
            print("✓ Found Data Health Diagnostics in report")
            # Print specifically that section
            start = content.find("Data Health Diagnostics")
            end = content.find("Column Overview")
            print(content[start:end])
        else:
            print("✗ Data Health Diagnostics NOT found in report")

if __name__ == "__main__":
    test_phase5_reporting()
