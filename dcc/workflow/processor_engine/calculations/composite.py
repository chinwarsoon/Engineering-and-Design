"""
Composite calculations: document ID building, row indexing, and complex lookups.
Extracted from UniversalDocumentProcessor composite and lookup methods.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

# Import hierarchical logging functions from dcc_utility
from dcc_utility.console import status_print, debug_print


def _get_preservation_mode(engine, column_name: str) -> str:
    """
    Get data preservation mode from engine strategy if available.
    Defaults to 'preserve_existing' for backward compatibility.
    """
    # Check if engine has strategy resolver (new strategy-aware engine)
    if hasattr(engine, 'get_column_strategy'):
        try:
            strategy = engine.get_column_strategy(column_name)
            if strategy:
                return strategy.preservation_mode.value
        except Exception:
            pass  # Fall back to default
    
    # Check if strategy is in column definition (passed via calculation dict)
    # This allows strategy to be passed through calculation config
    return "preserve_existing"  # Default behavior


def apply_composite_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply composite calculation using row-by-row formatting.
    Builds values by combining multiple source columns with a format string.
    
    Respects strategy configuration:
    - preserve_existing: Keep existing values, only calculate for nulls (default)
    - overwrite_existing: Replace all values with calculated results
    """
    # Support both 'sources' and 'source_columns'
    source_columns = calculation.get('sources') or calculation.get('source_columns', [])
    format_string = calculation.get('format', '')

    if not format_string:
        engine._print_processing_step("Composite", column_name, "ERROR: No format string provided")
        return df

    # Verify which sources exist in df
    available_sources = [col for col in source_columns if col in df.columns]

    if not available_sources:
        engine._print_processing_step("Composite", column_name, "ERROR: No available source columns")
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

    # Get preservation mode from strategy (respects schema configuration)
    preservation_mode = _get_preservation_mode(engine, column_name)
    
    if preservation_mode == "overwrite_existing":
        # Strategy: Calculate for ALL rows (overwrite mode)
        engine._print_processing_step("Composite", column_name, f"Strategy: overwrite_existing - calculating all {len(df)} rows")
        df[column_name] = df[available_sources].apply(format_row, axis=1)
        engine._print_processing_step("Composite", column_name, f"Applied to all rows (overwritten)")
    else:
        # Strategy: preserve_existing (default) - only calculate for nulls
        existing_mask = df[column_name].notna()
        if existing_mask.any():
            engine._print_processing_step("Composite", column_name, f"Preserving {existing_mask.sum()} existing values")

        # Calculate only for null values
        null_mask = df[column_name].isna()
        if null_mask.any():
            df.loc[null_mask, column_name] = df.loc[null_mask, available_sources].apply(format_row, axis=1)
            engine._print_processing_step("Composite", column_name, f"Applied to {null_mask.sum()} null rows")
        else:
            debug_print(f"Skipped composite for {column_name}: all values present")

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
        engine._print_processing_step("Row-Index", column_name, f"Applied to {null_mask.sum()} null rows")
    else:
        debug_print(f"Skipped row index for {column_name}: all values present")

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
        engine._print_processing_step("Complex-Lookup", column_name, f"ERROR: Missing columns: {missing_cols}")
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
        engine._print_processing_step("Complex-Lookup", column_name, f"Preserving {existing_mask.sum()} existing values")

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
        engine._print_processing_step("Complex-Lookup", column_name, f"Applied to {null_mask.sum()} null rows: {(delay > 0).sum()} rows with positive delay")
    else:
        debug_print(f"Skipped delay_of_resubmission for {column_name}: all values present")

    return df


def apply_copy_calculation(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply direct copy calculation.
    Simply copies values from a source column to the target column.
    """
    source_column = calculation.get('source_column')

    if source_column not in df.columns:
        engine._print_processing_step("Copy", column_name, f"ERROR: Source column {source_column} not found")
        return df

    engine._print_processing_step("Copy", column_name, f"Copying from {source_column}")

    df = df.copy()

    # Initialize column if not exists
    if column_name not in df.columns:
        df[column_name] = None

    # Get existing non-null values
    existing_mask = df[column_name].notna()
    if existing_mask.any():
        engine._print_processing_step("Copy", column_name, f"Preserving {existing_mask.sum()} existing values")

    # Only copy to null values
    null_mask = df[column_name].isna()
    if null_mask.any():
        df.loc[null_mask, column_name] = df.loc[null_mask, source_column]
        engine._print_processing_step("Copy", column_name, f"Applied to {null_mask.sum()} null rows")
    else:
        debug_print(f"Skipped copy for {column_name}: all values present")

    return df


def apply_extract_affixes(engine, df: pd.DataFrame, column_name: str, calculation: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract affixes from Document_ID and store in Document_ID_Affixes column.
    
    Issue #16: Document_ID affix handling
    
    Reads schema parameters:
    - delimiter: from Document_ID.validation.derived_pattern.separator
    - sequence_length: from Document_Sequence_Number.validation.pattern
    
    Args:
        engine: The processing engine
        df: DataFrame with Document_ID column
        column_name: Target column (Document_ID_Affixes)
        calculation: Calculation configuration with source_column
        
    Returns:
        DataFrame with Document_ID_Affixes column populated
    """
    # Import affix extractor
    try:
        from .affix_extractor import extract_document_id_affixes
    except ImportError:
        engine._print_processing_step("Extract Affixes", column_name, "ERROR: affix_extractor not available")
        return df
    
    # Get source column (usually Document_ID)
    source_column = calculation.get('source_column', 'Document_ID')
    
    if source_column not in df.columns:
        engine._print_processing_step("Extract Affixes", column_name, f"ERROR: Source column {source_column} not found")
        return df
    
    # Get schema parameters
    delimiter = calculation.get('delimiter', '-')
    sequence_length = calculation.get('sequence_length', 4)
    
    # Extract affixes
    engine._print_processing_step("Extract Affixes", column_name, f"Extracting from {source_column}")
    
    df = df.copy()
    
    # Apply affix extraction to each row
    affix_results = df[source_column].apply(
        lambda x: extract_document_id_affixes(
            str(x) if pd.notna(x) else '',
            delimiter=delimiter,
            sequence_length=sequence_length
        ) if pd.notna(x) else ('', '')
    )
    
    # Extract affix part (second element of tuple)
    df[column_name] = affix_results.apply(lambda x: x[1])
    
    affix_count = df[column_name].ne('').sum()
    engine._print_processing_step("Extract Affixes", column_name, f"Extracted {affix_count} affixes")
    
    return df
