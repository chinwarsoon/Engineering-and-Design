"""
Fuzzy matching algorithms for column header matching.
"""

from .fuzzy import (
    normalize_string,
    fuzzy_match_column,
    fuzzy_match_with_aliases,
    batch_fuzzy_match,
)

__all__ = [
    'normalize_string',
    'fuzzy_match_column',
    'fuzzy_match_with_aliases',
    'batch_fuzzy_match',
]
