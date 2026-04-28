"""
Foundation data utilities for DataFrame manipulation, cleaning, and initialization.
"""
from typing import List, Optional, Any, Dict
import pandas as pd

from utility_engine.console import debug_print


def prepare_dataframe_for_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a DataFrame for safe processing by resetting index."""
    if not isinstance(df.index, pd.RangeIndex):
        df = df.reset_index(drop=True)
    return df


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex/tuple columns to simple string names."""
    df_copy = df.copy()
    if hasattr(pd, 'MultiIndex') and isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = ['_'.join(str(level) for level in levels).strip('_')
                           for levels in df_copy.columns]
    elif len(df_copy.columns) > 0 and isinstance(df_copy.columns[0], tuple):
        df_copy.columns = ['_'.join(str(level) for level in levels).strip('_')
                           for levels in df_copy.columns]
    return df_copy


def ensure_columns_are_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all DataFrame columns are strings."""
    if not all(isinstance(c, str) for c in df.columns):
        df = df.copy()
        df.columns = [str(c) for c in df.columns]
    return df


def initialize_missing_columns(df: pd.DataFrame, 
                                columns_schema: Dict[str, Any],
                                parameters: Dict[str, Any]) -> pd.DataFrame:
    """Initialize missing columns based on schema rules."""
    df_init = df.copy()
    df_init = ensure_columns_are_strings(df_init)

    dyn_creation = parameters.get('dynamic_column_creation', {})
    enabled = dyn_creation.get('enabled', False)
    default = dyn_creation.get('default_value', 'NA')

    for col_name, col_def in columns_schema.items():
        if col_name not in df_init.columns:
            create_missing = col_def.get('create_if_missing', False)
            if create_missing and enabled:
                is_calculated = col_def.get('is_calculated', False)
                default_val = col_def.get('default_value', default)
                
                # Calculated columns should be initialized as None
                df_init[col_name] = None if is_calculated else default_val
                debug_print(f"Created missing column: {col_name}")

    return df_init


def verify_required_columns(df: pd.DataFrame, columns_schema: Dict[str, Any]) -> List[str]:
    """Verify that all non-calculated required columns are present."""
    missing_required = []
    for col_name, col_def in columns_schema.items():
        if col_def.get('required', False) and not col_def.get('is_calculated', False):
            if col_name not in df.columns:
                missing_required.append(col_name)
    return missing_required
