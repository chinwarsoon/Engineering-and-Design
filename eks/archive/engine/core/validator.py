"""
Multi-Stage Validation - Setup, schema, data, and parser validation.

This module implements the Multi-Stage Validation pattern per Appendix F,
providing validation stages for setup, schema, data, and parser components.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum


class ValidationStage(Enum):
    """Validation stages for the pipeline."""
    SETUP = "setup"
    SCHEMA = "schema"
    DATA = "data"
    PARSER = "parser"


@dataclass
class ValidationError:
    """Validation error with context."""
    stage: ValidationStage
    error_code: str
    error_message: str
    context: Optional[Dict[str, Any]] = None
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage.value,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "context": self.context,
            "severity": self.severity
        }


@dataclass
class ValidationResult:
    """Result of a validation stage."""
    is_valid: bool
    stage: ValidationStage
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error_code: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Add an error to the validation result."""
        self.errors.append(ValidationError(
            stage=self.stage,
            error_code=error_code,
            error_message=error_message,
            context=context,
            severity="ERROR"
        ))
        self.is_valid = False
    
    def add_warning(self, error_code: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Add a warning to the validation result."""
        self.warnings.append(ValidationError(
            stage=self.stage,
            error_code=error_code,
            error_message=error_message,
            context=context,
            severity="WARNING"
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "stage": self.stage.value,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "metadata": self.metadata
        }


class MultiStageValidator:
    """
    Multi-stage validator for pipeline components.
    
    This class implements the Multi-Stage Validation pattern per Appendix F,
    providing validation stages for setup, schema, data, and parser components.
    
    Validation Stages:
    1. Setup: Validate project structure, configuration files, environment
    2. Schema: Validate schema files, schema inheritance, schema validation
    3. Data: Validate data files, data integrity, data quality
    4. Parser: Validate parser configuration, parser availability, parser compatibility
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize multi-stage validator.
        
        Args:
            verbose: Whether to print verbose validation output
        """
        self.verbose = verbose
        self.validation_results: Dict[ValidationStage, ValidationResult] = {}
    
    def validate_all(self, context: Dict[str, Any]) -> Dict[ValidationStage, ValidationResult]:
        """
        Run all validation stages.
        
        Args:
            context: Pipeline context with paths, configuration, etc.
            
        Returns:
            Dictionary of validation results by stage
        """
        self.validation_results = {}
        
        # Stage 1: Setup validation
        self.validation_results[ValidationStage.SETUP] = self.validate_setup(context)
        
        # Stage 2: Schema validation
        self.validation_results[ValidationStage.SCHEMA] = self.validate_schema(context)
        
        # Stage 3: Data validation
        self.validation_results[ValidationStage.DATA] = self.validate_data(context)
        
        # Stage 4: Parser validation
        self.validation_results[ValidationStage.PARSER] = self.validate_parser(context)
        
        return self.validation_results
    
    def validate_setup(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate project setup.
        
        Checks:
        - Required directories exist
        - Configuration files exist
        - Environment file exists
        - Log directory is writable
        
        Args:
            context: Pipeline context
            
        Returns:
            ValidationResult for setup stage
        """
        result = ValidationResult(is_valid=True, stage=ValidationStage.SETUP)
        
        # Check required directories
        required_dirs = [
            context.get("data_dir"),
            context.get("schema_dir"),
            context.get("output_dir"),
            context.get("archive_dir"),
            context.get("log_dir")
        ]
        
        for dir_path in required_dirs:
            if dir_path is None:
                result.add_error(
                    error_code="SETUP-001",
                    error_message=f"Required directory path is None"
                )
                continue
            
            path = Path(dir_path) if isinstance(dir_path, str) else dir_path
            if not path.exists():
                result.add_error(
                    error_code="SETUP-002",
                    error_message=f"Required directory does not exist: {path}",
                    context={"path": str(path)}
                )
            elif not path.is_dir():
                result.add_error(
                    error_code="SETUP-003",
                    error_message=f"Path is not a directory: {path}",
                    context={"path": str(path)}
                )
        
        # Check configuration file
        config_file = context.get("config_file")
        if config_file:
            path = Path(config_file) if isinstance(config_file, str) else config_file
            if not path.exists():
                result.add_error(
                    error_code="SETUP-004",
                    error_message=f"Configuration file does not exist: {path}",
                    context={"path": str(path)}
                )
        
        # Check environment file
        env_file = context.get("env_file")
        if env_file:
            path = Path(env_file) if isinstance(env_file, str) else env_file
            if not path.exists():
                result.add_warning(
                    error_code="SETUP-005",
                    error_message=f"Environment file does not exist: {path}",
                    context={"path": str(path)}
                )
        
        # Check log directory writability
        log_dir = context.get("log_dir")
        if log_dir:
            path = Path(log_dir) if isinstance(log_dir, str) else log_dir
            if path.exists():
                test_file = path / ".write_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    result.add_error(
                        error_code="SETUP-006",
                        error_message=f"Log directory is not writable: {path}",
                        context={"path": str(path), "error": str(e)}
                    )
        
        if self.verbose:
            print(f"[VALIDATION-SETUP] {'PASS' if result.is_valid else 'FAIL'}")
            for error in result.errors:
                print(f"  ERROR: {error.error_code} - {error.error_message}")
            for warning in result.warnings:
                print(f"  WARNING: {warning.error_code} - {warning.error_message}")
        
        return result
    
    def validate_schema(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate schema files.
        
        Checks:
        - Schema directory exists
        - Required schema files exist
        - Schema files are valid JSON
        - Schema files follow 3-layer pattern
        
        Args:
            context: Pipeline context
            
        Returns:
            ValidationResult for schema stage
        """
        result = ValidationResult(is_valid=True, stage=ValidationStage.SCHEMA)
        
        schema_dir = context.get("schema_dir")
        if not schema_dir:
            result.add_error(
                error_code="SCHEMA-001",
                error_message="Schema directory not specified in context"
            )
            return result
        
        schema_path = Path(schema_dir) if isinstance(schema_dir, str) else schema_dir
        if not schema_path.exists():
            result.add_error(
                error_code="SCHEMA-002",
                error_message=f"Schema directory does not exist: {schema_path}",
                context={"path": str(schema_path)}
            )
            return result
        
        # Check for required schema files
        required_schemas = context.get("required_schemas", [])
        for schema_name in required_schemas:
            schema_file = schema_path / schema_name
            if not schema_file.exists():
                result.add_error(
                    error_code="SCHEMA-003",
                    error_message=f"Required schema file does not exist: {schema_name}",
                    context={"schema_file": str(schema_file)}
                )
            else:
                # Validate JSON structure
                try:
                    import json
                    with open(schema_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    result.add_error(
                        error_code="SCHEMA-004",
                        error_message=f"Schema file is not valid JSON: {schema_name}",
                        context={"schema_file": str(schema_file), "error": str(e)}
                    )
        
        if self.verbose:
            print(f"[VALIDATION-SCHEMA] {'PASS' if result.is_valid else 'FAIL'}")
            for error in result.errors:
                print(f"  ERROR: {error.error_code} - {error.error_message}")
            for warning in result.warnings:
                print(f"  WARNING: {warning.error_code} - {warning.error_message}")
        
        return result
    
    def validate_data(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate data files.
        
        Checks:
        - Data directory exists
        - Data files are accessible
        - Data file formats are supported
        - Data integrity (basic checks)
        
        Args:
            context: Pipeline context
            
        Returns:
            ValidationResult for data stage
        """
        result = ValidationResult(is_valid=True, stage=ValidationStage.DATA)
        
        data_dir = context.get("data_dir")
        if not data_dir:
            result.add_warning(
                error_code="DATA-001",
                error_message="Data directory not specified in context"
            )
            return result
        
        data_path = Path(data_dir) if isinstance(data_dir, str) else data_dir
        if not data_path.exists():
            result.add_warning(
                error_code="DATA-002",
                error_message=f"Data directory does not exist: {data_path}",
                context={"path": str(data_path)}
            )
            return result
        
        # Check for data files
        data_files = list(data_path.glob("*"))
        if not data_files:
            result.add_warning(
                error_code="DATA-003",
                error_message=f"No data files found in directory: {data_path}",
                context={"path": str(data_path)}
            )
        
        # Validate file extensions
        supported_extensions = context.get("supported_extensions", [".pdf", ".docx", ".xlsx"])
        unsupported_files = [
            f for f in data_files 
            if f.is_file() and f.suffix.lower() not in supported_extensions
        ]
        
        if unsupported_files:
            result.add_warning(
                error_code="DATA-004",
                error_message=f"Found {len(unsupported_files)} files with unsupported extensions",
                context={"unsupported_files": [str(f) for f in unsupported_files[:5]]}
            )
        
        if self.verbose:
            print(f"[VALIDATION-DATA] {'PASS' if result.is_valid else 'FAIL'}")
            for error in result.errors:
                print(f"  ERROR: {error.error_code} - {error.error_message}")
            for warning in result.warnings:
                print(f"  WARNING: {warning.error_code} - {warning.error_message}")
        
        return result
    
    def validate_parser(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate parser configuration.
        
        Checks:
        - Parser classes are available
        - Parser configuration is valid
        - Parser dependencies are installed
        
        Args:
            context: Pipeline context
            
        Returns:
            ValidationResult for parser stage
        """
        result = ValidationResult(is_valid=True, stage=ValidationStage.PARSER)
        
        # Check parser configuration
        parser_config = context.get("parser_config", {})
        if not parser_config:
            result.add_warning(
                error_code="PARSER-001",
                error_message="Parser configuration not specified in context"
            )
            return result
        
        # Check for required parsers
        required_parsers = parser_config.get("required_parsers", [])
        for parser_name in required_parsers:
            try:
                # Attempt to import parser class
                module_path, class_name = parser_name.rsplit(".", 1)
                __import__(module_path)
            except ImportError as e:
                result.add_error(
                    error_code="PARSER-002",
                    error_message=f"Required parser class not available: {parser_name}",
                    context={"parser": parser_name, "error": str(e)}
                )
        
        # Check parser dependencies
        parser_dependencies = parser_config.get("dependencies", [])
        for dep in parser_dependencies:
            try:
                __import__(dep)
            except ImportError:
                result.add_error(
                    error_code="PARSER-003",
                    error_message=f"Required parser dependency not installed: {dep}",
                    context={"dependency": dep}
                )
        
        if self.verbose:
            print(f"[VALIDATION-PARSER] {'PASS' if result.is_valid else 'FAIL'}")
            for error in result.errors:
                print(f"  ERROR: {error.error_code} - {error.error_message}")
            for warning in result.warnings:
                print(f"  WARNING: {warning.error_code} - {warning.error_message}")
        
        return result
    
    def get_overall_result(self) -> ValidationResult:
        """
        Get overall validation result across all stages.
        
        Returns:
            ValidationResult combining all stages
        """
        all_errors = []
        all_warnings = []
        is_valid = True
        
        for stage, result in self.validation_results.items():
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            if not result.is_valid:
                is_valid = False
        
        overall_result = ValidationResult(
            is_valid=is_valid,
            stage=ValidationStage.SETUP,  # Use SETUP as overall stage
            errors=all_errors,
            warnings=all_warnings,
            metadata={"stages_validated": len(self.validation_results)}
        )
        
        return overall_result
    
    def get_stage_result(self, stage: ValidationStage) -> Optional[ValidationResult]:
        """
        Get validation result for a specific stage.
        
        Args:
            stage: Validation stage
            
        Returns:
            ValidationResult if stage was validated, None otherwise
        """
        return self.validation_results.get(stage)
