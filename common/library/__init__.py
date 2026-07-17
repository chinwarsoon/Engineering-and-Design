"""
common.library — Universal shared libraries for all pipeline projects.

Architecture-aligned sub-packages
--------------------------------
config/     Runtime behavior parameter normalization and lookup (L15)
cli/        Universal schema-driven pipeline CLI parser (L18)
bootstrap/  Universal BootstrapManager orchestrator (L19)
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

from . import bootstrap, cli, config, errors, factories, logging, messages, paths, pipeline, telemetry, ui, validation

# L20 — core.system is a sub-package under core/, accessed via common.library.core.system
# (not imported at this level to avoid circular dependencies)

__all__ = [
    "bootstrap",
    "cli",
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
