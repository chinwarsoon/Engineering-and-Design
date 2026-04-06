"""
date.py: All date-related math, including _calculate_working_days and _apply_resubmission_plan_date.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def apply_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Standard date calculation (e.g., adding a fixed number of days to a source column).
    """
    source_column = calculation.get('source_column')
    parameters = calculation.get('parameters', {})
    days = parameters.get('days', 0)
    
    if not source_column or source_column not in df.columns:
        return df

    engine._print_processing_step("Date-Calc", column_name, f"Adding {days} days to {source_column}")

    # Ensure source is datetime
    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
    
    # Apply addition
    df[column_name] = df[source_column] + pd.Timedelta(days=days)
    
    return df

def calculate_working_days(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates a future date by adding a specific number of days to a source date.
    Note: In the original implementation, this used a simple Timedelta addition.
    """
    source_column = calculation.get('source_column')
    parameters = calculation.get('parameters', {})
    days = parameters.get('days', 14) # Default to 14 days if not specified
    
    if source_column not in df.columns:
        return df

    engine._print_processing_step("Working-Days", column_name, f"+{days} days from {source_column}")

    # Convert columns to datetime for safety
    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
    
    # Calculate target date
    # mask ensures we only calculate where the source date is valid
    mask = df[source_column].notna()
    df.loc[mask, column_name] = df.loc[mask, source_column] + pd.Timedelta(days=days)
    
    return df

def apply_resubmission_plan_date(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Specialized logic for 'Resubmission_Plan_Date' based on review status.
    Typically adds a set duration (e.g., 14 days) to the review return date.
    """
    source_column = calculation.get('source_column', 'Review_Return_Actual_Date')
    parameters = calculation.get('parameters', {})
    days_to_add = parameters.get('days', 14)

    if source_column not in df.columns:
        return df

    engine._print_processing_step("Resubmission-Plan", column_name, f"Calculating based on {source_column}")

    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
    
    mask = df[source_column].notna()
    df.loc[mask, column_name] = df.loc[mask, source_column] + pd.Timedelta(days=days_to_add)

    return df

def apply_conditional_date_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies date math only if certain conditions (like a status check) are met.
    """
    source_column = calculation.get('source_column')
    condition_col = calculation.get('condition_column')
    target_status = calculation.get('target_status')
    days = calculation.get('days', 0)

    if not all(col in df.columns for col in [source_column, condition_col]):
        return df

    df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
    
    # Only apply to rows matching the status
    mask = (df[condition_col] == target_status) & df[source_column].notna()
    df.loc[mask, column_name] = df.loc[mask, source_column] + pd.Timedelta(days=days)
    
    return df