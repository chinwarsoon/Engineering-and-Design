# Row Validation Phase 1 Report — Anchor & Composite Identity

**Phase:** 1 of 3  
**Workplan Reference:** row_validation_workplan.md § Phase 1  
**Date:** 2026-04-19  
**Status:** COMPLETE — Implementation delivered, pipeline run pending

---

## 1. Scope

Phase 1 validates the fundamental identity of each row: anchor columns must not be null, and the composite `Document_ID` must exactly match its 5 constituent fields.

---

## 2. Functions Implemented

| Function | File | Description |
|----------|------|-------------|
| `_validate_anchor_completeness` | `row_validator.py` | Null check on 5 anchor columns |
| `_validate_composite_identity` | `row_validator.py` | Document_ID segment match (affix-aware) |

---

## 3. Validation Rules Applied

### 3.1 Anchor Completeness — `P1-A-P-0101` (HIGH)

Columns checked (must not be null or empty):

| # | Column | Null Handling Strategy |
|---|--------|----------------------|
| 1 | `Document_ID` | composite calc |
| 2 | `Project_Code` | default: "NA" |
| 3 | `Document_Type` | default: "NA" |
| 4 | `Submission_Date` | required |
| 5 | `Document_Sequence_Number` | zero_pad: 4 |

**Logic:** For each anchor column, a null/empty mask is applied across all rows. Each failing row emits one `P1-A-P-0101` error with `error_key=ANCHOR_NULL`.

### 3.2 Composite Identity — `P2-I-V-0204` (HIGH)

**Expected pattern:**
```
Document_ID = {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}
```

**Affix handling:** If `Document_ID_Affixes` column is present, the known affix is stripped from `Document_ID` before segment comparison. This prevents false positives for IDs like `131242-WST00-PP-PM-0001_Reply`.

**Segment map:**

| Segment Index | Source Column |
|---------------|---------------|
| 0 | `Project_Code` |
| 1 | `Facility_Code` |
| 2 | `Document_Type` |
| 3 | `Discipline` |
| 4 | `Document_Sequence_Number` |

**Logic:**
1. Skip rows where `Document_ID` is null (caught by anchor check).
2. Strip affix from base ID.
3. Split base ID by `-` delimiter.
4. If fewer than 5 segments → emit `P2-I-V-0204` immediately.
5. Compare each segment against its source column value.
6. Any mismatch → emit `P2-I-V-0204` with `mismatches` list in context.

---

## 4. Target Achievement

| Metric | Target (Workplan) | Implementation |
|--------|-------------------|----------------|
| Composite identity match | 100% agreement | Segment-by-segment comparison per row |
| Affix handling | 1,600+ affixes without false positives | Affix stripped via `Document_ID_Affixes` column |
| Legacy format mismatches | 100+ detected | Mismatch logged with detail per row |
| Anchor null detection | 100% | All 5 anchor columns checked |

---

## 5. Error Output

Errors are emitted as `DetectionResult` objects with:
- `error_code`: `P1-A-P-0101` or `P2-I-V-0204`
- `row`: DataFrame row index
- `column`: failing column name
- `severity`: HIGH
- `context.error_key`: `ANCHOR_NULL` or `COMPOSITE_MISMATCH`
- `context.mismatches`: list of segment mismatch descriptions (composite only)

All errors feed into `error_aggregator` → `Validation_Errors` column → `Data_Health_Score`.

**Health score deductions:**
- `ANCHOR_NULL`: −25 pts per row
- `COMPOSITE_MISMATCH`: −20 pts per row

---

## 6. Potential Issues Addressed

| Issue | Handling |
|-------|----------|
| Varied delimiters in legacy Document_ID (e.g. `_` vs `-`) | Affix stripping isolates base; segment split uses `-` only |
| Leading/trailing whitespace in constituent columns | `.strip()` applied to both segment and source value before comparison |
| Fewer than 5 segments | Caught before segment loop; separate error emitted |
| Null source columns | Empty string used for comparison; mismatch only flagged if source is non-empty |

---

## 7. Integration

- **Trigger:** `RowValidator.detect()` called from `engine.py` Phase 4, after `apply_validation()`.
- **Class:** `RowValidator` in `processor_engine/error_handling/detectors/row_validator.py`
- **Exported:** `detectors/__init__.py`
