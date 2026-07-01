"""UI Contracts — Single Source of Truth for UI contract definitions.

Per Appendix G §7, this module defines the contracts that govern
communication between the frontend and the backend API.

Revision: 0.1
Date: 2026-07-01
Author: System
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DocumentSelectionContract:
    """Validates document selection for pipeline processing.

    Attributes:
        data_dir: Path to document data folder.
        file_types: Filter by extension (e.g., ["pdf", "docx"]).
        include_subfolders: Whether to recurse into subdirectories.
        max_files: Maximum files to accept in one batch.
    """
    data_dir: str
    file_types: Optional[List[str]] = None
    include_subfolders: bool = True
    max_files: int = 1000


@dataclass
class PipelineConfigContract:
    """Pipeline execution parameters.

    Attributes:
        debug: Enable verbose debug output.
        workers: Number of parallel workers.
        health_threshold: Minimum score for auto-register.
        skip_parsing: Dry-run mode (scan + register only).
    """
    debug: bool = False
    workers: int = 1
    health_threshold: float = 0.5
    skip_parsing: bool = False


@dataclass
class QueryRequestContract:
    """User query input (Phase 5).

    Attributes:
        query: Natural language query string.
        filters: Optional filters (project, discipline, doc type, revision).
        max_results: Maximum results to return.
    """
    query: str
    filters: Optional[Dict[str, Any]] = None
    max_results: int = 10


@dataclass
class QueryResponseContract:
    """Query result output (Phase 5).

    Attributes:
        answer: Generated answer text.
        sources: Citations with doc_number, revision, page.
        assets: Linked asset references.
        confidence: Answer confidence score.
    """
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
