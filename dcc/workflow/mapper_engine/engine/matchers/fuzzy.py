"""
Fuzzy matching algorithms for column header matching.
Extracted from UniversalColumnMapper fuzzy matching methods.
"""

import difflib
import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def normalize_string(text: str) -> str:
    """
    Normalize string for comparison.
    
    Args:
        text: String to normalize
        
    Returns:
        Normalized string
    """
    # Convert to lowercase and remove extra whitespace
    normalized = text.lower().strip()
    
    # Remove common prefixes/suffixes
    prefixes = ['the ', 'a ', 'an ']
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    # Remove special characters and extra spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized.strip()


def fuzzy_match_column(header: str, target_columns: List[str], threshold: float = 0.6) -> Tuple[str, float]:
    """
    Perform fuzzy matching between header and target columns.
    
    Args:
        header: Input header to match
        target_columns: List of possible target columns
        threshold: Minimum similarity score (0-1)
        
    Returns:
        Tuple of (best_match, similarity_score)
    """
    header_clean = normalize_string(header)
    best_match = ""
    best_score = 0.0
    
    for target in target_columns:
        target_clean = normalize_string(target)
        
        # Exact match
        if header_clean == target_clean:
            return target, 1.0
        
        # Fuzzy match using sequence matcher
        score = difflib.SequenceMatcher(None, header_clean, target_clean).ratio()
        if score > best_score and score >= threshold:
            best_match = target
            best_score = score
    
    return best_match, best_score


def fuzzy_match_with_aliases(header: str, aliases: List[str], threshold: float = 0.6) -> Tuple[str, float]:
    """
    Match a header against a list of aliases.
    
    Args:
        header: Input header to match
        aliases: List of alias strings for a column
        threshold: Minimum similarity score (0-1)
        
    Returns:
        Tuple of (best_matching_alias, similarity_score)
    """
    return fuzzy_match_column(header, aliases, threshold)


def batch_fuzzy_match(headers: List[str], target_columns: List[str], threshold: float = 0.6) -> List[Tuple[str, str, float]]:
    """
    Perform fuzzy matching for multiple headers against target columns.
    
    Args:
        headers: List of input headers to match
        target_columns: List of possible target columns
        threshold: Minimum similarity score (0-1)
        
    Returns:
        List of tuples (header, best_match, similarity_score) for matches above threshold
    """
    results = []
    for header in headers:
        match, score = fuzzy_match_column(header, target_columns, threshold)
        if score >= threshold:
            results.append((header, match, score))
    return results
