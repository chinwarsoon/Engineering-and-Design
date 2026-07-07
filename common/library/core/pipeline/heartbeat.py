"""
L05 — TelemetryHeartbeat

Merges DCC TelemetryHeartbeat (row-oriented tick()) with EKS TelemetryHeartbeat
(phase/document-oriented add_checkpoint(), threading lock, CPU sampling).

Both forms are supported on the same class so either project can use its
preferred API without changes.

Sources
-------
dcc: core_engine/logging/log_telemetry.py  (TelemetryHeartbeat, HeartbeatPayload)
eks: engine/core/telemetry.py              (TelemetryHeartbeat, DocumentProcessingHeartbeat,
                                            PerformanceMetrics, Checkpoint)
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import psutil


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class HeartbeatPayload:
    """Payload emitted by tick() — DCC row-oriented API."""
    rows_processed: int
    current_phase: str
    memory_usage_mb: float
    timestamp: float
    total_rows: Optional[int] = None
    percent_complete: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows_processed": self.rows_processed,
            "current_phase": self.current_phase,
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "timestamp": self.timestamp,
            "total_rows": self.total_rows,
            "percent_complete": round(self.percent_complete, 1) if self.percent_complete is not None else None,
        }


@dataclass
class Checkpoint:
    """Checkpoint emitted by add_checkpoint() — EKS phase-oriented API."""
    phase: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class PerformanceMetrics:
    """Aggregate performance metrics collected over a run."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    items_per_second: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    cpu_percent_avg: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "items_per_second": self.items_per_second,
            "memory_peak_mb": self.memory_peak_mb,
            "cpu_percent_avg": self.cpu_percent_avg,
        }


# ---------------------------------------------------------------------------
# TelemetryHeartbeat
# ---------------------------------------------------------------------------

