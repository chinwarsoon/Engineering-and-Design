"""
Defensive Pandas DataFrame utility functions extracted from UniversalDocumentProcessor.
Includes index resetting, column flattening, column management, and safe copy operations.
"""

import pandas as pd
from typing import List, Optional, Set

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine import status_print, debug_print


def prepare_dataframe_for_processing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a DataFrame for safe processing by resetting index and ensuring clean state.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with RangeIndex and clean state
    """
    debug_print(f"[PREPARE] Entry - DataFrame index type: {type(df.index)}")
    if not isinstance(df.index, pd.RangeIndex):
        debug_print(f"DataFrame index is {type(df.index)}, resetting to RangeIndex")
        debug_print(f"Current index sample: {df.index[:3].tolist() if hasattr(df.index, 'tolist') else list(df.index)[:3]}")
        df = df.reset_index(drop=True)
        debug_print(f"Index reset to RangeIndex, new index sample: {df.index[:3].tolist()}")

    return df


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex/tuple columns to simple string column names.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with flattened string column names
    """
    df_copy = df.copy()

    if hasattr(pd, 'MultiIndex') and isinstance(df_copy.columns, pd.MultiIndex):
        debug_print("Flattening MultiIndex columns")
        df_copy.columns = ['_'.join(str(level) for level in levels).strip('_')
                           for levels in df_copy.columns]
    elif len(df_copy.columns) > 0 and isinstance(df_copy.columns[0], tuple):
        debug_print("Flattening tuple columns")
        df_copy.columns = ['_'.join(str(level) for level in levels).strip('_')
                           for levels in df_copy.columns]

    # Double-check all columns are strings
    if not all(isinstance(c, str) for c in df_copy.columns):
        debug_print("Non-string columns detected, converting all to strings")
        df_copy.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_')
                           for c in df_copy.columns]

    return df_copy


def ensure_columns_are_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all DataFrame columns are strings, flattening if necessary.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with string column names
    """
    if not all(isinstance(c, str) for c in df.columns):
        debug_print("Flattening non-string columns")
        df = df.copy()
        df.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_')
                      for c in df.columns]
    return df


def move_column_to_front(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Move a specified column to the first position in the DataFrame.

    Args:
        df: Input DataFrame
        column_name: Name of column to move

    Returns:
        DataFrame with specified column as first column
    """
    cols = df.columns.tolist()
    if column_name not in cols:
        return df

    cols.remove(column_name)
    return df[[column_name] + cols]


def initialize_missing_columns(df: pd.DataFrame, columns_schema: dict,
                                parameters: dict, global_enabled: bool = False,
                                global_default: str = 'NA') -> pd.DataFrame:
    """
    Initialize missing columns based on schema rules.

    Args:
        df: Input DataFrame
        columns_schema: Column definitions from schema
        parameters: Schema parameters
        global_enabled: Whether dynamic column creation is globally enabled
        global_default: Default value for missing columns

    Returns:
        DataFrame with missing columns initialized
    """
    df_init = df.copy()

    # Ensure columns are strings before processing
    df_init = ensure_columns_are_strings(df_init)

    dyn_creation = parameters.get('dynamic_column_creation', {})
    enabled = dyn_creation.get('enabled', global_enabled)
    default = dyn_creation.get('default_value', global_default)

    # Cast Submission_Session related columns to string for consistent grouping
    submission_session_cols = ['Submission_Session', 'Submission_Session_Revision']
    for col in submission_session_cols:
        if col in df_init.columns:
            df_init[col] = df_init[col].astype(str)
            debug_print(f"Cast {col} to string for consistent grouping")

    for col_name, col_def in columns_schema.items():
        if not isinstance(col_def, dict):
            continue
        if col_name not in df_init.columns:
            create_missing = col_def.get('create_if_missing', False)

            if create_missing and enabled:
                # Calculated columns should be initialized as None to ensure 
                # they are processed by the calculation engine later.
                is_calculated = col_def.get('is_calculated', False)
                default_val = default
                if 'default_value' in col_def:  # Top level overrides global
                    default_val = col_def.get('default_value')
                
                final_val = None if is_calculated else default_val
                df_init[col_name] = final_val
                debug_print(f"Created missing column: {col_name} with value '{final_val}' (calculated={is_calculated})")

    return df_init


def verify_required_columns(df: pd.DataFrame, columns_schema: dict) -> List[str]:
    """
    Verify that all columns marked as required (and not calculated) are present.

    Args:
        df: DataFrame to check
        columns_schema: Column definitions from schema

    Returns:
        List of missing required column names

    Raises:
        ValueError: If required input columns are missing
    """
    missing_required = []
    for col_name, col_def in columns_schema.items():
        if not isinstance(col_def, dict):
            continue
        is_required = col_def.get('required', False)
        is_calculated = col_def.get('is_calculated', False)

        # If required, but NOT calculated, it MUST be in the input
        if is_required and not is_calculated:
            if col_name not in df.columns:
                missing_required.append(col_name)

    return missing_required


def cast_submission_session_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast Submission_Session related columns to string for consistent grouping.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with submission session columns cast to string
    """
    df_copy = df.copy()
    submission_session_cols = ['Submission_Session', 'Submission_Session_Revision']
    for col in submission_session_cols:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].astype(str)
            debug_print(f"Cast {col} to string for consistent grouping")
    return df_copy


def safe_copy_with_index_reset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a safe copy of DataFrame with index reset if needed.

    Args:
        df: Input DataFrame

    Returns:
        Safe copy with RangeIndex
    """
    df_copy = df.reset_index(drop=True).copy() if not isinstance(df.index, pd.RangeIndex) else df.copy()
    return df_copy


def remove_duplicate_columns(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Remove duplicate columns from DataFrame, keeping only first occurrence.

    Args:
        df: Input DataFrame
        column_name: Column name to check for duplicates

    Returns:
        DataFrame with duplicates removed
    """
    if df.columns.tolist().count(column_name) > 1:
        debug_print(f"DUPLICATE COLUMNS DETECTED: '{column_name}' appears {df.columns.tolist().count(column_name)} times! Removing duplicates.")
        df = df.loc[:, ~df.columns.duplicated()].copy()
        df.index = pd.RangeIndex(len(df))
    return df
