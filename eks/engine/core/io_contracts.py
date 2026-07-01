"""Engine I/O Contracts — Standardized input/output contracts for all EKS engines.

This module consolidates and extends the base EngineInput/EngineOutput contracts
from base.py with domain-specific contracts for each engine type (discovery,
health scoring). Parser-specific contracts live in parsers/io_contracts.py.

Revision: 0.1
Date: 2026-07-01
Author: System
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import EngineInput, EngineOutput, ErrorRecord, ValidationResult

__all__ = [
    "EngineInput", "EngineOutput", "ErrorRecord", "ValidationResult",
    "DiscoveryInput", "DiscoveryOutput",
    "HealthInput", "HealthOutput",
]


@dataclass
class DiscoveryInput(EngineInput):
    """Input contract for the discovery/file-scanning engine.

    Extends EngineInput with file-type filtering and recursion control.
    """
    file_types: Optional[List[str]] = None
    recursive: bool = True


@dataclass
class DiscoveryOutput(EngineOutput):
    """Output contract for the discovery engine.

    Adds scan summary counters and the list of discovered file metadata.
    """
    discovered: int = 0
    valid: int = 0
    unknown: int = 0
    registered: int = 0
    files: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "discovered": self.discovered,
            "valid": self.valid,
            "unknown": self.unknown,
            "registered": self.registered,
            "files": self.files,
        })
        return base


@dataclass
class HealthInput(EngineInput):
    """Input contract for the health scoring engine.

    Extends EngineInput with the document record and detected structural elements.
    """
    document: Optional[Dict[str, Any]] = None
    elements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HealthOutput(EngineOutput):
    """Output contract for the health scoring engine.

    Adds overall score and per-dimension breakdown.
    """
    overall: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "overall": self.overall,
            "dimensions": self.dimensions,
        })
        return base
