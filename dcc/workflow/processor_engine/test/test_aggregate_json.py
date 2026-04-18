
import pandas as pd
import json
from processor_engine.core.engine import CalculationEngine

def test_aggregate_json_serialization():
    # 1. Setup mock schema with json data types
    schema_data = {
        "columns": {
            "Document_ID": {"is_calculated": False},
            "Submission_Date": {"is_calculated": False},
            "All_Submission_Dates": {
                "is_calculated": True,
                "data_type": "json",
                "processing_phase": "P3",
                "calculation": {
                    "type": "aggregate",
                    "method": "concatenate_dates",
                    "source_column": "Submission_Date",
                    "group_by": ["Document_ID"],
                    "date_format": "YYYY-MM-DD"
                }
            },
            "All_Submission_Dates_Plain": {
                "is_calculated": True,
                "data_type": "string",
                "processing_phase": "P3",
                "calculation": {
                    "type": "aggregate",
                    "method": "concatenate_dates",
                    "source_column": "Submission_Date",
                    "group_by": ["Document_ID"],
                    "date_format": "YYYY-MM-DD"
                }
            },
            "All_Sessions": {
                "is_calculated": True,
                "data_type": "json",
                "processing_phase": "P3",
                "calculation": {
                    "type": "aggregate",
                    "method": "concatenate_unique",
                    "source_column": "Session",
                    "group_by": ["Document_ID"]
                }
            }
        },
        "column_sequence": ["Document_ID", "Submission_Date", "Session", "All_Submission_Dates", "All_Submission_Dates_Plain", "All_Sessions"],
        "parameters": {"fail_fast": False}
    }

    # 2. Setup sample data
    df = pd.DataFrame({
        "Document_ID": ["DOC1", "DOC1", "DOC2"],
        "Submission_Date": ["2023-01-01", "2023-01-15", "2023-02-01"],
        "Session": ["S1", "S2", "S1"]
    })

    # 3. Run engine
    engine = CalculationEngine(schema_data)
    df_processed = engine.process_data(df)

    # 4. Assertions
    # DOC1 should have both dates in a JSON array for All_Submission_Dates
    doc1_json = df_processed.loc[df_processed["Document_ID"] == "DOC1", "All_Submission_Dates"].iloc[0]
    doc1_plain = df_processed.loc[df_processed["Document_ID"] == "DOC1", "All_Submission_Dates_Plain"].iloc[0]
    doc1_sessions = df_processed.loc[df_processed["Document_ID"] == "DOC1", "All_Sessions"].iloc[0]

    print(f"DOC1 JSON: {doc1_json}")
    print(f"DOC1 Plain: {doc1_plain}")
    print(f"DOC1 Sessions: {doc1_sessions}")

    assert isinstance(doc1_json, str)
    dates_list = json.loads(doc1_json)
    assert len(dates_list) == 2
    assert "2023-01-01" in dates_list
    assert "2023-01-15" in dates_list

    assert doc1_plain == "2023-01-01, 2023-01-15"

    assert json.loads(doc1_sessions) == ["S1", "S2"]
    
    # DOC2 should have single date in JSON array
    doc2_json = df_processed.loc[df_processed["Document_ID"] == "DOC2", "All_Submission_Dates"].iloc[0]
    print(f"DOC2 JSON: {doc2_json}")
    assert json.loads(doc2_json) == ["2023-02-01"]

    print("✓ Aggregate JSON serialization test passed!")

if __name__ == "__main__":
    test_aggregate_json_serialization()
