"""
L06 — BasePipelineContext

Abstract base providing serialization, checkpoint persistence, and phase
lifecycle methods. Both DCC PipelineContext and EKS EKSPipelineContext
extend this base with their domain-specific fields.

Sources
-------
dcc: core_engine/context/context_pipeline.py  (PipelineContext + nested dataclasses)
eks: engine/core/context.py                   (EKSPipelineContext + nested dataclasses)
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class BasePipelineContext(ABC):
    """
    Abstract base for all pipeline context objects.

    Provides
    --------
    - to_dict() / to_json()         serialization
    - from_dict() / from_json()     deserialization (class methods on subclass)
    - save_checkpoint()             persist state to JSON file
    - load_checkpoint()             restore state from JSON file
    - update_phase()                update current phase + add telemetry checkpoint
    - complete() / fail()           terminal lifecycle transitions

    Subclasses must implement
    -------------------------
    - to_dict()     return a JSON-serializable dict of all fields
    - _from_dict()  class method reconstructing the subclass from a dict
    """

    # ------------------------------------------------------------------
    # Serialization — subclass must implement to_dict()
    # ------------------------------------------------------------------

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict of all context fields."""

    def to_json(self) -> str:
        """Serialize context to a JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    @abstractmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "BasePipelineContext":
        """Reconstruct context from a dict. Implemented by each subclass."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BasePipelineContext":
        return cls._from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> "BasePipelineContext":
        return cls._from_dict(json.loads(json_str))

    # ------------------------------------------------------------------
    # Checkpoint persistence
    # ------------------------------------------------------------------

    def save_checkpoint(self, checkpoint_path: str | Path) -> None:
        """Persist current context state to a JSON file."""
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str | Path) -> "BasePipelineContext":
        """Restore context from a previously saved checkpoint file."""
        path = Path(checkpoint_path)
        return cls.from_json(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Phase lifecycle — subclasses override to update their state fields
    # ------------------------------------------------------------------

    def update_phase(self, phase: str, status: str = "IN_PROGRESS") -> None:
        """
        Update the current phase and status.
        Subclasses should call super() then update their own state fields.
        """

    def complete(self) -> None:
        """Mark the pipeline run as successfully completed."""

    def fail(self, error_message: str) -> None:
        """Mark the pipeline run as failed with an error message."""
