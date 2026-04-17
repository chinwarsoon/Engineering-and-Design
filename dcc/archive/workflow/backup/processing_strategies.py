import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def safe_handler(func):
    """Decorator to manage duplicate columns, series extraction, and errors."""
    def wrapper(df, column_name, *args, **kwargs):
        if column_name not in df.columns:
            return None
        data = df[column_name]
        if isinstance(data, pd.DataFrame):
            data = data.iloc[:, 0]
        return func(data, df=df, **kwargs)
    return wrapper

# --- NULL HANDLING STRATEGIES ---

@safe_handler
def ffill_strategy(series, df=None, group_by=None, **kwargs):
    """Forward fill, optionally grouped (e.g. fill Revision based on Doc ID)."""
    if group_by:
        valid_groups = [g for g in group_by if g in df.columns]
        if valid_groups:
            return df.groupby(valid_groups)[series.name].ffill()
    return series.ffill()

@safe_handler
def static_value_strategy(series, fill_value="NA", **kwargs):
    """Fills nulls with a fixed string or number."""
    return series.fillna(fill_value)

@safe_handler
def boolean_flag_strategy(series, **kwargs):
    """Converts truthy values to True/False (useful for 'Is Latest' columns)."""
    return series.map({1: True, 0: False, 'Yes': True, 'No': False}).fillna(False)

# --- CALCULATION STRATEGIES ---

@safe_handler
def date_diff_strategy(series, df=None, end_col=None, **kwargs):
    """Calculates days between dates (e.g., Review Turnaround)."""
    if end_col not in df.columns: return series
    start = pd.to_datetime(series, errors='coerce')
    end = pd.to_datetime(df[end_col], errors='coerce')
    return (end - start).dt.days

# --- REGISTRY ---
STRATEGY_MAP = {
    "forward_fill": ffill_strategy,
    "static_value": static_value_strategy,
    "boolean_flag": boolean_flag_strategy,
    "date_difference": date_diff_strategy
}