"""
L07 + L08 — BaseEngine, BaseProcessor, EngineInput, EngineOutput,
             ValidationResult, ErrorRecord

Merges DCC BaseEngine/BaseProcessor with EKS BaseEngine and the EKS
EngineInput/EngineOutput contract dataclasses (Pattern §3.15).

Sources
-------
L07  dcc: core_engine/base/base_engine.py, base_processor.py
     eks: engine/core/base.py (BaseEngine, BaseProcessor)
L08  eks: engine/core/base.py + engine/core/io_contracts.py (reference impl)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar


# ---------------------------------------------------------------------------
# L08 — ErrorRecord / ValidationResult / EngineInput / EngineOutput
# ---------------------------------------------------------------------------

@dataclass
class ErrorRecord:
    """Structured error record for engine execution."""
    error_type: str
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


@dataclass
class ValidationResult:
    """Result of input or output validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_error(self) -> ErrorRecord:
        return ErrorRecord(
            error_type="ValidationError",
            error_message="; ".join(self.errors),
            context={"warnings": self.warnings},
        )


@dataclass
class EngineInput:
    """Standard input contract for all pipeline engines (Pattern §3.15)."""
    run_id: str
    data_dir: Path
    config_file: Path
    schema_dir: Path
    output_dir: Path
    parameters: Dict[str, Any] = field(default_factory=dict)
    checkpoint_state: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "data_dir": str(self.data_dir),
            "config_file": str(self.config_file),
            "schema_dir": str(self.schema_dir),
            "output_dir": str(self.output_dir),
            "parameters": self.parameters,
            "checkpoint_state": self.checkpoint_state,
        }


@dataclass
class EngineOutput:
    """Standard output contract for all pipeline engines (Pattern §3.15)."""
    run_id: str
    status: str  # SUCCESS | PARTIAL | FAILED
    output_files: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[ErrorRecord] = field(default_factory=list)
    checkpoint_state: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "output_files": [str(f) for f in self.output_files],
            "metadata": self.metadata,
            "errors": [e.to_dict() for e in self.errors],
            "checkpoint_state": self.checkpoint_state,
            "telemetry": self.telemetry,
        }


# ---------------------------------------------------------------------------
# Generic type vars
# ---------------------------------------------------------------------------

I = TypeVar("I", bound=EngineInput)
O = TypeVar("O", bound=EngineOutput)


# ---------------------------------------------------------------------------
# L07 — BaseEngine
# ---------------------------------------------------------------------------

class BaseEngine(ABC, Generic[I, O]):
    """
    Abstract base class for all pipeline engines.

    Execution flow: validate_input → execute → validate_output  (Pattern §3.15)

    Subclasses must implement validate_input, execute, validate_output.
    """

    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @abstractmethod
    def validate_input(self, input_data: I) -> ValidationResult:
        """Validate engine input before processing."""

    @abstractmethod
    def execute(self, input_data: I) -> O:
        """Execute the engine's core logic."""

    @abstractmethod
    def validate_output(self, output: O) -> ValidationResult:
        """Validate engine output before returning."""

    def run(self, input_data: I) -> O:
        """Standard execution flow: validate → execute → validate."""
        self.start_time = datetime.now()

        input_validation = self.validate_input(input_data)
        if not input_validation.is_valid:
            self.end_time = datetime.now()
            return EngineOutput(  # type: ignore[return-value]
                run_id=input_data.run_id,
                status="FAILED",
                metadata={
                    "engine": self.name,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "duration_seconds": (self.end_time - self.start_time).total_seconds(),
                },
                errors=[input_validation.to_error()],
            )

        output = self.execute(input_data)

        output_validation = self.validate_output(output)
        if not output_validation.is_valid:
            output.status = "FAILED"
            output.errors.append(output_validation.to_error())

        self.end_time = datetime.now()
        output.metadata.update({
            "engine": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
        })
        return output


# ---------------------------------------------------------------------------
# L07 — BaseProcessor
# ---------------------------------------------------------------------------

class BaseProcessor(ABC):
    """
    Abstract base class for processors within engines.

    Sources
    -------
    dcc: core_engine/base/base_processor.py
    eks: engine/core/base.py (BaseProcessor)
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process input data and return result."""

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate input data before processing."""
