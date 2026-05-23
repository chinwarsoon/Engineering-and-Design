# Workplan: Upgrade Condense Workplans Script

**Document ID:** WP-MAINT-CONDENSE-001  
**Version:** 1.1  
**Status:** ✅ COMPLETE  
**Last Updated:** 2026-05-23  
**Lead:** Gemini CLI

---

## 1. Objective
The objective of this workplan is to upgrade the `condense_workplans.py` script to ensure it processes all Markdown files within the `dcc/workplan/` directory and outputs the condensed knowledge base to the `dcc/output/` directory. This will improve project-wide visibility and traceability by centralizing workplan knowledge.

---

## 2. Scope Summary

| ID | Detail | Category | Status | Related Phase |
| :--- | :--- | :--- | :--- | :--- |
| S1 | Expand file discovery to include all `.md` files in `dcc/workplan/` | Data Extraction | ✅ COMPLETE | Phase 2 |
| S2 | Update output destination to `dcc/output/workplan_knowledge.md` | Configuration | ✅ COMPLETE | Phase 2 |
| S3 | Implement robust metadata extraction for non-workplan documents | Data Processing | ✅ COMPLETE | Phase 2 |
| S4 | Validate generated output for completeness and accuracy | Testing | ✅ COMPLETE | Phase 3 |
| S5 | Move script to `dcc/workplan/maintenance/` | Organization | ✅ COMPLETE | Phase 2 |
| S6 | Log updates and generate phase reports | Documentation | ✅ COMPLETE | Phase 4 |

---

## 3. Index of Content
1. [Objective](#1-objective)
2. [Scope Summary](#2-scope-summary)
3. [Dependencies & Alignment](#4-dependencies--alignment)
4. [Implementation Phases](#5-implementation-phases)
   - [Phase 1: Research & Analysis](#phase-1-research--analysis)
   - [Phase 2: Relocation & Script Implementation](#phase-2-relocation--script-implementation)
   - [Phase 3: Testing & Verification](#phase-3-testing--verification)
   - [Phase 4: Logging & Reporting](#phase-4-logging--reporting)
5. [Success Criteria](#6-success-criteria)
6. [Risks & Mitigation](#7-risks--mitigation)

---

## 4. Dependencies & Alignment

### Dependencies
- **Source Data:** All `.md` files under `dcc/workplan/`.
- **Target Folder:** `dcc/output/` must exist and be writable.
- **Relocation Path:** `dcc/workplan/maintenance/` must be the final home for the script.

### Architecture Alignment
- Follows `agent_rule.md` Section 8 (Workplan) and Section 4 (Module Design).
- Ensures Single Source of Truth (SSOT) for workplan knowledge by centralizing it in `dcc/output/`.
- Adheres to standard DCC project directory structure by placing maintenance scripts in the `maintenance` folder.

---

## 5. Implementation Phases

### Phase 1: Research & Analysis
**Timeline:** Day 1  
**Milestone:** Completion of script logic audit.  
**Deliverables:** List of target file variations and metadata patterns.

- [x] Analyze current `find_targets()` logic in `condense_workplans.py`.
- [x] Identify all `.md` files in `dcc/workplan/` that are currently excluded.
- [x] Determine if additional metadata extraction patterns are needed for non-workplan files (e.g., design rules, logic references).

### Phase 2: Relocation & Script Implementation
**Timeline:** Day 1  
**Milestone:** Script relocated, updated, and functional.  
**Deliverables:** Updated `dcc/workplan/maintenance/condense_workplans.py`.

- [x] Move `dcc/workplan/condense_workplans.py` to `dcc/workplan/maintenance/`.
- [x] Modify `find_targets()` to include all files in `WORKPLAN_DIR` (parent of `maintenance/`) with `.md` extension, while still respecting critical exclusions (like `__pycache__`).
- [x] Update `OUTPUT_FILE` path to `ROOT / "output" / "workplan_knowledge.md"`.
- [x] Refine `extract_meta` and `format_workplan` functions to handle diverse document types gracefully.
- [x] Add standardized docstrings and breadcrumb comments (per `agent_rule.md` Section 5).

### Phase 3: Testing & Verification
**Timeline:** Day 1  
**Milestone:** Successful execution and validation.  
**Deliverables:** Verified `dcc/output/workplan_knowledge.md`.

- [x] Execute the updated script.
- [x] Verify the existence of the output file in `dcc/output/`.
- [x] Manually inspect the content to ensure all expected documents are included.
- [x] Check for duplicate or missing entries.

### Phase 4: Logging & Reporting
**Timeline:** Day 1  
**Milestone:** Logs and reports updated.  
**Deliverables:** Phase reports and log entries.

- [x] Generate phase reports in `dcc/workplan/maintenance/reports/`.
- [x] Update `dcc/log/issue_log.md` with any identified issues.
- [x] Update `dcc/log/update_log.md` with the changes made to the script.
- [x] Update `dcc/log/test_log.md` with verification results.

---

## 6. Success Criteria
- [x] Script successfully processes all 160+ files in `dcc/workplan/`.
- [x] Output file `workplan_knowledge.md` is generated in `dcc/output/`.
- [x] Output file contains accurate metadata for all processed documents.
- [x] All log files (`issue_log.md`, `update_log.md`, `test_log.md`) are updated per project rules.

---

## 7. Risks & Mitigation
| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| Large output file size | May exceed context limits for LLM | Medium | Implement truncation or focus on key metadata only. |
| Inconsistent metadata formats | Incomplete information in the condensed file | High | Use flexible regex patterns and provide sensible defaults for missing fields. |
| Permission issues in `dcc/output` | Script failure | Low | Ensure directory existence and write permissions before writing. |

---

## 8. References
- `agent_rule.md`
- `dcc/workplan/maintenance/condense_workplans.py`
- `dcc/workplan/README.md`
