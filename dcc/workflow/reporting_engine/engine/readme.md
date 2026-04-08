# Reporting Engine

A modular engine for generating processing reports and summaries for the DCC document processing pipeline. This engine provides comprehensive reporting functionality including processing summaries, column mapping reports, and validation status reports.

---

## Table of Contents

- [Module Structure](#module-structure)
- [Core Functions](#core-functions)
- [Usage Examples](#usage-examples)
- [Import Quick Reference](#import-quick-reference)

---

## Module Structure

```
reporting_engine/engine/
├── __init__.py          # Module exports
├── readme.md            # This documentation file
└── summary.py           # Processing summary generator
```

---

## Core Functions

### write_processing_summary(...)

**File:** `summary.py`

Generates a comprehensive text summary of the DCC processing pipeline execution.

| Attribute | Details |
|-----------|---------|
| **Input** | `summary_path` (Path): Output file path<br>`input_file` (Path): Input Excel file<br>`main_schema_path` (Path): Main schema JSON<br>`schema_results` (Dict): Validation results<br>`raw_columns` (List[str]): Raw input columns<br>`mapped_columns` (List[str]): Mapped columns<br>`processed_columns` (List[str]): Processed columns<br>`raw_shape` (Tuple[int, int]): Raw dimensions<br>`mapped_shape` (Tuple[int, int]): Mapped dimensions<br>`processed_shape` (Tuple[int, int]): Processed dimensions<br>`df_raw` (Any): Raw DataFrame<br>`df_mapped` (Any): Mapped DataFrame<br>`df_processed` (Any): Processed DataFrame<br>`mapping_result` (Dict): Column mapping details<br>`schema_reference_count` (int): Number of references<br>`csv_path` (Path): CSV export path<br>`excel_path` (Path): Excel export path |
| **Output** | None (writes to file) |
| **Function** | Generates comprehensive processing report |
| **Report Sections** | - Processing timestamp<br>- Input/output file paths<br>- Schema files used<br>- Dataset shapes<br>- Column mapping details with scores<br>- Null count summaries<br>- Warnings and issues |

---

## Usage Examples

### Generate Processing Summary

```python
from pathlib import Path
from reporting_engine.engine import write_processing_summary

# After pipeline processing
write_processing_summary(
    summary_path=Path("output/processing_summary.txt"),
    input_file=Path("data/input.xlsx"),
    main_schema_path=Path("config/schema.json"),
    schema_results={"ready": True, "references": []},
    raw_columns=["Col1", "Col2"],
    mapped_columns=["Column_1", "Column_2"],
    processed_columns=["Column_1", "Column_2", "Calculated"],
    raw_shape=(100, 2),
    mapped_shape=(100, 2),
    processed_shape=(100, 3),
    df_raw=df_raw,
    df_mapped=df_mapped,
    df_processed=df_processed,
    mapping_result={"match_rate": 1.0, "detected_columns": {}},
    schema_reference_count=3,
    csv_path=Path("output/data.csv"),
    excel_path=Path("output/data.xlsx"),
)
```

---

## Import Quick Reference

```python
# Full import
from reporting_engine.engine import write_processing_summary

# Via reporting_engine package
from reporting_engine import write_processing_summary
```

---

## Dependencies

- Python 3.10+
- Standard library: datetime, pathlib, typing

---

## Notes

- The reporting engine is designed to be called by the pipeline orchestrator after all processing engines complete
- It aggregates data from all engines (initiation, schema, mapper, processor) into a single summary report
- Output directory is created automatically if it doesn't exist
