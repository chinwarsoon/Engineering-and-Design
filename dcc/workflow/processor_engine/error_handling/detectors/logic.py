"""
Logic Detector Module (L3xx - Layer 3)

Validates P3 (Priority 3) business logic:
- Date inversions (return before submission)
- Revision regression
- Status conflicts
- Overdue detection

Error Codes:
- L3-L-P-0301: Review return before submission (CRITICAL)
- L3-L-V-0302: Revision regression detected (HIGH)
- L3-L-V-0303: Status conflict (HIGH)
- L3-L-W-0304: Review overdue warning (WARNING)
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from .base import BaseDetector, DetectionResult


class LogicDetector(BaseDetector):
    """
    Detector for P3 business logic validation.
    
    Validates complex business rules and temporal relationships
    between columns.
    """
    
    # Error codes
    ERROR_DATE_INVERSION = "L3-L-P-0301"
    ERROR_REV_REGRESSION = "L3-L-V-0302"
    ERROR_STATUS_CONFLICT = "L3-L-V-0303"
    ERROR_OVERDUE_PENDING = "L3-L-W-0304"
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True
    ):
        """
        Initialize logic detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run all L3 business logic validations.
        
        Args:
            df: DataFrame to validate
            context: Additional context
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Run detection methods
        self._detect_date_inversion(df)
        self._detect_revision_regression(df)
        self._detect_status_conflict(df)
        self._detect_overdue_pending(df)
        
        return self.get_errors()
    
    def _detect_date_inversion(self, df: pd.DataFrame) -> None:
        """
        Detect date inversions where review return is before submission.
        
        Error: L3-L-P-0301 (CRITICAL - FAIL FAST)
        """
        submit_col = "Submission_Date"
        return_col = "Review_Return_Actual_Date"
        
        if submit_col not in df.columns or return_col not in df.columns:
            return
        
        # Check rows where both dates exist
        valid_mask = (
            df[submit_col].notna() & 
            df[return_col].notna() &
            (df[submit_col] != '') &
            (df[return_col] != '')
        )
        
        for idx in df[valid_mask].index:
            submit_date = self._parse_date(df.at[idx, submit_col])
            return_date = self._parse_date(df.at[idx, return_col])
            
            if submit_date and return_date:
                if return_date < submit_date:
                    self.detect_error(
                        error_code=self.ERROR_DATE_INVERSION,
                        message=f"Review return date before submission at row {idx}",
                        row=idx,
                        column=return_col,
                        severity="CRITICAL",
                        fail_fast=True,
                        additional_context={
                            "submission_date": str(submit_date),
                            "return_date": str(return_date),
                            "days_inverted": (submit_date - return_date).days,
                            "suggestion": "Verify dates - return cannot be before submission"
                        }
                    )
    
    def _detect_revision_regression(self, df: pd.DataFrame) -> None:
        """
        Detect revision regression (decreasing revision numbers).
        
        Error: L3-L-V-0302 (HIGH)
        """
        id_col = "Document_ID"
        rev_col = "Document_Revision"
        
        if id_col not in df.columns or rev_col not in df.columns:
            return
        
        # Group by Document_ID and check revision progression
        for doc_id, group in df.groupby(id_col):
            if len(group) <= 1:
                continue
            
            # Sort by submission date if available
            if "Submission_Date" in group.columns:
                group = group.sort_values("Submission_Date")
            
            prev_rev = None
            for idx in group.index:
                current_rev = str(df.at[idx, rev_col])
                
                # Skip if revision is missing
                if pd.isna(df.at[idx, rev_col]) or current_rev == '':
                    prev_rev = current_rev
                    continue
                
                # Try to parse as numeric revision
                try:
                    current_rev_num = self._parse_revision(current_rev)
                    
                    if prev_rev is not None:
                        prev_rev_num = self._parse_revision(prev_rev)
                        
                        if current_rev_num < prev_rev_num:
                            self.detect_error(
                                error_code=self.ERROR_REV_REGRESSION,
                                message=f"Revision regression for {doc_id}: {prev_rev} → {current_rev}",
                                row=idx,
                                column=rev_col,
                                severity="HIGH",
                                fail_fast=False,
                                additional_context={
                                    "document_id": str(doc_id),
                                    "previous_revision": str(prev_rev),
                                    "current_revision": str(current_rev),
                                    "suggestion": "Revision should not decrease"
                                }
                            )
                    
                    prev_rev = current_rev
                except (ValueError, TypeError):
                    # Can't parse revision - skip comparison
                    prev_rev = current_rev
    
    def _detect_status_conflict(self, df: pd.DataFrame) -> None:
        """
        Detect status conflicts:
        - Approved but marked for resubmission
        - Closed but has open review
        
        Error: L3-L-V-0303 (HIGH)
        """
        # Check approved + resubmission conflict
        approval_col = "Approval_Code"
        resubmit_col = "Resubmission_Required"
        
        if approval_col in df.columns and resubmit_col in df.columns:
            # Approved codes
            approved_values = ["Approved", "A", "1"]
            
            approved_mask = df[approval_col].isin(approved_values)
            resubmit_mask = df[resubmit_col].isin(["Yes", "Y", "1", "True", True])
            
            conflict_mask = approved_mask & resubmit_mask
            
            for idx in df[conflict_mask].index:
                self.detect_error(
                    error_code=self.ERROR_STATUS_CONFLICT,
                    message=f"Status conflict: Approved but marked for resubmission",
                    row=idx,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "approval_code": str(df.at[idx, approval_col]),
                        "resubmission_required": str(df.at[idx, resubmit_col]),
                        "conflict_type": "approved_but_resubmit",
                        "suggestion": "Document cannot be both approved and require resubmission"
                    }
                )
        
        # Check closed + active review conflict
        closed_col = "Submission_Closed"
        status_col = "Review_Status"
        
        if closed_col in df.columns and status_col in df.columns:
            closed_mask = df[closed_col].isin(["Yes", "Y", "1", "True", True])
            active_status = ["Pending", "In Review", "Submitted"]
            active_mask = df[status_col].isin(active_status)
            
            conflict_mask = closed_mask & active_mask
            
            for idx in df[conflict_mask].index:
                self.detect_error(
                    error_code=self.ERROR_STATUS_CONFLICT,
                    message=f"Status conflict: Closed but review still active",
                    row=idx,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "submission_closed": str(df.at[idx, closed_col]),
                        "review_status": str(df.at[idx, status_col]),
                        "conflict_type": "closed_but_active",
                        "suggestion": "Close submission only after review completes"
                    }
                )
    
    def _detect_overdue_pending(self, df: pd.DataFrame) -> None:
        """
        Detect overdue pending reviews.
        
        Error: L3-L-W-0304 (WARNING)
        """
        plan_col = "Review_Return_Plan_Date"
        actual_col = "Review_Return_Actual_Date"
        status_col = "Review_Status"
        
        # Check if we have plan date and status
        if plan_col not in df.columns or status_col not in df.columns:
            return
        
        # Pending status values
        pending_status = ["Pending", "In Review", "Submitted", "Reviewing"]
        pending_mask = df[status_col].isin(pending_status)
        
        # Has plan date
        has_plan_mask = df[plan_col].notna() & (df[plan_col] != '')
        
        # No actual return date
        no_actual_mask = True
        if actual_col in df.columns:
            no_actual_mask = df[actual_col].isna() | (df[actual_col] == '')
        
        overdue_mask = pending_mask & has_plan_mask & no_actual_mask
        
        today = datetime.now()
        
        for idx in df[overdue_mask].index:
            plan_date = self._parse_date(df.at[idx, plan_col])
            
            if plan_date and plan_date < today:
                days_overdue = (today - plan_date).days
                
                # Only warn if more than 1 day overdue
                if days_overdue > 1:
                    self.detect_error(
                        error_code=self.ERROR_OVERDUE_PENDING,
                        message=f"Review overdue by {days_overdue} days",
                        row=idx,
                        column=plan_col,
                        severity="WARNING",
                        fail_fast=False,
                        additional_context={
                            "planned_date": str(plan_date),
                            "days_overdue": days_overdue,
                            "review_status": str(df.at[idx, status_col]),
                            "suggestion": "Follow up with reviewer"
                        }
                    )
    
    def _parse_date(self, value: Any) -> Optional[datetime]:
        """
        Parse date from various formats.
        
        Args:
            value: Date value to parse
            
        Returns:
            Parsed datetime or None
        """
        if pd.isna(value) or value == '':
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_revision(self, value: str) -> float:
        """
        Parse revision string to number.
        
        Supports:
        - Numeric: "01" → 1, "10" → 10
        - Alphabetic: "A" → 1, "B" → 2
        - Alphanumeric: "A1" → 1.1
        
        Args:
            value: Revision string
            
        Returns:
            Numeric revision value
        """
        value = str(value).strip().upper()
        
        # Try numeric first
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try single letter (A=1, B=2, etc.)
        if len(value) == 1 and value.isalpha():
            return ord(value) - ord('A') + 1
        
        # Try letter + number (A1, B2, etc.)
        if len(value) >= 2 and value[0].isalpha():
            letter_val = ord(value[0]) - ord('A') + 1
            try:
                num_val = float(value[1:])
                return letter_val + num_val / 100
            except ValueError:
                pass
        
        # Fallback: return hash for consistent comparison
        return hash(value) % 10000
    
    def detect_L301_date_inversion(
        self,
        df: pd.DataFrame
    ) -> List[Tuple[int, str, str]]:
        """
        Public API: Check for date inversions.
        
        Args:
            df: DataFrame
            
        Returns:
            List of (row_index, submit_date, return_date) tuples
        """
        submit_col = "Submission_Date"
        return_col = "Review_Return_Actual_Date"
        
        if submit_col not in df.columns or return_col not in df.columns:
            return []
        
        inversions = []
        valid_mask = (
            df[submit_col].notna() & 
            df[return_col].notna() &
            (df[submit_col] != '') &
            (df[return_col] != '')
        )
        
        for idx in df[valid_mask].index:
            submit_date = self._parse_date(df.at[idx, submit_col])
            return_date = self._parse_date(df.at[idx, return_col])
            
            if submit_date and return_date and return_date < submit_date:
                inversions.append((idx, str(submit_date), str(return_date)))
        
        return inversions
    
    def detect_L302_rev_regression(
        self,
        df: pd.DataFrame
    ) -> Dict[str, List[Tuple[str, str, int]]]:
        """
        Public API: Check for revision regressions.
        
        Args:
            df: DataFrame
            
        Returns:
            Dict of doc_id -> [(prev_rev, curr_rev, row_index), ...]
        """
        id_col = "Document_ID"
        rev_col = "Document_Revision"
        
        if id_col not in df.columns or rev_col not in df.columns:
            return {}
        
        regressions = {}
        
        for doc_id, group in df.groupby(id_col):
            if len(group) <= 1:
                continue
            
            if "Submission_Date" in group.columns:
                group = group.sort_values("Submission_Date")
            
            prev_rev = None
            doc_regressions = []
            
            for idx in group.index:
                current_rev = str(df.at[idx, rev_col])
                
                if pd.isna(df.at[idx, rev_col]) or current_rev == '':
                    prev_rev = current_rev
                    continue
                
                try:
                    current_rev_num = self._parse_revision(current_rev)
                    
                    if prev_rev is not None:
                        prev_rev_num = self._parse_revision(prev_rev)
                        
                        if current_rev_num < prev_rev_num:
                            doc_regressions.append((prev_rev, current_rev, idx))
                    
                    prev_rev = current_rev
                except (ValueError, TypeError):
                    prev_rev = current_rev
            
            if doc_regressions:
                regressions[str(doc_id)] = doc_regressions
        
        return regressions
