"""
Heavy-duty grouping logic such as _apply_aggregate_calculation, _apply_latest_by_date_calculation, and _apply_latest_non_pending_status.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def apply_aggregate_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Performs standard grouping and aggregation (Min, Max, Sum, etc.)
    """
    source_column = calculation.get('source_column')
    group_by = calculation.get('group_by', [])
    agg_func = calculation.get('function', 'max')

    if not source_column or not group_by:
        return df

    engine._print_processing_step("Aggregate", column_name, f"{agg_func} of {source_column} grouped by {group_by}")

    # Calculate aggregate and map back to the original dataframe
    agg_series = df.groupby(group_by)[source_column].transform(agg_func)
    df[column_name] = agg_series

    return df

def apply_latest_by_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Identifies the 'latest' value in a group based on a date column.
    Commonly used to find the 'Latest Review Status' for a document.
    """
    group_by = calculation.get('group_by', ['Document_Number'])
    date_col = calculation.get('date_column', 'Submission_Date')
    source_col = calculation.get('source_column')

    if source_col not in df.columns or date_col not in df.columns:
        return df

    engine._print_processing_step("Latest-By-Date", column_name, f"Finding latest {source_col} via {date_col}")

    # Ensure date is datetime for comparison
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    # Sort by group and date, then take the last entry for each group
    # We use transform('last') after sorting to keep the dataframe index aligned
    df_sorted = df.sort_values(by=group_by + [date_col], ascending=True)
    
    # Map the last value of the sorted source_col back to every row in the group
    df[column_name] = df_sorted.groupby(group_by)[source_col].transform('last')

    return df

def apply_latest_non_pending_status(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized logic to find the latest status that is NOT 'Pending'.
    Used to determine the 'Effective Status' of a document sequence.
    """
    group_by = calculation.get('group_by', ['Document_Number'])
    status_col = calculation.get('source_column', 'Review_Status')
    date_col = calculation.get('date_column', 'Submission_Date')

    if status_col not in df.columns:
        return df

    engine._print_processing_step("Aggregate", column_name, "Finding latest non-pending status")

    # 1. Create a temporary version of the status column where 'Pending' is NaN
    temp_col = f"_{status_col}_filtered"
    df[temp_col] = df[status_col].apply(lambda x: x if str(x).lower() != 'pending' else np.nan)

    # 2. Sort by date
    df_sorted = df.sort_values(by=group_by + [date_col], ascending=True)

    # 3. Get the last non-NaN value per group
    df[column_name] = df_sorted.groupby(group_by)[temp_col].transform('last')

    # 4. Cleanup
    df.drop(columns=[temp_col], inplace=True)
    
    return df