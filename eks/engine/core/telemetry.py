"""
TelemetryHeartbeat - Progress and performance monitoring for EKS pipeline.

This module implements the TelemetryHeartbeat pattern per Appendix F,
providing document processing checkpoints, performance metrics, and
progress tracking.

Revision: 0.1
Date: 2026-06-30
Author: System
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import time
import psutil
import threading


@dataclass
class Checkpoint:
    """Telemetry checkpoint for pipeline progress tracking."""
    phase: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for pipeline execution."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    documents_per_second: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    cpu_percent_avg: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "documents_per_second": self.documents_per_second,
            "memory_peak_mb": self.memory_peak_mb,
            "cpu_percent_avg": self.cpu_percent_avg
        }


class TelemetryHeartbeat:
    """
    Telemetry heartbeat for progress and performance monitoring.
    
    This class implements the TelemetryHeartbeat pattern per Appendix F,
    providing document processing checkpoints, performance metrics, and
    progress tracking.
    
    Attributes:
        checkpoints: List of telemetry checkpoints
        metrics: Performance metrics
        callbacks: Callback functions for heartbeat events
        enabled: Whether telemetry is enabled
        verbose: Whether to print verbose output
    """
    
    def __init__(self, enabled: bool = True, verbose: bool = False):
        """
        Initialize telemetry heartbeat.
        
        Args:
            enabled: Whether telemetry is enabled
            verbose: Whether to print verbose output
        """
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.metrics = PerformanceMetrics()
        self.callbacks: Dict[str, Callable] = {}
        self.enabled = enabled
        self.verbose = verbose
        self._lock = threading.Lock()
        self._process = psutil.Process()
        self._cpu_samples: list = []
        self._memory_samples: list = []
        self._documents_processed: int = 0
        self._start_time: Optional[datetime] = None
    
    def start(self):
        """Start telemetry recording."""
        if not self.enabled:
            return
        
        with self._lock:
            self._start_time = datetime.now()
            self.metrics.start_time = self._start_time
            self._cpu_samples = []
            self._memory_samples = []
            self._documents_processed = 0
            
            if self.verbose:
                print(f"[TELEMETRY] Started at {self._start_time.isoformat()}")
    
    def stop(self):
        """Stop telemetry recording and calculate final metrics."""
        if not self.enabled:
            return
        
        with self._lock:
            self.metrics.end_time = datetime.now()
            if self.metrics.start_time:
                self.metrics.duration_seconds = (
                    self.metrics.end_time - self.metrics.start_time
                ).total_seconds()
            
            if self._documents_processed > 0 and self.metrics.duration_seconds:
                self.metrics.documents_per_second = (
                    self._documents_processed / self.metrics.duration_seconds
                )
            
            if self._memory_samples:
                self.metrics.memory_peak_mb = max(self._memory_samples)
            
            if self._cpu_samples:
                self.metrics.cpu_percent_avg = sum(self._cpu_samples) / len(self._cpu_samples)
            
            if self.verbose:
                print(f"[TELEMETRY] Stopped at {self.metrics.end_time.isoformat()}")
                print(f"[TELEMETRY] Duration: {self.metrics.duration_seconds:.2f}s")
                print(f"[TELEMETRY] Documents/sec: {self.metrics.documents_per_second:.2f}")
                print(f"[TELEMETRY] Memory peak: {self.metrics.memory_peak_mb:.2f}MB")
                print(f"[TELEMETRY] CPU avg: {self.metrics.cpu_percent_avg:.2f}%")
    
    def add_checkpoint(
        self,
        phase: str,
        details: Optional[Dict[str, Any]] = None,
        document_count: Optional[int] = None
    ):
        """
        Add a telemetry checkpoint.
        
        Args:
            phase: Phase name (e.g., "SCAN", "PARSE", "SCORE")
            details: Optional details about the checkpoint
            document_count: Optional document count for progress tracking
        """
        if not self.enabled:
            return
        
        with self._lock:
            checkpoint = Checkpoint(
                phase=phase,
                timestamp=datetime.now(),
                details=details or {}
            )
            
            if document_count is not None:
                self._documents_processed = document_count
                checkpoint.details["documents_processed"] = document_count
            
            self.checkpoints[phase] = checkpoint
            
            # Collect system metrics
            self._collect_system_metrics()
            
            # Trigger callback if registered
            if phase in self.callbacks:
                self.callbacks[phase](checkpoint)
            
            if self.verbose:
                progress = self._calculate_progress()
                print(
                    f"[TELEMETRY] Checkpoint: {phase} | "
                    f"Progress: {progress:.1f}% | "
                    f"Docs: {self._documents_processed} | "
                    f"Memory: {self._memory_samples[-1] if self._memory_samples else 0:.2f}MB | "
                    f"CPU: {self._cpu_samples[-1] if self._cpu_samples else 0:.1f}%"
                )
    
    def _collect_system_metrics(self):
        """Collect system metrics (memory, CPU)."""
        try:
            memory_info = self._process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self._memory_samples.append(memory_mb)
            
            cpu_percent = self._process.cpu_percent()
            self._cpu_samples.append(cpu_percent)
        except Exception:
            pass
    
    def _calculate_progress(self) -> float:
        """Calculate progress percentage based on checkpoints."""
        if not self.checkpoints:
            return 0.0
        
        # Simple progress based on number of checkpoints
        # In a real implementation, this would be based on expected phases
        total_phases = 5  # A, B, C, D, E phases
        return (len(self.checkpoints) / total_phases) * 100
    
    def register_callback(self, phase: str, callback: Callable[[Checkpoint], None]):
        """
        Register a callback for a specific phase.
        
        Args:
            phase: Phase name
            callback: Callback function
        """
        self.callbacks[phase] = callback
    
    def get_checkpoint(self, phase: str) -> Optional[Checkpoint]:
        """
        Get a checkpoint by phase name.
        
        Args:
            phase: Phase name
            
        Returns:
            Checkpoint if found, None otherwise
        """
        return self.checkpoints.get(phase)
    
    def get_all_checkpoints(self) -> Dict[str, Checkpoint]:
        """Get all checkpoints."""
        return self.checkpoints.copy()
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry to dictionary for serialization."""
        return {
            "checkpoints": {
                phase: cp.to_dict() for phase, cp in self.checkpoints.items()
            },
            "metrics": self.metrics.to_dict(),
            "enabled": self.enabled
        }
    
    def reset(self):
        """Reset telemetry state."""
        with self._lock:
            self.checkpoints.clear()
            self.metrics = PerformanceMetrics()
            self._cpu_samples = []
            self._memory_samples = []
            self._documents_processed = 0
            self._start_time = None


