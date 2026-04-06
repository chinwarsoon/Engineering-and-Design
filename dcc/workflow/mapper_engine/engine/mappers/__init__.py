"""
Column mapping logic for schema-driven header detection.
"""

from dcc.workflow.mapper_engine.engine.mappers.detection import (
    flatten_multiindex_headers,
    detect_columns,
    extract_categorical_choices,
    rename_dataframe_columns,
)

__all__ = [
    'flatten_multiindex_headers',
    'detect_columns',
    'extract_categorical_choices',
    'rename_dataframe_columns',
]
