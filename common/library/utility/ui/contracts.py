"""
L14 — UIRequest, UIResponse, UIContractManager

Standardized UI contract dataclasses and manager.
Projects subclass UIContractManager and implement _execute_pipeline().

Source: dcc/workflow/core_engine/ui/ui_contract.py  (reference impl)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class UIRequest:
    """
    Standardized UI request format for pipeline execution.

    Expected JSON shape
    -------------------
    {
        "path_selection": {
            "base_path": "/path/to/project",
            "upload_file_name": "data.xlsx",
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
    def from_json(cls, json_str: str) -> "UIRequest":
        data = json.loads(json_str)
        ps = data.get("path_selection", data)
        params = data.get("parameters", {})
        return cls(
            base_path=ps["base_path"],
            upload_file_name=ps["upload_file_name"],
            output_folder=ps.get("output_folder", "output"),
            schema_file_name=ps.get("schema_file_name"),
            debug_mode=params.get("debug_mode", False),
            nrows=params.get("nrows"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_selection": {
                "base_path": self.base_path,
                "upload_file_name": self.upload_file_name,
                "output_folder": self.output_folder,
                "schema_file_name": self.schema_file_name,
            },
            "parameters": {
                "debug_mode": self.debug_mode,
                "nrows": self.nrows,
            },
        }


@dataclass
class UIResponse:
    """
    Standardized UI response format.

    JSON shape
    ----------
    {
        "success": true,
        "message": "Pipeline completed successfully",
        "execution_time_seconds": 45.3,
        "rows_processed": 11099,
        "output_files": {"csv": "...", "excel": "...", "summary": "..."},
        "telemetry": {"heartbeats": 5, "peak_memory_mb": 145.2},
        "validation": {"errors": 3581, "critical": 0},
        "errors": []
    }
    """
    success: bool
    message: str
    execution_time_seconds: float = 0.0
    rows_processed: int = 0
    output_files: Dict[str, str] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({
            "success": self.success,
            "message": self.message,
            "execution_time_seconds": self.execution_time_seconds,
            "rows_processed": self.rows_processed,
            "output_files": self.output_files,
            "telemetry": self.telemetry,
            "validation": self.validation,
            "errors": self.errors,
        }, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return json.loads(self.to_json())


class UIContractManager:
    """
    Base manager for UI-pipeline contract operations.

    Projects subclass this and implement _execute_pipeline() with their
    own pipeline runner. The validate→run flow is provided here.

    Usage
    -----
    class MyUIManager(UIContractManager):
        def _execute_pipeline(self, request: UIRequest) -> Dict[str, Any]:
            return run_my_pipeline(request.base_path, request.upload_file_name)
    """

    def validate_selection(
        self,
        base_path: str,
        upload_file_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate a user selection before running the pipeline.
        Override to add project-specific validation logic.
        """
        errors = []
        if not base_path:
            errors.append("base_path is required")
        elif not Path(base_path).exists():
            errors.append(f"base_path does not exist: {base_path}")
        if not upload_file_name:
            errors.append("upload_file_name is required")
        else:
            full_path = Path(base_path) / upload_file_name if base_path else Path(upload_file_name)
            if not full_path.exists():
                errors.append(f"upload file not found: {full_path}")
        return {"valid": len(errors) == 0, "errors": errors}

    def run_pipeline(
        self,
        base_path: str,
        upload_file_name: str,
        output_folder: str = "output",
        schema_file_name: Optional[str] = None,
        debug_mode: bool = False,
        nrows: Optional[int] = None,
    ) -> UIResponse:
        """Run the pipeline from explicit parameters."""
        import time
        start = time.time()
        request = UIRequest(
            base_path=base_path,
            upload_file_name=upload_file_name,
            output_folder=output_folder,
            schema_file_name=schema_file_name,
            debug_mode=debug_mode,
            nrows=nrows,
        )
        validation = self.validate_selection(base_path, upload_file_name)
        if not validation["valid"]:
            return UIResponse(
                success=False,
                message="Validation failed",
                errors=validation["errors"],
                execution_time_seconds=round(time.time() - start, 2),
            )
        try:
            result = self._execute_pipeline(request)
            return UIResponse(
                success=True,
                message="Pipeline completed successfully",
                execution_time_seconds=round(time.time() - start, 2),
                rows_processed=result.get("rows_processed", 0),
                output_files=result.get("output_files", {}),
                telemetry=result.get("telemetry", {}),
                validation=result.get("validation", {}),
            )
        except Exception as exc:
            return UIResponse(
                success=False,
                message=f"Pipeline failed: {exc}",
                errors=[str(exc)],
                execution_time_seconds=round(time.time() - start, 2),
            )

    def run_from_ui_request(self, json_request: str) -> UIResponse:
        """Parse a JSON request string and run the pipeline."""
        try:
            request = UIRequest.from_json(json_request)
        except Exception as exc:
            return UIResponse(success=False, message=f"Failed to parse request: {exc}", errors=[str(exc)])
        return self.run_pipeline(
            base_path=request.base_path,
            upload_file_name=request.upload_file_name,
            output_folder=request.output_folder,
            schema_file_name=request.schema_file_name,
            debug_mode=request.debug_mode,
            nrows=request.nrows,
        )

    def _execute_pipeline(self, request: UIRequest) -> Dict[str, Any]:
        """
        Override in subclass to run the actual pipeline.
        Must return a dict with keys: rows_processed, output_files, telemetry, validation.
        """
        raise NotImplementedError("Subclass must implement _execute_pipeline()")
