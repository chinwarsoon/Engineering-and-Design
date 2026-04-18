"""
Row Validator Module - Phase 4 Row-Level Validation

Implements cross-field business logic, temporal sequence checks, and
relational invariants per row_validation_workplan.md and dcc_register_rule.md.

Phases:
  Phase 1 - Anchor & Composite Identity (Document_ID segment match, anchor nulls)
  Phase 2 - Temporal & Logical Sequence (date inversion, closure logic, status inter-dep)
  Phase 3 - Relational Invariants & Aggregation (group consistency, revision progression)

Error Codes (from dcc_register_rule.md Section 5):
  P1-A-P-0101  : Null anchor column
  P2-I-V-0204  : Document_ID composite mismatch
  L3-L-P-0301  : Date inversion (Submission_Date > Review_Return_Actual_Date)
  CLOSED_WITH_PLAN_DATE : Resubmission_Plan_Date not null when Submission_Closed=YES
  RESUBMISSION_MISMATCH : REJ status without Resubmission_Required=YES/RESUBMITTED
  OVERDUE_MISMATCH      : Overdue status mismatch
  GROUP_INCONSISTENT    : Submission_Date inconsistent within Submission_Session
  VERSION_REGRESSION    : Document_Revision decreases per Document_ID
  REVISION_GAP          : Submission_Session_Revision not sequential
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
ROW_ERROR_WEIGHTS: Dict[str, int] = {
    "ANCHOR_NULL":            25,
    "COMPOSITE_MISMATCH":     20,
    "GROUP_INCONSISTENT":     15,
    "VERSION_REGRESSION":     15,
    "INCONSISTENT_CLOSURE":   10,
    "CLOSED_WITH_PLAN_DATE":  10,
    "INCONSISTENT_SUBJECT":    5,
    "OVERDUE_MISMATCH":        5,
    "REVISION_GAP":            5,
}

# Anchor columns that must not be null (Section 4.1)
ANCHOR_REQUIRED = [
    "Document_ID",
    "Project_Code",
    "Document_Type",
    "Submission_Date",
    "Document_Sequence_Number",
]

# Document_ID constituent segments in order (Section 4.2)
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

        logger.info(
            f"[RowValidator.detect] Complete — {len(self._errors)} row-level errors found"
        )
        return self.get_errors()

    def compute_row_health_weights(self) -> Dict[str, int]:
        """
        Return the error-weight map used for Data_Health_Score calculation.

        Returns:
            Dict mapping error key → deduction weight
        """
        return ROW_ERROR_WEIGHTS.copy()

    # ------------------------------------------------------------------
    # Phase 1 – Anchor & Composite Identity
    # ------------------------------------------------------------------

    def _validate_anchor_completeness(self, df: pd.DataFrame) -> None:
        """
        Phase 1.1 – Verify no anchor column is null.

        Error: P1-A-P-0101 (HIGH)
        Breadcrumb: df → ANCHOR_REQUIRED columns → null mask → detect_error per row
        """
        for col in ANCHOR_REQUIRED:
            if col not in df.columns:
                continue
            null_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
            for idx in df.index[null_mask]:
                self.detect_error(
                    error_code="P1-A-P-0101",
                    message=f"Anchor column '{col}' is null at row {idx}",
                    row=idx,
                    column=col,
                    severity="HIGH",
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

        available_segs = [c for c in DOC_ID_SEGMENTS if c in df.columns]
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
                    error_code="P2-I-V-0204",
                    message=f"Document_ID '{doc_id}' has fewer than 5 segments at row {idx}",
                    row=idx,
                    column="Document_ID",
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={"error_key": "COMPOSITE_MISMATCH", "base_id": base_id},
                )
                continue

            # Compare each segment against its source column
            mismatches = []
            for seg_idx, col in enumerate(DOC_ID_SEGMENTS):
                expected = str(df.at[idx, col]).strip() if pd.notna(df.at[idx, col]) else ""
                actual = parts[seg_idx].strip()
                if expected and actual != expected:
                    mismatches.append(f"{col}: expected '{expected}' got '{actual}'")

            if mismatches:
                self.detect_error(
                    error_code="P2-I-V-0204",
                    message=f"Document_ID composite mismatch at row {idx}: {'; '.join(mismatches)}",
                    row=idx,
                    column="Document_ID",
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "error_key": "COMPOSITE_MISMATCH",
                        "base_id": base_id,
                        "mismatches": mismatches,
                    },
                )

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
                    message=(
                        f"Date inversion at row {idx}: "
                        f"Review_Return_Actual_Date ({ret_dt.date()}) < "
                        f"Submission_Date ({sub_dt.date()})"
                    ),
                    row=idx,
                    column=ret_col,
                    severity="HIGH",
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
        Phase 2.2 – If Submission_Closed=YES then Resubmission_Plan_Date must be NULL.

        Error: CLOSED_WITH_PLAN_DATE (HIGH)
        Breadcrumb: df['Submission_Closed'] == 'YES' → df['Resubmission_Plan_Date'].notna()
        """
        closed_col = "Submission_Closed"
        plan_col = "Resubmission_Plan_Date"
        if closed_col not in df.columns or plan_col not in df.columns:
            return

        closed_mask = df[closed_col].astype(str).str.upper() == "YES"
        has_plan_mask = df[plan_col].notna() & (df[plan_col].astype(str).str.strip() != "")

        for idx in df.index[closed_mask & has_plan_mask]:
            self.detect_error(
                error_code="CLOSED_WITH_PLAN_DATE",
                message=(
                    f"Submission_Closed=YES but Resubmission_Plan_Date is set "
                    f"('{df.at[idx, plan_col]}') at row {idx}"
                ),
                row=idx,
                column=plan_col,
                severity="HIGH",
                fail_fast=False,
                additional_context={
                    "error_key": "CLOSED_WITH_PLAN_DATE",
                    "plan_date": str(df.at[idx, plan_col]),
                },
            )

    def _validate_resubmission_logic(self, df: pd.DataFrame) -> None:
        """
        Phase 2.3 – Review_Status containing 'REJ' must have Resubmission_Required in (YES, RESUBMITTED).

        Error: RESUBMISSION_MISMATCH (MEDIUM)
        Breadcrumb: df['Review_Status'].str.contains('REJ') → df['Resubmission_Required']
        """
        status_col = "Review_Status"
        resub_col = "Resubmission_Required"
        if status_col not in df.columns or resub_col not in df.columns:
            return

        rej_mask = df[status_col].astype(str).str.upper().str.contains("REJ", na=False)
        valid_resub = {"YES", "RESUBMITTED"}
        bad_resub_mask = ~df[resub_col].astype(str).str.upper().isin(valid_resub)

        for idx in df.index[rej_mask & bad_resub_mask]:
            self.detect_error(
                error_code="RESUBMISSION_MISMATCH",
                message=(
                    f"Review_Status='{df.at[idx, status_col]}' (REJ) but "
                    f"Resubmission_Required='{df.at[idx, resub_col]}' at row {idx}"
                ),
                row=idx,
                column=resub_col,
                severity="MEDIUM",
                fail_fast=False,
                additional_context={
                    "error_key": "RESUBMISSION_MISMATCH",
                    "review_status": str(df.at[idx, status_col]),
                    "resubmission_required": str(df.at[idx, resub_col]),
                },
            )

    def _validate_overdue_status(self, df: pd.DataFrame) -> None:
        """
        Phase 2.4 – Resubmission_Overdue_Status must be 'Overdue' when today > Resubmission_Plan_Date
        and Submission_Closed != YES.

        Error: OVERDUE_MISMATCH (MEDIUM)
        Breadcrumb: today > Resubmission_Plan_Date & not closed → check Resubmission_Overdue_Status
        """
        plan_col = "Resubmission_Plan_Date"
        overdue_col = "Resubmission_Overdue_Status"
        closed_col = "Submission_Closed"
        if plan_col not in df.columns or overdue_col not in df.columns:
            return

        today = datetime.now()
        not_closed_mask = pd.Series(True, index=df.index)
        if closed_col in df.columns:
            not_closed_mask = df[closed_col].astype(str).str.upper() != "YES"

        has_plan_mask = df[plan_col].notna() & (df[plan_col].astype(str).str.strip() != "")

        for idx in df.index[has_plan_mask & not_closed_mask]:
            plan_dt = _parse_date(df.at[idx, plan_col])
            if plan_dt and plan_dt < today:
                raw_status = df.at[idx, overdue_col]
                # Skip rows where Resubmission_Overdue_Status is null/NaN — not yet calculated
                if pd.isna(raw_status):
                    continue
                actual_status = str(raw_status).strip()
                if actual_status.lower() not in ("overdue", "resubmitted"):
                    self.detect_error(
                        error_code="OVERDUE_MISMATCH",
                        message=(
                            f"Resubmission_Plan_Date ({plan_dt.date()}) is past but "
                            f"Resubmission_Overdue_Status='{actual_status}' at row {idx}"
                        ),
                        row=idx,
                        column=overdue_col,
                        severity="MEDIUM",
                        fail_fast=False,
                        additional_context={
                            "error_key": "OVERDUE_MISMATCH",
                            "plan_date": str(plan_dt.date()),
                            "overdue_status": actual_status,
                            "days_overdue": (today - plan_dt).days,
                        },
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
            ("Submission_Date",            "GROUP_INCONSISTENT",   "MEDIUM"),
            ("Transmittal_Number",         "GROUP_INCONSISTENT",   "MEDIUM"),
            ("Submission_Session_Subject", "INCONSISTENT_SUBJECT", "MEDIUM"),
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
                    message=(
                        f"'{target_col}' is inconsistent within group "
                        f"{group_cols} at row {idx}"
                    ),
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
                                error_code="VERSION_REGRESSION",
                                message=(
                                    f"Revision regression for Document_ID '{doc_id}': "
                                    f"'{prev_rev_str}' → '{curr_rev_str}' at row {idx}"
                                ),
                                row=idx,
                                column=rev_col,
                                severity="HIGH",
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
                        error_code="REVISION_GAP",
                        message=(
                            f"Revision gap in Submission_Session '{session_id}': "
                            f"{numeric_revs[i-1]} → {numeric_revs[i]}"
                        ),
                        row=first_idx,
                        column=rev_col,
                        severity="LOW",
                        fail_fast=False,
                        additional_context={
                            "error_key": "REVISION_GAP",
                            "session_id": str(session_id),
                            "gap_from": numeric_revs[i - 1],
                            "gap_to": numeric_revs[i],
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
