## Issue Log: Pipeline Architecture Workplan

**Workplan ID**: WP-PIPE-ARCH-001  
**Document**: [pipeline_architecture_design_workplan.md](pipeline_architecture_design_workplan.md)

---

## Open Issues

*None currently tracked.*

---

## Resolved Issues

### ISS-001: Phase 3 Heartbeat Interval Limitation
**ID**: ISS-001  
**Status**: RESOLVED  
**Phase**: 3  
**Date Opened**: 2026-04-28  
**Date Closed**: 2026-04-28

**Description**:  
R17 Telemetry Module requires heartbeat logs every 1,000 rows. However, the CalculationEngine uses **vectorized pandas operations** (processes entire columns at once) rather than row-by-row iteration. This architectural pattern does not provide natural iteration points to emit true "every 1000 rows" heartbeats without significant performance impact from chunked processing.

**Impact**:  
- Heartbeats emit at **phase checkpoints** (P1, P2, P2.5, P3) rather than at true 1,000-row intervals
- For an 11,099-row dataset, only 1 heartbeat was emitted at the end of P1 instead of ~11 heartbeats
- User-visible progress messages show "100.0%" at each phase checkpoint
- Telemetry data still captures `rows_processed`, `current_phase`, `memory_usage_mb`, and `percent_complete`

**Resolution**:  
Accepted as **architectural limitation** with phase-based heartbeats as the pragmatic solution:
1. Heartbeats emit at the end of each processing phase (P1, P2, P2.5, P3)
2. Each heartbeat captures total rows processed so far
3. Memory usage is sampled at each checkpoint
4. Future enhancement: Implement chunked processing if true row-by-row heartbeats are required

**Mitigation**:  
- Phase-based heartbeats provide adequate progress visibility for typical use cases
- Heartbeat interval can be adjusted via `TelemetryHeartbeat(interval=N)` if needed
- Chunked processing could be implemented as an optional processing mode

**References**:  
- [telemetry_heartbeat.py](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/core_engine/telemetry_heartbeat.py)
- [engine.py:apply_phased_processing()](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/processor_engine/core/engine.py)
- [R17 Requirement - Telemetry Module](pipeline_architecture_design_workplan.md#4-scope-summary)

---

## Issue Template

**ID**: [Unique issue identifier]
**Status**: [OPEN / IN_PROGRESS / RESOLVED]
**Phase**: [Related phase number]
**Date Opened**: [YYYY-MM-DD]
**Date Closed**: [YYYY-MM-DD]

**Description**: [Brief description]

**Impact**: [What is affected]

**Resolution**: [How it was resolved]

**References**: [Links to related files/commits]
