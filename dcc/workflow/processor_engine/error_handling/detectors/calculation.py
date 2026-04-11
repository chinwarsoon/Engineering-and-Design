"""
Calculation Detector Module (C6xx - Layer 3)

Detects calculation errors:
- Missing input columns
- Circular dependencies
- Division by zero
- Aggregate empty sets
- Date arithmetic failures
- Mapping no match

Error Codes:
- C6-C-C-0601: Missing input columns (CRITICAL)
- C6-C-C-0602: Circular dependency detected (CRITICAL)
- C6-C-C-0603: Division by zero (HIGH)
- C6-C-C-0604: Aggregate on empty set (HIGH)
- C6-C-C-0605: Date arithmetic failed (HIGH)
- C6-C-C-0606: Mapping no match (HIGH)
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta

from .base import BaseDetector, DetectionResult


class CalculationDetector(BaseDetector):
    """
    Detector for calculation errors.
    
    Validates calculation operations and dependencies.
    """
    
    # Error codes
    ERROR_DEPENDENCY_FAIL = "C6-C-C-0601"
    ERROR_CIRCULAR_DEPENDENCY = "C6-C-C-0602"
    ERROR_DIVISION_BY_ZERO = "C6-C-C-0603"
    ERROR_AGGREGATE_EMPTY = "C6-C-C-0604"
    ERROR_DATE_ARITHMETIC_FAIL = "C6-C-C-0605"
    ERROR_MAPPING_NO_MATCH = "C6-C-C-0606"
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True
    ):
        """
        Initialize calculation detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self._dependency_graph: Dict[str, Set[str]] = {}
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run all calculation validations.
        
        Args:
            df: DataFrame to validate
            context: Additional context (calculations, dependencies, etc.)
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
            
            # Check for calculation info
            if "calculations" in context:
                self._validate_calculations(df, context["calculations"])
            if "dependency_graph" in context:
                self._validate_dependencies(context["dependency_graph"])
        
        # Always run heuristic detections
        self._detect_division_by_zero(df)
        self._detect_aggregate_issues(df)
        self._detect_date_arithmetic_failures(df)
        
        return self.get_errors()
    
    def _validate_calculations(
        self,
        df: pd.DataFrame,
        calculations: List[Dict[str, Any]]
    ) -> None:
        """
        Validate calculation definitions against data.
        
        Args:
            df: DataFrame
            calculations: List of calculation definitions
        """
        for calc in calculations:
            calc_type = calc.get("type")
            target_column = calc.get("target_column")
            input_columns = calc.get("input_columns", [])
            
            # Check input columns exist
            missing_inputs = [col for col in input_columns if col not in df.columns]
            if missing_inputs:
                self.detect_error(
                    error_code=self.ERROR_DEPENDENCY_FAIL,
                    message=f"Missing input columns for {target_column}: {missing_inputs}",
                    column=target_column,
                    severity="CRITICAL",
                    fail_fast=True,
                    additional_context={
                        "calculation_type": calc_type,
                        "target_column": target_column,
                        "missing_inputs": missing_inputs,
                        "available_columns": list(df.columns),
                        "suggestion": "Add missing input columns or revise calculation"
                    }
                )
            
            # Type-specific validation
            if calc_type == "mapping":
                self._validate_mapping(df, calc)
            elif calc_type == "date_diff":
                self._validate_date_diff(df, calc)
    
    def _validate_dependencies(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> None:
        """
        Validate dependency graph for circular dependencies.
        
        Args:
            dependency_graph: Dict of column -> set of dependencies
        """
        # Check for circular dependencies using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    self.detect_error(
                        error_code=self.ERROR_CIRCULAR_DEPENDENCY,
                        message=f"Circular dependency detected: {' -> '.join(cycle)}",
                        severity="CRITICAL",
                        fail_fast=True,
                        additional_context={
                            "cycle": cycle,
                            "suggestion": "Break circular dependency by restructuring calculations"
                        }
                    )
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in dependency_graph:
            if node not in visited:
                has_cycle(node, [])
    
    def _validate_mapping(
        self,
        df: pd.DataFrame,
        calc: Dict[str, Any]
    ) -> None:
        """
        Validate mapping calculation.
        
        Error: C6-C-C-0606
        """
        source_column = calc.get("source_column")
        target_column = calc.get("target_column")
        mapping = calc.get("mapping", {})
        
        if source_column not in df.columns:
            return
        
        # Check for values with no mapping
        for idx in df.index:
            source_value = df.at[idx, source_column]
            
            if pd.isna(source_value) or source_value == '':
                continue
            
            if str(source_value) not in mapping:
                self.detect_error(
                    error_code=self.ERROR_MAPPING_NO_MATCH,
                    message=f"No mapping match for '{source_value}' in {source_column}",
                    row=idx,
                    column=target_column,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "source_column": source_column,
                        "source_value": str(source_value),
                        "available_mappings": list(mapping.keys())[:10],
                        "suggestion": "Add mapping for this value or use default"
                    }
                )
    
    def _validate_date_diff(
        self,
        df: pd.DataFrame,
        calc: Dict[str, Any]
    ) -> None:
        """
        Validate date difference calculation.
        
        Error: C6-C-C-0605
        """
        start_column = calc.get("start_column")
        end_column = calc.get("end_column")
        target_column = calc.get("target_column")
        
        if start_column not in df.columns or end_column not in df.columns:
            return
        
        # Check for invalid date pairs
        for idx in df.index:
            start_val = df.at[idx, start_column]
            end_val = df.at[idx, end_column]
            
            # Skip if either is null
            if pd.isna(start_val) or pd.isna(end_val):
                continue
            
            start_date = self._parse_date(start_val)
            end_date = self._parse_date(end_val)
            
            if start_date is None:
                self.detect_error(
                    error_code=self.ERROR_DATE_ARITHMETIC_FAIL,
                    message=f"Invalid start date in '{start_column}': '{start_val}'",
                    row=idx,
                    column=target_column,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "start_column": start_column,
                        "start_value": str(start_val),
                        "suggestion": "Fix date format"
                    }
                )
            
            if end_date is None:
                self.detect_error(
                    error_code=self.ERROR_DATE_ARITHMETIC_FAIL,
                    message=f"Invalid end date in '{end_column}': '{end_val}'",
                    row=idx,
                    column=target_column,
                    severity="HIGH",
                    fail_fast=False,
                    additional_context={
                        "end_column": end_column,
                        "end_value": str(end_val),
                        "suggestion": "Fix date format"
                    }
                )
    
    def _detect_division_by_zero(self, df: pd.DataFrame) -> None:
        """
        Detect potential division by zero in calculated columns.
        
        Error: C6-C-C-0603
        """
        # Check for Duration_of_Review calculation issues
        duration_col = "Duration_of_Review"
        
        if duration_col in df.columns:
            # Check for zero or negative durations
            for idx in df.index:
                value = df.at[idx, duration_col]
                
                if pd.notna(value):
                    try:
                        num_val = float(value)
                        if num_val == 0:
                            self.detect_error(
                                error_code=self.ERROR_DIVISION_BY_ZERO,
                                message=f"Zero duration may cause division issues",
                                row=idx,
                                column=duration_col,
                                severity="HIGH",
                                fail_fast=False,
                                additional_context={
                                    "value": str(value),
                                    "suggestion": "Verify calculation inputs"
                                }
                            )
                        elif num_val < 0:
                            self.detect_error(
                                error_code=self.ERROR_DATE_ARITHMETIC_FAIL,
                                message=f"Negative duration detected",
                                row=idx,
                                column=duration_col,
                                severity="HIGH",
                                fail_fast=False,
                                additional_context={
                                    "value": str(value),
                                    "suggestion": "Check date order in calculation"
                                }
                            )
                    except (ValueError, TypeError):
                        pass
    
    def _detect_aggregate_issues(self, df: pd.DataFrame) -> None:
        """
        Detect aggregate calculation issues.
        
        Error: C6-C-C-0604
        """
        # Check for aggregation columns
        aggregate_cols = [
            "Count_of_Submissions",
            "All_Submission_Sessions",
            "All_Submission_Dates"
        ]
        
        for col in aggregate_cols:
            if col not in df.columns:
                continue
            
            # Check for empty aggregates
            for idx in df.index:
                value = df.at[idx, col]
                
                if pd.notna(value):
                    str_val = str(value).strip()
                    
                    # Empty list-like values
                    if str_val in ["[]", "", "0", "None", "null"]:
                        self.detect_error(
                            error_code=self.ERROR_AGGREGATE_EMPTY,
                            message=f"Empty aggregate value in '{col}'",
                            row=idx,
                            column=col,
                            severity="HIGH",
                            fail_fast=False,
                            additional_context={
                                "value": str(value),
                                "suggestion": "Verify aggregation data source"
                            }
                        )
    
    def _detect_date_arithmetic_failures(self, df: pd.DataFrame) -> None:
        """
        Detect date arithmetic issues.
        
        Error: C6-C-C-0605
        """
        date_calc_columns = [
            "Duration_of_Review",
            "Delay_of_Resubmission",
            "Resubmission_Forecast_Date"
        ]
        
        for col in date_calc_columns:
            if col not in df.columns:
                continue
            
            for idx in df.index:
                value = df.at[idx, col]
                
                # Check for NaN or invalid values
                if pd.isna(value):
                    continue
                
                # Try to detect obvious arithmetic failures
                if isinstance(value, str):
                    if "error" in value.lower() or "invalid" in value.lower():
                        self.detect_error(
                            error_code=self.ERROR_DATE_ARITHMETIC_FAIL,
                            message=f"Date calculation error in '{col}'",
                            row=idx,
                            column=col,
                            severity="HIGH",
                            fail_fast=False,
                            additional_context={
                                "value": str(value),
                                "suggestion": "Check date inputs and formula"
                            }
                        )
    
    def _parse_date(self, value: Any) -> Optional[datetime]:
        """
        Parse date from various formats.
        
        Args:
            value: Value to parse
            
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
    
    def detect_C601_dependency_fail(
        self,
        df: pd.DataFrame,
        input_columns: List[str]
    ) -> List[str]:
        """
        Public API: Check for missing input columns.
        
        Args:
            df: DataFrame
            input_columns: Required input columns
            
        Returns:
            List of missing column names
        """
        return [col for col in input_columns if col not in df.columns]
    
    def detect_C602_circular_dependency(
        self,
        dependency_graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """
        Public API: Detect all circular dependencies.
        
        Args:
            dependency_graph: Dict of column -> dependencies
            
        Returns:
            List of cycles (each cycle is a list of columns)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        
        def find_cycles(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, set()):
                if neighbor not in visited:
                    find_cycles(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                find_cycles(node, [])
        
        return cycles
    
    def detect_C606_mapping_no_match(
        self,
        df: pd.DataFrame,
        source_column: str,
        mapping: Dict[str, str]
    ) -> List[Tuple[int, str]]:
        """
        Public API: Find values with no mapping match.
        
        Args:
            df: DataFrame
            source_column: Column to check
            mapping: Mapping dictionary
            
        Returns:
            List of (row_index, value) tuples
        """
        if source_column not in df.columns:
            return []
        
        no_matches = []
        
        for idx in df.index:
            value = df.at[idx, source_column]
            
            if pd.isna(value) or value == '':
                continue
            
            if str(value) not in mapping:
                no_matches.append((idx, str(value)))
        
        return no_matches
