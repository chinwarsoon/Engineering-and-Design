# Issue Lifecycle Management Proposal

**Document ID**: WP-EKS-P1-PROP-001
**Version**: 0.3
**Last Updated**: 2026-07-22
**Status**: 🔷 DRAFT — For Review
**Author**: CodeBuddy

---

## Contents

- [1. Objective](#1-objective)
- [2. Problem Analysis](#2-problem-analysis)
- [3. Proposed 5-Stage Lifecycle](#3-proposed-5-stage-lifecycle)
- [4. Changes to Existing Artifacts](#4-changes-to-existing-artifacts)
- [5. Cross-Reference Integrity Rules](#5-cross-reference-integrity-rules)
- [6. Examples — Current vs Proposed](#6-examples--current-vs-proposed)
- [7. Implementation Plan](#7-implementation-plan)

---

## 1. Objective

Define a management cycle for issues that makes every stage explicit and auditable — from discovery through task approval, implementation, verification, and workplan alignment — without adding bureaucratic overhead to the existing workflow.

The 5-stage workflow is:

```
Record & Evaluate → Plan & Approve → Implement & Update → Test & Verify → Close & Align
```

---

## 2. Problem Analysis

### 2.1 Six Gaps in the Current System

| # | Gap | Evidence | Impact |
|---|-----|----------|--------|
| G1 | **No approval gate** between task planning and implementation | `update_log.md` shows U171 (I114 — tasks proposed for review) → U173 (I114 resolved, same tasks). No record of who approved or when. | Ambiguity: was the approval implicit, or were tasks self-approved during implementation? |
| G2 | **No per-issue closure criteria** — what "done" means is implicit | Issue Resolution column is freeform text. No checklist proving every aspect of an issue was verified. Example I028: `Resolved | Removed metadata fields from both config files (U077). All 114 tests pass.` — What exactly was checked? | Cannot prove issue is fully resolved without reading every linked task + test |
| G3 | **No workplan alignment record** on issue closure | Issue I114 → Resolved in U173. Workplan went from v3.84→v3.85 in the same update. But there is no field or convention marking "workplan aligned" separately from "issue resolved". | Cannot distinguish "code fixed but docs pending" from "fully closed" |
| G4 | **Issue → Checklist link missing** | Appendix P1.5 has 89 success criteria referencing `(T1.xx)` task IDs, but no criteria reference an Ixxx issue ID directly. | Can't grep "which checklist criteria prove issue I028 is closed?" |
| G5 | **No structured resolution format** | Resolution column mixes freeform narrative, Uxxx refs, Txxx refs, and test counts inconsistently. Hard to parse programmatically. | grep-based audit cannot reliably extract linked updates, tasks, or tests |
| G6 | **Task table `Tests` column underpopulated** | ~40+ tasks in §2–§11 show `—` for Tests despite being implemented. No policy requiring populating it for non-Docs tasks. | Traceability chain broken; cannot verify which tests prove a task complete |

### 2.2 What Works Well (preserve these)

- **Bidirectional issue↔task links**: Issues reference `T{phase}.{seq}`, tasks reference `I{xxx}`. This is solid.
- **Issue→update links**: Nearly every resolved issue references the closing `U{xxx}`. Consistent.
- **Update→task links**: Every update entry references the task IDs it implements. Consistent.
- **Status summary in issue_log**: Counts by status; refreshed on every edit. Good practice.
- **Priority Resolution Sequence table**: Orders outstanding issues by urgency. Effective triage tool.

### 2.3 Design Constraints

- No breaking changes to existing file formats (AGENTS.md §5.17 protects issue_log structure)
- Changes must be greppable and manually verifiable
- Must work with existing tooling (no scripts required for daily use)
- Must integrate with the 12-column task table format already in place
- Must respect the I190 precedent — no full-file rewrites of issue_log

---

## 3. Proposed 5-Stage Lifecycle

### 3.1 The Five Stages

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  ① RECORD &      ② PLAN &         ③ IMPLEMENT &    ④ TEST &         ⑤ CLOSE &       │
│     EVALUATE        APPROVE           UPDATE            VERIFY           ALIGN          │
│                                                                        │
│  Log issue       Define tasks      Code changes     Run tests        Close issue     │
│  Set severity    Link to issue     Log in           Document         Update          │
│  Assign phase    Get approval       update_log       results in        workplan        │
│                                   Write closure     test_log           revision        │
│                                   criteria                             history        │
└────────────────────────────────────────────────────────────────────────┘
     │                  │                  │                  │                  │
     ▼                  ▼                  ▼                  ▼                  ▼
  Artifact:          Artifact:          Artifact:          Artifact:          Artifact:
  issue_log.md       Task table         update_log.md      test_log.md        workplan
  (🔴 OPEN)          (🔷 PLANNED)       (Uxxx entry)       (TLxxx entry)      (P1.6 entry)
```

### 3.2 Stage Entry and Exit Criteria

| Stage | Entry | Exit | Artifacts Produced |
|-------|-------|------|--------------------|
| **① RECORD & EVALUATE** | Problem discovered | Severity, priority, and phase assigned | issue_log entry with `🔴 Open`, severity marker, phase column |
| **② PLAN & APPROVE** | Issue triaged | Tasks approved for implementation | One or more task rows with `Issues: Ixxx`; status `🔷 PLANNED`; approval note in issue Resolution column |
| **③ IMPLEMENT & UPDATE** | Tasks approved | All tasks marked `✅ COMPLETE`; update_log entry written | update_log entry `Uxxx` with `Task: T{phase}.{seq}` and `Status: ✅ Done` |
| **④ TEST & VERIFY** | Implementation complete | Test results documented; closure criteria met | test_log entry `TLxxx`; all closure criteria in issue matched against task table `Tests` column |
| **⑤ CLOSE & ALIGN** | Verification passed | Issue closed with full cross-refs; workplan updated | issue_log `✅ Resolved` with `Tasks` column populated and structured `Resolution` field; workplan revision updated |

### 3.3 Approval Gate (Stage ②→③)

When tasks are defined but not yet approved, the task table status is `🔷 PLANNED`. After review and approval:

- **Approved**: A note is added to the issue's `Resolution` field (provisional): `Approved: YYYY-MM-DD by {author}` and issue status changes to `🟢 Approved`. Task rows remain `🔷 PLANNED` until implementation begins.
- **Deferred**: Issue moved to `⏸️ Deferred` with reason.
- **Rejected**: Issue moved to `⛔ Won't Implement` with rationale.

---

## 4. Changes to Existing Artifacts

### 4.1 issue_log.md — New Tasks Column

The 8-column issue log table gains one column — `Tasks` — inserted between `Status` and `Resolution`:

**Current (8 columns):**

```
| ID | Date | Phase | Severity | Title | Description | Status | Resolution |
```

**Proposed (9 columns):**

```
| ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
```

The `Tasks` column holds the task ID(s) that implement this issue (e.g. `T1.99.31` or `T1.21/T1.22` or `T1.99.75–80`). Multiple tasks are separated by `/` or `–`. This column is the primary link to the [task log](../log/phase1/p1_task_log.md).

**Why a dedicated Tasks column?** Task IDs are the most frequently cross-referenced identifier — every resolved issue maps to at least one task. Storing them in a dedicated column makes the issue↔task link explicit, filterable, and sortable. This is where manual review will focus most.

**Migration**: For existing resolved issues, extract `T{phase}.{seq}` references from the Resolution text and populate the new Tasks column. Old format remains valid — tasks can be left empty for backward compatibility.

### 4.2 issue_log.md — Resolution Column Format

**Current**: Freeform text.

**Proposed**: Structured format with labeled segments separated by ` — ` (space-emdash-space):

```
Updates: Uxxx — Tests: TLxxx — Close: {summary} — Workplan: {filename} vX→vY — Approved: date by author
```

Note that `Tasks:` is **not** part of Resolution — it now has its own column.

| Segment | Purpose | Required? |
|---------|---------|:---------:|
| `Updates:` | Update log entry IDs (Uxxx) | Recommended for ✅/📐 |
| `Tests:` | Test log entry IDs (TLxxx) | Optional |
| `Close:` | 1-line human-readable summary | Optional |
| `Workplan:` | Workplan file name + version change e.g. `phase_1_foundation_workplan.md v3.71→v3.72` | Recommended for 📐 |
| `Approved:` | Who approved and when | Recommended for 🟢/✅ |

### 4.3 issue_log.md — New Status: 📐 Aligned

The current `✅ Resolved` conflates "code fixed" with "workplan updated". Add `📐 Aligned` as a distinct status:

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| 📐 | Aligned | Issue resolved AND workplan/docs updated to reflect the change |

This is a **superset** of ✅ Resolved — every 📐 Aligned issue was first ✅ Resolved, then had its workplan alignment step completed.

Example transition:
```
1. Issue implemented → ✅ Resolved  (but docs may be stale)
2. Workplan updated → 📐 Aligned   (fully closed)
```

Not all issues need the 📐 step — only those that change the pipeline architecture, task registry, or config schemas. Cosmetic fixes and minor patches can close at ✅ Resolved.

**Transition rule**: Changing an issue from ✅ to 📐 requires a new update_log entry (Uxxx) documenting which workplan files were updated.

### 4.4 issue_log.md — New Status: 🟢 Approved

Between planning and implementation, there is currently no recorded state. Add `🟢 Approved`:

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| 🟢 | Approved | Tasks defined and approved; awaiting implementation |

This is the visible output of the approval gate (§3.3). An issue moves from `🔷 PLANNED` to `🟢 Approved` when its tasks are reviewed and approved, then to `✅ Resolved` or `📐 Aligned` when implementation is complete.

### 4.5 issue_log.md — Legend Update

Add four new rows to the Status legend:

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| 📐 | Aligned | Issue resolved AND workplan/docs updated to reflect the change |
| 🟢 | Approved | Tasks defined and approved; awaiting implementation |

### 4.6 issue_log.md — Status Summary Enhancement

Add rows for the two new lifecycle markers:

| Status | Marker | Count |
|--------|:------:|------:|
| Aligned | 📐 | N |
| Approved (pending impl) | 🟢 | N |

The `📐 Aligned` row tracks workplan alignment completeness. The `🟢 Approved` row tracks issues whose tasks are approved but not yet implemented.

### 4.7 Task Table — Policy for `Tests` Column

Make the `Tests` column mandatory for code-level tasks:

| Task category | Tests column policy |
|:--------------|:--------------------|
| `[Code]` | Required — at least one `TLxxx` |
| `[Schema]` | Required — at least one `TLxxx` |
| `[Fix]` | Required — at least one `TLxxx` |
| `[Config]` | Recommended |
| `[Testing]` | Required — self-referencing (`TLxxx` for the test file itself) |
| `[Docs]` | Optional — `—` is acceptable |
| `[Cleanup]` | Optional — `—` is acceptable |
| `[Init]` | Optional — `—` is acceptable |

This is a **policy rule**, not a column change. Existing entries with `—` in [Code]/[Schema]/[Fix] categories should be backfilled.

### 4.8 Closure Criteria — Lightweight per-Issue Checklist

Each issue implicitly defines its own "definition of done" through:
1. The tasks linked to it (all must be ✅ COMPLETE)
2. The tests linked to those tasks (all must pass)
3. Optional: specific criteria documented in the issue description or resolution

Rather than creating a new Cxxx ID system (too complex), we can make the implicit explicit by adding a structured checklist inside the issue's **Description** column:

**Current** (I100):
```
I100 | Phase 1 | 🟡 Medium | EKS suite config drift | During I099 / L18 implementation... | ✅ Resolved | Root cause was a config-resolution bug...
```

**Proposed** — Description adopts a trailing checklist format:
```
| I100 | Phase 1 | 🟡 Medium | EKS suite config drift | During I099 / L18 implementation. [x] Fix _schema_config_candidates search path — Done T1.99.31 [x] Add 2 regression tests — Done TL003 [x] Verify 277/277 green — Result: all pass [x] Update workplan v3.71→v3.72 — Done U160 | 📐 Aligned | T1.99.31 | Updates: U160 — Tests: TL003 — Close: config-resolution bug fixed, 15 pre-existing failures restored to green — Workplan: phase_1_foundation_workplan.md v3.71→v3.72 — Approved: 2026-07-15 by opencode |
```

The checklist is `[ ]` or `[x]` inside the Description, after the narrative text, on the same or following line. This is **optional** — only needed for complex issues where closure criteria are not obvious from the task list alone.

---

## 5. Cross-Reference Integrity Rules

Five lightweight rules — not a formal state machine, just grep-able assertions.

### Rule 1 — Resolved Issue Completeness

```
Every Ixxx marked ✅ Resolved or 📐 Aligned must have:
  ☐ Tasks column references at least one T{phase}.{seq}
  ☐ Resolution references at least one U{xxx}
  ☐ All referenced T{phase}.{seq} exist in the task table
  ☐ All referenced U{xxx} exist in update_log.md
```

### Rule 2 — Task Test Coverage

```
Every T{phase}.{seq} with category [Code], [Schema], [Fix], or [Testing] and status ✅ COMPLETE:
  ☐ Must have Tests != "—" (at least one TLxxx)
  ☐ Referenced TLxxx must exist in test_log.md
```

### Rule 3 — Update Log Consistency

```
Every Uxxx marked ✅ Done:
  ☐ Must reference at least one Ixxx in the Task column
  ☐ Must reference at least one T{phase}.{seq} in the Task column
```

### Rule 4 — Approval Gate

```
Every issue transitioning from 🔷 PLANNED to implementation (⏳ or ✅):
  ☐ Resolution should contain "Approved: {date} by {author}"
```

This is a recommended convention, not a mandatory gate.

### Rule 5 — Workplan Alignment

```
Every issue that changes pipeline architecture, task tables, or config schemas:
  ☐ Should transition from ✅ Resolved to 📐 Aligned after workplan is updated
  ☐ Resolution must reference the workplan file name and version change:
     "Workplan: {filename} vX→vY"
```

---

## 6. Examples — Current vs Proposed

All examples show the **full issue log row** using the 9-column proposed format.

### 6.1 Simple Issue (I001)

**Current**:
```
| I001 | 2026-06-15 | Phase 1 | 🟠 High | Missing __init__.py files in engine packages | engine/__init__.py... | ✅ Resolved | Created 4 __init__.py files with import statements and version info (U011) |
```

**Proposed**:
```
| I001 | 2026-06-15 | Phase 1 | 🟠 High | Missing __init__.py files in engine packages | engine/__init__.py... | ✅ Resolved | T1.1 | Updates: U011 — Close: init files created in all 4 engine packages — Approved: 2026-06-15 by System |
```

### 6.2 Complex Issue (I100 — config drift fix, 15 tests restored)

**Current**:
```
| I100 | 2026-07-15 | Phase 1 | 🟡 Medium | EKS suite config drift — missing project_setup config section causes 15 pre-existing test failures | During I099 / L18 implementation, the full EKS suite showed 15 failures... | ✅ Resolved | Root cause was a config-resolution bug... 277/277 green. U160. |
```

**Proposed**:
```
| I100 | 2026-07-15 | Phase 1 | 🟡 Medium | EKS suite config drift — missing project_setup config section causes 15 pre-existing test failures | During I099 / L18 implementation, the full EKS suite showed 15 failures. [x] Fix _schema_config_candidates search path — Done T1.99.31 [x] Add 2 regression tests — Done TL003 [x] Verify 277/277 green — Result: all pass [x] Update workplan v3.71→v3.72 — Done U160 | 📐 Aligned | T1.99.31 | Updates: U160 — Tests: TL003 — Close: config-resolution bug fixed, 15 pre-existing failures restored to green — Workplan: phase_1_foundation_workplan.md v3.71→v3.72 — Approved: 2026-07-15 by opencode |
```

### 6.3 Issue with Approval Gate (I114 — env check)

**Current**:
```
| I114 | 2026-07-17 | Phase 1 | 🟠 High | No environment/dependency check in EKS bootstrap | Two-pronged gap: (A)... (B)... | ✅ Resolved | T1.99.75–80 implemented. See §30.5.2 v3.84. |
```

**Proposed**:
```
| I114 | 2026-07-17 | Phase 1 | 🟠 High | No environment/dependency check in EKS bootstrap | Two-pronged gap: (A)... (B)... [x] Create test_environment() in common/library — Done U179 [x] Add env_tester hook to BootstrapManager — Done U179 [x] Wire EKS _bootstrap_env() — Done U179 [x] Register P1-BOOT-ENV in error config — Done U179 [x] Lazy-import refactor in main() — Done U179 [x] Verify all 6 tasks pass — TL003: 17/29 (12 expected failures) [x] Update workplan v3.82→v3.85 — Done U173 | 📐 Aligned | T1.99.75–80 | Updates: U170 (proposed), U171 (redesign), U173 (impl) — Tests: TL003 — Close: universal test_environment in L20, env_tester hook in BootstrapManager, EKS wiring, P1-BOOT-ENV registered, lazy-import refactor — Workplan: phase_1_foundation_workplan.md v3.82→v3.84→v3.85 — Approved: 2026-07-17 by opencode |
```

---

## 7. Implementation Plan

### Phase A — Tasks Column + Resolution Format (estimated: 2 edit cycles)

1. **Add Tasks column** to issue_log table header: `| ... | Status | Tasks | Resolution |`
2. Define the structured Resolution format in a comment near the Issue Log Table
3. Update issue_log.md legend: add `📐 Aligned` and `🟢 Approved` status definitions
4. Update Status Summary: add `📐` and `🟢` rows
5. Migrate 10–20 recently resolved issues (I100–I233) to the new 9-column format as examples
6. Leave earlier issues (I001–I099) in old 8-column format — no blanket rewrite per I190 precedent

### Phase B — Approval Gate Implementation (estimated: 1 edit cycle)

1. Identify all issues with 🔷 Planned tasks that are now ✅ Resolved but have no approval record
2. Add `Approved: {date} by {author}` to their Resolution fields, inferred from update_log timestamps
3. For current open issues with planned tasks, ensure approval is recorded before implementation starts

### Phase C — Task Table Test Coverage Backfill (estimated: 2 edit cycles)

1. Identify all [Code], [Schema], [Fix] tasks in the [task log](../log/phase1/p1_task_log.md) with `Tests: —` and status ✅ COMPLETE
2. For each, determine which TLxxx applies (TL001–TL004) or add a note if no test exists
3. Backfill the Tests column

### Phase D — Workplan Alignment Tracking (estimated: 1 edit cycle)

1. For recently resolved issues that changed architecture or schemas, transition from ✅ to 📐
2. Add `Workplan: {filename} vX→vY` to their Resolution fields
3. Document the 📐→✅ transition convention in AGENTS.md or a workplan appendix

### Phase E — Validation Script (estimated: 1 edit cycle)

1. Create `eks/test/verify_lifecycle_integrity.py` — a grep-based checker for Rules 1–3
2. Run against current state; document violations
3. Add as a pre-close gate for Phase 1 completion

---

## Summary of Changes

| Artifact | Change | Breaking? |
|----------|--------|-----------|
| `issue_log.md` table | **+1 column**: `Tasks` inserted between `Status` and `Resolution` | Yes — requires header + data migration for rows migrated to new format |
| `issue_log.md` Legend | Add `📐 Aligned`, `🟢 Approved` status definitions | No — additive |
| `issue_log.md` Status Summary | Add `📐`, `🟢` count rows | No — additive |
| `issue_log.md` Resolution column | Structured format with ` — ` segments; `Workplan:` includes filename | No — backward-compat freeform |
| `issue_log.md` Description column | Optional checklist `[ ]` items for complex issues | No — additive |
| `p1_task_log.md` Tests column | Backfill missing values | No — data fill, no structural change |
| `eks/test/verify_lifecycle_integrity.py` | New file | New — additive |
| `update_log.md` | No change | — |
| `test_log.md` | No change | — |
| `appendix_p1.5` checklists | No change (optional future: add Ixxx refs) | — |
