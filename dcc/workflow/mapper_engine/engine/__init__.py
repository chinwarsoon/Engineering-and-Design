"""
Column Mapper Engine

A modular engine for fuzzy header detection and schema-driven column mapping.
"""

from dcc.workflow.mapper_engine.engine.core import ColumnMapperEngine

from dcc.workflow.mapper_engine.engine.matchers import (
    normalize_string,
    fuzzy_match_column,
    fuzzy_match_with_aliases,
    batch_fuzzy_match,
)

from dcc.workflow.mapper_engine.engine.mappers import (
    flatten_multiindex_headers,
    detect_columns,
    extract_categorical_choices,
    rename_dataframe_columns,
)

from dcc.workflow.mapper_engine.engine.utils import (
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
