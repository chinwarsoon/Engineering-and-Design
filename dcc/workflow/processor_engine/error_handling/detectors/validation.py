"""
Validation Detector Module (V5xx - Layer 2/3)

Performs comprehensive data validation:
- Pattern matching (regex)
- Length constraints
- Enum validation
- Type checking
- Required field validation
- Foreign key validation

Error Codes:
- V5-I-V-0501: Pattern mismatch (HIGH)
- V5-I-V-0502: Length exceeded (HIGH)
- V5-I-V-0503: Invalid enum value (HIGH)
- V5-I-V-0504: Type mismatch (HIGH)
- V5-I-V-0505: Required field missing (CRITICAL)
- V5-I-V-0506: Foreign key validation failed (HIGH)
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional, Callable, Union

from .base import BaseDetector, DetectionResult


class ValidationRule:
    """Represents a validation rule for a column."""
    
    def __init__(
        self,
        column: str,
        rule_type: str,  # pattern, length, enum, type, required, foreign_key
        params: Dict[str, Any],
        severity: str = "HIGH",
        error_code: Optional[str] = None
    ):
        self.column = column
        self.rule_type = rule_type
        self.params = params
        self.severity = severity
        self.error_code = error_code


class ValidationDetector(BaseDetector):
    """
    Detector for field-level validation.
    
    Validates data against schema rules including:
    - Pattern matching (regex)
    - Length constraints
    - Enum values
    - Data types
    - Foreign key relationships
    """
    
    # Error codes
    ERROR_PATTERN_MISMATCH = "V5-I-V-0501"
    ERROR_LENGTH_EXCEEDED = "V5-I-V-0502"
    ERROR_INVALID_ENUM = "V5-I-V-0503"
    ERROR_TYPE_MISMATCH = "V5-I-V-0504"
    ERROR_REQUIRED_MISSING = "V5-I-V-0505"
    ERROR_FOREIGN_KEY_FAIL = "V5-I-V-0506"
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = True
    ):
        """
        Initialize validation detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Whether to raise on critical errors
        """
        super().__init__(
            layer="L3",
            logger=logger,
            enable_fail_fast=enable_fail_fast
        )
        self._rules: Dict[str, List[ValidationRule]] = {}
        self._patterns: Dict[str, re.Pattern] = {}
        self._foreign_keys: Dict[str, set] = {}
    
    def detect(
        self,
        df: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Run all validation rules.
        
        Args:
            df: DataFrame to validate
            context: Additional context (rules, foreign_keys, etc.)
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
            
            # Load rules from context if provided
            if "validation_rules" in context:
                self._rules = context["validation_rules"]
            if "foreign_keys" in context:
                self._foreign_keys = context["foreign_keys"]
        
        # Run validation on all rules
        for column, rules in self._rules.items():
            if column not in df.columns:
                continue
            
            for rule in rules:
                self._apply_rule(df, column, rule)
        
        return self.get_errors()
    
    def _apply_rule(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Apply a validation rule to a column.
        
        Args:
            df: DataFrame
            column: Column name
            rule: ValidationRule to apply
        """
        if rule.rule_type == "pattern":
            self._validate_pattern(df, column, rule)
        elif rule.rule_type == "length":
            self._validate_length(df, column, rule)
        elif rule.rule_type == "enum":
            self._validate_enum(df, column, rule)
        elif rule.rule_type == "type":
            self._validate_type(df, column, rule)
        elif rule.rule_type == "required":
            self._validate_required(df, column, rule)
        elif rule.rule_type == "foreign_key":
            self._validate_foreign_key(df, column, rule)
    
    def _validate_pattern(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate regex pattern matching.
        
        Error: V5-I-V-0501
        """
        pattern = rule.params.get("pattern")
        if not pattern:
            return
        
        compiled_pattern = re.compile(pattern)
        
        for idx in df.index:
            value = df.at[idx, column]
            
            # Skip nulls
            if pd.isna(value) or value == '':
                continue
            
            if not compiled_pattern.match(str(value)):
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_PATTERN_MISMATCH,
                    message=f"Pattern mismatch in '{column}': '{value}'",
                    row=idx,
                    column=column,
                    severity=rule.severity,
                    fail_fast=False,
                    additional_context={
                        "value": str(value),
                        "pattern": pattern,
                        "suggestion": rule.params.get("suggestion", "Check format")
                    }
                )
    
    def _validate_length(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate string length constraints.
        
        Error: V5-I-V-0502
        """
        max_length = rule.params.get("max")
        min_length = rule.params.get("min")
        
        for idx in df.index:
            value = df.at[idx, column]
            
            # Skip nulls
            if pd.isna(value) or value == '':
                continue
            
            str_value = str(value)
            
            if max_length is not None and len(str_value) > max_length:
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_LENGTH_EXCEEDED,
                    message=f"Length exceeded in '{column}': {len(str_value)} > {max_length}",
                    row=idx,
                    column=column,
                    severity=rule.severity,
                    fail_fast=False,
                    additional_context={
                        "value": str_value[:50] + "..." if len(str_value) > 50 else str_value,
                        "actual_length": len(str_value),
                        "max_length": max_length,
                        "suggestion": f"Reduce to {max_length} characters"
                    }
                )
            
            if min_length is not None and len(str_value) < min_length:
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_LENGTH_EXCEEDED,
                    message=f"Length below minimum in '{column}': {len(str_value)} < {min_length}",
                    row=idx,
                    column=column,
                    severity=rule.severity,
                    fail_fast=False,
                    additional_context={
                        "value": str_value,
                        "actual_length": len(str_value),
                        "min_length": min_length,
                        "suggestion": f"Increase to {min_length} characters"
                    }
                )
    
    def _validate_enum(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate enum values.
        
        Error: V5-I-V-0503
        """
        allowed_values = rule.params.get("values", [])
        case_sensitive = rule.params.get("case_sensitive", False)
        
        if not allowed_values:
            return
        
        # Normalize for case-insensitive comparison
        if not case_sensitive:
            allowed_normalized = [str(v).lower() for v in allowed_values]
        else:
            allowed_normalized = [str(v) for v in allowed_values]
        
        for idx in df.index:
            value = df.at[idx, column]
            
            # Skip nulls
            if pd.isna(value) or value == '':
                continue
            
            check_value = str(value)
            if not case_sensitive:
                check_value = check_value.lower()
            
            if check_value not in allowed_normalized:
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_INVALID_ENUM,
                    message=f"Invalid enum value in '{column}': '{value}'",
                    row=idx,
                    column=column,
                    severity=rule.severity,
                    fail_fast=False,
                    additional_context={
                        "value": str(value),
                        "allowed_values": allowed_values,
                        "suggestion": f"Must be one of: {', '.join(allowed_values[:5])}"
                    }
                )
    
    def _validate_type(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate data types.
        
        Error: V5-I-V-0504
        """
        expected_type = rule.params.get("type")
        if not expected_type:
            return
        
        type_mapping = {
            "int": int,
            "integer": int,
            "float": float,
            "number": (int, float),
            "str": str,
            "string": str,
            "bool": bool,
            "boolean": bool,
            "datetime": pd.Timestamp,
            "date": pd.Timestamp
        }
        
        expected = type_mapping.get(expected_type, str)
        
        for idx in df.index:
            value = df.at[idx, column]
            
            # Skip nulls
            if pd.isna(value) or value == '':
                continue
            
            # Check type
            if not isinstance(value, expected):
                # Try to convert
                try:
                    if expected_type in ["int", "integer"]:
                        int(value)
                    elif expected_type in ["float", "number"]:
                        float(value)
                    elif expected_type in ["bool", "boolean"]:
                        bool(value)
                    else:
                        raise ValueError("Type mismatch")
                except (ValueError, TypeError):
                    self.detect_error(
                        error_code=rule.error_code or self.ERROR_TYPE_MISMATCH,
                        message=f"Type mismatch in '{column}': expected {expected_type}, got {type(value).__name__}",
                        row=idx,
                        column=column,
                        severity=rule.severity,
                        fail_fast=False,
                        additional_context={
                            "value": str(value),
                            "expected_type": expected_type,
                            "actual_type": type(value).__name__,
                            "suggestion": f"Convert to {expected_type}"
                        }
                    )
    
    def _validate_required(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate required fields.
        
        Error: V5-I-V-0505 (CRITICAL)
        """
        for idx in df.index:
            value = df.at[idx, column]
            
            if pd.isna(value) or value == '':
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_REQUIRED_MISSING,
                    message=f"Required field '{column}' is missing at row {idx}",
                    row=idx,
                    column=column,
                    severity="CRITICAL",
                    fail_fast=True,
                    additional_context={
                        "column": column,
                        "suggestion": "Provide required value"
                    }
                )
    
    def _validate_foreign_key(
        self,
        df: pd.DataFrame,
        column: str,
        rule: ValidationRule
    ) -> None:
        """
        Validate foreign key references.
        
        Error: V5-I-V-0506
        """
        reference_table = rule.params.get("reference_table")
        reference_column = rule.params.get("reference_column")
        
        if not reference_table or not reference_column:
            return
        
        # Get valid values from foreign key cache
        valid_values = self._foreign_keys.get(reference_table, set())
        
        if not valid_values:
            return
        
        for idx in df.index:
            value = df.at[idx, column]
            
            # Skip nulls
            if pd.isna(value) or value == '':
                continue
            
            if str(value) not in valid_values:
                self.detect_error(
                    error_code=rule.error_code or self.ERROR_FOREIGN_KEY_FAIL,
                    message=f"Foreign key validation failed for '{column}': '{value}' not in {reference_table}",
                    row=idx,
                    column=column,
                    severity=rule.severity,
                    fail_fast=False,
                    additional_context={
                        "value": str(value),
                        "reference_table": reference_table,
                        "reference_column": reference_column,
                        "suggestion": f"Value must exist in {reference_table}.{reference_column}"
                    }
                )
    
    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a validation rule.
        
        Args:
            rule: ValidationRule to add
        """
        if rule.column not in self._rules:
            self._rules[rule.column] = []
        self._rules[rule.column].append(rule)
    
    def set_foreign_key_values(
        self,
        table: str,
        values: Union[List, set]
    ) -> None:
        """
        Set valid foreign key values.
        
        Args:
            table: Table name
            values: Valid values set
        """
        self._foreign_keys[table] = set(str(v) for v in values)
    
    def validate_row(
        self,
        row: pd.Series,
        row_index: int,
        rules: Optional[List[ValidationRule]] = None
    ) -> List[DetectionResult]:
        """
        Validate a single row against rules.
        
        Args:
            row: Row data as Series
            row_index: Row index
            rules: Optional rules to apply (uses registered rules if not provided)
            
        Returns:
            List of detection results
        """
        self.clear_errors()
        
        rules_to_apply = rules or []
        if not rules_to_apply and self._rules:
            # Use all rules for this row
            for col, col_rules in self._rules.items():
                if col in row.index:
                    rules_to_apply.extend(col_rules)
        
        # Create single-row DataFrame for rule application
        df = row.to_frame().T
        
        for rule in rules_to_apply:
            self._apply_rule(df, rule.column, rule)
        
        # Update row numbers
        for error in self._errors:
            error.row = row_index
        
        return self.get_errors()
    
    def detect_V501_pattern_mismatch(
        self,
        df: pd.DataFrame,
        column: str,
        pattern: str
    ) -> List[int]:
        """
        Public API: Check pattern mismatches.
        
        Args:
            df: DataFrame
            column: Column to check
            pattern: Regex pattern
            
        Returns:
            List of row indices with mismatches
        """
        if column not in df.columns:
            return []
        
        compiled = re.compile(pattern)
        mismatches = []
        
        for idx in df.index:
            value = df.at[idx, column]
            if pd.notna(value) and value != '':
                if not compiled.match(str(value)):
                    mismatches.append(idx)
        
        return mismatches
    
    def detect_V502_length_exceeded(
        self,
        df: pd.DataFrame,
        column: str,
        max_length: int
    ) -> List[int]:
        """
        Public API: Check length exceeded.
        
        Args:
            df: DataFrame
            column: Column to check
            max_length: Maximum length
            
        Returns:
            List of row indices where length exceeded
        """
        if column not in df.columns:
            return []
        
        exceeded = []
        
        for idx in df.index:
            value = df.at[idx, column]
            if pd.notna(value) and value != '':
                if len(str(value)) > max_length:
                    exceeded.append(idx)
        
        return exceeded
