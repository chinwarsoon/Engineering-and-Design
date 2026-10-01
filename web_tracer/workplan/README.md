# Web Application Tracer — Workplan Index

| Field | Value |
|---|---|
| **Project** | Web Application Tracer (abbreviation `web_tracer`) |
| **Date** | 2026-09-30 |
| **Maintained by** | AI assistant, under direction of Song Qinghua |
| **Governance** | AGENTS.md §15 (Workplan Rules), §6 (folder convention), §6.1 (single test root) |

## Master Workplan

| Workplan ID | Title | Status | Revision | Document |
|---|---|---|---|---|
| `WP-WEB-TRACER-001` | Web Application Tracer (Cross-Layer Web Tracing) | ACTIVE DRAFT — pending user approval | r3 | [`web_application_tracing_workplan.md`](web_application_tracing_workplan.md) |

Scope in one line: trace one user action across the browser and (when present) a backend, and show it as one interactive execution tree. Two target profiles: **Case A** cross-layer (`dcc` pipeline UI, served) and **Case B** standalone browser-only HTML (§12.4).

## Phase Reports

Reports are written into this folder at the completion of each phase (`workplan/reports/`).

| Phase | Report | Status |
|---|---|---|
| P0 — Spike | _pending_ | Not started (target re-scoped to `dcc`, two profiles defined §12.4) |
| P1 — Skeleton and contracts | _pending_ | Not started |
| P2 — Browser runtime | _pending_ | Not started |
| P3 — Backend (Python) runtime | _pending_ | Not started |
| P4 — Correlation and execution tree | _pending_ | Not started |
| P5 — Python static analysis | _pending_ | Not started |
| P6 — Web static analysis | _pending_ | Not started |
| P7 — Unified graph and dashboard | _pending_ | Not started |
| P8 — Enhancements | _pending_ | Not started |
| Closeout | _pending_ | Not started |

## Archive

| File | Original revision | Retired on | Reason |
|---|---|---|---|
| [`archive/web_application_tracing_workplan.zh-CN.r0.md`](archive/web_application_tracing_workplan.zh-CN.r0.md) | r0 (Chinese draft, 802 lines) | 2026-09-30 | Superseded by the English master workplan created per AGENTS.md §15. Kept for traceability — task IDs (T01–T61), contract IDs (WT-xx), risk IDs (R1–R12) and question IDs (Q1–Q11) are carried over unchanged |
