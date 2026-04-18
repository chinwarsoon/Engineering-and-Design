# DCC Register Data Rules

**Extracted from:** All markdown workplan and documentation files  
**Based on:** dcc_register_config.json schema, pipeline execution, error handling framework  
**Last Updated:** 2026-04-18

---

## Quick Reference: Master Column Table

All 48 columns consolidated in one view. **Click column type** for details, **See Appendix A** for full validation rules per column.

### Consolidated Column Reference

| # | Column | Priority | Calc | Data Type | Category | Phase | Group | Constraint | Business Logic | Null Handling | Manual | Overwrites | Dependencies | Foreign Key | Notes |
|---|--------|----------|------|-----------|----------|-------|-------|------------|----------------|---------------|--------|------------|--------------|-------------|-------|
| 1 | [Project_Code](#code-columns) | P1 | ❌ | categorical | Project ID | P1 | Meta | `^[A-Z0-9-]*$` / schema | Defines project context | default: "NA" | YES | N/A | - | **PK Component** | Safe for bounded forward fill |
| 2 | [Facility_Code](#code-columns) | P1 | ❌ | categorical | Org Metadata | P1 | Meta | `^[A-Z0-9-]*$` / schema | Facility location | default: "NA" | YES | N/A | - | **PK Component** | Safe for bounded forward fill |
| 3 | [Document_Type](#code-columns) | P1 | ❌ | categorical | Org Metadata | P1 | Meta | document_type_schema | Document category | default: "NA" | YES | N/A | - | **PK Component** | Safe for bounded forward fill |
| 4 | [Discipline](#code-columns) | P1 | ❌ | categorical | Org Metadata | P1 | Meta | discipline_schema | Engineering discipline | default: "NA" | YES | N/A | - | **PK Component** | Safe for bounded forward fill |
| 5 | [Document_Sequence_Number](#sequence-columns) | P2 | ❌ | string(4-digit) | Unique ID | P2 | Identity | Required, pattern `^[0-9]{4}$` | Document numbering | zero_pad: 4 | YES | N/A | - | **PK Component** | Document_ID component |
| 6 | [Document_ID](#id-columns) | P2.5 | ✅ | string | **PRIMARY KEY** | P2.5 | Anomaly | Composite pattern `{P}-{F}-{T}-{D}-{S}` | **Calculated PRIMARY KEY** | composite calc | NO | Preserves | P,F,T,D,S | **PRIMARY KEY** (5 components) | Processed P2.5 between P2 and P3 |
| 7 | [Document_Revision](#sequence-columns) | P2 | ❌ | string(2-digit) | Revision Control | P2 | Identity | Required, pattern `^[0-9]{2}$` | Specific revision | forward_fill | YES | N/A | - | - | Must not decrease per Document_ID |
| 8 | [Document_Title](#text-columns) | P2 | ❌ | string | Unique ID | P2 | Identity | Required, min_length | Document description | leave_null | YES | N/A | - | - | Missing in source data |
| 9 | [Transmittal_Number](#id-columns) | P1 | ❌ | string | Source Tracking | P1 | Meta | `^[A-Z0-9-]*$` | Transmittal reference | default: "NA" | YES | N/A | - | - | Safe for bounded forward fill |
| 10 | [Submission_Session](#sequence-columns) | P1 | ❌ | string(6-digit) | Source Tracking | P1 | Meta | `^[0-9]{6}$`, Group consistency | Submission container | forward_fill | YES | N/A | - | - | Groups documents together |
| 11 | [Submission_Session_Revision](#sequence-columns) | P1 | ❌ | string(2-digit) | Source Tracking | P1 | Meta | `^[0-9]{2}$` | Revision within session | forward_fill | YES | N/A | - | - | Sequential within session |
| 12 | [Submission_Session_Subject](#text-columns) | P1 | ❌ | string | Source Tracking | P1 | Meta | min_length: 2 | Session description | multi_level_ff | YES | N/A | - | - | Two-level forward fill |
| 13 | [Consolidated_Submission_Session_Subject](#text-columns) | P3 | ✅ | string | Aggregate | P3 | Derived | Concatenated | Consolidated subjects | calculated | NO | Preserves | Session_Subject, Doc_ID | **FK → Document_ID** | Aggregate unique subjects |
| 14 | [Department](#code-columns) | P1 | ❌ | categorical | Org Metadata | P1/P2.5 | Meta | department_schema | Originating department | multi_level_ff | YES | N/A | - | - | 8,132 nulls (81%) in pipeline |
| 15 | [Submitted_By](#code-columns) | P1 | ❌ | string | Source Tracking | P2.5 | Meta | department_schema | Submitter identity | forward_fill | YES | N/A | - | - | 8,167 nulls (74%) in pipeline |
| 16 | [Submission_Date](#date-columns) | P1 | ❌ | date | Source Tracking | P1 | Meta | **Required**, YYYY-MM-DD | Transaction timestamp | required | YES | N/A | - | - | **Cannot be null** - temporal anchor |
| 17 | [First_Submission_Date](#date-columns) | P3 | ✅ | date | Aggregate | P3 | Derived | Aggregate MIN | First submission per document | calculated | NO | Preserves | Submission_Date, Doc_ID | **FK → Document_ID** | MIN(Submission_Date) |
| 18 | [Latest_Submission_Date](#date-columns) | P3 | ✅ | date | Aggregate | P3 | Derived | Aggregate MAX | Latest submission per document | calculated | NO | Preserves | Submission_Date, Doc_ID | **FK → Document_ID** | MAX(Submission_Date) |
| 19 | [Latest_Revision](#sequence-columns) | P2.5 | ✅ | string | **ANOMALY** | P2.5 | Anomaly | `^[A-Z0-9.]*$` | **Calculated revision control** | calculated | NO | Preserves | Document_Revision, Doc_ID | **FK → Document_ID** | Aggregate: MAX revision |
| 20 | [All_Submission_Sessions](#json-columns) | P3 | ✅ | string | Aggregate | P3 | Derived | Concat `&&` | All sessions per document | calculated | NO | Preserves | Submission_Session, Doc_ID | **FK → Document_ID** | Unique concatenation |
| 21 | [All_Submission_Dates](#json-columns) | P3 | ✅ | string | Aggregate | P3 | Derived | Concat `,` sorted | All dates per document | calculated | NO | Preserves | Submission_Date, Doc_ID | **FK → Document_ID** | Sorted concatenation |
| 22 | [All_Submission_Session_Revisions](#json-columns) | P3 | ✅ | string | Aggregate | P3 | Derived | Concat `,` unique | All revisions per document | calculated | NO | Preserves | Revision, Doc_ID | **FK → Document_ID** | Unique sorted |
| 23 | [Count_of_Submissions](#numeric-columns) | P3 | ✅ | numeric | Aggregate | P3 | Derived | Range: 1-100 | Total submissions count | calculated | NO | Preserves | Doc_ID | **FK → Document_ID** | COUNT per Document_ID |
| 24 | [Reviewer](#code-columns) | P2 | ❌ | string | Workflow | P2 | Transactional | department_schema, Allow null | Assigned reviewer | forward_fill | YES | N/A | - | - | Missing in source data |
| 25 | [Review_Return_Actual_Date](#date-columns) | P1 | ❌ | date | Workflow Date | P1 | Transactional | **Required**, >= Submission_Date | Actual return date | required | YES | N/A | - | - | Business days calculation source |
| 26 | [Review_Return_Plan_Date](#date-columns) | P3 | ✅ | date | Workflow Date | P3 | Derived | >= Submission_Date | First/second review duration | calculated | NO | Preserves | Submission_Date, count | - | Conditional date logic |
| 27 | [Review_Status](#status-columns) | P2 | ❌ | categorical | Workflow Status | P2.5 | Transactional | approval_code_schema, Allow null | Current review state | forward_fill | YES | N/A | - | - | 20 values not in schema |
| 28 | [Review_Status_Code](#status-columns) | P2.5 | ✅ | categorical | **ANOMALY** | P2.5 | Anomaly | Mapped from Review_Status | **Calculated but transactional** | derived | NO | Preserves | Review_Status | - | Process immediately after Review_Status |
| 29 | [Approval_Code](#status-columns) | P2.5 | ✅ | categorical | Workflow Status | P2.5 | Derived | approval_code_schema | Mapped approval code | forward_fill | NO | Preserves | Review_Status | - | Status → Code mapping |
| 30 | [Review_Comments](#text-columns) | P2 | ❌ | string | Workflow Data | P2.5 | Transactional | Allow null | Review feedback | multi_level_ff | YES | NO | - | - | Multi-level forward fill |
| 31 | [Latest_Approval_Status](#status-columns) | P3 | ✅ | categorical | Aggregate | P3 | Derived | approval_code_schema | Latest non-PEN status | calculated | NO | Preserves | Review_Status, Doc_ID, Date | **FK → Document_ID** | 14 values not in schema |
| 32 | [Latest_Approval_Code](#status-columns) | P3 | ✅ | categorical | Mapping | P3 | Derived | approval_code_schema | Mapped latest code | calculated | NO | Preserves | Latest_Approval_Status | **FK → Document_ID** | Last non-null per Doc_ID |
| 33 | [All_Approval_Code](#json-columns) | P3 | ✅ | string | Aggregate | P3 | Derived | Concat `,` unique | All approval codes | calculated | NO | Preserves | Approval_Code, Doc_ID | **FK → Document_ID** | Unique per Document_ID |
| 34 | [Duration_of_Review](#numeric-columns) | P3 | ✅ | numeric | Conditional | P3 | Derived | Range: 0-365 business days | Business days calculation | calculated | NO | Preserves | Sub_Date, Review_Date | - | 4 values > 365 flagged |
| 35 | [Resubmission_Required](#status-columns) | P3 | ✅ | categorical | Conditional | P3 | Derived | YES/NO/RESUBMITTED/PENDING | Resubmission evaluation | calculated | NO | Preserves | Review_Date, Revision | - | Based on REJ in Review_Status |
| 36 | [Submission_Closed](#status-columns) | P3 | ✅ | categorical | Conditional | P3 | Derived | YES/NO | **ONLY Priority 3 with Manual Input** | conditional | **YES** | Preserves | Latest_Approval_Code, Date | **FK → Document_ID** | 2-step: fill if user value, else calc |
| 37 | [Resubmission_Plan_Date](#date-columns) | P3 | ✅ | date | Conditional | P3 | Derived | NULL if Submission_Closed=YES | Due date for resubmission | calculated | NO | Preserves | Sub_Date, Review_Date, Closed | **FK → Document_ID** | 1,707 → null (closed) |
| 38 | [Resubmission_Forecast_Date](#date-columns) | P2 | ❌ | date | **User Estimate** | P1 | Transactional | YYYY-MM-DD, Allow null | User estimate input | user_provided | YES | NO | - | - | **Forward fill within boundary allowed** |
| 39 | [Resubmission_Overdue_Status](#status-columns) | P3 | ✅ | categorical | Conditional | P3 | Derived | Overdue/Resubmitted/NO | Overdue evaluation | calculated | NO | Preserves | Plan_Date, today | **FK → Document_ID** | 241 rows marked Overdue |
| 40 | [Delay_of_Resubmission](#numeric-columns) | P3 | ✅ | numeric | Complex Lookup | P3 | Derived | Range: 0-365 | Days delayed calculation | calculated | NO | Preserves | Previous submission history | **FK → Document_ID** | **239 negative values = ERROR** |
| 41 | [Notes](#text-columns) | P1 | ❌ | string | Transactional | P1 | Meta | Allow null | Additional notes | leave_null | YES | NO | - | - | Optional field |
| 42 | [Submission_Reference_1](#text-columns) | P1 | ❌ | string | Transactional | P1 | Meta | Allow null | External reference | leave_null | YES | NO | - | - | Optional field |
| 43 | [Internal_Reference](#text-columns) | P1 | ❌ | string | Transactional | P1 | Meta | Allow null | Internal tracking | leave_null | YES | NO | - | - | Optional field |
| 44 | [This_Submission_Approval_Code](#status-columns) | P3 | ✅ | categorical | Conditional | P3 | Derived | approval_code_schema | Current submission approval | calculated | NO | Preserves | Latest_Code, Sub_Date, Latest_Date | **FK → Document_ID** | If is_current_submission |
| 45 | [Row_Index](#id-columns) | P1 | ✅ | numeric | **UNIQUE** | P1 | Meta | Auto-increment >= 1 | **UNIQUE row identifier** | auto_gen | NO | YES | Auto-increment | **ALTERNATE KEY** | **Only unique field** (per Rule 3) |
| 46 | [Document_ID_Affixes](#text-columns) | P3 | ✅ | string | Extracted | P3 | Derived | Suffix extraction | Document_ID suffixes | extracted | NO | Preserves | Document_ID | **FK → Document_ID** | 1,638 affixes extracted |
| 47 | [Validation_Errors](#json-columns) | P4 | ✅ | string | Error Tracking | P4 | Validation | Concat `;` all errors | Aggregated validation errors | aggregated | NO | **YES** | All columns | **FK → Document_ID** | **Rebuilds each run** |
| 48 | [Data_Health_Score](#score-columns) | P4 | ✅ | numeric | Score | P4 | Validation | Range: 0-100 | Weighted error sum | calculated | NO | Preserves | Validation_Errors | **FK → Document_ID** | 98.5% avg (Grade A) |

### Date Requirements Summary

| Date Column | Phase | Constraint | Calculation Logic |
|-------------|-------|------------|-------------------|
| Submission_Date | P1 | **Required**, YYYY-MM-DD | User input |
| First_Submission_Date | P3 | Aggregate | MIN(Submission_Date) per Document_ID |
| Latest_Submission_Date | P3 | Aggregate | MAX(Submission_Date) per Document_ID |
| Review_Return_Actual_Date | P1 | >= Submission_Date | User input, business days calc |
| Review_Return_Plan_Date | P3 | >= Submission_Date | Conditional: First/second review duration |
| Resubmission_Plan_Date | P3 | NULL if Submission_Closed=YES | Conditional date logic |
| Resubmission_Forecast_Date | P1 | User estimate | Forward fill within boundary allowed |

### Legend

| Column | Description |
|--------|-------------|
| **Priority** | Processing priority: P1=Meta Data, P2=Transactional, P2.5=Anomaly, P3=Derived, P4=Validation |
| **Calc** | ✅ = Calculated (system generated), ❌ = Not calculated (user input or static) |
| **Data Type** | Specific data type: categorical, string(N-digit), date, numeric, etc. |
| **Category** | Functional category: Project ID, Org Metadata, Unique ID, Workflow, Aggregate, etc. |
| **Phase** | Processing phase: P1, P2, P2.5, P3, P4 |
| **Group** | Column group: Meta, Identity, Anomaly, Transactional, Derived, Validation |
| **Constraint** | Validation constraints: Pattern, schema reference, Required, Range, Allow null |
| **Business Logic** | Description of the business rule or calculation logic |
| **Null Handling** | Strategy: default, forward_fill, multi_level_ff, required, calculated, leave_null |
| **Manual** | Manual Input: YES = User can provide value, NO = System calculated only |
| **Overwrites** | Data preservation: Preserves = Only fills nulls, YES = Rebuilds each run, N/A = Not applicable |
| **Dependencies** | Column dependencies for calculated fields |
| **Foreign Key** | Key relationship: **PK Component** (part of composite PK), **PRIMARY KEY**, **FK → Document_ID**, **ALTERNATE KEY**, or "-" |
| **Notes** | Additional notes, pipeline findings, special handling |

**Abbreviations:** P=Project_Code, F=Facility_Code, T=Document_Type, D=Discipline, S=Document_Sequence_Number

---

## Key Relationships & Data Model

### Primary Key Structure

The DCC Register uses a **composite primary key** pattern:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT_ID COMPOSITE KEY                            │
├─────────────────────────────────────────────────────────────────────────┤
│ Document_ID = {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number} │
│                      ↑              ↑              ↑            ↑                  ↑              │
│                   PK Comp         PK Comp        PK Comp      PK Comp             PK Comp           │
│                   (P1)            (P1)           (P1)         (P1)                (P2)              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Types Summary

| Key Type | Column(s) | Description |
|----------|-----------|-------------|
| **PK Components** (5) | Project_Code, Facility_Code, Document_Type, Discipline, Document_Sequence_Number | Components that constitute Document_ID |
| **PRIMARY KEY** (1) | Document_ID | Calculated composite key (can have duplicates per submission) |
| **ALTERNATE KEY** (1) | Row_Index | **ONLY truly unique field** per Rule 3 (auto-increment) |
| **Foreign Keys** (16) | All aggregate columns | Reference Document_ID for GROUP BY operations |

### Foreign Key Relationships

16 columns have **FK → Document_ID** relationships:

**Aggregate Columns (13):**
- Consolidated_Submission_Session_Subject
- First_Submission_Date, Latest_Submission_Date
- All_Submission_Sessions, All_Submission_Dates, All_Submission_Session_Revisions
- Count_of_Submissions
- Latest_Revision
- Latest_Approval_Status, Latest_Approval_Code, All_Approval_Code
- Document_ID_Affixes

**Conditional/Status Columns (3):**
- Submission_Closed, Resubmission_Plan_Date, Resubmission_Overdue_Status

**Validation Columns (2):**
- Validation_Errors, Data_Health_Score

### Important Notes

1. **Document_ID is NOT unique** - Multiple rows can have same Document_ID (resubmissions)
2. **Row_Index IS unique** - Auto-generated sequential number, true primary key
3. **All aggregates GROUP BY Document_ID** - Document history aggregation point
4. **FK relationships are implicit** - Calculations reference Document_ID for grouping

---

## Table of Contents

1. [Data Processing Pipeline Rules](#1-data-processing-pipeline-rules)
2. [Column Rules by Type](#2-column-rules-by-type) (Consolidated)
3. [Validation Rules by Category](#3-validation-rules-by-category)
4. [Row-Level Integrity Rules](#4-row-level-integrity-rules)
5. [Error Codes & Severity](#5-error-codes--severity)
6. [Success Metrics & Thresholds](#6-success-metrics--thresholds)
7. [Appendix A: Full Column Details](#appendix-a-full-column-details)

---

## 1. Data Processing Pipeline Rules

### 1.1 Processing Phase Order (Sequential)

| Phase | Name | Description | Rules Applied |
|-------|------|-------------|---------------|
| P1 | Anchor Processing | Process anchor columns (Project, Facility, Type, Discipline) | Required field validation, schema reference |
| P2 | Identity Processing | Process identity columns (Document_ID, Sequence, Revision) | Pattern validation, composite ID generation |
| P2.5 | Fill Processing | Apply null handling strategies | Forward fill, multi-level fill, default values |
| P3 | Calculation Processing | Compute derived columns | Date arithmetic, aggregates, conditionals |
| P4 | Validation Processing | Validate all columns and rows | Pattern, range, schema, cross-field validation |

**Critical Rule:** ALL validations MUST be performed AFTER Phase 3 completes (fully processed data only).

### 1.2 Null Handling Strategy Rules

| Strategy | Applicable Columns | Rule |
|----------|-------------------|------|
| forward_fill | Submission_Session, Submission_Session_Revision | Fill within group_by boundaries only |
| multi_level_forward_fill | Submission_Session_Subject, Review_Comments | Try multiple grouping levels, final_fill = "NA" |
| default_value | Project_Code, Facility_Code, Document_Type, Discipline | Fill nulls with "NA" for ID construction |
| leave_null | Transmittal_Number, Notes | Allow nulls if not required |
| bounded_forward_fill | Department, Submitted_By | Fill within Document_ID group only |

### 1.3 Zero-Padding Rules

| Column | Digits | Rule |
|--------|--------|------|
| Document_Sequence_Number | 4 | Must be 4-digit zero-padded (0001-9999) |
| Submission_Session | 6 | Must be 6-digit zero-padded (000001-999999) |
| Submission_Session_Revision | 2 | Must be 2-digit zero-padded (00-99) |
| Document_Revision | 2 | Must be 2-digit zero-padded (00-99) |
| Latest_Revision | 2 | Must be 2-digit zero-padded (00-99) |

---

## 2. Column Rules by Type

Consolidated rules by column type. **See Master Table** above for column-to-type mapping.

<a id="id-columns"></a>
### 2.1 ID Columns (3 columns)

| Column | Data Type | Pattern | Null Allowed |
|--------|-----------|---------|--------------|
| Document_ID | string | `PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE` | NO |
| Row_Index | numeric | Auto-generated starting from 1 | NO |
| Transmittal_Number | string | `^[A-Z0-9-]*$` | YES (default: "NA") |

**Critical Rules:**
- Document_ID: Cannot be null (41 nulls = CRITICAL error)
- Row_Index: Auto-generated sequential integer
- Transmittal_Number: Forward filled within Document_ID

<a id="code-columns"></a>
### 2.2 Code Columns (9 columns)

| Column | Schema Reference | Pattern | Null Handling |
|--------|-----------------|---------|---------------|
| Project_Code | project_code_schema | `^[A-Z0-9-]*$` | default_value = "NA" |
| Facility_Code | facility_schema | `^[A-Z0-9-]*$` | default_value = "NA" |
| Document_Type | document_type_schema | Schema enum | default_value = "NA" |
| Discipline | discipline_schema | Schema enum | default_value = "NA" |
| Department | department_schema | Schema enum | Multi-level forward fill |
| Approval_Code | approval_code_schema | Schema enum | Calculated |
| Review_Status_Code | approval_code_schema | Schema enum | Derived from Review_Status |
| Submitted_By | department_schema | Schema enum | Forward fill |
| Reviewer | department_schema | Schema enum | Forward fill |

**Critical Rules:**
- All code columns: Must exist in respective schema
- Project_Code: Document_ID component (segment 0)
- Schema failures: 20 Review_Status, 14 Latest_Approval_Status

<a id="date-columns"></a>
### 2.3 Date Columns (7 columns)

| Column | Format | Constraints |
|--------|--------|-------------|
| Submission_Date | YYYY-MM-DD | Required, no nulls |
| First_Submission_Date | YYYY-MM-DD | MIN(Submission_Date) per Document_ID |
| Latest_Submission_Date | YYYY-MM-DD | MAX(Submission_Date) per Document_ID |
| Review_Return_Actual_Date | YYYY-MM-DD | Must be >= Submission_Date |
| Review_Return_Plan_Date | YYYY-MM-DD | Must be >= Submission_Date |
| Resubmission_Plan_Date | YYYY-MM-DD | NULL if Submission_Closed = YES |
| Resubmission_Forecast_Date | YYYY-MM-DD | 305 format errors detected in pipeline |

**Critical Rules:**
- Group consistency: Submission_Date must be same within (Submission_Session, Submission_Session_Revision)
- Closure rule: If Submission_Closed = YES then Resubmission_Plan_Date = NULL

<a id="sequence-columns"></a>
### 2.4 Sequence Columns (5 columns)

| Column | Pattern | Zero-Pad | Validation |
|--------|---------|----------|------------|
| Document_Sequence_Number | `^[0-9]{4}$` | 4 digits | Must be numeric 4-digit |
| Submission_Session | `^[0-9]{6}$` | 6 digits | Group consistency with Submission_Date |
| Submission_Session_Revision | `^[0-9]{2}$` | 2 digits | Sequential within session |
| Document_Revision | `^[0-9]{2}$` | 2 digits | Pattern validation |
| Latest_Revision | `^[A-Z0-9.]*$` | N/A | Pattern validation |

**Critical Rules:**
- Document_Sequence_Number: Document_ID component (segment 4)
- Submission_Session: 6-digit zero-padded
- All sequence columns: Must match pattern after zero-padding

<a id="status-columns"></a>
### 2.5 Status Columns (6 columns)

| Column | Allowed Values | Default | Rule |
|--------|----------------|---------|------|
| Review_Status | approval_code_schema | From schema | Schema reference |
| Latest_Approval_Status | approval_code_schema | From schema | 14 schema failures detected |
| Resubmission_Required | YES, NO, RESUBMITTED, PENDING | Evaluate from Review_Status | Conditional logic |
| Submission_Closed | YES, NO | NO | Categorical |
| Resubmission_Overdue_Status | Resubmitted, Overdue, NO | Calculate from dates | Conditional logic |
| This_Submission_Approval_Code | approval_code_schema | Current row value | Conditional |

**Critical Rules:**
- Review_Status: 20 values not in schema = WARNING
- Resubmission_Required: Derived from Review_Status containing "REJ"
- Resubmission_Overdue_Status: 241 rows marked Overdue

<a id="numeric-columns"></a>
### 2.6 Numeric Columns (3 columns)

| Column | Min | Max | Calculation |
|--------|-----|-----|-------------|
| Duration_of_Review | 0 | 365 | Business days (Submission_Date to Review_Return_Actual_Date) |
| Delay_of_Resubmission | 0 | 365 | Days from Resubmission_Plan_Date (239 negative values = ERROR) |
| Count_of_Submissions | 1 | 100 | COUNT per Document_ID |

**Critical Rules:**
- Duration_of_Review: 4 values > 365 days flagged
- Delay_of_Resubmission: Negative values impossible (239 found = ERROR)

<a id="text-columns"></a>
### 2.7 Text Columns (8 columns)

| Column | Min Length | Null Handling |
|--------|------------|---------------|
| Document_Title | N/A | Required (missing in source - pipeline warning) |
| Review_Comments | N/A | Multi-level forward fill |
| Notes | N/A | Leave null allowed |
| Submission_Session_Subject | 2 | Multi-level forward fill |
| Consolidated_Submission_Session_Subject | N/A | Calculated (concatenate) |
| Submission_Reference_1 | N/A | Optional |
| Internal_Reference | N/A | Optional |
| Document_ID_Affixes | N/A | Extracted from Document_ID |

**Critical Rules:**
- Document_ID_Affixes: 1,638 affixes extracted (suffixes like "_Reply", "_ST607")
- Submission_Session_Subject: min_length 2, two-level forward fill

<a id="score-columns"></a>
### 2.8 Score Column (1 column)

| Column | Min | Max | Calculation |
|--------|-----|-----|-------------|
| Data_Health_Score | 0 | 100 | Weighted sum of validation errors (no handler warning in pipeline) |

**Critical Rules:**
- Calculated from Validation_Errors weighted sum
- Grade: A (95+), B (85-94), C (70-84), F (<70)
- Pipeline: 98.5% average (Grade A)

<a id="json-columns"></a>
### 2.9 JSON Columns (5 columns)

| Column | Format | Separator | Calculation |
|--------|--------|-----------|-------------|
| All_Submission_Sessions | Concatenated | && | Concatenate unique per Document_ID |
| All_Submission_Dates | Concatenated | , | Concatenate sorted per Document_ID |
| All_Submission_Session_Revisions | Concatenated | , | Concatenate unique sorted per Document_ID |
| All_Approval_Code | Concatenated | , | Concatenate unique per Document_ID |
| Validation_Errors | Concatenated | ; | Aggregate all errors per row |

**Critical Rules:**
- Validation_Errors: Aggregates all errors per row (1,238 total errors)
- All_* columns: Aggregate history per Document_ID

---

## 3. Validation Rules by Category

### 3.1 Integrity Gate Rules

#### Type Matching Rules
- All columns must match declared data_type in schema
- Implicit type conversion allowed for string columns
- Numeric columns must be parseable as numbers
- Date columns must be valid ISO 8601 format

#### Null Check Rules
**Critical Required Columns (NULL = CRITICAL ERROR):**
- Document_ID (41 nulls detected in pipeline = 0.4% error rate)
- Project_Code (4 nulls = 0.04%)
- Document_Type (71 nulls = 0.6%)
- Submission_Date (3 nulls = 0.03%)
- Document_Sequence_Number (63 nulls = 0.6%)
- Submission_Session (0 nulls after forward fill)
- Submission_Session_Revision (0 nulls after forward fill)

#### Pattern Validation Rules

| Column | Pattern | Pipeline Failures |
|--------|---------|-------------------|
| Project_Code | `^[A-Z0-9-]+$` | 43 invalid values |
| Document_Sequence_Number | `^[0-9]{4}$` | 1,638 invalid values |
| Submission_Session | `^[0-9]{6}$` | Group consistency check |
| Document_Revision | `^[0-9]{2}$` | 80 invalid values |
| Document_ID | Dynamic from 5 fields | 100 invalid values |

### 3.2 Domain Gate Rules

#### Schema Reference Rules

| Column | Reference | Entries | Failures |
|--------|-----------|---------|----------|
| Project_Code | project_code_schema | 2 projects | Validate existence |
| Facility_Code | facility_schema | 97 facilities | 69 nulls |
| Document_Type | document_type_schema | 15 types | 71 nulls |
| Discipline | discipline_schema | 15 disciplines | 67 nulls |
| Department | department_schema | 17 departments | 8,132 nulls (81%) |
| Approval_Code | approval_code_schema | 7 codes | Auto-populated |
| Review_Status | approval_code_schema | 7 codes | 20 not in schema |
| Submitted_By | department_schema | 17 departments | 8,167 nulls (74%) |

#### Range Validation Rules

| Column | Rule | Violations |
|--------|------|------------|
| Duration_of_Review | 0 <= value <= 365 | 4 values > 365 |
| Delay_of_Resubmission | 0 <= value <= 365 | 239 < 0, 347 > 365 |
| Count_of_Submissions | 1 <= value <= 100 | Aggregate check |
| Data_Health_Score | 0 <= value <= 100 | Score calculation |

#### Categorical Rules

| Column | Allowed Values | Violation Action |
|--------|----------------|------------------|
| Submission_Closed | YES, NO | Flag if other values |
| Resubmission_Required | YES, NO, RESUBMITTED, PENDING | Evaluate from Review_Status |
| Resubmission_Overdue_Status | Resubmitted, Overdue, NO | Calculate from dates |

### 3.3 Logic Gate Rules

#### Composite Identity Rules
**Document_ID must match:**
```
{Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}
```

Validation steps:
1. Split by "-" delimiter
2. Validate 5 segments match constituent columns
3. Extract affixes (suffixes like "_Reply", "_ST607")
4. Flag mismatch (100 invalid values in pipeline)

#### Date Consistency Rules

| Rule | Logic | Priority |
|------|-------|----------|
| Group Consistency | Submission_Date same within (Submission_Session, Submission_Session_Revision) | HIGH |
| Sequence | First_Submission_Date <= Submission_Date <= Latest_Submission_Date | HIGH |
| Response | Submission_Date <= Review_Return_Actual_Date | MEDIUM |
| Plan | Submission_Date <= Review_Return_Plan_Date | MEDIUM |
| Closure | If Submission_Closed = YES then Resubmission_Plan_Date = NULL | HIGH |

#### Cross-Reference Rules

| Column | Reference Column | Rule |
|--------|-----------------|------|
| Review_Status_Code | Review_Status | Map to code schema |
| Latest_Approval_Code | Approval_Code | Last non-null per Document_ID |
| This_Submission_Approval_Code | Approval_Code | Current row if is_current_submission |
| All_Approval_Code | Approval_Code | Concatenate unique per Document_ID |

---

## 4. Row-Level Integrity Rules

### 4.1 Anchor Completeness Rules

Critical fields must not be null:
- Document_ID (composite identity anchor)
- Project_Code (project classification)
- Document_Type (document categorization)
- Submission_Date (temporal anchor)
- Document_Sequence_Number (sequential identifier)

**Error Code:** P1-A-P-0101 (Null Anchor Column)
**Severity:** HIGH

### 4.2 Composite Identity Rules

**Rule:** Document_ID segments must match constituent fields exactly

```python
expected_segments = [
    Project_Code,      # Segment 0
    Facility_Code,   # Segment 1
    Document_Type,   # Segment 2
    Discipline,      # Segment 3
    Document_Sequence_Number  # Segment 4
]
```

**Error Code:** P2-I-V-0204 (Invalid Document_ID Format)
**Pipeline Findings:** 100 invalid values, 1,638 affixes extracted

### 4.3 Temporal Sequence Rules

| Rule | Validation | Error Code |
|------|------------|------------|
| Date Inversion | Submission_Date <= Review_Return_Actual_Date | L3-L-P-0301 |
| Group Consistency | Same Submission_Date within (Session, Revision) | GROUP_INCONSISTENT |
| Closure Date | NULL Resubmission_Plan_Date if Submission_Closed = YES | CLOSED_WITH_PLAN_DATE |
| Overdue | Mark Overdue if today > Resubmission_Plan_Date and not closed | OVERDUE_MISMATCH |

**Pipeline Findings:**
- 305 invalid date formats in Resubmission_Forecast_Date
- 4 Duration_of_Review > 365 days
- 239 Delay_of_Resubmission < 0 (impossible)

### 4.4 Categorical Inter-Dependency Rules

| Condition | Required State | Error Code |
|-----------|---------------|------------|
| Approval_Code in (APP, REJ) | Submission_Closed = YES | INCONSISTENT_CLOSURE |
| Review_Status contains REJ | Resubmission_Required in (YES, RESUBMITTED) | RESUBMISSION_MISMATCH |
| Today > Resubmission_Plan_Date | Resubmission_Overdue_Status = Overdue | OVERDUE_MISMATCH |

### 4.5 Status & Version Regression Rules

| Rule | Validation | Error Code |
|------|------------|------------|
| Revision Increment | Document_Revision must not decrease per Document_ID | L3-L-V-0302 |
| Status Conflict | Cannot be APPROVED and REJECTED simultaneously | L3-L-V-0303 |
| Version Gap | Submission_Session_Revision should be continuous | REVISION_GAP |

### 4.6 Relational Invariant Rules

| Rule | Group By | Validation |
|------|----------|------------|
| Subject Consistency | Submission_Session | Submission_Session_Subject must be same |
| Transmittal Consistency | Submission_Session | Transmittal_Number must be same |
| Fill Boundaries | Document_ID | Forward fill within Document_ID only |

---

## 5. Error Codes & Severity

### 5.1 Error Code Categories

| Category | Range | Phase | Description |
|----------|-------|-------|-------------|
| S1xx | S1-I-F-08xx | Initiation | Input file and schema errors |
| P1xx | P1-A-P-01xx | P1 | Anchor column errors |
| P2xx | P2-I-P-02xx | P2 | Identity column errors |
| F4xx | F4-C-F-04xx | P2.5 | Forward fill errors |
| L3xx | L3-L-P-03xx | P3 | Business logic errors |
| C6xx | C6-C-C-06xx | P3 | Calculation errors |
| V5xx | V5-I-V-05xx | P4 | Output validation errors |

### 5.2 Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | Data integrity compromised | Block processing |
| HIGH | Significant data quality issue | Flag for review |
| MEDIUM | Moderate quality concern | Log and continue |
| WARNING | Minor inconsistency | Log only |
| INFO | Informational | Dashboard only |

### 5.3 Critical Error Codes

| Code | Description | Severity |
|------|-------------|----------|
| S1-I-V-0502 | Missing required columns | CRITICAL |
| P1-A-P-0101 | Null anchor column | HIGH |
| P2-I-P-0201 | Document_ID null or empty | HIGH |
| P2-I-V-0204 | Document_ID format invalid | HIGH |
| L3-L-P-0301 | Date inversion | HIGH |
| F4-C-F-0401 | Forward fill row jump exceeded | HIGH |
| F4-C-F-0402 | Session boundary crossed | HIGH |

### 5.4 Row Health Score Weights

| Error Type | Weight | Description |
|------------|--------|-------------|
| ANCHOR_NULL | 25 | Critical missing data |
| COMPOSITE_MISMATCH | 20 | Identity integrity failure |
| GROUP_INCONSISTENT | 15 | Temporal consistency failure |
| VERSION_REGRESSION | 15 | Version integrity failure |
| INCONSISTENT_CLOSURE | 10 | Business rule violation |
| CLOSED_WITH_PLAN_DATE | 10 | Date logic violation |
| INCONSISTENT_SUBJECT | 5 | Relational invariant failure |
| OVERDUE_MISMATCH | 5 | Status logic failure |
| REVISION_GAP | 5 | Version gap |

**Scoring Formula:**
```python
score = max(0, 100 - sum(weights))
if score >= 95: grade = 'A'
elif score >= 85: grade = 'B'
elif score >= 70: grade = 'C'
else: grade = 'F'
```

---

## 6. Success Metrics & Thresholds

### 6.1 Column-Level Metrics

| Metric | Target | Current (Pipeline) | Status |
|--------|--------|-------------------|--------|
| Error rate | < 1% | 11% (1,238/11,099) | ⚠️ Needs improvement |
| Pattern pass rate | > 95% | ~85% | ⚠️ Below target |
| Schema match rate | > 98% | ~95% | ⚠️ Below target |
| Data Health Score | > 95% | 98.5% | ✅ Pass |

### 6.2 Row-Level Metrics

| Metric | Target | Current (Pipeline) | Status |
|--------|--------|-------------------|--------|
| Critical errors | < 0.1% | 0.04% (41 rows) | ✅ Pass |
| Composite identity match | > 99% | ~99% (100 mismatches) | ✅ Pass |
| Group consistency | > 99% | ~99.9% (1 violation) | ✅ Pass |
| Temporal violations | < 1% | < 0.1% | ✅ Pass |
| Overall health score | > 95% | 98.5% | ✅ Pass |

### 6.3 Pipeline Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Schema load time | < 500ms | 6.14ms max | ✅ Pass |
| Memory overhead | < 50MB | 0.88MB | ✅ Pass |
| Cache hit rate | > 80% | 86.6% | ✅ Pass |
| Processing time | N/A | 13.6s | ✅ Acceptable |

### 6.4 High Priority Issues

| Issue | Count | Action Required |
|-------|-------|-----------------|
| Document_Sequence_Number pattern failures | 1,638 | Review source data |
| Delay_of_Resubmission negative values | 239 | Fix calculation logic |
| Review_Status not in schema | 20 | Update approval codes |
| Latest_Approval_Status not in schema | 14 | Update approval codes |
| Missing Document_Title column | N/A | Add to source data |
| Missing Reviewer column | N/A | Add to source data |

---

## Appendix A: Full Column Details

Complete validation rules for all 48 columns. **See Master Table** at document start for quick reference.

### A.1 Anchor Columns (P1 Phase)

| Column | Data Type | Required | Null Handling | Validation | Error Code |
|--------|-----------|----------|---------------|------------|------------|
| Project_Code | categorical | Yes | default: "NA" | Pattern: `^[A-Z0-9-]*$`, Schema: project_code_schema | P1-A-P-0101 |
| Facility_Code | categorical | Yes | default: "NA" | Pattern: `^[A-Z0-9-]*$`, Schema: facility_schema | P1-A-P-0101 |
| Document_Type | categorical | Yes | default: "NA" | Schema: document_type_schema | P1-A-P-0101 |
| Discipline | categorical | Yes | default: "NA" | Schema: discipline_schema | P1-A-P-0101 |
| Submission_Session | string | Yes | forward_fill, zero_pad: 6 | Pattern: `^[0-9]{6}$`, Group consistency | P1-A-V-0102 |
| Submission_Session_Revision | string | Yes | forward_fill, zero_pad: 2 | Pattern: `^[0-9]{2}$` | P1-A-V-0102 |
| Submission_Session_Subject | string | Yes | multi_level_ff | min_length: 2 | - |
| Submission_Date | date | Yes | required | Format: YYYY-MM-DD, No nulls | P1-A-V-0103 |
| Transmittal_Number | string | No | default: "NA" | Pattern: `^[A-Z0-9-]*$` | - |

### A.2 Identity Columns (P2 Phase)

| Column | Data Type | Required | Null Handling | Validation | Error Code |
|--------|-----------|----------|---------------|------------|------------|
| Document_Sequence_Number | string | Yes | zero_pad: 4 | Pattern: `^[0-9]{4}$` | P2-I-P-0202 |
| Document_ID | string | Yes | composite | Pattern: `{P}-{F}-{T}-{D}-{S}` | P2-I-P-0201 |
| Document_Revision | string | Yes | forward_fill | Pattern: `^[0-9]{2}$` | P2-I-P-0202 |
| Document_Title | string | No | leave_null | Required (missing in source) | - |
| Row_Index | numeric | Yes | auto_gen | Min: 1 | - |

### A.3 Fill Columns (P2.5 Phase)

| Column | Data Type | Required | Null Handling | Validation | Pipeline Issues |
|--------|-----------|----------|---------------|------------|-----------------|
| Department | categorical | No | multi_level_ff | Schema: department_schema | 8,132 nulls (81%) |
| Submitted_By | categorical | No | forward_fill | Schema: department_schema | 8,167 nulls (74%) |
| Reviewer | categorical | No | forward_fill | Schema: department_schema | Missing in source |
| Review_Status | categorical | No | forward_fill | Schema: approval_code_schema | 20 not in schema |
| Review_Status_Code | categorical | No | derived | Schema: approval_code_schema | Derived mapping |
| Approval_Code | categorical | No | forward_fill | Schema: approval_code_schema | Auto-populated |
| Review_Comments | string | No | multi_level_ff | N/A | Multi-level fill |

### A.4 Calculated Columns (P3 Phase)

| Column | Data Type | Calculation | Validation | Pipeline Issues |
|--------|-----------|-------------|------------|-----------------|
| First_Submission_Date | date | MIN(Submission_Date) per Document_ID | YYYY-MM-DD | - |
| Latest_Submission_Date | date | MAX(Submission_Date) per Document_ID | YYYY-MM-DD | - |
| Latest_Revision | string | MAX(Document_Revision) per Document_ID | Pattern: `^[A-Z0-9.]*$` | 63 pattern failures |
| All_Submission_Sessions | string | Concatenate unique `&&` | Concatenated | - |
| All_Submission_Dates | string | Concatenate sorted `,` | Concatenated | - |
| All_Submission_Session_Revisions | string | Concatenate unique sorted `,` | Concatenated | - |
| Count_of_Submissions | numeric | COUNT per Document_ID | Range: 1-100 | - |
| Consolidated_Submission_Session_Subject | string | Concatenate | Concatenated | - |
| Duration_of_Review | numeric | Business days | Range: 0-365 | 4 values > 365 |
| Resubmission_Required | categorical | Conditional from Review_Status | YES/NO/RESUB/PENDING | Evaluated |
| Submission_Closed | categorical | Conditional | YES/NO | Default: NO |
| Resubmission_Plan_Date | date | Conditional | NULL if closed | 1707→null |
| Resubmission_Overdue_Status | categorical | Calculated from dates | Overdue/Resub/NO | 241 Overdue |
| Delay_of_Resubmission | numeric | Days from plan date | Range: 0-365 | 239 negative |
| Latest_Approval_Status | categorical | Last non-null | approval_code_schema | 14 not in schema |
| Latest_Approval_Code | categorical | Last non-null | approval_code_schema | - |
| All_Approval_Code | string | Concatenate unique `,` | Concatenated | - |
| This_Submission_Approval_Code | categorical | Current if is_current | approval_code_schema | Conditional |
| Document_ID_Affixes | string | Extracted suffixes | Suffixes | 1,638 extracted |

### A.5 Validation Columns (P4 Phase)

| Column | Data Type | Calculation | Validation |
|--------|-----------|-------------|------------|
| Validation_Errors | string | Aggregate all errors | Concatenated `;` |
| Data_Health_Score | numeric | Weighted sum of errors | Range: 0-100 |

### A.6 Reference Columns (P1 Phase - Optional)

| Column | Data Type | Required | Null Handling | Validation |
|--------|-----------|----------|---------------|------------|
| Resubmission_Forecast_Date | date | No | user_provided | YYYY-MM-DD |
| Notes | string | No | leave_null | N/A |
| Submission_Reference_1 | string | No | leave_null | N/A |
| Internal_Reference | string | No | leave_null | N/A |

---

## Appendix: Column Summary

**Total Columns:** 48 (including Data_Health_Score)

**By Type:**
- ID columns: 3
- Code columns: 9
- Date columns: 7
- Sequence columns: 5
- Status columns: 6
- Numeric columns: 3
- Text columns: 8
- Score columns: 1
- JSON columns: 5

**By Processing Phase:**
- P1 (Anchor): 10 columns
- P2 (Identity): 5 columns
- P2.5 (Fill): 8 columns
- P3 (Calculation): 18 columns
- P4 (Validation): All columns

---

*Document compiled from:*
- col_validation_workplan.md
- row_validation_workplan.md
- error_code_reference.md
- dcc_register_config.json
- phase_10_report.md
- processing_summary.txt
- All detector documentation

*Last Compiled:* 2026-04-18
*Version:* 1.0
*Total Rules Extracted:* 100+
