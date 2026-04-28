"""
Core engine orchestrator for the mapper engine.
Refactored from UniversalColumnMapper class.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..mappers.detection import (
    flatten_multiindex_headers,
    detect_columns,
    extract_categorical_choices,
    rename_dataframe_columns,
)
from ..utils.columns import get_column_bounds

# Import hierarchical logging functions from core_engine and utility_engine
from utility_engine.console import status_print, debug_print
from core_engine.logging import log_error


from core_engine.context import PipelineContext
from core_engine.base import BaseEngine

class ColumnMapperEngine(BaseEngine):
    """
    Column mapper engine with fuzzy matching and schema-driven validation.
    Refactored from UniversalColumnMapper class.
    """
    
    def __init__(self, context: PipelineContext):
        """
        Initialize column mapper engine.
        """
        super().__init__(context)
        # Fallback to schema property if resolved_schema is not yet populated
        self.resolved_schema = self.context.state.resolved_schema
    
    def detect_columns(self, headers: List[Any], threshold: float = 0.6) -> Dict[str, Any]:
        """
        Detect and map input headers to schema columns.
        
        Args:
            headers: List of input headers (may contain tuples from MultiIndex)
            threshold: Minimum similarity score for matching
            
        Returns:
            Dictionary with detected_columns, unmatched_headers, missing_required, etc.
        """
        if not self.resolved_schema:
            error_msg = "No schema loaded. Call load_main_schema() first."
            # Record error in context
            if hasattr(self.context, 'add_system_error'):
                self.context.add_system_error(
                    code="S-C-M-0101",
                    message=error_msg,
                    details="Schema must be loaded before column mapping can be performed",
                    engine="mapper_engine",
                    phase="column_detection",
                    severity="critical",
                    fatal=True
                )
            raise ValueError(error_msg)
        
        # Flatten tuple headers
        flattened_headers = flatten_multiindex_headers(headers)
        
        # Support new top-level 'columns' key and legacy 'enhanced_schema.columns'
        _schema_root = self.resolved_schema if 'columns' in self.resolved_schema else self.resolved_schema.get('enhanced_schema', {})
        columns = _schema_root.get('columns', {})
        
        # Detect columns using the mapper module
        result = detect_columns(flattened_headers, columns, threshold)
        
        # Add schema choices for categorical columns
        extract_categorical_choices(result['detected_columns'], self.resolved_schema)
        
        return result
    
    def rename_dataframe_columns(self, df: Any, mapping_result: Dict) -> Any:
        """
        Rename DataFrame columns based on detected mapping.
        
        Args:
            df: Input DataFrame with original column names
            mapping_result: Result from detect_columns() method
            
        Returns:
            DataFrame with columns renamed to schema names
        """
        return rename_dataframe_columns(df, mapping_result)
    
    def get_column_bounds(self, data: Any, mapping_result: Dict) -> Dict[str, Any]:
        """
        Get non-null bounds for each detected column.
        
        Args:
            data: Input data (list of lists or DataFrame)
            mapping_result: Result from detect_columns() method
            
        Returns:
            Dictionary mapping column names to (start_row, end_row) tuples
        """
        detected_columns = mapping_result.get('detected_columns', {})
        return get_column_bounds(data, detected_columns)
    
    def map_dataframe(self, df: Optional[Any] = None, threshold: float = 0.6) -> Dict[str, Any]:
        """
        Complete pipeline: detect columns and rename DataFrame.
        
        Args:
            df: Input DataFrame (optional if context.data.df_raw is set)
            threshold: Minimum similarity score for matching
            
        Returns:
            Dictionary with mapping_result and renamed_df
        """
        if df is None:
            df = self.context.data.df_raw
            if df is None:
                error_msg = "No input DataFrame provided in context.data.df_raw."
                # Record error in context
                if hasattr(self.context, 'add_system_error'):
                    self.context.add_system_error(
                        code="S-C-M-0102",
                        message=error_msg,
                        details="DataFrame must be provided either as parameter or in context.data.df_raw",
                        engine="mapper_engine",
                        phase="dataframe_mapping",
                        severity="critical",
                        fatal=True
                    )
                raise ValueError(error_msg)
                
        # Ensure resolved_schema is up to date from context if modified
        if not self.resolved_schema and self.context.state.resolved_schema:
            self.resolved_schema = self.context.state.resolved_schema
            
        # Get headers from DataFrame
        headers = df.columns.tolist()
        
        # Detect columns
        mapping_result = self.detect_columns(headers, threshold)
        
        # Rename DataFrame
        renamed_df = self.rename_dataframe_columns(df, mapping_result)
        
        # Store in context
        self.context.state.mapping_result = mapping_result
        self.context.data.df_mapped = renamed_df
        
        return {
            'mapping_result': mapping_result,
            'renamed_df': renamed_df,
            'original_headers': headers
        }
