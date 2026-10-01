# Issue Log

| Field | Value |
|---|---|
| **Project** | Web Application Tracer (abbreviation `web_tracer`) |
| **Location** | `web_tracer/log/issue_log.md` |
| **Last Updated** | 2026-09-30 |
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
| ✅ Resolved | 2 |
| 🔵 Under Review | 0 |
| ⏳ In Progress | 0 |
| ⏸️ On Hold | 0 |
| 🔷 Planned | 0 |
| 🔴 Open | 0 |
| ⛔ Blocked | 1 |
| 🔶 Needs Decision | 0 |
| 🟣 Monitoring | 0 |
| ⚪ Closed — Wont Fix | 0 |
| **Total** | **3** |

## Priority Resolution Sequence

| Seq | Priority | Issue IDs | Count | Theme |
|---|---|---|---|---|
| 1 | P2 — Medium | I003 | 1 | Shared schema infrastructure referenced but absent (blocked) |
| 2 | P3 — Low | I001 | 1 | Documentation compliance (resolved) |

## Issue Log Table

| Issue ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
|---|---|---|---|---|---|---|---|---|
| I001 | 2026-09-30 | Planning | S3 | Workplan did not meet AGENTS.md structure and language requirements | The r0 workplan was written in Chinese and lacked the AGENTS.md §15 mandatory sections: Object, Scope Summary with per-item ID and status, Index of Content, Dependencies, Evaluation and Alignment, and per-phase Risks and Mitigation plus Success Criteria. It was also hard for a non-specialist user to read. | ✅ | U001, U002, U003 | Resolved by creating the English master workplan `workplan/web_application_tracing_workplan.md` r1 with the full §15 structure plus a beginner glossary. The Chinese draft was archived as `workplan/archive/web_application_tracing_workplan.zh-CN.r0.md` with a RETIRED banner, keeping all task, contract, risk and question IDs unchanged. |
| I002 | 2026-09-30 | Planning | S2 | `web_tracer/knowledge.json` is missing | AGENTS.md §5.10 requires every project to carry a `knowledge.json` at its root, declaring the canonical project name and abbreviation in `project_metadata.name`, plus architecture overview and known issues. The file does not exist, so the project is currently non-compliant. Note: the shared schema referenced by AGENTS.md §2.4 is also absent — see I003. | ✅ | T00 | Resolved in T00 (2026-09-30): `web_tracer/knowledge.json` created (v0.1.0) declaring canonical name "Web Application Tracer" and abbreviation `web_tracer`, with the full AGENTS.md §2.4 structure (project_metadata, architecture_overview, domain_concepts, key_schemas, workflows, functions, data_flows, dependencies, known_issues). The shared `config/schemas/knowledge_base_schema.json` (AGENTS.md §2.4) is still absent (I003, blocked), so knowledge.json was built to the documented field contract and will be re-validated once I003 closes. All ten required folders created (config/ data/ docs/ output/ test/ ui/ engine/ added; archive/ log/ workplan/ pre-existed). |
| I003 | 2026-09-30 | Planning | S3 | `config/schemas/knowledge_base_schema.json` does not exist | AGENTS.md §2.4 states the knowledge-base schema is defined in `config/schemas/knowledge_base_schema.json` at the repository root. A repository-wide search returned zero matches, so no shared schema is available to validate `knowledge.json` against. | ⛔ | — | Blocked on a repository owner decision: either create the shared schema under `config/schemas/`, or correct the AGENTS.md reference to point at the real location. No schema content was invented in the meantime. |
