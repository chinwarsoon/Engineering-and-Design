"""Parser I/O Contracts — Standardized input/output for the parser engine.

Revision: 0.1
Date: 2026-07-01
Author: System
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.base import EngineInput, EngineOutput


@dataclass
class ParserInput(EngineInput):
    """Input contract for the parser engine.

    Extends EngineInput with the target file path, file type code,
    and optional parser configuration overrides.
    """
    file_path: str = ""
    file_type: str = ""
    parser_config: Optional[Dict[str, Any]] = None


@dataclass
class ParserOutput(EngineOutput):
    """Output contract for the parser engine.

    Adds the extracted content blocks, metadata, detected structural
    elements, and per-file confidence.
    """
    content_blocks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    elements: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "content_blocks": self.content_blocks,
            "metadata": self.metadata,
            "elements": self.elements,
            "confidence": self.confidence,
        })
        return base
