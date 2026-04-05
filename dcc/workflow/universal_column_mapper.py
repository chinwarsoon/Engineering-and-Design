#!/usr/bin/env python3
"""
Universal Column Mapper
Implements fuzzy header detection and schema-driven validation for universal document processing.
"""

import json
import os
import re
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import pandas as pd
from schema_validation import SchemaLoader, validate_validation_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalColumnMapper:
    """Universal column mapper with fuzzy matching and schema-driven validation."""
    
    def __init__(self, schema_file: str = None):
        """
        Initialize universal column mapper.
        
        Args:
            schema_file: Path to main schema file
        """
        self.schema_file = schema_file
        self.schema_loader = SchemaLoader()
        self.main_schema = {}
        self.resolved_schema = {}
        
        if schema_file:
            self.load_main_schema(schema_file)
    
    def load_main_schema(self, schema_file: str):
        """
        Load main schema file after schema_validation.py has succeeded.
        
        Args:
            schema_file: Path to main schema file
        """
        try:
            is_validated, message = validate_validation_status(schema_file)
            if not is_validated:
                raise ValueError(message)

            self.schema_loader = SchemaLoader()
            self.schema_loader.set_main_schema_path(schema_file)
            self.main_schema = self.schema_loader.load_json_file(schema_file)
            self.resolved_schema = self.schema_loader.resolve_schema_dependencies(self.main_schema)
            logger.info("Schema dependencies resolved")
            
        except Exception as e:
            logger.error(f"Error loading main schema {schema_file}: {e}")
            raise
    
    def fuzzy_match_column(self, header: str, target_columns: List[str], threshold: float = 0.6) -> Tuple[str, float]:
        """
        Perform fuzzy matching between header and target columns.
        
        Args:
            header: Input header to match
            target_columns: List of possible target columns
            threshold: Minimum similarity score (0-1)
            
        Returns:
            Tuple of (best_match, similarity_score)
        """
        header_clean = self._normalize_string(header)
        best_match = ""
        best_score = 0.0
        
        for target in target_columns:
            target_clean = self._normalize_string(target)
            
            # Exact match
            if header_clean == target_clean:
                return target, 1.0
            
            # Fuzzy match using sequence matcher
            score = difflib.SequenceMatcher(None, header_clean, target_clean).ratio()
            if score > best_score and score >= threshold:
                best_match = target
                best_score = score
        
        return best_match, best_score
    
    def _normalize_string(self, text: str) -> str:
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
    
    def detect_columns(self, headers: List[str]) -> Dict[str, Dict]:
        """
        Detect and map input headers to schema columns.
        
        Args:
            headers: List of input headers
            
        Returns:
            Dictionary mapping detected columns with metadata
        """
        if not self.resolved_schema:
            raise ValueError("No schema loaded. Call load_main_schema() first.")
        
        enhanced_schema = self.resolved_schema.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        
        detected = {}
        unmatched = []
        missing_required = []
        
        # Track which schema columns were matched to ensure all required are found
        matched_column_names = set()
        
        for header in headers:
            best_match = None
            best_score = 0.0
            best_column_name = None
            
            # Try to match against each column's aliases
            for column_name, column_def in columns.items():
                if not isinstance(column_def, dict) or column_def.get('is_calculated', False):
                    continue
                aliases = column_def.get('aliases', [])
                match, score = self.fuzzy_match_column(header, aliases)
                
                if score > best_score:
                    best_match = match
                    best_score = score
                    best_column_name = column_name
            
            if best_score >= 0.6:  # Threshold for acceptance
                detected[header] = {
                    'mapped_column': best_column_name,
                    'original_header': header,
                    'match_score': best_score,
                    'matched_alias': best_match,
                    'column_definition': columns[best_column_name]
                }
                matched_column_names.add(best_column_name)
            else:
                unmatched.append(header)
                
        # Check for missing required columns (that are NOT calculated)
        for col_name, col_def in columns.items():
            is_required = col_def.get('required', False)
            is_calculated = col_def.get('is_calculated', False)
            if is_required and not is_calculated and col_name not in matched_column_names:
                missing_required.append(col_name)
                logger.warning(f"Required input column missing during mapping detection: {col_name}")
        
        # Add schema choices for categorical columns
        for header, mapping in detected.items():
            col_def = mapping['column_definition']
            if col_def.get('data_type') == 'categorical':
                schema_ref = col_def.get('schema_reference')
                if schema_ref:
                    schema_data = self.resolved_schema.get(f'{schema_ref}_data')
                    if schema_data:
                        # Find array key containing code/description objects (document, discipline, department, etc.)
                        array_key = None
                        for key in schema_data.keys():
                            if isinstance(schema_data[key], list) and len(schema_data[key]) > 0:
                                if isinstance(schema_data[key][0], dict) and 'code' in schema_data[key][0]:
                                    array_key = key
                                    break
                        
                        if array_key:
                            # Handle new format: array with code/description objects
                            mapping['choices'] = [item.get('code') for item in schema_data[array_key] if item.get('code')]
                            mapping['choice_descriptions'] = {item.get('code'): item.get('description') 
                                                                for item in schema_data[array_key] if item.get('code')}
                        # Handle old format: choices array
                        elif 'choices' in schema_data:
                            mapping['choices'] = schema_data.get('choices', [])
        
        return {
            'detected_columns': detected,
            'unmatched_headers': unmatched,
            'missing_required': missing_required,
            'total_headers': len(headers),
            'matched_count': len(detected),
            'match_rate': len(detected) / len(headers) if len(headers) > 0 else 0
        }
    
    def rename_dataframe_columns(self, df: pd.DataFrame, mapping_result: Dict) -> pd.DataFrame:
        """
        Rename DataFrame columns based on detected mapping.
        
        Args:
            df: Input DataFrame with original column names
            mapping_result: Result from detect_columns() method
            
        Returns:
            DataFrame with columns renamed to schema names
        """
        df_renamed = df.copy()
        
        # Create rename mapping
        rename_dict = {}
        for header, mapping in mapping_result['detected_columns'].items():
            schema_column = mapping['mapped_column']
            if header in df_renamed.columns:
                rename_dict[header] = schema_column
        
        # Apply renaming
        df_renamed = df_renamed.rename(columns=rename_dict)
        
        logger.info(f"Renamed {len(rename_dict)} columns to schema names")
        
        return df_renamed
    
    def get_column_bounds(self, data, detected_columns: Dict) -> Dict[str, Tuple[int, int]]:
        """
        Get non-null bounds for each detected column.
        
        Args:
            data: Input data (list of lists or similar)
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


def main():
    """Example usage of UniversalColumnMapper."""
    # Initialize mapper
    mapper = UniversalColumnMapper()
    
    # Load DCC enhanced schema
    schema_path = Path(__file__).parent / "config" / "dcc_register_enhanced.json"
    mapper.load_main_schema(schema_path)
    
    # Example headers
    sample_headers = [
        "CES_SALCON-SDC JV Cor Ref No",
        "Document Description", 
        "Rev ",
        "Dept",
        "Discipline",
        "Doc Type",
        "Prolog Submittal No.",
        "Date Submit",
        "SO Review Status"
    ]
    
    # Detect columns
    result = mapper.detect_columns(sample_headers)
    
    print("=== Column Detection Results ===")
    print(f"Total Headers: {result['total_headers']}")
    print(f"Matched: {result['matched_count']}")
    print(f"Match Rate: {result['match_rate']:.2%}")
    print(f"\nUnmatched Headers: {result['unmatched_headers']}")
    
    print("\n=== Detected Columns ===")
    for header, mapping in result['detected_columns'].items():
        print(f"{header} -> {mapping['mapped_column']} (score: {mapping['match_score']:.2f})")
        if 'choices' in mapping:
            print(f"  Choices: {', '.join(mapping['choices'][:5])}...")


if __name__ == "__main__":
    main()
