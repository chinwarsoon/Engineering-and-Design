"""
Row Validator Module - Phase 4 Row-Level Validation

Implements cross-field business logic, temporal sequence checks, and
relational invariants per row_validation_workplan.md and dcc_register_rule.md.

Phases:
  Phase 1 - Anchor & Composite Identity (Document_ID segment match, anchor nulls)
  Phase 2 - Temporal & Logical Sequence (date inversion, closure logic, status inter-dep)
  Phase 3 - Relational Invariants & Aggregation (group consistency, revision progression)

Error Codes (Standardized per error_code_standardization_proposal.md):
  P1-A-P-0101  : Null anchor column
  P2-I-V-0204  : Document_ID composite mismatch
  L3-L-P-0301  : Date inversion (Submission_Date > Review_Return_Actual_Date)
  L3-L-V-0302  : LATEST_CLOSED_WITH_PLAN_DATE - Resubmission_Plan_Date not null when latest submission Closed=YES
  L3-L-V-0303  : RESUBMISSION_MISMATCH - REJ status without Resubmission_Required=YES/RESUBMITTED
  L3-L-V-0304  : OVERDUE_MISMATCH - Overdue status mismatch
  L3-L-V-0305  : VERSION_REGRESSION - Document_Revision decreases per Document_ID
  L3-L-V-0306  : REVISION_GAP - Submission_Session_Revision not sequential
  L3-L-V-0307  : CLOSED_WITH_RESUBMISSION - Submission_Closed=YES but Resubmission_Required=YES
  P4-I-V-0401  : REVISION_MISSING_FOR_VALID_ID - Document_Revision null/NA for valid Document_ID
  GROUP_INCONSISTENT    : Submission_Date inconsistent within Submission_Session
  INCONSISTENT_SUBJECT  : Submission_Session_Subject inconsistent within session
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .base import BaseDetector, DetectionResult

logger = logging.getLogger(__name__)

# Health score weights per dcc_register_rule.md Section 5.4
# Updated to use standardized error codes (Phase 2 - 2026-04-24)
# C13: Fallback weights — catalog (data_error_config.json health_score_impact) is SSOT.
# These are used only when error_catalog is not available in context.
ROW_ERROR_WEIGHTS: Dict[str, int] = {
    "ANCHOR_NULL":            25,
    "COMPOSITE_MISMATCH":     20,
    "L3-L-V-0305":            15,  # VERSION_REGRESSION
    "P4-I-V-0401":            20,  # REVISION_MISSING
    "GROUP_INCONSISTENT":     15,
    "INCONSISTENT_CLOSURE":   10,
    "L3-L-V-0302":            10,  # LATEST_CLOSED_WITH_PLAN_DATE
    "L3-L-V-0307":            10,  # CLOSED_WITH_RESUBMISSION
    "INCONSISTENT_SUBJECT":    5,
    "L3-L-V-0304":             5,  # OVERDUE_MISMATCH
    "L3-L-V-0306":             5,  # REVISION_GAP
}

# C10: Fallback anchor columns — schema (dcc_register_config.json is_anchor: true) is SSOT.
# Used only when blueprint.columns is not available.
ANCHOR_REQUIRED = [
    "Document_ID",
    "Project_Code",
    "Document_Type",
    "Submission_Date",
    "Document_Sequence_Number",
]

# C11: Fallback Document_ID segments — schema (Document_ID.calculation.source_columns) is SSOT.
# Used only when blueprint.columns is not available.
DOC_ID_SEGMENTS = [
    "Project_Code",
    "Facility_Code",
    "Document_Type",
    "Discipline",
    "Document_Sequence_Number",
]


class RowValidator(BaseDetector):
    """
    Row-level cross-field validator for Phase 4.

    Validates internal consistency across columns within each row.
    Runs after all calculations (P1-P3) are complete.
    """

    def __init__(self, logger_inst=None, enable_fail_fast: bool = False):
        """
        Initialize RowValidator.

        Args:
            logger_inst: StructuredLogger instance (breadcrumb: injected from engine)
            enable_fail_fast: Whether to raise on CRITICAL errors (default False for row validation)
        """
        super().__init__(layer="RV", logger=logger_inst, enable_fail_fast=enable_fail_fast)

    def _get_anchor_columns(self) -> List[str]:
        """
        C10: Return required anchor columns for row-level completeness check.
        Reads columns with is_anchor: true OR (required: true AND allow_null: false AND is_row_key: true)
        from context schema_data. Falls back to ANCHOR_REQUIRED constant.

        Note: is_anchor covers P1 anchor detector columns; is_row_key covers Document_ID and
        Submission_Date which are required for row-level cross-field validation.
        """
        schema_data = self._context.get("schema_data", {})
        columns = schema_data.get("columns", {})
        if columns:
            anchor_cols = [
                name for name, defn in columns.items()
                if isinstance(defn, dict) and (
                    defn.get("is_anchor")
                    or (defn.get("is_row_key") and defn.get("required") and not defn.get("allow_null", True))
                )
            ]
            if anchor_cols:
                return anchor_cols
        return ANCHOR_REQUIRED

    def _get_doc_id_segments(self) -> List[str]:
        """
        C11: Return Document_ID source columns from schema (SSOT) or fallback constant.
        Reads Document_ID.calculation.source_columns from context blueprint.
        """
        schema_data = self._context.get("schema_data", {})
        columns = schema_data.get("columns", {})
        doc_id_def = columns.get("Document_ID", {})
        source_cols = doc_id_def.get("calculation", {}).get("source_columns")
        if source_cols and isinstance(source_cols, list):
            return source_cols
        return DOC_ID_SEGMENTS

    def _get_row_error_weights(self) -> Dict[str, int]:
        """
        C13: Return error weights from error catalog (SSOT) or fallback constant.
        Reads health_score_impact from context error_catalog.
        """
        catalog = self._context.get("error_catalog", {})
        if catalog:
            weights = {}
            for code, entry in catalog.items():
                impact = entry.get("health_score_impact")
                if impact is not None:
                    weights[code] = abs(int(impact))
            if weights:
                return weights
        return ROW_ERROR_WEIGHTS.copy()

    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectionResult]:
        """
        Run all three row-validation phases and return aggregated results.

        Args:
            df: Fully processed DataFrame (post Phase 3)
            context: Optional dict with 'schema_data' key

        Returns:
            List of DetectionResult objects
        """
        self.clear_errors()
        if context:
            self.set_context(**context)

        # Phase 1 – Anchor & Composite Identity
        self._validate_anchor_completeness(df)
        self._validate_composite_identity(df)

        # Phase 2 – Temporal & Logical Sequence
        self._validate_date_sequence(df)
        self._validate_status_closure(df)
        self._validate_resubmission_logic(df)
        self._validate_overdue_status(df)

        # Phase 3 – Relational Invariants & Aggregation
        self._validate_group_consistency(df)
        self._validate_revision_progression(df)
        self._validate_session_revision_sequence(df)

        # Phase 4 – Data Quality & Null Handling
        self._validate_revision_completeness(df)

        logger.info(
            f"[RowValidator.detect] Complete — {len(self._errors)} row-level errors found"
        )
        return self.get_errors()

    def compute_row_health_weights(self) -> Dict[str, int]:
        """
        Return the error-weight map used for Data_Health_Score calculation.
        C13: Reads from error catalog (SSOT) when available.

        Returns:
            Dict mapping error key → deduction weight
        """
        return self._get_row_error_weights()

    # ------------------------------------------------------------------
    # Phase 1 – Anchor & Composite Identity
    # ------------------------------------------------------------------

    def _validate_anchor_completeness(self, df: pd.DataFrame) -> None:
        """
        Phase 1.1 – Verify no anchor column is null.

        Error: P1-A-P-0101 (HIGH)
        Breadcrumb: df → anchor columns (C10: schema-driven) → null mask → detect_error per row
        """
        # C10: Read anchor columns from schema (SSOT) or fallback constant
        anchor_cols = self._get_anchor_columns()
        for col in anchor_cols:
            if col not in df.columns:
                continue
            null_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
            for idx in df.index[null_mask]:
                self.detect_error(
                    error_code="P1-A-P-0101",
                    message=self._format_message("P1-A-P-0101", col=col),
                    row=idx,
                    column=col,
                    fail_fast=False,
                    additional_context={"error_key": "ANCHOR_NULL", "anchor_column": col},
                )

    def _validate_composite_identity(self, df: pd.DataFrame) -> None:
        """
        Phase 1.2 – Verify Document_ID matches its 5 constituent segments.

        Expected: {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}
        Affixes (e.g. _Reply, _ST607) are stripped before comparison using Document_ID_Affixes.

        Error: P2-I-V-0204 (HIGH)
        Breadcrumb: df['Document_ID'] → strip affix → split('-') → compare segments
        """
        if "Document_ID" not in df.columns:
            return

        # C11: Read Document_ID segments from schema (SSOT) or fallback constant
        doc_id_segments = self._get_doc_id_segments()
        available_segs = [c for c in doc_id_segments if c in df.columns]
        if len(available_segs) < 5:
            logger.warning(
                f"[RowValidator._validate_composite_identity] Only {len(available_segs)}/5 "
                f"segment columns available — skipping full composite check"
            )
            return

        for idx in df.index:
            doc_id = df.at[idx, "Document_ID"]
            if pd.isna(doc_id) or str(doc_id).strip() == "":
                continue  # Already caught by anchor check

            # Strip known affix if Document_ID_Affixes column exists
            base_id = str(doc_id)
            if "Document_ID_Affixes" in df.columns:
                affix = str(df.at[idx, "Document_ID_Affixes"]) if pd.notna(df.at[idx, "Document_ID_Affixes"]) else ""
                if affix and base_id.endswith(affix):
                    base_id = base_id[: -len(affix)]

            parts = base_id.split("-")
            if len(parts) < 5:
                self.detect_error(
                    error_code="P2-I-V-0204-B",
                    message=self._format_message("P2-I-V-0204-B"),
                    row=idx,
                    column="Document_ID",
                    fail_fast=False,
                    additional_context={"error_key": "COMPOSITE_MISMATCH", "base_id": base_id},
                )
                continue

            # Compare each segment against its source column
            mismatches = []
            warnings = []
            for seg_idx, col in enumerate(doc_id_segments):
                expected = str(df.at[idx, col]).strip() if pd.notna(df.at[idx, col]) else ""
                actual = parts[seg_idx].strip()
                if expected and actual != expected:
                    # Check for affix warning (segment is prefix of expected)
                    if expected.startswith(actual):
                        warnings.append(f"{col}: expected '{expected}' got '{actual}' (Affix detected)")
                    else:
                        mismatches.append(f"{col}: expected '{expected}' got '{actual}'")

            if warnings:
                self.detect_error(
                    error_code="P2-I-V-0204-W",
                    message=self._format_message("P2-I-V-0204-W"),
                    row=idx,
                    column="Document_ID",
                    fail_fast=False,
                    additional_context={
                        "error_key": "COMPOSITE_WARNING",
                        "base_id": base_id,
                        "warnings": warnings,
                    },
                )

            if mismatches:
                self.detect_error(
                    error_code="P2-I-V-0204-C",
                    message=self._format_message("P2-I-V-0204-C"),
                    row=idx,
                    column="Document_ID",
                    fail_fast=False,
                    additional_context={
                        "error_key": "COMPOSITE_MISMATCH",
                        "base_id": base_id,
                        "mismatches": mismatches,
                    },
                )

    def _get_rejected_code(self) -> str:
        """
        C14: Return the rejected approval code from schema (SSOT) or fallback 'REJ'.
        Reads from approval_code_schema filtered by status == 'Rejected'.
        """
        schema_data = self._context.get("schema_data", {})
        approval_codes = schema_data.get("approval_codes", [])
        for entry in approval_codes:
            if isinstance(entry, dict) and entry.get("status", "").lower() == "rejected":
                return entry.get("code", "REJ")
        return "REJ"

    # ------------------------------------------------------------------
    # Phase 2 – Temporal & Logical Sequence
    # ------------------------------------------------------------------

    def _validate_date_sequence(self, df: pd.DataFrame) -> None:
        """
        Phase 2.1 – Submission_Date must be <= Review_Return_Actual_Date.

        Error: L3-L-P-0301 (HIGH)
        Breadcrumb: df['Submission_Date'], df['Review_Return_Actual_Date'] → parse → compare
        """
        sub_col = "Submission_Date"
        ret_col = "Review_Return_Actual_Date"
        if sub_col not in df.columns or ret_col not in df.columns:
            return

        both_valid = df[sub_col].notna() & df[ret_col].notna()
        for idx in df.index[both_valid]:
            sub_dt = _parse_date(df.at[idx, sub_col])
            ret_dt = _parse_date(df.at[idx, ret_col])
            if sub_dt and ret_dt and ret_dt < sub_dt:
                self.detect_error(
                    error_code="L3-L-P-0301",
                    message=self._format_message("L3-L-P-0301"),
                    row=idx,
                    column=ret_col,
                    fail_fast=False,
                    additional_context={
                        "error_key": "DATE_INVERSION",
                        "submission_date": str(sub_dt.date()),
                        "return_date": str(ret_dt.date()),
                        "days_inverted": (sub_dt - ret_dt).days,
                    },
                )

    def _validate_status_closure(self, df: pd.DataFrame) -> None:
        """
        Phase 2.2 – If latest submission Closed=YES then Resubmission_Plan_Date must be NULL.
        Only applies to the latest submission revision — historical revisions may
        have both closed=YES and a plan date as benchmark for Delay_of_Resubmission.

        Error: LATEST_CLOSED_WITH_PLAN_DATE (HIGH)
        Breadcrumb: df['Submission_Closed'] == 'YES' → df['Resubmission_Plan_Date'].notna()
        → Latest_Submission_Date check excludes non-latest rows
        """
        closed_col = "Submission_Closed"
        plan_col = "Resubmission_Plan_Date"
        if closed_col not in df.columns or plan_col not in df.columns:
            return

        closed_mask = df[closed_col].astype(str).str.upper() == "YES"
        has_plan_mask = df[plan_col].notna() & (df[plan_col].astype(str).str.strip() != "")

        # Only flag if this is the latest submission revision — historical revisions
        # may legitimately have both closed=YES and a plan date for the next submission.
        submission_date_col = "Submission_Date"
        latest_submission_col = "Latest_Submission_Date"
        if latest_submission_col in df.columns and submission_date_col in df.columns:
            sub_dates = pd.to_datetime(df[submission_date_col], errors='coerce')
            latest_dates = pd.to_datetime(df[latest_submission_col], errors='coerce')
            is_latest_mask = sub_dates >= latest_dates
            query_mask = closed_mask & has_plan_mask & is_latest_mask
        else:
            query_mask = closed_mask & has_plan_mask

        for idx in df.index[query_mask]:
            self.detect_error(
                error_code="L3-L-V-0302",
                message=self._format_message("L3-L-V-0302"),
                row=idx,
                column=plan_col,
                fail_fast=False,
                additional_context={
                    "error_key": "LATEST_CLOSED_WITH_PLAN_DATE",
                    "plan_date": str(df.at[idx, plan_col]),
                },
            )

    def _validate_resubmission_logic(self, df: pd.DataFrame) -> None:
        """
        Phase 2.3 – Review_Status containing rejected code must have Resubmission_Required in (YES, RESUBMITTED).

        Error: RESUBMISSION_MISMATCH (MEDIUM)
        Breadcrumb: df['Review_Status'].str.contains(rejected_code) → df['Resubmission_Required']
        """
        status_col = "Review_Status"
        resub_col = "Resubmission_Required"
        if status_col not in df.columns or resub_col not in df.columns:
            return

        # C14: Read rejected code from approval_code_schema (SSOT)
        rejected_code = self._get_rejected_code()
        rej_mask = df[status_col].astype(str).str.upper().str.contains(rejected_code, na=False)
        valid_resub = {"YES", "RESUBMITTED"}
        bad_resub_mask = ~df[resub_col].astype(str).str.upper().isin(valid_resub)

        for idx in df.index[rej_mask & bad_resub_mask]:
            self.detect_error(
                error_code="L3-L-V-0303",
                message=self._format_message("L3-L-V-0303"),
                row=idx,
                column=resub_col,
                fail_fast=False,
                additional_context={
                    "error_key": "RESUBMISSION_MISMATCH",
                    "review_status": str(df.at[idx, status_col]),
                    "resubmission_required": str(df.at[idx, resub_col]),
                },
            )

    def _validate_overdue_status(self, df: pd.DataFrame) -> None:
        """
        Phase 2.4 – Validate Resubmission_Overdue_Status against Plan_Date and Required state.
        
        Logic (5-value matrix):
        1. OVERDUE_RESUBMITTED: Required=RESUBMITTED and Plan_Date < today
        2. RESUBMITTED: Required=RESUBMITTED and Plan_Date >= today
        3. NO: Required=NO or Submission_Closed=YES
        4. OVERDUE: Required=YES and Plan_Date < today
        5. ON_TRACK: Required=YES and Plan_Date >= today
        
        Error: L3-L-V-0304 (HIGH)
        """
        overdue_col = "Resubmission_Overdue_Status"
        plan_col = "Resubmission_Plan_Date"
        required_col = "Resubmission_Required"
        closed_col = "Submission_Closed"
        
        if any(col not in df.columns for col in [overdue_col, plan_col, required_col]):
            return
            
        current_date = pd.Timestamp.now().normalize()
        
        for idx in df.index:
            status = str(df.at[idx, overdue_col])
            required = str(df.at[idx, required_col]).upper()
            plan_date = df.at[idx, plan_col]
            closed = str(df.at[idx, closed_col]).upper() if closed_col in df.columns else "NO"
            
            # Skip if status is null/NaN — not yet calculated
            if pd.isna(df.at[idx, overdue_col]):
                continue
                
            # Parse plan_date
            plan_dt = _parse_date(plan_date) if pd.notna(plan_date) else None

            expected = "NO"
            if required == "RESUBMITTED":
                expected = "OVERDUE_RESUBMITTED" if plan_dt and plan_dt < current_date else "RESUBMITTED"
            elif closed == "YES" or required == "NO":
                expected = "NO"
            elif required == "YES":
                expected = "OVERDUE" if plan_dt and plan_dt < current_date else "ON_TRACK"
            
            if status != expected:
                self.detect_error(
                    error_code="L3-L-V-0304",
                    message=self._format_message("L3-L-V-0304", value=status, required=required, plan_date=str(plan_dt.date()) if plan_dt else "None"),
                    row=idx, column=overdue_col, fail_fast=False,
                    additional_context={
                        "actual": status,
                        "expected": expected,
                        "required": required,
                        "plan_date": str(plan_dt.date()) if plan_dt else "None"
                    }
                )

    # ------------------------------------------------------------------
    # Phase 3 – Relational Invariants & Aggregation
    # ------------------------------------------------------------------

    def _validate_group_consistency(self, df: pd.DataFrame) -> None:
        """
        Phase 3.1 – Within each (Submission_Session, Submission_Session_Revision) group:
          - Submission_Date must be uniform
          - Submission_Session_Subject must be uniform
          - Transmittal_Number must be uniform

        Error: GROUP_INCONSISTENT / INCONSISTENT_SUBJECT (MEDIUM)
        Breadcrumb: groupby(['Submission_Session','Submission_Session_Revision']) → nunique check
        """
        session_col = "Submission_Session"
        rev_col = "Submission_Session_Revision"
        if session_col not in df.columns:
            return

        group_cols = [c for c in [session_col, rev_col] if c in df.columns]

        checks = [
            ("Submission_Date",            "L3-L-V-0308",   "MEDIUM"),
            ("Transmittal_Number",         "L3-L-V-0308",   "MEDIUM"),
            ("Submission_Session_Subject", "L3-L-V-0309",   "MEDIUM"),
        ]

        for target_col, error_key, severity in checks:
            if target_col not in df.columns:
                continue
            # Exclude NA/empty from consistency check
            df_check = df[df[target_col].notna() & (df[target_col].astype(str).str.strip() != "NA")]
            if df_check.empty:
                continue
            nunique = df_check.groupby(group_cols)[target_col].transform("nunique")
            inconsistent_idx = df_check.index[nunique > 1]
            for idx in inconsistent_idx:
                self.detect_error(
                    error_code=error_key,
                    message=self._format_message(error_key, target_col=target_col, group_cols=group_cols),
                    row=idx,
                    column=target_col,
                    severity=severity,
                    fail_fast=False,
                    additional_context={
                        "error_key": error_key,
                        "target_column": target_col,
                        "group_columns": group_cols,
                    },
                )

    def _validate_revision_progression(self, df: pd.DataFrame) -> None:
        """
        Phase 3.2 – Document_Revision must not decrease for subsequent submissions
        of the same Document_ID (sorted by Submission_Date).

        Error: VERSION_REGRESSION (HIGH)
        Breadcrumb: groupby('Document_ID') → sort by Submission_Date → compare consecutive revisions
        """
        id_col = "Document_ID"
        rev_col = "Document_Revision"
        if id_col not in df.columns or rev_col not in df.columns:
            return

        sort_col = "Submission_Date" if "Submission_Date" in df.columns else None

        for doc_id, group in df.groupby(id_col):
            if len(group) <= 1:
                continue
            if sort_col:
                group = group.copy()
                group[sort_col] = pd.to_datetime(group[sort_col], errors='coerce')
                group = group.sort_values(sort_col)

            prev_rev_str: Optional[str] = None
            for idx in group.index:
                curr_rev_str = str(df.at[idx, rev_col]) if pd.notna(df.at[idx, rev_col]) else ""
                if not curr_rev_str or curr_rev_str.upper() == 'NA':
                    prev_rev_str = curr_rev_str
                    continue

                if prev_rev_str is not None and prev_rev_str:
                    try:
                        if _parse_revision(curr_rev_str) < _parse_revision(prev_rev_str):
                            self.detect_error(
                                error_code="L3-L-V-0305",
                                message=self._format_message("L3-L-V-0305", doc_id=doc_id, prev_rev=prev_rev_str, curr_rev=curr_rev_str),
                                row=idx,
                                column=rev_col,
                                fail_fast=False,
                                additional_context={
                                    "error_key": "VERSION_REGRESSION",
                                    "document_id": str(doc_id),
                                    "previous_revision": prev_rev_str,
                                    "current_revision": curr_rev_str,
                                },
                            )
                    except (ValueError, TypeError):
                        pass  # Non-comparable revision formats — skip

                prev_rev_str = curr_rev_str

    def _validate_session_revision_sequence(self, df: pd.DataFrame) -> None:
        """
        Phase 3.3 – Submission_Session_Revision should be continuous (no gaps)
        within each Submission_Session.

        Error: REVISION_GAP (LOW)
        Breadcrumb: groupby('Submission_Session') → sorted unique revisions → gap detection
        """
        session_col = "Submission_Session"
        rev_col = "Submission_Session_Revision"
        if session_col not in df.columns or rev_col not in df.columns:
            return

        for session_id, group in df.groupby(session_col):
            revisions = (
                group[rev_col]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )
            # Only check numeric 2-digit revisions
            numeric_revs = []
            for r in revisions:
                try:
                    numeric_revs.append(int(r))
                except ValueError:
                    pass

            if len(numeric_revs) < 2:
                continue

            numeric_revs.sort()
            for i in range(1, len(numeric_revs)):
                if numeric_revs[i] - numeric_revs[i - 1] > 1:
                    # Flag first row of this session as representative
                    first_idx = group.index[0]
                    self.detect_error(
                        error_code="L3-L-V-0306",
                        message=self._format_message("L3-L-V-0306", session_id=session_id, prev_rev=numeric_revs[i-1], curr_rev=numeric_revs[i]),
                        row=first_idx,
                        column=rev_col,
                        fail_fast=False,
                        additional_context={
                            "error_key": "REVISION_GAP",
                            "session_id": str(session_id),
                            "gap_from": numeric_revs[i - 1],
                            "gap_to": numeric_revs[i],
                        },
                    )

    # ------------------------------------------------------------------
    # Phase 4 – Data Quality & Null Handling
    # ------------------------------------------------------------------

    def _validate_revision_completeness(self, df: pd.DataFrame) -> None:
        """
        Phase 4.1 – Ensure valid Document_ID has a Latest_Revision.
        If Latest_Revision is null for a valid ID, it means manual input is required.

        Error: P4-I-V-0401 (CRITICAL)
        """
        if "Latest_Revision" not in df.columns or "Document_ID" not in df.columns:
            return

        # Valid ID = not null and has 5 segments (P2 standard)
        id_mask = df["Document_ID"].notna() & (df["Document_ID"].astype(str).str.count("-") == 4)
        
        # Null Revision = is null (not "NA", as "NA" for malformed is handled in calculation)
        null_rev_mask = df["Latest_Revision"].isna()
        
        for idx in df.index[id_mask & null_rev_mask]:
            self.detect_error(
                error_code="P4-I-V-0401",
                message=self._format_message("P4-I-V-0401"),
                row=idx,
                column="Document_Revision",  # Flag source column for user fix
                fail_fast=False,
                additional_context={
                    "error_key": "REVISION_MISSING",
                    "document_id": str(df.at[idx, "Document_ID"]),
                },
            )


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _parse_date(value: Any) -> Optional[datetime]:
    """
    Parse date from string, Timestamp, or datetime.

    Args:
        value: Raw date value from DataFrame cell

    Returns:
        datetime or None if unparseable
    """
    if pd.isna(value) or str(value).strip() in ("", "NA", "NaT"):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            continue
    return None


def _parse_revision(value: str) -> float:
    """
    Convert revision string to comparable float.

    Supports: numeric ('01'→1), alpha ('A'→1, 'B'→2), alphanumeric ('A1'→1.01).

    Args:
        value: Revision string

    Returns:
        Float for comparison
    """
    v = str(value).strip().upper()
    try:
        return float(v)
    except ValueError:
        pass
    if len(v) == 1 and v.isalpha():
        return float(ord(v) - ord("A") + 1)
    if len(v) >= 2 and v[0].isalpha():
        try:
            return (ord(v[0]) - ord("A") + 1) + float(v[1:]) / 100
        except ValueError:
            pass
    return float(hash(v) % 10000)
