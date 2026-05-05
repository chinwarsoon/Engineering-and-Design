"""Processing Summary Report Generator.

This module provides functions to generate comprehensive processing summary reports
for the DCC document processing pipeline.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def write_processing_summary(
    summary_path: Path,
    input_file: Path,
    main_schema_path: Path,
    schema_results: Dict[str, Any],
    raw_columns: List[str],
    mapped_columns: List[str],
    processed_columns: List[str],
    raw_shape: Tuple[int, int],
    mapped_shape: Tuple[int, int],
    processed_shape: Tuple[int, int],
    df_raw: Any,
    df_mapped: Any,
    df_processed: Any,
    mapping_result: Dict[str, Any],
    schema_reference_count: int,
    csv_path: Path,
    excel_path: Path,
) -> None:
    """Write comprehensive processing summary to file.

    This function generates a detailed text report of the DCC processing pipeline
    execution, including file paths, dataset shapes, column mappings, null counts,
    and any warnings or issues encountered.

    Args:
        summary_path: Path where the summary file will be written
        input_file: Path to the input Excel file
        main_schema_path: Path to the main schema JSON file
        schema_results: Results from schema validation including references
        raw_columns: List of column names from the raw input data
        mapped_columns: List of column names after schema mapping
        processed_columns: List of column names after processing
        raw_shape: Tuple of (rows, cols) for raw input data
        mapped_shape: Tuple of (rows, cols) for mapped data
        processed_shape: Tuple of (rows, cols) for processed data
        df_raw: Raw input DataFrame
        df_mapped: Mapped DataFrame
        df_processed: Processed DataFrame
        mapping_result: Column mapping result with detected_columns and match scores
        schema_reference_count: Number of schema references loaded
        csv_path: Path to the exported CSV file
        excel_path: Path to the exported Excel file

    Returns:
        None. Writes the summary to the specified file path.

    Example:
        >>> write_processing_summary(
        ...     summary_path=Path("output/summary.txt"),
        ...     input_file=Path("data/input.xlsx"),
        ...     main_schema_path=Path("config/schema.json"),
        ...     schema_results={"ready": True, "references": []},
        ...     raw_columns=["Col1", "Col2"],
        ...     mapped_columns=["Column_1", "Column_2"],
        ...     processed_columns=["Column_1", "Column_2", "Calculated"],
        ...     raw_shape=(100, 2),
        ...     mapped_shape=(100, 2),
        ...     processed_shape=(100, 3),
        ...     df_raw=df_raw,
        ...     df_mapped=df_mapped,
        ...     df_processed=df_processed,
        ...     mapping_result={"match_rate": 1.0, "detected_columns": {}},
        ...     schema_reference_count=3,
        ...     csv_path=Path("output/data.csv"),
        ...     excel_path=Path("output/data.xlsx"),
        ... )
    """
    detected_columns = mapping_result.get("detected_columns", {})
    unmatched_headers = mapping_result.get("unmatched_headers", [])
    missing_required = mapping_result.get("missing_required", [])
    processed_added_columns = [col for col in processed_columns if col not in mapped_columns]

    summary_path.parent.mkdir(parents=True, exist_ok=True)

    # Build schema files list
    schema_files = [str(main_schema_path)]
    schema_files.extend(
        item.get("resolved_path")
        for item in schema_results.get("references", [])
        if item.get("resolved_path")
    )
    schema_files = list(dict.fromkeys(schema_files))

    # Build warnings list
    warnings: List[str] = []
    warnings.extend(f"Missing required mapped column: {col}" for col in missing_required)
    warnings.extend(f"Unmatched input header: {header}" for header in unmatched_headers)
    warnings.extend(f"Column created during processing: {col}" for col in processed_added_columns)
    warnings.extend(schema_results.get("errors", []))

    # Calculate null counts
    raw_null_counts = {col: int(df_raw[col].isna().sum()) for col in df_raw.columns}
    mapped_null_counts = {col: int(df_mapped[col].isna().sum()) for col in df_mapped.columns}
    processed_null_counts = {col: int(df_processed[col].isna().sum()) for col in df_processed.columns}

    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write("Universal Document Processing Summary\n")
        handle.write("=" * 50 + "\n\n")
        handle.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        handle.write("Input and Output Files:\n")
        handle.write(f"  Input Data File: {input_file}\n")
        handle.write(f"  CSV Export: {csv_path}\n")
        handle.write(f"  Excel Export: {excel_path}\n")
        handle.write(f"  Summary Report: {summary_path}\n\n")

        handle.write("Schema Files Used:\n")
        for schema_file in schema_files:
            handle.write(f"  - {schema_file}\n")
        handle.write("\n")

        handle.write("Dataset Shapes:\n")
        handle.write(f"  Raw Input Shape: {raw_shape}\n")
        handle.write(f"  Mapped Data Shape: {mapped_shape}\n")
        handle.write(f"  Processed Data Shape: {processed_shape}\n\n")

        # Phase 5: Data Health KPI (Layer 5)
        error_summary = schema_results.get("error_summary", {})
        health_kpi = error_summary.get("health_kpi", {})
        if health_kpi:
            handle.write("Data Health Diagnostics:\n")
            handle.write(f"  Health Score: {health_kpi.get('score', 0):.1f}% ({health_kpi.get('grade', 'N/A')})\n")
            handle.write(f"  Total Row-Level Errors: {error_summary.get('total_errors', 0)}\n")
            handle.write(f"  Unique Error Types: {error_summary.get('unique_errors', 0)}\n")
            handle.write(f"  Affected Rows: {error_summary.get('affected_rows', 0)} / {processed_shape[0]}\n")
            
            counts = health_kpi.get("detailed_counts", {})
            if counts:
                severity_str = ", ".join([f"{k}: {v}" for k, v in counts.items() if v > 0])
                handle.write(f"  Severity Breakdown: {severity_str}\n")
            handle.write("\n")

        handle.write("Column Overview:\n")
        handle.write(f"  Column Mapping Success Rate: {mapping_result['match_rate']:.1%}\n")
        handle.write(f"  Matched Headers: {mapping_result['matched_count']} / {mapping_result['total_headers']}\n")
        handle.write(f"  Missing Required Columns: {len(mapping_result['missing_required'])}\n")
        handle.write(f"  Schema References Loaded: {schema_reference_count}\n\n")

        handle.write("Columns Read From Input:\n")
        for index, column_name in enumerate(raw_columns, start=1):
            handle.write(f"  {index:02d}. {column_name}\n")
        handle.write("\n")

        handle.write("Column Mapping Details:\n")
        for original_header in raw_columns:
            if original_header in detected_columns:
                mapped_column = detected_columns[original_header]["mapped_column"]
                matched_alias = detected_columns[original_header].get("matched_alias", "")
                match_score = detected_columns[original_header].get("match_score", 0.0)
                handle.write(
                    f"  - {original_header} -> {mapped_column} "
                    f"(alias='{matched_alias}', score={match_score:.2f})\n"
                )
            else:
                handle.write(f"  - {original_header} -> NOT MAPPED\n")
        handle.write("\n")

        handle.write("Mapped Columns After Rename:\n")
        for index, column_name in enumerate(mapped_columns, start=1):
            handle.write(f"  {index:02d}. {column_name}\n")
        handle.write("\n")

        handle.write("Processed Columns:\n")
        for index, column_name in enumerate(processed_columns, start=1):
            marker = " [ADDED DURING PROCESSING]" if column_name in processed_added_columns else ""
            handle.write(f"  {index:02d}. {column_name}{marker}\n")
        handle.write("\n")

        handle.write("Null Summary:\n")
        handle.write("  Raw Input Columns With Nulls:\n")
        raw_null_items = [(col, count) for col, count in raw_null_counts.items() if count > 0]
        if raw_null_items:
            for column_name, count in sorted(raw_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")

        handle.write("  Mapped Columns With Nulls:\n")
        mapped_null_items = [(col, count) for col, count in mapped_null_counts.items() if count > 0]
        if mapped_null_items:
            for column_name, count in sorted(mapped_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")

        handle.write("  Processed Columns With Nulls:\n")
        processed_null_items = [(col, count) for col, count in processed_null_counts.items() if count > 0]
        if processed_null_items:
            for column_name, count in sorted(processed_null_items, key=lambda item: (-item[1], item[0])):
                handle.write(f"    - {column_name}: {count}\n")
        else:
            handle.write("    - None\n")
        handle.write("\n")

        handle.write("Warnings and Potential Issues:\n")
        if warnings:
            for warning in warnings:
                handle.write(f"  - {warning}\n")
        else:
            handle.write("  - None\n")


def print_summary(results: Dict[str, Any], status_print_fn: Any = print) -> None:
    """Print processing summary to console.

    Args:
        results: Dictionary containing processing results.
        status_print_fn: Function to use for printing (defaults to print).
    """
    status_print_fn("\n" + "=" * 72)
    status_print_fn("DCC ENGINE PIPELINE - PROCESSING COMPLETE")
    status_print_fn("=" * 72)
    status_print_fn(f"Base Path: {results['base_path']}")
    status_print_fn(f"Schema File: {results['schema_path']}")
    status_print_fn(f"Excel File: {results['excel_path']}")
    status_print_fn(f"CSV Output: {results['csv_output_path']}")
    status_print_fn(f"Excel Output: {results['excel_output_path']}")
    status_print_fn(f"Raw Shape: {tuple(results['raw_shape'])}")
    status_print_fn(f"Mapped Shape: {tuple(results['mapped_shape'])}")
    status_print_fn(f"Processed Shape: {tuple(results['processed_shape'])}")
    status_print_fn(f"Matched Headers: {results['matched_count']} / {results['total_headers']}")
    status_print_fn(f"Match Rate: {results['match_rate']:.1%}")
    if results.get("missing_required"):
        status_print_fn(f"Missing Required Columns: {results['missing_required']}")
    status_print_fn("Ready: YES")
