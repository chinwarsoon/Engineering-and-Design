"""
Composite calculations: document ID building, row indexing, and complex lookups.
Extracted from UniversalDocumentProcessor composite and lookup methods.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def apply_composite_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply composite calculation using row-by-row formatting.
    Builds values by combining multiple source columns with a format string.
    """
    # Support both 'sources' and 'source_columns'
    source_columns = calculation.get('sources') or calculation.get('source_columns', [])
    format_string = calculation.get('format', '')

    if not format_string:
        logger.warning(f"No format string provided for composite calculation of {column_name}")
        return df

    # Verify which sources exist in df
    available_sources = [col for col in source_columns if col in df.columns]

    if not available_sources:
        logger.warning(f"No available source columns for composite calculation: {column_name}")
        return df

    engine._print_processing_step("Composite", column_name, f"Formatting with {len(available_sources)}/{len(source_columns)} sources")

    def format_row(row):
        try:
            # Fill NA/NaN values with empty string before formatting
            values = {col: '' if pd.isna(row.get(col)) else row[col] for col in available_sources}
            return format_string.format(**values)
        except Exception:
            return "ERR-COMPOSITE"

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = np.nan

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        logger.info(f"Preserving {existing_mask.sum()} existing values in {column_name}")

    # Calculate only for null values
    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = df.loc[null_mask, available_sources].apply(format_row, axis=1)
        logger.info(f"Applied composite calculation to {null_mask.sum()} null rows in {column_name}")
    else:
        logger.info(f"Skipped composite for {column_name}: all values present")

    return df


def apply_row_index(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate or preserve auto-increment row index starting from 1.

    This creates a unique index for each row in the imported data,
    useful for tracking original row positions.
    The Row_Index column is placed as the first column in the DataFrame.
    """
    df = df.copy()

    # Only generate row index where null - preserve existing values
    if column_name not in df.columns:
        df[column_name] = None

    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = range(1, null_mask.sum() + 1)
        logger.info(f"Applied row index to {null_mask.sum()} null rows in {column_name}")
    else:
        logger.info(f"Skipped row index for {column_name}: all values present")

    # Move column to front
    cols = df.columns.tolist()
    if column_name in cols:
        cols.remove(column_name)
        df = df[[column_name] + cols]

    return df


def apply_delay_of_resubmission(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate Delay_of_Resubmission with non-negative check.

    Logic:
    - If Submission_Closed == 'YES', return 0
    - Find previous submissions for same Document_ID with earlier Submission_Date
    - Get latest Resubmission_Plan_Date from previous submissions
    - Calculate days between that plan date and current Submission_Date
    - Ensure non-negative: return max(delay, 0)

    FIX: replaced O(n^2) iterrows loop with a vectorised self-join approach.
    """
    doc_id_col = 'Document_ID'
    submission_date_col = 'Submission_Date'
    plan_date_col = 'Resubmission_Plan_Date'
    closed_col = 'Submission_Closed'

    required_cols = [doc_id_col, submission_date_col, plan_date_col, closed_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing required columns for delay calculation: {missing_cols}")
        df = df.copy()
        df[column_name] = 0
        return df

    engine._print_processing_step("Complex-Lookup", column_name, "Calculating delay from previous resubmission plan")

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        logger.info(f"Preserving {existing_mask.sum()} existing values in {column_name}")

    df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
    df[plan_date_col] = pd.to_datetime(df[plan_date_col], errors='coerce')

    # For each row we need the max Resubmission_Plan_Date of all earlier rows
    # (same Document_ID, earlier Submission_Date).
    # Vectorised: sort by doc + date, use shifted cummax per group, then re-align.
    df_sorted = df[[doc_id_col, submission_date_col, plan_date_col, closed_col]].copy()
    df_sorted = df_sorted.sort_values([doc_id_col, submission_date_col])

    df_sorted['_prev_max_plan'] = (
        df_sorted.groupby(doc_id_col)[plan_date_col]
        .transform(lambda s: s.shift(1).cummax())
    )

    # Re-align to original index
    prev_max_plan = df_sorted['_prev_max_plan'].reindex(df.index)

    # Calculate delay
    delay = (df[submission_date_col] - prev_max_plan).dt.days.fillna(0).clip(lower=0).astype(int)

    # Override: closed submissions always have delay 0
    closed_mask = df[closed_col] == 'YES'
    delay[closed_mask] = 0

    # Only apply to null values
    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = delay[null_mask]
        logger.info(f"Applied delay_of_resubmission to {null_mask.sum()} null rows in {column_name}: {(delay > 0).sum()} rows with positive delay")
    else:
        logger.info(f"Skipped delay_of_resubmission for {column_name}: all values present")

    return df


def apply_copy_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply direct copy calculation.
    Simply copies values from a source column to the target column.
    """
    source_column = calculation.get('source_column')

    if source_column not in df.columns:
        logger.warning(f"Copy calculation skipped for {column_name}: source column {source_column} not found")
        return df

    engine._print_processing_step("Copy", column_name, f"Copying from {source_column}")

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        logger.info(f"Preserving {existing_mask.sum()} existing values in {column_name}")

    # Only copy to null values
    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = df.loc[null_mask, source_column]
        logger.info(f"Applied copy to {null_mask.sum()} null rows in {column_name}")
    else:
        logger.info(f"Skipped copy for {column_name}: all values present")

    return df
