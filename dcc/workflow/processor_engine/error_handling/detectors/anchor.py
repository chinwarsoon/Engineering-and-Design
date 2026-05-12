"""
Anchor Detector Module (P1xx - Layer 3)

Validates P1 (Priority 1) anchor columns:
- Project_Code, Facility_Code, Document_Type, Discipline
- Submission_Session, Document_Sequence_Number

Error Codes:
- P1-A-P-0101: Null anchor column (CRITICAL)
- P1-A-V-0102: Invalid session format (6 digits)
- P1-A-V-0103: Invalid date format
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .base import BaseDetector, DetectionResult, FailFastError


class AnchorDetector(BaseDetector):
    """
    Detector for P1 anchor column validation.
    
    P1 columns are foundational - they must exist and be valid
    before any downstream processing.
    """
    
    # P1 anchor columns — fallback when schema is not available
    # C10: Schema (dcc_register_config.json is_anchor: true) is SSOT
    ANCHOR_COLUMNS = [
        "Project_Code",
        "Facility_Code", 
        "Document_Type",
        "Discipline",
        "Submission_Session"
    ]
    
    # Error codes
    ERROR_NULL_ANCHOR = "P1-A-P-0101"
    ERROR_SESSION_FORMAT = "P1-A-V-0102"
    ERROR_DATE_INVALID = "P1-A-V-0103"
    
    # Validation patterns
    SESSION_PATTERN = re.compile(r'^\d{6}$')  # 6 digits
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True,
        required_anchors: Optional[List[str]] = None
    ):
        """
        Initialize anchor detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
            required_anchors: Override default anchor columns
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self.required_anchors = required_anchors or self.ANCHOR_COLUMNS

    def _get_anchor_columns(self) -> List[str]:
        """
        C10: Return anchor columns from schema (SSOT) or fallback constant.
        Reads columns with is_anchor: true from context schema_data.
        """
        schema_data = self._context.get("schema_data", {})
        columns = schema_data.get("columns", {})
        if columns:
            anchor_cols = [
                name for name, defn in columns.items()
                if isinstance(defn, dict) and defn.get("is_anchor")
            ]
            if anchor_cols:
                return anchor_cols
        return self.ANCHOR_COLUMNS
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run all P1 anchor validations.
        
        Args:
            df: DataFrame to validate
            context: Additional context (project_code, facility_code, etc.)
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Run detection methods
        self._detect_null_anchors(df)
        self._detect_session_format(df)
        self._detect_invalid_dates(df)
        
        return self.get_errors()
    
    def _detect_null_anchors(self, df: pd.DataFrame) -> None:
        """
        Detect null values in anchor columns.

        Error: P1-A-P-0101 (CRITICAL - FAIL FAST)
        """
        # C10: Use schema-driven anchor columns (SSOT) with fallback to required_anchors
        anchor_cols = self._get_anchor_columns()
        for col in anchor_cols:
            if col not in df.columns:
                # Column missing entirely - critical error
                self.detect_error(
                    error_code=self.ERROR_NULL_ANCHOR,
                    message=f"Anchor column '{col}' is missing from DataFrame",
                    column=col,
                    severity=self._get_severity(self.ERROR_NULL_ANCHOR, "CRITICAL"),
                    fail_fast=True,
                    additional_context={
                        "available_columns": list(df.columns),
                        "error_type": "column_missing"
                    }
                )
                continue
            
            # Check for null values
            null_mask = df[col].isna() | (df[col] == '')
            null_count = null_mask.sum()
            
            if null_count > 0:
                # Get first few rows with nulls for reporting
                null_indices = df[null_mask].index.tolist()[:5]  # First 5
                
                self.detect_error(
                    error_code=self.ERROR_NULL_ANCHOR,
                    message=f"Anchor column '{col}' has {null_count} null/empty values",
                    column=col,
                    severity=self._get_severity(self.ERROR_NULL_ANCHOR, "CRITICAL"),
                    fail_fast=True,
                    additional_context={
                        "null_count": int(null_count),
                        "total_rows": len(df),
                        "null_percentage": round(null_count / len(df) * 100, 2),
                        "sample_rows": null_indices,
                        "error_type": "null_values"
                    }
                )
    
    def _detect_session_format(self, df: pd.DataFrame) -> None:
        """
        Validate Submission_Session format (6 digits).
        
        Error: P1-A-V-0102 (HIGH)
        """
        session_col = "Submission_Session"
        
        if session_col not in df.columns:
            return
            
        # Task B3: Use pattern from schema if available (SSOT)
        pattern = self.SESSION_PATTERN
        schema_data = getattr(self, 'schema_data', {})
        if schema_data:
            cols = schema_data.get('columns', {})
            session_schema = cols.get(session_col, {})
            # Navigate to validation[type=pattern].pattern
            validation_list = session_schema.get('validation', [])
            for v in validation_list:
                if v.get('type') == 'pattern' and v.get('pattern'):
                    try:
                        pattern = re.compile(v.get('pattern'))
                        break
                    except re.error:
                        continue
        
        # Check non-null values
        valid_mask = df[session_col].notna() & (df[session_col] != '')
        
        for idx in df[valid_mask].index:
            value = str(df.at[idx, session_col])
            
            # Check pattern
            if not pattern.match(value):
                self.detect_error(
                    error_code=self.ERROR_SESSION_FORMAT,
                    message=f"Invalid Submission_Session format: '{value}' (expected pattern: {pattern.pattern})",
                    row=idx,
                    column=session_col,
                    severity=self._get_severity(self.ERROR_SESSION_FORMAT, "HIGH"),
                    fail_fast=False,
                    additional_context={
                        "actual_value": value,
                        "expected_pattern": pattern.pattern,
                        "example_valid": "240101"
                    }
                )
    
    def _detect_invalid_dates(self, df: pd.DataFrame) -> None:
        """
        Detect invalid date formats in date columns.
        
        Error: P1-A-V-0103 (HIGH)
        """
        date_columns = [
            "First_Submission_Date",
            "Submission_Date",
            "Review_Return_Actual_Date",
            "Review_Return_Plan_Date"
        ]
        
        for col in date_columns:
            if col not in df.columns:
                continue
            
            # Check non-null values
            valid_mask = df[col].notna() & (df[col] != '')
            
            for idx in df[valid_mask].index:
                value = df.at[idx, col]
                
                # Try to parse as date
                if not self._is_valid_date(value):
                    self.detect_error(
                        error_code=self.ERROR_DATE_INVALID,
                        message=f"Invalid date format in '{col}': '{value}'",
                        row=idx,
                        column=col,
                        severity=self._get_severity(self.ERROR_DATE_INVALID, "HIGH"),
                        fail_fast=False,
                        additional_context={
                            "actual_value": str(value),
                            "expected_formats": [
                                "YYYY-MM-DD",
                                "DD/MM/YYYY",
                                "MM/DD/YYYY"
                            ]
                        }
                    )
    
    def _is_valid_date(self, value: Any) -> bool:
        """
        Check if value is a valid date.
        
        Args:
            value: Value to check
            
        Returns:
            True if valid date
        """
        if pd.isna(value) or value == '':
            return True  # Nulls handled separately
        
        # Already a datetime
        if isinstance(value, (datetime, pd.Timestamp)):
            return True
        
        # Try common formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(str(value), fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def detect_P101_null_anchor(
        self,
        df: pd.DataFrame,
        column: str
    ) -> List[int]:
        """
        Public API: Check specific column for nulls.
        
        Args:
            df: DataFrame
            column: Column to check
            
        Returns:
            List of row indices with nulls
        """
        if column not in df.columns:
            return []
        
        null_mask = df[column].isna() | (df[column] == '')
        return df[null_mask].index.tolist()
    
    def detect_P102_session_format(
        self,
        df: pd.DataFrame
    ) -> List[Tuple[int, str]]:
        """
        Public API: Check session format violations.
        
        Args:
            df: DataFrame
            
        Returns:
            List of (row_index, invalid_value) tuples
        """
        if "Submission_Session" not in df.columns:
            return []
        
        violations = []
        valid_mask = df["Submission_Session"].notna() & (df["Submission_Session"] != '')
        
        for idx in df[valid_mask].index:
            value = str(df.at[idx, "Submission_Session"])
            if not self.SESSION_PATTERN.match(value):
                violations.append((idx, value))
        
        return violations
    
    def detect_P103_date_invalid(
        self,
        df: pd.DataFrame,
        column: str
    ) -> List[int]:
        """
        Public API: Check specific date column for invalid dates.
        
        Args:
            df: DataFrame
            column: Date column to check
            
        Returns:
            List of row indices with invalid dates
        """
        if column not in df.columns:
            return []
        
        invalid_indices = []
        valid_mask = df[column].notna() & (df[column] != '')
        
        for idx in df[valid_mask].index:
            if not self._is_valid_date(df.at[idx, column]):
                invalid_indices.append(idx)
        
        return invalid_indices
