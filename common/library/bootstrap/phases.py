"""
L19 — Configurable ``BootstrapPhaseRegistry``.

Allows projects to register custom phases or reorder the default P1–P8 sequence.
The universal ``BootstrapManager`` uses this registry to drive phase ordering.

Revision: 0.1
Date: 2026-07-17
Author: opencode
Summary: T1.99.51 — Universal BootstrapPhaseRegistry for L19.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BootstrapPhaseStatus:
    """
    Per-phase tracking record.

    Mirrors DCC's ``BootstrapPhaseStatus`` (boot_pipeline.py L111–148).

    Attributes:
        phase_id:   Phase identifier (e.g. ``"P1_cli"``).
        phase_name: Human-readable phase name (e.g. ``"CLI Parsing"``).
        status:     Current status — ``pending``, ``running``, ``complete``, ``failed``.
        start_time: ISO 8601 timestamp of phase start.
        end_time:   ISO 8601 timestamp of phase end.
        duration_ms: Phase duration in milliseconds.
        error_code: Error code if phase failed.
    """
    phase_id: str
    phase_name: str
    status: str = "pending"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None


@dataclass
class PhaseEntry:
    """
    A single phase entry in the registry.

    Attributes:
        phase_id:   Phase identifier.
        phase_name: Human-readable name.
        order:      Execution order (lower = earlier).
        method:     Name of the BootstrapManager method that implements this phase.
    """
    phase_id: str
    phase_name: str
    order: int
    method: str


class BootstrapPhaseRegistry:
    """
    Configurable registry of bootstrap phases.

    The default 8-phase sequence mirrors DCC's P1–P8:
    1. P1_cli      — CLI Parsing
    2. P2_paths    — Path Validation
    3. P3_registry — Registry Loading
    4. P4_defaults — Native Defaults Building
    5. P5_fallback — Fallback Validation
    6. P6_env      — Environment Testing
    7. P7_schema   — Schema Resolution
    8. P8_params   — Parameters Resolution

    Projects can register additional phases, reorder existing ones, or
    override method names via the fluent API.
    """

    _DEFAULT_PHASES: List[PhaseEntry] = [
        PhaseEntry("P1_cli",      "CLI Parsing",              1, "_bootstrap_cli"),
        PhaseEntry("P2_paths",    "Path Validation",           2, "_bootstrap_paths"),
        PhaseEntry("P3_registry", "Registry Loading",          3, "_bootstrap_registry"),
        PhaseEntry("P4_defaults", "Native Defaults Building",  4, "_bootstrap_defaults"),
        PhaseEntry("P5_fallback", "Fallback Validation",       5, "_bootstrap_fallback"),
        PhaseEntry("P6_env",      "Environment Testing",       6, "_bootstrap_env"),
        PhaseEntry("P7_schema",   "Schema Resolution",         7, "_bootstrap_schema"),
        PhaseEntry("P8_params",   "Parameters Resolution",     8, "_bootstrap_params"),
    ]

    def __init__(self) -> None:
        self._phases: Dict[str, PhaseEntry] = {}
        for entry in self._DEFAULT_PHASES:
            self._phases[entry.phase_id] = entry

    # ------------------------------------------------------------------
    # Fluent API
    # ------------------------------------------------------------------

    def register(
        self,
        phase_id: str,
        phase_name: str,
        order: int,
        method: str = "",
    ) -> BootstrapPhaseRegistry:
        """Register or replace a phase entry. Returns self for chaining."""
        self._phases[phase_id] = PhaseEntry(phase_id, phase_name, order, method)
        return self

    def remove(self, phase_id: str) -> BootstrapPhaseRegistry:
        """Remove a phase from the registry. Returns self for chaining."""
        self._phases.pop(phase_id, None)
        return self

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, phase_id: str) -> Optional[PhaseEntry]:
        """Get a phase entry by id."""
        return self._phases.get(phase_id)

    def get_phase_name(self, phase_id: str) -> str:
        """Get the human-readable name for a phase id."""
        entry = self._phases.get(phase_id)
        return entry.phase_name if entry else phase_id

    def iter_ordered(self):
        """Yield phase entries in ascending order."""
        for entry in sorted(self._phases.values(), key=lambda e: e.order):
            yield entry

    def get_method(self, phase_id: str) -> str:
        """Get the method name for a phase id."""
        entry = self._phases.get(phase_id)
        return entry.method if entry else ""

    def build_phase_status(self) -> Dict[str, BootstrapPhaseStatus]:
        """Build the initial phase-tracking dict from the registry."""
        return {
            e.phase_id: BootstrapPhaseStatus(e.phase_id, e.phase_name)
            for e in self.iter_ordered()
        }

    @property
    def phase_count(self) -> int:
        return len(self._phases)

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize all phase entries to a list of dicts."""
        return [
            {"phase_id": e.phase_id, "phase_name": e.phase_name,
             "order": e.order, "method": e.method}
            for e in self.iter_ordered()
        ]
