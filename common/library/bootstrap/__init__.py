"""
L19 — Universal Bootstrap Manager

Provides a project-agnostic, stateful bootstrap orchestrator extracted from DCC's
mature ``BootstrapManager`` (~1223 lines, 8 phases).  EKS (and future projects)
delegate bootstrap to this shared manager rather than building their own logic.

Sub-packages
------------
- ``manager`` — ``BootstrapManager`` class with phase tracking, traces, and dual-mode
- ``errors``  — ``BootstrapError`` exception wired to L10 ``BaseErrorManager``
- ``phases``  — ``BootstrapPhaseRegistry`` for configurable phase ordering

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.50–54 — L19 universal BootstrapManager scaffold.
"""

from .manager import BootstrapManager
from .errors import BootstrapError
from .phases import BootstrapPhaseRegistry, BootstrapPhaseStatus

__all__ = [
    "BootstrapManager",
    "BootstrapError",
    "BootstrapPhaseRegistry",
    "BootstrapPhaseStatus",
]
