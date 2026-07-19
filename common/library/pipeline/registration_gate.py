"""
Registration Gate Protocol — common.library.pipeline.registration_gate.

Abstract base class defining the register→check→skip-or-create contract.
Project-specific registries (EKS, DCC, code_tracer) implement this interface
against their own storage backends.

Revision: 0.1
Date: 2026-07-19
Author: CodeBuddy
Summary: Extracted from eks.engine.core.registry.DocumentRegistry pattern
         (T1.99.149 — I187).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

__all__ = ["RegistrationGate"]


class RegistrationGate(ABC):
    """
    Abstract protocol for a content-aware registration gateway.

    Concrete implementations answer four questions:
    1. Does this business key already exist?
    2. Has the content changed since the last registration?
    3. Should we skip registration entirely?
    4. How do we register new content?

    This separates *policy* (when to skip/register) from *mechanism*
    (how to persist), allowing projects to swap storage backends while
    maintaining consistent logic.
    """

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Return ``True`` if a row for *key* already exists in storage.

        Args:
            key: A business-level unique identifier (e.g. document_number).
        """
        ...

    @abstractmethod
    def content_changed(self, key: str, content_hash: str) -> bool:
        """
        Return ``True`` if the content hash for *key* differs from the
        currently-registered value.

        Args:
            key: Business-level identifier.
            content_hash: Computed hash of the current file content.
        """
        ...

    @abstractmethod
    def register(self, metadata: Dict[str, Any]) -> str:
        """
        Persist a new registration entry.

        Args:
            metadata: Arbitrary metadata dict.

        Returns:
            The unique row identifier assigned by storage.
        """
        ...

    @abstractmethod
    def should_skip(self, key: str, content_hash: str) -> bool:
        """
        Return ``True`` if registration should be skipped for this key+hash.

        Default policy: skip when ``exists(key) AND NOT content_changed(key, content_hash)``.

        Args:
            key: Business-level identifier.
            content_hash: Computed hash of the current file content.
        """
        ...
