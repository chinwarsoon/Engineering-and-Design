# Data Business Logic Validation Workplan

**Document ID:** WP-DCC-BLV-001  
**Version:** 1.0.1  
**Status:** DRAFT — Pending Approval  
**Created:** 2026-05-17  
**Author:** AI Agent  
**Based on:** `agent_rule.md`, `column_priority_reference.md`, `column_update_logic.md`, `dcc_register_config.json`, pipeline execution results

---

## Revision History

| Version | Date | Summary | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-05-17 | Initial workplan — pipeline execution findings, 8 contradicting issues identified | AI Agent |
| 1.0.7 | 2026-05-17 | BLV-005 revised: Resubmission_Required is primary determinant; NO/RESUBMITTED → NaT, YES/PEN → calculate (overrides terminal); 6,300+ rows affected | AI Agent |

---

## Table of Contents

1. [Objective](#1-objective)
2. [Scope Summary](#2-scope-summary)
3. [Dependencies](#3-dependencies)
4. [Evaluation and Architecture Alignment](#4-evaluation-and-architecture-alignment)
5. [Implementation Phases](#5-implementation-phases)
   - [Phase 1: Submission_Closed vs Resubmission_Plan_Date Contradiction](#phase-1-submission_closed-vs-resubmission_plan_date-contradiction)
   - [Phase 2: Document_ID Format and Quality](#phase-2-document_id-format-and-quality)
   - [Phase 3: Resubmission_Overdue_Status Logic Gap](#phase-3-resubmission_overdue_status-logic-gap)
   - [Phase 4: Latest_Revision Null Handling](#phase-4-latest_revision-null-handling)
   - [Phase 5: Terminal Approval Resubmission_Plan_Date Logic](#phase-5-terminal-approval-resubmission_plan_date-logic)
   - [Phase 6: All_Submission_Sessions Format Consistency](#phase-6-all_submission_sessions-format-consistency)
   - [Phase 7: Validation_Errors Volume Reduction](#phase-7-validation_errors-volume-reduction)
   - [Phase 8: Schema Validation Rule Review](#phase-8-schema-validation-rule-review)
6. [Success Criteria](#6-success-criteria)
7. [Risks and Mitigation](#7-risks-and-mitigation)
8. [References](#8-references)

---

## 1. Objective

Validate and resolve all contradicting business logic issues identified during pipeline execution of `dcc_engine_pipeline.py` against the documented business rules in `column_priority_reference.md` and `column_update_logic.md`. Ensure the processing pipeline produces output consistent with the defined schema, calculation strategies, and business logic rules.

**Pipeline Execution Baseline:**
- Input: `Submittal and RFI Tracker Lists.xlsx` (11,821 rows, 27 columns)
- Output: `processed_dcc_universal.xlsx` (11,821 rows, 45 columns)
- Header Match Rate: 100%
- Rows with Validation Errors: 3,784 (32%)

---

## 2. Scope Summary

| ID | Issue | Category | Severity | Phase | Status |
|----|-------|----------|----------|-------|--------|
| BLV-001 | Latest submission Closed=YES with Resubmission_Plan_Date set (713 rows) | Logic Contradiction | HIGH | Phase 1 | Identified |
| BLV-002 | Document_ID format violations (1,702 rows: 1,613 affixed + 89 malformed) | Data Quality / Calculation | HIGH | Phase 2 | Identified |
| BLV-003 | Resubmission_Overdue_Status 3-value logic insufficient (696 rows misclassified) | Logic Expansion | HIGH | Phase 3 | Identified |
| BLV-004 | Latest_Revision null for 119 rows (108 unique Document_IDs) | Null Handling | MEDIUM | Phase 4 | Revised — business logic matrix defined |
| BLV-005 | Resubmission_Plan_Date set when Resubmission_Required=NO/RESUBMITTED or terminal approval (~6,300 rows) | Logic Contradiction | HIGH | Phase 5 | Revised — Resubmission_Required is primary determinant |
| BLV-006 | All_Submission_Sessions format mismatch (JSON-like vs "&&" separator) | Format Consistency | LOW | Phase 6 | Identified |
| BLV-007 | Validation_Errors in 32% of rows — systemic data quality | Data Quality | MEDIUM | Phase 7 | Identified |
| BLV-008 | Count_of_Submissions max_value=100 may be too restrictive | Schema Rule | LOW | Phase 8 | Identified |

---

## 3. Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `dcc_register_config.json` | Schema | Primary schema defining column processing rules, strategies, and validation |
| `dcc_global_parameters.json` | Config | Duration parameters (first_review=20, second_review=14, resubmission=14) |
| `approval_code_schema.json` | Schema | Terminal codes (APP, VOID, INF) and pending status (PEN) definitions |
| `column_priority_reference.md` | Documentation | Priority definitions, forward fill boundaries, processing sequence |
| `column_update_logic.md` | Documentation | Detailed calculation methods, null handling strategies |
| `processor_engine/core/engine.py` | Code | Calculation engine implementation |
| `processor_engine/calculations/*.py` | Code | Individual calculation handlers |

---

## 4. Evaluation and Architecture Alignment

### 4.1 Current Architecture Assessment

The pipeline follows a 4-phase processing model (P1→P2→P2.5→P3) as documented. The architecture is sound but has gaps in:

1. **Conditional logic completeness**: Some calculation handlers do not cover all edge cases defined in business rules
2. **Data preservation strategy consistency**: Some columns overwrite where they should preserve
3. **Format standardization**: Aggregate columns produce inconsistent output formats
4. **Source data quality handling**: Pipeline processes malformed data without sufficient pre-validation

### 4.2 Alignment with agent_rule.md

| Rule | Compliance | Notes |
|------|------------|-------|
| Section 1.4 — Priority processing | ✅ | P1→P2→P2.5→P3 sequence followed |
| Section 1.5 — Processing sequence | ✅ | Impute→Validate→Calculate order correct |
| Section 2 — Schema compliance | ⚠️ | Schema defines rules but some not enforced in code |
| Section 12 — Independent error codes | ✅ | Error codes defined and applied |

---

## 5. Implementation Phases

### Phase 1: Submission_Closed vs Resubmission_Plan_Date Contradiction

**Issue BLV-001:** Latest submission with `Submission_Closed=YES` but `Resubmission_Plan_Date` is set (713 rows).

#### 5.1.1 Analysis

Per business logic clarification:
- **Superseded rows** (where `Submission_Date < Latest_Submission_Date`): `Submission_Closed=YES` is correct AND `Resubmission_Plan_Date` SHOULD be set — this is expected behavior (4,965 rows, NOT a bug)
- **Latest row** (where `Submission_Date == Latest_Submission_Date`): If `Submission_Closed=YES`, then `Resubmission_Plan_Date` should be `NaT` — no resubmission plan needed for a closed latest submission

**Re-analysis results:**

| Category | Rows | Status |
|----------|------|--------|
| Superseded + Closed=YES + Plan_Date set | 4,965 | ✅ Correct behavior — no action needed |
| Latest + Closed=YES + Plan_Date set | 713 | ❌ Bug to fix |
| Latest + Terminal approval + Plan_Date set | 0 | ✅ Already correct |

**Breakdown of 713 problematic rows by Latest_Approval_Code:**
- AWC (Approved with Comments): 431 rows
- NAP (Not Approved): 183 rows
- REJ (Rejected): 99 rows

**Root Cause:** The `Resubmission_Plan_Date` calculation only sets `NaT` for latest rows with **terminal** approval codes (APP/VOID/INF). It does not handle the case where the latest row has `Submission_Closed=YES` from user input preservation with non-terminal codes (AWC/NAP/REJ).

#### 5.1.2 What Will Be Updated

**A. Calculation Logic Fix**

- **File:** `processor_engine/calculations/conditional_date.py` (Resubmission_Plan_Date handler)
- **Change:** Add condition for latest closed submission:
  ```
  if Submission_Date == Latest_Submission_Date AND Submission_Closed == "YES" → Resubmission_Plan_Date = NaT
  else → apply existing conditional logic
  ```

**B. Error Code Description Updates (L3-L-V-0302)**

The detector in `row_validator.py` already has correct logic (only flags latest rows via `is_latest_mask`). However, the error code **name and message** are misleading — they imply ALL rows with `Closed=YES`, not just latest ones. The following files will be updated to clarify this:

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `config/schemas/data_error_config.json` | `name` | `CLOSED_WITH_PLAN_DATE` | `LATEST_CLOSED_WITH_PLAN_DATE` |
| `config/schemas/data_error_config.json` | `message` | `Submission_Closed=YES but Resubmission_Plan_Date is set` | `Latest submission Closed=YES but Resubmission_Plan_Date is set` |
| `config/schemas/data_error_config.json` | `message_template` | Same as message | Same as message |
| `config/schemas/data_error_config.json` | `remediation` | `Clear Resubmission_Plan_Date when Submission_Closed is YES` | `Clear Resubmission_Plan_Date for latest submission when Closed=YES` |
| `workflow/processor_engine/error_handling/config/messages/en.json` | `L3-L-V-0302` | `Submission_Closed=YES but Resubmission_Plan_Date is set` | `Latest submission Closed=YES but Resubmission_Plan_Date is set` |
| `workflow/processor_engine/error_handling/config/messages/zh.json` | `L3-L-V-0302` | `提交已关闭但重新提交计划日期已设置` | `最新提交已关闭但重新提交计划日期已设置` |
| `workflow/processor_engine/error_handling/detectors/row_validator.py` | Docstring (line 16) | `CLOSED_WITH_PLAN_DATE - Resubmission_Plan_Date not null when Submission_Closed=YES` | `LATEST_CLOSED_WITH_PLAN_DATE - Resubmission_Plan_Date not null when latest submission Closed=YES` |
| `workflow/processor_engine/error_handling/detectors/row_validator.py` | Docstring (line 338) | `If Submission_Closed=YES then Resubmission_Plan_Date must be NULL` | `If latest submission Closed=YES then Resubmission_Plan_Date must be NULL` |

**C. Schema Documentation**

- **File:** `dcc_register_config.json`
- **Change:** Update `Resubmission_Plan_Date` strategy to document the "latest closed submission" dependency

#### 5.1.3 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M1.1 | Root cause analysis document | Day 1 |
| M1.2 | Code update to calculation handler | Day 2 |
| M1.3 | Test with current dataset | Day 3 |
| M1.4 | Verify 713 contradictions resolved | Day 3 |

#### 5.1.4 Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Removing valid plan dates for superseded rows | HIGH | Only apply condition to latest rows (`Submission_Date == Latest_Submission_Date`) |
| Performance impact on 11k+ rows | LOW | Vectorized operation, minimal overhead |

#### 5.1.5 Success Criteria

- [ ] Zero **latest** rows with `Submission_Closed=YES` AND `Resubmission_Plan_Date` not null
- [ ] All **superseded** rows (4,965) retain their `Resubmission_Plan_Date` values unchanged
- [ ] All `Submission_Closed=NO` rows retain correct plan dates
- [ ] Error code L3-L-V-0302 name updated to `LATEST_CLOSED_WITH_PLAN_DATE`
- [ ] Error code L3-L-V-0302 message updated to mention "latest submission" in en.json, zh.json, and data_error_config.json
- [ ] Validation error `[L3-L-V-0302]` eliminated from output

---

### Phase 2: Document_ID Format and Quality

**Issue BLV-002:** 1,702 rows have invalid Document_ID format.

#### 5.2.1 Analysis

Seven distinct error cases identified from pipeline output analysis:

| Case | Description | Count | % | Root Cause | Action |
|------|-------------|-------|---|------------|--------|
| 1 | Valid base ID + affix/suffix | 1,613 | 94.8% | Original data contains underscore suffixes (e.g., `_ST604`, `_PUB`) | Strip affix, populate `Document_ID_Affixes` |
| 2 | NA segments (missing source) | 65 | 3.8% | Source columns null → composite fills with "NA" | Flag as unresolvable, do not calculate |
| 3 | Reply/Comment sheet references | 4 | 0.2% | Raw input is transmittal text, not document ID | Flag as malformed source |
| 4 | Spaces in segments | 21 | 1.2% | Text in sequence field (e.g., "comment reply") | Flag as data quality issue |
| 5 | Wrong segment count (>5 or <5) | 23 | 1.4% | Source values contain dashes, splitting incorrectly | Flag as structural error |
| 6 | Lowercase letters only | 0 | 0% | Co-occurs with other cases, not standalone | N/A |
| 7 | Special characters (dots, parens) | 20 | 1.2% | Version numbers, numbered lists in source | Flag as malformed source |

**Case 1 Detail (1,613 rows — 94.8% of invalid IDs):**

These are **valid document IDs from original data** with affix/suffix appended via underscore. The processing pipeline must:
1. **Strip** the affix portion (everything after `_`) from the raw Document_ID
2. **Validate** the remaining base ID against the 5-segment pattern
3. **Populate** `Document_ID_Affixes` with the extracted suffix
4. **Store** the clean base ID in `Document_ID`

Examples of valid base + affix:
- `131242-WST00-DR-C-8000_ST604` → ID: `131242-WST00-DR-C-8000`, Affix: `_ST604`
- `131242-WST00-DR-S-1000_ST604` → ID: `131242-WST00-DR-S-1000`, Affix: `_ST604`
- `131242-WST02-DR-A-1001_PUB` → ID: `131242-WST02-DR-A-1001`, Affix: `_PUB`

**Cases 2-7 Detail (89 rows — 5.2% of invalid IDs):**

These are genuine data quality issues where source columns contain invalid/malformed data. The composite calculation produces invalid IDs because source data cannot be structured into the 5-segment format.

#### 5.2.2 What Will Be Updated

**A. Affix Extraction and Separation (Case 1 — 1,613 rows)**

- **File:** `processor_engine/calculations/composite.py` (Document_ID builder)
- **Change:** Add affix extraction step **before** validation:
  ```
  1. If raw Document_ID contains '_', split at first underscore
  2. base_id = part before '_'
  3. affix = '_' + part after '_'
  4. Validate base_id against 5-segment pattern
  5. If valid → store base_id in Document_ID, affix in Document_ID_Affixes
  6. If invalid → fall through to malformed source handling
  ```
- **File:** `processor_engine/calculations/affix.py` (Document_ID_Affixes handler)
- **Change:** Update `extract_document_id_affixes` to run **after** composite calculation but **before** validation, so the extracted affix is available when validation runs

**B. Malformed Source Handling (Cases 2-7 — 89 rows)**

- **File:** `processor_engine/calculations/composite.py`
- **Change:** Add pre-validation of source columns before composite calculation:
  - If any source column = "NA" or contains non-standard characters → skip calculation
  - Flag row with specific error code for the type of malformed data
- **File:** `processor_engine/error_handling/detectors/validation.py`
- **Change:** Add specific error codes for each malformed source type:
  - `P2-I-V-0204-D`: NA segments in composite ID
  - `P2-I-V-0204-E`: Reply/Comment reference in ID field
  - `P2-I-V-0204-F`: Spaces in ID segments
  - `P2-I-V-0204-G`: Wrong segment count
  - `P2-I-V-0204-H`: Special characters in ID

**C. Error Code Configuration Updates**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `data_error_config.json` | Add 5 new codes | — | P2-I-V-0204-D through P2-I-V-0204-H |
| `messages/en.json` | Add 5 new messages | — | Descriptive messages for each malformed type |
| `messages/zh.json` | Add 5 new messages | — | Chinese translations |

**D. Schema Documentation**

- **File:** `dcc_register_config.json`
- **Change:** Update `Document_ID` validation pattern and `Document_ID_Affixes` processing sequence documentation

#### 5.2.3 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M2.1 | Implement affix extraction + separation logic | Day 1 |
| M2.2 | Add malformed source pre-validation | Day 2 |
| M2.3 | Add 5 new error codes to config and messages | Day 2 |
| M2.4 | Test with current dataset | Day 3 |
| M2.5 | Verify 1,613 affixed IDs resolved, 89 malformed flagged | Day 3 |

#### 5.2.4 Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incorrect affix split (multiple underscores) | MEDIUM | Split at **first** underscore only; validate resulting base ID |
| Losing affix data during separation | HIGH | Always store extracted affix in `Document_ID_Affixes` before modifying `Document_ID` |
| Affix extraction runs after validation | HIGH | Ensure processing order: extract → validate → flag |

#### 5.2.5 Success Criteria

- [ ] 1,613 affixed IDs: base ID extracted and stored in `Document_ID`, affix in `Document_ID_Affixes`
- [ ] 1,613 rows pass validation (no longer flagged as invalid format)
- [ ] 89 malformed source rows flagged with specific error codes (not calculated)
- [ ] Validation error `[P2-I-V-0204-A]` count reduced from 1,613 to 0 for affixed IDs
- [ ] `Latest_Revision` null count reduced for rows with valid affixed IDs
- [ ] `Document_ID_Affixes` populated for all 1,613 rows with extracted affix values

---

### Phase 3: Resubmission_Overdue_Status Logic Expansion

**Issue BLV-003:** Current 3-value logic (`Overdue`, `Resubmitted`, `NO`) cannot distinguish between overdue-but-resubmitted vs overdue-and-not-yet-resubmitted. 653 rows with `Resubmission_Required="RESUBMITTED"` are marked `Overdue` but the status does not indicate resubmission completion.

#### 5.3.1 Analysis

Per business logic (`column_update_logic.md` Step 39):
- Current condition: `Resubmission_Required == "YES"` AND `Resubmission_Plan_Date < current_date` → `"Overdue"`, else → `"NO"`
- Schema `allowed_values`: `["Resubmitted", "Overdue", "NO"]` — but `"Resubmitted"` is **never produced** by the calculation
- Actual output: 4,039 `Overdue`, 7,782 `NO`, 0 `Resubmitted`

**Five business scenarios not covered by current logic:**

| # | Scenario | Current Output | Problem |
|---|----------|---------------|---------|
| 1 | Overdue but already resubmitted | `Overdue` | Does not indicate resubmission completed |
| 2 | Overdue and not resubmitted | `Overdue` | Correct but ambiguous |
| 3 | Not overdue but resubmitted | `NO` | Loses resubmission information |
| 4 | Not overdue, not resubmitted yet | `NO` | No distinction from closed documents |
| 5 | Resubmission not required | `NO` | Correct |

#### 5.3.2 Proposed Value Matrix

| Value | Business Meaning | Condition | Actionable |
|-------|-----------------|-----------|------------|
| `OVERDUE_RESUBMITTED` | Was overdue, resubmission already completed | `Plan_Date < today` AND `Resubmission_Required == "RESUBMITTED"` | No — historical record |
| `OVERDUE` | Currently overdue, action needed | `Plan_Date < today` AND `Resubmission_Required == "YES"` | Yes — requires attention |
| `RESUBMITTED` | Resubmitted on or before deadline | `Plan_Date >= today` AND `Resubmission_Required == "RESUBMITTED"` | No — completed on time |
| `ON_TRACK` | Resubmission required, deadline not yet passed | `Plan_Date >= today` AND `Resubmission_Required == "YES"` | No — monitoring only |
| `NO` | Resubmission not required | `Submission_Closed == "YES"` OR `Resubmission_Required == "NO"` | No — closed or N/A |

#### 5.3.3 What Will Be Updated

**A. Calculation Logic Rewrite**

- **File:** `processor_engine/calculations/conditional.py` (`apply_calculate_overdue_status`)
- **Change:** Replace 2-value logic with 5-value logic:
  ```
  if Resubmission_Required == "RESUBMITTED" AND Plan_Date < today:
      → "OVERDUE_RESUBMITTED"
  elif Resubmission_Required == "RESUBMITTED" AND Plan_Date >= today:
      → "RESUBMITTED"
  elif Resubmission_Required == "NO" OR Submission_Closed == "YES":
      → "NO"
  elif Resubmission_Required == "YES" AND Plan_Date < today:
      → "OVERDUE"
  elif Resubmission_Required == "YES" AND Plan_Date >= today:
      → "ON_TRACK"
  else:
      → "NO"
  ```

**B. Schema Updates**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `dcc_register_config.json` | `allowed_values` | `["Resubmitted", "Overdue", "NO"]` | `["OVERDUE_RESUBMITTED", "OVERDUE", "RESUBMITTED", "ON_TRACK", "NO"]` |
| `dcc_register_config.json` | `calculation.conditions` | 2 conditions | 5 conditions |
| `dcc_register_config.json` | `calculation.description` | Existing | Updated with 5-value logic |

**C. Error Code and Message Updates**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `data_error_config.json` | L3-L-V-0304 `message` | `Resubmission_Overdue_Status mismatch` | Updated to reflect 5 values |
| `data_error_config.json` | L3-L-V-0304 `remediation` | Existing | Updated |
| `messages/en.json` | L3-L-V-0304 | Existing | Updated |
| `messages/zh.json` | L3-L-V-0304 | Existing | Updated |

**D. Validation Logic Update**

- **File:** `processor_engine/error_handling/detectors/row_validator.py` (`_validate_overdue_status`)
- **Change:** Update validation to accept all 5 values and check against appropriate conditions per value

#### 5.3.4 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M3.1 | Rewrite overdue calculation with 5-value logic | Day 1 |
| M3.2 | Update schema allowed_values and conditions | Day 1 |
| M3.3 | Update error codes and messages (en/zh) | Day 2 |
| M3.4 | Update row validator to accept 5 values | Day 2 |
| M3.5 | Test with current dataset | Day 3 |
| M3.6 | Verify value distribution matches expected | Day 3 |

#### 5.3.5 Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking downstream consumers expecting old values | HIGH | Document value mapping; provide migration guide |
| `ON_TRACK` confusion with `NO` | MEDIUM | Clear documentation and UI labels |
| Performance impact on 11k+ rows | LOW | Vectorized operations, minimal overhead |

#### 5.3.6 Success Criteria

- [ ] 653 `RESUBMITTED` rows with past plan dates → `OVERDUE_RESUBMITTED`
- [ ] 3,377 `YES` rows with past plan dates → `OVERDUE`
- [ ] 3 `RESUBMITTED` rows with future plan dates → `RESUBMITTED`
- [ ] 27 `YES` rows with future plan dates → `ON_TRACK`
- [ ] All closed/NO rows → `NO`
- [ ] Schema `allowed_values` updated to 5 values
- [ ] Validation accepts all 5 values without errors
- [ ] Error code L3-L-V-0304 messages updated in en.json and zh.json

---

### Phase 4: Latest_Revision Null Handling

**Issue BLV-004:** 119 rows have null `Latest_Revision`.

#### 5.4.1 Analysis

Per business logic (`column_update_logic.md` Step 19):
- `Latest_Revision`: Derived from `Document_Revision` grouped by `Document_ID`, sorted by `Submission_Date` desc
- `Document_Revision` is **manually input by user** — no forward fill or session-based fallback applies
- Actual: 119 nulls across 108 unique Document_IDs

**Root Cause Breakdown:**

| Cause | Rows | Description |
|-------|------|-------------|
| Valid Document_ID + null Document_Revision | 106 | User has not entered revision — business logic error, requires manual input |
| Malformed Document_ID (not 5-segment) | 13 | Invalid Document_ID prevents proper grouping — set to "NA" until Document_ID is corrected |

#### 5.4.2 Business Logic Matrix

| # | Document_ID Valid? | Document_Revision | Latest_Revision Result | Action |
|---|-------------------|-------------------|------------------------|--------|
| 1 | YES | Has value (not "NA") | Use Document_Revision value | Normal — no action |
| 2 | YES | null | **null** (business logic error) | Flag with P4-I-V-0401 for manual user input |
| 3 | YES | "NA" | **null** (business logic error) | Flag with P4-I-V-0401 for manual user input |
| 4 | NO (malformed) | Any | **"NA"** | Set to "NA"; will be recalculated after Phase 2 fixes Document_ID |

#### 5.4.3 What Will Be Updated

**A. Calculation Logic Update**

- **File:** `processor_engine/calculations/aggregate.py` (`apply_latest_by_date_calculation`)
- **Change:** Replace multi-level forward fill with simple final fill logic:
  ```
  1. Validate Document_ID format (5-segment pattern)
  2. If Document_ID is malformed → set Latest_Revision = "NA"
  3. If Document_ID is valid:
     a. Check if Document_Revision is null or "NA"
     b. If null or "NA" → leave Latest_Revision = null (flag P4-I-V-0401 for manual input)
     c. If has valid value → group by Document_ID, sort by Submission_Date desc
     d. Apply valid revision to all rows in group
  4. No forward fill, no session-based fallback
  ```

**B. Schema Updates**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `dcc_register_config.json` | `Document_Revision.null_handling` | `multi_level_forward_fill` with 3 levels | Remove; replace with `final_fill: "NA"` only |
| `dcc_register_config.json` | `Latest_Revision.calculation` | Existing | Add Document_ID validation step before groupby |
| `dcc_register_config.json` | `Latest_Revision.allow_null` | `true` | Keep `true` — null indicates missing user input |

**C. Error Code Configuration**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `data_error_config.json` | Add new code | — | `P4-I-V-0401`: Document_Revision null or "NA" for valid Document_ID — manual input required |
| `messages/en.json` | Add new message | — | "Revision number is required. Please enter a valid Document_Revision (not blank or 'NA')." |
| `messages/zh.json` | Add new message | — | Chinese translation |

#### 5.4.4 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M4.1 | Remove multi-level forward fill from Document_Revision config | Day 1 |
| M4.2 | Add Document_ID validation step to latest_by_date calculation | Day 1 |
| M4.3 | Add error code P4-I-V-0401 for missing revision | Day 2 |
| M4.4 | Set malformed Document_ID rows to "NA" | Day 2 |
| M4.5 | Test with current dataset | Day 3 |
| M4.6 | Verify 13 malformed rows → "NA", 106 valid rows → null (flagged with P4-I-V-0401) | Day 3 |

#### 5.4.5 Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-filling null revisions | HIGH | Never auto-fill; leave null and flag for user input |
| Malformed IDs blocking calculation | MEDIUM | Set to "NA" first; recalculate after Phase 2 |
| Breaking downstream consumers expecting values | LOW | Document that null = missing user input |

#### 5.4.6 Success Criteria

- [ ] 13 malformed Document_ID rows → `Latest_Revision = "NA"`
- [ ] 106 valid Document_ID rows with null/"NA" revision → `Latest_Revision = null` (flagged with P4-I-V-0401)
- [ ] Multi-level forward fill removed from `Document_Revision` config
- [ ] No forward fill or session-based fallback applied
- [ ] Error code P4-I-V-0401 added to data_error_config.json
- [ ] Messages added in en.json and zh.json
- [ ] After Phase 2 completes, 68 rows recalculated with corrected Document_IDs

---

### Phase 5: Terminal Approval Resubmission_Plan_Date Logic

**Issue BLV-005:** ~6,300 rows have incorrect `Resubmission_Plan_Date` values due to missing `Resubmission_Required` check in calculation logic.

#### 5.5.1 Analysis

Per business logic (`column_update_logic.md` Step 37):
- Current condition: `Submission_Date == Latest_Submission_Date` AND `Latest_Approval_Code` in terminal codes → `NaT`
- **Only the latest submission row** of a terminally approved document gets `NaT`
- Superseded rows receive calculated dates (current behavior)
- **Missing:** No check for `Resubmission_Required` — dates calculated even when resubmission is not needed

**Root Cause:** The calculation does not check `Resubmission_Required` before determining plan dates. This causes:
1. 5,678 rows with `Resubmission_Required=NO` to have calculated dates (should be NaT)
2. 656 rows with `Resubmission_Required=RESUBMITTED` to have calculated dates (should be NaT)
3. 34 rows with `Resubmission_Required=YES` + terminal approval to have NaT (should be calculated)

**Data Breakdown:**

| Category | Rows | Description |
|----------|------|-------------|
| Resubmission_Required=NO + plan date set | 5,678 | Bug: resubmission not required but date calculated |
| Resubmission_Required=RESUBMITTED + plan date set | 656 | Bug: already resubmitted but date not cleared |
| Resubmission_Required=YES + terminal approval + NaT | 34 | Bug: user requires resubmission but date not calculated |

Note: The 972 superseded rows with terminal approval are a subset of the 5,678 NO rows (884) and 656 RESUBMITTED rows (88).

#### 5.5.2 Calculation Priority Table

| Priority | Condition Check | Column | Operator | Value | If TRUE → Resubmission_Plan_Date | If FALSE → Next Step |
|----------|----------------|--------|----------|-------|----------------------------------|---------------------|
| 1 | Resubmission not needed | `Resubmission_Required` | `IN` | `["NO", "RESUBMITTED"]` | **NaT** | Step 2 |
| 2 | User requires resubmission | `Resubmission_Required` | `IN` | `["YES", "PEN"]` | **Calculated** (see sub-rules) | Step 3 |
| 3 | Terminal approval | `Latest_Approval_Code` | `IN` | `["APP", "VOID", "INF"]` | **NaT** | Step 4 |
| 4 | Has return date | `Review_Return_Actual_Date` | `NOT NULL` | — | `Review_Return_Actual_Date + resubmission_duration` | Step 5 |
| 5 | First submission | `Latest_Submission_Date` | `==` | `Submission_Date` | `Submission_Date + first_review + resubmission_duration` | Step 6 |
| 6 | Subsequent submission | — | — | — | `Submission_Date + second_review + resubmission_duration` | — |

**Step 2 sub-rules (when Resubmission_Required in ["YES", "PEN"]):**

| Sub-Priority | Condition | Result |
|--------------|-----------|--------|
| 2a | `Review_Return_Actual_Date` NOT NULL | `Review_Return_Actual_Date + resubmission_duration` |
| 2b | `Latest_Submission_Date == Submission_Date` | `Submission_Date + first_review + resubmission_duration` |
| 2c | Else | `Submission_Date + second_review + resubmission_duration` |

#### 5.5.3 Business Logic Matrix

| # | Resubmission_Required | Latest_Approval_Code | Resubmission_Plan_Date | Reason |
|---|----------------------|---------------------|------------------------|--------|
| 1 | NO | Any | **NaT** | No resubmission needed |
| 2 | RESUBMITTED | Any | **NaT** | Already resubmitted |
| 3 | YES | Any (including terminal) | **Calculated** | User explicitly requires resubmission — overrides terminal approval |
| 4 | PEN | Any (including terminal) | **Calculated** | Pending decision — calculate plan date until decision is made |
| 5 | (not YES/PEN) | Terminal (APP/VOID/INF) | **NaT** | Document closed, no resubmission needed |
| 6 | (not YES/PEN) | Non-terminal | **Calculated** | Active document awaiting decision |

**Exception case identified:** 34 rows have `Resubmission_Required=YES` AND `Latest_Approval_Code=INF`. Currently all have `Resubmission_Plan_Date=NaT`. Per new rule, these 34 rows must have calculated dates.

**Note:** `Resubmission_Required=PEN` (763 rows) also requires calculated dates. No PEN rows have terminal approval, so no override conflict exists.

#### 5.5.4 What Will Be Updated

**A. Calculation Logic Update**

- **File:** `processor_engine/calculations/date.py` (`apply_resubmission_plan_date`)
- **Change:** Add `Resubmission_Required` check as highest priority, then apply terminal approval to all rows:
  ```
  1. If Resubmission_Required in ["NO", "RESUBMITTED"]:
     → Resubmission_Plan_Date = NaT
  2. Else if Resubmission_Required in ["YES", "PEN"]:
     → Calculate Resubmission_Plan_Date (overrides terminal approval)
     a. If Review_Return_Actual_Date is not null → Review_Return_Actual_Date + resubmission_duration
     b. Else if Latest_Submission_Date == Submission_Date → Submission_Date + first_review + resubmission_duration
     c. Else → Submission_Date + second_review + resubmission_duration
  3. Else if Latest_Approval_Code in terminal_codes (APP, VOID, INF):
     → Resubmission_Plan_Date = NaT (all rows, not just latest)
  4. Else if Review_Return_Actual_Date is not null:
     → Resubmission_Plan_Date = Review_Return_Actual_Date + resubmission_duration
  5. Else if Latest_Submission_Date == Submission_Date:
     → Resubmission_Plan_Date = Submission_Date + first_review + resubmission_duration
  6. Else:
     → Resubmission_Plan_Date = Submission_Date + second_review + resubmission_duration
  ```

**B. Schema Updates**

| File | Field | Current | Updated |
|------|-------|---------|---------|
| `dcc_register_config.json` | `Resubmission_Plan_Date.calculation.conditions` | 4 conditions | 6 conditions with Resubmission_Required as primary determinant |
| `dcc_register_config.json` | `Resubmission_Plan_Date.calculation.dependencies` | Existing | Add `Resubmission_Required` as first dependency |
| `dcc_register_config.json` | `Resubmission_Plan_Date.calculation.description` | Existing | Updated to reflect Resubmission_Required priority and terminal approval override |

#### 5.5.5 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M5.1 | Add Resubmission_Required check as highest priority (NO/RESUBMITTED → NaT, YES/PEN → calculate) | Day 1 |
| M5.2 | Remove latest-row restriction from terminal approval condition | Day 1 |
| M5.3 | Test with current dataset | Day 2 |
| M5.4 | Verify 5,678 NO rows → NaT | Day 2 |
| M5.5 | Verify 656 RESUBMITTED rows → NaT | Day 2 |
| M5.6 | Verify 34 YES+terminal rows → calculated dates | Day 2 |

#### 5.5.6 Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Losing historical resubmission plan dates | LOW | Terminal approval or NO/RESUBMITTED status means dates are no longer actionable |
| Breaking downstream consumers | MEDIUM | 6,300+ rows changing from date to NaT; document the change |
| Resubmission_Required=YES rows missed | HIGH | Check processed as highest priority; explicit validation for 34 exception rows |

#### 5.5.7 Success Criteria

- [ ] 5,678 rows with `Resubmission_Required=NO` + plan date → `Resubmission_Plan_Date = NaT`
- [ ] 656 rows with `Resubmission_Required=RESUBMITTED` + plan date → `Resubmission_Plan_Date = NaT`
- [ ] 34 rows with `Resubmission_Required=YES` + terminal approval → calculated `Resubmission_Plan_Date`
- [ ] Total rows with `Resubmission_Plan_Date` set reduced by ~6,300 (5,678 + 656 - 34)
- [ ] `Resubmission_Required` added as first dependency in schema

---

### Phase 6: All_Submission_Sessions Format Consistency

**Issue BLV-006:** Output shows `["000001"]` instead of `000001` or `000001&&000002`.

#### 5.6.1 Analysis

Per business logic (`column_update_logic.md` Step 20):
- `All_Submission_Sessions`: Group by `Document_ID`, join unique sessions with `"&&"`
- Actual: JSON-like array format `["000001"]`

**Root Cause:** The `concatenate_unique` method may be producing JSON array strings instead of plain concatenated strings.

#### 5.6.2 What Will Be Updated

- **File:** `processor_engine/calculations/aggregate.py` (concatenate_unique handler)
- **Change:** Ensure output is plain string with separator, not JSON array format
- **Schema:** Verify `column_type: "json_column"` vs actual output format expectation

#### 5.6.3 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M6.1 | Identify format generation point | Day 1 |
| M6.2 | Fix to produce "&&" separated string | Day 2 |
| M6.3 | Test all aggregate columns for format consistency | Day 2 |

#### 5.6.4 Success Criteria

- [ ] `All_Submission_Sessions` format: `000001&&000002` (not JSON array)
- [ ] `All_Submission_Dates` format: `2023-05-15, 2024-05-13` (consistent)
- [ ] `All_Submission_Session_Revisions` format: `00, 01` (consistent)

---

### Phase 7: Validation_Errors Volume Reduction

**Issue BLV-007:** 3,784 rows (32%) have validation errors.

#### 5.7.1 Analysis

Top error codes:
| Error Code | Count | Description |
|------------|-------|-------------|
| P2-I-V-0204-C | 1,667 | Document_ID segment count issue (1,613 affixed + 54 other) |
| L3-L-V-0302 | 713 | Latest submission Closed=YES but Resubmission_Plan_Date set |
| F4-C-F-0403-C | 710 | Default value applied to fill nulls |
| L3-L-V-0304 | 615 | Resubmission_Overdue_Status value mismatch |
| L3-L-V-0303 | 313 | Related to Resubmission logic |
| F4-C-F-0401-A | 281 | Forward fill applied |
| L3-L-V-0308 | 259 | Related to Overdue status |
| L3-L-V-0305 | 214 | Related to closure logic |

#### 5.7.2 What Will Be Updated

- **Dependency:** Phases 1-6 will resolve the majority of these errors
- **Phase 3 impact:** 5-value Resubmission_Overdue_Status matrix eliminates 696 misclassified rows; L3-L-V-0304 and L3-L-V-0308 errors resolved
- **Phase 4 impact:** 13 malformed Document_ID rows set to "NA"; 106 valid Document_ID rows flagged with P4-I-V-0401 for manual revision input
- **File:** `processor_engine/error_handling/detectors/validation.py`
- **Change:** Review error code definitions to ensure appropriate severity levels
- **Goal:** Reduce validation error rows from 32% to <10% after all phases complete

#### 5.7.3 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M7.1 | Execute Phases 1-6 | Day 1-4 |
| M7.2 | Re-run pipeline and measure error reduction | Day 5 |
| M7.3 | Analyze remaining errors | Day 5 |

#### 5.7.4 Success Criteria

- [ ] Validation error rows reduced from 3,784 to <1,200 (<10%)
- [ ] Top 3 error codes eliminated or significantly reduced
- [ ] Remaining errors are legitimate data quality issues (not pipeline bugs)

---

### Phase 8: Schema Validation Rule Review

**Issue BLV-008:** `Count_of_Submissions` max_value=100 may be too restrictive.

#### 5.8.1 Analysis

- Schema defines: `max_value: 100` for `Count_of_Submissions`
- Actual max in data: Within limit (no rows > 100)
- **Assessment:** Current data does not trigger this, but large projects may exceed 100 submissions per document

#### 5.8.2 What Will Be Updated

- **File:** `dcc_register_config.json`
- **Change:** Consider increasing `max_value` to 500 or removing upper bound
- **Decision:** Pending — only update if business case supports higher submission counts

#### 5.8.3 Timeline and Deliverables

| Milestone | Deliverable | Target |
|-----------|-------------|--------|
| M8.1 | Research max submission counts in historical data | Day 1 |
| M8.2 | Update schema if needed | Day 2 |

#### 5.8.4 Success Criteria

- [ ] Schema validation rule reflects realistic business constraints
- [ ] No false-positive validation errors for legitimate high-count documents

---

## 6. Success Criteria

### Overall Pipeline Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Rows with Validation_Errors | 3,784 (32%) | <1,200 (<10%) |
| Latest Closed=YES with Resubmission_Plan_Date | 713 | 0 |
| Superseded Closed=YES with Resubmission_Plan_Date | 4,965 | 4,965 (unchanged, correct) |
| Invalid Document_ID format (affixed) | 1,613 | 0 (base ID extracted, affix separated) |
| Invalid Document_ID format (malformed) | 89 | 89 (flagged with specific error codes) |
| Overdue when Resubmission_Required≠YES | 696 | 0 (5-value matrix eliminates ambiguity) |
| Resubmission_Overdue_Status values | 3 (Overdue, Resubmitted, NO) | 5 (OVERDUE_RESUBMITTED, OVERDUE, RESUBMITTED, ON_TRACK, NO) |
| Latest_Revision null | 119 | 106 (flagged for manual input) + 13 (set to "NA" after Phase 2) |
| Data_Health_Score average | TBD | >80 |

### Phase Completion Criteria

- [ ] All 8 phases completed and tested
- [ ] Pipeline runs without errors on test dataset
- [ ] Output matches business logic specifications
- [ ] Validation error count reduced by >60%
- [ ] 1,613 affixed IDs resolved via extraction (not flagged as errors)
- [ ] 89 malformed IDs flagged with specific error codes
- [ ] All changes documented and logged

---

## 7. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing valid calculations | Medium | HIGH | Preserve existing values, only fill nulls |
| Performance degradation on large datasets | Low | Medium | Use vectorized operations, benchmark |
| Schema changes breaking downstream consumers | Low | Medium | Version schema, test compatibility |
| Source data quality issues masking as pipeline bugs | High | Medium | Separate data quality vs logic errors |
| Regression in previously working functionality | Medium | HIGH | Full regression test after each phase |

---

## 8. References

### Documentation
- [`agent_rule.md`](/home/franklin/dsai/Engineering-and-Design/agent_rule.md) — Project rules and standards
- [`column_priority_reference.md`](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/column_processing/column_priority_reference.md) — Column priority and processing rules
- [`column_update_logic.md`](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/column_processing/column_update_logic.md) — Detailed calculation logic

### Schema Files
- [`dcc_register_config.json`](/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/dcc_register_config.json) — Main register schema
- [`dcc_global_parameters.json`](/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/dcc_global_parameters.json) — Global parameters
- [`approval_code_schema.json`](/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/approval_code_schema.json) — Approval code definitions

### Code Files
- [`dcc_engine_pipeline.py`](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/dcc_engine_pipeline.py) — Main pipeline orchestrator
- [`processor_engine/core/engine.py`](/home/franklin/dsai/Engineering-and-Design/dcc/workflow/processor_engine/core/engine.py) — Calculation engine
- `processor_engine/calculations/*.py` — Individual calculation handlers

### Data Files
- Input: `/home/franklin/dsai/Engineering-and-Design/dcc/data/Submittal and RFI Tracker Lists.xlsx`
- Output: `/home/franklin/dsai/Engineering-and-Design/dcc/output/processed_dcc_universal.xlsx`

---

## Appendix A: Error Code Reference

| Code | Category | Description | Related Phase |
|------|----------|-------------|---------------|
| L3-L-V-0302 | Logic | Latest submission Closed=YES but Resubmission_Plan_Date is set | Phase 1 |
| L3-L-V-0303 | Logic | Resubmission logic contradiction | Phase 3 |
| L3-L-V-0304 | Logic | Resubmission_Overdue_Status value mismatch | Phase 3 |
| L3-L-V-0305 | Logic | Closure status contradiction | Phase 1 |
| L3-L-V-0308 | Logic | Overdue status contradiction | Phase 3 |
| P2-I-V-0204-A | Identity | Invalid Document_ID format (legacy) | Phase 2 |
| P2-I-V-0204-B | Identity | Document_ID fewer than 5 segments | Phase 2 |
| P2-I-V-0204-C | Identity | Document_ID segment count issue | Phase 2 |
| P2-I-V-0204-D | Identity | NA segments in composite Document_ID | Phase 2 (proposed) |
| P2-I-V-0204-E | Identity | Reply/Comment reference in Document_ID field | Phase 2 (proposed) |
| P2-I-V-0204-F | Identity | Spaces in Document_ID segments | Phase 2 (proposed) |
| P2-I-V-0204-G | Identity | Wrong segment count in Document_ID | Phase 2 (proposed) |
| P2-I-V-0204-H | Identity | Special characters in Document_ID | Phase 2 (proposed) |
| F4-C-F-0401-A | Fill | Forward fill applied | N/A (expected) |
| F4-C-F-0403-C | Fill | Default value applied to fill nulls | N/A (expected) |

---

**Status:** Awaiting approval to proceed with Phase 1 implementation.
