"""
L20 — Universal ``test_environment()``.

Project-agnostic environment/dependency checker extracted from DCC's
``dcc/workflow/core_engine/system/system_environment.py``.

Accepts a ``dependencies`` dict (``required``/``optional``/``engines``) and
runs ``importlib.import_module()`` on each — one at a time, logging failures
without aborting the loop. Returns a structured ``{ready, errors, ...}`` dict.

Stdlib-only — no external package dependencies — so it can run before any
heavy project imports.

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.75 — Universal test_environment() for L20.
"""

from .tester import test_environment

__all__ = ["test_environment"]
