"""
Template Guard Module (L0 - Pre-flight Validation)

Performs pre-flight validation before data loading.
Validates template signatures, schema versions, and configuration compatibility.

Fail Fast: Stops processing immediately if template version mismatch detected.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class TemplateValidationResult:
    """Result of template validation."""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    schema_version: Optional[str] = None
    template_signature: Optional[str] = None
    
    @property
    def can_proceed(self) -> bool:
        """Check if processing can continue."""
        return self.is_valid and len(self.errors) == 0
    
    @property
    def has_fail_fast(self) -> bool:
        """Check if any error requires fail-fast."""
        return any(e.get("fail_fast", False) for e in self.errors)


class TemplateGuard:
    """
    Pre-flight template validation guard.
    
    Validates:
    - Schema version compatibility
    - Template signature (checksum/hash)
    - Configuration compatibility
    - Required files existence
    
    Error Codes:
    - S0-I-F-0801: Template version mismatch (FAIL FAST)
    - S0-I-F-0802: Template signature invalid
    - S0-I-F-0803: Configuration incompatible
    - S0-I-F-0804: Required file missing
    """
    
    def __init__(
        self,
        expected_schema_version: str = "1.0.0",
        config_path: Optional[str] = None
    ):
        """
        Initialize TemplateGuard.
        
        Args:
            expected_schema_version: Expected schema version
            config_path: Path to configuration file
        """
        self.expected_schema_version = expected_schema_version
        self.config_path = Path(config_path) if config_path else None
        self._config: Optional[Dict] = None
    
    def verify_schema_version(
        self,
        expected: str,
        actual: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify schema version compatibility.
        
        Args:
            expected: Expected schema version
            actual: Actual schema version from template
        
        Returns:
            Tuple of (is_valid, error_dict or None)
        """
        # Parse versions
        try:
            exp_parts = [int(x) for x in expected.split(".")]
            act_parts = [int(x) for x in actual.split(".")]
        except ValueError:
            return False, {
                "error_code": "S0-I-F-0801",
                "message": f"Invalid version format: expected={expected}, actual={actual}",
                "fail_fast": True,
                "severity": "CRITICAL",
                "layer": "L0"
            }
        
        # Major version must match exactly
        if exp_parts[0] != act_parts[0]:
            return False, {
                "error_code": "S0-I-F-0801",
                "message": f"Major version mismatch: expected={expected}, actual={actual}",
                "fail_fast": True,
                "severity": "CRITICAL",
                "layer": "L0",
                "details": {
                    "expected_version": expected,
                    "actual_version": actual,
                    "expected_major": exp_parts[0],
                    "actual_major": act_parts[0]
                }
            }
        
        # Minor version can differ but warn if actual < expected
        if act_parts[1] < exp_parts[1]:
            return True, {
                "error_code": "S0-I-F-0801",
                "message": f"Minor version behind: expected={expected}, actual={actual}",
                "fail_fast": False,
                "severity": "WARNING",
                "layer": "L0",
                "details": {
                    "expected_version": expected,
                    "actual_version": actual
                }
            }
        
        return True, None
    
    def calculate_signature(self, template_path: str) -> str:
        """
        Calculate SHA-256 signature of template file.
        
        Args:
            template_path: Path to template file
        
        Returns:
            Hex digest of file hash
        """
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def validate_signature(
        self,
        template_path: str,
        expected_signature: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate template file signature.
        
        Args:
            template_path: Path to template file
            expected_signature: Expected SHA-256 hash (optional)
        
        Returns:
            Tuple of (is_valid, error_dict or None)
        """
        try:
            actual_signature = self.calculate_signature(template_path)
        except FileNotFoundError as e:
            return False, {
                "error_code": "S0-I-F-0802",
                "message": str(e),
                "fail_fast": True,
                "severity": "CRITICAL",
                "layer": "L0"
            }
        
        if expected_signature and actual_signature != expected_signature:
            return False, {
                "error_code": "S0-I-F-0802",
                "message": "Template signature mismatch",
                "fail_fast": True,
                "severity": "CRITICAL",
                "layer": "L0",
                "details": {
                    "template_path": template_path,
                    "expected_signature": expected_signature[:16] + "...",
                    "actual_signature": actual_signature[:16] + "..."
                }
            }
        
        return True, None
    
    def check_compatibility(
        self,
        config: Dict[str, Any]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check configuration compatibility.
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ["schema_version", "template_name", "columns"]
        for field in required_fields:
            if field not in config:
                errors.append({
                    "error_code": "S0-I-F-0803",
                    "message": f"Missing required config field: {field}",
                    "fail_fast": True,
                    "severity": "CRITICAL",
                    "layer": "L0",
                    "details": {"missing_field": field}
                })
        
        # Check schema version if present
        if "schema_version" in config:
            is_valid, error = self.verify_schema_version(
                self.expected_schema_version,
                config["schema_version"]
            )
            if error:
                errors.append(error)
        
        # Check columns exist and are valid
        if "columns" in config:
            if not isinstance(config["columns"], list):
                errors.append({
                    "error_code": "S0-I-F-0803",
                    "message": "Columns must be a list",
                    "fail_fast": True,
                    "severity": "CRITICAL",
                    "layer": "L0"
                })
            elif len(config["columns"]) == 0:
                errors.append({
                    "error_code": "S0-I-F-0803",
                    "message": "No columns defined in template",
                    "fail_fast": True,
                    "severity": "CRITICAL",
                    "layer": "L0"
                })
        
        return len(errors) == 0, errors
    
    def validate_files_exist(
        self,
        required_files: List[str]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that required files exist.
        
        Args:
            required_files: List of file paths to check
        
        Returns:
            Tuple of (all_exist, list of missing file errors)
        """
        errors = []
        
        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                errors.append({
                    "error_code": "S0-I-F-0804",
                    "message": f"Required file not found: {file_path}",
                    "fail_fast": True,
                    "severity": "CRITICAL",
                    "layer": "L0",
                    "details": {"missing_file": file_path}
                })
        
        return len(errors) == 0, errors
    
    def preflight_check(
        self,
        template_path: str,
        required_files: Optional[List[str]] = None,
        expected_signature: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> TemplateValidationResult:
        """
        Perform complete pre-flight validation.
        
        Args:
            template_path: Path to template file
            required_files: List of required file paths
            expected_signature: Expected template signature
            config: Configuration dict (loads from file if not provided)
        
        Returns:
            TemplateValidationResult with all validation results
        """
        errors = []
        warnings = []
        schema_version = None
        template_signature = None
        
        # 1. Validate template file exists and signature
        sig_valid, sig_error = self.validate_signature(template_path, expected_signature)
        if sig_error:
            if sig_error.get("fail_fast", False):
                errors.append(sig_error)
            else:
                warnings.append(sig_error)
        
        # 2. Load and validate configuration
        if config is None and self.config_path:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                errors.append({
                    "error_code": "S0-I-F-0803",
                    "message": f"Failed to load config: {e}",
                    "fail_fast": True,
                    "severity": "CRITICAL",
                    "layer": "L0"
                })
        
        if config:
            schema_version = config.get("schema_version")
            comp_valid, comp_errors = self.check_compatibility(config)
            for error in comp_errors:
                if error.get("fail_fast", False):
                    errors.append(error)
                else:
                    warnings.append(error)
        
        # 3. Check required files
        if required_files:
            files_valid, file_errors = self.validate_files_exist(required_files)
            errors.extend(file_errors)
        
        # Calculate signature for reference
        try:
            template_signature = self.calculate_signature(template_path)
        except FileNotFoundError:
            pass
        
        return TemplateValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            schema_version=schema_version,
            template_signature=template_signature
        )
    
    def get_validation_summary(self, result: TemplateValidationResult) -> Dict[str, Any]:
        """
        Get human-readable validation summary.
        
        Args:
            result: TemplateValidationResult
        
        Returns:
            Summary dictionary
        """
        return {
            "status": "VALID" if result.can_proceed else "INVALID",
            "can_proceed": result.can_proceed,
            "has_fail_fast": result.has_fail_fast,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "schema_version": result.schema_version,
            "template_signature": result.template_signature[:16] + "..." if result.template_signature else None,
            "errors": [
                {
                    "code": e.get("error_code"),
                    "message": e.get("message"),
                    "fail_fast": e.get("fail_fast", False),
                    "severity": e.get("severity")
                }
                for e in result.errors
            ],
            "warnings": [
                {
                    "code": w.get("error_code"),
                    "message": w.get("message"),
                    "severity": w.get("severity")
                }
                for w in result.warnings
            ]
        }
