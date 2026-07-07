"""
common.library.utility.factories — Factory ABC and config-driven DI pattern.

Exports
-------
Factory     L09  Abstract base with create(**kwargs) and _get_config(key)

Sources
-------
dcc: processor_engine/core/proc_factories.py, core/registry.py
eks: engine/core/factories.py  (Factory ABC — reference impl)
"""

from common.library.utility.factories.base_factory import Factory

__all__ = ["Factory"]
