"""
Column Mapper Engine

A modular engine for fuzzy header detection and schema-driven column mapping.
"""

from .core import ColumnMapperEngine

from .matchers import (
    normalize_string,
    fuzzy_match_column,
    fuzzy_match_with_aliases,
    batch_fuzzy_match,
)

from .mappers import (
    flatten_multiindex_headers,
    detect_columns,
    extract_categorical_choices,
    rename_dataframe_columns,
)

from .utils import (
    get_column_bounds,
    analyze_column_coverage,
)

__all__ = [
    'ColumnMapperEngine',
    'normalize_string',
    'fuzzy_match_column',
    'fuzzy_match_with_aliases',
    'batch_fuzzy_match',
    'flatten_multiindex_headers',
    'detect_columns',
    'extract_categorical_choices',
    'rename_dataframe_columns',
    'get_column_bounds',
    'analyze_column_coverage',
]
