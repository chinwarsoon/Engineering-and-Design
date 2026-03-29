#!/usr/bin/env python3
"""
Example demonstrating the rename_dataframe_columns method
"""

import pandas as pd
from universal_column_mapper import UniversalColumnMapper

def example_column_rename():
    """Demonstrate column renaming functionality"""
    
    print("🔧 Example: DataFrame Column Renaming")
    print("=" * 50)
    
    # 1. Create sample DataFrame with original Excel column names
    print("\n📋 Step 1: Original DataFrame with Excel Headers")
    df_original = pd.DataFrame({
        'CES_SALCON-SDC JV Cor Ref No': ['DOC-001', 'DOC-002', 'DOC-003'],
        'Document Description': ['Foundation Plan', 'Structural Design', 'MEP Layout'],
        'Rev ': ['0', '1', '2'],
        'Dept': ['Civil', 'Structural', 'MEP'],
        'Discipline': ['Civil', 'Structural', 'MEP'],
        'Date Submit': ['2024-01-15', '2024-01-20', '2024-02-01'],
        'SO Review Status': ['Approved', 'Rejected', 'Pending'],
        'Actual Date S.O. Response': ['2024-01-25', '2024-01-30', '2024-02-15']
    })
    
    print("Original DataFrame:")
    print(df_original.head())
    print(f"Original columns: {list(df_original.columns)}")
    
    # 2. Create mapping result (simulating detect_columns output)
    print("\n🔍 Step 2: Column Mapping Result")
    mapping_result = {
        'detected_columns': {
            'CES_SALCON-SDC JV Cor Ref No': {
                'mapped_column': 'Document_ID',
                'match_score': 1.00,
                'original_header': 'CES_SALCON-SDC JV Cor Ref No'
            },
            'Document Description': {
                'mapped_column': 'Document_Title',
                'match_score': 1.00,
                'original_header': 'Document Description'
            },
            'Rev ': {
                'mapped_column': 'Document_Revision',
                'match_score': 1.00,
                'original_header': 'Rev '
            },
            'Dept': {
                'mapped_column': 'Department',
                'match_score': 1.00,
                'original_header': 'Dept'
            },
            'Discipline': {
                'mapped_column': 'Discipline',
                'match_score': 1.00,
                'original_header': 'Discipline'
            },
            'Date Submit': {
                'mapped_column': 'Submission_Date',
                'match_score': 1.00,
                'original_header': 'Date Submit'
            },
            'SO Review Status': {
                'mapped_column': 'Review_Status',
                'match_score': 1.00,
                'original_header': 'SO Review Status'
            },
            'Actual Date S.O. Response': {
                'mapped_column': 'Review_Return_Actual_Date',
                'match_score': 1.00,
                'original_header': 'Actual Date S.O. Response'
            }
        },
        'unmatched_headers': [],
        'total_headers': 8,
        'matched_count': 8,
        'match_rate': 1.0
    }
    
    print("Mapping result:")
    for header, mapping in mapping_result['detected_columns'].items():
        print(f"  {header} -> {mapping['mapped_column']} (score: {mapping['match_score']:.2f})")
    
    # 3. Apply column renaming
    print("\n🔄 Step 3: Apply Column Renaming")
    mapper = UniversalColumnMapper()
    df_renamed = mapper.rename_dataframe_columns(df_original, mapping_result)
    
    print("Renamed DataFrame:")
    print(df_renamed.head())
    print(f"Renamed columns: {list(df_renamed.columns)}")
    
    # 4. Show the mapping dictionary created internally
    print("\n📊 Step 4: Internal Rename Dictionary")
    rename_dict = {}
    for header, mapping in mapping_result['detected_columns'].items():
        schema_column = mapping['mapped_column']
        if header in df_original.columns:
            rename_dict[header] = schema_column
    
    print("Rename dictionary:")
    for old, new in rename_dict.items():
        print(f"  '{old}' -> '{new}'")
    
    # 5. Demonstrate the benefit
    print("\n✅ Step 5: Benefits of Column Renaming")
    print("Before renaming:")
    print(f"  - Column names: Excel-specific, inconsistent")
    print(f"  - Schema processing: ❌ KeyError: 'Document_ID' not found")
    print(f"  - Null handling: ❌ Cannot apply group_by operations")
    
    print("\nAfter renaming:")
    print(f"  - Column names: Standardized, schema-compliant")
    print(f"  - Schema processing: ✅ Works perfectly")
    print(f"  - Null handling: ✅ Can apply forward_fill by Document_ID")
    
    # 6. Show how this enables document processing
    print("\n🔧 Step 6: Enabling Document Processing")
    print("With renamed columns, the universal document processor can:")
    print("  ✅ Apply null handling: df.groupby('Document_ID').ffill()")
    print("  ✅ Execute calculations: Use standard column names")
    print("  ✅ Validate data: Apply schema validation rules")
    print("  ✅ Generate exports: Consistent column naming")
    
    return df_original, df_renamed, mapping_result

if __name__ == "__main__":
    example_column_rename()
