import pandas as pd
import pytest
from engine.calculations.date import calculate_working_days

def test_calculate_working_days():
    # 1. Setup minimal data
    df = pd.DataFrame({
        'Submission_Date': ['2024-01-01', '2024-01-10', None]
    })
    
    # Mock the engine object since the function expects it for logging
    class MockEngine:
        def _print_processing_step(self, *args): pass
            
    calculation_config = {'source_column': 'Submission_Date', 'parameters': {'days': 5}}
    
    # 2. Execute
    result_df = calculate_working_days(MockEngine(), df, 'Due_Date', calculation_config)
    
    # 3. Assert
    assert result_df.loc[0, 'Due_Date'] == pd.Timestamp('2024-01-06')
    assert pd.isna(result_df.loc[2, 'Due_Date'])dcc/workflow/processor_engine/test/__pycache__