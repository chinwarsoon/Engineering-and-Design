# Revision Notes: dcc_mdl.ipynb

## Overview
This notebook is a full DCC register ETL and reporting workflow.
It reads an uploaded Excel file, cleans, standardizes, computes key metrics, and exports processed results to Excel and DuckDB.
It then generates reporting outputs (monthly report and approval status visuals).

## Main change sections

### 1) Initialization and schema mapping
- Set global constants: `start_col='P'`, `end_col='AP'`, `header_row_index=4`, working-day durations.
- Imported pandas, numpy, ipywidgets, BDay, datetime.
- Added schema dictionary mapping raw column labels to standardized output names.
- Added approval code mapping dictionary for various review statuses.

### 2) Upload + sheet selection
- Added robust file upload handling for Colab, Tkinter, and manual path fallback.
- Reads Excel file and lists sheets.
- Interactive dropdown selection for sheet (target: `Prolog Submittals `) with header row 5.

### 3) Data load + clean
- Reads selected sheet with `usecols='P:AP'` and `header=4`.
- Drops all-empty rows and columns.
- Prints null-count summary for QA.

### 4) Data type check + column rename
- Calls `df_cleaned_and_filtered.info()`.
- Renames columns using schema mapping by first matching raw names.

### 5) Derived fields and updates (major transformation logic)
#### 5.1 Document ID
- Null-fills key component columns and builds `Document ID` concatenation.

#### 5.2 Submission Session + Revision
- Forward fills session values, converts to zero-padded string (`000001` style).
- Forward fills revisions grouped by session and revision, zero-pads to 2 digits.
- Adds aggregated `All Submission Sessions` per `Document ID` using `&&`.

#### 5.3 Submission dates
- Converts `Submission Date` to datetime; forward fills by session and revision.
- Creates `First Submittion Date` (min) and `Latest Submittion Date` (max) per `Document ID`.

#### 5.4 Revision updates
- Forward fills `Document Revision` across nested groups and fills missing as `NA`.
- Sets `Latest Revsion` by latest submission date where revision != NA.

#### 5.5 Review status and approval
- Forward fills `Review Status`; fills remainder with `Awaiting S.O. Review`.
- Derives `Latest Approval Status` as latest non-awaiting value per `Document ID`.
- Adds `Count of Submissions` per `Document ID`.

#### 5.6 Submitted by, title, and notes
- Forward fills and consolidates `Submitted by` per document.
- Forward fills + consolidates `Document Title` per document.
- Ensures `Notes` is non-null string.

#### 5.7 Review dates and plan date
- Forward fills `Review Return Actual Date` grouped by session/revision.
- Computes `Latest Approval Code` from mapping and updates `Submission Closed`.
- Calculates `Resubmission Plan Date` with business day offsets depending on status.

#### 5.8 Overdue/delay/durations
- Calculates `Resubmission Overdue Status` (Resubmitted/Overdue/NO) using today.
- Updates `Resubmission Required` from existing and closed status.
- Computes `Delay of Resubmission` from difference to previous same-document submission.
- Forward fills `Department` and `Review Comments` and fills NA.
- Computes working-day `Duration of Review` with `np.busday_count`.

### 6) Final QA and export
- Prints final DataFrame info + null-summary.
- Exports processed DataFrame to `Processed_Submittal_Tracker.xlsx`.
- Exports to DuckDB table and prints schema.

### 7) Monthly/report outputs
- Converts `This Submission Date` and `This Review Return Date` to datetime, creates `Submission Month-Year`.
- Creates `Monthly Submission.xlsx` with month-sheet split report.
- Builds approval summary `summary_df` grouped by `Doc ID`, `Discipline`.
- Plots overall status distribution, discipline subplots, approval trends stacked bar, and submission curve over time (PDF outputs).
- Downloads each PDF file in Colab environment.

### 8) Overdue review report
- Filters overdue rows where `This Revision Approval Status == Pending`, no review return date, and older than ~30 days.
- Exports `Overdue_Submission_Records.xlsx` for download.

### 9) Script consolidation
- Contains final cells to extract all notebook code and create `main.py` script.
- This is intended to produce a consolidated execution script.

## Observed behavior and key notes
- The notebook is not purely idempotent: it assumes specific raw column names and may fail if missing.
- Some conversions use `.astype(int)` and `.str.zfill`, which may error on non-numeric or NaN session values.
- The pipeline has both a `Document ID` and `Doc ID` variant in similar logic; this can create duplicates in downstream operations if running mixed sections.
- `Submission Closed` uses a row-level `.apply`, and approval mapping may produce null codes for unknown statuses.
- The data export and download steps are Colab-specific; local VS Code still writes files but no `files.download` UI.

## Recommendations
1. Add strict required-column validation early and fail clearly if missing.
2. Replace unsafe numeric casts with `pd.to_numeric(..., errors='coerce')` and check.
3. Consolidate repeated derivation logic into reusable helper functions.
4. Keep one canonical pipeline (document ID / prolog ID) and avoid duplicate variable names across steps.
5. Add quick `assert` checks before exports for expected output columns.

## Quick path for next changes
- If you want a cleaned production script, we can refactor this notebook into one script file with clear function boundaries and robust validation.
- We can also implement a lightweight param-driven pipeline so you can run on different DCC templates.
