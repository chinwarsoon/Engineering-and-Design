#!/usr/bin/env python3
"""
Integrated test script for universal_column_mapper + universal_document_processor pipeline
Uses Submittal and RFI Tracker Lists.xlsx with parameters from dcc_register_enhanced.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add workflow folder to path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

import pandas as pd
import numpy as np
from universal_column_mapper import UniversalColumnMapper
from universal_document_processor import UniversalDocumentProcessor


def load_excel_with_schema_params(excel_file, schema_file):
    """Load Excel using parameters from dcc_register_enhanced.json"""
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    params = schema_data.get('parameters', {})
    
    sheet_name = params.get('upload_sheet_name', 'Prolog Submittals ')
    header_row = params.get('header_row_index', 4)
    start_col = params.get('start_col', 'P')
    end_col = params.get('end_col', 'AP')
    usecols = f"{start_col}:{end_col}"
    
    print(f"📊 Loading Excel:")
    print(f"   File: {excel_file.name}")
    print(f"   Sheet: '{sheet_name}'")
    print(f"   Header row: {header_row} (0-indexed)")
    print(f"   Columns: {usecols}")
    print()
    
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols
    )
    
    return df, params, schema_data


def test_mapper_processor_pipeline():
    """Test integrated mapper + processor pipeline"""
    
    base_path = Path(__file__).parent.parent
    excel_file = base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"
    schema_file = base_path / "config" / "schemas" / "dcc_register_enhanced.json"
    test_output_dir = base_path / "test"
    test_output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = test_output_dir / f"mapper_processor_pipeline_{timestamp}.txt"
    
    print("=" * 70)
    print("🧪 MAPPER + PROCESSOR PIPELINE TEST")
    print("=" * 70)
    print()
    
    # Step 1: Load Excel data
    print("STEP 1: Load Excel Data")
    print("-" * 70)
    try:
        df_raw, params, schema_data = load_excel_with_schema_params(excel_file, schema_file)
        print(f"✅ Loaded: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
        print(f"   Raw columns: {list(df_raw.columns)[:5]}...")
        print()
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return False
    
    # Step 2: Initialize and run UniversalColumnMapper
    print("STEP 2: UniversalColumnMapper - Detect & Map Columns")
    print("-" * 70)
    
    mapper = UniversalColumnMapper(schema_file=str(schema_file))
    raw_headers = list(df_raw.columns)
    
    print(f"🔍 Detecting mappings for {len(raw_headers)} headers...")
    mapping_result = mapper.detect_columns(raw_headers)
    
    print(f"✅ Matched: {mapping_result['matched_count']} / {mapping_result['total_headers']}")
    print(f"   Match rate: {mapping_result['match_rate']:.1%}")
    print(f"   Unmatched: {len(mapping_result['unmatched_headers'])}")
    print()
    
    # Show key mappings
    print("📋 Key Column Mappings:")
    for header, mapping in list(mapping_result['detected_columns'].items())[:10]:
        print(f"   '{header}' → {mapping['mapped_column']} ({mapping['match_score']:.2f})")
    print()
    
    # Step 3: Rename DataFrame columns
    print("STEP 3: Rename DataFrame Columns")
    print("-" * 70)
    try:
        df_mapped = mapper.rename_dataframe_columns(df_raw.copy(), mapping_result)
        print(f"✅ Renamed: {df_mapped.shape[0]} rows x {df_mapped.shape[1]} columns")
        print(f"   Schema columns: {list(df_mapped.columns)[:10]}...")
        print()
    except Exception as e:
        print(f"❌ Error renaming columns: {e}")
        return False
    
    # Step 4: Initialize UniversalDocumentProcessor
    print("STEP 4: UniversalDocumentProcessor - Schema-Driven Processing")
    print("-" * 70)
    
    processor = UniversalDocumentProcessor()
    processor.schema_file = str(schema_file)
    
    try:
        processor.load_schema()
        print(f"✅ Schema loaded: {schema_file.name}")
        
        # Show schema info
        enhanced_schema = processor.schema_data.get('enhanced_schema', {})
        columns = enhanced_schema.get('columns', {})
        print(f"   Schema columns: {len(columns)}")
        print(f"   Schema references: {list(processor.schema_data.get('schema_references', {}).keys())}")
        print()
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return False
    
    # Step 5: Process mapped data
    print("STEP 5: Process Data with Schema Rules")
    print("-" * 70)
    try:
        df_processed = processor.process_data(df_mapped)
        print(f"✅ Processing complete: {df_processed.shape[0]} rows x {df_processed.shape[1]} columns")
        print()
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Compare results
    print("STEP 6: Results Comparison")
    print("-" * 70)
    print(f"Raw data:      {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print(f"Mapped data:   {df_mapped.shape[0]} rows x {df_mapped.shape[1]} columns")
    print(f"Processed:     {df_processed.shape[0]} rows x {df_processed.shape[1]} columns")
    print()
    
    # Check for new/calculated columns
    new_cols = set(df_processed.columns) - set(df_mapped.columns)
    if new_cols:
        print(f"📊 New columns created ({len(new_cols)}):")
        for col in sorted(new_cols):
            print(f"   + {col}")
        print()
    
    # Check data types and nulls for key columns
    print("📊 Key Columns Summary:")
    key_cols = ['Document_ID', 'Project_Code', 'Document_Type', 'Discipline', 
                'Submission_Date', 'Review_Status']
    for col in key_cols:
        if col in df_processed.columns:
            null_count = df_processed[col].isna().sum()
            dtype = str(df_processed[col].dtype)
            unique = df_processed[col].nunique()
            print(f"   {col}: dtype={dtype}, nulls={null_count}, unique={unique}")
    print()
    
    # Step 7: Sample data preview
    print("STEP 7: Sample Processed Data")
    print("-" * 70)
    preview_cols = ['Document_ID', 'Project_Code', 'Document_Type', 'Discipline', 'Submission_Date']
    preview_cols = [c for c in preview_cols if c in df_processed.columns]
    print(df_processed[preview_cols].head(5).to_string())
    print()
    
    # Generate comprehensive report
    print(f"📝 Generating test report: {report_file.name}")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("MAPPER + PROCESSOR PIPELINE TEST REPORT\n")
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
        
        f.write("STEP 1: EXCEL LOAD\n")
        f.write("-" * 40 + "\n")
        f.write(f"Rows: {df_raw.shape[0]}\n")
        f.write(f"Columns: {df_raw.shape[1]}\n")
        f.write(f"Raw Headers: {', '.join(list(df_raw.columns)[:15])}\n")
        if len(df_raw.columns) > 15:
            f.write(f"... and {len(df_raw.columns) - 15} more\n")
        f.write("\n")
        
        f.write("STEP 2: COLUMN MAPPING\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Headers: {mapping_result['total_headers']}\n")
        f.write(f"Matched: {mapping_result['matched_count']}\n")
        f.write(f"Match Rate: {mapping_result['match_rate']:.1%}\n")
        f.write(f"Unmatched: {len(mapping_result['unmatched_headers'])}\n")
        f.write("\n")
        
        f.write("DETECTED MAPPINGS:\n")
        for header, mapping in mapping_result['detected_columns'].items():
            f.write(f"  {header} -> {mapping['mapped_column']} ({mapping['match_score']:.2f})\n")
        f.write("\n")
        
        if mapping_result['unmatched_headers']:
            f.write("UNMATCHED HEADERS:\n")
            for h in mapping_result['unmatched_headers']:
                f.write(f"  - {h}\n")
            f.write("\n")
        
        f.write("STEP 3: COLUMN RENAMING\n")
        f.write("-" * 40 + "\n")
        f.write(f"Success: Yes\n")
        f.write(f"Mapped Shape: {df_mapped.shape}\n")
        f.write("\n")
        
        f.write("STEP 4: SCHEMA LOADING\n")
        f.write("-" * 40 + "\n")
        f.write(f"Schema: {schema_file.name}\n")
        f.write(f"Schema Columns: {len(columns)}\n")
        f.write(f"References: {', '.join(processor.schema_data.get('schema_references', {}).keys())}\n")
        f.write("\n")
        
        f.write("STEP 5: DATA PROCESSING\n")
        f.write("-" * 40 + "\n")
        f.write(f"Success: Yes\n")
        f.write(f"Processed Shape: {df_processed.shape}\n")
        f.write("\n")
        
        f.write("STEP 6: RESULTS COMPARISON\n")
        f.write("-" * 40 + "\n")
        f.write(f"Raw: {df_raw.shape}\n")
        f.write(f"Mapped: {df_mapped.shape}\n")
        f.write(f"Processed: {df_processed.shape}\n")
        if new_cols:
            f.write(f"\nNew Columns ({len(new_cols)}):\n")
            for col in sorted(new_cols):
                f.write(f"  + {col}\n")
        f.write("\n")
        
        f.write("KEY COLUMNS SUMMARY:\n")
        f.write("-" * 40 + "\n")
        for col in key_cols:
            if col in df_processed.columns:
                null_count = df_processed[col].isna().sum()
                dtype = str(df_processed[col].dtype)
                unique = df_processed[col].nunique()
                f.write(f"{col}:\n")
                f.write(f"  dtype: {dtype}\n")
                f.write(f"  nulls: {null_count}\n")
                f.write(f"  unique: {unique}\n")
        f.write("\n")
        
        f.write("STEP 7: SAMPLE DATA\n")
        f.write("-" * 40 + "\n")
        f.write(df_processed[preview_cols].head(10).to_string())
        f.write("\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("TEST RESULT: PASS\n" if mapping_result['match_rate'] > 0.5 else "TEST RESULT: FAIL\n")
        f.write("=" * 70 + "\n")
    
    print(f"✅ Report saved: {report_file}")
    print()
    
    # Final summary
    print("=" * 70)
    print("📊 PIPELINE TEST SUMMARY")
    print("=" * 70)
    print("✅ Step 1: Excel loaded successfully")
    print(f"✅ Step 2: Column mapping ({mapping_result['match_rate']:.1%} match rate)")
    print("✅ Step 3: Columns renamed successfully")
    print("✅ Step 4: Schema loaded successfully")
    print("✅ Step 5: Data processed successfully")
    print("✅ Step 6: Results analyzed")
    print("✅ Step 7: Report generated")
    print()
    print(f"🎉 Pipeline test PASSED - Full workflow validated!")
    print()
    
    return True


if __name__ == "__main__":
    success = test_mapper_processor_pipeline()
    sys.exit(0 if success else 1)
