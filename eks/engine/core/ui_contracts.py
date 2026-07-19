"""EKS UI Contracts — standardized interfaces between pipeline engine and UI layer.

T1.99.192 (I217): Created per Appendix F §2.3.7 UI contract specifications.
Defines the data contracts that the UI layer consumes from the pipeline:
progress events, phase summaries, document review items, and pipeline status.

T1.99.193 (I222): Added UIRenderInput, UIRenderOutput, UIEvent, UIActionResponse
stubs per Appendix F §2.3.3 for independent engine UI contract boundaries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ProgressEvent:
    """Pipeline progress event for UI progress bars and status updates.

    Emitted by the pipeline orchestrator at each processing milestone.
    """
    event_id: str
    phase: str  # A, B, C
    status: str  # STARTED, IN_PROGRESS, COMPLETE, FAILED
    message: str
    percent: float = 0.0  # 0.0–100.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "phase": self.phase,
            "status": self.status,
            "message": self.message,
            "percent": self.percent,
            "timestamp": self.timestamp,
        }


@dataclass
class PhaseSummary:
    """Aggregate summary for a single pipeline phase (A/B/C).

    Rendered in the UI as a summary card or section header.
    """
    phase: str
    status: str
    docs_total: int = 0
    docs_processed: int = 0
    docs_succeeded: int = 0
    docs_failed: int = 0
    docs_flagged: int = 0
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status,
            "docs_total": self.docs_total,
            "docs_processed": self.docs_processed,
            "docs_succeeded": self.docs_succeeded,
            "docs_failed": self.docs_failed,
            "docs_flagged": self.docs_flagged,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
        }


@dataclass
class DocumentReviewItem:
    """A single document flagged for manual review.

    Consumed by the Phase C review UI to display flagged documents
    with their health scores, confidence, and review actions.
    """
    doc_id: str
    document_number: str
    revision: str
    document_type: str = ""
    extract_status: str = "pending"
    extraction_confidence: float = 0.0
    health_score: float = 0.0
    needs_review: bool = True
    review_reason: str = ""
    elements: List[Dict[str, Any]] = field(default_factory=list)
    file_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "document_number": self.document_number,
            "revision": self.revision,
            "document_type": self.document_type,
            "extract_status": self.extract_status,
            "extraction_confidence": self.extraction_confidence,
            "health_score": self.health_score,
            "needs_review": self.needs_review,
            "review_reason": self.review_reason,
            "elements": self.elements,
            "file_path": self.file_path,
        }


@dataclass
class PipelineStatus:
    """Full pipeline status for the UI dashboard.

    Aggregate of all phase summaries plus overall pipeline health.
    """
    run_id: str
    status: str  # INITIALIZED, IN_PROGRESS, COMPLETE, FAILED
    current_phase: str = "INIT"
    phases: Dict[str, PhaseSummary] = field(default_factory=dict)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "current_phase": self.current_phase,
            "phases": {k: v.to_dict() for k, v in self.phases.items()},
            "start_time": self.start_time,
            "end_time": self.end_time,
            "telemetry": self.telemetry,
        }


@dataclass
class UIContext:
    """Top-level UI context contract.

    Wraps all UI-facing data from a pipeline run: progress events,
    phase summaries, flagged documents, and final pipeline status.
    """
    run_id: str
    pipeline_status: PipelineStatus = field(default_factory=lambda: PipelineStatus(run_id="", status="INITIALIZED"))
    progress_events: List[ProgressEvent] = field(default_factory=list)
    phase_summaries: Dict[str, PhaseSummary] = field(default_factory=dict)
    flagged_documents: List[DocumentReviewItem] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "pipeline_status": self.pipeline_status.to_dict(),
            "progress_events": [e.to_dict() for e in self.progress_events],
            "phase_summaries": {k: v.to_dict() for k, v in self.phase_summaries.items()},
            "flagged_documents": [d.to_dict() for d in self.flagged_documents],
            "errors": self.errors,
        }


@dataclass
class UIRenderInput:
    """Input contract for rendering pipeline results in the UI.

    Carries the data needed by the UI rendering layer to display
    pipeline progress, flagged documents, and status.
    """
    run_id: str
    pipeline_status: "PipelineStatus" = field(default_factory=lambda: PipelineStatus(run_id="", status="INITIALIZED"))
    phase_summaries: Dict[str, "PhaseSummary"] = field(default_factory=dict)
    flagged_documents: List["DocumentReviewItem"] = field(default_factory=list)
    progress_events: List["ProgressEvent"] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "pipeline_status": self.pipeline_status.to_dict(),
            "phase_summaries": {k: v.to_dict() for k, v in self.phase_summaries.items()},
            "flagged_documents": [d.to_dict() for d in self.flagged_documents],
            "progress_events": [e.to_dict() for e in self.progress_events],
            "errors": self.errors,
            "config": self.config,
        }


@dataclass
class UIRenderOutput:
    """Output contract from the UI rendering layer.

    Contains the rendered page/component state after processing a
    UIRenderInput.  Used to track what was rendered and whether the
    render completed successfully.
    """
    run_id: str
    rendered: bool = True
    template: str = "pipeline_dashboard"
    sections_rendered: List[str] = field(default_factory=list)
    render_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "rendered": self.rendered,
            "template": self.template,
            "sections_rendered": self.sections_rendered,
            "render_time_ms": self.render_time_ms,
            "errors": self.errors,
        }


@dataclass
class UIEvent:
    """User-initiated UI event contract.

    Captures user actions (button clicks, form submissions, navigation)
    from the UI layer for processing by the pipeline engine.
    """
    event_id: str
    event_type: str  # e.g., "rerun", "approve_doc", "correct_field", "export"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = "anonymous"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
        }


@dataclass
class UIActionResponse:
    """Response contract for UI events processed by the pipeline engine.

    Returned to the UI after processing a UIEvent to indicate success
    or failure and any updated data.
    """
    event_id: str
    success: bool = True
    message: str = ""
    updated_fields: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "success": self.success,
            "message": self.message,
            "updated_fields": self.updated_fields,
            "errors": self.errors,
            "timestamp": self.timestamp,
        }


__all__ = [
    "ProgressEvent",
    "PhaseSummary",
    "DocumentReviewItem",
    "PipelineStatus",
    "UIContext",
    "UIRenderInput",
    "UIRenderOutput",
    "UIEvent",
    "UIActionResponse",
]
