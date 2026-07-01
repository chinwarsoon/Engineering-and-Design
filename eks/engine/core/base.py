"""
BaseEngine - Abstract base class for all EKS engines.

This module implements the BaseEngine pattern per Appendix F Section 2.3.1,
providing a standard execution flow (validate → execute → validate) for all
pipeline engines.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ErrorRecord:
    """Error record for engine execution."""
    error_type: str
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


@dataclass
class ValidationResult:
    """Validation result for input/output."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_error(self) -> ErrorRecord:
        """Convert validation failure to error record."""
        return ErrorRecord(
            error_type="ValidationError",
            error_message="; ".join(self.errors),
            context={"warnings": self.warnings}
        )


@dataclass
class EngineInput:
    """
    Standard input contract for all EKS engines.
    
    This class implements the EngineInput contract per Appendix F Section 2.3.1.
    """
    run_id: str
    data_dir: Path
    config_file: Path
    schema_dir: Path
    output_dir: Path
    parameters: Dict[str, Any] = field(default_factory=dict)
    checkpoint_state: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "data_dir": str(self.data_dir),
            "config_file": str(self.config_file),
            "schema_dir": str(self.schema_dir),
            "output_dir": str(self.output_dir),
            "parameters": self.parameters,
            "checkpoint_state": self.checkpoint_state
        }


@dataclass
class EngineOutput:
    """
    Standard output contract for all EKS engines.
    
    This class implements the EngineOutput contract per Appendix F Section 2.3.1.
    """
    run_id: str
    status: str  # SUCCESS, PARTIAL, FAILED
    output_files: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[ErrorRecord] = field(default_factory=list)
    checkpoint_state: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "status": self.status,
            "output_files": [str(f) for f in self.output_files],
            "metadata": self.metadata,
            "errors": [e.to_dict() for e in self.errors],
            "checkpoint_state": self.checkpoint_state,
            "telemetry": self.telemetry
        }


class BaseEngine(ABC):
    """
    Abstract base class for all EKS engines.
    
    This class implements the BaseEngine pattern per Appendix F Section 2.3.1,
    providing a standard execution flow (validate → execute → validate) for all
    pipeline engines.
    
    Subclasses must implement:
    - validate_input: Validate input before processing
    - execute: Execute the engine logic
    - validate_output: Validate output before returning
    """
    
    def __init__(self, name: str):
        """
        Initialize the engine.
        
        Args:
            name: Engine name for logging and telemetry
        """
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    @abstractmethod
    def validate_input(self, input_data: EngineInput) -> ValidationResult:
        """
        Validate input before processing.
        
        Args:
            input_data: Engine input data
            
        Returns:
            ValidationResult with is_valid flag and any errors/warnings
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: EngineInput) -> EngineOutput:
        """
        Execute the engine logic.
        
        Args:
            input_data: Engine input data
            
        Returns:
            EngineOutput with results, status, and metadata
        """
        pass
    
    @abstractmethod
    def validate_output(self, output: EngineOutput) -> ValidationResult:
        """
        Validate output before returning.
        
        Args:
            output: Engine output data
            
        Returns:
            ValidationResult with is_valid flag and any errors/warnings
        """
        pass
    
    def run(self, input_data: EngineInput) -> EngineOutput:
        """
        Standard execution flow.
        
        This method implements the standard execution flow per Appendix F:
        1. Validate input
        2. Execute
        3. Validate output
        
        Args:
            input_data: Engine input data
            
        Returns:
            EngineOutput with results, status, and metadata
        """
        self.start_time = datetime.now()
        
        # 1. Validate input
        input_validation = self.validate_input(input_data)
        if not input_validation.is_valid:
            self.end_time = datetime.now()
            return EngineOutput(
                run_id=input_data.run_id,
                status="FAILED",
                output_files=[],
                metadata={
                    "engine": self.name,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "duration_seconds": (self.end_time - self.start_time).total_seconds()
                },
                errors=[input_validation.to_error()],
                checkpoint_state={},
                telemetry={}
            )
        
        # 2. Execute
        output = self.execute(input_data)
        
        # 3. Validate output
        output_validation = self.validate_output(output)
        if not output_validation.is_valid:
            output.status = "FAILED"
            output.errors.append(output_validation.to_error())
        
        # Add metadata
        self.end_time = datetime.now()
        output.metadata.update({
            "engine": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds()
        })
        
        return output


class BaseProcessor(ABC):
    """
    Abstract base class for processors within engines.
    
    This class provides a common interface for processors that perform
    specific tasks within an engine (e.g., parsing, scoring, detection).
    """
    
    def __init__(self, name: str):
        """
        Initialize the processor.
        
        Args:
            name: Processor name for logging and telemetry
        """
        self.name = name
    
    @abstractmethod
    def process(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process the input data.
        
        Args:
            data: Input data to process
            context: Optional context information
            
        Returns:
            Processed output data
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """
        Validate input data.
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult with is_valid flag and any errors/warnings
        """
        pass
