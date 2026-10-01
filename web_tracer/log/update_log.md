# Update Log

| Field | Value |
|---|---|
| **Project** | Web Application Tracer (abbreviation `web_tracer`) |
| **Location** | `web_tracer/log/update_log.md` |
| **Last Updated** | 2026-09-30 |
| **Governance** | AGENTS.md §5.4 (log everything), §5.7 (revision metadata) |

## Update Table

| Update ID | Date | Phase | Change | Files | Author |
|---|---|---|---|---|---|
| U001 | 2026-09-30 | Planning | Created the English master workplan `WP-WEB-TRACER-001` r1 per AGENTS.md §15 (title/description, object, scope summary, index, glossary for beginners, dependencies, evaluation and alignment, architecture with Mermaid, repository compliance, 10 phases with all eight elements each, task table T00–T61, decisions, risks, gates, testing, logs, revision history) | `workplan/web_application_tracing_workplan.md` | AI assistant |
| U002 | 2026-09-30 | Planning | Retired the Chinese draft r0 to `workplan/archive/` with a RETIRED banner; task / contract / risk / question IDs carried over unchanged | `workplan/archive/web_application_tracing_workplan.zh-CN.r0.md` | AI assistant |
| U003 | 2026-09-30 | Planning | Created the workplan index with master-workplan table, phase-report placeholders and archive table | `workplan/README.md` | AI assistant |
| U004 | 2026-09-30 | Planning | Baseline changed: no `ref/` copy folder; `../code_tracer/` is now a read-only reference, reused files are copied one file at a time. Reason: `code_tracer/engine/` holds about 41 740 files (front-end dependencies), so a full copy is impractical | `workplan/web_application_tracing_workplan.md` §7.2 | AI assistant |
| U005 | 2026-09-30 | Planning | Recorded decisions Q1–Q4: Spring AOP aspect with strategy abstraction kept; target application is the user's existing business system; native Linux; JDK 17 + Maven | `workplan/web_application_tracing_workplan.md` §12.1 | Song Qinghua / AI assistant |
| U006 | 2026-09-30 | Planning | Created `log/issue_log.md` with the fixed AGENTS.md §5.17 structure and logged I001–I003 | `log/issue_log.md` | AI assistant |
| U007 | 2026-09-30 | Planning | Corrected the UI approach to AGENTS.md §18: shared `common/universal_ui_design.css` + `.js` as base layer, project CSS as override only (the retired draft had copied `code-tracer.css` wholesale) | `workplan/web_application_tracing_workplan.md` §9.5 | AI assistant |
| U008 | 2026-09-30 | Planning | Added compliance task T00 (folders, `knowledge.json`, logs) as the first Phase 1 task | `workplan/web_application_tracing_workplan.md` §11 | AI assistant |
| U009 | 2026-09-30 | Planning | Added §8.3.4 "Webpage Graph Model" to the master workplan: beginner guide to webpage node/edge definitions, `JsFunction` dataclass, `web_static_graph.json` shape, endpoint matching to Java, and a worked example JSON | `workplan/web_application_tracing_workplan.md` §8.3.4 | AI assistant |
| U010 | 2026-09-30 | Planning | Re-targeted the workplan to `dcc` (Python 3.13, not Java): Q1 → OTel Python SDK + `@traced`; Q4 → Python 3.13 + OTel; Q2 intake resolved for `dcc`; added §12.4 two target profiles (Case A cross-layer `dcc` pipeline served, Case B standalone browser-only HTML); Phase 5 tree-sitter-java → tree-sitter-python / `python_call_graph.json`; Phase 0 gate and T12 updated for the two cases; dependency/architecture/README refreshed | `workplan/web_application_tracing_workplan.md` §12, §14, S-05, T12/T41/T43; `workplan/README.md`; `log/update_log.md` | AI assistant |
| U011 | 2026-09-30 | P1 | Completed T00 repository compliance: created the 7 missing required folders (config/ data/ docs/ output/ test/ ui/ engine/) with .gitkeep scaffolding; created `web_tracer/knowledge.json` (v0.1.0) declaring canonical name "Web Application Tracer" and abbreviation `web_tracer` with the full AGENTS.md §2.4 structure; I002 resolved; I003 remains blocked (shared schema absent) so knowledge.json was built to the documented AGENTS.md §2.4 field contract | `knowledge.json`, `config/ data/ docs/ output/ test/ ui/ engine/` | AI assistant |
