"""Architecture-aligned pipeline package for shared pipeline libraries."""

from common.library.core.pipeline.context import BasePipelineContext
from common.library.core.pipeline.base_engine import BaseEngine, BaseProcessor, EngineInput, EngineOutput, ErrorRecord, ValidationResult

# T1.99.149 (I187): Registration gate protocol
from .registration_gate import RegistrationGate

__all__ = [
    "BasePipelineContext",
    "BaseEngine",
    "BaseProcessor",
    "EngineInput",
    "EngineOutput",
    "ErrorRecord",
    "ValidationResult",
    "RegistrationGate",
]
