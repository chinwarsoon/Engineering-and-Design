"""
Core engine orchestrator for the mapper engine.
Refactored from UniversalColumnMapper class.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from dcc.workflow.mapper_engine.engine.mappers.detection import (
    flatten_multiindex_headers,
    detect_columns,
    extract_categorical_choices,
    rename_dataframe_columns,
)
from dcc.workflow.mapper_engine.engine.utils.columns import get_column_bounds

logger = logging.getLogger(__name__)


class ColumnMapperEngine:
    """
    Column mapper engine with fuzzy matching and schema-driven validation.
    Refactored from UniversalColumnMapper class.
    """
    
    def __init__(self, schema_loader: Any = None, schema_file: str = None):
        """
        Initialize column mapper engine.
        
        Args:
            schema_loader: Schema loader instance (optional)
            schema_file: Path to main schema file (optional)
        """
        self.schema_loader = schema_loader
        self.schema_file = schema_file
        self.main_schema = {}
        self.resolved_schema = {}
        
        if schema_file and schema_loader:
            self.load_main_schema(schema_file, schema_loader)
    
    def load_main_schema(self, schema_file: str, schema_loader: Any):
        """
        Load main schema file.
        
        Args:
            schema_file: Path to main schema file
            schema_loader: Schema loader instance with load_json_file and resolve_schema_dependencies methods
        """
        try:
            self.schema_loader = schema_loader
            self.schema_loader.set_main_schema_path(schema_file)
            self.main_schema = self.schema_loader.load_json_file(schema_file)
            self.resolved_schema = self.schema_loader.resolve_schema_dependencies(self.main_schema)
            logger.info("Schema dependencies resolved")
            
        except Exception as e:
            logger.error(f"Error loading main schema {schema_file}: {e}")
            raise
    
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
            raise ValueError("No schema loaded. Call load_main_schema() first.")
        
        # Flatten tuple headers
        flattened_headers = flatten_multiindex_headers(headers)
        
        enhanced_schema = self.resolved_schema.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        
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
    
    def map_dataframe(self, df: Any, threshold: float = 0.6) -> Dict[str, Any]:
        """
        Complete pipeline: detect columns and rename DataFrame.
        
        Args:
            df: Input DataFrame
            threshold: Minimum similarity score for matching
            
        Returns:
            Dictionary with mapping_result and renamed_df
        """
        # Get headers from DataFrame
        headers = df.columns.tolist()
        
        # Detect columns
        mapping_result = self.detect_columns(headers, threshold)
        
        # Rename DataFrame
        renamed_df = self.rename_dataframe_columns(df, mapping_result)
        
        return {
            'mapping_result': mapping_result,
            'renamed_df': renamed_df,
            'original_headers': headers
        }
