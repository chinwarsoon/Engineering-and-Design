"""
Utility functions for the document processor engine.
"""

from .dataframe import (
    prepare_dataframe_for_processing,
    flatten_columns,
    ensure_columns_are_strings,
    move_column_to_front,
    initialize_missing_columns,
    verify_required_columns,
    cast_submission_session_columns,
    safe_copy_with_index_reset,
    remove_duplicate_columns,
)

from .dataio import (
    load_excel_data,
)

__all__ = [
    'prepare_dataframe_for_processing',
    'flatten_columns',
    'ensure_columns_are_strings',
    'move_column_to_front',
    'load_excel_data',
]
