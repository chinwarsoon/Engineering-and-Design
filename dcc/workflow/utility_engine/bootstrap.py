"""
Utility Engine Bootstrap Submodule - Centralized Pipeline Initialization

Provides BootstrapManager class that encapsulates all pipeline initialization phases:
- CLI parsing and logging setup
- Path validation (base_path, home directory)
- ParameterTypeRegistry loading
- Native defaults building with schema-driven keys
- Fallback file/directory validation
- Environment testing
- Schema path resolution
- Effective parameters resolution
- Pre-pipeline input/output validation

Follows the Manager pattern (like ValidationManager) for stateful initialization
management. All validation occurs before PipelineContext creation.

Breadcrumb: base_path -> BootstrapManager -> bootstrap_all() -> to_pipeline_context()

Example:
    >>> manager = BootstrapManager(base_path)
    >>> manager.bootstrap_all(cli_args)
    >>> context = manager.to_pipeline_context()
    >>> result = run_engine_pipeline(context)

Phase 1 Implementation: Bootstrap Module Creation
Workplan: DCC-WP-UTIL-BOOTSTRAP-001
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Core engine imports
from core_engine.context import PipelineContext, PipelinePaths, PipelineState, PipelineData, ContextTraceItem
from core_engine.logging import DEBUG_LEVEL
from core_engine.paths import (
    default_base_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)
from core_engine.system import test_environment

# Utility engine imports
from utility_engine.console import status_print, milestone_print, debug_print
from utility_engine.errors import system_error_print
from utility_engine.paths import safe_resolve
from utility_engine.validation import (
    ValidationManager,
    ValidationStatus,
    ParameterTypeRegistry,
    get_parameter_registry,
)
from utility_engine.cli import (
    parse_cli_args,
    build_native_defaults,
    resolve_effective_parameters,
)

# Schema engine imports
from schema_engine import load_schema_parameters, default_schema_path

# Error handling imports (for schema-based messages)
from initiation_engine.error_handling import get_system_error_message


class BootstrapError(Exception):
    """
    Structured error for bootstrap failures.
    
    Provides error code, message, and phase for system_error_print() compatibility.
    
    Breadcrumb: phase failure -> BootstrapError(code, message, phase) -> system_error_print()
    
    Args:
        code: Error code in S-C-S-XXXX format (e.g., "S-F-S-0206", "S-C-S-0306")
        message: Human-readable error message (loaded from system_en.json via get_system_error_message)
        phase: Which bootstrap phase failed (e.g., "paths", "registry")
    
    Example:
        >>> msg = get_system_error_message("S-F-S-0206").format(detail="/invalid/path")
        >>> raise BootstrapError("S-F-S-0206", msg, "paths")
    """
    
    def __init__(self, code: str, message: str, phase: str):
        self.code = code
        self.message = message
        self.phase = phase
        super().__init__(f"[{code}] {message} (phase: {phase})")
    
    def to_system_error(self) -> Tuple[str, str]:
        """
        Return tuple for system_error_print() compatibility.
        
        Returns:
            Tuple of (system_error_code, message) where code is in S-C-S-XXXX format.
            All bootstrap errors now use standardized S-C-S-XXXX codes per WP-DCC-EH-BOOT-001.
        """
        return self.code, self.message


@dataclass
class BootstrapPhaseStatus:
    """
    Status tracking for a single bootstrap phase.
    
    Records start time, end time, duration, status, and error information
    for each bootstrap phase. Used for performance monitoring and debugging.
    
    Breadcrumb: _record_phase_start() -> _record_phase_complete()/failure() -> _phase_status
    
    Attributes:
        phase_id: Phase identifier (e.g., "P1_cli", "P2_paths")
        phase_name: Human-readable phase name (e.g., "CLI Parsing")
        status: Current status ("pending", "running", "complete", "failed")
        start_time: When phase started (ISO format datetime)
        end_time: When phase ended (ISO format datetime)
        duration_ms: Phase execution time in milliseconds
        error_code: Error code if phase failed
        
    Example:
        >>> status = BootstrapPhaseStatus(
        ...     phase_id="P1_cli",
        ...     phase_name="CLI Parsing",
        ...     status="complete",
        ...     start_time="2026-05-01T03:45:00.123Z",
        ...     end_time="2026-05-01T03:45:00.145Z",
        ...     duration_ms=22.0,
        ...     error_code=None
        ... )
    """
    phase_id: str
    phase_name: str
    status: str = "pending"  # "pending", "running", "complete", "failed"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None


class BootstrapManager:
    """
    Manager for centralized pipeline initialization.
    
    Encapsulates all setup phases (CLI, paths, registry, validation) and provides
    methods to run bootstrap and convert to PipelineContext. Follows the Manager
    pattern consistent with ValidationManager and ParameterTypeRegistry.
    
    Breadcrumb: base_path -> BootstrapManager -> bootstrap_all() -> to_pipeline_context()
    
    Attributes:
        base_path: Validated project root directory
        _bootstrapped: Whether bootstrap has completed successfully
        cli_args: Parsed CLI arguments (empty dict for UI mode)
        native_defaults: 15 native fallback parameters
        effective_parameters: Merged CLI + Schema + Native parameters
        schema_path: Validated schema file path
        registry: ParameterTypeRegistry with 42 schema-driven parameters
        validator: ValidationManager instance for path/parameter validation
        environment: Environment test results dict
        cli_overrides_provided: Whether CLI args were provided
        debug_mode: Derived from verbose level
    
    Example:
        >>> manager = BootstrapManager(Path("/path/to/project"))
        >>> manager.bootstrap_all(cli_args={"verbose": "normal"})
        >>> assert manager.is_bootstrapped
        >>> context = manager.to_pipeline_context()
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize BootstrapManager with base path.
        
        Args:
            base_path: Project root directory (will be validated during bootstrap)
        """
        self.base_path: Path = base_path
        self._bootstrapped: bool = False
        
        # Phase results (populated during bootstrap)
        self.cli_args: Dict[str, Any] = {}
        self.native_defaults: Dict[str, Any] = {}
        self.effective_parameters: Dict[str, Any] = {}
        self.schema_path: Optional[Path] = None
        
        # Initialized components
        self.registry: Optional[ParameterTypeRegistry] = None
        self.system_registry: Optional[ParameterTypeRegistry] = None
        self.dcc_registry: Optional[ParameterTypeRegistry] = None
        self.validator: Optional[ValidationManager] = None
        self.environment: Dict[str, Any] = {}
        
        # Metadata
        self.cli_overrides_provided: bool = False
        self.debug_mode: bool = False
        
        # Phase P3: Context trace data (populated during/after bootstrap)
        self._preload_trace: Optional[Dict[str, ContextTraceItem]] = None
        self._postload_trace: Optional[Dict[str, ContextTraceItem]] = None
        
        # Phase P4: Bootstrap phase tracking
        self._phase_status: Dict[str, BootstrapPhaseStatus] = {}
        self._bootstrap_start_time: Optional[str] = None
        self._initialize_phase_tracking()
    
    def _initialize_phase_tracking(self) -> None:
        """Initialize phase tracking for all 8 bootstrap phases."""
        self._phase_status = {
            "P1_cli": BootstrapPhaseStatus("P1_cli", "CLI Parsing"),
            "P2_paths": BootstrapPhaseStatus("P2_paths", "Path Validation"),
            "P3_registry": BootstrapPhaseStatus("P3_registry", "Registry Loading"),
            "P4_defaults": BootstrapPhaseStatus("P4_defaults", "Native Defaults Building"),
            "P5_fallback": BootstrapPhaseStatus("P5_fallback", "Fallback Validation"),
            "P6_env": BootstrapPhaseStatus("P6_env", "Environment Testing"),
            "P7_schema": BootstrapPhaseStatus("P7_schema", "Schema Resolution"),
            "P8_params": BootstrapPhaseStatus("P8_params", "Parameters Resolution"),
            "P3_trace": BootstrapPhaseStatus("P3_trace", "Context Trace Building"),
        }
        self._bootstrap_start_time = datetime.now().isoformat()
    
    def _record_phase_start(self, phase_id: str) -> None:
        """Record phase start time and mark as running."""
        if phase_id in self._phase_status:
            self._phase_status[phase_id].status = "running"
            self._phase_status[phase_id].start_time = datetime.now().isoformat()
    
    def _record_phase_complete(self, phase_id: str) -> None:
        """Record phase completion and calculate duration."""
        if phase_id in self._phase_status:
            phase = self._phase_status[phase_id]
            phase.status = "complete"
            phase.end_time = datetime.now().isoformat()
            if phase.start_time:
                start = datetime.fromisoformat(phase.start_time)
                end = datetime.fromisoformat(phase.end_time)
                phase.duration_ms = (end - start).total_seconds() * 1000
    
    def _record_phase_failure(self, phase_id: str, error_code: str) -> None:
        """Record phase failure with error code."""
        if phase_id in self._phase_status:
            phase = self._phase_status[phase_id]
            phase.status = "failed"
            phase.end_time = datetime.now().isoformat()
            phase.error_code = error_code
            if phase.start_time:
                start = datetime.fromisoformat(phase.start_time)
                end = datetime.fromisoformat(phase.end_time)
                phase.duration_ms = (end - start).total_seconds() * 1000
    
    @property
    def bootstrap_summary(self) -> Dict[str, Any]:
        """
        Return dynamic summary of bootstrap status for banner display.
        
        Returns:
            Dict with status, completed_count, total_count, failed_phase, error_code, total_duration_ms
        """
        completed = sum(1 for p in self._phase_status.values() if p.status == "complete")
        failed = [p for p in self._phase_status.values() if p.status == "failed"]
        total = len(self._phase_status)
        
        # Determine overall status
        if failed:
            status = "failed"
        elif completed == total:
            status = "complete"
        elif completed > 0:
            status = "partial"
        else:
            status = "in_progress"
        
        # Calculate total duration
        total_duration = None
        if self._bootstrap_start_time:
            start = datetime.fromisoformat(self._bootstrap_start_time)
            end = datetime.now()
            total_duration = (end - start).total_seconds() * 1000
        
        return {
            "status": status,
            "completed_count": completed,
            "total_count": total,
            "failed_phase": failed[0].phase_id if failed else None,
            "error_code": failed[0].error_code if failed else None,
            "total_duration_ms": total_duration,
        }
    
    @property
    def is_bootstrapped(self) -> bool:
        """Check if bootstrap has completed successfully."""
        return self._bootstrapped
    
    @property
    def preload_trace(self) -> Dict[str, ContextTraceItem]:
        """
        Get preload trace data (available after bootstrap completes).
        
        Breadcrumb: bootstrap_all() -> _build_preload_trace() -> preload_trace property
        
        Returns:
            Dictionary of ContextTraceItem with pre-context state
            
        Raises:
            BootstrapError: If bootstrap has not been completed
        """
        if not self._bootstrapped:
            raise BootstrapError(
                "S-B-S-0601",
                "Bootstrap must be completed before accessing preload trace",
                "traces"
            )
        if self._preload_trace is None:
            raise BootstrapError(
                "S-B-S-0602",
                "Preload trace not built - pre-pipeline validation may have failed",
                "traces"
            )
        return self._preload_trace
    
    @property
    def postload_trace(self) -> Optional[Dict[str, ContextTraceItem]]:
        """
        Get postload trace data (available after to_pipeline_context() called).
        
        Breadcrumb: to_pipeline_context() -> _build_postload_trace() -> postload_trace property
        
        Returns:
            Dictionary of ContextTraceItem with post-context state, or None if not yet built
        """
        return self._postload_trace
    
    def bootstrap_all(self, cli_args: Optional[Dict[str, Any]] = None) -> BootstrapManager:
        """
        Run all initialization phases for CLI mode.
        
        Executes 8 phases in sequence:
        1. CLI parsing and logging setup
        2. Path validation (base_path, home directory)
        3. Registry loading
        4. Native defaults building
        5. Fallback validation
        6. Environment testing
        7. Schema resolution
        8. Parameters resolution and pre-pipeline validation
        
        Args:
            cli_args: Optional CLI arguments dict. If None, will call parse_cli_args()
        
        Returns:
            Self for method chaining: BootstrapManager(...).bootstrap_all().to_pipeline_context()
        
        Raises:
            BootstrapError: If any phase fails validation
        
        Example:
            >>> manager = BootstrapManager(base_path).bootstrap_all()
            >>> # or with explicit args
            >>> manager = BootstrapManager(base_path).bootstrap_all({"verbose": "debug"})
        """
        try:
            # Phase 1: CLI parsing and logging
            self._bootstrap_cli(cli_args)
            
            # Phase 2: Path validation
            self._bootstrap_paths()
            
            # Phase 3: Registry loading
            self._bootstrap_registry()
            
            # Phase 4: Native defaults
            self._bootstrap_defaults()
            
            # Phase 5: Fallback validation
            self._bootstrap_fallback_validation()
            
            # Phase 6: Environment testing
            self._bootstrap_environment()
            
            # Phase 7: Schema resolution
            self._bootstrap_schema()
            
            # Phase 8: Parameters resolution and pre-pipeline validation
            self._bootstrap_parameters()
            self._bootstrap_pre_pipeline_validation()
            
            # Mark as bootstrapped
            self._bootstrapped = True
            debug_print("Bootstrap Complete: All 8 phases completed successfully")
            
            return self
            
        except BootstrapError:
            # Re-raise BootstrapError as-is
            raise
        except Exception as exc:
            # Wrap unexpected errors
            raise BootstrapError("B-UNK-001", f"Unexpected bootstrap error: {exc}", "unknown")
    
    def bootstrap_for_ui(
        self,
        upload_file_name: str,
        output_folder: str = "output",
        schema_file_name: Optional[str] = None,
        debug_mode: bool = False,
        nrows: Optional[int] = None,
        **additional_params
    ) -> BootstrapManager:
        """
        Run initialization phases for UI mode.
        
        Similar to bootstrap_all() but skips CLI parsing (uses provided UI values).
        UI-provided values take precedence over schema and native defaults.
        
        Args:
            upload_file_name: Excel file name selected by user
            output_folder: Output subfolder name (default: "output")
            schema_file_name: Optional custom schema file
            debug_mode: Enable debug logging
            nrows: Optional row limit for testing
            **additional_params: Additional UI-provided parameters
        
        Returns:
            Self for method chaining
        
        Raises:
            BootstrapError: If any phase fails validation
        """
        try:
            # Set CLI args from UI-provided values (empty dict, UI values applied later)
            self.cli_args = {}
            self.cli_overrides_provided = True
            self.debug_mode = debug_mode
            
            # Note: Logger should be setup by the UI entry point before calling bootstrap_for_ui()
            debug_print(f"Bootstrap UI Mode: Base: {self.base_path}")
            
            # Phase 2: Path validation (same as CLI mode)
            self._bootstrap_paths()
            
            # Phase 3: Registry loading
            self._bootstrap_registry()
            
            # Phase 4: Native defaults
            self._bootstrap_defaults()
            
            # Phase 6: Environment testing (skip 5 - no fallback validation for UI)
            self._bootstrap_environment()
            
            # Phase 7: Schema resolution (with optional custom schema)
            if schema_file_name:
                self.schema_path = self.base_path / schema_file_name
            else:
                self._bootstrap_schema()
            
            # Phase 8: Parameters resolution with UI overrides
            self._bootstrap_parameters_for_ui(
                upload_file_name=upload_file_name,
                output_folder=output_folder,
                debug_mode=debug_mode,
                nrows=nrows,
                **additional_params
            )
            self._bootstrap_pre_pipeline_validation()
            
            # Mark as bootstrapped
            self._bootstrapped = True
            debug_print("Bootstrap Complete: UI mode - All phases completed")
            
            return self
            
        except BootstrapError:
            raise
        except Exception as exc:
            raise BootstrapError("B-UNK-002", f"Unexpected bootstrap error (UI): {exc}", "unknown")
    
    def to_pipeline_context(self) -> PipelineContext:
        """
        Convert bootstrapped state to PipelineContext.
        
        Requires that bootstrap_all() or bootstrap_for_ui() has been called
        and completed successfully.
        
        Returns:
            PipelineContext with validated paths and parameters
        
        Raises:
            BootstrapError: If bootstrap has not been completed
        
        Example:
            >>> manager = BootstrapManager(base_path).bootstrap_all()
            >>> context = manager.to_pipeline_context()
            >>> result = run_engine_pipeline(context)
        """
        if not self._bootstrapped:
            raise BootstrapError(
                "B-CTX-001",
                "Must bootstrap before creating PipelineContext",
                "context"
            )
        
        # Resolve paths from effective parameters
        from utility_engine.paths import safe_resolve
        
        csv_output_path = self.base_path / self.effective_parameters.get(
            "download_file_path", "output"
        ) / f"{self.effective_parameters.get('output_filename_pattern', 'processed_dcc_universal')}.csv"
        
        excel_output_path = csv_output_path.with_suffix(".xlsx")
        
        summary_path = csv_output_path.parent / self.effective_parameters.get(
            "summary_filename", "processing_summary.txt"
        )
        
        # Resolve debug log path
        debug_log_filename = self.effective_parameters.get("debug_log_filename", "debug_log.json")
        debug_log_path = csv_output_path.parent / debug_log_filename
        
        paths = PipelinePaths(
            base_path=self.base_path,
            excel_path=Path(self.effective_parameters["upload_file_name"]),
            schema_path=self.schema_path or Path(self.effective_parameters["schema_register_file"]),
            csv_output_path=csv_output_path,
            excel_output_path=excel_output_path,
            summary_path=summary_path,
            debug_log_path=debug_log_path,
        )
        
        # Create PipelineContext
        context = PipelineContext(
            paths=paths,
            parameters=self.effective_parameters,
            debug_mode=self.debug_mode
        )
        
        # Phase P3: Build postload trace after context creation
        self._build_postload_trace(paths)
        
        debug_print(f"PipelineContext Created: Paths validated, {len(self.effective_parameters)} parameters")
        
        return context
    
    # ==========================================================================
    # Phase 1: CLI Parsing and Logging
    # ==========================================================================
    
    def _bootstrap_cli(self, cli_args: Optional[Dict[str, Any]] = None) -> None:
        """
        Phase 1: Parse CLI args and determine debug mode.
        
        Note: Logger is now setup in main() before bootstrap_all() is called.
        
        Breadcrumb: cli_args -> parse_cli_args() -> debug_mode determination
        
        Args:
            cli_args: Optional pre-parsed CLI arguments. If None, calls parse_cli_args()
        
        Raises:
            BootstrapError: If CLI parsing fails
        """
        self._record_phase_start("P1_cli")
        try:
            if cli_args is None:
                # Parse CLI args from sys.argv
                args, parsed_cli_args, cli_overrides = parse_cli_args()
                self.cli_args = parsed_cli_args
                self.cli_overrides_provided = cli_overrides
            else:
                # Use provided CLI args
                self.cli_args = cli_args or {}
                self.cli_overrides_provided = bool(cli_args)
            
            # Note: Logger is now setup in main() before bootstrap_all() is called
            # This ensures logging is available from the start of pipeline execution
            
            # Determine debug mode from verbose level
            verbose = self.cli_args.get("verbose_level", "normal")
            self.debug_mode = verbose in ["debug", "trace"]
            
            self._record_phase_complete("P1_cli")
            debug_print(f"Bootstrap Phase 1: CLI parsed, {len(self.cli_args)} args")
            
        except Exception as exc:
            self._record_phase_failure("P1_cli", "B-CLI-001")
            raise BootstrapError("B-CLI-001", f"CLI parsing failed: {exc}", "cli")
    
    # ==========================================================================
    # Phase 2: Path Validation
    # ==========================================================================
    
    def _bootstrap_paths(self) -> None:
        """
        Phase 2: Validate base_path and home directory.
        
        Breadcrumb: base_path -> ValidationManager.validate_path() -> ValidationManager.validate_home_directory()
        
        Raises:
            BootstrapError: If path validation fails
        """
        self._record_phase_start("P2_paths")
        try:
            # Initialize validator
            self.validator = ValidationManager()
            
            # Validate base_path
            base_validation = self.validator.validate_path_with_system_context(
                path_input=self.base_path,
                path_type="directory",
                name="Base Directory",
                required=True,
                base_path=None
            )
            
            if base_validation.status.name == "FAIL":
                msg = get_system_error_message("S-F-S-0206").format(detail=base_validation.message)
                raise BootstrapError("S-F-S-0206", msg, "paths")
            
            self.base_path = base_validation.path
            
            # Validate home directory (warning only, not fatal)
            home_validation = self.validator.validate_home_directory()
            if home_validation.status.name == "FAIL":
                debug_print(f"Warning: Home directory validation: {home_validation.message}")
            else:
                self._record_phase_complete("P2_paths")
                debug_print(f"Bootstrap Phase 2: Base path validated: {self.base_path}")
            
        except BootstrapError as e:
            self._record_phase_failure("P2_paths", e.code)
            raise
        except Exception as exc:
            self._record_phase_failure("P2_paths", "S-F-S-0207")
            msg = get_system_error_message("S-F-S-0207").format(detail=str(exc))
            raise BootstrapError("S-F-S-0207", msg, "paths")
    
    # ==========================================================================
    # Phase 3: Registry Loading
    # ==========================================================================
    
    def _bootstrap_registry(self) -> None:
        """
        Phase 3: Load ParameterTypeRegistry for both System and DCC domains.
        
        Breadcrumb: base_path -> get_parameter_registry() -> unified registry loaded
        
        Loads:
        - System parameters from project_setup.json
        - DCC parameters from dcc_register_setup.json
        
        Both are loaded into a single unified registry.
        
        Raises:
            BootstrapError: If registry loading fails
        """
        self._record_phase_start("P3_registry")
        try:
            # Define schema paths
            dcc_params_path = self.base_path / "config" / "schemas" / "dcc_register_setup.json"
            system_params_path = self.base_path / "config" / "schemas" / "project_setup.json"
            
            # Fallback to legacy global_parameters.json (deprecated)
            if not dcc_params_path.exists():
                legacy_path = self.base_path / "config" / "schemas" / "global_parameters.json"
                if legacy_path.exists():
                    dcc_params_path = legacy_path
            
            if dcc_params_path.exists():
                # Load unified registry with both system and DCC parameters
                self.registry = ParameterTypeRegistry()
                self.registry.load_from_schema(
                    schema_path=dcc_params_path,
                    system_schema_path=system_params_path if system_params_path.exists() else None
                )
                
                # Store references for backward compatibility
                self.system_registry = self.registry
                self.dcc_registry = self.registry
                
                domains = self.registry._metadata.get("domains", [])
                debug_print(f"Bootstrap Phase 3: Unified registry loaded: {self.registry.parameter_count} parameters (domains: {domains})")
            else:
                # Continue without registry (legacy mode)
                self.registry = None
                self.system_registry = None
                self.dcc_registry = None
                debug_print("Bootstrap Phase 3: Registry not found, using legacy mode")
            
            self._record_phase_complete("P3_registry")
            
        except Exception as exc:
            # Registry failure is not fatal - can continue in legacy mode
            self._record_phase_failure("P3_registry", "S-C-S-0306")
            msg = get_system_error_message("S-C-S-0306").format(detail=str(exc))
            debug_print(f"Warning: {msg}")
            self.registry = None
            self.system_registry = None
            self.dcc_registry = None
    
    # ==========================================================================
    # Phase 4: Native Defaults Building
    # ==========================================================================
    
    def _bootstrap_defaults(self) -> None:
        """
        Phase 4: Build native defaults with schema-driven keys.
        
        Breadcrumb: base_path + registry -> build_native_defaults() -> native_defaults
        
        Raises:
            BootstrapError: If defaults building fails
        """
        self._record_phase_start("P4_defaults")
        try:
            self.native_defaults = build_native_defaults(self.base_path, registry=self.registry)
            self._record_phase_complete("P4_defaults")
            debug_print(f"Bootstrap Phase 4: Native defaults: {len(self.native_defaults)} parameters")
            
        except Exception as exc:
            self._record_phase_failure("P4_defaults", "S-C-S-0307")
            msg = get_system_error_message("S-C-S-0307").format(detail=str(exc))
            raise BootstrapError("S-C-S-0307", msg, "defaults")
    
    # ==========================================================================
    # Phase 5: Fallback Validation
    # ==========================================================================
    
    def _bootstrap_fallback_validation(self) -> None:
        """
        Phase 5: Validate native fallback files and directories.
        
        Only validates if CLI has not provided override values.
        
        Breadcrumb: cli_args vs native_defaults -> validate files/dirs -> skip if CLI provided
        
        Raises:
            BootstrapError: If fallback validation fails critically
        """
        self._record_phase_start("P5_fallback")
        try:
            # Get schema-driven parameter keys
            upload_file_key = "upload_file_name"
            download_path_key = "download_file_path"
            data_dir_key = "data_dir"
            config_dir_key = "config_dir"
            
            if self.registry:
                upload_file_key = self.registry.get_canonical_key("upload_file_name")
                download_path_key = self.registry.get_canonical_key("download_file_path")
                data_dir_key = self.registry.get_canonical_key("data_dir")
                config_dir_key = self.registry.get_canonical_key("config_dir")
            
            # Check if CLI provided upload file
            cli_upload = self.cli_args.get(upload_file_key)
            native_upload = self.native_defaults.get(upload_file_key)
            
            files_to_validate = []
            dirs_to_validate = []
            
            # Validate native upload file only if CLI didn't provide one
            if not cli_upload and native_upload:
                files_to_validate.append((
                    Path(native_upload),
                    "Native Default Input File",
                    False,  # Not required (fallback)
                    False   # Don't create parent
                ))
            
            # Check if CLI provided output path
            cli_output = self.cli_args.get(download_path_key)
            native_output = self.native_defaults.get(download_path_key)
            
            # Validate native output dir only if CLI didn't provide one
            if not cli_output and native_output:
                dirs_to_validate.append((
                    Path(native_output),
                    "Native Default Output Directory",
                    False,  # Not required (fallback)
                    False   # Don't create
                ))
            
            # Always validate infrastructure directories
            data_dir = self.base_path / self.native_defaults.get(data_dir_key, "data")
            dirs_to_validate.append((data_dir, "Data Directory", False, False))
            
            config_dir = self.base_path / self.native_defaults.get(config_dir_key, "config")
            dirs_to_validate.append((config_dir, "Config Directory", False, False))
            
            # Run validation if there are items to check
            if files_to_validate or dirs_to_validate:
                result = self.validator.validate_paths_and_parameters(
                    files=files_to_validate,
                    directories=dirs_to_validate
                )
                
                if result.has_errors:
                    errors = "\n".join(result.errors)
                    self._record_phase_complete("P5_fallback")
                    debug_print(f"Bootstrap Phase 5: Fallback validation warnings:\n{errors}")
                else:
                    self._record_phase_complete("P5_fallback")
                    debug_print(f"Bootstrap Phase 5: Fallback validation: {len(files_to_validate)} files, {len(dirs_to_validate)} dirs")
            else:
                self._record_phase_complete("P5_fallback")
                debug_print("Bootstrap Phase 5: No fallback validation needed")
            
        except Exception as exc:
            # Fallback validation failure is warning only, not fatal
            self._record_phase_failure("P5_fallback", "S-F-S-0208")
            msg = get_system_error_message("S-F-S-0208").format(detail=str(exc))
            debug_print(f"Warning: {msg}")
    
    # ==========================================================================
    # Phase 6: Environment Testing
    # ==========================================================================
    
    def _bootstrap_environment(self) -> None:
        """
        Phase 6: Test Python environment and dependencies.
        
        Breadcrumb: test_environment() -> check deps -> verify ready
        
        Raises:
            BootstrapError: If environment test fails
        """
        self._record_phase_start("P6_env")
        try:
            self.environment = test_environment(base_path=self.base_path)
            
            if not self.environment.get("ready", False):
                missing = ", ".join(self.environment.get("missing_packages", [])) or "see output"
                msg = get_system_error_message("S-E-S-0105").format(detail=missing)
                raise BootstrapError("S-E-S-0105", msg, "environment")
            
            self._record_phase_complete("P6_env")
            debug_print("Bootstrap Phase 6: Environment ready")
            
        except BootstrapError as e:
            self._record_phase_failure("P6_env", e.code)
            raise
        except Exception as exc:
            self._record_phase_failure("P6_env", "S-E-S-0106")
            msg = get_system_error_message("S-E-S-0106").format(detail=str(exc))
            raise BootstrapError("S-E-S-0106", msg, "environment")
    
    # ==========================================================================
    # Phase 7: Schema Resolution
    # ==========================================================================
    
    def _bootstrap_schema(self) -> None:
        """
        Phase 7: Resolve and validate schema file path.
        
        Breadcrumb: cli_args or native_defaults -> resolve schema path -> validate exists
        
        Raises:
            BootstrapError: If schema resolution fails
        """
        self._record_phase_start("P7_schema")
        try:
            # Get schema path from CLI or native defaults
            schema_key = "schema_register_file"
            if self.registry:
                schema_key = self.registry.get_canonical_key("schema_register_file")
            
            schema_path_input = self.cli_args.get(schema_key) or self.native_defaults.get(schema_key)
            
            if not schema_path_input:
                schema_path_input = default_schema_path(self.base_path)
            
            # Validate schema path
            schema_validation = self.validator.validate_path_with_system_context(
                path_input=Path(schema_path_input),
                path_type="file",
                name="Schema File",
                required=True,
                base_path=self.base_path
            )
            
            if schema_validation.status.name == "FAIL":
                msg = get_system_error_message("S-F-S-0209").format(detail=schema_validation.message)
                raise BootstrapError("S-F-S-0209", msg, "schema")
            
            self.schema_path = schema_validation.path
            self._record_phase_complete("P7_schema")
            debug_print(f"Bootstrap Phase 7: Schema: {self.schema_path.name}")
            
        except BootstrapError as e:
            self._record_phase_failure("P7_schema", e.code)
            raise
        except Exception as exc:
            self._record_phase_failure("P7_schema", "S-C-S-0308")
            msg = get_system_error_message("S-C-S-0308").format(detail=str(exc))
            raise BootstrapError("S-C-S-0308", msg, "schema")
    
    # ==========================================================================
    # Phase 8: Parameters Resolution
    # ==========================================================================
    
    def _bootstrap_parameters(self) -> None:
        """
        Phase 8a: Resolve effective parameters (CLI mode).
        
        Breadcrumb: cli_args + native_defaults + schema -> resolve_effective_parameters()
        
        Raises:
            BootstrapError: If parameter resolution fails
        """
        self._record_phase_start("P8_params")
        try:
            # Load parameters from both system and DCC domains
            system_params_path = self.base_path / "config" / "schemas" / "project_config.json"
            dcc_schema_path = self.schema_path or Path(default_schema_path(self.base_path))
            
            self.effective_parameters = resolve_effective_parameters(
                dcc_schema_path=dcc_schema_path,
                cli_args=self.cli_args,
                native_defaults=self.native_defaults,
                load_schema_params_fn=load_schema_parameters,
                registry=self.registry,
                system_params_path=system_params_path if system_params_path.exists() else None
            )
            
            # Apply platform path resolution
            self.effective_parameters = resolve_platform_paths(
                self.effective_parameters,
                self.base_path,
                status_print
            )
            
            self._record_phase_complete("P8_params")
            debug_print(f"Bootstrap Phase 8: Parameters: {len(self.effective_parameters)} total")
            
        except Exception as exc:
            self._record_phase_failure("P8_params", "S-C-S-0309")
            msg = get_system_error_message("S-C-S-0309").format(detail=str(exc))
            raise BootstrapError("S-C-S-0309", msg, "parameters")
    
    def _bootstrap_parameters_for_ui(self, **ui_params) -> None:
        """
        Phase 8a (UI): Resolve effective parameters with UI overrides.
        
        Breadcrumb: ui_params + native_defaults + schema -> merge with UI precedence
        
        Args:
            **ui_params: UI-provided parameter overrides
        
        Raises:
            BootstrapError: If parameter resolution fails
        """
        try:
            # Start with native defaults
            params = self.native_defaults.copy()
            
            # Load schema parameters
            if self.schema_path and self.schema_path.exists():
                try:
                    schema_params = load_schema_parameters(self.schema_path)
                    params.update(schema_params)
                except Exception:
                    pass  # Schema params optional
            
            # Apply UI overrides (highest precedence)
            params.update(ui_params)
            
            # Apply platform path resolution
            self.effective_parameters = resolve_platform_paths(
                params,
                self.base_path,
                status_print
            )
            
            milestone_print("Bootstrap Phase 8", f"UI Parameters: {len(self.effective_parameters)} total")
            
        except Exception as exc:
            msg = get_system_error_message("S-C-S-0310").format(detail=str(exc))
            raise BootstrapError("S-C-S-0310", msg, "parameters")
    
    def _bootstrap_pre_pipeline_validation(self) -> None:
        """
        Phase 8b: Validate input/output paths before pipeline execution.
        
        Breadcrumb: effective_parameters -> validate input file -> validate output dir
        
        Raises:
            BootstrapError: If pre-pipeline validation fails
        """
        try:
            # Get parameter keys
            upload_key = "upload_file_name"
            download_key = "download_file_path"
            overwrite_key = "overwrite_existing_downloads"
            
            if self.registry:
                upload_key = self.registry.get_canonical_key("upload_file_name")
                download_key = self.registry.get_canonical_key("download_file_path")
                overwrite_key = self.registry.get_canonical_key("overwrite_existing_downloads")
            
            # Validate input file
            input_file = self.effective_parameters.get(upload_key)
            if not input_file:
                msg = get_system_error_message("S-F-S-0210").format(detail="upload_file_name not set")
                raise BootstrapError("S-F-S-0210", msg, "pre-pipeline")
            
            input_validation = self.validator.validate_path_with_system_context(
                path_input=Path(input_file),
                path_type="file",
                name="Input File",
                required=True,
                base_path=self.base_path
            )
            
            if input_validation.status.name == "FAIL":
                msg = get_system_error_message("S-F-S-0211").format(detail=input_validation.message)
                raise BootstrapError("S-F-S-0211", msg, "pre-pipeline")
            
            # Validate output directory (create if needed)
            output_dir = self.effective_parameters.get(download_key, "output")
            output_path = self.base_path / output_dir
            
            # Ensure output directory exists or can be created
            if not output_path.exists():
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    msg = get_system_error_message("S-F-S-0212").format(detail=str(exc))
                    raise BootstrapError("S-F-S-0212", msg, "pre-pipeline")
            
            debug_print("Bootstrap Phase 8b: Pre-pipeline validation complete")
            
            # Phase P3: Build preload trace and validate pre-context gate
            self._build_preload_trace()
            self._validate_pre_context_gate()
            
        except BootstrapError:
            raise
        except Exception as exc:
            msg = get_system_error_message("S-R-S-0407").format(detail=str(exc))
            raise BootstrapError("S-R-S-0407", msg, "pre-pipeline")
    
    def _build_preload_trace(self) -> None:
        """
        Phase P3: Build preload trace from current bootstrap state.
        
        Breadcrumb: bootstrap state -> _preload_trace attribute
        
        Builds trace data BEFORE PipelineContext is created, capturing
        the resolved values from all bootstrap phases.
        
        Raises:
            BootstrapError: If required state is not available
        """
        self._record_phase_start("P3_trace")
        try:
            # Build export paths for trace
            csv_output_path = self.base_path / self.effective_parameters.get(
                "download_file_path", "output"
            ) / f"{self.effective_parameters.get('output_filename_pattern', 'processed_dcc_universal')}.csv"
            
            excel_output_path = csv_output_path.with_suffix(".xlsx")
            summary_path = csv_output_path.parent / self.effective_parameters.get(
                "summary_filename", "processing_summary.txt"
            )
            
            # Build phases status for trace (convert to serializable format)
            phases_status = {}
            for phase_id, status in self._phase_status.items():
                phases_status[phase_id] = {
                    "phase_id": status.phase_id,
                    "phase_name": status.phase_name,
                    "status": status.status,
                    "start_time": status.start_time,
                    "end_time": status.end_time,
                    "duration_ms": status.duration_ms,
                    "error_code": status.error_code,
                }
            
            self._preload_trace = {
                "phases": ContextTraceItem(
                    "phases", phases_status, "phase_tracking", "dict", True
                ),
                "base_path": ContextTraceItem(
                    "base_path", str(self.base_path), "resolved", "directory", True
                ),
                "schema_path": ContextTraceItem(
                    "schema_path", str(self.schema_path or ""), "resolved", "file", 
                    bool(self.schema_path)
                ),
                "upload_file_name": ContextTraceItem(
                    "upload_file_name",
                    self.effective_parameters.get("upload_file_name"),
                    "effective_parameters",
                    "file",
                    bool(self.effective_parameters.get("upload_file_name")),
                ),
                "download_file_path": ContextTraceItem(
                    "download_file_path",
                    self.effective_parameters.get("download_file_path"),
                    "effective_parameters",
                    "directory",
                    bool(self.effective_parameters.get("download_file_path")),
                ),
                "csv_output_path": ContextTraceItem(
                    "csv_output_path", str(csv_output_path), "resolved", "file", True
                ),
                "excel_output_path": ContextTraceItem(
                    "excel_output_path", str(excel_output_path), "resolved", "file", True
                ),
                "summary_path": ContextTraceItem(
                    "summary_path", str(summary_path), "resolved", "file", True
                ),
                "parameters": ContextTraceItem(
                    "parameters", self.effective_parameters, "effective_parameters", 
                    "dict", isinstance(self.effective_parameters, dict)
                ),
            }
            
            self._record_phase_complete("P3_trace")
            debug_print("Bootstrap Phase P3a: Preload trace built")
            
        except Exception as exc:
            self._record_phase_failure("P3_trace", "S-B-S-0603")
            raise BootstrapError("S-B-S-0603", f"Failed to build preload trace during bootstrap: {exc}", "traces")
    
    def _validate_pre_context_gate(self) -> None:
        """
        Phase P3: Validate pre-context gate before allowing PipelineContext creation.
        
        Breadcrumb: _preload_trace -> validation check -> gate pass/fail
        
        Fail-fast if preload trace contains invalid items or validation failed.
        
        Raises:
            BootstrapError: If gate validation fails (code B-GATE-001)
        """
        if self._preload_trace is None:
            raise BootstrapError(
                "S-B-S-0605",
                "Cannot validate gate: preload trace not built",
                "gate"
            )
        
        # Check for invalid items in preload trace
        invalid_items = [
            key for key, item in self._preload_trace.items() 
            if not item.validated
        ]
        
        if invalid_items:
            raise BootstrapError(
                "S-B-S-0604",
                f"Pre-context validation gate failed: invalid preload fields: {', '.join(invalid_items)}",
                "gate"
            )
        
        # Check if validator has errors (if validation was performed)
        if self.validator and hasattr(self.validator, '_last_validation_result'):
            last_result = self.validator._last_validation_result
            if last_result and getattr(last_result, 'has_errors', False):
                errors = getattr(last_result, 'errors', [])
                raise BootstrapError(
                    "B-GATE-001",
                    f"Pre-context validation gate failed: {'; '.join(errors)}",
                    "gate"
                )
        
        debug_print("Bootstrap Phase P3b: Pre-context gate validated")
    
    def _build_postload_trace(self, paths: PipelinePaths) -> None:
        """
        Phase P3: Build postload trace from PipelinePaths after context creation.
        
        Breadcrumb: PipelinePaths -> _postload_trace attribute
        
        Builds trace data AFTER PipelineContext is created, confirming
        all paths are ready and in the context.
        
        Args:
            paths: PipelinePaths instance from created PipelineContext
        """
        try:
            self._postload_trace = {
                "base_path": ContextTraceItem(
                    "base_path", str(paths.base_path), "context.paths", "directory", True, "ready"
                ),
                "schema_path": ContextTraceItem(
                    "schema_path", str(paths.schema_path), "context.paths", "file", True, "ready"
                ),
                "excel_path": ContextTraceItem(
                    "excel_path", str(paths.excel_path), "context.paths", "file", True, "ready"
                ),
                "csv_output_path": ContextTraceItem(
                    "csv_output_path", str(paths.csv_output_path), "context.paths", "file", True, "ready"
                ),
                "excel_output_path": ContextTraceItem(
                    "excel_output_path", str(paths.excel_output_path), "context.paths", "file", True, "ready"
                ),
                "summary_path": ContextTraceItem(
                    "summary_path", str(paths.summary_path), "context.paths", "file", True, "ready"
                ),
                "parameters": ContextTraceItem(
                    "parameters", self.effective_parameters, "context.parameters", 
                    "dict", isinstance(self.effective_parameters, dict), "ready"
                ),
            }
            
            debug_print("Bootstrap Phase P3c: Postload trace built")
            
        except Exception as exc:
            # Non-fatal: log warning but don't raise
            debug_print(f"Bootstrap Warning: Failed to build postload trace: {exc}")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "BootstrapManager",
    "BootstrapError",
    "BootstrapPhaseStatus",
]
