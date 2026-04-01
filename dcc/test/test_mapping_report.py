import pandas as pd
import json
import sys
import os
from pathlib import Path
import logging

# Add workflow directory to path to import mapper
# Script is in dcc/test/, mapper is in dcc/workflow/
dcc_root = Path(__file__).parent.parent
sys.path.append(str(dcc_root / "workflow"))
from universal_column_mapper import UniversalColumnMapper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_report():
    # Paths
    dcc_root = Path(__file__).parent.parent
    schema_path = dcc_root / "config" / "schemas" / "dcc_register_enhanced.json"
    excel_path = dcc_root / "data" / "Submittal and RFI Tracker Lists.xlsx"
    sheet_name = "Prolog Submittals "
    
    # Initialize mapper
    mapper = UniversalColumnMapper()
    mapper.load_main_schema(str(schema_path))
    
    # Load Excel headers using range from schema
    logger.info(f"Loading headers from {excel_path} [{sheet_name}]")
    try:
        # Get parameters from schema
        params = mapper.main_schema.get('parameters', {})
        start_col = params.get('start_col', 'A')
        end_col = params.get('end_col', 'ZZ')
        header_row = params.get('header_row_index', 0)
        
        # Load only headers within range
        df_headers = pd.read_excel(
            excel_path, 
            sheet_name=sheet_name, 
            usecols=f"{start_col}:{end_col}",
            header=header_row,
            nrows=0
        )
        headers = df_headers.columns.tolist()
        logger.info(f"Extracted {len(headers)} headers from range {start_col}:{end_col} at row {header_row}")
    except Exception as e:
        logger.error(f"Failed to load Excel file: {e}")
        return
    
    # Run mapping detection
    result = mapper.detect_columns(headers)
    detected = result['detected_columns']
    unmatched = result['unmatched_headers']
    missing_required = result['missing_required']
    
    # Analyze results
    report = []
    report.append("# Column Mapping Analysis Report\n")
    report.append(f"**Source File**: `{excel_path.name}`")
    report.append(f"**Sheet**: `{sheet_name}`")
    report.append(f"**Total Headers**: {result['total_headers']}")
    report.append(f"**Successfully Matched**: {result['matched_count']}")
    report.append(f"**Match Rate**: {result['match_rate']:.2%}\n")
    
    report.append("## Detailed Mappings\n")
    report.append("| Excel Header | Matched Schema Column | Match Score | matched Alias |")
    report.append("| :--- | :--- | :--- | :--- |")
    
    low_confidence = []
    for header, mapping in detected.items():
        score = mapping['match_score']
        row = f"| {header} | **{mapping['mapped_column']}** | {score:.2f} | {mapping['matched_alias']} |"
        report.append(row)
        if score < 0.8:
            low_confidence.append((header, mapping['mapped_column'], score))
            
    report.append("\n## Low Confidence Matches (< 0.8)\n")
    if not low_confidence:
        report.append("*No low confidence matches found.*")
    else:
        report.append("| Excel Header | Mapped To | Score |")
        report.append("| :--- | :--- | :--- |")
        for header, col, score in low_confidence:
            report.append(f"| {header} | {col} | {score:.2f} |")
            
    report.append("\n## Missing Required Input Columns\n")
    if not missing_required:
        report.append("*All required input columns matched.*")
    else:
        report.append("> [!WARNING]")
        report.append("> The following required columns are NOT matched to the Excel file. They may be handled by the Document Processor later:")
        for col in missing_required:
            report.append(f"- {col}")
            
    report.append("\n## Unmatched Headers\n")
    if not unmatched:
        report.append("*All headers were matched.*")
    else:
        for header in unmatched:
            if not header.startswith("Unnamed:"):
                report.append(f"- {header}")
                
    # Identify missing schema columns (including calculated)
    enhanced_schema = mapper.main_schema.get('enhanced_schema', {})
    schema_columns = enhanced_schema.get('columns', {})
    matched_schema_cols = set(m['mapped_column'] for m in detected.values())
    
    missing_from_excel = []
    for col_name in schema_columns:
        if col_name not in matched_schema_cols:
            missing_from_excel.append(col_name)
            
    report.append("\n## Other Schema Columns Missing in Excel\n")
    if not missing_from_excel:
        report.append("*All schema columns found in Excel.*")
    else:
        for col in missing_from_excel:
            if col not in missing_required:
                report.append(f"- {col}")
            
    # Write report
    report_content = "\n".join(report)
    report_path = dcc_root / "test" / "mapping_analysis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info(f"Report generated at {report_path}")
    print(f"Report generated at {report_path}")

if __name__ == "__main__":
    generate_report()
