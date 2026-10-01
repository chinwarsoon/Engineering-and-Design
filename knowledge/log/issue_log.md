# Issue Log

| Field | Value |
|---|---|
| **Project** | Knowledge Network Viewer (abbreviation `knowledge_network`) |
| **Location** | `knowledge/log/issue_log.md` |
| **Last Updated** | 2026-10-01 |
| **Governance** | AGENTS.md §5.17 — fixed structure, targeted edits only, never rewrite the whole file |

## Legend

### Status

| Marker | Status | Meaning |
|---|---|---|
| ✅ | Resolved | Fixed, verified, closed |
| 🔵 | Under Review | Solution proposed, waiting for review |
| ⏳ | In Progress | Actively being worked on |
| ⏸️ | On Hold | Paused intentionally, will resume |
| 🔷 | Planned | Accepted and scheduled, not started |
| 🔴 | Open | Known problem, not yet scheduled |
| ⛔ | Blocked | Cannot proceed, waiting for an external input or decision |
| 🔶 | Needs Decision | Requires a user or owner decision before it can move |
| 🟣 | Monitoring | Not fixed, being watched for recurrence or impact |
| ⚪ | Closed — Wont Fix | Closed without a fix, reason recorded |

### Severity

| Marker | Severity | Meaning |
|---|---|---|
| **S1** | Critical | Blocks delivery or produces wrong results; must be fixed before the phase gate |
| **S2** | High | Major functional or compliance gap; fix within the current phase |
| **S3** | Medium | Degrades quality or usability; fix in a near phase |
| **S4** | Low | Cosmetic or documentation issue |
| **S5** | Info | Observation, no action required yet |

## Status Summary

| Status | Count |
|---|---|
| ✅ Resolved | 1 |
| 🔵 Under Review | 0 |
| ⏳ In Progress | 0 |
| ⏸️ On Hold | 0 |
| 🔷 Planned | 0 |
| 🔴 Open | 0 |
| ⛔ Blocked | 0 |
| 🔶 Needs Decision | 1 |
| 🟣 Monitoring | 0 |
| ⚪ Closed — Wont Fix | 0 |
| **Total** | **2** |

## Priority Resolution Sequence

| Seq | Priority | Issue IDs | Count | Theme |
|---|---|---|---|---|
| 1 | P2 — Medium | KNV-I002 | 1 | Offline CDN policy + default --source (decisions Q2/Q3) |
| 2 | P3 — Low | KNV-I001 | 1 | Repository compliance (resolved) |

## Issue Log Table

| Issue ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
|---|---|---|---|---|---|---|---|---|
| KNV-I001 | 2026-10-01 | Planning | S3 | `knowledge/` repository compliance not established | AGENTS.md §5.10/§6/§5.4 require every project to carry a `knowledge.json`, the ten required folders, and issue/update logs. At inception none existed. | ✅ | T00 | Resolved in T00 (2026-10-01): created the ten required folders (archive/ config/ data/ output/ test/ ui/ engine/ log/ docs/ workplan/), `knowledge/knowledge.json` v0.1.0 declaring canonical name "Knowledge Network Viewer" and abbreviation `knowledge_network`, and `log/issue_log.md` + `log/update_log.md` with the fixed AGENTS.md §5.17 structure. |
| KNV-I002 | 2026-10-01 | Planning | S3 | Offline CDN policy and default `--source` undecided | Q2 (bundle vis-network vs pyvis server mode for true offline use) and Q3 (what `--source` defaults to when omitted) are open design decisions. Until decided, the builder requires an explicit `--source`. The absent shared `config/schemas/knowledge_base_schema.json` (web_tracer I003) means knowledge_network parses structurally and tolerates unknown keys. | 🔶 | Q2, Q3 | Not started. Requires a user/owner decision in Phase 1 (T06 for offline, CLI default in T04). |
