"""
Error Aggregator Module

Provides functions for:
- Collecting errors per row
- Generating phase-level summaries
- Deduplicating errors
- Formatting errors for pipeline output
"""

from typing import List, Dict, Any, Optional, Set
import pandas as pd
from .detectors.base import DetectionResult

class ErrorAggregator:
    """
    Aggregates errors from multiple detectors and phases.
    """
    
    def __init__(self):
        self._errors: List[DetectionResult] = []
        
    def add_errors(self, errors: List[DetectionResult]) -> None:
        """Add multiple errors to aggregation."""
        if errors:
            self._errors.extend(errors)
        
    def add_error(self, error: DetectionResult) -> None:
        """Add a single error to aggregation."""
        if error:
            self._errors.append(error)
        
    def get_all_errors(self) -> List[DetectionResult]:
        """Get all aggregated errors."""
        return self._errors.copy()
        
    def aggregate_row_errors(self) -> Dict[int, List[DetectionResult]]:
        """
        Groups errors by row index.
        
        Returns:
            Dictionary mapping row index to list of DetectionResult objects
        """
        row_errors = {}
        for error in self._errors:
            if error.row is not None:
                if error.row not in row_errors:
                    row_errors[error.row] = []
                row_errors[error.row].append(error)
        return row_errors
        
    def aggregate_phase_errors(self) -> Dict[str, List[DetectionResult]]:
        """
        Groups errors by processing phase.
        
        Returns:
            Dictionary mapping phase name to list of DetectionResult objects
        """
        phase_errors = {}
        for error in self._errors:
            phase = error.context.get("phase", "Unknown")
            if phase not in phase_errors:
                phase_errors[phase] = []
            phase_errors[phase].append(error)
        return phase_errors
        
    def deduplicate_errors(self) -> List[DetectionResult]:
        """
        Removes duplicate errors (same row, code, column).
        
        Returns:
            List of unique DetectionResult objects
        """
        seen = set()
        unique_errors = []
        for error in self._errors:
            # Create a unique key for the error
            # If row is None, we use -1 as placeholder
            row_key = error.row if error.row is not None else -1
            key = (row_key, error.error_code, error.column)
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)
        return unique_errors
        
    def format_validation_errors_column(self, num_rows: int) -> pd.Series:
        """
        Formats errors for the 'Validation_Errors' column.
        
        Args:
            num_rows: Total number of rows in the dataframe
            
        Returns:
            Pandas Series of formatted error strings
        """
        row_errors = self.aggregate_row_errors()
        error_strings = []
        
        for i in range(num_rows):
            if i in row_errors:
                # Deduplicate within the row
                row_results = row_errors[i]
                unique_row_errors = []
                seen_row = set()
                for e in row_results:
                    # Within a row, we only care about code and column uniqueness
                    key = (e.error_code, e.column)
                    if key not in seen_row:
                        seen_row.add(key)
                        unique_row_errors.append(e)
                
                # Format: [CODE] Message (Column)
                row_error_msgs = []
                for e in unique_row_errors:
                    msg = f"[{e.error_code}] {e.message}"
                    if e.column:
                        msg += f" ({e.column})"
                    row_error_msgs.append(msg)
                
                row_str = "; ".join(row_error_msgs)
                error_strings.append(row_str)
            else:
                error_strings.append("")
                
        return pd.Series(error_strings)
        
    def get_structured_summary(self) -> Dict[str, Any]:
        """
        Generates a structured summary for logging or reporting.
        """
        unique_errors = self.deduplicate_errors()
        severities = {}
        layers = {}
        codes = {}
        
        for error in unique_errors:
            severities[error.severity] = severities.get(error.severity, 0) + 1
            layer = error.layer if error.layer else "Unknown"
            layers[layer] = layers.get(layer, 0) + 1
            codes[error.error_code] = codes.get(error.error_code, 0) + 1
            
        return {
            "total_unique_errors": len(unique_errors),
            "by_severity": severities,
            "by_layer": layers,
            "by_code": codes,
            "has_critical": severities.get("CRITICAL", 0) > 0 or severities.get("FATAL", 0) > 0
        }

def aggregate_row_errors(errors: List[DetectionResult]) -> Dict[int, List[DetectionResult]]:
    """Helper function to aggregate row errors."""
    agg = ErrorAggregator()
    agg.add_errors(errors)
    return agg.aggregate_row_errors()

def aggregate_phase_errors(errors: List[DetectionResult]) -> Dict[str, List[DetectionResult]]:
    """Helper function to aggregate phase errors."""
    agg = ErrorAggregator()
    agg.add_errors(errors)
    return agg.aggregate_phase_errors()
