"""
Core Engine - UI Contract Module (Phase 4)

Consolidated backend contract definitions for UI integration.
This module provides the main interface between the frontend UI and
backend pipeline, handling path selection, parameter overrides, and
pipeline execution requests.

Usage:
    from core_engine.ui_contract import UIContractManager
    
    # Initialize manager
    manager = UIContractManager()
    
    # Get available files for a base path
    files = manager.get_available_files("/home/user/dcc")
    
    # Validate and run pipeline from UI request
    result = manager.run_from_ui_request(ui_request_json)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from initiation_engine.overrides import (
    PathSelectionContract,
    ParameterOverrideContract,
    UIContractBundle,
    get_available_files,
    suggest_base_paths,
    validate_and_resolve,
)
from core_engine.context import PipelineContext, PipelinePaths
from core_engine.telemetry_heartbeat import TelemetryHeartbeat


@dataclass
class UIRequest:
    """
    Standardized UI request format for pipeline execution.
    
    This is the expected format for JSON API requests from the UI.
    
    Example JSON request:
    {
        "path_selection": {
            "base_path": "/home/user/dcc",
            "upload_file_name": "project_a.xlsx",
            "output_folder": "output"
        },
        "parameters": {
            "debug_mode": false,
            "nrows": 1000
        }
    }
    """
    base_path: str
    upload_file_name: str
    output_folder: str = "output"
    schema_file_name: Optional[str] = None
    debug_mode: bool = False
    nrows: Optional[int] = None
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UIRequest':
        """Parse JSON string to UIRequest."""
        data = json.loads(json_str)
        return cls(
            base_path=data["path_selection"]["base_path"],
            upload_file_name=data["path_selection"]["upload_file_name"],
            output_folder=data["path_selection"].get("output_folder", "output"),
            schema_file_name=data["path_selection"].get("schema_file_name"),
            debug_mode=data.get("parameters", {}).get("debug_mode", False),
            nrows=data.get("parameters", {}).get("nrows")
        )
    
    def to_contract_bundle(self) -> UIContractBundle:
        """Convert UIRequest to UIContractBundle."""
        path_contract = PathSelectionContract(
            base_path=Path(self.base_path),
            upload_file_name=self.upload_file_name,
            output_folder=self.output_folder,
            schema_file_name=self.schema_file_name
        )
        
        param_contract = ParameterOverrideContract(
            debug_mode=self.debug_mode,
            nrows=self.nrows
        )
        
        return UIContractBundle(
            path_selection=path_contract,
            parameters=param_contract
        )


@dataclass
class UIResponse:
    """
    Standardized UI response format.
    
    Returns pipeline execution results and metadata to the UI.
    
    Example JSON response:
    {
        "success": true,
        "message": "Pipeline completed successfully",
        "execution_time_seconds": 45.3,
        "rows_processed": 11099,
        "output_files": {
            "csv": "/home/user/dcc/output/processed_dcc_universal.csv",
            "excel": "/home/user/dcc/output/processed_dcc_universal.xlsx",
            "summary": "/home/user/dcc/output/summary.json"
        },
        "telemetry": {
            "heartbeats": 5,
            "peak_memory_mb": 145.2
        },
        "validation": {
            "errors": 3581,
            "critical": 0,
            "high": 2074
        }
    }
    """
    success: bool
    message: str
    execution_time_seconds: float = 0.0
    rows_processed: int = 0
    output_files: Dict[str, str] = None
    telemetry: Dict[str, Any] = None
    validation: Dict[str, int] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = {}
        if self.telemetry is None:
            self.telemetry = {}
        if self.validation is None:
            self.validation = {}
        if self.errors is None:
            self.errors = []
    
    def to_json(self) -> str:
        """Serialize response to JSON string."""
        return json.dumps({
            "success": self.success,
            "message": self.message,
            "execution_time_seconds": self.execution_time_seconds,
            "rows_processed": self.rows_processed,
            "output_files": self.output_files,
            "telemetry": self.telemetry,
            "validation": self.validation,
            "errors": self.errors
        }, indent=2)


class UIContractManager:
    """
    Central manager for UI-Pipeline contract operations.
    
    This class provides a unified interface for:
    - File browsing and selection
    - Path validation
    - Pipeline execution from UI requests
    - Response formatting
    
    Example:
        >>> manager = UIContractManager()
        >>> 
        >>> # Browse available files
        >>> files = manager.get_available_files("/home/user/dcc")
        >>> 
        >>> # Validate selection
        >>> result = manager.validate_selection(
        ...     base_path="/home/user/dcc",
        ...     upload_file_name="project.xlsx"
        ... )
        >>> 
        >>> # Run pipeline
        >>> response = manager.run_pipeline(
        ...     base_path="/home/user/dcc",
        ...     upload_file_name="project.xlsx",
        ...     nrows=1000
        ... )
    """
    
    def __init__(self):
        """Initialize the UI contract manager."""
        self._run_pipeline_fn: Optional[Callable] = None
    
    def set_pipeline_runner(self, runner: Callable) -> None:
        """
        Set the pipeline execution function.
        
        Args:
            runner: Function that accepts PipelinePaths and PipelineContext
                   and returns a result dictionary
        """
        self._run_pipeline_fn = runner
    
    def get_available_files(self, base_path: str) -> List[Dict[str, Any]]:
        """
        Get list of available Excel files for UI dropdown.
        
        Args:
            base_path: Base directory path as string
            
        Returns:
            List of file information dictionaries
        """
        return get_available_files(Path(base_path))
    
    def get_suggested_paths(self) -> List[Dict[str, Any]]:
        """
        Get list of suggested base paths for UI.
        
        Returns:
            List of suggested path dictionaries with labels
        """
        return suggest_base_paths()
    
    def validate_selection(
        self,
        base_path: str,
        upload_file_name: str,
        debug_mode: bool = False,
        nrows: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate user's selection before running pipeline.
        
        Args:
            base_path: Selected base directory
            upload_file_name: Selected Excel file
            debug_mode: Debug mode flag
            nrows: Optional row limit
            
        Returns:
            Validation result dictionary
        """
        path_contract = PathSelectionContract(
            base_path=Path(base_path),
            upload_file_name=upload_file_name
        )
        
        param_contract = ParameterOverrideContract(
            debug_mode=debug_mode,
            nrows=nrows
        )
        
        bundle = UIContractBundle(
            path_selection=path_contract,
            parameters=param_contract
        )
        
        return bundle.validate()
    
    def run_pipeline(
        self,
        base_path: str,
        upload_file_name: str,
        output_folder: str = "output",
        schema_file_name: Optional[str] = None,
        debug_mode: bool = False,
        nrows: Optional[int] = None
    ) -> UIResponse:
        """
        Run pipeline with user-selected parameters.
        
        This is the main entry point for UI-triggered pipeline execution.
        
        Args:
            base_path: Base directory containing data/ folder
            upload_file_name: Excel file to process
            output_folder: Output subfolder name
            schema_file_name: Optional custom schema file
            debug_mode: Enable debug logging
            nrows: Optional row limit for testing
            
        Returns:
            UIResponse with execution results
        """
        import time
        
        start_time = time.time()
        
        try:
            # Create contract bundle
            path_contract = PathSelectionContract(
                base_path=Path(base_path),
                upload_file_name=upload_file_name,
                output_folder=output_folder,
                schema_file_name=schema_file_name
            )
            
            param_contract = ParameterOverrideContract(
                debug_mode=debug_mode,
                nrows=nrows
            )
            
            # Validate before running
            validation = validate_and_resolve(path_contract, param_contract)
            
            if not validation["valid"]:
                return UIResponse(
                    success=False,
                    message="Validation failed",
                    errors=validation["errors"],
                    execution_time_seconds=time.time() - start_time
                )
            
            # Resolve paths
            paths = validation["paths"]
            
            # Create context with overrides
            context = PipelineContext(
                paths=paths,
                parameters={},
                nrows=nrows or 0,
                debug_mode=debug_mode
            )
            
            # Apply parameter overrides
            param_contract.apply_to_context(context)
            
            # Run pipeline if runner is set
            if self._run_pipeline_fn:
                result = self._run_pipeline_fn(context)
            else:
                # Default: import and run dcc_engine_pipeline
                from dcc_engine_pipeline import run_engine_pipeline
                result = run_engine_pipeline(
                    base_path=Path(base_path),
                    upload_file_name=upload_file_name,
                    output_folder=output_folder,
                    debug_mode=debug_mode,
                    nrows=nrows
                )
            
            # Build response
            execution_time = time.time() - start_time
            
            return UIResponse(
                success=True,
                message="Pipeline completed successfully",
                execution_time_seconds=round(execution_time, 2),
                rows_processed=result.get("rows_processed", 0),
                output_files={
                    "csv": str(paths.csv_output_path),
                    "excel": str(paths.excel_output_path),
                    "summary": str(paths.summary_path)
                },
                telemetry={
                    "heartbeats": len(context.telemetry.heartbeat_logs),
                    "peak_memory_mb": max(
                        (hb.get("memory_usage_mb", 0) for hb in context.telemetry.heartbeat_logs),
                        default=0
                    )
                },
                validation=result.get("validation", {})
            )
            
        except Exception as e:
            return UIResponse(
                success=False,
                message=f"Pipeline failed: {str(e)}",
                errors=[str(e)],
                execution_time_seconds=time.time() - start_time
            )
    
    def run_from_ui_request(self, json_request: str) -> UIResponse:
        """
        Convenience method to run pipeline from a JSON API request.
        
        Args:
            json_request: JSON string containing UIRequest data
            
        Returns:
            UIResponse with execution results
        """
        try:
            request = UIRequest.from_json(json_request)
            bundle = request.to_contract_bundle()
            
            return self.run_pipeline(
                base_path=str(request.base_path),
                upload_file_name=request.upload_file_name,
                output_folder=request.output_folder,
                schema_file_name=request.schema_file_name,
                debug_mode=request.debug_mode,
                nrows=request.nrows
            )
        except Exception as e:
            return UIResponse(
                success=False,
                message=f"Failed to parse request: {str(e)}",
                errors=[str(e)]
            )


