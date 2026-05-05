"""
Foundation data utilities for DataFrame manipulation, cleaning, and initialization.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from core_engine.data.data_dataframe import (
    prepare_dataframe_for_processing,
    flatten_columns,
    ensure_columns_are_strings,
    initialize_missing_columns,
    verify_required_columns,
)

__all__ = [
    "prepare_dataframe_for_processing",
    "flatten_columns",
    "ensure_columns_are_strings",
    "initialize_missing_columns",
    "verify_required_columns",
]
