"""
Initiation Engine - UI Override Contracts (Phase 4)

This module defines the backend contracts for user input/output selection
and parameter overrides as specified in R20 (Path Pickers) and R21 (Parameter Overrides).

Precedence Rules:
    CLI Arguments > UI Overrides > Schema Configuration > Hardcoded Defaults

Example Usage:
    # From UI/API
    path_contract = PathSelectionContract(
        base_path="/home/user/dcc-projects",
        upload_file_name="project_a.xlsx",
        output_folder="processed_a"
    )
    
    param_contract = ParameterOverrideContract(
        debug_mode=True,
        nrows=500
    )
    
    # Apply to pipeline
    paths = path_contract.to_paths()
    param_contract.apply_to_context(context)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
import json


@dataclass
class PathSelectionContract:
    """
    Backend contract for user path selection (R20 - Path Pickers).
    
    Captures user's selection of:
    - Base directory (where data/ and output/ folders exist)
    - Input Excel file name
    - Optional output folder customization
    
    Attributes:
        base_path: Root directory containing data/ and output/ subfolders
        upload_file_name: Name of the Excel file to process
        output_folder: Optional custom output subfolder name (default: "output")
        
    Example:
        >>> contract = PathSelectionContract(
        ...     base_path="/home/user/dcc",
        ...     upload_file_name="Submittal Tracker.xlsx"
        ... )
        >>> paths = contract.to_paths()
        >>> paths.excel_path
        Path('/home/user/dcc/data/Submittal Tracker.xlsx')
    """
    base_path: Path
    upload_file_name: str
    output_folder: str = "output"
    schema_file_name: Optional[str] = None  # Optional: custom schema file
    
    def __post_init__(self):
        """Normalize paths and file names."""
        if isinstance(self.base_path, str):
            self.base_path = Path(self.base_path)
        # Ensure upload_file_name has .xlsx extension
        if not self.upload_file_name.endswith(('.xlsx', '.xls')):
            self.upload_file_name += '.xlsx'
    
    def to_paths(self) -> 'PipelinePaths':
        """
        Convert contract selections to full PipelinePaths.
        
        Returns:
            PipelinePaths with absolute paths resolved
            
        Raises:
            ValueError: If required paths cannot be constructed
        """
        from core_engine.context import PipelinePaths
        
        base = self.base_path.resolve()
        
        # Default schema if not specified
        schema_name = self.schema_file_name or "dcc_register_config.json"
        
        return PipelinePaths(
            base_path=base,
            schema_path=base / "config" / "schemas" / schema_name,
            excel_path=base / "data" / self.upload_file_name,
            csv_output_path=base / self.output_folder / "processed_dcc_universal.csv",
            excel_output_path=base / self.output_folder / "processed_dcc_universal.xlsx",
            summary_path=base / self.output_folder / "summary.json",
            debug_log_path=base / self.output_folder / "debug.json"
        )
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the path selection contract.
        
        Returns:
            Dict with validation results:
            {
                "valid": bool,
                "base_path_exists": bool,
                "file_exists": bool,
                "file_readable": bool,
                "errors": List[str]
            }
        """
        result = {
            "valid": False,
            "base_path_exists": False,
            "file_exists": False,
            "file_readable": False,
            "errors": []
        }
        
        # Check base path
        if not self.base_path.exists():
            result["errors"].append(f"Base path does not exist: {self.base_path}")
            return result
        result["base_path_exists"] = True
        
        # Check data folder exists
        data_folder = self.base_path / "data"
        if not data_folder.exists():
            result["errors"].append(f"Data folder not found: {data_folder}")
            return result
        
        # Check file exists
        excel_path = data_folder / self.upload_file_name
        if not excel_path.exists():
            result["errors"].append(f"File not found: {excel_path}")
            return result
        result["file_exists"] = True
        
        # Check file readable
        try:
            with open(excel_path, 'rb') as f:
                f.read(1)  # Try reading first byte
            result["file_readable"] = True
        except Exception as e:
            result["errors"].append(f"File not readable: {e}")
            return result
        
        result["valid"] = True
        return result
    
    def to_dict(self) -> Dict[str, str]:
        """Serialize contract to dictionary."""
        return {
            "base_path": str(self.base_path),
            "upload_file_name": self.upload_file_name,
            "output_folder": self.output_folder,
            "schema_file_name": self.schema_file_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PathSelectionContract':
        """Create contract from dictionary."""
        return cls(
            base_path=Path(data["base_path"]),
            upload_file_name=data["upload_file_name"],
            output_folder=data.get("output_folder", "output"),
            schema_file_name=data.get("schema_file_name")
        )


@dataclass
class ParameterOverrideContract:
    """
    Backend contract for user parameter overrides (R21 - Parameter Overrides).
    
    Captures user's runtime configuration:
    - Debug mode for verbose logging
    - Row limit for testing/prototyping
    
    Attributes:
        debug_mode: Enable verbose logging and debug output
        nrows: Limit number of rows to process (None = all rows)
        
    Example:
        >>> contract = ParameterOverrideContract(debug_mode=True, nrows=100)
        >>> contract.apply_to_context(context)
    """
    debug_mode: bool = False
    nrows: Optional[int] = None
    
    def __post_init__(self):
        """Validate parameter values."""
        if self.nrows is not None:
            if not isinstance(self.nrows, int) or self.nrows < 1:
                error_msg = f"nrows must be a positive integer, got {self.nrows}"
                # Store validation error for potential context recording
                self._validation_error = {
                    "code": "S-P-S-0101",
                    "message": error_msg,
                    "details": f"Invalid nrows value: {self.nrows} (type: {type(self.nrows).__name__})",
                    "engine": "initiation_engine",
                    "phase": "parameter_validation",
                    "severity": "critical",
                    "fatal": True
                }
                raise ValueError(error_msg)
    
    def apply_to_context(self, context: 'PipelineContext') -> None:
        """
        Apply override parameters to pipeline context.
        
        Args:
            context: PipelineContext to modify
            
        Note:
            This modifies the context in-place.
        """
        # Record any validation errors that occurred during __post_init__
        if hasattr(self, '_validation_error') and hasattr(context, 'add_system_error'):
            context.add_system_error(**self._validation_error)
        
        if self.debug_mode is not None:
            context.debug_mode = self.debug_mode
        if self.nrows is not None:
            context.nrows = self.nrows
            context.parameters["nrows"] = self.nrows
            context.parameters["verbose"] = True
        
        # Apply row limit
        if self.nrows is not None:
            context.nrows = self.nrows
            context.parameters["nrows"] = self.nrows
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the parameter override contract.
        
        Returns:
            Dict with validation results
        """
        result = {
            "valid": True,
            "warnings": []
        }
        
        # Warn if debug mode is enabled in production
        if self.debug_mode:
            result["warnings"].append("Debug mode enabled - verbose logging active")
        
        # Warn if row limit is very small
        if self.nrows is not None and self.nrows < 10:
            result["warnings"].append(f"Very small row limit ({self.nrows}) - may affect processing")
        
        # Warn if row limit is very large
        if self.nrows is not None and self.nrows > 100000:
            result["warnings"].append(f"Large row limit ({self.nrows}) - may impact performance")
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract to dictionary."""
        return {
            "debug_mode": self.debug_mode,
            "nrows": self.nrows
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParameterOverrideContract':
        """Create contract from dictionary."""
        return cls(
            debug_mode=data.get("debug_mode", False),
            nrows=data.get("nrows")
        )


@dataclass
class UIContractBundle:
    """
    Combined UI contract for complete pipeline configuration.
    
    Encapsulates both path selection and parameter overrides for
    a single pipeline run initiated from the UI.
    
    Attributes:
        path_selection: PathSelectionContract for input/output paths
        parameters: ParameterOverrideContract for runtime configuration
        
    Example:
        >>> bundle = UIContractBundle(
        ...     path_selection=PathSelectionContract(
        ...         base_path="/home/user/dcc",
        ...         upload_file_name="project.xlsx"
        ...     ),
        ...     parameters=ParameterOverrideContract(
        ...         debug_mode=False,
        ...         nrows=1000
        ...     )
        ... )
    """
    path_selection: PathSelectionContract
    parameters: ParameterOverrideContract = field(
        default_factory=ParameterOverrideContract
    )
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the complete UI contract bundle.
        
        Returns:
            Combined validation results from path and parameter contracts
        """
        path_result = self.path_selection.validate()
        param_result = self.parameters.validate()
        
        return {
            "valid": path_result["valid"],
            "path_selection": path_result,
            "parameters": param_result,
            "all_warnings": param_result.get("warnings", [])
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete bundle to dictionary."""
        return {
            "path_selection": self.path_selection.to_dict(),
            "parameters": self.parameters.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UIContractBundle':
        """Create bundle from dictionary (e.g., from JSON API request)."""
        return cls(
            path_selection=PathSelectionContract.from_dict(data["path_selection"]),
            parameters=ParameterOverrideContract.from_dict(data.get("parameters", {}))
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UIContractBundle':
        """Create bundle from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_json(self) -> str:
        """Serialize bundle to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# Utility functions for UI integration

def get_available_files(base_path: Path, pattern: str = "*.xlsx") -> List[Dict[str, Any]]:
    """
    Get list of available Excel files in the data folder.
    
    Args:
        base_path: Base directory containing data/ subfolder
        pattern: File pattern to match (default: *.xlsx)
        
    Returns:
        List of file info dictionaries:
        [
            {
                "name": "file.xlsx",
                "size_mb": 2.4,
                "modified": "2026-04-28T10:30:00",
                "columns_preview": [...]  # First 5 column names
            }
        ]
    """
    data_folder = base_path / "data"
    
    if not data_folder.exists():
        return []
    
    files = []
    for file_path in data_folder.glob(pattern):
        stat = file_path.stat()
        files.append({
            "name": file_path.name,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": stat.st_mtime,  # Unix timestamp
            "path": str(file_path)
        })
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    return files


def suggest_base_paths() -> List[Dict[str, Any]]:
    """
    Suggest common base paths for the user.
    
    Returns:
        List of suggested paths with metadata
    """
    suggestions = []
    
    # Current working directory
    cwd = Path.cwd()
    if (cwd / "data").exists():
        suggestions.append({
            "path": str(cwd),
            "label": "Current Directory",
            "exists": True
        })
    
    # Home directory DCC folder
    home_dcc = Path.home() / "dcc"
    if home_dcc.exists():
        suggestions.append({
            "path": str(home_dcc),
            "label": "Home DCC Folder",
            "exists": True
        })
    
    # Common project locations
    common_paths = [
        Path("/home/franklin/dsai/Engineering-and-Design/dcc"),
        Path("/opt/dcc"),
        Path("/var/dcc"),
    ]
    
    for path in common_paths:
        if path.exists() and str(path) not in [s["path"] for s in suggestions]:
            suggestions.append({
                "path": str(path),
                "label": f"Project: {path.name}",
                "exists": True
            })
    
    return suggestions


def validate_and_resolve(
    path_contract: PathSelectionContract,
    param_contract: Optional[ParameterOverrideContract] = None
) -> Dict[str, Any]:
    """
    Complete validation and resolution for UI pipeline run.
    
    Args:
        path_contract: User's path selection
        param_contract: Optional parameter overrides
        
    Returns:
        Complete resolution result with PipelinePaths ready for execution
    """
    result = {
        "valid": False,
        "paths": None,
        "validation": {},
        "errors": [],
        "warnings": []
    }
    
    # Validate path selection
    path_validation = path_contract.validate()
    result["validation"]["paths"] = path_validation
    
    if not path_validation["valid"]:
        result["errors"].extend(path_validation["errors"])
        return result
    
    # Validate parameters
    if param_contract:
        param_validation = param_contract.validate()
        result["validation"]["parameters"] = param_validation
        result["warnings"].extend(param_validation.get("warnings", []))
    
    # Resolve to PipelinePaths
    try:
        result["paths"] = path_contract.to_paths()
        result["valid"] = True
    except Exception as e:
        result["errors"].append(f"Failed to resolve paths: {e}")
    
    return result


__all__ = [
    'PathSelectionContract',
    'ParameterOverrideContract',
    'UIContractBundle',
    'get_available_files',
    'suggest_base_paths',
    'validate_and_resolve',
]
