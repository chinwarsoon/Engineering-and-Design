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
from typing import Dict, List, Any, Optional, Set
import logging
import re
from schema_validation import SchemaLoader, validate_validation_status

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
        enhanced_schema = schema_data.get('enhanced_schema', {})
        raw_columns = enhanced_schema.get('columns', {})
        column_sequence = enhanced_schema.get('column_sequence', [])
        
        if column_sequence:
            # Reorder columns based on column_sequence, keeping only valid column definitions
            self.columns = {
                name: raw_columns[name] 
                for name in column_sequence 
                if name in raw_columns and isinstance(raw_columns[name], dict)
            }
            # Add any columns from raw_columns that are not in column_sequence
            for name, definition in raw_columns.items():
                if name not in self.columns and isinstance(definition, dict):
                    self.columns[name] = definition
        else:
            self.columns = {name: defn for name, defn in raw_columns.items() if isinstance(defn, dict)}
            
        self.calculation_order = self._resolve_calculation_order()

    def _print_processing_step(self, phase: str, column_name: str, detail: str):
        """Print user-visible progress for column processing order."""
        message = f"[{phase}] {column_name}: {detail}"
        print(message)
        logger.info(message)

    def _resolve_schema_reference(self, ref_config: Dict) -> any:
        """
        Resolve a schema reference to its actual value.
        
        Args:
            ref_config: Dictionary with 'schema', 'code', and 'field' keys
            
        Returns:
            Resolved value from the referenced schema, or None if not found
        """
        schema_name = ref_config.get('schema')
        code = ref_config.get('code')
        field = ref_config.get('field')
        
        if not all([schema_name, code, field]):
            logger.warning(f"Invalid schema reference: {ref_config}")
            return None
        
        # Load referenced schema data
        ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
        if not ref_schema_data:
            logger.warning(f"Referenced schema data not found: {schema_name}_data")
            return None
        
        # Find the entry with matching code
        data_section = ref_config.get('data_section', 'approval')
        entries = ref_schema_data.get(data_section, [])
        
        for entry in entries:
            if entry.get('code') == code:
                value = entry.get(field)
                if value is not None:
                    logger.debug(f"Resolved {schema_name} reference: code={code}, field={field} -> {value}")
                    return value
        
        logger.warning(f"Code '{code}' not found in {schema_name}.{data_section}")
        return None

    def _extract_column_dependencies(self, column_name: str, column_def: Dict) -> Set[str]:
        """Extract schema column dependencies for a calculated column."""
        dependencies = set()
        calculation = column_def.get('calculation', {})

        dependency_keys = [
            'dependencies',
            'source_columns',
            'group_by',
            'sort_by',
        ]
        scalar_keys = [
            'source_column',
            'target_column',
        ]

        for key in dependency_keys:
            value = calculation.get(key, [])
            if isinstance(value, list):
                dependencies.update(value)

        for key in scalar_keys:
            value = calculation.get(key)
            if isinstance(value, str):
                dependencies.add(value)

        # Self-references such as source_column == column_name are treated as
        # seed/input values rather than recursive calculation dependencies.
        dependencies.discard(column_name)

        return {dep for dep in dependencies if dep in self.columns}

    def _find_cycle_path(self, dependency_graph: Dict[str, Set[str]]) -> List[str]:
        """Return one cycle path if present, otherwise an empty list."""
        visiting = set()
        visited = set()
        stack: List[str] = []

        def dfs(node: str) -> List[str]:
            visiting.add(node)
            stack.append(node)

            for dep in dependency_graph.get(node, set()):
                if dep in visiting:
                    cycle_start = stack.index(dep)
                    return stack[cycle_start:] + [dep]
                if dep not in visited:
                    cycle = dfs(dep)
                    if cycle:
                        return cycle

            stack.pop()
            visiting.remove(node)
            visited.add(node)
            return []

        for node in dependency_graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle

        return []

    def _resolve_calculation_order(self) -> List[str]:
        """
        Validate that calculated columns can be processed in schema order.

        Raises:
            ValueError: If the schema introduces a circular dependency or
                requires a later schema column to be processed first
        """
        calculated_columns = [
            name for name, definition in self.columns.items()
            if definition.get('is_calculated', False)
        ]
        dependency_graph: Dict[str, Set[str]] = {
            name: {
                dep for dep in self._extract_column_dependencies(name, self.columns[name])
                if self.columns.get(dep, {}).get('is_calculated', False)
            }
            for name in calculated_columns
        }

        cycle = self._find_cycle_path(dependency_graph)
        if cycle:
            raise ValueError(
                "Circular calculated-column dependency detected: "
                + " -> ".join(cycle)
            )

        original_index = {name: idx for idx, name in enumerate(self.columns.keys())}
        schema_order_violations = []
        for column_name, deps in dependency_graph.items():
            later_dependencies = [
                dep for dep in deps
                if original_index.get(dep, -1) > original_index.get(column_name, -1)
            ]
            if later_dependencies:
                schema_order_violations.append(
                    f"{column_name} depends on later calculated columns {later_dependencies}"
                )

        if schema_order_violations:
            raise ValueError(
                "Schema column processing order violation detected. "
                "A column cannot depend on a later schema column. "
                + " | ".join(schema_order_violations)
            )

        logger.info(
            "Validated schema-order calculation sequence for %s calculated columns",
            len(calculated_columns)
        )
        return calculated_columns
        
    def apply_null_handling(self, df: pd.DataFrame, original_columns: set = None) -> pd.DataFrame:
        """
        Apply null handling rules based on schema definitions.
        
        Processing order follows self.columns which is ordered by column_sequence from schema.

        Args:
            df: Input DataFrame
            original_columns: Set of columns natively mapped via detection

        Returns:
            DataFrame with null handling applied
        """
        # CRITICAL: Reset DataFrame index to simple RangeIndex to prevent tuple corruption
        logger.info(f"[NULL_HANDLING] Entry - DataFrame index type: {type(df.index)}")
        if not isinstance(df.index, pd.RangeIndex):
            logger.warning(f"DataFrame index is {type(df.index)}, resetting to RangeIndex")
            logger.warning(f"Current index sample: {df.index[:3].tolist() if hasattr(df.index, 'tolist') else list(df.index)[:3]}")
            df = df.reset_index(drop=True)
            logger.info(f"Index reset to RangeIndex, new index sample: {df.index[:3].tolist()}")
        
        # CRITICAL: Ensure all columns are strings before any processing
        # This prevents tuple columns from propagating through copies
        if not all(isinstance(c, str) for c in df.columns):
            logger.warning("Flattening non-string columns in apply_null_handling before processing")
            df = df.copy()
            df.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_') 
                          for c in df.columns]
        
        logger.info(f"[NULL_HANDLING] Starting null handling with {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"[NULL_HANDLING] Column processing order (from schema column_sequence): {list(self.columns.keys())[:10]}...")

        df_processed = df.copy()
        
        # Verify index is still RangeIndex after copy
        if not isinstance(df_processed.index, pd.RangeIndex):
            logger.warning("Index corrupted after copy, resetting again")
            df_processed = df_processed.reset_index(drop=True)
        
        # Verify columns are still strings after copy
        if not all(isinstance(c, str) for c in df_processed.columns):
            logger.error("Columns became tuples during copy! Re-flattening.")
            df_processed.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_') 
                                    for c in df_processed.columns]
        
        if original_columns is None:
            original_columns = set(df_processed.columns)

        null_columns = [
            column_name for column_name, column_def in self.columns.items()
            if column_name in df_processed.columns and column_def.get('null_handling', {}).get('strategy')
        ]
        print(f"[NULL_HANDLING] Processing sequence: {null_columns}")
        
        for column_name, column_def in self.columns.items():
            if column_name not in df_processed.columns:
                continue
                
            null_handling = column_def.get('null_handling', {})
            strategy = null_handling.get('strategy')
            if strategy:
                self._print_processing_step('NULL_HANDLING', column_name, f"strategy={strategy}")
            
            if strategy == 'forward_fill':
                df_processed = self._apply_forward_fill(df_processed, column_name, null_handling)
            elif strategy == 'multi_level_forward_fill':
                df_processed = self._apply_multi_level_forward_fill(df_processed, column_name, null_handling)
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

        # DEBUG: Log entry into function
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - column_name='{column_name}' (type={type(column_name)})")
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - df.shape={df.shape}")
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - df.columns[:10]={list(df.columns)[:10]}")
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - df.index type={type(df.index)}")
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - df.index[:5]={df.index[:5].tolist()}")
        logger.info(f"[DEBUG] _apply_forward_fill ENTRY - group_by={group_by}")

        # Defensive check: ensure column_name is a string, not a tuple
        if not isinstance(column_name, str):
            logger.error(f"Invalid column_name type: {type(column_name)} - {column_name}")
            column_name = str(column_name) if isinstance(column_name, tuple) else column_name

        # Resolve fill_value from schema reference if specified
        fill_value_ref = null_handling.get('fill_value_reference')
        if fill_value_ref:
            fill_value = self._resolve_schema_reference(fill_value_ref)
            if fill_value is None:
                fill_value = null_handling.get('fill_value', 'NA')
        else:
            fill_value = null_handling.get('fill_value', 'NA')

        na_fallback = null_handling.get('na_fallback', False)
        formatting = null_handling.get('formatting', {})
        zero_pad = formatting.get('zero_pad')

        # Validate that column exists in DataFrame
        if column_name not in df.columns:
            logger.error(f"Column '{column_name}' not found in DataFrame. Available columns: {list(df.columns)[:10]}...")
            return df

        if group_by:
            # Validate group_by columns exist
            valid_group_by = [col for col in group_by if col in df.columns]
            if not valid_group_by:
                logger.warning(f"None of the group_by columns {group_by} found in DataFrame. Skipping forward fill for {column_name}.")
                return df
            
            # Group by specified columns and forward fill within groups
            # Do NOT sort - preserve original row order for correct forward fill
            df_copy = df.copy()
            
            logger.info(f"[DEBUG] After copy - df_copy.index type={type(df_copy.index)}")
            logger.info(f"[DEBUG] After copy - df_copy.index[:5]={df_copy.index[:5].tolist()}")
            
            for col in valid_group_by:
                df_copy[col] = df_copy[col].astype(str)
                
            logger.info(f"[DEBUG] After astype - df_copy.index type={type(df_copy.index)}")
            logger.info(f"[DEBUG] After astype - df_copy.index[:5]={df_copy.index[:5].tolist()}")
            logger.info(f"[DEBUG] df_copy['{column_name}'][:5]={df_copy[column_name].head().tolist()}")

            # Forward fill within groups - ONLY fill null values, preserve existing data
            mask = df_copy[column_name].isna()
            
            logger.info(f"[DEBUG] mask type={type(mask)}")
            logger.info(f"[DEBUG] mask index type={type(mask.index)}")
            logger.info(f"[DEBUG] mask index[:5]={mask.index[:5].tolist()}")
            logger.info(f"[DEBUG] mask.sum()={mask.sum()}")
            
            filled_values = df_copy.groupby(valid_group_by)[column_name].ffill()
            
            logger.info(f"[DEBUG] _apply_forward_fill - filled_values type={type(filled_values)}")
            logger.info(f"[DEBUG] _apply_forward_fill - filled_values.shape={filled_values.shape if hasattr(filled_values, 'shape') else 'N/A'}")
            
            # Use .values to avoid pandas index alignment issues that cause string iteration
            fill_data = filled_values[mask].values
            logger.info(f"[DEBUG] _apply_forward_fill - fill_data type={type(fill_data)}, shape={fill_data.shape if hasattr(fill_data, 'shape') else 'N/A'}")
            
            df_copy.loc[mask, column_name] = fill_data

            # Apply fill_value for any remaining NaN (groups that started with null)
            df_copy[column_name] = df_copy[column_name].fillna(fill_value)

            # Update original dataframe with filled values
            df[column_name] = df_copy[column_name]
        else:
            # Simple forward fill - ONLY fill nulls, preserve existing data
            logger.info(f"[DEBUG] Simple forward fill branch - column_name='{column_name}' (type={type(column_name)})")
            logger.info(f"[DEBUG] df.shape={df.shape}, df.index type={type(df.index)}")
            logger.info(f"[DEBUG] df.columns type={type(df.columns)}, df.columns[:5]={list(df.columns)[:5]}")
            logger.info(f"[DEBUG] df index sample={df.index[:3].tolist() if hasattr(df.index, 'tolist') else list(df.index)[:3]}")
            
            # CRITICAL: Check for duplicate columns which cause df[col] to return DataFrame
            col_count = df.columns.tolist().count(column_name)
            if col_count > 1:
                logger.error(f"DUPLICATE COLUMNS DETECTED: '{column_name}' appears {col_count} times!")
                logger.error(f"All columns: {list(df.columns)}")
                logger.error("Removing duplicate columns...")
                
                # Keep only the first occurrence of each column
                df = df.loc[:, ~df.columns.duplicated()].copy()
                logger.info(f"Removed duplicates. New df.columns: {list(df.columns)}")
                df.index = pd.RangeIndex(len(df))
            
            # CRITICAL: Rebuild DataFrame to ensure clean structure
            # This fixes any corruption from previous operations
            try:
                # Reset index to ensure it's clean
                if not isinstance(df.index, pd.RangeIndex):
                    logger.warning("Resetting index before forward fill")
                    df = df.reset_index(drop=True)
                
                # Verify column exists and is accessible
                if column_name not in df.columns:
                    logger.error(f"Column '{column_name}' not found in df.columns")
                    logger.error(f"Available columns: {list(df.columns)}")
                    return df
                
                # Test column access explicitly
                test_col = df[column_name]
                if isinstance(test_col, pd.DataFrame):
                    logger.error(f"df['{column_name}'] returned a DataFrame, not a Series!")
                    logger.error(f"This indicates DataFrame corruption. Attempting to fix...")
                    # Rebuild the DataFrame from scratch
                    df = pd.DataFrame(df.values, columns=df.columns, index=df.index)
                    df.index = pd.RangeIndex(len(df))
                    logger.info("DataFrame rebuilt successfully")
                
                logger.info(f"[DEBUG] Attempting df['{column_name}'].isna()")
                mask = df[column_name].isna()
                logger.info(f"[DEBUG] mask created successfully, mask.sum()={mask.sum()}")
            except Exception as e:
                logger.error(f"[DEBUG] Error creating mask: {e}")
                logger.error(f"[DEBUG] df.index type={type(df.index)}, df.index[:5]={df.index[:5].tolist() if hasattr(df.index, 'tolist') else list(df.index)[:5]}")
                logger.error(f"[DEBUG] df.columns type={type(df.columns)}, df.columns[:10]={list(df.columns)[:10]}")
                raise
            
            try:
                logger.info(f"[DEBUG] Attempting df['{column_name}'].ffill()")
                filled_values = df[column_name].ffill()
                logger.info(f"[DEBUG] ffill successful, filled_values[:5]={filled_values.head().tolist()}")
            except Exception as e:
                logger.error(f"[DEBUG] Error in ffill: {e}")
                logger.error(f"[DEBUG] df['{column_name}'] type={type(df[column_name])}")
                raise

            # Use .values to avoid pandas index alignment issues that cause string iteration
            try:
                logger.info(f"[DEBUG] Attempting df.loc[mask, '{column_name}'] assignment")
                fill_data = filled_values[mask].values
                df.loc[mask, column_name] = fill_data
                logger.info(f"[DEBUG] Assignment successful")
            except Exception as e:
                logger.error(f"[DEBUG] Error in loc assignment: {e}")
                logger.error(f"[DEBUG] fill_data type={type(fill_data)}, fill_data[:5]={fill_data[:5]}")
                logger.error(f"[DEBUG] mask index type={type(mask.index)}, mask index[:5]={mask.index[:5].tolist()}")
                raise
            
            # Apply fill_value for any remaining NaN at start
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
    
    def _apply_multi_level_forward_fill(self, df: pd.DataFrame, column_name: str, null_handling: Dict) -> pd.DataFrame:
        """Apply multi-level forward fill strategy."""
        levels = null_handling.get('levels', [])
        final_fill = null_handling.get('final_fill')
        datetime_conversion = null_handling.get('datetime_conversion', {})
        
        # Optionally perform datetime conversion beforehand
        if datetime_conversion and column_name in df.columns:
            errors = datetime_conversion.get('errors', 'coerce')
            df[column_name] = pd.to_datetime(df[column_name], errors=errors)
        
        for level in levels:
            group_by = level.get('group_by', [])
            if group_by:
                df_copy = df.copy()
                for col in group_by:
                    if col in df_copy.columns:
                        df_copy[col] = df_copy[col].astype(str)

                # Forward fill within groups - ONLY fill null values, preserve existing data
                mask = df_copy[column_name].isna()
                filled_values = df_copy.groupby(group_by)[column_name].ffill()
                # Use .values to avoid pandas index alignment issues
                df_copy.loc[mask, column_name] = filled_values[mask].values
                df[column_name] = df_copy[column_name]
                
        if final_fill is not None and column_name in df.columns:
            df[column_name] = df[column_name].fillna(final_fill)
            
        logger.info(f"Applied multi_level_forward_fill for {column_name}")
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
        """
        Apply calculate if null strategy.
        
        Note: This method is deprecated for columns with is_calculated=true.
        Use null_handling.strategy: leave_null instead for calculated columns.
        Currently only handles legacy date_calculation and conditional calculations.
        """
        calculation = null_handling.get('calculation', {})
        calc_type = calculation.get('type')
        method = calculation.get('method')

        if calc_type == 'date_calculation' and method == 'add_working_days':
            df = self._calculate_working_days(df, column_name, calculation)
        elif calc_type == 'conditional' and method == 'status_based':
            df = self._apply_conditional_calculation(df, column_name, calculation)
        else:
            logger.warning(
                f"Unsupported calculation type in calculate_if_null: {calc_type}/{method} for {column_name}. "
                f"Use is_calculated:true with appropriate calculation type instead."
            )

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
        """Apply default value strategy with formatting support."""
        default_value = null_handling.get('default_value', null_handling.get('default', 'NA'))
        text_replacements = null_handling.get('text_replacements', {})
        type_conversion = null_handling.get('type_conversion')
        formatting = null_handling.get('formatting', {})
        zero_pad = formatting.get('zero_pad')
        
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
        
        # Apply zero-padding formatting if specified
        if zero_pad and column_name in df.columns:
            try:
                def pad_if_numeric(x):
                    if pd.isna(x) or x == 'NA':
                        return x
                    # Try to convert to int and pad
                    try:
                        num = int(float(str(x)))
                        return str(num).zfill(zero_pad)
                    except (ValueError, TypeError):
                        # Not a number, return as-is
                        return x
                
                df[column_name] = df[column_name].apply(pad_if_numeric)
                logger.info(f"Applied zero-padding ({zero_pad} digits) for {column_name}")
            except Exception as e:
                logger.warning(f"Could not apply zero-padding for {column_name}: {e}")
        
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
        print(f"[CALCULATION] Processing sequence: {self.calculation_order}")
        
        for column_name in self.calculation_order:
            column_def = self.columns[column_name]
                
            calculation = column_def.get('calculation', {})
            calc_type = calculation.get('type')
            method = calculation.get('method')
            self._print_processing_step(
                'CALCULATION',
                column_name,
                f"type={calc_type}, method={method}"
            )
            
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
            elif calc_type == 'aggregate' and method == 'concatenate_unique_quoted':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'concatenate_dates':
                df_calculated = self._apply_aggregate_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'aggregate' and method == 'latest_by_date':
                df_calculated = self._apply_latest_by_date_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'copy' and method == 'direct':
                df_calculated = self._apply_copy_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'conditional' and method == 'current_row':
                df_calculated = self._apply_current_row_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'conditional' and method == 'update_resubmission_required':
                df_calculated = self._apply_update_resubmission_required(df_calculated, column_name, calculation)
            elif calc_type == 'conditional' and method == 'submission_closure_status':
                df_calculated = self._apply_submission_closure_status(df_calculated, column_name, calculation)
            elif calc_type == 'conditional' and method == 'calculate_overdue_status':
                df_calculated = self._apply_calculate_overdue_status(df_calculated, column_name, calculation)
            elif calc_type == 'date_calculation':
                df_calculated = self._apply_date_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'conditional_date_calculation':
                df_calculated = self._apply_conditional_date_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'conditional_business_day_calculation':
                df_calculated = self._apply_conditional_business_day_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'custom_conditional_date' and method == 'calculate_resubmission_plan_date':
                df_calculated = self._apply_resubmission_plan_date(df_calculated, column_name, calculation)
            elif calc_type == 'custom_aggregate' and method == 'latest_non_pending_status':
                df_calculated = self._apply_latest_non_pending_status(df_calculated, column_name, calculation)
            elif calc_type == 'composite' and method == 'build_document_id':
                df_calculated = self._apply_composite_calculation(df_calculated, column_name, calculation)
            elif calc_type == 'auto_increment' and method == 'generate_row_index':
                df_calculated = self._apply_row_index(df_calculated, column_name, calculation)
            elif calc_type == 'complex_lookup' and method == 'calculate_delay_of_resubmission':
                df_calculated = self._apply_delay_of_resubmission(df_calculated, column_name, calculation)
            else:
                logger.warning(f"Unsupported calculation type: {calc_type} for {column_name}")
        
        return df_calculated
    
    def _apply_mapping_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply mapping calculation with support for external mapping references."""
        source_column = calculation.get('source_column')
        mapping = calculation.get('mapping', {})
        mapping_ref = calculation.get('mapping_reference')
        default = calculation.get('default', 'PEN')
        
        # Load external mapping if reference provided
        if mapping_ref and not mapping:
            ref_data = self.schema_data.get(f'{mapping_ref}_data', {})
            if ref_data:
                # approval_code_schema stores rows under approval[] with
                # {code, status, aliases}. Invert aliases/status to {text: code}.
                approval_rows = ref_data.get('approval', [])
                for row in approval_rows:
                    code = row.get('code')
                    if not code:
                        continue
                    status = row.get('status')
                    if status:
                        mapping[status] = code
                    for alias in row.get('aliases', []):
                        mapping[alias] = code
        
        if source_column in df.columns:
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
        
        if source_column in df.columns and group_by:
            grouped = df.groupby(group_by, dropna=False)
            
            if method == 'count':
                df[column_name] = grouped[source_column].transform('count')
            elif method in ['min', 'max']:
                df[column_name] = grouped[source_column].transform(method)
            elif method == 'concatenate_unique':
                if sort_by:
                    df_sorted = df.sort_values(sort_by)
                    grouped = df_sorted.groupby(group_by, dropna=False)
                
                def concat_unique(series):
                    # Filter out nulls and get unique values
                    unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
                    # Sort numerically if possible, otherwise alphabetically
                    try:
                        # Attempt numeric sort if all look like numbers
                        sorted_vals = sorted(unique_vals, key=lambda x: float(x))
                    except (ValueError, TypeError):
                        sorted_vals = sorted(unique_vals)
                    return separator.join(sorted_vals)
                
                df[column_name] = grouped[source_column].transform(concat_unique)
                
            elif method == 'concatenate_unique_quoted':
                if sort_by:
                    df_sorted = df.sort_values(sort_by)
                    grouped = df_sorted.groupby(group_by, dropna=False)
                
                quote_each = calculation.get('quote_each', True)
                def concat_unique_quoted(series):
                    unique_vals = [str(val) for val in series.dropna().unique() if pd.notna(val)]
                    # Alpha sort for quoted strings
                    sorted_vals = sorted(unique_vals)
                    if quote_each:
                        return separator.join(f'"{val}"' for val in sorted_vals)
                    return separator.join(sorted_vals)
                
                df[column_name] = grouped[source_column].transform(concat_unique_quoted)
                
            elif method == 'concatenate_dates':
                if sort_by:
                    df_sorted = df.sort_values(sort_by)
                    grouped = df_sorted.groupby(group_by, dropna=False)
                
                date_fmt = calculation.get('date_format', 'YYYY-MM-DD')
                py_date_fmt = date_fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
                
                def concat_dates(series):
                    # Convert to datetime and get unique, sorted dates
                    valid_dates = pd.to_datetime(series, errors='coerce').dropna()
                    if valid_dates.empty:
                        return ""
                    
                    unique_sorted_dates = sorted(valid_dates.unique())
                    # Convert back to Series to use dt.strftime if we want vector, 
                    # but simple list comprehension is safer and faster for unique small sets
                    formatted = [pd.Timestamp(d).strftime(py_date_fmt) for d in unique_sorted_dates]
                    return separator.join(formatted)
                
                df[column_name] = grouped[source_column].transform(concat_dates)
        
        logger.info(f"Applied aggregate calculation for {column_name}: method={method}")
        return df

    def _apply_latest_by_date_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply latest by date aggregations."""
        source_column = calculation.get('source_column')
        group_by = calculation.get('group_by', [])
        sort_by = calculation.get('sort_by', [])
        sort_dir = calculation.get('sort_direction', ['desc'])
        mapping = calculation.get('mapping', {})
        fallback = mapping.get('fallback_value', 'NA')
        
        if source_column in df.columns and group_by and sort_by:
            filtered_df = df.copy()
            exclude = calculation.get('filter', {}).get('exclude_values', [])
            if exclude:
                filtered_df = filtered_df[~filtered_df[source_column].isin(exclude)]
                
            asc_flags = [d.lower() == 'asc' for d in sort_dir]
            if len(asc_flags) < len(sort_by):
                asc_flags.extend([False] * (len(sort_by) - len(asc_flags)))
                
            sorted_df = filtered_df.sort_values(sort_by, ascending=asc_flags)
            latest_vals = sorted_df.groupby(group_by)[source_column].first()
            
            # Map values back to original dataframe lengths
            if len(group_by) == 1:
                df[column_name] = df[group_by[0]].map(latest_vals).fillna(fallback)
            else:
                mapped = pd.merge(df[group_by], latest_vals, left_on=group_by, right_index=True, how='left')
                df[column_name] = mapped[source_column].fillna(fallback)
        else:
            df[column_name] = fallback
            
        logger.info(f"Applied latest_by_date calculation for {column_name}")
        return df
    
    def _apply_latest_non_pending_status(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Apply custom aggregate to find latest non-pending status per group.

        For Latest_Approval_Status:
        - Groups by Document_ID
        - Sorts by Submission_Date descending
        - Filters out pending statuses
        - Takes the most recent non-pending status
        - Falls back to pending_status if all are pending
        """
        # Resolve pending_status parameter from schema (already resolved if it was a $ref)
        parameters = self.schema_data.get('parameters', {})
        pending_status_value = parameters.get('pending_status')
        
        # Fallback: if pending_status not in parameters, try to resolve from approval_code_schema
        if pending_status_value is None or pending_status_value == 'pending_status':
            pending_status_value = self._resolve_schema_reference({
                'schema': 'approval_code_schema',
                'code': 'PEN',
                'field': 'status'
            }) or "Awaiting S.O.'s response"
        
        source_column = calculation.get('source_column')
        group_by = calculation.get('group_by', ['Document_ID'])
        sort_by = calculation.get('sort_by', ['Submission_Date'])
        sort_direction = calculation.get('sort_direction', ['desc'])
        filter_config = calculation.get('filter', {})
        
        # Resolve exclude_values from schema reference if specified
        exclude_values_ref = filter_config.get('exclude_values_reference')
        if exclude_values_ref:
            exclude_values = self._resolve_schema_reference(exclude_values_ref)
            # If the reference returns aliases (a list), use them; otherwise wrap in list
            if isinstance(exclude_values, list):
                exclude_values = exclude_values
            else:
                exclude_values = [exclude_values] if exclude_values else []
        else:
            # Legacy support: use exclude_values directly
            exclude_values = filter_config.get('exclude_values', [])
            # Resolve 'pending_status' placeholder if still used
            exclude_values = [pending_status_value if v == 'pending_status' else v for v in exclude_values]
        
        # Resolve fallback_value from schema reference if specified
        fallback_ref = calculation.get('fallback_value_reference')
        if fallback_ref:
            fallback_value = self._resolve_schema_reference(fallback_ref)
        else:
            # Legacy support: use fallback_value directly
            fallback_config = calculation.get('fallback_value', 'pending_status')
            fallback_value = pending_status_value if fallback_config == 'pending_status' else fallback_config
        
        preprocessing = calculation.get('preprocessing', {})
        
        if source_column not in df.columns:
            logger.warning(f"Source column {source_column} not found for latest_non_pending_status")
            return df
        
        # Get required columns
        required_cols = group_by + sort_by + [source_column]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns for latest_non_pending_status: {missing_cols}")
            return df
        
        # Apply preprocessing if configured
        df_copy = df.copy()
        text_cleaning = preprocessing.get('text_cleaning', {})
        if text_cleaning:
            # Remove patterns
            remove_patterns = text_cleaning.get('remove_patterns', [])
            if remove_patterns:
                for pattern in remove_patterns:
                    df_copy[source_column] = df_copy[source_column].astype(str).str.replace(pattern, '', regex=True)
            # Strip whitespace
            if text_cleaning.get('strip_whitespace'):
                df_copy[source_column] = df_copy[source_column].astype(str).str.strip()
        
        def get_latest_non_pending(group_df):
            # Sort by date descending
            sorted_df = group_df.sort_values(by=sort_by[0], ascending=False)
            
            # Filter out excluded values (pending statuses)
            mask = ~sorted_df[source_column].isin(exclude_values)
            non_pending = sorted_df[mask]
            
            if len(non_pending) > 0:
                return non_pending.iloc[0][source_column]
            else:
                return fallback_value
        
        # Group and apply
        result = df_copy.groupby(group_by).apply(get_latest_non_pending, include_groups=False)
        
        # Merge back
        if isinstance(result, pd.Series):
            result_df = result.reset_index()
            result_df.columns = group_by + [column_name]
            df = pd.merge(df, result_df, on=group_by, how='left')
        else:
            df[column_name] = fallback_value
        
        logger.info(f"Applied latest_non_pending_status for {column_name}: grouped by {group_by}")
        return df
    
    def _apply_copy_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply direct copy calculation."""
        source_column = calculation.get('source_column')
        
        if source_column in df.columns:
            df[column_name] = df[source_column]
        
        logger.info(f"Applied copy calculation for {column_name}: source={source_column}")
        return df
    
    def _apply_current_row_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply current row calculation."""
        source_column = calculation.get('source_column')
        condition = calculation.get('condition')
        
        if source_column in df.columns:
            if condition == 'is_current_submission':
                # Mark current row values (simplified for demo)
                df[column_name] = df[source_column]
            else:
                df[column_name] = df[source_column]
        
        logger.info(f"Applied current row calculation for {column_name}: condition={condition}")
        return df
    
    def _apply_update_resubmission_required(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Update Resubmission_Required based on multiple conditions with short-circuit logic.
        Once a condition sets a value, subsequent conditions are skipped for that row.

        Priority order (per schema):
        1. Keep NO if already NO
        2. Set to NO if submission is closed
        3. Set to RESUBMITTED if not the latest submission (resubmission already done)
        4. Set to PEN if latest submission and awaiting review return
        5. Default to YES for remaining rows
        """
        source_column = calculation.get('source_column', 'Resubmission_Required')

        # Get required columns
        submission_closed_col = 'Submission_Closed' if 'Submission_Closed' in df.columns else None
        document_id_col = 'Document_ID' if 'Document_ID' in df.columns else None
        submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None
        review_return_col = 'Review_Return_Actual_Date' if 'Review_Return_Actual_Date' in df.columns else None

        # Initialize: start with default YES for all rows
        df[column_name] = 'YES'

        # Track which rows have been determined - these skip remaining checks
        determined_mask = pd.Series([False] * len(df), index=df.index)

        # Condition 1: Keep NO if already NO
        if source_column in df.columns:
            mask_already_no = df[source_column] == 'NO'
            df.loc[mask_already_no, column_name] = 'NO'
            determined_mask |= mask_already_no

        # Condition 2: Set to NO if submission is closed (skip rows already determined)
        if submission_closed_col:
            mask_closed = (df[submission_closed_col] == 'YES') & ~determined_mask
            df.loc[mask_closed, column_name] = 'NO'
            determined_mask |= mask_closed

        # Condition 3: Set to RESUBMITTED if not the latest submission (skip rows already determined)
        if document_id_col and submission_date_col:
            # Convert submission_date to datetime for comparison
            df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')

            # Find the latest submission date for each Document_ID
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')

            # If current row's submission date is NOT the latest, resubmission already done
            mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
            df.loc[mask_not_latest, column_name] = 'RESUBMITTED'
            determined_mask |= mask_not_latest

        # Condition 4: Set to PEN if latest submission and awaiting review return
        if review_return_col and submission_date_col and document_id_col:
            # Convert review return date to datetime
            df[review_return_col] = pd.to_datetime(df[review_return_col], errors='coerce')
            
            # Get latest submission dates again
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
            
            # Latest submission with no review return yet
            mask_pending = (
                (df[submission_date_col] == latest_dates) & 
                df[review_return_col].isna() & 
                ~determined_mask
            )
            df.loc[mask_pending, column_name] = 'PEN'
            determined_mask |= mask_pending

        # Condition 5: Default YES - already set for all remaining undetermined rows

        logger.info(f"Applied update_resubmission_required for {column_name}: {(df[column_name] == 'NO').sum()} NO, {(df[column_name] == 'RESUBMITTED').sum()} RESUBMITTED, {(df[column_name] == 'PEN').sum()} PEN, {(df[column_name] == 'YES').sum()} YES")
        return df
    
    def _apply_submission_closure_status(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Calculate Submission_Closed based on multiple conditions with short-circuit logic.
        Once a condition sets a value, subsequent conditions are skipped for that row.

        Priority order:
        1. Keep YES if already YES
        2. Set to YES if current submission is not the latest (superseded by newer submission)
        3. Set to YES if Latest_Approval_Code in ['APP', 'VOID']
        4. Default to NO for remaining rows

        Note: Does NOT depend on Resubmission_Required to avoid circular dependency
        (Resubmission_Required is processed after Submission_Closed).
        """
        source_column = calculation.get('source_column', 'Submission_Closed')
        
        # Get required columns
        latest_approval_col = 'Latest_Approval_Code' if 'Latest_Approval_Code' in df.columns else None
        document_id_col = 'Document_ID' if 'Document_ID' in df.columns else None
        submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None
        
        # Preprocessing: convert to uppercase and fill nulls
        preprocessing = calculation.get('preprocessing', {})
        text_cleaning = preprocessing.get('text_cleaning', {})
        if text_cleaning.get('convert_to_uppercase') and source_column in df.columns:
            df[source_column] = df[source_column].str.upper()
        if text_cleaning.get('fill_nulls') and source_column in df.columns:
            df[source_column] = df[source_column].fillna(text_cleaning['fill_nulls'])
        
        # Initialize: start with default NO for all rows
        df[column_name] = 'NO'
        
        # Track which rows have been determined - these skip remaining checks
        determined_mask = pd.Series([False] * len(df), index=df.index)
        
        # Condition 1: Keep YES if already YES (only for undetermined rows). This allow user to force closing the submission
        if source_column in df.columns:
            mask_already_yes = (df[source_column] == 'YES') & ~determined_mask
            df.loc[mask_already_yes, column_name] = 'YES'
            determined_mask |= mask_already_yes
        
        # Condition 2: Set to YES if current submission is not the latest (superseded)
        if document_id_col and submission_date_col:
            df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
            latest_dates = df.groupby(document_id_col)[submission_date_col].transform('max')
            mask_not_latest = (df[submission_date_col] < latest_dates) & ~determined_mask
            df.loc[mask_not_latest, column_name] = 'YES'
            determined_mask |= mask_not_latest
        
        # Condition 3: Set to YES if Latest_Approval_Code is in approval list
        if latest_approval_col:
            approval_codes = ['APP', 'VOID']
            mask_approved = df[latest_approval_col].isin(approval_codes) & ~determined_mask
            df.loc[mask_approved, column_name] = 'YES'
            determined_mask |= mask_approved
        
        # Condition 4: Default NO - already set for all remaining undetermined rows
        
        logger.info(f"Applied submission_closure_status for {column_name}: {(df[column_name] == 'YES').sum()} rows set to YES, {(df[column_name] == 'NO').sum()} rows set to NO")
        return df
    
    def _apply_calculate_overdue_status(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Calculate Resubmission_Overdue_Status based on conditional logic.
        
        Logic:
        1. If Resubmission_Required == 'YES' AND Resubmission_Plan_Date is not null AND Resubmission_Plan_Date < current_date → 'Overdue'
        2. Otherwise → null
        """
        from datetime import datetime
        
        # Get required columns
        resubmission_required_col = 'Resubmission_Required' if 'Resubmission_Required' in df.columns else None
        resubmission_plan_date_col = 'Resubmission_Plan_Date' if 'Resubmission_Plan_Date' in df.columns else None
        
        # Initialize with null
        df[column_name] = None
        
        if resubmission_required_col and resubmission_plan_date_col:
            # Convert plan date to datetime
            df[resubmission_plan_date_col] = pd.to_datetime(df[resubmission_plan_date_col], errors='coerce')
            
            # Get current date
            current_date = pd.Timestamp.now().normalize()
            
            # Condition: Resubmission_Required == 'YES' AND plan date not null AND plan date < current_date
            mask_overdue = (
                (df[resubmission_required_col] == 'YES') &
                (df[resubmission_plan_date_col].notna()) &
                (df[resubmission_plan_date_col] < current_date)
            )
            
            df.loc[mask_overdue, column_name] = 'Overdue'
            
            logger.info(f"Applied calculate_overdue_status for {column_name}: {mask_overdue.sum()} rows Overdue, {(~mask_overdue).sum()} rows null")
        else:
            logger.warning(f"Cannot calculate overdue status: missing required columns")
        
        return df
    
    def _apply_resubmission_plan_date(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Calculate Resubmission_Plan_Date based on conditional logic.
        Important: When Submission_Closed is YES, always overwrite to null (NaT).
        """
        dependencies = calculation.get('dependencies', [])
        conditions = calculation.get('conditions', [])
        parameters = calculation.get('parameters', {})
        
        # Get parameters
        resubmission_duration = parameters.get('resubmission_duration', 14)
        first_review_duration = parameters.get('first_review_duration', 20)
        second_review_duration = parameters.get('second_review_duration', 14)
        duration_is_working_day = parameters.get('duration_is_working_day', True)
        
        # Get required columns
        submission_closed_col = 'Submission_Closed' if 'Submission_Closed' in df.columns else None
        review_return_date_col = 'Review_Return_Actual_Date' if 'Review_Return_Actual_Date' in df.columns else None
        latest_submission_date_col = 'Latest_Submission_Date' if 'Latest_Submission_Date' in df.columns else None
        submission_date_col = 'Submission_Date' if 'Submission_Date' in df.columns else None
        
        # Initialize column as NaT (will be overwritten based on conditions)
        df[column_name] = pd.NaT
        
        # Track which rows have been determined (set) - these skip remaining checks
        determined_mask = pd.Series([False] * len(df), index=df.index)
        
        # Condition 1: If Submission_Closed == 'YES', set to NaT (null) - OVERWRITES existing values
        if submission_closed_col:
            mask_closed = df[submission_closed_col] == 'YES'
            df.loc[mask_closed, column_name] = pd.NaT
            determined_mask |= mask_closed
            
        # Condition 2: If Review_Return_Actual_Date is not null, add duration offset
        if review_return_date_col:
            df[review_return_date_col] = pd.to_datetime(df[review_return_date_col], errors='coerce')
            mask_has_return_date = df[review_return_date_col].notna() & ~determined_mask
            
            if duration_is_working_day:
                # Use business days
                from pandas.tseries.offsets import BDay
                df.loc[mask_has_return_date, column_name] = df.loc[mask_has_return_date, review_return_date_col] + BDay(resubmission_duration)
            else:
                # Use calendar days
                df.loc[mask_has_return_date, column_name] = df.loc[mask_has_return_date, review_return_date_col] + pd.Timedelta(days=resubmission_duration)
            
            determined_mask |= mask_has_return_date
        
        # Condition 3: If Latest_Submission_Date == Submission_Date (first submission)
        if latest_submission_date_col and submission_date_col:
            df[latest_submission_date_col] = pd.to_datetime(df[latest_submission_date_col], errors='coerce')
            df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
            
            mask_first_submission = (df[latest_submission_date_col] == df[submission_date_col]) & ~determined_mask
            
            total_days = first_review_duration + resubmission_duration
            if duration_is_working_day:
                from pandas.tseries.offsets import BDay
                df.loc[mask_first_submission, column_name] = df.loc[mask_first_submission, submission_date_col] + BDay(total_days)
            else:
                df.loc[mask_first_submission, column_name] = df.loc[mask_first_submission, submission_date_col] + pd.Timedelta(days=total_days)
            
            determined_mask |= mask_first_submission
        
        # Condition 4: Else (subsequent submission)
        if submission_date_col:
            mask_subsequent = ~determined_mask
            total_days = second_review_duration + resubmission_duration
            if duration_is_working_day:
                from pandas.tseries.offsets import BDay
                df.loc[mask_subsequent, column_name] = df.loc[mask_subsequent, submission_date_col] + BDay(total_days)
            else:
                df.loc[mask_subsequent, column_name] = df.loc[mask_subsequent, submission_date_col] + pd.Timedelta(days=total_days)
            determined_mask |= mask_subsequent
        
        logger.info(f"Applied resubmission_plan_date for {column_name}: {df[column_name].notna().sum()} rows with dates, {df[column_name].isna().sum()} rows null")
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
    
    def _apply_conditional_date_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Apply conditional date calculation based on previous submission existence.
        
        For Review_Return_Plan_Date:
        - First submission: Submission_Date + first_review_duration
        - Resubmission: Submission_Date + second_review_duration
        """
        dependencies = calculation.get('dependencies', [])
        conditions = calculation.get('conditions', [])
        lookup_logic = calculation.get('lookup_logic', {})
        group_by = calculation.get('group_by', [])
        
        # Get required columns
        doc_id_col = 'Document_ID'
        submission_date_col = 'Submission_Date'
        
        if doc_id_col not in df.columns or submission_date_col not in df.columns:
            logger.warning(f"Missing required columns for conditional date calculation: {doc_id_col}, {submission_date_col}")
            return df
        
        # Get durations from schema parameters
        first_duration = calculation.get('first_review_duration', 20)
        second_duration = calculation.get('second_review_duration', 14)
        
        # Convert submission date to datetime
        df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
        
        # Calculate for each row
        results = []
        for idx, row in df.iterrows():
            doc_id = row.get(doc_id_col)
            sub_date = row.get(submission_date_col)
            
            if pd.isna(sub_date) or not doc_id:
                results.append(pd.NaT)
                continue
            
            # Check if previous submission exists
            previous_exists = False
            if doc_id:
                previous = df[
                    (df[doc_id_col] == doc_id) & 
                    (df[submission_date_col] < sub_date)
                ]
                previous_exists = len(previous) > 0
            
            # Apply appropriate duration
            if previous_exists:
                # Resubmission: use second_review_duration
                result_date = sub_date + pd.Timedelta(days=second_duration)
            else:
                # First submission: use first_review_duration
                result_date = sub_date + pd.Timedelta(days=first_duration)
            
            results.append(result_date)
        
        df[column_name] = pd.to_datetime(results)
        
        logger.info(f"Applied conditional date calculation for {column_name}: first={first_duration}d, resub={second_duration}d")
        return df
    
    def _apply_conditional_business_day_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Apply conditional business day calculation.
        
        For Duration_of_Review:
        - Primary end date: Review_Return_Actual_Date
        - Fallback end date: current_date (today)
        - Calculate days between Submission_Date and end_date
        - Ensures non-negative values
        """
        # Get configuration
        end_date_logic = calculation.get('end_date_logic', {})
        primary_end = end_date_logic.get('primary', 'Review_Return_Actual_Date')
        fallback_end = end_date_logic.get('fallback', 'current_date')
        
        start_col = 'Submission_Date'
        
        if start_col not in df.columns:
            logger.warning(f"Missing required column for business day calculation: {start_col}")
            return df
        
        # Convert to datetime
        df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
        
        # Determine end date: primary if available, else fallback
        end_dates = []
        today = pd.Timestamp.now().normalize()
        
        for idx, row in df.iterrows():
            # Try primary end date first
            primary_date = None
            if primary_end in df.columns:
                primary_val = row.get(primary_end)
                if pd.notna(primary_val):
                    primary_date = pd.to_datetime(primary_val, errors='coerce')
            
            # Use primary if valid, else fallback to today
            if pd.notna(primary_date):
                end_dates.append(primary_date)
            elif fallback_end == 'current_date':
                end_dates.append(today)
            else:
                end_dates.append(pd.NaT)
        
        # Calculate duration in days
        durations = []
        for idx, row in df.iterrows():
            start = row.get(start_col)
            end = end_dates[idx]
            
            if pd.isna(start) or pd.isna(end):
                durations.append(np.nan)
                continue
            
            # Calculate calendar days
            diff = (end - start).days
            
            # Apply non-negative enforcement
            if diff < 0:
                diff = np.nan
            
            durations.append(diff)
        
        df[column_name] = durations
        
        logger.info(f"Applied conditional business day calculation for {column_name}: primary={primary_end}, fallback={fallback_end}")
        return df
    
    def _apply_composite_calculation(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """Apply composite calculation using row-by-row formatting."""
        # Support both 'sources' and 'source_columns'
        source_columns = calculation.get('sources') or calculation.get('source_columns', [])
        format_string = calculation.get('format', '')
        
        if not format_string:
            logger.warning(f"No format string provided for composite calculation of {column_name}")
            return df
            
        # Verify which sources exist in df
        available_sources = [col for col in source_columns if col in df.columns]
        
        if not available_sources:
            logger.warning(f"No available source columns for composite calculation: {column_name}")
            return df
            
        def format_row(row):
            try:
                # Convert row to dict and fill NaNs with empty string or 'NA' for cleaner output
                values = row.to_dict()
                # Ensure all required keys in format string are present
                return format_string.format(**values)
            except Exception:
                return "ERR-COMPOSITE"

        # Apply formatting row-by-row
        df[column_name] = df[available_sources].apply(format_row, axis=1)
        
        logger.info(f"Applied composite calculation for {column_name}: {len(available_sources)}/{len(source_columns)} sources found")
        return df
    
    def _apply_delay_of_resubmission(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Calculate Delay_of_Resubmission with non-negative check.
        
        Logic:
        - If Submission_Closed == 'YES', return 0
        - Find previous submissions for same Document_ID with earlier Submission_Date
        - Get latest Resubmission_Plan_Date from previous submissions
        - Calculate days between that plan date and current Submission_Date
        - Ensure non-negative: return max(delay, 0)
        """
        doc_id_col = 'Document_ID'
        submission_date_col = 'Submission_Date'
        plan_date_col = 'Resubmission_Plan_Date'
        closed_col = 'Submission_Closed'
        
        required_cols = [doc_id_col, submission_date_col, plan_date_col, closed_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns for delay calculation: {missing_cols}")
            df[column_name] = 0
            return df
        
        df[submission_date_col] = pd.to_datetime(df[submission_date_col], errors='coerce')
        df[plan_date_col] = pd.to_datetime(df[plan_date_col], errors='coerce')
        
        delays = []
        for idx, row in df.iterrows():
            # If submission is closed, delay is 0
            if row.get(closed_col) == 'YES':
                delays.append(0)
                continue
            
            current_doc_id = row.get(doc_id_col)
            current_submission_date = row.get(submission_date_col)
            
            if pd.isna(current_doc_id) or pd.isna(current_submission_date):
                delays.append(0)
                continue
            
            # Find previous submissions for same Document_ID
            prev_subs = df[(df[doc_id_col] == current_doc_id) & (df[submission_date_col] < current_submission_date)]
            
            if prev_subs.empty:
                delays.append(0)
                continue
            
            # Get latest Resubmission_Plan_Date from previous submissions
            latest_plan = prev_subs[plan_date_col].max()
            
            if pd.isna(latest_plan):
                delays.append(0)
                continue
            
            # Calculate days and ensure non-negative
            delay = (current_submission_date - latest_plan).days
            delay = max(delay, 0)  # Non-negative check
            
            delays.append(delay)
        
        df[column_name] = delays
        logger.info(f"Applied delay_of_resubmission for {column_name}: {len([d for d in delays if d > 0])} rows with positive delay")
        return df
    
    def _apply_row_index(self, df: pd.DataFrame, column_name: str, calculation: Dict) -> pd.DataFrame:
        """
        Generate or preserve auto-increment row index starting from 1.

        This creates a unique index for each row in the imported data,
        useful for tracking original row positions.
        The Row_Index column is placed as the first column in the DataFrame.
        """
        if column_name not in df.columns:
            df[column_name] = range(1, len(df) + 1)

        df = self._move_column_to_front(df, column_name)
        
        logger.info(f"Applied row index generation for {column_name}: {len(df)} rows indexed")
        return df

    def _move_column_to_front(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """Return a DataFrame with the specified column moved to the first position."""
        cols = df.columns.tolist()
        if column_name not in cols:
            return df

        cols.remove(column_name)
        return df[[column_name] + cols]


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
        """Load and process schema file after schema_validation.py has succeeded."""
        if self.schema_file is None:
            raise ValueError("Schema file path not set. Use UniversalDocumentProcessor(schema_file='path/to/schema.json')")
        
        try:
            is_validated, message = validate_validation_status(self.schema_file)
            if not is_validated:
                raise ValueError(message)

            schema_loader = SchemaLoader()
            schema_loader.set_main_schema_path(self.schema_file)
            main_schema = schema_loader.load_json_file(self.schema_file)
            logger.info(f"Loaded schema: {self.schema_file}")
            
            # Resolve schema dependencies (approval_code_schema, etc.)
            self.schema_data = schema_loader.resolve_schema_dependencies(main_schema)
            logger.info(f"Resolved schema dependencies: {list(main_schema.get('schema_references', {}).keys())}")

            # Resolve parameter references (e.g., pending_status from approval_code_schema)
            self._resolve_parameter_references()

            # Initialize calculation engine with resolved schema data
            self.calculation_engine = CalculationEngine(self.schema_data)
                
        except Exception as e:
            logger.error(f"Error loading schema {e}")
            raise

    def _resolve_parameter_references(self):
        """
        Resolve parameter references from other schemas.
        
        Converts $ref references in parameters to their actual values.
        This ensures single source of truth for values like pending_status.
        """
        parameters = self.schema_data.get('parameters', {})
        if not parameters:
            return
        
        calculation_engine = CalculationEngine(self.schema_data)
        
        for param_name, param_value in list(parameters.items()):
            if isinstance(param_value, dict) and '$ref' in param_value:
                ref_config = param_value['$ref']
                resolved_value = calculation_engine._resolve_schema_reference(ref_config)
                if resolved_value is not None:
                    self.schema_data['parameters'][param_name] = resolved_value
                    logger.info(f"Resolved parameter '{param_name}' from {ref_config.get('schema')}: {resolved_value}")
                else:
                    logger.warning(f"Failed to resolve parameter '{param_name}': {ref_config}")

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

        # CRITICAL: Flatten MultiIndex/tuple columns IMMEDIATELY
        # This must happen before ANY other processing
        df = df.copy()
        if hasattr(pd, 'MultiIndex') and isinstance(df.columns, pd.MultiIndex):
            logger.warning("Flattening MultiIndex columns at start of process_data")
            df.columns = ['_'.join(str(level) for level in levels).strip('_') 
                          for levels in df.columns]
        elif len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            logger.warning("Flattening tuple columns at start of process_data")
            df.columns = ['_'.join(str(level) for level in levels).strip('_') 
                          for levels in df.columns]
        
        # Double-check all columns are strings
        if not all(isinstance(c, str) for c in df.columns):
            logger.warning(f"Non-string columns detected, converting all to strings")
            df.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_') 
                          for c in df.columns]
        
        logger.info(f"DataFrame columns after flattening: {list(df.columns)[:10]}...")

        # Stamp a stable row index onto imported rows as early as possible so
        # downstream mapping/null-handling/calculation logic can rely on it.
        df = self._ensure_row_index_column(df)
        logger.info(f"Processing data with {len(df)} rows and {len(df.columns)} columns")
        original_columns = set(df.columns)

        # Step 0: Initialize missing columns (handles required columns if create_if_missing is true)
        df_initialized = self._initialize_missing_columns(df)
        
        # Step 1: Verify all required columns now exist (after attempted initialization)
        self._verify_required_columns(df_initialized)
        
        # Step 2: Apply null handling
        df_processed = self.calculation_engine.apply_null_handling(df_initialized, original_columns)
        
        # Step 3: Apply calculations
        df_calculated = self.calculation_engine.apply_calculations(df_processed)
        
        # Step 4: Apply final validation
        df_validated = self._apply_validation(df_calculated)

        # Final safeguard: keep the schema-defined row index as the first column.
        row_index_column = self._get_row_index_column_name()
        if row_index_column:
            df_validated = self._move_column_to_front(df_validated, row_index_column)
        
        logger.info(f"Data processing complete: {len(df_validated)} rows")
        return df_validated

    def _get_row_index_column_name(self) -> Optional[str]:
        """Return the schema-defined auto-increment row index column name, if any."""
        enhanced_schema = self.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})

        for col_name, col_def in columns.items():
            calculation = col_def.get('calculation', {})
            if (
                calculation.get('type') == 'auto_increment'
                and calculation.get('method') == 'generate_row_index'
            ):
                return col_name

        return None

    def _ensure_row_index_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add the schema-configured row index column immediately after input load.

        If the row index column already exists, preserve it and only move it to
        the front for consistent downstream ordering.
        """
        row_index_column = self._get_row_index_column_name()
        if not row_index_column:
            return df

        df_with_index = df.copy()
        if row_index_column not in df_with_index.columns:
            df_with_index[row_index_column] = range(1, len(df_with_index) + 1)
            logger.info(
                "Added %s immediately after data load: %s rows indexed",
                row_index_column,
                len(df_with_index),
            )

        return self._move_column_to_front(df_with_index, row_index_column)

    def _move_column_to_front(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """Return a DataFrame with the specified column moved to the first position."""
        cols = df.columns.tolist()
        if column_name not in cols:
            return df

        cols.remove(column_name)
        return df[[column_name] + cols]
        
    def _verify_required_columns(self, df: pd.DataFrame):
        """
        Verify that all columns marked as required (and not calculated) 
        are present in the data after initialization.
        
        Args:
            df: Initialized DataFrame
            
        Raises:
            ValueError: If required input columns are missing
        """
        enhanced_schema = self.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        
        missing_required = []
        for col_name, col_def in columns.items():
            if not isinstance(col_def, dict):
                continue
            is_required = col_def.get('required', False)
            is_calculated = col_def.get('is_calculated', False)
            
            # If required but NOT calculated, it MUST be in the input
            if is_required and not is_calculated:
                if col_name not in df.columns:
                    missing_required.append(col_name)
        
        if missing_required:
            error_msg = f"CRITICAL ERROR: The following required input columns are missing from the original data set: {', '.join(missing_required)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Successfully verified all required input columns exist.")

    def _initialize_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Initialize missing columns based on schema rules."""
        df_init = df.copy()
        
        # Ensure columns are strings before processing
        if not all(isinstance(c, str) for c in df_init.columns):
            logger.warning("Flattening columns in _initialize_missing_columns")
            df_init.columns = ['_'.join(str(level) for level in (c if isinstance(c, tuple) else [c])).strip('_') 
                               for c in df_init.columns]
        
        enhanced_schema = self.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        parameters = self.schema_data.get('parameters', {})
        dyn_creation = parameters.get('dynamic_column_creation', {})
        global_enabled = dyn_creation.get('enabled', False)
        global_default = dyn_creation.get('default_value', 'NA')
        
        # Cast Submission_Session related columns to string for consistent grouping
        submission_session_cols = ['Submission_Session', 'Submission_Session_Revision']
        for col in submission_session_cols:
            if col in df_init.columns:
                df_init[col] = df_init[col].astype(str)
                logger.info(f"Cast {col} to string for consistent grouping")
        
        for col_name, col_def in columns.items():
            if not isinstance(col_def, dict):
                continue
            if col_name not in df_init.columns:
                create_missing = col_def.get('create_if_missing', False)
                
                if create_missing and global_enabled:
                    default_val = global_default
                    if 'default_value' in col_def:  # Top level overrides global
                        default_val = col_def.get('default_value')
                    
                    df_init[col_name] = default_val
                    logger.info(f"Created missing column: {col_name} with default '{default_val}'")
                    
        return df_init
    
    def _apply_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply validation rules from schema and record errors per-row."""
        enhanced_schema = self.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        
        df_validated = df.copy()
        
        # Initialize Validation_Errors column if it exists in schema
        error_col = "Validation_Errors"
        if error_col in columns:
            df_validated[error_col] = ""

        def record_errors(mask, message):
            if error_col in df_validated.columns and mask.any():
                df_validated.loc[mask, error_col] = df_validated.loc[mask, error_col].apply(
                    lambda x: f"{x}; {message}".strip("; ")
                )

        for column_name, column_def in columns.items():
            if not isinstance(column_def, dict):
                continue
            is_required = column_def.get('required', False)
            if column_name not in df_validated.columns:
                if is_required:
                    logger.error(f"Validation failed: Required column {column_name} is missing.")
                continue
                
            allow_null = column_def.get('allow_null', True)
            mask_null = df_validated[column_name].isna()
            if not allow_null and mask_null.any():
                msg = f"{column_name} cannot be null"
                logger.warning(f"Validation failed: {msg} ({mask_null.sum()} found)")
                record_errors(mask_null, msg)

            validation_rules = self._normalize_validation_rules(column_def.get('validation', {}))

            for validation in validation_rules:
                rule_type = validation.get('type')

                if rule_type == 'pattern' or ('pattern' in validation and rule_type is None):
                    pattern = validation['pattern']
                    df_str = df_validated[column_name].astype(str)
                    mask = ~df_str.str.match(pattern)
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} pattern mismatch ({pattern})"
                        logger.warning(f"Pattern validation failed for {column_name}: {mask.sum()} invalid values")
                        record_errors(mask, msg)

                if rule_type == 'min_length' or ('min_length' in validation and rule_type is None):
                    min_len = validation['min_length']
                    df_str = df_validated[column_name].astype(str)
                    mask = df_str.str.len() < min_len
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} too short (<{min_len})"
                        logger.warning(f"Min length validation failed for {column_name}: {mask.sum()} values too short")
                        record_errors(mask, msg)

                if rule_type == 'max_length' or ('max_length' in validation and rule_type is None):
                    max_len = validation['max_length']
                    mask = df_validated[column_name].astype(str).str.len() > max_len
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} too long (>{max_len})"
                        logger.warning(f"Max length validation failed for {column_name}: {mask.sum()} values too long")
                        record_errors(mask, msg)

                if rule_type == 'max_value' or ('max_value' in validation and rule_type is None):
                    max_val = validation['max_value']
                    mask = pd.to_numeric(df_validated[column_name], errors='coerce') > max_val
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} too high (>{max_val})"
                        logger.warning(f"Max value validation failed for {column_name}: {mask.sum()} numeric values > {max_val}")
                        record_errors(mask, msg)

                if rule_type == 'min_value' or ('min_value' in validation and rule_type is None):
                    min_val = validation['min_value']
                    mask = pd.to_numeric(df_validated[column_name], errors='coerce') < min_val
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} too low (<{min_val})"
                        logger.warning(f"Min value validation failed for {column_name}: {mask.sum()} numeric values < {min_val}")
                        record_errors(mask, msg)

                if (rule_type == 'format' or ('format' in validation and rule_type is None)) and validation.get('format') == 'YYYY-MM-DD':
                    parsed = pd.to_datetime(df_validated[column_name], format="%Y-%m-%d", errors='coerce')
                    mask = parsed.isna() & df_validated[column_name].notna() & (df_validated[column_name] != 'NA')
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} invalid date format (expected YYYY-MM-DD)"
                        logger.warning(f"Format validation (YYYY-MM-DD) failed for {column_name}: {mask.sum()} invalid dates")
                        record_errors(mask, msg)

                if rule_type == 'allowed_values' or ('allowed_values' in validation and rule_type is None):
                    allowed = validation['allowed_values']
                    mask = ~df_validated[column_name].isin(allowed)
                    if allow_null:
                        mask &= df_validated[column_name].notna()
                    if mask.any():
                        msg = f"{column_name} value not allowed"
                        logger.warning(f"Allowed values validation failed for {column_name}: {mask.sum()} invalid values")
                        record_errors(mask, msg)

                if rule_type == 'group_consistency':
                    group_cols = validation.get('group_by', [])
                    target_col = validation.get('ensure_same')
                    if group_cols and target_col and target_col in df_validated.columns:
                        valid_group_cols = [c for c in group_cols if c in df_validated.columns]
                        if len(valid_group_cols) == len(group_cols):
                            nunique_counts = df_validated.groupby(valid_group_cols)[target_col].transform('nunique')
                            mask = nunique_counts > 1
                            if mask.any():
                                msg = f"{column_name} group inconsistency on {target_col}"
                                logger.warning(f"Group consistency validation failed for {column_name}: Column {target_col} must be the same within groups {valid_group_cols}")
                                record_errors(mask, msg)

                if rule_type == 'schema_reference_check':
                    schema_ref = validation.get('reference') or column_def.get('schema_reference')
                    if schema_ref:
                        mask = self._apply_schema_reference_validation(
                            df_validated,
                            column_name,
                            allow_null,
                            schema_ref,
                            data_section=validation.get('data_section'),
                            field_name=validation.get('field'),
                            exclude_codes=validation.get('exclude_codes', []),
                        )
                        if mask is not None and mask.any():
                            msg = f"{column_name} not in {schema_ref}"
                            record_errors(mask, msg)

                if rule_type == 'starts_with_schema_reference':
                    schema_ref = validation.get('reference') or column_def.get('schema_reference')
                    if schema_ref:
                        ref_data = self.schema_data.get(f'{schema_ref}_data', {})
                        allowed_codes = self._get_schema_reference_allowed_codes(
                            ref_data,
                            data_section=validation.get('data_section'),
                            field_name=validation.get('field'),
                        )
                        if allowed_codes:
                            codes_regex = "|".join([re.escape(str(c)) for c in allowed_codes if c is not None])
                            pattern = f"^({codes_regex})"
                            mask = ~df_validated[column_name].astype(str).str.match(pattern, na=False)
                            if allow_null:
                                mask &= df_validated[column_name].notna()
                            if mask.any():
                                msg = f"{column_name} does not start with valid code from {schema_ref}"
                                logger.warning(f"Starts-with validation failed for {column_name}: {mask.sum()} invalid values")
                                record_errors(mask, msg)

            # Backward-compatible default schema_reference validation when no
            # explicit schema_reference_check rule is declared.
            has_explicit_schema_ref_rule = any(
                rule.get('type') == 'schema_reference_check' for rule in validation_rules
            )
            schema_ref = column_def.get('schema_reference')
            if schema_ref and not has_explicit_schema_ref_rule:
                mask = self._apply_schema_reference_validation(
                    df_validated, column_name, allow_null, schema_ref
                )
                if mask is not None and mask.any():
                    msg = f"{column_name} not in {schema_ref}"
                    record_errors(mask, msg)
        
        return df_validated

    def _normalize_validation_rules(self, validation: Any) -> List[Dict[str, Any]]:
        """Normalize validation config to a list of rule objects."""
        if isinstance(validation, list):
            return [rule for rule in validation if isinstance(rule, dict)]
        if isinstance(validation, dict):
            scalar_keys = {
                'pattern',
                'min_length',
                'max_length',
                'min_value',
                'max_value',
                'format',
                'allowed_values',
            }
            nested_rule_keys = {'schema_reference_check', 'starts_with_schema_reference'}
            rules: List[Dict[str, Any]] = []

            for key in scalar_keys:
                if key in validation:
                    rule = {'type': key, key: validation[key]}
                    if 'description' in validation:
                        rule['description'] = validation['description']
                    rules.append(rule)

            for key in nested_rule_keys:
                value = validation.get(key)
                if isinstance(value, dict):
                    rule = {'type': key, **value}
                    rules.append(rule)

            return rules
        return []

    def _apply_schema_reference_validation(
        self,
        df: pd.DataFrame,
        column_name: str,
        allow_null: bool,
        schema_ref: str,
        data_section: Optional[str] = None,
        field_name: Optional[str] = None,
        exclude_codes: Optional[List[str]] = None,
    ) -> Optional[pd.Series]:
        """Validate a column against allowed values from a referenced schema."""
        ref_data = self.schema_data.get(f'{schema_ref}_data', {})
        if not ref_data:
            return None

        allowed_codes = self._get_schema_reference_allowed_codes(
            ref_data,
            data_section=data_section,
            field_name=field_name,
        )
        if allowed_codes is not None:
            # Filter out excluded codes (e.g., pending status)
            if exclude_codes:
                # Get all aliases for excluded codes from approval schema
                excluded_values = set(exclude_codes)
                for entry in ref_data.get('approval', []):
                    if entry.get('code') in exclude_codes:
                        # Add all aliases and the status itself
                        excluded_values.update(entry.get('aliases', []))
                        if entry.get('status'):
                            excluded_values.add(entry.get('status'))
                
                # Filter allowed_codes to exclude pending values
                allowed_codes = [c for c in allowed_codes if c not in excluded_values]
            
            mask = ~df[column_name].isin(allowed_codes)
            if allow_null:
                mask &= df[column_name].notna()
            invalid_count = mask.sum()
            if invalid_count > 0:
                logger.warning(
                    f"Schema reference validation failed for {column_name}: "
                    f"{invalid_count} values not in {schema_ref}"
                )
            return mask

        if 'choices' in ref_data:
            allowed = ref_data.get('choices', [])
            mask = ~df[column_name].isin(allowed)
            if allow_null:
                mask &= df[column_name].notna()
            invalid_count = mask.sum()
            if invalid_count > 0:
                logger.warning(f"Schema reference validation failed for {column_name}: {invalid_count} invalid values")
            return mask
        
        return None

    def _get_schema_reference_allowed_codes(
        self,
        ref_data: Dict[str, Any],
        data_section: Optional[str] = None,
        field_name: Optional[str] = None,
    ) -> Optional[List[str]]:
        """
        Return allowed values from a referenced schema.

        Preference order:
        1. The explicitly requested `data_section` and `field_name`
        2. The schema's own `data_section` using the explicit field or `code`
        3. The first list containing dict rows with the explicit field or `code`
        """
        target_field = field_name or 'code'
        target_section = data_section or ref_data.get('data_section')

        if isinstance(target_section, str):
            rows = ref_data.get(target_section)
            if isinstance(rows, list):
                return [
                    item.get(target_field)
                    for item in rows
                    if isinstance(item, dict) and item.get(target_field)
                ]

        for key, value in ref_data.items():
            if isinstance(value, list) and value:
                first_item = value[0]
                if isinstance(first_item, dict) and target_field in first_item:
                    return [
                        item.get(target_field)
                        for item in value
                        if isinstance(item, dict) and item.get(target_field)
                    ]

        return None


def main():
    """Example usage of UniversalDocumentProcessor."""
    # Create sample data with new document type codes
    sample_data = {
        'Document_ID': ['DOC-001', 'DOC-001', 'DOC-002', 'DOC-003'],
        'Document_Title': ['Foundation Plan', 'Foundation Plan', 'Structural Design', 'MEP Design'],
        'Document_Revision': ['0', '1', '2', '1'],
        'Department': ['Civil', 'Civil', 'Structural', 'NA'],
        'Discipline': ['Civil', 'Structural', 'MEP', 'NA'],
        'Project_Code': ['CESL-22120', 'CESL-22120', 'NA', 'CESL-22120'],
        'Document_Type': ['DR', 'DR', 'SP', 'NA'],  # Using new codes: DR=Drawing, SP=Specification
        'Submission_Date': ['2024-01-15', '2024-01-20', '2024-02-01', pd.NaT],
        'Review_Status': ['Approved', 'Rejected', 'Pending', 'Approved'],
        'Review_Return_Actual_Date': ['2024-01-25', pd.NaT, '2024-02-15', '2024-02-20']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Initialize processor with explicit schema path
    processor = UniversalDocumentProcessor()
    schema_path = Path(__file__).parent.parent / "config" / "schemas" / "dcc_register_enhanced.json"
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
