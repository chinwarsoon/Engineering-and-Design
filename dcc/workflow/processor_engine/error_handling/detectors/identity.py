"""
Identity Detector Module (P2xx - Layer 3)

Validates P2 (Priority 2) identity columns:
- Document_ID, Document_Revision
- Document_Title
- Transmittal_Number

Error Codes:
- P2-I-P-0201: Document_ID uncertain (CRITICAL)
- P2-I-P-0202: Document_Revision missing (CRITICAL)
- P2-I-V-0203: Duplicate Transmittal_Number (HIGH)
- P2-I-V-0204: Document_ID format invalid (HIGH)
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional, Tuple

from .base import BaseDetector, DetectionResult


class IdentityDetector(BaseDetector):
    """
    Detector for P2 identity column validation.
    
    P2 columns define document identity - critical for uniqueness
    and downstream processing.
    """
    
    # P2 identity columns
    IDENTITY_COLUMNS = [
        "Document_ID",
        "Document_Revision",
        "Document_Title",
        "Transmittal_Number"
    ]
    
    # Error codes
    ERROR_ID_UNCERTAIN = "P2-I-P-0201"
    ERROR_REV_MISSING = "P2-I-P-0202"
    ERROR_DUPLICATE_TRANS = "P2-I-V-0203"
    ERROR_ID_FORMAT_INVALID = "P2-I-V-0204"
    
    # Validation patterns
    # Document_ID: PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE (e.g., PRJ-FAC-DWG-ARC-0001)
    # Also supports optional suffix (e.g., -0, -1, -5.1)
    DOC_ID_PATTERN = re.compile(
        r'^[A-Z0-9]{3,10}-[A-Z0-9]{2,10}-[A-Z]{2,10}-[A-Z]{2,10}-\d{4}(?:-[A-Z0-9.]+)?$'
    )
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True,
        required_identities: Optional[List[str]] = None
    ):
        """
        Initialize identity detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
            required_identities: Override default identity columns
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self.required_identities = required_identities or self.IDENTITY_COLUMNS
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run P2 identity validations for required columns.
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Run detection methods only for required columns
        if "Document_ID" in self.required_identities:
            self._detect_uncertain_document_id(df)
            self._detect_invalid_id_format(df)
            
        if "Document_Revision" in self.required_identities:
            self._detect_missing_revision(df)
            
        if "Transmittal_Number" in self.required_identities:
            self._detect_duplicate_transmittal(df)
        
        return self.get_errors()
    
    def _detect_uncertain_document_id(self, df: pd.DataFrame) -> None:
        """
        Detect uncertain/invalid Document_ID values.
        
        Uncertain indicators:
        - "NA", "N/A", "UNKNOWN", "TBD", "TO BE DETERMINED"
        - Empty or null values
        - Non-standard format
        
        Error: P2-I-P-0201 (CRITICAL - FAIL FAST)
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return
        
        # Uncertain indicators
        uncertain_values = ['na', 'n/a', 'unknown', 'tbd', 'to be determined', 
                           'pending', 'draft', 'temp', 'temporary', '']
        
        for idx in df.index:
            value = str(df.at[idx, id_col]).strip().lower()
            
            # Check for uncertain values
            if value in uncertain_values or pd.isna(df.at[idx, id_col]):
                self.detect_error(
                    error_code=self.ERROR_ID_UNCERTAIN,
                    message=f"Document_ID uncertain at row {idx}: '{df.at[idx, id_col]}'",
                    row=idx,
                    column=id_col,
                    severity="CRITICAL",
                    fail_fast=True,
                    additional_context={
                        "actual_value": str(df.at[idx, id_col]),
                        "uncertain_type": "placeholder_value",
                        "suggestion": "Provide valid Document_ID"
                    }
                )
    
    def _detect_missing_revision(self, df: pd.DataFrame) -> None:
        """
        Detect missing Document_Revision values.
        
        Error: P2-I-P-0202 (CRITICAL - FAIL FAST)
        """
        rev_col = "Document_Revision"
        
        if rev_col not in df.columns:
            return
        
        # Check for nulls and empty strings
        null_mask = df[rev_col].isna() | (df[rev_col] == '')
        
        for idx in df[null_mask].index:
            self.detect_error(
                error_code=self.ERROR_REV_MISSING,
                message=f"Document_Revision missing at row {idx}",
                row=idx,
                column=rev_col,
                severity="CRITICAL",
                fail_fast=True,
                additional_context={
                    "suggestion": "Set default revision (e.g., '00' or 'A')"
                }
            )
    
    def _detect_duplicate_transmittal(self, df: pd.DataFrame) -> None:
        """
        Detect duplicate Transmittal_Number within session.
        
        Error: P2-I-V-0203 (HIGH)
        """
        trans_col = "Transmittal_Number"
        session_col = "Submission_Session"
        
        if trans_col not in df.columns:
            return
        
        # Group by session if available
        if session_col in df.columns:
            for session_id, group in df.groupby(session_col):
                duplicates = group[trans_col].duplicated(keep=False)
                
                for idx in group[duplicates].index:
                    self.detect_error(
                        error_code=self.ERROR_DUPLICATE_TRANS,
                        message=f"Duplicate Transmittal_Number in session {session_id}",
                        row=idx,
                        column=trans_col,
                        severity="HIGH",
                        fail_fast=False,
                        additional_context={
                            "session_id": str(session_id),
                            "transmittal_value": str(df.at[idx, trans_col]),
                            "duplicate_count": int(duplicates.sum()),
                            "suggestion": "Make Transmittal_Number unique per session"
                        }
                    )
        else:
            # Check across entire dataset
            duplicates = df[trans_col].duplicated(keep=False)
            
            for idx in df[duplicates].index:
                self.detect_error(
                    error_code=self.ERROR_DUPLICATE_TRANS,
                    message=f"Duplicate Transmittal_Number detected",
                    row=idx,
                    column=trans_col,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "transmittal_value": str(df.at[idx, trans_col]),
                        "suggestion": "Ensure Transmittal_Number uniqueness"
                    }
                )
    
    def _detect_invalid_id_format(self, df: pd.DataFrame) -> None:
        """
        Detect Document_ID format violations.
        
        Expected format: PROJECT-FACILITY-TYPE-SEQUENCE
        Example: PRJ-FAC-DWG-0001
        
        Error: P2-I-V-0204 (HIGH)
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return
        
        for idx in df.index:
            value = str(df.at[idx, id_col])
            
            # Skip nulls (handled by _detect_uncertain_document_id)
            if pd.isna(df.at[idx, id_col]) or value.strip() == '':
                continue
            
            # Check format
            if not self.DOC_ID_PATTERN.match(value):
                self.detect_error(
                    error_code=self.ERROR_ID_FORMAT_INVALID,
                    message=f"Invalid Document_ID format: '{value}'",
                    row=idx,
                    column=id_col,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "actual_value": value,
                        "expected_pattern": "PROJECT-FACILITY-TYPE-SEQUENCE",
                        "example_valid": "PRJ-FAC-DWG-0001",
                        "suggestion": "Use format: PROJECT(3-6 chars)-FACILITY(2-4)-TYPE(2-6)-0000"
                    }
                )
    
    def detect_P201_id_uncertain(
        self,
        df: pd.DataFrame
    ) -> List[Tuple[int, str]]:
        """
        Public API: Check for uncertain Document_ID values.
        
        Args:
            df: DataFrame
            
        Returns:
            List of (row_index, uncertain_value) tuples
        """
        id_col = "Document_ID"
        
        if id_col not in df.columns:
            return []
        
        uncertain_values = ['na', 'n/a', 'unknown', 'tbd', 'to be determined',
                           'pending', 'draft', 'temp', 'temporary', '']
        
        results = []
        for idx in df.index:
            value = str(df.at[idx, id_col]).strip().lower()
            if value in uncertain_values or pd.isna(df.at[idx, id_col]):
                results.append((idx, str(df.at[idx, id_col])))
        
        return results
    
    def detect_P202_rev_missing(
        self,
        df: pd.DataFrame
    ) -> List[int]:
        """
        Public API: Check for missing Document_Revision.
        
        Args:
            df: DataFrame
            
        Returns:
            List of row indices with missing revisions
        """
        rev_col = "Document_Revision"
        
        if rev_col not in df.columns:
            return []
        
        null_mask = df[rev_col].isna() | (df[rev_col] == '')
        return df[null_mask].index.tolist()
    
    def detect_P203_duplicate_trans(
        self,
        df: pd.DataFrame,
        group_by_session: bool = True
    ) -> Dict[str, List[int]]:
        """
        Public API: Find duplicate Transmittal_Numbers.
        
        Args:
            df: DataFrame
            group_by_session: Whether to check per session
            
        Returns:
            Dict of transmittal_value -> list of row indices
        """
        trans_col = "Transmittal_Number"
        
        if trans_col not in df.columns:
            return {}
        
        duplicates = {}
        
        if group_by_session and "Submission_Session" in df.columns:
            for session_id, group in df.groupby("Submission_Session"):
                dup_mask = group[trans_col].duplicated(keep=False)
                for idx in group[dup_mask].index:
                    value = str(df.at[idx, trans_col])
                    if value not in duplicates:
                        duplicates[value] = []
                    duplicates[value].append(idx)
        else:
            dup_mask = df[trans_col].duplicated(keep=False)
            for idx in df[dup_mask].index:
                value = str(df.at[idx, trans_col])
                if value not in duplicates:
                    duplicates[value] = []
                duplicates[value].append(idx)
        
        return duplicates
