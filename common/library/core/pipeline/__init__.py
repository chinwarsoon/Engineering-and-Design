"""
common.library.core.pipeline — Pipeline base classes and contracts.

Exports
-------
TelemetryHeartbeat          L05  Heartbeat with tick() and add_checkpoint()
DocumentProcessingHeartbeat L05  Subclass for document-oriented pipelines
BasePipelineContext         L06  Abstract base for all pipeline context dataclasses
BaseEngine                  L07  Abstract base with validate→execute→validate flow
BaseProcessor               L07  Abstract base for sub-engine processors
EngineInput                 L08  Standard input contract for all engines
EngineOutput                L08  Standard output contract for all engines
ValidationResult            L08  Input/output validation result
ErrorRecord                 L08  Structured error record

Sources
-------
L05  dcc: core_engine/logging/log_telemetry.py
     eks: engine/core/telemetry.py
L06  dcc: core_engine/context/context_pipeline.py
     eks: engine/core/context.py
L07  dcc: core_engine/base/base_engine.py, base_processor.py
     eks: engine/core/base.py
L08  eks: engine/core/base.py, engine/core/io_contracts.py  (reference impl)
"""

from common.library.core.pipeline.heartbeat import TelemetryHeartbeat, DocumentProcessingHeartbeat
from common.library.core.pipeline.context import BasePipelineContext
from common.library.core.pipeline.base_engine import (
    BaseEngine,
    BaseProcessor,
    EngineInput,
    EngineOutput,
    ValidationResult,
    ErrorRecord,
)

__all__ = [
    "TelemetryHeartbeat",
    "DocumentProcessingHeartbeat",
    "BasePipelineContext",
    "BaseEngine",
    "BaseProcessor",
    "EngineInput",
    "EngineOutput",
    "ValidationResult",
    "ErrorRecord",
]
