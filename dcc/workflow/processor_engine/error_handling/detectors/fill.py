"""
Fill Detector Module (F4xx - Layer 3)

Detects null handling and forward fill issues:
- Row jump limit exceeded
- Session boundary crossed during fill
- Calculation-based fills

Error Codes:
- F4-C-F-0401: Forward fill limit exceeded (HIGH)
- F4-C-F-0402: Session boundary crossed during fill (HIGH)
- F4-C-F-0403: Calculation-based fill applied (WARNING)
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from .base import BaseDetector, DetectionResult


class FillDetector(BaseDetector):
    """
    Detector for null handling and forward fill validation.
    
    Monitors forward fill operations and detects issues
    such as large row jumps or session boundary crossings.
    """
    
    # Error codes
    ERROR_JUMP_LIMIT = "F4-C-F-0401"
    ERROR_BOUNDARY_CROSS = "F4-C-F-0402"
    ERROR_FILL_INFERRED = "F4-C-F-0403"
    
    # Default limits
    DEFAULT_JUMP_LIMIT = 20
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True,
        jump_limit: int = 20
    ):
        """
        Initialize fill detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
            jump_limit: Maximum allowed row jump for forward fill
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self.jump_limit = jump_limit
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run all F4 fill validations.
        
        Args:
            df: DataFrame to validate
            context: Additional context (may contain fill_history)
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Check for fill history in context
        fill_history = context.get("fill_history", []) if context else []
        
        if fill_history:
            # Analyze provided fill history
            self._analyze_fill_history(fill_history)
        else:
            # Detect fills from DataFrame
            self._detect_jump_limit(df)
            self._detect_boundary_cross(df)
            self._detect_inferred_fills(df)
        
        return self.get_errors()
    
    def _analyze_fill_history(self, fill_history: List[Dict]) -> None:
        """
        Analyze recorded fill operations.
        
        Args:
            fill_history: List of fill operation records
        """
        for record in fill_history:
            operation = record.get("operation", "")
            
            if operation == "forward_fill":
                self._check_forward_fill_record(record)
            elif operation == "multi_level_fill":
                self._check_multi_level_record(record)
    
    def _check_forward_fill_record(self, record: Dict) -> None:
        """
        Check a forward fill record for issues.
        
        Args:
            record: Fill operation record
        """
        row_jump = record.get("row_jump", 0)
        column = record.get("column", "unknown")
        from_row = record.get("from_row", 0)
        to_row = record.get("to_row", 0)
        
        if row_jump > self.jump_limit:
            self.detect_error(
                error_code=self.ERROR_JUMP_LIMIT,
                message=f"Forward fill row jump exceeded limit: {row_jump} > {self.jump_limit}",
                row=to_row,
                column=column,
                severity="HIGH",
                fail_fast=False,
                additional_context={
                    "column": column,
                    "from_row": from_row,
                    "to_row": to_row,
                    "row_jump": row_jump,
                    "limit": self.jump_limit,
                    "filled_value": record.get("filled_value"),
                    "suggestion": "Consider using multi-level fill or manual data entry"
                }
            )
        
        # Check for session boundary crossing
        if record.get("session_boundary_crossed", False):
            self.detect_error(
                error_code=self.ERROR_BOUNDARY_CROSS,
                message=f"Forward fill crossed session boundary",
                row=to_row,
                column=column,
                severity="HIGH",
                fail_fast=False,
                additional_context={
                    "column": column,
                    "source_session": record.get("source_session"),
                    "target_session": record.get("target_session"),
                    "suggestion": "Use group-based forward fill within sessions"
                }
            )
    
    def _check_multi_level_record(self, record: Dict) -> None:
        """
        Check a multi-level fill record.
        
        Args:
            record: Multi-level fill operation record
        """
        # Multi-level fills are generally safer, but can still have issues
        levels = record.get("levels_applied", [])
        column = record.get("column", "unknown")
        
        # Check if all levels failed to find a value
        if record.get("all_levels_failed", False):
            self.detect_error(
                error_code=self.ERROR_FILL_INFERRED,
                message=f"Multi-level fill failed to find value, default applied",
                column=column,
                severity="WARNING",
                fail_fast=False,
                additional_context={
                    "column": column,
                    "levels_tried": levels,
                    "default_applied": record.get("default_applied"),
                    "suggestion": "Verify data exists in higher level groupings"
                }
            )
    
    def _detect_jump_limit(self, df: pd.DataFrame) -> None:
        """
        Detect row jumps exceeding limit in DataFrame.
        
        Error: F4-C-F-0401 (HIGH)
        """
        # This is a heuristic detection based on data patterns
        # Actual fill detection should use fill_history from null_handling.py
        
        columns_to_check = ["Reviewer", "Department", "Submitted_By"]
        
        for col in columns_to_check:
            if col not in df.columns:
                continue
            
            # Find sequences of same values
            prev_value = None
            prev_idx = None
            value_start_idx = None
            
            for idx in df.index:
                current_value = df.at[idx, col]
                
                if pd.notna(current_value) and current_value != '':
                    if prev_value is not None and current_value == prev_value:
                        # Same value continues
                        row_jump = idx - prev_idx
                        
                        if row_jump > self.jump_limit:
                            # This looks like a large forward fill
                            self.detect_error(
                                error_code=self.ERROR_JUMP_LIMIT,
                                message=f"Potential forward fill with {row_jump} row jump in '{col}'",
                                row=idx,
                                column=col,
                                severity="HIGH",
                                fail_fast=False,
                                additional_context={
                                    "column": col,
                                    "value": str(current_value),
                                    "row_jump": row_jump,
                                    "limit": self.jump_limit,
                                    "start_row": value_start_idx,
                                    "end_row": idx,
                                    "suggestion": "Verify this fill is intentional"
                                }
                            )
                    
                    value_start_idx = idx
                    prev_value = current_value
                    prev_idx = idx
    
    def _detect_boundary_cross(self, df: pd.DataFrame) -> None:
        """
        Detect potential session boundary crossings.
        
        Error: F4-C-F-0402 (HIGH)
        """
        session_col = "Submission_Session"
        
        if session_col not in df.columns:
            return
        
        # Columns commonly forward-filled
        fill_columns = ["Reviewer", "Department", "Submitted_By"]
        
        for col in fill_columns:
            if col not in df.columns:
                continue
            
            prev_value = None
            prev_session = None
            
            for idx in df.index:
                current_value = df.at[idx, col]
                current_session = df.at[idx, session_col]
                
                if pd.notna(current_value) and current_value != '':
                    if (prev_value is not None and 
                        current_value == prev_value and
                        prev_session is not None and
                        str(current_session) != str(prev_session)):
                        
                        # Same value across different sessions
                        self.detect_error(
                            error_code=self.ERROR_BOUNDARY_CROSS,
                            message=f"Value '{current_value}' appears in multiple sessions",
                            row=idx,
                            column=col,
                            severity="HIGH",
                            fail_fast=False,
                            additional_context={
                                "column": col,
                                "value": str(current_value),
                                "previous_session": str(prev_session),
                                "current_session": str(current_session),
                                "suggestion": "Verify intentional cross-session fill"
                            }
                        )
                    
                    prev_value = current_value
                    prev_session = current_session
    
    def _detect_inferred_fills(self, df: pd.DataFrame) -> None:
        """
        Detect calculation-based inferred fills.
        
        Error: F4-C-F-0403 (WARNING)
        """
        # Check for columns that may have inferred values
        inferred_columns = {
            "Duration_of_Review": ["Submission_Date", "Review_Return_Actual_Date"],
            "Delay_of_Resubmission": ["Resubmission_Plan_Date", "Resubmission_Forecast_Date"]
        }
        
        for col, source_cols in inferred_columns.items():
            if col not in df.columns:
                continue
            
            # Check if any source columns exist
            has_source = any(sc in df.columns for sc in source_cols)
            
            if not has_source:
                continue
            
            # Check for values without direct source
            for idx in df.index:
                value = df.at[idx, col]
                
                if pd.notna(value) and value != '':
                    # Check if any source is missing
                    sources_missing = all(
                        sc not in df.columns or pd.isna(df.at[idx, sc]) or df.at[idx, sc] == ''
                        for sc in source_cols
                    )
                    
                    if sources_missing:
                        self.detect_error(
                            error_code=self.ERROR_FILL_INFERRED,
                            message=f"Value in '{col}' may be calculated/inferred",
                            row=idx,
                            column=col,
                            severity="WARNING",
                            fail_fast=False,
                            additional_context={
                                "column": col,
                                "value": str(value),
                                "inferred_from": "calculation",
                                "suggestion": "Verify calculated value is correct"
                            }
                        )
    
    def detect_F401_jump_limit(
        self,
        df: pd.DataFrame,
        column: str,
        threshold: int = 20
    ) -> List[Tuple[int, int, int]]:
        """
        Public API: Find row jumps exceeding limit.
        
        Args:
            df: DataFrame
            column: Column to check
            threshold: Jump threshold
            
        Returns:
            List of (row_index, jump_size, repeated_count)
        """
        if column not in df.columns:
            return []
        
        jumps = []
        prev_idx = None
        prev_value = None
        
        for idx in df.index:
            current_value = df.at[idx, column]
            
            if pd.notna(current_value) and current_value != '':
                if prev_value is not None and current_value == prev_value and prev_idx is not None:
                    jump = idx - prev_idx
                    if jump > threshold:
                        # Count how many times this value repeats
                        repeated = 1
                        for j in range(idx + 1, len(df)):
                            if j in df.index:
                                if df.at[j, column] == current_value:
                                    repeated += 1
                                else:
                                    break
                        
                        jumps.append((idx, jump, repeated))
                
                prev_value = current_value
                prev_idx = idx
        
        return jumps
    
    def detect_F402_boundary_cross(
        self,
        df: pd.DataFrame,
        column: str,
        group_by: str = "Submission_Session"
    ) -> List[Tuple[int, str, str]]:
        """
        Public API: Find values that cross group boundaries.
        
        Args:
            df: DataFrame
            column: Column to check
            group_by: Grouping column
            
        Returns:
            List of (row_index, value, groups_crossed)
        """
        if column not in df.columns or group_by not in df.columns:
            return []
        
        violations = []
        prev_value = None
        prev_group = None
        value_groups = {}  # value -> set of groups
        
        for idx in df.index:
            current_value = df.at[idx, column]
            current_group = str(df.at[idx, group_by])
            
            if pd.notna(current_value) and current_value != '':
                if current_value not in value_groups:
                    value_groups[current_value] = set()
                value_groups[current_value].add(current_group)
                
                # Check if this value spans multiple groups
                if len(value_groups[current_value]) > 1:
                    if current_value == prev_value and current_group != prev_group:
                        violations.append((idx, str(current_value), 
                                          ", ".join(value_groups[current_value])))
                
                prev_value = current_value
                prev_group = current_group
        
        return violations
