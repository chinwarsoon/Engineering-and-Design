from engine.core.engine import CalculationEngine
import pandas as pd

def test_full_engine_flow():
    mock_schema = {
        "enhanced_schema": {
            "columns": {
                "Status": {"null_handling": {"strategy": "default_value", "value": "Unknown"}},
                "Is_Rejected": {
                    "is_calculated": True, 
                    "calculation": {"type": "conditional", "method": "update_resubmission_required", "source_column": "Status"}
                }
            }
        }
    }
    
    df = pd.DataFrame({'Status': [None, 'Rejected']})
    engine = CalculationEngine(mock_schema)
    
    result = engine.process_data(df)
    
    assert result.loc[0, 'Status'] == "Unknown"
    assert result.loc[1, 'Is_Rejected'] == "Yes"