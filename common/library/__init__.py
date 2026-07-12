"""
common.library — Universal shared libraries for all pipeline projects.

Architecture-aligned sub-packages
--------------------------------
config/     Runtime behavior parameter normalization and lookup (L15)
logging/    Shared logger and tracing utilities
telemetry/  Shared telemetry and heartbeat support
pipeline/   Shared pipeline context and engine contracts
errors/     Shared error management helpers
messages/   Shared message catalog helpers
paths/      Shared path helpers and OS detection
validation/ Shared validation framework
ui/         Shared UI contracts
factories/  Shared factory abstractions

Legacy compatibility modules remain available under core/ and utility/.
"""

from . import config, errors, factories, logging, messages, paths, pipeline, telemetry, ui, validation

__all__ = [
    "config",
    "errors",
    "factories",
    "logging",
    "messages",
    "paths",
    "pipeline",
    "telemetry",
    "ui",
    "validation",
]