class DocumentProcessingHeartbeat(TelemetryHeartbeat):
    """
    Specialized heartbeat for document processing.
    
    This class extends TelemetryHeartbeat with document-specific
    progress tracking and metrics.
    """
    
    def __init__(self, total_documents: int, enabled: bool = True, verbose: bool = False):
        """
        Initialize document processing heartbeat.
        
        Args:
            total_documents: Total number of documents to process
            enabled: Whether telemetry is enabled
            verbose: Whether to print verbose output
        """
        super().__init__(enabled=enabled, verbose=verbose)
        self.total_documents = total_documents
        self._document_progress: Dict[str, int] = {}
    
    def update_document_progress(self, phase: str, count: int):
        """
        Update document progress for a specific phase.
        
        Args:
            phase: Phase name
            count: Number of documents processed in this phase
        """
        self._document_progress[phase] = count
    
    def get_document_progress(self, phase: str) -> int:
        """
        Get document progress for a specific phase.
        
        Args:
            phase: Phase name
            
        Returns:
            Number of documents processed in this phase
        """
        return self._document_progress.get(phase, 0)
    
    def _calculate_progress(self) -> float:
        """Calculate progress percentage based on document counts."""
        if self.total_documents == 0:
            return 0.0
        
        # Use the maximum document count across all phases
        max_processed = max(self._document_progress.values()) if self._document_progress else 0
        return (max_processed / self.total_documents) * 100
    
    def add_checkpoint(
        self,
        phase: str,
        details: Optional[Dict[str, Any]] = None,
        document_count: Optional[int] = None
    ):
        """
        Add a telemetry checkpoint with document progress.
        
        Args:
            phase: Phase name
            details: Optional details about the checkpoint
            document_count: Optional document count for progress tracking
        """
        if document_count is not None:
            self.update_document_progress(phase, document_count)
        
        details = details or {}
        details["total_documents"] = self.total_documents
        details["document_progress"] = self._document_progress.copy()
        
        super().add_checkpoint(phase, details, document_count)
