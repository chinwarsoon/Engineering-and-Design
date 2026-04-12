"""
Document_ID Affix Extractor Module

Extracts affixes/suffixes from Document_ID values.
Affixes appear after the standard 5-segment format and may start with 
'_', '-', or other separator characters.

Examples:
- '131242-WSD11-CL-P-0009_ST607' -> ('131242-WSD11-CL-P-0009', '_ST607')
- 'PRJ-FAC-DWG-ARC-0001' -> ('PRJ-FAC-DWG-ARC-0001', '')
- 'INVALID-ID_ST607' -> ('INVALID-ID', '_ST607')  # Still extracts affix even if base invalid

Related to Issue #16: Document_ID affix handling
"""

import re
from typing import Tuple, Optional


def extract_document_id_affixes(
    document_id: str,
    delimiter: str = '-',
    sequence_length: int = 4
) -> Tuple[str, str]:
    """
    Extract affixes from Document_ID.
    
    Algorithm:
    1. Split Document_ID by delimiter (from schema)
    2. Extract Document_Sequence_Number from last segment (first N chars)
    3. Remaining chars in last segment = affix
    4. Return base Document_ID and affix string
    
    Args:
        document_id: Raw Document_ID value (may contain affixes)
        delimiter: Segment separator from schema (default: "-")
        sequence_length: Length of Document_Sequence_Number from schema (default: 4)
        
    Returns:
        Tuple of (base_document_id, affix)
        - base_document_id: Document_ID without affix (validated in Phase 2.5)
        - affix: Extracted affix string or empty string "" if none found
        
    Examples:
        >>> extract_document_id_affixes("131242-WSD11-CL-P-0009_ST607")
        ('131242-WSD11-CL-P-0009', '_ST607')
        
        >>> extract_document_id_affixes("131242-WSD11-CL-P-0009")
        ('131242-WSD11-CL-P-0009', '')
        
        >>> extract_document_id_affixes("131242-WSD11-CL-P-0009-V1")
        ('131242-WSD11-CL-P-0009', '-V1')
        
        >>> extract_document_id_affixes("")
        ('', '')
    """
    if not document_id or not isinstance(document_id, str):
        return ('', '')
    
    document_id = document_id.strip()
    
    if not document_id:
        return ('', '')
    
    # Delimiter-based extraction logic
    # Document_ID format: {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}<affix>
    # Delimiter: from schema (default: "-")
    # Document_Sequence_Number: from schema (default: 4 digits)
    # Affixes appear after the sequence number in the last segment
    
    segments = document_id.split(delimiter)
    
    # Must have at least 5 segments for standard Document_ID format
    if len(segments) >= 5:
        # First 4 segments form the base part (Project, Facility, Type, Discipline)
        base_segments = segments[0:4]
        
        # Last segment contains Document_Sequence_Number + optional affix
        last_segment = segments[-1]  # Use last segment to handle cases with extra delimiters
        
        # Document_Sequence_Number length from schema (default: 4 digits)
        # Extract first N chars as sequence number, remaining as affix
        if len(last_segment) >= sequence_length:
            sequence_number = last_segment[0:sequence_length]
            affix = last_segment[sequence_length:]  # Everything after sequence number
            
            # Reconstruct base: first 4 segments + sequence number
            base = delimiter.join(base_segments) + delimiter + sequence_number
            return (base, affix)
    
    # Fallback: if not enough segments, try to find separator and extract
    # Common separators: '_', '-', ' ', '.'
    separator_pattern = re.compile(r'[_\-\s.](?!.*[_\-\s.])')
    last_sep_match = separator_pattern.search(document_id)
    
    if last_sep_match:
        last_sep_pos = last_sep_match.start()
        base = document_id[:last_sep_pos]
        affix = document_id[last_sep_pos:]
        return (base, affix)
    
    # No separator found - return as-is with no affix
    return (document_id, '')


def has_affix(document_id: str) -> bool:
    """
    Check if Document_ID contains an affix.
    
    Args:
        document_id: Document_ID value to check
        
    Returns:
        True if affix detected, False otherwise
    """
    _, affix = extract_document_id_affixes(document_id)
    return bool(affix)


def strip_affix(document_id: str) -> str:
    """
    Remove affix from Document_ID, returning base only.
    
    Args:
        document_id: Document_ID value (may contain affix)
        
    Returns:
        Base Document_ID without affix
    """
    base, _ = extract_document_id_affixes(document_id)
    return base


# For backward compatibility and pandas DataFrame operations
def extract_affixes_series(document_ids):
    """
    Vectorized affix extraction for pandas Series.
    
    Args:
        document_ids: pandas Series or list of Document_ID values
        
    Returns:
        Tuple of (base_series, affix_series)
    """
    try:
        import pandas as pd
        
        if isinstance(document_ids, pd.Series):
            results = document_ids.apply(extract_document_id_affixes)
            base_series = results.apply(lambda x: x[0])
            affix_series = results.apply(lambda x: x[1])
            return (base_series, affix_series)
    except ImportError:
        pass
    
    # Fallback for list input
    results = [extract_document_id_affixes(str(did)) for did in document_ids]
    bases = [r[0] for r in results]
    affixes = [r[1] for r in results]
    return (bases, affixes)
