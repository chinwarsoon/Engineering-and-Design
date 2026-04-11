#!/usr/bin/env python3
"""
Document_ID Error Codes Test
=============================

Tests error code generation for Document_ID column using:
- IdentityDetector (P2xx) for ID validation
- CalculationDetector (C6xx) for composite calculation errors
- ValidationDetector (V5xx) for pattern/validation errors

Data Source: Submittal and RFI Tracker Lists.xlsx
Schema: dcc_register_enhanced.json
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add workflow path for imports
# Current location: workflow/processor_engine/error_handling/tests/
workflow_root = Path(__file__).parent.parent.parent.parent.parent  # dcc folder
sys.path.insert(0, str(workflow_root / "workflow"))
sys.path.insert(0, str(workflow_root / "workflow" / "processor_engine" / "error_handling"))

from detectors import (
    IdentityDetector,
    ValidationDetector,
    CalculationDetector,
    BusinessDetector,
    ProcessingPhase,
    ValidationRule,
)
from processor_engine import load_excel_data, CalculationEngine
from mapper_engine import ColumnMapperEngine
from schema_engine import SchemaValidator


class DocumentIDErrorTest:
    """Test Document_ID error code generation."""
    
    def __init__(self, data_path: str, schema_path: str):
        self.data_path = Path(data_path)
        self.schema_path = Path(schema_path)
        self.df = None  # Store DataFrame for value lookup
        self.results = {
            "test_date": datetime.now().isoformat(),
            "data_file": str(self.data_path),
            "schema_file": str(self.schema_path),
            "total_rows": 0,
            "errors_detected": [],
            "error_summary": {},
            "document_id_patterns": {},
            "data_values_with_errors": [],  # New: store data values
        }
    
    def load_data(self, nrows: int = 100) -> pd.DataFrame:
        """Load and map data from Excel file."""
        print(f"\n📊 Loading data from: {self.data_path}")
        
        # Load schema for parameters
        self.schema_validator = SchemaValidator(self.schema_path)
        resolved_schema = self.schema_validator.load_resolved_schema()
        effective_parameters = resolved_schema.get("parameters", {})
        
        # Load Excel data (raw)
        df_raw = load_excel_data(self.data_path, effective_parameters, nrows=nrows)
        print(f"   ✓ Loaded {len(df_raw)} rows (raw)")
        print(f"   Raw columns: {list(df_raw.columns)[:5]}...")
        
        # Step 2: Map columns using ColumnMapperEngine
        print("\n🗺️ Mapping columns...")
        mapper = ColumnMapperEngine()
        mapper.resolved_schema = resolved_schema
        
        mapping_out = mapper.map_dataframe(df_raw)
        df = mapping_out["renamed_df"]
        mapping_result = mapping_out["mapping_result"]
        
        print(f"   ✓ Mapping complete: {mapping_result['match_rate']:.1%} match rate")
        print(f"   Mapped columns: {list(df.columns)[:5]}...")
        
        self.results["total_rows"] = len(df)
        self.df = df  # Store for later value lookup
        self.resolved_schema = resolved_schema  # Store for processing
        
        return df
    
    def analyze_document_id(self, df: pd.DataFrame) -> dict:
        """Analyze Document_ID column for patterns and issues."""
        print("\n🔍 Analyzing Document_ID column...")
        
        analysis = {
            "total_rows": len(df),
            "null_count": 0,
            "empty_count": 0,
            "unique_count": 0,
            "pattern_counts": {},
            "invalid_formats": [],
        }
        
        if "Document_ID" not in df.columns:
            print("   ⚠️ Document_ID column not found - checking aliases...")
            # Check for aliases
            for col in df.columns:
                if "cor ref" in col.lower() or "document id" in col.lower():
                    print(f"   Found alias: {col}")
                    df = df.rename(columns={col: "Document_ID"})
                    break
        
        if "Document_ID" in df.columns:
            doc_id_col = df["Document_ID"]
            
            # Null/empty analysis
            analysis["null_count"] = doc_id_col.isna().sum()
            analysis["empty_count"] = (doc_id_col == "").sum()
            analysis["unique_count"] = doc_id_col.nunique()
            
            # Pattern analysis
            for idx, value in doc_id_col.items():
                if pd.isna(value) or value == "":
                    continue
                    
                val_str = str(value).strip()
                
                # Categorize by pattern
                if "-" in val_str:
                    parts = val_str.split("-")
                    pattern_key = f"{len(parts)}-part ID"
                    
                    # Check format validity
                    if len(parts) >= 3:
                        # Standard format: PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE
                        pattern_type = "Standard (5-part)"
                    elif len(parts) == 2:
                        pattern_type = "Short (2-part)"
                    else:
                        pattern_type = "Irregular"
                        analysis["invalid_formats"].append({
                            "row": idx,
                            "value": val_str,
                            "parts": parts,
                        })
                    
                    analysis["pattern_counts"][pattern_type] = \
                        analysis["pattern_counts"].get(pattern_type, 0) + 1
                else:
                    analysis["pattern_counts"]["No separator"] = \
                        analysis["pattern_counts"].get("No separator", 0) + 1
                    analysis["invalid_formats"].append({
                        "row": idx,
                        "value": val_str,
                        "issue": "Missing separator (-)",
                    })
        
        self.results["document_id_patterns"] = analysis
        print(f"   ✓ Analysis complete: {analysis['unique_count']} unique IDs")
        print(f"   - Null values: {analysis['null_count']}")
        print(f"   - Empty values: {analysis['empty_count']}")
        print(f"   - Pattern distribution: {analysis['pattern_counts']}")
        
        return analysis
    
    def run_identity_detector(self, df: pd.DataFrame) -> list:
        """Run IdentityDetector for P2xx error codes."""
        print("\n🛡️ Running IdentityDetector (P2xx)...")
        
        detector = IdentityDetector(enable_fail_fast=False)
        errors = detector.detect(df)
        
        # Filter Document_ID related errors
        doc_id_errors = [
            e for e in errors 
            if e.column == "Document_ID" or 
            (e.context and e.context.get("column") == "Document_ID")
        ]
        
        print(f"   ✓ Detected {len(doc_id_errors)} Document_ID errors")
        
        for error in doc_id_errors:
            self.results["errors_detected"].append({
                "detector": "IdentityDetector",
                "error_code": error.error_code,
                "message": error.message,
                "row": error.row,
                "column": error.column,
                "severity": error.severity,
                "context": error.context,
            })
            
            # Update summary
            code = error.error_code
            self.results["error_summary"][code] = \
                self.results["error_summary"].get(code, 0) + 1
            
            # Capture data value with error
            self._capture_data_value_with_error(error, "IdentityDetector")
        
        return doc_id_errors
    
    def _capture_data_value_with_error(self, error, detector_name: str):
        """Capture the actual data value that has an error."""
        if self.df is None or error.row is None:
            return
        
        try:
            # Get Document_ID value from the row
            if "Document_ID" in self.df.columns and error.row in self.df.index:
                doc_id_value = self.df.at[error.row, "Document_ID"]
                
                # Get additional context values if available
                context_info = error.context if hasattr(error, 'context') else {}
                
                self.results["data_values_with_errors"].append({
                    "row": error.row,
                    "document_id": str(doc_id_value) if pd.notna(doc_id_value) else "NULL",
                    "error_code": error.error_code,
                    "detector": detector_name,
                    "message": error.message,
                    "severity": error.severity,
                    "context": context_info,
                })
        except Exception:
            pass  # Skip if can't retrieve value
    
    def run_validation_detector(self, df: pd.DataFrame) -> list:
        """Run ValidationDetector for V5xx error codes."""
        print("\n🛡️ Running ValidationDetector (V5xx)...")
        
        # Create validation rules for Document_ID
        rules = {
            "Document_ID": [
                ValidationRule(
                    column="Document_ID",
                    rule_type="pattern",
                    params={
                        "pattern": r"^[A-Z0-9-]+$",
                        "description": "Uppercase, numeric, and hyphens only",
                    },
                ),
                ValidationRule(
                    column="Document_ID",
                    rule_type="required",
                    params={
                        "description": "Document_ID cannot be null or empty",
                    },
                ),
            ]
        }
        
        detector = ValidationDetector(enable_fail_fast=False)
        
        # Pass rules through context
        context = {"validation_rules": rules}
        errors = detector.detect(df, context=context)
        
        # Filter Document_ID related errors
        doc_id_errors = [
            e for e in errors 
            if e.column == "Document_ID"
        ]
        
        print(f"   ✓ Detected {len(doc_id_errors)} validation errors")
        
        for error in doc_id_errors:
            self.results["errors_detected"].append({
                "detector": "ValidationDetector",
                "error_code": error.error_code,
                "message": error.message,
                "row": error.row,
                "column": error.column,
                "severity": error.severity,
                "context": error.context,
            })
            
            code = error.error_code
            self.results["error_summary"][code] = \
                self.results["error_summary"].get(code, 0) + 1
            
            # Capture data value with error
            self._capture_data_value_with_error(error, "ValidationDetector")
        
        return doc_id_errors
    
    def run_calculation_detector(self, df: pd.DataFrame) -> list:
        """Run CalculationDetector for C6xx error codes."""
        print("\n🛡️ Running CalculationDetector (C6xx)...")
        
        # Define calculation dependencies for Document_ID
        calculations = [
            {
                "target_column": "Document_ID",
                "calculation_type": "composite",
                "input_columns": [
                    "Project_Code",
                    "Facility_Code",
                    "Document_Type",
                    "Discipline",
                    "Document_Sequence_Number",
                ],
            },
        ]
        
        detector = CalculationDetector(enable_fail_fast=False)
        
        # Pass calculations through context
        context = {"calculations": calculations}
        errors = detector.detect(df, context=context)
        
        # Filter Document_ID related errors
        doc_id_errors = [
            e for e in errors 
            if e.column == "Document_ID" or 
            (e.context and e.context.get("target_column") == "Document_ID")
        ]
        
        print(f"   ✓ Detected {len(doc_id_errors)} calculation errors")
        
        for error in doc_id_errors:
            self.results["errors_detected"].append({
                "detector": "CalculationDetector",
                "error_code": error.error_code,
                "message": error.message,
                "row": error.row,
                "column": error.column,
                "severity": error.severity,
                "context": error.context,
            })
            
            code = error.error_code
            self.results["error_summary"][code] = \
                self.results["error_summary"].get(code, 0) + 1
            
            # Capture data value with error
            self._capture_data_value_with_error(error, "CalculationDetector")
        
        return doc_id_errors
    
    def run_business_detector(self, df: pd.DataFrame) -> list:
        """Run BusinessDetector orchestrator for all phase errors."""
        print("\n🛡️ Running BusinessDetector (Orchestrator)...")
        
        detector = BusinessDetector(enable_fail_fast=False)
        
        # Run full detection across all phases (returns dict of phase -> errors)
        phase_errors = detector.detect(df)
        
        # Flatten all errors from all phases
        all_errors = []
        for phase, errors in phase_errors.items():
            all_errors.extend(errors)
        
        # Filter Document_ID related
        doc_id_errors = [
            e for e in all_errors 
            if e.column == "Document_ID" or 
            (e.context and 
             (e.context.get("column") == "Document_ID" or
              e.context.get("target_column") == "Document_ID"))
        ]
        
        print(f"   ✓ BusinessDetector found {len(doc_id_errors)} Document_ID errors")
        
        # Add to results
        for error in doc_id_errors:
            self.results["errors_detected"].append({
                "detector": "BusinessDetector",
                "error_code": error.error_code,
                "message": error.message,
                "row": error.row,
                "column": error.column,
                "severity": error.severity,
                "context": error.context,
            })
            
            code = error.error_code
            self.results["error_summary"][code] = \
                self.results["error_summary"].get(code, 0) + 1
            
            # Capture data value with error
            self._capture_data_value_with_error(error, "BusinessDetector")
        
        return doc_id_errors
    
    def generate_report(self) -> str:
        """Generate test report."""
        print("\n" + "=" * 80)
        print("📋 DOCUMENT_ID ERROR CODES TEST REPORT")
        print("=" * 80)
        
        report_lines = [
            "# Document_ID Error Codes Test Report",
            "",
            f"**Test Date:** {self.results['test_date']}",
            f"**Data File:** {self.results['data_file']}",
            f"**Schema File:** {self.results['schema_file']}",
            "",
            "## Test Summary",
            "",
            f"- **Total Rows Analyzed:** {self.results['total_rows']}",
            f"- **Total Errors Detected:** {len(self.results['errors_detected'])}",
            f"- **Unique Error Codes:** {len(self.results['error_summary'])}",
            "",
            "## Document_ID Pattern Analysis",
            "",
        ]
        
        patterns = self.results.get("document_id_patterns", {})
        report_lines.extend([
            f"- **Total Rows:** {patterns.get('total_rows', 0)}",
            f"- **Null Values:** {patterns.get('null_count', 0)}",
            f"- **Empty Values:** {patterns.get('empty_count', 0)}",
            f"- **Unique IDs:** {patterns.get('unique_count', 0)}",
            "",
            "### Pattern Distribution",
            "",
        ])
        
        for pattern, count in patterns.get("pattern_counts", {}).items():
            report_lines.append(f"- {pattern}: {count}")
        
        report_lines.extend([
            "",
            "### Invalid Format Samples",
            "",
        ])
        
        invalid_samples = patterns.get("invalid_formats", [])[:5]  # First 5
        if invalid_samples:
            for sample in invalid_samples:
                report_lines.append(f"- Row {sample['row']}: `{sample['value']}` ({sample.get('issue', 'Irregular format')})")
        else:
            report_lines.append("- No invalid formats detected")
        
        report_lines.extend([
            "",
            "## Error Code Summary",
            "",
            "| Error Code | Count | Description |",
            "|------------|-------|-------------|",
        ])
        
        # Error code descriptions
        code_descriptions = {
            "P2-I-P-0201": "Document_ID uncertain/placeholder",
            "P2-I-P-0202": "Document_Revision missing",
            "P2-I-V-0203": "Duplicate Transmittal_Number",
            "P2-I-V-0204": "Document_ID format invalid",
            "V5-I-V-0501": "Pattern mismatch",
            "V5-I-V-0505": "Required field missing",
            "C6-C-C-0601": "Missing input columns for calculation",
            "C6-C-C-0606": "Mapping no match",
        }
        
        for code, count in sorted(self.results["error_summary"].items()):
            desc = code_descriptions.get(code, "Unknown error")
            report_lines.append(f"| {code} | {count} | {desc} |")
        
        # Add new section: Data Values with Errors
        report_lines.extend([
            "",
            "## Data Values with Error Codes",
            "",
            "This section lists actual Document_ID values from the data that triggered error codes.",
            "",
            "| Row | Document_ID Value | Error Code | Detector | Severity | Details |",
            "|-----|-------------------|------------|----------|----------|---------|",
        ])
        
        data_errors = self.results.get("data_values_with_errors", [])
        if data_errors:
            for err in data_errors[:30]:  # Show first 30
                doc_id = err.get("document_id", "N/A")
                # Truncate long values
                if len(doc_id) > 40:
                    doc_id = doc_id[:37] + "..."
                report_lines.append(
                    f"| {err.get('row', 'N/A')} | `{doc_id}` | {err.get('error_code', 'N/A')} | "
                    f"{err.get('detector', 'N/A')} | {err.get('severity', 'N/A')} | "
                    f"{err.get('message', 'N/A')[:50]}... |"
                )
            
            if len(data_errors) > 30:
                report_lines.append(f"| ... | ... | ... | ... | ... | _and {len(data_errors) - 30} more_ |")
        else:
            report_lines.append("| - | - | - | - | - | No data values with errors captured |")
        
        report_lines.extend([
            "",
            "## Detailed Error Log",
            "",
        ])
        
        for i, error in enumerate(self.results["errors_detected"][:20], 1):  # First 20
            report_lines.extend([
                f"### Error {i}",
                "",
                f"- **Detector:** {error['detector']}",
                f"- **Error Code:** {error['error_code']}",
                f"- **Message:** {error['message']}",
                f"- **Row:** {error['row']}",
                f"- **Column:** {error['column']}",
                f"- **Severity:** {error['severity']}",
                "",
            ])
        
        if len(self.results["errors_detected"]) > 20:
            report_lines.append(f"_... and {len(self.results['errors_detected']) - 20} more errors_")
        
        report_lines.extend([
            "",
            "## Conclusion",
            "",
            "This test demonstrates the error handling module's ability to detect Document_ID issues",
            "across multiple error code families (P2, V5, C6).",
            "",
            "### Error Code Families Applied:",
            "",
            "- **P2-I-xxx**: Identity validation errors",
            "- **V5-I-V-xxxx**: Field validation errors",
            "- **C6-C-C-xxxx**: Calculation/dependency errors",
            "",
            "---",
            "*Generated by DocumentIDErrorTest*",
        ])
        
        report = "\n".join(report_lines)
        
        # Print summary to console
        print(f"\n📊 Results:")
        print(f"   - Total Rows: {self.results['total_rows']}")
        print(f"   - Errors Detected: {len(self.results['errors_detected'])}")
        print(f"   - Error Codes Used: {list(self.results['error_summary'].keys())}")
        print(f"\n📝 Error Summary:")
        for code, count in sorted(self.results["error_summary"].items()):
            print(f"   - {code}: {count} occurrences")
        
        return report
    
    def save_report(self, report: str, output_path: str = None):
        """Save report to file."""
        if output_path is None:
            output_path = Path(__file__).parent / "test_document_id_error_report.md"
        else:
            output_path = Path(output_path)
        
        with open(output_path, "w") as f:
            f.write(report)
        
        print(f"\n💾 Report saved to: {output_path}")
        return output_path


def main():
    """Run Document_ID error codes test."""
    print("=" * 80)
    print("🧪 DOCUMENT_ID ERROR CODES TEST")
    print("=" * 80)
    
    # Define paths - navigate from workflow/processor_engine/error_handling/tests/ to dcc/
    base_path = Path(__file__).parent.parent.parent.parent.parent  # dcc folder
    data_path = base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"
    schema_path = base_path / "config" / "schemas" / "dcc_register_enhanced.json"
    
    print(f"\n📁 Base Path: {base_path}")
    print(f"📊 Data Path: {data_path}")
    print(f"📋 Schema Path: {schema_path}")
    
    # Verify files exist
    if not data_path.exists():
        print(f"\n❌ Error: Data file not found at {data_path}")
        return 1
    
    if not schema_path.exists():
        print(f"\n❌ Error: Schema file not found at {schema_path}")
        return 1
    
    # Create test runner
    test = DocumentIDErrorTest(
        data_path=str(data_path),
        schema_path=str(schema_path),
    )
    
    # Run tests
    try:
        # Load data (first 100 rows for testing)
        df = test.load_data(nrows=100)
        
        # Analyze Document_ID patterns
        test.analyze_document_id(df)
        
        # Run detectors
        test.run_identity_detector(df)
        test.run_validation_detector(df)
        test.run_calculation_detector(df)
        test.run_business_detector(df)
        
        # Generate and save report
        report = test.generate_report()
        report_path = test.save_report(report)
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print(f"📄 Report saved: {report_path}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
