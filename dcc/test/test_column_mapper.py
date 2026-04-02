#!/usr/bin/env python3
"""
Test script for universal_column_mapper.py
Uses Submittal and RFI Tracker Lists.xlsx with parameters from dcc_register_enhanced.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add workflow folder to path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

import pandas as pd
from universal_column_mapper import UniversalColumnMapper


def load_excel_with_schema_params(excel_file, schema_file):
    """Load Excel using parameters from dcc_register_enhanced.json"""
    
    # Load schema to get parameters
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    params = schema_data.get('parameters', {})
    
    # Extract parameters
    sheet_name = params.get('upload_sheet_name', 'Prolog Submittals ')
    header_row = params.get('header_row_index', 4)  # Already 0-indexed in schema
    start_col = params.get('start_col', 'P')
    end_col = params.get('end_col', 'AP')
    
    # Convert columns to usecols format for pandas
    # P:AP means columns P through AP
    usecols = f"{start_col}:{end_col}"
    
    print(f"📊 Loading Excel with schema parameters:")
    print(f"   File: {excel_file}")
    print(f"   Sheet: '{sheet_name}'")
    print(f"   Header row: {header_row} (0-indexed)")
    print(f"   Columns: {usecols}")
    print()
    
    # Load Excel
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        header=header_row,  # Use directly as 0-indexed
        usecols=usecols
    )
    
    return df, params


def test_column_mapper():
    """Test universal_column_mapper with actual Excel data"""
    
    # Paths
    base_path = Path(__file__).parent.parent
    excel_file = base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"
    schema_file = base_path / "config" / "schemas" / "dcc_register_enhanced.json"
    test_output_dir = base_path / "test"
    test_output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = test_output_dir / f"column_mapper_test_{timestamp}.txt"
    
    print("=" * 70)
    print("🧪 UNIVERSAL COLUMN MAPPER TEST")
    print("=" * 70)
    print()
    
    # Load Excel data
    try:
        df_raw, params = load_excel_with_schema_params(excel_file, schema_file)
        print(f"✅ Excel loaded successfully: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
        print()
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return False
    
    # Initialize column mapper
    print("🔧 Initializing UniversalColumnMapper...")
    mapper = UniversalColumnMapper(schema_file=str(schema_file))
    print("✅ Column mapper initialized")
    print()
    
    # Get raw headers
    raw_headers = list(df_raw.columns)
    print(f"📋 Raw Excel Headers ({len(raw_headers)}):")
    for i, h in enumerate(raw_headers, 1):
        print(f"   {i:2}. {h}")
    print()
    
    # Detect columns
    print("🔍 Detecting column mappings...")
    mapping_result = mapper.detect_columns(raw_headers)
    print()
    
    # Print mapping results
    print("📊 MAPPING RESULTS:")
    print("-" * 70)
    detected = mapping_result['detected_columns']
    unmatched = mapping_result['unmatched_headers']
    
    print(f"✅ Matched: {mapping_result['matched_count']} / {mapping_result['total_headers']}")
    print(f"❌ Unmatched: {len(unmatched)}")
    print(f"📈 Match rate: {mapping_result['match_rate']:.1%}")
    print()
    
    print("📝 DETECTED COLUMN MAPPINGS:")
    print("-" * 70)
    for header, mapping in detected.items():
        col_def = mapping['column_definition']
        schema_ref = col_def.get('schema_reference', '')
        data_type = col_def.get('data_type', '')
        
        print(f"   '{header}'")
        print(f"      → {mapping['mapped_column']} (score: {mapping['match_score']:.2f})")
        print(f"        type: {data_type}, schema_ref: {schema_ref}")
        
        # Show choices if available
        if 'choices' in mapping:
            choices = mapping['choices']
            desc_count = len(mapping.get('choice_descriptions', {}))
            print(f"        choices: {len(choices)} items ({desc_count} with descriptions)")
        print()
    
    if unmatched:
        print("❌ UNMATCHED HEADERS:")
        print("-" * 70)
        for h in unmatched:
            print(f"   - '{h}'")
        print()
    
    if mapping_result['missing_required']:
        print("⚠️  MISSING REQUIRED COLUMNS:")
        print("-" * 70)
        for col in mapping_result['missing_required']:
            print(f"   - {col}")
        print()
    
    # Test DataFrame renaming
    print("🔄 Testing DataFrame column renaming...")
    try:
        df_renamed = mapper.rename_dataframe_columns(df_raw.copy(), mapping_result)
        print(f"✅ DataFrame renamed: {df_renamed.shape[0]} rows x {df_renamed.shape[1]} columns")
        print(f"   New columns: {list(df_renamed.columns)[:10]}...")
        print()
    except Exception as e:
        print(f"❌ Error renaming DataFrame: {e}")
        df_renamed = None
    
    # Check schema references loaded
    print("📚 SCHEMA REFERENCES LOADED:")
    print("-" * 70)
    loaded_schemas = mapper.schema_loader.loaded_schemas
    for schema_name, schema_data in loaded_schemas.items():
        # Count items based on format
        if isinstance(schema_data, dict):
            if 'document' in schema_data:
                count = len(schema_data['document'])
                print(f"   ✅ {schema_name}: {count} document types")
            elif 'discipline' in schema_data:
                count = len(schema_data['discipline'])
                print(f"   ✅ {schema_name}: {count} disciplines")
            elif 'choices' in schema_data:
                count = len(schema_data['choices'])
                print(f"   ✅ {schema_name}: {count} choices (old format)")
            else:
                print(f"   ✅ {schema_name}: loaded")
    print()
    
    # Generate report
    print(f"📝 Generating test report: {report_file.name}")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("UNIVERSAL COLUMN MAPPER TEST REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Excel File: {excel_file}\n")
        f.write(f"Schema File: {schema_file}\n")
        f.write("\n")
        
        f.write("PARAMETERS FROM SCHEMA:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Sheet Name: {params.get('upload_sheet_name')}\n")
        f.write(f"Header Row: {params.get('header_row_index')}\n")
        f.write(f"Column Range: {params.get('start_col')}:{params.get('end_col')}\n")
        f.write("\n")
        
        f.write("RESULTS SUMMARY:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Headers: {mapping_result['total_headers']}\n")
        f.write(f"Matched: {mapping_result['matched_count']}\n")
        f.write(f"Unmatched: {len(unmatched)}\n")
        f.write(f"Match Rate: {mapping_result['match_rate']:.1%}\n")
        f.write(f"Missing Required: {len(mapping_result['missing_required'])}\n")
        f.write("\n")
        
        f.write("DETECTED MAPPINGS:\n")
        f.write("-" * 40 + "\n")
        for header, mapping in detected.items():
            f.write(f"{header} -> {mapping['mapped_column']} ({mapping['match_score']:.2f})\n")
        f.write("\n")
        
        if unmatched:
            f.write("UNMATCHED HEADERS:\n")
            f.write("-" * 40 + "\n")
            for h in unmatched:
                f.write(f"- {h}\n")
            f.write("\n")
        
        if mapping_result['missing_required']:
            f.write("MISSING REQUIRED:\n")
            f.write("-" * 40 + "\n")
            for col in mapping_result['missing_required']:
                f.write(f"- {col}\n")
            f.write("\n")
        
        f.write("SCHEMA REFERENCES:\n")
        f.write("-" * 40 + "\n")
        for schema_name in loaded_schemas.keys():
            f.write(f"- {schema_name}\n")
        f.write("\n")
        
        if df_renamed is not None:
            f.write("RENAME TEST:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Success: Yes\n")
            f.write(f"Shape: {df_renamed.shape}\n")
            f.write(f"Columns: {', '.join(list(df_renamed.columns)[:20])}\n")
            if len(df_renamed.columns) > 20:
                f.write(f"... and {len(df_renamed.columns) - 20} more\n")
        
        f.write("\n")
        f.write("=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n")
    
    print(f"✅ Report saved: {report_file}")
    print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    if mapping_result['match_rate'] > 0.8:
        print("✅ PASS: High match rate achieved")
    elif mapping_result['match_rate'] > 0.5:
        print("⚠️  WARNING: Moderate match rate - some columns may need attention")
    else:
        print("❌ FAIL: Low match rate - review column aliases in schema")
    
    return mapping_result['match_rate'] > 0.5


if __name__ == "__main__":
    success = test_column_mapper()
    sys.exit(0 if success else 1)
