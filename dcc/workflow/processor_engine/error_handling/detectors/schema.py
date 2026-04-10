"""
Layer 2: Schema Validation Detector

Detects schema-level errors:
- Pattern mismatch (regex validation)
- Length validation
- Enum/allowed values validation
- Type checking
- Foreign key validation

Error Codes (V5xx):
- V5-I-V-0501: Pattern mismatch
- V5-I-V-0502: Length exceeded
- V5-I-V-0503: Invalid enum value
- V5-I-V-0504: Type mismatch
"""

import re
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

from .base import BaseDetector, DetectionResult


class SchemaDetector(BaseDetector):
    """
    Layer 2: Schema validation detector.
    
    Validates:
    - Pattern matching (regex)
    - Length constraints
    - Allowed values (enums)
    - Data types
    - Cross-field validation
    
    Supports both row-by-row and batch validation.
    """
    
    def __init__(
        self,
        logger=None,
        enable_fail_fast: bool = False
    ):
        """
        Initialize schema detector.
        
        Args:
            logger: StructuredLogger instance
            enable_fail_fast: Enable fail-fast (usually False for schema layer)
        """
        super().__init__(layer="L2", logger=logger, enable_fail_fast=enable_fail_fast)
        
        self._patterns: Dict[str, re.Pattern] = {}
        self._validators: Dict[str, Callable] = {}
    
    def register_pattern(self, column: str, pattern: str, description: str = "") -> None:
        """
        Register regex pattern for column validation.
        
        Args:
            column: Column name
            pattern: Regex pattern string
            description: Human-readable pattern description
        """
        self._patterns[column] = {
            "regex": re.compile(pattern),
            "pattern": pattern,
            "description": description
        }
    
    def detect(
        self,
        data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Detect schema errors.
        
        Args:
            data: Data to validate (dict, list of dicts, or DataFrame-like)
            context: Additional context
        
        Returns:
            List of DetectionResult objects
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # Handle different data types
        if hasattr(data, 'iterrows'):  # pandas DataFrame
            self._detect_dataframe(data)
        elif isinstance(data, list):
            for i, row in enumerate(data):
                self._detect_row(row, row_index=i)
        elif isinstance(data, dict):
            self._detect_row(data, row_index=0)
        
        return self.get_errors()
    
    def _detect_dataframe(self, df) -> None:
        """Detect errors in pandas DataFrame."""
        for column, pattern_info in self._patterns.items():
            if column not in df.columns:
                continue
            
            for idx, value in df[column].items():
                if pd.isna(value):
                    continue
                
                if not self._validate_pattern(value, pattern_info["regex"]):
                    self.detect_error(
                        error_code="V5-I-V-0501",
                        message=f"Pattern mismatch in {column}: '{value}' doesn't match {pattern_info['description'] or pattern_info['pattern']}",
                        row=idx,
                        column=column,
                        severity="HIGH",
                        fail_fast=False,
                        remediation_type="MANUAL_FIX",
                        additional_context={
                            "value": str(value),
                            "expected_pattern": pattern_info['pattern'],
                            "column": column
                        }
                    )
    
    def _detect_row(self, row: Dict[str, Any], row_index: int) -> None:
        """Detect errors in a single row."""
        for column, pattern_info in self._patterns.items():
            if column not in row:
                continue
            
            value = row[column]
            
            if value is None:
                continue
            
            if not self._validate_pattern(value, pattern_info["regex"]):
                self.detect_error(
                    error_code="V5-I-V-0501",
                    message=f"Pattern mismatch in {column}: '{value}' doesn't match {pattern_info['description'] or pattern_info['pattern']}",
                    row=row_index,
                    column=column,
                    severity="HIGH",
                    fail_fast=False,
                    remediation_type="MANUAL_FIX",
                    additional_context={
                        "value": str(value),
                        "expected_pattern": pattern_info['pattern'],
                        "column": column
                    }
                )
    
    def _validate_pattern(self, value: Any, pattern: re.Pattern) -> bool:
        """Validate value against regex pattern."""
        try:
            return bool(pattern.match(str(value)))
        except (TypeError, ValueError):
            return False
    
    def validate_length(
        self,
        value: Any,
        column: str,
        row_index: int,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> bool:
        """
        Validate string length constraints.
        
        Args:
            value: Value to validate
            column: Column name
            row_index: Row index for error reporting
            max_length: Maximum allowed length
            min_length: Minimum required length
        
        Returns:
            True if valid
        """
        if value is None:
            return True
        
        str_value = str(value)
        str_len = len(str_value)
        
        if max_length is not None and str_len > max_length:
            self.detect_error(
                error_code="V5-I-V-0502",
                message=f"Length exceeded in {column}: {str_len} chars (max: {max_length})",
                row=row_index,
                column=column,
                severity="HIGH",
                fail_fast=False,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "value": str_value[:50] + "..." if str_len > 50 else str_value,
                    "actual_length": str_len,
                    "max_length": max_length,
                    "column": column
                }
            )
            return False
        
        if min_length is not None and str_len < min_length:
            self.detect_error(
                error_code="V5-I-V-0502",
                message=f"Length too short in {column}: {str_len} chars (min: {min_length})",
                row=row_index,
                column=column,
                severity="HIGH",
                fail_fast=False,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "value": str_value,
                    "actual_length": str_len,
                    "min_length": min_length,
                    "column": column
                }
            )
            return False
        
        return True
    
    def validate_enum(
        self,
        value: Any,
        column: str,
        row_index: int,
        allowed_values: List[str],
        case_sensitive: bool = True
    ) -> bool:
        """
        Validate value against allowed enum values.
        
        Args:
            value: Value to validate
            column: Column name
            row_index: Row index
            allowed_values: List of allowed values
            case_sensitive: Whether comparison is case-sensitive
        
        Returns:
            True if valid
        """
        if value is None:
            return True
        
        str_value = str(value)
        
        if case_sensitive:
            is_valid = str_value in allowed_values
        else:
            is_valid = str_value.lower() in [v.lower() for v in allowed_values]
        
        if not is_valid:
            self.detect_error(
                error_code="V5-I-V-0503",
                message=f"Invalid value in {column}: '{value}' not in allowed values",
                row=row_index,
                column=column,
                severity="HIGH",
                fail_fast=False,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "value": str_value,
                    "allowed_values": allowed_values,
                    "column": column
                }
            )
            return False
        
        return True
    
    def validate_type(
        self,
        value: Any,
        column: str,
        row_index: int,
        expected_type: type
    ) -> bool:
        """
        Validate value type.
        
        Args:
            value: Value to validate
            column: Column name
            row_index: Row index
            expected_type: Expected Python type
        
        Returns:
            True if valid
        """
        if value is None:
            return True
        
        if not isinstance(value, expected_type):
            self.detect_error(
                error_code="V5-I-V-0504",
                message=f"Type mismatch in {column}: expected {expected_type.__name__}, got {type(value).__name__}",
                row=row_index,
                column=column,
                severity="HIGH",
                fail_fast=False,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "value": str(value)[:50],
                    "expected_type": expected_type.__name__,
                    "actual_type": type(value).__name__,
                    "column": column
                }
            )
            return False
        
        return True
    
    def validate_row(
        self,
        row: Dict[str, Any],
        row_index: int,
        validations: List[Dict[str, Any]]
    ) -> List[bool]:
        """
        Validate a row against multiple validation rules.
        
        Args:
            row: Row data as dictionary
            row_index: Row index
            validations: List of validation rules
                Each rule: {"column": str, "type": str, "params": dict}
                Types: "pattern", "length", "enum", "type"
        
        Returns:
            List of validation results (True/False)
        """
        results = []
        
        for rule in validations:
            column = rule.get("column")
            validation_type = rule.get("type")
            params = rule.get("params", {})
            
            if column not in row:
                results.append(True)  # Skip missing columns
                continue
            
            value = row[column]
            
            if validation_type == "pattern":
                pattern = params.get("pattern")
                if pattern:
                    regex = re.compile(pattern)
                    results.append(self._validate_pattern(value, regex))
                    if not results[-1]:
                        self.detect_error(
                            error_code="V5-I-V-0501",
                            message=f"Pattern mismatch in {column}",
                            row=row_index,
                            column=column,
                            severity="HIGH",
                            additional_context={"value": str(value), "pattern": pattern}
                        )
            
            elif validation_type == "length":
                result = self.validate_length(
                    value, column, row_index,
                    max_length=params.get("max"),
                    min_length=params.get("min")
                )
                results.append(result)
            
            elif validation_type == "enum":
                result = self.validate_enum(
                    value, column, row_index,
                    allowed_values=params.get("values", [])
                )
                results.append(result)
            
            elif validation_type == "type":
                type_map = {
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "datetime": datetime
                }
                expected = type_map.get(params.get("type"))
                if expected:
                    result = self.validate_type(value, column, row_index, expected)
                    results.append(result)
                else:
                    results.append(True)
            
            else:
                results.append(True)
        
        return results
