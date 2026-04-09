"""
Column bounds and data analysis utilities.
Extracted from UniversalColumnMapper get_column_bounds method.
"""

import logging
from typing import Dict, Tuple, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def get_column_bounds(data: Any, detected_columns: Dict[str, Dict]) -> Dict[str, Tuple[int, int]]:
    """
    Get non-null bounds for each detected column.
    
    Args:
        data: Input data (list of lists or DataFrame)
        detected_columns: Dictionary of detected column mappings
        
    Returns:
        Dictionary mapping column names to (start_row, end_row) tuples
    """
    bounds = {}
    
    for header, mapping in detected_columns.items():
        column_name = mapping['mapped_column']
        
        # Find the column index in data
        col_index = None
        if hasattr(data, 'columns'):
            # Pandas DataFrame
            try:
                col_index = data.columns.get_loc(header)
            except KeyError:
                continue
        else:
            # List of lists - find header row
            if len(data) > 0 and isinstance(data[0], list):
                try:
                    col_index = data[0].index(header)
                except ValueError:
                    continue
        
        if col_index is not None:
            # Find non-null bounds
            start_row = None
            end_row = None
            
            for i, row in enumerate(data):
                value = row[col_index] if isinstance(row, list) else row.iloc[col_index]
                if pd.notna(value) and str(value).strip():
                    if start_row is None:
                        start_row = i
                    end_row = i
            
            if start_row is not None:
                bounds[column_name] = (start_row, end_row)
    
    return bounds


def analyze_column_coverage(bounds: Dict[str, Tuple[int, int]]) -> Dict[str, Any]:
    """
    Analyze column coverage statistics.
    
    Args:
        bounds: Dictionary mapping column names to (start_row, end_row) tuples
        
    Returns:
        Dictionary with coverage statistics
    """
    if not bounds:
        return {'total_columns': 0, 'total_data_rows': 0, 'average_coverage': 0}
    
    coverages = []
    max_end = 0
    
    for col_name, (start, end) in bounds.items():
        coverage = end - start + 1 if start is not None and end is not None else 0
        coverages.append(coverage)
        max_end = max(max_end, end if end is not None else 0)
    
    return {
        'total_columns': len(bounds),
        'total_data_rows': max_end + 1,
        'average_coverage': sum(coverages) / len(coverages) if coverages else 0,
        'max_coverage': max(coverages) if coverages else 0,
        'min_coverage': min(coverages) if coverages else 0
    }
