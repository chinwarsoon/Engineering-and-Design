#!/usr/bin/env python3
"""
Universal Document Processor
Implements schema-driven calculations, null handling, and data processing for universal document processing.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationEngine:
    """Handles schema-driven calculations and null handling."""
    
    def __init__(self, schema_data: Dict):
        """
        Initialize calculation engine with schema data.
        
        Args:
            schema_data: Resolved schema dictionary with column definitions
        """
        self.schema_data = schema_data
        self.columns = schema_data.get('enhanced_schema', {}).get('columns', {})
        
    def apply_null_handling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply null handling rules based on schema definitions.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with null handling applied
        """
        df_processed = df.copy()
        
        for column_name, column_def in self.columns.items():
            if column_name not in df_processed.columns:
                continue
                
            null_handling = column_def.get('null_handling', {})
            strategy = null_handling.get('strategy')
            
            if strategy == 'forward_fill':
                df_processed = self._apply_forward_fill(df_processed, column_name, null_handling)
            elif strategy == 'copy_from':
                df_processed = self._apply_copy_from(df_processed, column_name, null_handling)
            elif strategy == 'calculate_if_null':
                df_processed = self._apply_calculate_if_null(df_processed, column_name, null_handling)
            elif strategy == 'default_value':
                df_processed = self._apply_default_value(df_processed, column_name, null_handling)
            elif strategy == 'leave_null':
                # Leave null values as-is
                pass
            elif strategy == 'lookup_if_null':
                df_processed = self._apply_lookup_if_null(df_processed, column_name, null_handling)
        
        return df_processed
    
    def _apply_forward_fill(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply forward fill strategy."""
        group_by = null_handling.get('group_by', [])
        fill_value = null_handling.get('fill_value', 'NA')
        na_fallback = null_handling.get('na_fallback', False)
        formatting = null_handling.get('formatting', {})
        zero_pad = formatting.get('zero_pad')
        
        if group_by:
            # Group by specified columns and forward fill within groups
            # Convert group_by columns to string to avoid type comparison issues
            df_copy = df.copy()
            for col in group_by:
                if col in df_copy.columns:
                    df_copy[col] = df_copy[col].astype(str)
            
            # Sort and forward fill within groups
            df_sorted = df_copy.sort_values(group_by)
            df_sorted[column_name] = df_sorted.groupby(group_by)[column_name].ffill()
            
            # Update original dataframe with filled values
            df[column_name] = df_sorted[column_name].reindex(df.index)
        else:
            # Simple forward fill
            df[column_name] = df[column_name].fillna(fill_value)
        
        if na_fallback:
            # Replace remaining NaN with 'NA' if fill_value was NaN
            df[column_name] = df[column_name].fillna('NA')
        
        # Apply zero-padding formatting if specified
        if zero_pad:
            try:
                # Convert to numeric, then format with zero padding
                df[column_name] = df[column_name].apply(
                    lambda x: str(int(float(x))).zfill(zero_pad) if pd.notna(x) and x != 'NA' else x
                )
                logger.info(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
            except Exception as e:
                logger.warning(f"Could not apply zero-padding for {column_name}: {e}")
        
        logger.info(f"Applied forward fill for {column_name}: strategy={null_handling.get('strategy')}, group_by={group_by}")
        return df
    
    def _apply_copy_from(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply copy from strategy."""
        source_column = null_handling.get('source_column')
        fallback_value = null_handling.get('fallback_value', 'NA')
        
        # Copy from source column where target is null
        mask = df[column_name].isna()
        df.loc[mask, column_name] = df.loc[mask, source_column]
        
        # Apply fallback for remaining null values
        df[column_name] = df[column_name].fillna(fallback_value)
        
        logger.info(f"Applied copy from for {column_name}: source={source_column}, fallback={fallback_value}")
        return df
    
    def _apply_calculate_if_null(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply calculate if null strategy."""
        calculation = null_handling.get('calculation', {})
        calc_type = calculation.get('type')
        method = calculation.get('method')
        
        if calc_type == 'date_calculation' and method == 'add_working_days':
            df = self._calculate_working_days(df, column_name, calculation)
        elif calc_type == 'conditional' and method == 'status_based':
            df = self._apply_conditional_calculation(df, column_name, calculation)
        else:
            logger.warning(f"Unsupported calculation type: {calc_type} for {column_name}")
        
        return df
    
    def _calculate_working_days(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Calculate working days between dates."""
        source_column = calculation.get('source_column')
        parameters = calculation.get('parameters', {})
        days = parameters.get('days', 14)
        
        # Convert date columns to datetime
        if source_column in df.columns:
            df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
        
        # Calculate target date
        if column_name in df.columns:
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
        
        # Add working days
        mask = df[column_name].notna() & df[source_column].notna()
        df.loc[mask, column_name] = df.loc[mask, source_column] + pd.Timedelta(days=days)
        
        logger.info(f"Calculated working days for {column_name}: +{days} days from {source_column}")
        return df
    
    def _apply_conditional_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply conditional calculation based on another column."""
        source_column = calculation.get('source_column')
        mapping = calculation.get('mapping', {})
        default_value = calculation.get('default', False)
        
        if source_column in df.columns and column_name in df.columns:
            mask = df[column_name].isna()
            for value, result in mapping.items():
                df.loc[mask & (df[source_column] == value), column_name] = result
            
            # Apply default for remaining null values
            df[column_name] = df[column_name].fillna(default_value)
        
        logger.info(f"Applied conditional calculation for {column_name}: based on {source_column}")
        return df
    
    def _apply_default_value(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply default value strategy."""
        default_value = null_handling.get('default_value', null_handling.get('default', 'NA'))
        text_replacements = null_handling.get('text_replacements', {})
        type_conversion = null_handling.get('type_conversion')
        
        # Apply text replacements first
        if text_replacements and column_name in df.columns:
            for old_text, new_text in text_replacements.items():
                df[column_name] = df[column_name].replace(old_text, new_text)
                # Also replace in string representation
                df[column_name] = df[column_name].astype(str).str.replace(old_text, new_text, regex=False)
        
        # Apply type conversion if specified
        if type_conversion == 'string' and column_name in df.columns:
            df[column_name] = df[column_name].astype(str)
            # Replace 'nan' string with actual NaN for proper null handling
            df[column_name] = df[column_name].replace('nan', pd.NA)
            df[column_name] = df[column_name].replace('NaN', pd.NA)
        
        # Fill null values with default
        if column_name in df.columns:
            df[column_name] = df[column_name].fillna(default_value)
        
        logger.info(f"Applied default value for {column_name}: {default_value}")
        return df
    
    def _apply_lookup_if_null(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply lookup strategy for null values."""
        calculation = null_handling.get('calculation', {})
        lookup_key = calculation.get('lookup_key')
        source_column = calculation.get('source_column')
        fallback_value = calculation.get('fallback_value', 'NA')
        
        if lookup_key and source_column and column_name in df.columns:
            mask = df[column_name].isna()
            
            # Group by lookup key and find first non-null value
            grouped = df.groupby(lookup_key, dropna=False)
            for key, group in grouped:
                # Get first non-null source value in group
                non_null_mask = group[source_column].notna()
                if non_null_mask.any():
                    first_value = group.loc[non_null_mask.idxmax(), source_column]
                    df.loc[mask & (df[lookup_key] == key), column_name] = first_value
            
            # Apply fallback for remaining null values
            df[column_name] = df[column_name].fillna(fallback_value)
        
        logger.info(f"Applied lookup if null for {column_name}: lookup_key={lookup_key}")
        return df
    
    def apply_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all calculated columns based on schema definitions.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with all calculations applied
        """
        df_calculated = df.copy()
        
        for column_name, column_def in self.columns.items():
            if column_def.get('is_calculated', False):
                continue
                
            calculation = column_def.get('calculation', {})
            calc_type = calculation.get('type')
            method = calculation.get('method')
            
            if calc_type == 'mapping' and method == 'status_to_code':
                df_calculated = self._apply_mapping_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'count':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'min':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'max':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'concatenate_unique':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'copy' and method == 'direct':
                df_calculated = self._apply_copy_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'conditional' and method == 'current_row':
                df_calculated = self._apply_current_row_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'date_calculation':
                df_calculated = self._apply_date_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'composite' and method == 'build_document_id':
                df_calculated = self._apply_composite_calculation(df_calculated, column_name, calculation)
            else:
                logger.warning(f"Unsupported calculation type: {calc_type} for {column_name}")
        
        return df_calculated
    
    def _apply_mapping_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply mapping calculation."""
        source_column = calculation.get('source_column')
        mapping = calculation.get('mapping', {})
        default = calculation.get('default', 'PEN')
        
        if source_column in df.columns and column_name in df.columns:
            df[column_name] = df[source_column].map(mapping).fillna(default)
        
        logger.info(f"Applied mapping calculation for {column_name}: {len(mapping)} mappings")
        return df
    
    def _apply_aggregate_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply aggregate calculation."""
        source_column = calculation.get('source_column')
        method = calculation.get('method')
        group_by = calculation.get('group_by', [])
        sort_by = calculation.get('sort_by', [])
        separator = calculation.get('separator', ', ')
        
        if source_column in df.columns and column_name in df.columns and group_by:
            grouped = df.groupby(group_by, dropna=False)
            
            if method == 'count':
                df[column_name] = grouped[source_column].transform('count')
            elif method in ['min', 'max']:
                df[column_name] = grouped[source_column].transform(method)
            elif method == 'concatenate_unique':
                if sort_by:
                    df_sorted = df.sort_values(sort_by)
                    grouped = df_sorted.groupby(group_by, dropna=False)
                
                def concat_unique(x):
                    unique_vals = x[source_column].dropna().unique()
                    return separator.join(str(val) for val in unique_vals if pd.notna(val))
                
                df[column_name] = grouped.apply(concat_unique)
        
        logger.info(f"Applied aggregate calculation for {column_name}: method={method}")
        return df
    
    def _apply_copy_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply direct copy calculation."""
        source_column = calculation.get('source_column')
        
        if source_column in df.columns and column_name in df.columns:
            df[column_name] = df[source_column]
        
        logger.info(f"Applied copy calculation for {column_name}: source={source_column}")
        return df
    
    def _apply_current_row_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply current row calculation."""
        source_column = calculation.get('source_column')
        condition = calculation.get('condition')
        
        if source_column in df.columns and column_name in df.columns:
            if condition == 'is_current_submission':
                # Mark current row values (simplified for demo)
                df[column_name] = df[source_column]
            else:
                df[column_name] = df[source_column]
        
        logger.info(f"Applied current row calculation for {column_name}: condition={condition}")
        return df
    
    def _apply_date_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply date calculation."""
        method = calculation.get('method')
        parameters = calculation.get('parameters', {})
        
        if method == 'add_working_days':
            df = self._calculate_working_days(df, column_name, calculation)
        elif method == 'date_difference':
            df = self._calculate_date_difference(df, column_name, calculation)
        
        logger.info(f"Applied date calculation for {column_name}: method={method}")
        return df
    
    def _calculate_date_difference(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Calculate difference between two dates."""
        source_column = calculation.get('source_column')
        target_column = calculation.get('target_column', column_name)
        
        if source_column in df.columns and target_column in df.columns:
            # Convert to datetime
            df[source_column] = pd.to_datetime(df[source_column], errors='coerce')
            df[target_column] = pd.to_datetime(df[target_column], errors='coerce')
            
            # Calculate difference in days
            diff = (df[target_column] - df[source_column]).dt.days
            df[column_name] = diff
        
        logger.info(f"Calculated date difference for {column_name}: {source_column} to {target_column}")
        return df
    
    def _apply_composite_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply composite calculation."""
        source_columns = calculation.get('source_columns', [])
        format_string = calculation.get('format', '{Document_ID}')
        fallback_source = calculation.get('fallback_source')
        
        if all(col in df.columns for col in source_columns) and column_name in df.columns:
            # Build composite string
            composite_values = {}
            for col in source_columns:
                if col in df.columns:
                    composite_values[col] = df[col].fillna('NA')
            
            # Apply format string
            try:
                df[column_name] = format_string.format(**composite_values)
            except KeyError as e:
                if fallback_source and fallback_source in df.columns:
                    df[column_name] = df[fallback_source]
                else:
                    df[column_name] = 'UNKNOWN-COMPOSITE'
        
        logger.info(f"Applied composite calculation for {column_name}: {len(source_columns)} sources")
        return df


class UniversalDocumentProcessor:
    """Universal document processor with schema-driven calculations."""
    
    def __init__(self, schema_file: str = None):
        """
        Initialize universal document processor.
        
        Args:
            schema_file: Path to enhanced schema file
        """
        self.schema_file = schema_file
        self.schema_data = {}
        self.calculation_engine = None
        
        if schema_file:
            self.load_schema()
    
    def load_schema(self):
        """Load and process schema file."""
        if self.schema_file is None:
            raise ValueError("Schema file path not set. Use UniversalDocumentProcessor(schema_file='path/to/schema.json')")
        
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                self.schema_data = json.load(f)
                logger.info(f"Loaded schema: {self.schema_file}")
                
                # Initialize calculation engine
                self.calculation_engine = CalculationEngine(self.schema_data)
                
        except Exception as e:
            logger.error(f"Error loading schema {e}")
            raise
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data according to schema rules.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Processed DataFrame with all calculations applied
        """
        if self.calculation_engine is None:
            raise ValueError("Schema not loaded. Call load_schema() first.")
        
        logger.info(f"Processing data with {len(df)} rows and {len(df.columns)} columns")
        
        # Step 1: Apply null handling
        df_processed = self.calculation_engine.apply_null_handling(df)
        
        # Step 2: Apply calculations
        df_calculated = self.calculation_engine.apply_calculations(df_processed)
        
        # Step 3: Apply validation
        df_validated = self._apply_validation(df_calculated)
        
        logger.info(f"Data processing complete: {len(df_validated)} rows")
        return df_validated
    
    def _apply_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply validation rules from schema."""
        enhanced_schema = self.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        
        df_validated = df.copy()
        
        for column_name, column_def in columns.items():
            if column_name not in df_validated.columns:
                continue
                
            validation = column_def.get('validation', {})
            
            # Apply pattern validation
            if 'pattern' in validation:
                pattern = validation['pattern']
                # Convert to string for pattern matching
                df_str = df_validated[column_name].astype(str)
                mask = ~df_str.str.match(pattern)
                invalid_count = mask.sum()
                if invalid_count > 0:
                    logger.warning(f"Pattern validation failed for {column_name}: {invalid_count} invalid values")
            
            # Apply min/max length validation
            if 'min_length' in validation:
                min_len = validation['min_length']
                df_str = df_validated[column_name].astype(str)
                mask = df_str.str.len() < min_len
                invalid_count = mask.sum()
                if invalid_count > 0:
                    logger.warning(f"Min length validation failed for {column_name}: {invalid_count} values too short")
            
            # Apply allowed values validation
            if 'allowed_values' in validation:
                allowed = validation['allowed_values']
                mask = ~df_validated[column_name].isin(allowed)
                invalid_count = mask.sum()
                if invalid_count > 0:
                    logger.warning(f"Allowed values validation failed for {column_name}: {invalid_count} invalid values")
        
        return df_validated


def main():
    """Example usage of UniversalDocumentProcessor."""
    # Create sample data
    sample_data = {
        'Document_ID': ['DOC-001', 'DOC-001', 'DOC-002', 'DOC-003'],
        'Document_Title': ['Foundation Plan', 'Foundation Plan', 'Structural Design', 'MEP Design'],
        'Document_Revision': ['0', '1', '2', '1'],
        'Department': ['Civil', 'Civil', 'Structural', 'NA'],
        'Discipline': ['Civil', 'Structural', 'MEP', 'NA'],
        'Project_Code': ['CESL-22120', 'CESL-22120', 'NA', 'CESL-22120'],
        'Document_Type': ['Drawing', 'Drawing', 'Specification', 'NA'],
        'Submission_Date': ['2024-01-15', '2024-01-20', '2024-02-01', pd.NaT],
        'Review_Status': ['Approved', 'Rejected', 'Pending', 'Approved'],
        'Review_Return_Actual_Date': ['2024-01-25', pd.NaT, '2024-02-15', '2024-02-20']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Initialize processor with explicit schema path
    processor = UniversalDocumentProcessor()
    schema_path = Path(__file__).parent / "config" / "dcc_register_enhanced.json"
    processor.schema_file = str(schema_path)  # Convert to string
    processor.load_schema()
    
    # Process data
    result = processor.process_data(df)
    
    print("=== Universal Document Processing Results ===")
    print(f"Input rows: {len(df)}")
    print(f"Input columns: {len(df.columns)}")
    print(f"Output rows: {len(result)}")
    print(f"Output columns: {len(result.columns)}")
    
    print("\n=== Sample Processed Data ===")
    print(result.head(10).to_string())
    
    print("\n=== Processing Summary ===")
    for col in result.columns:
        null_count = result[col].isna().sum()
        print(f"{col}: {len(result)} rows, {null_count} null values")


if __name__ == "__main__":
    main()