def create_api_response(
    success: bool,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standardized API response.
    
    Args:
        success: Whether the operation succeeded
        data: Response data payload
        error: Error message if failed
        **kwargs: Additional fields to include
        
    Returns:
        Standardized API response dictionary
    """
    response = {
        "success": success,
        "timestamp": None  # Would add actual timestamp here
    }
    
    if data:
        response["data"] = data
    
    if error:
        response["error"] = error
    
    response.update(kwargs)
    
    return response


# Predefined API endpoints (for reference/documentation)

API_ENDPOINTS = {
    "GET /api/v1/paths/suggestions": {
        "description": "Get suggested base paths",
        "response": List[Dict[str, Any]]  # suggest_base_paths()
    },
    "GET /api/v1/files": {
        "description": "List available Excel files in base_path",
        "params": {"base_path": str},
        "response": List[Dict[str, Any]]  # get_available_files()
    },
    "POST /api/v1/pipeline/validate": {
        "description": "Validate user selection without running",
        "body": UIRequest,
        "response": Dict[str, Any]  # bundle.validate()
    },
    "POST /api/v1/pipeline/run": {
        "description": "Run pipeline with user selection",
        "body": UIRequest,
        "response": UIResponse
    }
}


__all__ = [
    'UIRequest',
    'UIResponse',
    'UIContractManager',
    'create_api_response',
    'API_ENDPOINTS',
]
