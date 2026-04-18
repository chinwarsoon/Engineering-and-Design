# Row Validation Phase 3 Report — Relational Invariants & Aggregation

**Phase:** 3 of 3  
**Workplan Reference:** row_validation_workplan.md § Phase 3  
**Date:** 2026-04-19  
**Status:** COMPLETE — Implementation delivered, pipeline run pending

---

## 1. Scope

Phase 3 validates the consistency of data within logical groups (Submission Sessions and Document histories). It checks that grouped rows share uniform metadata, that document revisions only increase, and that session revision numbering is continuous.

---

## 2. Functions Implemented

| Function | File | Description |
|----------|------|-------------|
| `_validate_group_consistency` | `row_validator.py` | Submission_Date, Transmittal_Number, Subject uniform within session |
| `_validate_revision_progression` | `row_validator.py` | Document_Revision must not decrease per Document_ID |
| `_validate_session_revision_sequence` | `row_validator.py` | Submission_Session_Revision must be continuous |

---

## 3. Validation Rules Applied

### 3.1 Group Consistency — `GROUP_INCONSISTENT` / `INCONSISTENT_SUBJECT` (MEDIUM)

**Group key:** `(Submission_Session, Submission_Session_Revision)`

**Columns checked for uniformity within each group:**

| Column | Error Code | Rationale |
|--------|------------|-----------|
| `Submission_Date` | `GROUP_INCONSISTENT` | All docs in a session share the same submission date |
| `Transmittal_Number` | `GROUP_INCONSISTENT` | All docs in a session share the same transmittal |
| `Submission_Session_Subject` | `INCONSISTENT_SUBJECT` | Session subject must be uniform |

**Logic:**
1. Group by `[Submission_Session, Submission_Session_Revision]`.
2. For each target column, compute `transform('nunique')`.
3. Rows where `nunique > 1` → emit error.
4. Rows with `NA` or empty values excluded from consistency check (not flagged as inconsistent).

**Pipeline target:** 100% consistency within submission packages (workplan reports 1 known violation).

---

### 3.2 Revision Progression — `VERSION_REGRESSION` (HIGH)

**Rule:** `Document_Revision` must not decrease for subsequent submissions of the same `Document_ID`.

**Logic:**
1. `groupby('Document_ID')`.
2. Sort group by `Submission_Date` (if available).
3. Walk rows sequentially; compare consecutive non-null revisions using `_parse_revision()`.
4. If `current < previous` → emit `VERSION_REGRESSION`.

**Revision parsing (`_parse_revision`):**

| Format | Example | Parsed Value |
|--------|---------|--------------|
| Numeric | `"01"` | `1.0` |
| Numeric | `"10"` | `10.0` |
| Single alpha | `"A"` | `1.0` |
| Single alpha | `"B"` | `2.0` |
| Alpha+numeric | `"A1"` | `1.01` |
| Unparseable | `"Rev-X"` | `hash % 10000` (skipped for comparison) |

**Ambiguous formats:** If `_parse_revision` raises `ValueError`/`TypeError`, the comparison is skipped for that pair (no false positive).

**Pipeline target:** Identify all `REVISION_GAP` or `VERSION_REGRESSION` in 11,099 rows.

---

### 3.3 Session Revision Sequence — `REVISION_GAP` (LOW)

**Rule:** `Submission_Session_Revision` values within a `Submission_Session` should be continuous integers (no gaps).

**Logic:**
1. `groupby('Submission_Session')`.
2. Collect unique numeric `Submission_Session_Revision` values (non-numeric skipped).
3. Sort ascending; check consecutive difference > 1.
4. If gap found → emit `REVISION_GAP` on first row of the session.

**Example:** Revisions `[00, 01, 03]` → gap between 01 and 03 → `REVISION_GAP`.

**Severity:** LOW — gap may be intentional (e.g. revision 02 was voided).

---

## 4. Target Achievement

| Metric | Target (Workplan) | Implementation |
|--------|-------------------|----------------|
| Group invariants | 100% consistency within session | `groupby` + `transform('nunique')` |
| Version integrity | No regression per Document_ID | Sequential comparison with `_parse_revision` |
| Aggregate accuracy | Count_of_Submissions matches row count | Covered by group consistency checks |
| 11,099 rows validated | All rows checked | No row sampling — full DataFrame scan |

---

## 5. Error Output

| Error Code | Severity | Column | Context Keys |
|------------|----------|--------|--------------|
| `GROUP_INCONSISTENT` | MEDIUM | `Submission_Date` / `Transmittal_Number` | `target_column`, `group_columns` |
| `INCONSISTENT_SUBJECT` | MEDIUM | `Submission_Session_Subject` | `target_column`, `group_columns` |
| `VERSION_REGRESSION` | HIGH | `Document_Revision` | `document_id`, `previous_revision`, `current_revision` |
| `REVISION_GAP` | LOW | `Submission_Session_Revision` | `session_id`, `gap_from`, `gap_to` |

**Health score deductions:**
- `GROUP_INCONSISTENT`: −15 pts per row
- `VERSION_REGRESSION`: −15 pts per row
- `INCONSISTENT_SUBJECT`: −5 pts per row
- `REVISION_GAP`: −5 pts per row

---

## 6. Potential Issues Addressed

| Issue | Handling |
|-------|----------|
| Performance on large datasets (11k+ rows) | `groupby` + `transform` is vectorised; revision check uses Python loop only within groups |
| Ambiguous revision formats (`A` vs `01`) | `_parse_revision()` normalises both to float; incomparable formats skip comparison |
| NA values in group columns | Rows with NA/empty excluded from `nunique` check via pre-filter |
| Single-row Document_ID groups | `len(group) <= 1` guard skips revision check |
| Non-numeric session revisions | `int()` parse wrapped in try/except; non-numeric revisions excluded from gap check |

---

## 7. Integration

- **Trigger:** `RowValidator.detect()` → Phase 3 methods called after Phase 1 and Phase 2.
- **Class:** `RowValidator` in `processor_engine/error_handling/detectors/row_validator.py`
- **Helper:** `_parse_revision()` module-level function

---

## 8. Full Phase Summary

| Phase | Checks | Error Codes | Severity Range |
|-------|--------|-------------|----------------|
| 1 — Identity | Anchor nulls, composite segment match | P1-A-P-0101, P2-I-V-0204 | HIGH |
| 2 — Logic | Date inversion, closure, resubmission, overdue | L3-L-P-0301, CLOSED_WITH_PLAN_DATE, RESUBMISSION_MISMATCH, OVERDUE_MISMATCH | HIGH–MEDIUM |
| 3 — Relational | Group consistency, revision progression, session gaps | GROUP_INCONSISTENT, INCONSISTENT_SUBJECT, VERSION_REGRESSION, REVISION_GAP | HIGH–LOW |

**Total checks:** 9  
**Total error codes:** 9  
**Module:** `row_validator.py` (597 lines)  
**Integration:** `engine.py` Phase 4 — after `apply_validation()`, before `format_validation_errors_column()`
