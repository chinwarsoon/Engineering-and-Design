"""
Layer 1: Input Validation Detector

Detects input-level errors:
- File existence/format validation
- Column presence detection
- Encoding detection
- File type validation

Fail Fast: Stops on critical input errors.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import csv

from .base import BaseDetector, DetectionResult


class InputDetector(BaseDetector):
    """
    Layer 1: Input validation detector.
    
    Validates:
    - File existence
    - File format (CSV, Excel, JSON)
    - Column presence
    - File encoding
    - File size limits
    
    Error Codes (S1xx):
    - S1-I-F-0804: File not found
    - S1-I-F-0805: Invalid file format
    - S1-I-V-0501: Encoding error
    - S1-I-V-0502: Required column missing
    """
    
    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        supported_formats: Optional[List[str]] = None,
        max_file_size_mb: float = 100.0,
        logger=None,
        enable_fail_fast: bool = True
    ):
        """
        Initialize input detector.
        
        Args:
            required_columns: List of required column names
            supported_formats: List of supported file extensions
            max_file_size_mb: Maximum file size in MB
            logger: StructuredLogger instance
            enable_fail_fast: Enable fail-fast behavior
        """
        super().__init__(layer="L1", logger=logger, enable_fail_fast=enable_fail_fast)
        
        self.required_columns = required_columns or []
        self.supported_formats = supported_formats or [".csv", ".xlsx", ".xls", ".json"]
        self.max_file_size_mb = max_file_size_mb
    
    def detect(self, data: Any, context: Optional[Dict[str, Any]] = None) -> List[DetectionResult]:
        """
        Detect input errors.
        
        Args:
            data: File path string or file-like object
            context: Additional context
        
        Returns:
            List of DetectionResult objects
        """
        self.clear_errors()
        
        if context:
            self.set_context(**context)
        
        # If data is a file path, validate it
        if isinstance(data, (str, Path)):
            file_path = Path(data)
            
            # Validate file exists
            if not self._validate_file_exists(file_path):
                return self.get_errors()
            
            # Validate file format
            if not self._validate_file_format(file_path):
                return self.get_errors()
            
            # Validate file size
            if not self._validate_file_size(file_path):
                return self.get_errors()
            
            # Validate encoding
            if not self._validate_encoding(file_path):
                return self.get_errors()
            
            # For CSV/Excel, validate columns
            if file_path.suffix.lower() in [".csv", ".xlsx", ".xls"]:
                self._validate_columns(file_path)
        
        return self.get_errors()
    
    def _validate_file_exists(self, file_path: Path) -> bool:
        """Validate file exists."""
        if not file_path.exists():
            self.detect_error(
                error_code="S1-I-F-0804",
                message=f"File not found: {file_path}",
                severity="CRITICAL",
                fail_fast=True,
                remediation_type="MANUAL_FIX",
                additional_context={"file_path": str(file_path)}
            )
            return False
        return True
    
    def _validate_file_format(self, file_path: Path) -> bool:
        """Validate file format is supported."""
        suffix = file_path.suffix.lower()
        
        if suffix not in self.supported_formats:
            self.detect_error(
                error_code="S1-I-F-0805",
                message=f"Unsupported file format: {suffix}",
                severity="CRITICAL",
                fail_fast=True,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "file_path": str(file_path),
                    "detected_format": suffix,
                    "supported_formats": self.supported_formats
                }
            )
            return False
        return True
    
    def _validate_file_size(self, file_path: Path) -> bool:
        """Validate file size within limits."""
        size_mb = file_path.stat().st_size / (1024 * 1024)
        
        if size_mb > self.max_file_size_mb:
            self.detect_error(
                error_code="S1-I-F-0805",
                message=f"File too large: {size_mb:.1f}MB (max: {self.max_file_size_mb}MB)",
                severity="HIGH",
                fail_fast=False,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "file_path": str(file_path),
                    "file_size_mb": size_mb,
                    "max_size_mb": self.max_file_size_mb
                }
            )
            return False
        return True
    
    def _validate_encoding(self, file_path: Path) -> bool:
        """Validate file encoding (UTF-8)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Read first 1KB to check encoding
            return True
        except UnicodeDecodeError:
            self.detect_error(
                error_code="S1-I-V-0501",
                message=f"File encoding error (expected UTF-8): {file_path}",
                severity="HIGH",
                fail_fast=True,
                remediation_type="MANUAL_FIX",
                additional_context={"file_path": str(file_path), "expected_encoding": "utf-8"}
            )
            return False
    
    def _validate_columns(self, file_path: Path) -> bool:
        """Validate required columns exist."""
        if not self.required_columns:
            return True
        
        try:
            if file_path.suffix.lower() == ".csv":
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
            else:
                # For Excel, we'd need pandas
                # For now, skip detailed column validation
                return True
            
            missing_columns = [col for col in self.required_columns if col not in headers]
            
            if missing_columns:
                self.detect_error(
                    error_code="S1-I-V-0502",
                    message=f"Missing required columns: {', '.join(missing_columns)}",
                    severity="CRITICAL",
                    fail_fast=True,
                    remediation_type="MANUAL_FIX",
                    additional_context={
                        "file_path": str(file_path),
                        "missing_columns": missing_columns,
                        "available_columns": headers
                    }
                )
                return False
            
            return True
            
        except Exception as e:
            self.detect_error(
                error_code="S1-I-V-0502",
                message=f"Failed to validate columns: {e}",
                severity="HIGH",
                fail_fast=False,
                additional_context={"file_path": str(file_path), "error": str(e)}
            )
            return False
    
    def validate_dataframe_columns(
        self,
        columns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[DetectionResult]:
        """
        Validate columns in a DataFrame (called after loading).
        
        Args:
            columns: List of available column names
            context: Additional context
        
        Returns:
            List of DetectionResult objects
        """
        if context:
            self.set_context(**context)
        
        if not self.required_columns:
            return []
        
        missing_columns = [col for col in self.required_columns if col not in columns]
        
        if missing_columns:
            self.detect_error(
                error_code="S1-I-V-0502",
                message=f"Missing required columns: {', '.join(missing_columns)}",
                severity="CRITICAL",
                fail_fast=True,
                remediation_type="MANUAL_FIX",
                additional_context={
                    "missing_columns": missing_columns,
                    "available_columns": columns
                }
            )
        
        return self.get_errors()
