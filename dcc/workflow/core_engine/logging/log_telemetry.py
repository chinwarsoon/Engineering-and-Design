"""
Telemetry Heartbeat Module

Implements Phase 3: Telemetry and Progress Contract (R17)
Provides heartbeat logging every N rows during data processing.

Features:
- Heartbeat logs every 1,000 rows (configurable)
- Tracks: rows_processed, current_phase, memory_usage, timestamp
- Visible by default at milestone level for user feedback
- Integrates with PipelineContext telemetry system
"""

import time
import psutil
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class HeartbeatPayload:
    """Telemetry heartbeat payload structure."""
    rows_processed: int
    current_phase: str
    memory_usage_mb: float
    timestamp: float
    total_rows: Optional[int] = None
    percent_complete: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "rows_processed": self.rows_processed,
            "current_phase": self.current_phase,
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "timestamp": self.timestamp,
            "total_rows": self.total_rows,
            "percent_complete": round(self.percent_complete, 1) if self.percent_complete else None,
        }


class TelemetryHeartbeat:
    """
    Heartbeat telemetry tracker for data processing.
    
    Emits progress logs every N rows to provide real-time feedback
    on processing status.
    
    Example:
        heartbeat = TelemetryHeartbeat(interval=1000)
        for idx, row in df.iterrows():
            heartbeat.tick(idx, current_phase="P1", total_rows=len(df))
            process_row(row)
    """
    
    DEFAULT_INTERVAL = 1000  # Log every 1000 rows
    
    def __init__(self, interval: int = DEFAULT_INTERVAL):
        """
        Initialize heartbeat tracker.
        
        Args:
            interval: Number of rows between heartbeat logs (default 1000)
        """
        self.interval = interval
        self.last_heartbeat_row = 0
        self.heartbeat_count = 0
        self.start_time = time.time()
        
    def tick(
        self,
        current_row: int,
        current_phase: str,
        total_rows: Optional[int] = None,
        status_print_fn: Optional[callable] = None,
    ) -> Optional[HeartbeatPayload]:
        """
        Process a row tick and emit heartbeat if interval reached.
        
        Args:
            current_row: Current row index being processed
            current_phase: Current processing phase (P1, P2, P2.5, P3, etc.)
            total_rows: Total number of rows (for percentage calculation)
            status_print_fn: Optional print function for output
            
        Returns:
            HeartbeatPayload if heartbeat emitted, None otherwise
        """
        # Check if we've reached the next heartbeat interval
        next_heartbeat = self.last_heartbeat_row + self.interval
        
        if current_row >= next_heartbeat:
            payload = self._emit_heartbeat(
                current_row=current_row,
                current_phase=current_phase,
                total_rows=total_rows,
                status_print_fn=status_print_fn,
            )
            return payload
        
        return None
    
    def _emit_heartbeat(
        self,
        current_row: int,
        current_phase: str,
        total_rows: Optional[int],
        status_print_fn: Optional[callable],
    ) -> HeartbeatPayload:
        """Emit heartbeat log and update tracking."""
        # Get memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Calculate percent complete
        percent = None
        if total_rows and total_rows > 0:
            percent = (current_row / total_rows) * 100
        
        # Create payload
        payload = HeartbeatPayload(
            rows_processed=current_row,
            current_phase=current_phase,
            memory_usage_mb=memory_mb,
            timestamp=time.time(),
            total_rows=total_rows,
            percent_complete=percent,
        )
        
        # Update tracking
        self.last_heartbeat_row = current_row
        self.heartbeat_count += 1
        
        # Format message for user visibility (default level)
        progress_msg = self._format_progress_message(payload)
        
        # Emit via status print if available, otherwise print
        if status_print_fn:
            status_print_fn(progress_msg, min_level=1)  # Level 1 = always visible
        else:
            print(progress_msg)
        
        return payload
    
    def _format_progress_message(self, payload: HeartbeatPayload) -> str:
        """Format heartbeat payload for user display."""
        if payload.percent_complete is not None:
            return (
                f"⏳ Processing row {payload.rows_processed:,} "
                f"({payload.percent_complete:.1f}%) | "
                f"Phase: {payload.current_phase} | "
                f"Memory: {payload.memory_usage_mb:.1f} MB"
            )
        else:
            return (
                f"⏳ Processing row {payload.rows_processed:,} | "
                f"Phase: {payload.current_phase} | "
                f"Memory: {payload.memory_usage_mb:.1f} MB"
            )
    
    def final_summary(
        self,
        total_rows: int,
        status_print_fn: Optional[callable] = None,
    ) -> HeartbeatPayload:
        """Emit final summary heartbeat."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
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
            f"Heartbeats: {self.heartbeat_count}"
        )
        
        if status_print_fn:
            status_print_fn(msg, min_level=1)
        else:
            print(msg)
        
        return payload


def create_heartbeat(
    interval: int = TelemetryHeartbeat.DEFAULT_INTERVAL,
) -> TelemetryHeartbeat:
    """Factory function to create heartbeat tracker."""
    return TelemetryHeartbeat(interval=interval)
