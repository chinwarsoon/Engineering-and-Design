"""
common.library.core.errors — BaseErrorManager and catalog loader.

Exports
-------
BaseErrorManager    L10  Abstract base: catalog loading, severity lookup,
                         system/data error handling, fail-fast, error summary

Sources
-------
dcc: core_engine/errors/error_manager.py  (functional helpers wrapping PipelineContext)
eks: engine/core/error_manager.py         (ErrorManager class — reference impl)
"""

from common.library.core.errors.error_manager import BaseErrorManager

__all__ = ["BaseErrorManager"]