class TelemetryHeartbeat:
    """
    Universal telemetry heartbeat supporting both row-oriented (DCC) and
    phase/document-oriented (EKS) APIs.

    Row-oriented usage (DCC)
    ------------------------
    hb = TelemetryHeartbeat(interval=1000)
    for idx, row in df.iterrows():
        hb.tick(idx, current_phase="P1", total_rows=len(df))

    Phase-oriented usage (EKS)
    --------------------------
    hb = TelemetryHeartbeat()
    hb.start()
    hb.add_checkpoint("SCAN", details={"files": 42}, document_count=42)
    hb.stop()
    """

    DEFAULT_INTERVAL = 1000

    def __init__(
        self,
        interval: int = DEFAULT_INTERVAL,
        enabled: bool = True,
        verbose: bool = False,
    ):
        self.interval = interval
        self.enabled = enabled
        self.verbose = verbose

        # Row-oriented state
        self._last_heartbeat_row: int = 0
        self._heartbeat_count: int = 0
        self._start_time_perf: float = time.time()

        # Phase-oriented state
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.metrics = PerformanceMetrics()
        self.callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._process = psutil.Process()
        self._cpu_samples: List[float] = []
        self._memory_samples: List[float] = []
        self._items_processed: int = 0

    # ------------------------------------------------------------------
    # Row-oriented API (DCC)
    # ------------------------------------------------------------------

    def tick(
        self,
        current_row: int,
        current_phase: str,
        total_rows: Optional[int] = None,
        status_print_fn: Optional[Callable] = None,
    ) -> Optional[HeartbeatPayload]:
        """Emit a heartbeat if the row interval has been reached."""
        if not self.enabled:
            return None
        if current_row < self._last_heartbeat_row + self.interval:
            return None

        memory_mb = self._process.memory_info().rss / (1024 * 1024)
        percent = (current_row / total_rows * 100) if total_rows else None

        payload = HeartbeatPayload(
            rows_processed=current_row,
            current_phase=current_phase,
            memory_usage_mb=memory_mb,
            timestamp=time.time(),
            total_rows=total_rows,
            percent_complete=percent,
        )
        self._last_heartbeat_row = current_row
        self._heartbeat_count += 1

        msg = self._format_row_message(payload)
        if status_print_fn:
            status_print_fn(msg, min_level=1)
        elif self.verbose:
            print(msg)

        return payload

    def final_summary(
        self,
        total_rows: int,
        status_print_fn: Optional[Callable] = None,
    ) -> HeartbeatPayload:
        """Emit a final completion heartbeat."""
        memory_mb = self._process.memory_info().rss / (1024 * 1024)
        payload = HeartbeatPayload(
            rows_processed=total_rows,
            current_phase="COMPLETE",
            memory_usage_mb=memory_mb,
            timestamp=time.time(),
            total_rows=total_rows,
            percent_complete=100.0,
        )
        msg = (
            f"✅ Processing complete: {total_rows:,} rows | "
            f"Memory: {memory_mb:.1f} MB | "
            f"Heartbeats: {self._heartbeat_count}"
        )
        if status_print_fn:
            status_print_fn(msg, min_level=1)
        elif self.verbose:
            print(msg)
        return payload

    @staticmethod
    def _format_row_message(payload: HeartbeatPayload) -> str:
        if payload.percent_complete is not None:
            return (
                f"⏳ Processing row {payload.rows_processed:,} "
                f"({payload.percent_complete:.1f}%) | "
                f"Phase: {payload.current_phase} | "
                f"Memory: {payload.memory_usage_mb:.1f} MB"
            )
        return (
            f"⏳ Processing row {payload.rows_processed:,} | "
            f"Phase: {payload.current_phase} | "
            f"Memory: {payload.memory_usage_mb:.1f} MB"
        )

    # ------------------------------------------------------------------
    # Phase-oriented API (EKS)
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start telemetry recording."""
        if not self.enabled:
            return
        with self._lock:
            self.metrics.start_time = datetime.now()
            self._cpu_samples.clear()
            self._memory_samples.clear()
            self._items_processed = 0

    def stop(self) -> None:
        """Stop recording and calculate final metrics."""
        if not self.enabled:
            return
        with self._lock:
            self.metrics.end_time = datetime.now()
            if self.metrics.start_time:
                self.metrics.duration_seconds = (
                    self.metrics.end_time - self.metrics.start_time
                ).total_seconds()
            if self._items_processed > 0 and self.metrics.duration_seconds:
                self.metrics.items_per_second = (
                    self._items_processed / self.metrics.duration_seconds
                )
            if self._memory_samples:
                self.metrics.memory_peak_mb = max(self._memory_samples)
            if self._cpu_samples:
                self.metrics.cpu_percent_avg = sum(self._cpu_samples) / len(self._cpu_samples)

    def add_checkpoint(
        self,
        phase: str,
        details: Optional[Dict[str, Any]] = None,
        document_count: Optional[int] = None,
    ) -> None:
        """Record a named phase checkpoint with optional document count."""
        if not self.enabled:
            return
        with self._lock:
            cp = Checkpoint(phase=phase, timestamp=datetime.now(), details=details or {})
            if document_count is not None:
                self._items_processed = document_count
                cp.details["items_processed"] = document_count
            self.checkpoints[phase] = cp
            self._collect_system_metrics()
            if phase in self.callbacks:
                self.callbacks[phase](cp)
            if self.verbose:
                mem = self._memory_samples[-1] if self._memory_samples else 0
                print(f"[TELEMETRY] Checkpoint: {phase} | Items: {self._items_processed} | Memory: {mem:.1f}MB")

    def register_callback(self, phase: str, callback: Callable) -> None:
        """Register a callback triggered when a named phase checkpoint is added."""
        self.callbacks[phase] = callback

    def _collect_system_metrics(self) -> None:
        try:
            self._memory_samples.append(self._process.memory_info().rss / (1024 * 1024))
            self._cpu_samples.append(self._process.cpu_percent())
        except Exception:
            pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoints": {p: cp.to_dict() for p, cp in self.checkpoints.items()},
            "metrics": self.metrics.to_dict(),
            "heartbeat_count": self._heartbeat_count,
            "enabled": self.enabled,
        }

    def reset(self) -> None:
        with self._lock:
            self.checkpoints.clear()
            self.metrics = PerformanceMetrics()
            self._cpu_samples.clear()
            self._memory_samples.clear()
            self._items_processed = 0
            self._last_heartbeat_row = 0
            self._heartbeat_count = 0


# ---------------------------------------------------------------------------
# DocumentProcessingHeartbeat (EKS subclass)
# ---------------------------------------------------------------------------

class DocumentProcessingHeartbeat(TelemetryHeartbeat):
    """
    Specialized heartbeat for document-processing pipelines.
    Tracks per-phase document counts and calculates progress against a total.

    Source: eks/engine/core/telemetry.py (DocumentProcessingHeartbeat)
    """

    def __init__(self, total_documents: int, enabled: bool = True, verbose: bool = False):
        super().__init__(enabled=enabled, verbose=verbose)
        self.total_documents = total_documents
        self._document_progress: Dict[str, int] = {}

    def update_document_progress(self, phase: str, count: int) -> None:
        self._document_progress[phase] = count

    def get_document_progress(self, phase: str) -> int:
        return self._document_progress.get(phase, 0)

    def add_checkpoint(
        self,
        phase: str,
        details: Optional[Dict[str, Any]] = None,
        document_count: Optional[int] = None,
    ) -> None:
        if document_count is not None:
            self.update_document_progress(phase, document_count)
        details = details or {}
        details["total_documents"] = self.total_documents
        details["document_progress"] = self._document_progress.copy()
        super().add_checkpoint(phase, details, document_count)
