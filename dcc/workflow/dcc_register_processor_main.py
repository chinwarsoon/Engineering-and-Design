#!/usr/bin/env python3
"""
Main DCC processing pipeline:
1. project_setup_validation
2. schema_validation
3. universal_column_mapper
4. universal_document_processor
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from project_setup_validation import ProjectSetupValidator
from schema_validation import SchemaValidator, write_validation_status
from universal_column_mapper import UniversalColumnMapper
from universal_document_processor import UniversalDocumentProcessor


def _default_base_path() -> Path:
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent if script_dir.name.lower() == "workflow" else script_dir


def _default_schema_path(base_path: Path) -> Path:
    return base_path / "config" / "schemas" / "dcc_register_enhanced.json"


def _load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as handle:
        schema_data = json.load(handle)
    return schema_data.get("parameters", {})


def _default_excel_path(base_path: Path, params: Dict[str, Any]) -> Path:
    candidates = [
        params.get("upload_file_name"),
        params.get("linux_upload_file"),
        str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser().resolve()
        if path.is_file():
            return path

    xlsx_files = sorted(path for path in (base_path / "data").glob("*.xlsx") if path.is_file())
    if xlsx_files:
        return xlsx_files[0]

    raise FileNotFoundError("No Excel input file found. Use --excel-file to specify one.")


def _default_output_path(base_path: Path, params: Dict[str, Any]) -> Path:
    output_dir = Path(params.get("download_file_path", base_path / "output")).expanduser().resolve()
    return output_dir / "processed_dcc_universal.csv"


def _load_excel_data(excel_path: Path, params: Dict[str, Any], nrows: int | None = None) -> pd.DataFrame:
    sheet_name = params.get("upload_sheet_name", "Prolog Submittals ")
    header_row = params.get("header_row_index", 4)
    start_col = params.get("start_col", "P")
    end_col = params.get("end_col", "AP")
    usecols = f"{start_col}:{end_col}"

    return pd.read_excel(
        excel_path,
        sheet_name=sheet_name,
        header=header_row,
        usecols=usecols,
        nrows=nrows,
    )


def run_pipeline(
    base_path: Path,
    schema_path: Path,
    excel_path: Path | None = None,
    output_path: Path | None = None,
    nrows: int | None = None,
) -> Dict[str, Any]:
    setup_validator = ProjectSetupValidator(base_path=base_path)
    setup_results = setup_validator.validate()
    if not setup_results.get("ready"):
        raise ValueError(setup_validator.format_report(setup_results))

    schema_validator = SchemaValidator(schema_path)
    schema_results = schema_validator.validate()
    write_validation_status(schema_results)
    if not schema_results.get("ready"):
        raise ValueError(json.dumps(schema_results, indent=2))

    params = _load_schema_parameters(schema_path)
    excel_path = excel_path or _default_excel_path(base_path, params)
    output_path = output_path or _default_output_path(base_path, params)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_raw = _load_excel_data(excel_path, params, nrows=nrows)

    mapper = UniversalColumnMapper(schema_file=str(schema_path))
    mapping_result = mapper.detect_columns(df_raw.columns.tolist())
    df_mapped = mapper.rename_dataframe_columns(df_raw, mapping_result)

    processor = UniversalDocumentProcessor(schema_file=str(schema_path))
    df_processed = processor.process_data(df_mapped)
    df_processed.to_csv(output_path, index=False)

    return {
        "base_path": str(base_path),
        "schema_path": str(schema_path),
        "excel_path": str(excel_path),
        "output_path": str(output_path),
        "raw_shape": list(df_raw.shape),
        "mapped_shape": list(df_mapped.shape),
        "processed_shape": list(df_processed.shape),
        "matched_count": mapping_result["matched_count"],
        "total_headers": mapping_result["total_headers"],
        "match_rate": mapping_result["match_rate"],
        "missing_required": mapping_result["missing_required"],
        "ready": True,
    }


def main() -> int:
    base_path = _default_base_path()
    parser = argparse.ArgumentParser(description="Run the main DCC processing pipeline.")
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    parser.add_argument(
        "--schema-file",
        default=str(_default_schema_path(base_path)),
        help="Main schema file path.",
    )
    parser.add_argument("--excel-file", default=None, help="Excel file to process.")
    parser.add_argument("--output-file", default=None, help="CSV output file path.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit for processing.")
    parser.add_argument("--json", action="store_true", help="Print pipeline summary as JSON.")
    args = parser.parse_args()

    try:
        results = run_pipeline(
            base_path=Path(args.base_path).expanduser().resolve(),
            schema_path=Path(args.schema_file).expanduser().resolve(),
            excel_path=Path(args.excel_file).expanduser().resolve() if args.excel_file else None,
            output_path=Path(args.output_file).expanduser().resolve() if args.output_file else None,
            nrows=args.nrows,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"ready": False, "error": str(exc)}, indent=2))
        else:
            print(str(exc))
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("DCC REGISTER PROCESSOR PIPELINE")
        print("=" * 72)
        print(f"Base Path: {results['base_path']}")
        print(f"Schema File: {results['schema_path']}")
        print(f"Excel File: {results['excel_path']}")
        print(f"Output File: {results['output_path']}")
        print(f"Raw Shape: {tuple(results['raw_shape'])}")
        print(f"Mapped Shape: {tuple(results['mapped_shape'])}")
        print(f"Processed Shape: {tuple(results['processed_shape'])}")
        print(f"Matched Headers: {results['matched_count']} / {results['total_headers']}")
        print(f"Match Rate: {results['match_rate']:.1%}")
        if results["missing_required"]:
            print(f"Missing Required Columns: {results['missing_required']}")
        print("Ready: YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
