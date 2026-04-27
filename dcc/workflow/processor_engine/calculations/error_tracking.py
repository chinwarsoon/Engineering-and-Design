"""
Error tracking calculations: aggregating per-row errors into a single column.
"""

import pandas as pd
from typing import Dict, Any, List

# Import hierarchical logging functions from dcc_utility
from dcc_utility.console import status_print, debug_print

def apply_aggregate_row_errors(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Aggregates all errors found in the DetectionResult objects for each row.
    This is typically called in Phase 4/5 after all validations are complete.
    """
    if not hasattr(engine, 'aggregator'):
        return df

    engine._print_processing_step("Error-Tracking", column_name, "Aggregating row-level errors")

    df = df.copy()
    
    # Get all errors from aggregator
    row_errors = engine.aggregator.aggregate_row_errors()
    
    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = ""
    else:
        # Fill nulls with empty string to avoid concatenation issues
        df[column_name] = df[column_name].fillna("")

    # Map errors to rows
    for row_idx, errors in row_errors.items():
        if row_idx < len(df):
            # Format: [CODE] Message; [CODE2] Message2
            error_msgs = [f"[{e.error_code}] {e.message}" for e in errors]
            aggregated_msg = "; ".join(error_msgs)
            
            # Combine with existing value if any
            existing = df.at[row_idx, column_name]
            if existing and aggregated_msg:
                df.at[row_idx, column_name] = f"{existing}; {aggregated_msg}"
            else:
                df.at[row_idx, column_name] = aggregated_msg

    engine._print_processing_step("Error-Tracking", column_name, f"Populated {len(row_errors)} rows with error details")
    
    return df
