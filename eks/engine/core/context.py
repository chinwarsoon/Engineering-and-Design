"""
EKSPipelineContext - Centralized state management for EKS pipeline.

This module implements the PipelineContext pattern per Appendix F Section 2.2,
providing a single source of truth for pipeline state, paths, data, parameters,
telemetry, and schema/config registries.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class EKSPaths:
    """Document paths, schema paths, output paths."""
    data_dir: Path
    schema_dir: Path
    output_dir: Path
    archive_dir: Path
    config_dir: Path
    log_dir: Path
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization (uses as_posix() for cross-platform)."""
        return {
            "data_dir": self.data_dir.as_posix(),
            "schema_dir": self.schema_dir.as_posix(),
            "output_dir": self.output_dir.as_posix(),
            "archive_dir": self.archive_dir.as_posix(),
            "config_dir": self.config_dir.as_posix(),
            "log_dir": self.log_dir.as_posix()
        }


@dataclass
class EKSData:
    """Document metadata, extracted content."""
    documents: Dict[str, Any] = field(default_factory=dict)
    extracted_content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "documents": self.documents,
            "extracted_content": self.extracted_content,
            "metadata": self.metadata
        }


@dataclass
class EKSState:
    """Processing status, document counts."""
    status: str = "INITIALIZED"
    documents_processed: int = 0
    documents_total: int = 0
    documents_succeeded: int = 0
    documents_failed: int = 0
    current_phase: str = "INIT"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status,
            "documents_processed": self.documents_processed,
            "documents_total": self.documents_total,
            "documents_succeeded": self.documents_succeeded,
            "documents_failed": self.documents_failed,
            "current_phase": self.current_phase,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


@dataclass
class EKSTelemetry:
    """Performance metrics, memory usage."""
    checkpoints: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    memory_usage: Dict[str, float] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    def add_checkpoint(self, phase: str, timestamp: datetime, details: Dict[str, Any]):
        """Add a telemetry checkpoint."""
        self.checkpoints[phase] = {
            "timestamp": timestamp.isoformat(),
            "details": details
        }
    
    def record_metric(self, name: str, value: float):
        """Record a performance metric."""
        self.performance_metrics[name] = value
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checkpoints": self.checkpoints,
            "performance_metrics": self.performance_metrics,
            "memory_usage": self.memory_usage,
            "error_counts": self.error_counts
        }


@dataclass
class EKSPipelineContext:
    """
    Centralized state management for EKS pipeline.
    
    This class implements the PipelineContext pattern per Appendix F Section 2.2,
    providing a single source of truth for pipeline state, paths, data, parameters,
    telemetry, and schema/config registries.
    
    Attributes:
        paths: Document paths, schema paths, output paths
        data: Document metadata, extracted content
        parameters: Parser options, health thresholds
        state: Processing status, document counts
        telemetry: Performance metrics, memory usage
        schema_registry: Loaded schema definitions
        config_registry: Global configuration SSOT
    """
    paths: EKSPaths
    data: EKSData = field(default_factory=EKSData)
    parameters: Dict[str, Any] = field(default_factory=dict)
    state: EKSState = field(default_factory=EKSState)
    telemetry: EKSTelemetry = field(default_factory=EKSTelemetry)
    schema_registry: Optional[Any] = None
    config_registry: Optional[Any] = None
    
    def __post_init__(self):
        """Initialize state with start time."""
        if self.state.start_time is None:
            self.state.start_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire context to dictionary for serialization."""
        return {
            "paths": self.paths.to_dict(),
            "data": self.data.to_dict(),
            "parameters": self.parameters,
            "state": self.state.to_dict(),
            "telemetry": self.telemetry.to_dict(),
            "schema_registry": str(self.schema_registry) if self.schema_registry else None,
            "config_registry": str(self.config_registry) if self.config_registry else None
        }
    
    def to_json(self) -> str:
        """Serialize context to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EKSPipelineContext':
        """Reconstruct context from dictionary."""
        paths = EKSPaths(
            data_dir=Path(data["paths"]["data_dir"]),
            schema_dir=Path(data["paths"]["schema_dir"]),
            output_dir=Path(data["paths"]["output_dir"]),
            archive_dir=Path(data["paths"]["archive_dir"]),
            config_dir=Path(data["paths"]["config_dir"]),
            log_dir=Path(data["paths"]["log_dir"])
        )
        
        state_data = data["state"]
        state = EKSState(
            status=state_data["status"],
            documents_processed=state_data["documents_processed"],
            documents_total=state_data["documents_total"],
            documents_succeeded=state_data["documents_succeeded"],
            documents_failed=state_data["documents_failed"],
            current_phase=state_data["current_phase"],
            start_time=datetime.fromisoformat(state_data["start_time"]) if state_data["start_time"] else None,
            end_time=datetime.fromisoformat(state_data["end_time"]) if state_data["end_time"] else None
        )
        
        context = cls(
            paths=paths,
            data=EKSData(**data["data"]),
            parameters=data["parameters"],
            state=state,
            telemetry=EKSTelemetry(**data["telemetry"])
        )
        
        return context
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EKSPipelineContext':
        """Reconstruct context from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_phase(self, phase: str, status: str = "IN_PROGRESS"):
        """Update current phase and status."""
        self.state.current_phase = phase
        self.state.status = status
        self.telemetry.add_checkpoint(
            phase=phase,
            timestamp=datetime.now(),
            details={"status": status}
        )
    
    def complete(self):
        """Mark pipeline as complete."""
        self.state.status = "COMPLETE"
        self.state.end_time = datetime.now()
        self.telemetry.add_checkpoint(
            phase="COMPLETE",
            timestamp=datetime.now(),
            details={"status": "COMPLETE"}
        )
    
    def fail(self, error_message: str):
        """Mark pipeline as failed."""
        self.state.status = "FAILED"
        self.state.end_time = datetime.now()
        self.telemetry.add_checkpoint(
            phase="FAILED",
            timestamp=datetime.now(),
            details={"error": error_message}
        )
    
    def save_checkpoint(self, checkpoint_path: Path):
        """
        Save checkpoint state to file.
        
        Args:
            checkpoint_path: Path to save checkpoint file
        """
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_checkpoint(cls, checkpoint_path: Path) -> 'EKSPipelineContext':
        """
        Load checkpoint state from file.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            EKSPipelineContext loaded from checkpoint
        """
        with open(checkpoint_path, 'r') as f:
            return cls.from_json(f.read())
