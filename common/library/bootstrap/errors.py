"""
L19 — Universal ``BootstrapError`` exception.

Wired into ``common.library.core.errors.BaseErrorManager`` (L10) so both EKS
and DCC raise structured bootstrap errors with project-prefix-aware error codes.

Source
------
dcc: ``workflow/utility_engine/bootstrap/boot_pipeline.py`` (BootstrapError, L76–108)

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.54 — Universal BootstrapError for L19.
"""
from __future__ import annotations

from typing import Optional, Tuple


class BootstrapError(Exception):
    """
    Structured exception for bootstrap phase failures.

    Carries a ``code``, ``message``, and ``phase`` so that both EKS and DCC
    error managers can surface bootstrap failures with full context.  The
    ``to_system_error()`` method returns a ``(code, message)`` tuple for
    compatibility with DCC's ``system_error_print()`` / ``BaseErrorManager``.

    Error code format is project-prefix-aware:
    - EKS:  ``P1-BOOT-*``  (registered in ``eks_error_config.json``)
    - DCC:  ``S-*-S-*``    (legacy format)

    Attributes:
        code:    Error code string (e.g. ``"P1-BOOT-READINESS"``).
        message: Human-readable error message.
        phase:   Bootstrap phase name (e.g. ``"readiness"``, ``"cli"``).
    """

    def __init__(self, code: str, message: str, phase: str = "unknown") -> None:
        self.code = code
        self.message = message
        self.phase = phase
        super().__init__(f"[{code}] {message} (phase: {phase})")

    def to_system_error(self) -> Tuple[str, str]:
        """
        Return ``(code, message)`` tuple for error-manager consumption.

        Compatible with DCC's ``system_error_print(code, message)`` and
        L10 ``BaseErrorManager.handle_system_error()``.
        """
        return (self.code, self.message)

    def to_dict(self) -> dict:
        """Serialize error to a JSON-safe dict."""
        return {
            "code": self.code,
            "message": self.message,
            "phase": self.phase,
        }

    @classmethod
    def from_system_error(cls, code: str, message: str, phase: str = "unknown") -> BootstrapError:
        """Reconstruct from the ``(code, message)`` pair emitted by ``to_system_error()``."""
        return cls(code, message, phase)
