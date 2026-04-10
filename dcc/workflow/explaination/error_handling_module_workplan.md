# DCC Column Data Error Handling Module - Work Plan (Updated)

**Version:** 2.2  
**Date:** April 10, 2026  
**Status:** Planning Phase  
**Based on:** `data_error_handling.md` and `processing_pipeline_issues.md`
**Core Philosophy:** **"Fail Fast, Inform Well, Resolve Smart"**
**Pattern:** **Decorator/Interceptor Pattern (AOP-style)**
**Architecture:** **Pure JSON Configuration (Option B)**

---

## Executive Summary

This work plan outlines the implementation of a comprehensive **Column Data Error Handling Module** for the DCC Pipeline. The module follows the **"Fail Fast, Inform Well"** philosophy, providing structured error taxonomy with multi-layer validation, comprehensive logging, and localized error messages.

### Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Fail Fast** | Detect errors at earliest possible layer; stop on critical errors |
| **Inform Well** | Rich error context with actionable details; multiple output formats |
| **Resolve Smart** | Error status tracking, suppression logic, remediation workflows |
| **Structured Taxonomy** | Hierarchical error classification (Engine → Module → Function → ID) |
| **Multi-Layer Validation** | Input validation → Schema validation → Business logic validation |
| **Interceptor Pattern** | AOP-style decorators instead of if/else in every calculation |
| **Log Everything** | Comprehensive logging at all layers with structured output |
| **Localization Ready** | Message templates separated from code; i18n support |

### Goals
1. Detect errors at the earliest possible layer (fail fast)
2. Provide rich, actionable error context (inform well)
3. Track error status: Open → Suppressed → Resolved → Archived
4. Implement suppression logic for "wrong but acceptable" errors
5. Define remediation types: auto-fix, manual-fix, suppress, escalate
6. Use JSON-based error registry for maintainability
7. Implement structured error code anatomy (E-M-F-U)
8. Enable multi-layer validation strategy (L0/L1/L2/L2.5/L3/L4/L5) ← EXPANDED
9. Use decorator/interceptor pattern instead of if/else in calculations
10. Build resolution module for categorizing, dispatching, and archiving
11. **Calculate Data Health KPI:** (Total - Critical - High) / Total × 100 ← NEW
12. **Handle null_handling data errors:** F4xx errors via decorator pattern ← NEW
13. **Use JSON Schema for taxonomy validation** ← NEW
14. Log everything with structured format
15. Support localization of error details
16. Integrate seamlessly with phased processing (P1→P2→P2.5→P3)

---

## 1. Architecture Overview

### 1.1 Module Structure (Pure JSON Architecture - Option B)

```
processor_engine/
├── error_handling/              # NEW MODULE
│   ├── __init__.py              # Public exports
│   ├── config/                  # ALL CONFIGURATION IN JSON ← UPDATED
│   │   ├── __init__.py
│   │   ├── error_codes.json     # Error registry (24 codes)
│   │   ├── taxonomy.json        # Engine/Module/Function/Family definitions
│   │   ├── status_lifecycle.json # Status states & transitions
│   │   ├── anatomy_schema.json  # JSON Schema for E-M-F-U validation
│   │   ├── remediation_types.json # 8 remediation strategies
│   │   ├── suppression_rules.json # Suppression configuration
│   │   └── messages/            # Localization files
│   │       ├── en.json
│   │       └── zh.json
│   ├── core/                    # JSON loaders & runtime
│   │   ├── __init__.py
│   │   ├── registry.py          # Load error_codes.json
│   │   ├── taxonomy_loader.py   # Load taxonomy.json ← NEW
│   │   ├── status_loader.py     # Load status_lifecycle.json ← NEW
│   │   ├── anatomy_loader.py    # Validate & load anatomy_schema.json ← NEW
│   │   ├── remediation_loader.py # Load remediation_types.json ← NEW
│   │   ├── validator.py         # JSON Schema validation ← NEW
│   │   ├── logger.py            # Structured logging
│   │   └── interceptor.py       # Decorator/interceptor framework
│   ├── exceptions/              # Global exception handling
│   │   ├── __init__.py
│   │   ├── base.py              # Base exception classes
│   │   ├── engine.py            # Engine-level exceptions
│   │   ├── validation.py        # Validation exceptions
│   │   └── calculation.py       # Calculation exceptions
│   ├── detectors/               # Error detection functions
│   │   ├── __init__.py
│   │   ├── input.py             # Layer 1: Input validation
│   │   ├── schema.py            # Layer 2: Schema validation
│   │   ├── business.py          # Layer 3: Business logic
│   │   ├── anchor.py            # P1xx errors
│   │   ├── identity.py          # P2xx errors
│   │   ├── logic.py             # L3xx errors
│   │   ├── fill.py              # F4xx warnings
│   │   ├── validation.py        # V5xx errors
│   │   └── calculation.py       # C6xx errors
│   ├── resolution/              # Error resolution workflow
│   │   ├── __init__.py
│   │   ├── categorizer.py       # Auto-categorize errors
│   │   ├── dispatcher.py        # Route to appropriate handler
│   │   ├── suppressor.py        # Suppression logic & rules
│   │   ├── remediator.py        # Apply remediation strategies
│   │   ├── archiver.py          # Archive resolved errors
│   │   └── status_manager.py    # Status lifecycle management
│   ├── decorators/              # AOP-style decorators
│   │   ├── __init__.py
│   │   ├── validate.py          # @validate decorator
│   │   ├── track_errors.py      # @track_errors decorator
│   │   ├── log_execution.py     # @log_execution decorator
│   │   └── suppressible.py      # @suppressible decorator
│   ├── aggregator.py            # Row-level error aggregation
│   ├── formatter.py             # Error formatting for UI
│   ├── localizer.py             # Message localization (JSON-based)
│   └── tracker.py               # Phase-level error tracking
└── ...
```

**Key Change:** All definitions in `config/*.json`, runtime in `core/*_loader.py`

### 1.1a Architecture Decision: Python vs JSON for Core Definitions

You raise a valid question: **Why use Python files (.py) for taxonomy, status, anatomy, remediation types instead of pure JSON?**

#### Current Hybrid Approach (Proposed in v2.2)

| Component | Format | Reason |
|-----------|--------|--------|
| **Error Codes Registry** | JSON (`error_codes.json`) | Hot-reloadable, user-editable |
| **Suppression Rules** | JSON (`suppression_rules.json`) | Business rules, user-configurable |
| **Localization Messages** | JSON (`messages/*.json`) | Translators can edit without code |
| **Taxonomy Schema** | JSON Schema (`taxonomy_schema.json`) | Validation, documentation |
| **Taxonomy Enums** | Python (`taxonomy.py`) | IDE autocomplete, type safety |
| **Status Lifecycle** | Python (`status.py`) | State machine logic, methods |
| **Anatomy Dataclass** | Python (`anatomy.py`) | Type hints, validation methods |
| **Remediation Types** | Python (`remediation.py`) | Strategy pattern, polymorphism |

#### Alternative: Pure JSON Architecture

All definitions could be moved to JSON files:

```
config/
├── error_codes.json          # Already JSON
├── suppression_rules.json    # Already JSON
├── taxonomy.json             # ← Alternative to taxonomy.py
├── status_lifecycle.json     # ← Alternative to status.py
├── anatomy_schema.json       # ← Alternative to anatomy.py
├── remediation_types.json    # ← Alternative to remediation.py
└── messages/
    ├── en.json               # Already JSON
    └── zh.json               # Already JSON
```

**Example: `config/taxonomy.json`**
```json
{
  "engines": {
    "P": {"name": "Processor", "description": "Main processing engine"},
    "M": {"name": "Mapper", "description": "Column mapping engine"}
  },
  "modules": {
    "C": {"name": "Core", "description": "Core processing"},
    "V": {"name": "Validation", "description": "Validation logic"}
  },
  "functions": {
    "P": {"name": "Process", "description": "Processing function"},
    "V": {"name": "Validate", "description": "Validation function"}
  },
  "families": {
    "1": {"name": "Anchor", "layer": "L3", "description": "Priority column errors"}
  }
}
```

**Example: `config/status_lifecycle.json`**
```json
{
  "states": ["OPEN", "SUPPRESSED", "RESOLVED", "ARCHIVED", "ESCALATED", "PENDING", "REOPEN"],
  "transitions": {
    "OPEN": ["SUPPRESSED", "RESOLVED", "ESCALATED"],
    "SUPPRESSED": ["RESOLVED", "REOPEN"],
    "RESOLVED": ["ARCHIVED", "REOPEN"]
  },
  "initial_state": "OPEN",
  "terminal_states": ["ARCHIVED"]
}
```

#### Comparison

| Aspect | Python Approach | JSON Approach |
|--------|-----------------|---------------|
| **Type Safety** | ✅ Native (dataclasses, enums) | ❌ Requires schema validation |
| **IDE Support** | ✅ Autocomplete, type hints | ❌ Limited |
| **Hot Reload** | ❌ Requires restart | ✅ Load on demand |
| **Runtime Validation** | ✅ Python validates | ❌ Need jsonschema library |
| **User Editing** | ❌ Need Python knowledge | ✅ Business users can edit |
| **Version Control** | ✅ Both work | ✅ Both work |
| **Performance** | ✅ Slightly faster (compiled) | ⚠️ Slight parse overhead |
| **Flexibility** | ✅ Can add methods/logic | ⚠️ Data only |

#### Recommendation

**✅ SELECTED: Option B - Pure JSON Architecture**

All definitions moved to JSON for maximum flexibility and hot-reload capability:

| Component | Format | File |
|-----------|--------|------|
| **Error Codes** | JSON | `config/error_codes.json` |
| **Taxonomy** | JSON | `config/taxonomy.json` |
| **Status Lifecycle** | JSON | `config/status_lifecycle.json` |
| **Anatomy Schema** | JSON Schema | `config/anatomy_schema.json` |
| **Remediation Types** | JSON | `config/remediation_types.json` |
| **Suppression Rules** | JSON | `config/suppression_rules.json` |
| **Localization** | JSON | `config/messages/*.json` |

**Benefits:**
- ✅ Non-technical users can modify definitions
- ✅ Hot-reload of ALL definitions without restart
- ✅ Visual config editor can be built on top
- ✅ Single source of truth in `config/` folder
- ✅ Easy to version control and audit changes

**Implementation:** Python loader modules (`registry.py`, `taxonomy_loader.py`, etc.) parse JSON at runtime with validation.

---

### 1.2 Error Code Anatomy (E-M-F-U Format)

**New structured format: `E-M-F-XXXX`**

```
┌──────────┬──────────┬──────────┬──────────────┐
│  Engine  │  Module  │ Function │  Unique ID   │
│  (1 char)│  (1 char)│ (1 char) │  (4 digits)  │
└──────────┴──────────┴──────────┴──────────────┘
```

| Position | Meaning | Values |
|----------|---------|--------|
| **E** (Engine) | Processing engine | P=Processor, M=Mapper, I=Initiation, S=Schema, R=Reporting |
| **M** (Module) | Module within engine | C=Core, V=Validation, A=Aggregate, D=Date, etc. |
| **F** (Function) | Function type | P=Process, V=Validate, C=Calculate, F=Fill |
| **XXXX** (Unique ID) | Sequential number | 0001-9999 |

**Examples:**
- `P-C-P-0101` = Processor Engine → Core Module → Process Function → ID 0101
- `P-V-V-0501` = Processor Engine → Validation Module → Validate Function → ID 0501
- `P-A-C-0604` = Processor Engine → Aggregate Module → Calculate Function → ID 0604

### 1.3 Multi-Layer Validation Strategy (Expanded L0-L5)

```
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 0: TEMPLATE GUARD (L0)                    │
│  - Schema version verification                                   │
│  - Template signature validation                                 │
│  - Configuration compatibility check                             │
│  - Pre-flight validation before data load                        │
├─────────────────────────────────────────────────────────────────┤
│                    LAYER 1: INPUT VALIDATION                    │
│  - File existence, format, encoding                              │
│  - Column presence, header validation                            │
│  - Basic data type checks                                        │
│  - Early exit on critical failures                               │
├─────────────────────────────────────────────────────────────────┤
│                    LAYER 2: SCHEMA VALIDATION                     │
│  - Field-level validation (pattern, length, enum)                │
│  - Data type conformance                                         │
│  - Required field validation                                   │
│  - Foreign key validation                                        │
├─────────────────────────────────────────────────────────────────┤
│              LAYER 2.5: HISTORICAL LOOKUP (L2.5)               │
│  - Cross-session duplicate detection                             │
│  - Historical revision comparison                                │
│  - Temporal consistency validation                               │
│  - Previous submission reference validation                      │
├─────────────────────────────────────────────────────────────────┤
│                 LAYER 3: BUSINESS LOGIC VALIDATION               │
│  - Cross-column dependencies                                    │
│  - Chronological consistency                                     │
│  - Business rule compliance                                      │
│  - Calculation validation                                        │
├─────────────────────────────────────────────────────────────────┤
│                LAYER 4: APPROVAL HOOK (L4)                     │
│  - Manual overrule interface                                     │
│  - User-initiated suppression                                    │
│  - Approval workflow for "wrong but acceptable"                │
│  - Audit trail for human decisions                               │
├─────────────────────────────────────────────────────────────────┤
│              LAYER 5: METRIC AGGREGATOR (L5)                   │
│  - Calculate % Clean Run                                         │
│  - Data Health Score computation                                 │
│  - Trend analysis and reporting                                  │
│  - Final output validation                                       │
└─────────────────────────────────────────────────────────────────┘
```

**Fail Fast Implementation:**
- **L0 (Template):** Critical version mismatch stops processing immediately
- **L1 (Input):** File format errors stop processing immediately  
- **L2 (Schema):** Errors collect per row but continue
- **L2.5 (History):** Warnings for duplicates, can continue with flags
- **L3 (Business):** Errors collect per row with severity-based actions
- **L4 (Approval):** Interactive - pauses for human decision if configured
- **L5 (Metrics):** Always runs, calculates final quality scores

### 1.3a Error Status Lifecycle (NEW)

**Status States:**
```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  OPEN    │────▶│SUPPRESSED│────▶│ RESOLVED │────▶│ ARCHIVED │
│  (New)   │     │(Accepted)│     │  (Fixed) │     │ (Closed) │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      │                │                │
      │                │                │
      ▼                ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ESCALATED │     │ PENDING  │     │  REOPEN  │
│(Critical)│     │(Waiting) │     │ (Recur)  │
└──────────┘     └──────────┘     └──────────┘
```

| Status | Description | Transitions |
|--------|-------------|-------------|
| **OPEN** | Newly detected error, unreviewed | → SUPPRESSED, RESOLVED, ESCALATED |
| **SUPPRESSED** | Error acknowledged as "wrong but acceptable" | → RESOLVED, REOPEN |
| **RESOLVED** | Error fixed or remediated | → ARCHIVED, REOPEN |
| **ESCALATED** | Critical error requiring manual intervention | → RESOLVED |
| **PENDING** | Waiting for external action (e.g., user input) | → RESOLVED, REOPEN |
| **ARCHIVED** | Closed error kept for audit trail | → REOPEN |
| **REOPEN** | Previously resolved/suppressed error reoccurred | → SUPPRESSED, RESOLVED, ESCALATED |

**Storage:**
- `Error_Status` column in output (Step 47, after Validation_Errors)
- `error_history.json` for tracking status changes over time
- `error_archive/` folder for long-term storage

### 1.3b Suppression Logic (NEW)

**Suppression Rules Configuration (`config/suppression_rules.json`):**
```json
{
  "rules": [
    {
      "rule_id": "SUP-001",
      "name": "Legacy Date Format Tolerance",
      "description": "Accept dates in old format for legacy submissions",
      "error_codes": ["P-C-P-0103", "P-V-V-0504"],
      "conditions": {
        "submission_session_before": "20240101",
        "column": "Submission_Date"
      },
      "justification": "Historical data uses different date format",
      "approved_by": "system_admin",
      "expires_at": "2026-12-31",
      "severity_override": "WARNING"
    },
    {
      "rule_id": "SUP-002",
      "name": "Known Missing References",
      "error_codes": ["P-V-V-0506"],
      "conditions": {
        "document_type": ["MEM", "NTS"]
      },
      "justification": "Memo and notes don't require full discipline list",
      "approved_by": "dcc_manager"
    }
  ]
}
```

**Suppression Types:**
| Type | Description | Use Case |
|------|-------------|----------|
| **GLOBAL** | Suppress across all files/projects | System-wide known issue |
| **PROJECT** | Suppress for specific project code | Project-specific exception |
| **FILE** | Suppress for specific input file | One-time data import |
| **ROW** | Suppress for specific row/document | Document-level override |
| **TEMPORARY** | Time-bound suppression | Migration period, expires automatically |

**API:**
```python
# Check if error should be suppressed
suppressor = ErrorSuppressor()
is_suppressed = suppressor.check(error_code, context={
    "project_code": "PRJ001",
    "submission_session": "240315",
    "column": "Submission_Date",
    "value": "15/03/2024"
})

# Suppress with justification
suppressor.suppress(error_id, 
    reason="Known data migration issue",
    approved_by="john.doe@company.com",
    expires_at="2026-06-30"
)
```

### 1.3c Remediation Types (NEW)

**Remediation Strategy Framework:**

| Type | Code | Action | Auto/Manual | Example |
|------|------|--------|-------------|---------|
| **AUTO_FIX** | R001 | Automatically correct the error | Auto | Zero-pad sequence numbers |
| **MANUAL_FIX** | R002 | User must correct in source | Manual | Fix invalid project code |
| **SUPPRESS** | R003 | Accept as-is with justification | Semi | Legacy date format |
| **ESCALATE** | R004 | Route to expert/team | Manual | Business rule violation |
| **DERIVE** | R005 | Calculate correct value | Auto | Infer missing Document_ID |
| **DEFAULT** | R006 | Apply default value | Auto | Fill null with "NA" |
| **FILL_DOWN** | R007 | Forward fill from previous row | Auto | Fill missing reviewer |
| **AGGREGATE** | R008 | Calculate from related rows | Auto | Compute latest revision |

**Remediation Decision Matrix (`core/remediation.py`):**
```python
REMEDIATION_MATRIX = {
    "P-C-P-0101": {  # NULL_ANCHOR
        "default_strategy": "MANUAL_FIX",
        "auto_eligible": False,
        "escalation_required": True
    },
    "P-V-V-0501": {  # PATTERN_MISMATCH
        "default_strategy": "AUTO_FIX",
        "auto_eligible": True,
        "auto_action": "zero_pad",
        "fallback": "MANUAL_FIX"
    },
    "F4-C-F-0401": {  # JUMP_LIMIT
        "default_strategy": "SUPPRESS",
        "auto_eligible": True,
        "condition": "jump_size < 50"
    }
}
```

**Remediation Application:**
```python
@apply_remediation
 def process_column(df, column_config):
    # If error detected, automatically apply remediation
    # based on error code and configured strategy
    pass
```

### 1.3d Decorator/Interceptor Pattern (NEW)

**AOP-Style Decorators instead of if/else:**

**Before (Traditional):**
```python
def apply_null_handling(df, column):
    if column.null_handling.strategy == "forward_fill":
        # ... 20 lines of logic
    elif column.null_handling.strategy == "default_value":
        # ... 15 lines of logic
    elif column.null_handling.strategy == "multi_level":
        # ... 30 lines of logic
    # Error handling inline
    if df[column.name].isna().sum() > threshold:
        log_error(...)
```

**After (Interceptor Pattern):**
```python
@validate_input(schema=NullHandlingSchema)
@track_errors(error_family="Fill", layer="L3")
@log_execution(phase="P2")
@suppressible(rule_category="fill_warnings")
@apply_remediation(strategy="auto_fix")
def apply_null_handling(df, column):
    # Pure business logic - no error handling code
    return df[column.name].fillna(method='ffill')
```

**Decorator Stack:**
```
┌─────────────────────────────────────────────────────────────────┐
│  @suppressible()          ← Check suppression rules first        │
├─────────────────────────────────────────────────────────────────┤
│  @validate_input()        ← Validate input parameters            │
├─────────────────────────────────────────────────────────────────┤
│  @track_errors()          ← Detect & collect errors            │
├─────────────────────────────────────────────────────────────────┤
│  @apply_remediation()     ← Auto-fix if configured             │
├─────────────────────────────────────────────────────────────────┤
│  @update_status()         ← Update error status column         │
├─────────────────────────────────────────────────────────────────┤
│  @log_execution()         ← Log entry/exit with metrics        │
├─────────────────────────────────────────────────────────────────┤
│  def actual_function():   ← Pure business logic                │
└─────────────────────────────────────────────────────────────────┘
```

**Interceptor Implementation (`core/interceptor.py`):**
```python
class ErrorInterceptor:
    """
    AOP-style interceptor that wraps calculation functions
    with error handling, logging, and remediation.
    """
    
    def __init__(self):
        self.before_hooks = []
        self.after_hooks = []
        self.error_hooks = []
    
    def intercept(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = self._build_context(func, args, kwargs)
            
            # BEFORE: Validation, suppression check
            for hook in self.before_hooks:
                hook(context)
            
            try:
                # EXECUTE: Actual function
                result = func(*args, **kwargs)
                context['result'] = result
                
                # AFTER: Track success, update status
                for hook in self.after_hooks:
                    hook(context)
                    
            except Exception as e:
                context['exception'] = e
                
                # ERROR: Detect, log, remediate
                for hook in self.error_hooks:
                    hook(context)
                
                # Apply remediation or re-raise
                if not self._apply_remediation(context):
                    raise
            
            return result
        
        return wrapper
```

### 1.4 Integration Points

| Integration Point | Layer | Purpose | File |
|---------------------|-------|---------|------|
| **Template Guard** | L0 | Version & signature verification | `validation_engine/preflight/template.py` |
| **Input Handler** | L1 | File/column validation | `initiation_engine/file_handler.py` |
| **Mapper Engine** | L1 | Header validation | `mapper_engine/core/mapper.py` |
| **Schema Engine** | L2 | Schema conformance | `schema_engine/validator.py` |
| **Historical Lookup** | L2.5 | Cross-session ID duplicates | `validation_engine/validations/history.py` |
| **Field Validator** | L2/L3 | Field-level validation | `processor_engine/validations/field_validator.py` |
| **Null Handling** | L3 | Null fill error detection | `processor_engine/calculations/null_handling.py` |
| **Calculations** | L3 | Calculation error detection | `processor_engine/calculations/*.py` |
| **Engine Core** | L3 | Phased processing errors | `processor_engine/core/engine.py` |
| **Global Handler** | All | Exception catching | `error_handling/exceptions/handler.py` |
| **Logger** | All | Structured logging | `error_handling/core/logger.py` |
| **Interceptor** | L3 | AOP-style decoration | `error_handling/core/interceptor.py` |
| **Resolution** | L3 | Categorize, dispatch, archive | `error_handling/resolution/*.py` |
| **Approval Hook** | L4 | Manual overrule/suppression | `error_handling/resolution/approval.py` |
| **Status Manager** | All | Error status lifecycle | `error_handling/resolution/status_manager.py` |
| **Suppressor** | L3 | Suppression rule application | `error_handling/resolution/suppressor.py` |
| **Remediator** | L3 | Auto-remediation strategies | `error_handling/resolution/remediator.py` |
| **Metric Aggregator** | L5 | % Clean Run & Health Scores | `reporting_engine/analytics/health.py` |

### 1.5 Error Flow with Fail Fast

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT (Layer 1)                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ File Check  │───▶│  Critical?  │───▶│   STOP      │         │
│  └─────────────┘    └─────────────┘    │  (Fail Fast)│         │
│                                        └─────────────┘         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Col Check   │───▶│  Critical?  │───▶│  Continue   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SCHEMA (Layer 2)                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Field Val   │───▶│  Per Row    │───▶│  Collect    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Type Check  │───▶│  Per Row    │───▶│  Collect    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC (Layer 3)                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  P1 Phase   │───▶│  Check P1   │───▶│  Log & Track│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  P2 Phase   │───▶│  Check P2   │───▶│  Log & Track│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ P2.5 Phase  │───▶│ Check P2.5  │───▶│  Log & Track│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  P3 Phase   │───▶│  Check P3   │───▶│  Log & Track│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGGREGATION & OUTPUT                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Collect All │───▶│  Aggregate  │───▶│ Validation_ │         │
│  │   Errors    │    │  Per Row    │    │   Errors    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Implementation Phases (Updated)

### Phase 1: Foundation & Core Infrastructure (Week 1)
**Goal:** Create JSON-based registry, taxonomy, anatomy, and core infrastructure

#### Tasks:
1. [ ] **Create `error_handling/` module directory structure (Pure JSON)**
   ```
   error_handling/
   ├── __init__.py
   ├── config/                    # ALL JSON CONFIGURATION
   │   ├── __init__.py
   │   ├── error_codes.json       # Error definitions
   │   ├── taxonomy.json          # E-M-F-U taxonomy
   │   ├── status_lifecycle.json  # Status states
   │   ├── anatomy_schema.json    # E-M-F-U schema
   │   ├── remediation_types.json # Remediation strategies
   │   ├── suppression_rules.json # Suppression rules
   │   └── messages/
   │       ├── en.json
   │       └── zh.json
   ├── core/                      # JSON LOADERS
   │   ├── __init__.py
   │   ├── registry.py            # Load error_codes.json
   │   ├── taxonomy_loader.py     # Load taxonomy.json
   │   ├── status_loader.py       # Load status_lifecycle.json
   │   ├── anatomy_loader.py      # Load & validate anatomy_schema.json
   │   ├── remediation_loader.py  # Load remediation_types.json
   │   ├── validator.py           # JSON Schema validation
   │   └── logger.py
   ├── exceptions/
   ├── detectors/
   ├── resolution/
   ├── decorators/
   ├── aggregator.py
   ├── formatter.py
   ├── localizer.py
   └── tracker.py
   ```
   - Estimated: 2 hours
   - Output: Complete directory structure

2. [ ] **Create `config/error_codes.json`** (JSON-based registry)
   - Migrate from Python constants to JSON objects
   - Include full error metadata: code, layer, severity, taxonomy
   - Include message keys for localization
   - Include actionable guidance
   - Estimated: 6 hours
   - Output: `config/error_codes.json`
   - **Structure:**
   ```json
   {
     "errors": {
       "P-C-P-0101": {
         "legacy_code": "P101",
         "layer": "L3",
         "severity": "CRITICAL",
         "taxonomy": {
           "engine": "Processor",
           "module": "Core",
           "function": "Process",
           "family": "Anchor"
         },
         "message_key": "error.anchor.null_project_code",
         "description": "Priority 1 column is null and cannot be forward-filled",
         "action": "Provide required value in Excel source",
         "fail_fast": true,
         "log_level": "ERROR"
       }
     }
   }
   ```

3. [ ] **Create `config/anatomy_schema.json`** (Error code anatomy schema) ← CHANGED
   - Define E-M-F-U format schema with regex patterns
   - Create JSON Schema for validation
   - Include engine, module, function, unique_id constraints
   - Estimated: 3 hours
   - Output: `config/anatomy_schema.json`
   - **Structure:**
   ```json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "title": "Error Code Anatomy Schema",
     "description": "E-M-F-XXXX format validation",
     "type": "object",
     "properties": {
       "format": {
         "type": "string",
         "pattern": "^[A-Z]-[A-Z]-[A-Z]-\\d{4}$",
         "description": "E-M-F-XXXX format"
       },
       "components": {
         "engine": {"enum": ["P", "M", "I", "S", "R"], "description": "Processing engine"},
         "module": {"enum": ["C", "V", "A", "D", "F", "S", "L"], "description": "Module within engine"},
         "function": {"enum": ["P", "V", "C", "F"], "description": "Function type"},
         "unique_id": {"type": "integer", "minimum": 1, "maximum": 9999}
       }
     }
   }
   ```

3b. [ ] **Implement `core/anatomy_loader.py`** (Load & validate anatomy) ← NEW
   - Load `config/anatomy_schema.json`
   - Validate error codes against schema
   - Implement `ErrorCode` dataclass from JSON
   - Estimated: 3 hours
   - Output: `anatomy_loader.py`

4. [ ] **Create `config/taxonomy.json`** (Structured taxonomy definitions) ← CHANGED
   - Define error families and hierarchies in pure JSON
   - Include engines, modules, functions, families with descriptions
   - Make it editable without code changes
   - Estimated: 4 hours
   - Output: `config/taxonomy.json`
   - **Structure:**
   ```json
   {
     "version": "1.0",
     "engines": {
       "P": {"name": "Processor", "description": "Main processing engine", "modules": ["C", "V", "A", "D"]},
       "M": {"name": "Mapper", "description": "Column mapping engine", "modules": ["C", "F"]},
       "I": {"name": "Initiation", "description": "Initiation engine", "modules": ["S", "F"]},
       "S": {"name": "Schema", "description": "Schema engine", "modules": ["V", "L"]},
       "R": {"name": "Reporting", "description": "Reporting engine", "modules": ["G", "E"]}
     },
     "modules": {
       "C": {"name": "Core", "description": "Core processing"},
       "V": {"name": "Validation", "description": "Validation logic"},
       "A": {"name": "Aggregate", "description": "Aggregation logic"},
       "D": {"name": "Date", "description": "Date processing"}
     },
     "functions": {
       "P": {"name": "Process", "description": "Processing function"},
       "V": {"name": "Validate", "description": "Validation function"},
       "C": {"name": "Calculate", "description": "Calculation function"},
       "F": {"name": "Fill", "description": "Null handling function"}
     },
     "families": {
       "1": {"name": "Anchor", "layer": "L3", "description": "Priority column errors"},
       "2": {"name": "Identity", "layer": "L3", "description": "Document identity errors"},
       "3": {"name": "Logic", "layer": "L3", "description": "Business logic errors"},
       "4": {"name": "Fill", "layer": "L3", "description": "Null handling warnings"},
       "5": {"name": "Validation", "layer": "L2", "description": "Schema validation errors"},
       "6": {"name": "Calculation", "layer": "L3", "description": "Calculation errors"}
     }
   }
   ```

4b. [ ] **Implement `core/taxonomy_loader.py`** (Load taxonomy from JSON) ← NEW
   - Load `config/taxonomy.json` at runtime
   - Provide lookup methods for engine/module/function/family
   - Cache loaded definitions
   - Estimated: 3 hours
   - Output: `taxonomy_loader.py`

5. [ ] **Create `config/status_lifecycle.json`** (Error status states) ← CHANGED
   - Define all status states: OPEN, SUPPRESSED, RESOLVED, ARCHIVED, ESCALATED, PENDING, REOPEN
   - Define allowed transitions between states
   - Make status workflow configurable
   - Estimated: 2 hours
   - Output: `config/status_lifecycle.json`
   - **Structure:**
   ```json
   {
     "version": "1.0",
     "states": ["OPEN", "SUPPRESSED", "RESOLVED", "ARCHIVED", "ESCALATED", "PENDING", "REOPEN"],
     "transitions": {
       "OPEN": ["SUPPRESSED", "RESOLVED", "ESCALATED"],
       "SUPPRESSED": ["RESOLVED", "REOPEN"],
       "RESOLVED": ["ARCHIVED", "REOPEN"],
       "ESCALATED": ["RESOLVED"],
       "PENDING": ["RESOLVED", "REOPEN"],
       "REOPEN": ["SUPPRESSED", "RESOLVED", "ESCALATED"],
       "ARCHIVED": ["REOPEN"]
     },
     "initial_state": "OPEN",
     "terminal_states": ["ARCHIVED"],
     "descriptions": {
       "OPEN": "Newly detected error, unreviewed",
       "SUPPRESSED": "Error acknowledged as 'wrong but acceptable'",
       "RESOLVED": "Error fixed or remediated",
       "ARCHIVED": "Closed error kept for audit trail",
       "ESCALATED": "Critical error requiring manual intervention",
       "PENDING": "Waiting for external action",
       "REOPEN": "Previously resolved/suppressed error reoccurred"
     }
   }
   ```

5b. [ ] **Implement `core/status_loader.py`** (Load status lifecycle) ← NEW
   - Load `config/status_lifecycle.json`
   - Implement state machine with transition validation
   - Provide status management methods
   - Estimated: 3 hours
   - Output: `status_loader.py`

6. [ ] **Create `config/remediation_types.json`** (Remediation strategies) ← CHANGED
   - Define all 8 remediation types in JSON
   - Include descriptions, auto_eligible flags, conditions
   - Make remediation rules configurable
   - Estimated: 3 hours
   - Output: `config/remediation_types.json`
   - **Structure:**
   ```json
   {
     "version": "1.0",
     "types": {
       "AUTO_FIX": {
         "code": "R001",
         "description": "Automatically correct the error",
         "auto_eligible": true,
         "requires_approval": false,
         "examples": ["zero_pad_sequence_numbers", "trim_whitespace"]
       },
       "MANUAL_FIX": {
         "code": "R002",
         "description": "User must correct in source",
         "auto_eligible": false,
         "requires_approval": false
       },
       "SUPPRESS": {
         "code": "R003",
         "description": "Accept as-is with justification",
         "auto_eligible": true,
         "requires_approval": true
       },
       "ESCALATE": {
         "code": "R004",
         "description": "Route to expert/team",
         "auto_eligible": false,
         "requires_approval": true
       },
       "DERIVE": {
         "code": "R005",
         "description": "Calculate correct value",
         "auto_eligible": true,
         "requires_approval": false
       },
       "DEFAULT": {
         "code": "R006",
         "description": "Apply default value",
         "auto_eligible": true,
         "requires_approval": false
       },
       "FILL_DOWN": {
         "code": "R007",
         "description": "Forward fill from previous row",
         "auto_eligible": true,
         "requires_approval": false
       },
       "AGGREGATE": {
         "code": "R008",
         "description": "Calculate from related rows",
         "auto_eligible": true,
         "requires_approval": false
       }
     }
   }
   ```

6b. [ ] **Implement `core/remediation_loader.py`** (Load remediation types) ← NEW
   - Load `config/remediation_types.json`
   - Implement strategy pattern for each type
   - Provide remediation lookup and execution
   - Estimated: 3 hours
   - Output: `remediation_loader.py`

7. [ ] **Implement `core/interceptor.py`** (AOP framework)
   - Decorator base classes
   - Before/after/error hook registration
   - Context building and propagation
   - Estimated: 6 hours
   - Output: `interceptor.py`

8. [ ] **Implement `core/validator.py`** (JSON Schema validation) ← NEW
   - Validate all JSON configs against schemas
   - Load JSON Schema library
   - Provide validation errors for config issues
   - Estimated: 3 hours
   - Output: `validator.py`

9. [ ] **Create `config/suppression_rules.json`**
   - JSON configuration for suppression rules
   - Example rules for common scenarios
   - Rule validation structure
   - Estimated: 2 hours
   - Output: `config/suppression_rules.json`

10. [ ] **Create `resolution/` module structure**
    - `resolution/categorizer.py` - Auto-categorize errors using JSON taxonomy
    - `resolution/dispatcher.py` - Route errors to handlers
    - `resolution/suppressor.py` - Apply suppression rules from JSON
    - `resolution/remediator.py` - Apply remediation strategies from JSON
    - `resolution/archiver.py` - Archive resolved errors
    - `resolution/status_manager.py` - Manage status lifecycle from JSON
    - Estimated: 6 hours
    - Output: Resolution module with all components

11. [ ] **Create `config/messages/en.json`** (Localization)
    - Define all error message templates
    - Support parameterized messages
    - Include user actions
    - Estimated: 3 hours
    - Output: `config/messages/en.json`
    - **Structure:**
    ```json
    {
      "error": {
        "anchor": {
          "null_project_code": "Project Code is required and cannot be empty (Row {row})",
          "invalid_session_format": "Session ID '{value}' must be exactly 6 digits (e.g., 001234)"
        },
        "identity": {
          "id_uncertain": "Document ID could not be determined from available data"
        }
      },
      "action": {
        "fix_in_excel": "Fix this issue in the Excel source file",
        "contact_admin": "Contact system administrator for assistance"
      }
    }
    ```

12. [ ] **Implement `localizer.py`**
    - Load message files by locale
    - Parameter substitution
    - Fallback to default locale
    - Estimated: 3 hours
    - Output: `localizer.py`

13. [ ] **Create `decorators/` module**
    - `decorators/validate.py` - Input validation decorator
    - `decorators/track_errors.py` - Error tracking decorator
    - `decorators/log_execution.py` - Execution logging decorator
    - `decorators/suppressible.py` - Suppression check decorator
    - `decorators/apply_remediation.py` - Auto-remediation decorator
    - Estimated: 6 hours
    - Output: Full decorator suite

14. [ ] **Unit tests for foundation**
    - Test JSON registry loading
    - Test taxonomy JSON loading
    - Test status lifecycle JSON loading
    - Test remediation types JSON loading
    - Test anatomy schema validation
    - Test localization
    - Test structured logging
    - Estimated: 6 hours
    - Output: `tests/test_error_foundation.py`

**Phase 1 Deliverables (Pure JSON Architecture):**
- ✅ JSON-based error registry (`config/error_codes.json`)
- ✅ Anatomy schema (`config/anatomy_schema.json`) + loader (`core/anatomy_loader.py`)
- ✅ Taxonomy definitions (`config/taxonomy.json`) + loader (`core/taxonomy_loader.py`)
- ✅ Status lifecycle (`config/status_lifecycle.json`) + loader (`core/status_loader.py`)
- ✅ Remediation types (`config/remediation_types.json`) + loader (`core/remediation_loader.py`)
- ✅ Suppression rules (`config/suppression_rules.json`)
- ✅ Localization messages (`config/messages/en.json`)
- ✅ Structured logging (`core/logger.py`)
- ✅ JSON Schema validation (`core/validator.py`)
- ✅ Interceptor framework (`core/interceptor.py`)
- ✅ Resolution module (`resolution/*.py`)
- ✅ Decorator suite (`decorators/*.py`)
- ✅ Unit tests passing

---

### Phase 2: Global Exception Handling & Multi-Layer Detectors (Week 2)
**Goal:** Implement global exception handling and Layer 0-2 detectors with fail-fast

#### Tasks:

1. [x] **Implement Template Guard (`validation_engine/preflight/template.py`)** ← NEW (L0) ✅ COMPLETED
   - Schema version verification
   - Template signature validation (checksum/hash)
   - Configuration compatibility check
   - Pre-flight validation before data load
   - **Fail Fast:** Stop if template version mismatch
   - Estimated: 4 hours
   - Output: `template.py`
   - **API:**
   ```python
   class TemplateGuard:
       def verify_schema_version(self, expected: str, actual: str) -> bool
       def validate_signature(self, template_path: str) -> bool
       def check_compatibility(self, config: dict) -> List[Error]
   ```

2. [x] **Implement `exceptions/base.py`** (Global exception handling) ✅ COMPLETED
   - Create `DCCError` base exception class
   - Add error code integration
   - Add context preservation
   - Estimated: 4 hours
   - Output: `base.py`
   - **API:**
   ```python
   class DCCError(Exception):
       def __init__(self, error_code: str, context: dict = None, ...)
       def to_dict(self) -> dict
       def to_json(self) -> str
       def get_user_message(self, locale: str = "en") -> str
   ```

3. [x] **Implement `exceptions/handler.py`** (Global exception handler) ✅ COMPLETED
   - Catch unhandled exceptions at top level
   - Map exceptions to error codes
   - Log and re-raise with context
   - Estimated: 4 hours
   - Output: `handler.py`

4. [x] **Implement `detectors/base.py`** (Base detector with logging) ✅ COMPLETED
   - Integrate with structured logger
   - Add fail-fast capability
   - Add context collection
   - Estimated: 3 hours
   - Output: `detectors/base.py`

5. [x] **Implement `detectors/input.py`** (Layer 1: Input validation) ✅ COMPLETED
   - File existence/format validation
   - Column presence detection
   - Encoding detection
   - **Fail Fast:** Stop on critical input errors
   - Estimated: 6 hours
   - Output: `input.py`

6. [x] **Implement `detectors/schema.py`** (Layer 2: Schema validation) ✅ COMPLETED
   - Pattern mismatch detection
   - Length/enum validation
   - Type checking
   - Foreign key validation
   - Estimated: 6 hours
   - Output: `schema.py`

7. [x] **Integration tests** ✅ COMPLETED (33 tests, 100% pass)
   - Test fail-fast behavior
   - Test multi-layer detection
   - Test global exception handling
   - Estimated: 4 hours
   - Output: `tests/test_exception_handling.py`

**Phase 2 Deliverables:** ✅ ALL COMPLETED
- ✅ Global exception handling system (`exceptions/`)
- ✅ Layer 1 (Input) detectors with fail-fast (`detectors/input.py`)
- ✅ Layer 2 (Schema) detectors (`detectors/schema.py`)
- ✅ Multi-layer validation working
- ✅ Template Guard L0 (`validation_engine/preflight/`)
- ✅ Integration tests (33 tests, 100% pass)
- ✅ Test reports (`tests/PHASE1_TEST_REPORT.md`, `tests/PHASE2_TEST_REPORT.md`)

---

### Phase 3: Business Logic Detectors (Layer 3) (Week 3)
**Goal:** Implement P1-P2-P2.5-P3 phase detectors for business logic validation

#### Tasks:

1. [ ] **Implement `detectors/anchor.py` (P1xx - Layer 3)**
   - `detect_P101_null_anchor()` - Check P1 columns for nulls
   - `detect_P102_session_format()` - Validate 6-digit pattern
   - `detect_P103_date_invalid()` - Check date parsing
   - Integration with P1 phase processing
   - **Fail Fast:** Stop if critical anchor errors found
   - Estimated: 6 hours
   - Output: `detectors/anchor.py`

2. [ ] **Implement `detectors/identity.py` (P2xx - Layer 3)**
   - `detect_P201_id_uncertain()` - Check Document_ID calculation
   - `detect_P202_rev_missing()` - Check Document_Revision
   - `detect_P203_duplicate_trans()` - Check for duplicates
   - Integration with P2 phase processing
   - Estimated: 6 hours
   - Output: `detectors/identity.py`

3. [ ] **Implement `detectors/business.py` (Layer 3 orchestrator)**
   - Coordinate all business logic detectors
   - Manage phase transitions
   - Collect and route errors
   - Estimated: 4 hours
   - Output: `detectors/business.py`

4. [ ] **Document Null Handling Error Detection** ← NEW
   - **Analysis:** How null_handling data errors are detected and handled
   - **Integration Points:**
     - `null_handling.py` errors captured via decorator @track_errors
     - Forward fill failures → F4-C-F-0401 (Fill Limit Exceeded)
     - Multi-level fill failures → F4-C-F-0402 (Multi-level Fail)
     - Default value application → F4-C-F-0403 (Default Applied)
   - **Error Flow:**
     ```
     null_handling.apply_forward_fill()
       └─ @track_errors(error_family="Fill", layer="L3")
          └─ If fill fails → Create F4xx error
             └─ @apply_remediation(strategy="FILL_DOWN")
                └─ Try forward fill → Success/Failure
                   └─ Update Error_Status column
     ```
   - **Remediation:**
     - AUTO_FIX: Try alternative fill strategy
     - MANUAL_FIX: Flag for user to provide data
     - DEFAULT: Apply schema-defined default value
   - **Storage:** Null handling errors logged with context:
     ```json
     {
       "error_code": "F4-C-F-0401",
       "null_handling_strategy": "forward_fill",
       "column": "Reviewer",
       "group_by": ["Project_Code", "Document_ID"],
       "rows_affected": 5,
       "filled_values": 3,
       "remaining_nulls": 2
     }
     ```
   - Estimated: 4 hours
   - Output: `docs/null_handling_error_handling.md`

5. [ ] **Implement Historical Lookup (`validation_engine/validations/history.py`)** ← NEW (L2.5)
   - Cross-session duplicate Document_ID detection
   - Historical revision comparison
   - Temporal consistency validation
   - Previous submission reference validation
   - **API:**
   ```python
   class HistoricalLookup:
       def check_cross_session_duplicates(
           self, 
           current_df: pd.DataFrame, 
           historical_data: pd.DataFrame
       ) -> List[Tuple[int, str, str]]  # (row_index, doc_id, error_code)
       
       def validate_revision_consistency(
           self,
           document_id: str,
           current_revision: str,
           history: List[dict]
       ) -> bool
       
       def check_temporal_integrity(
           self,
           submission_dates: pd.Series,
           session_ids: pd.Series
       ) -> List[Error]
   ```
   - **Error Codes:**
     - `H2-V-H-0201` - Cross-session duplicate Document_ID
     - `H2-V-H-0202` - Revision regression vs. history
     - `H2-V-H-0203` - Temporal inconsistency across sessions
   - Estimated: 6 hours
   - Output: `history.py`

6. [ ] **Implement `detectors/logic.py` (L3xx - Layer 3)**
   - `detect_L301_date_inversion()` - Return before submission
   - `detect_L302_rev_regression()` - Revision regression
   - `detect_L303_status_conflict()` - Closure status conflict
   - `detect_L304_overdue_pending()` - Overdue detection
   - Integration with P3 phase processing
   - Estimated: 6 hours
   - Output: `detectors/logic.py`

7. [ ] **Implement `detectors/fill.py` (F4xx warnings - Layer 3)**
   - `detect_F401_jump_limit()` - Row jump > 20
   - `detect_F402_boundary_cross()` - Session boundary breach
   - `detect_F403_fill_inferred()` - Calculation-based fill
   - Integration with null_handling.py
   - Estimated: 4 hours
   - Output: `detectors/fill.py`

8. [ ] **Implement `detectors/validation.py` (V5xx - Layer 2/3)**
   - `detect_V501_pattern_mismatch()` - Regex validation
   - `detect_V502_length_exceeded()` - Max length check
   - `detect_V503_invalid_enum()` - Allowed values check
   - `detect_V504_type_mismatch()` - Data type validation
   - `detect_V505_required_missing()` - Required field check
   - `detect_V506_foreign_key_fail()` - Reference validation
   - Integration with field_validator.py
   - Estimated: 6 hours
   - Output: `detectors/validation.py`

9. [ ] **Implement `detectors/calculation.py` (C6xx - Layer 3)**
   - `detect_C601_dependency_fail()` - Missing input columns
   - `detect_C602_circular_dependency()` - Dependency graph check
   - `detect_C603_division_by_zero()` - Math error detection
   - `detect_C604_aggregate_empty()` - Aggregation validation
   - `detect_C605_date_arithmetic_fail()` - Date calc errors
   - `detect_C606_mapping_no_match()` - Mapping validation
   - Integration with calculation handlers
   - Estimated: 6 hours
   - Output: `detectors/calculation.py`

10. [ ] **Unit tests for all detectors**
    - Test each detector with valid/invalid data
    - Test edge cases
    - Test error code assignment
    - Test historical lookup functionality
    - Estimated: 6 hours
    - Output: `tests/test_all_detectors.py`

**Phase 3 Deliverables:**
- All 24 error detectors implemented
- Layer 2.5 (Historical Lookup) validation complete ← NEW
- Layer 3 (Business Logic) validation complete
- Phase integration (P1, P2, P2.5, P3) working
- Full detector test coverage

---

### Phase 4: Aggregation, Integration & Localization (Week 4)
**Goal:** Implement error aggregation, engine integration, and localization

#### Tasks:

1. [ ] **Implement `aggregator.py`**
   - `aggregate_row_errors()` - Collect all errors per row
   - `aggregate_phase_errors()` - Summary per phase
   - Error deduplication logic
   - CSV string formatting for `Validation_Errors` column
   - JSON output for structured logging
   - Estimated: 6 hours
   - Output: `aggregator.py`

2. [ ] **Implement `formatter.py`** with localization support
   - `format_for_ui()` - JSON error format with localized messages
   - `format_for_log()` - Structured text format
   - `get_error_tooltip()` - Localized tooltip message
   - `format_by_locale()` - Multi-language support
   - Severity-based formatting
   - Estimated: 6 hours
   - Output: `formatter.py`

3. [ ] **Integrate with `engine.py`** with logging
   - Modify `apply_phased_processing()` to track errors
   - Add structured logging at each phase
   - Log all errors with context (row, column, phase, layer)
   - Call aggregators at end of processing
   - Estimated: 6 hours
   - Output: Updated `engine.py`

4. [ ] **Integrate with `Validation_Errors` column (Step 46)**
   - Create calculation handler for error aggregation
   - Ensure it runs after all other P3 columns
   - Include localized error summaries
   - Test with full pipeline
   - Estimated: 4 hours
   - Output: Error aggregation in pipeline

5. [ ] **Create `config/messages/zh.json`** (Chinese localization)
   - Translate all error messages
   - Translate user actions
   - Test with Chinese locale
   - Estimated: 4 hours
   - Output: `messages/zh.json`

6. [ ] **Implement Approval Hook (`error_handling/resolution/approval.py`)** ← NEW (L4)
   - Manual overrule interface for human decisions
   - User-initiated suppression workflow
   - Approval audit trail with timestamp & approver
   - UI integration for error review and approval
   - **API:**
   ```python
   class ApprovalHook:
       def request_approval(
           self,
           error_id: str,
           justification: str,
           requested_by: str
       ) -> ApprovalRequest
       
       def approve_error(
           self,
           error_id: str,
           approver: str,
           reason: str
       ) -> ErrorStatus
       
       def get_pending_approvals(
           self,
           project_code: str = None
       ) -> List[ApprovalRequest]
       
       def get_approval_history(
           self,
           error_id: str
       ) -> List[ApprovalEvent]
   ```
   - **JSON Config:** `config/approval_workflow.json`
   - **Features:**
     - Email notifications for pending approvals
     - Escalation after timeout (24h)
     - Bulk approval for similar errors
     - Required approvers by error severity
   - Estimated: 6 hours
   - Output: `approval.py`, `config/approval_workflow.json`

7. [ ] **Integration tests with logging verification**
   - Full pipeline test with error injection
   - Verify all error types are captured
   - Verify structured logs are generated
   - Verify localization works
   - Test approval workflow end-to-end
   - Estimated: 6 hours
   - Output: `tests/test_full_integration.py`

**Phase 4 Deliverables:**
- Error aggregation working
- Validation_Errors column populated
- Full integration with pipeline
- Layer 4 (Approval Hook) workflow complete ← NEW

---

### Phase 5: Logging, Reporting & UI Support (Week 5)
**Goal:** Implement comprehensive logging, monitoring, reporting, and UI integration

#### Tasks:

1. [ ] **Implement comprehensive logging throughout pipeline**
   - Add structured logging to all engine entry points
   - Log every error detection with full context
   - Log every phase transition
   - Log performance metrics
   - Create log rotation and archiving
   - Estimated: 6 hours
   - Output: Complete logging integration

2. [ ] **Implement `reporting_engine/error_reporter.py`**
   - `generate_error_summary()` - Overall stats with trends
   - `generate_error_by_phase()` - Phase breakdown
   - `generate_error_by_column()` - Column analysis
   - `generate_error_by_taxonomy()` - Taxonomy-based reports
   - Export to Excel/CSV with localized headers
   - Estimated: 6 hours
   - Output: `error_reporter.py`

3. [ ] **Add error summary to pipeline output**
   - Update `processing_summary.txt` with error stats
   - Add error count to console output
   - Add severity breakdown
   - Add "fail fast" stopped status
   - Estimated: 3 hours
   - Output: Enhanced summary

4. [ ] **Create error dashboard data export**
   - JSON export for UI dashboard
   - Error trend data with time series
   - Taxonomy-based drill-down
   - Severity heat maps
   - Estimated: 4 hours
   - Output: Dashboard endpoint

5. [ ] **Create log viewer and analysis tools**
   - `tools/error_log_viewer.py` - Parse and display structured logs
   - `tools/error_analyzer.py` - Trend analysis and reporting
   - `tools/error_export.py` - Export logs to various formats
   - Estimated: 4 hours
   - Output: Log analysis tools

6. [ ] **Implement Metric Aggregator (`reporting_engine/analytics/health.py`)** ← NEW (L5)
   - Calculate % Clean Run (rows with zero critical/high errors)
   - Data Health Score with grade distribution
   - Error trend analysis over time
   - Project-level quality metrics aggregation
   - **API:**
   ```python
   class MetricAggregator:
       def calculate_clean_run_percentage(
           self,
           total_rows: int,
           rows_with_errors: int
       ) -> float
       
       def aggregate_health_scores(
           self,
           project_runs: List[RunResult]
       ) -> ProjectHealthReport
       
       def calculate_error_trends(
           self,
           historical_data: List[ErrorSummary],
           window_days: int = 30
       ) -> TrendReport
       
       def generate_quality_dashboard(
           self,
           filters: dict
       ) -> DashboardData
   ```
   - **Metrics Calculated:**
     - % Clean Run = (Clean Rows / Total Rows) × 100
     - Health Score = (Total - Critical - High) / Total × 100
     - Error Density = Errors per 1000 rows
     - Mean Time To Resolution (MTTR)
   - **Output Files:**
     - CSV exports for management reports
     - JSON for dashboard API
     - Excel for detailed analysis
   - Estimated: 6 hours
   - Output: `health.py`, quality metrics export

7. [ ] **Implement Data Health KPI (`reporting_engine/data_health.py`)** ← NEW
   - `calculate_health_score()` - (Total - Critical - High) / Total × 100
   - `get_grade()` - Convert score to letter grade (A+/A/B/C/D/F)
   - `get_trend()` - Compare with previous runs
   - `export_health_report()` - Generate health report with recommendations
   - Add `Data_Health_Score` column to output (Step 48)
   - Integration with dashboard for real-time display
   - Estimated: 6 hours
   - Output: `data_health.py`, health score column
   - **API:**
   ```python
   @dataclass
   class DataHealthKPI:
       total_rows: int
       critical_errors: int
       high_errors: int
       health_score: float  # 0-100%
       grade: str           # A+/A/B/C/D/F
       trend: str          # ↑ → ↓
       
       def to_dict(self) -> dict:
           return {
               "score": self.health_score,
               "grade": self.grade,
               "summary": f"{self.health_score:.1f}% ({self.grade}) - "
                          f"{self.critical_errors} critical, "
                          f"{self.high_errors} high errors"
           }
   ```

8. [ ] **Documentation**
   - Update `processor_engine/readme.md` with new architecture
   - Document all 6 layers (L0-L5) of validation
   - Document JSON error registry format
   - Document JSON taxonomy schema
   - Document localization approach
   - Document logging structure
   - Document approval workflow (L4)
   - Document data health KPI calculation (L5)
   - Document historical lookup integration (L2.5)
   - Create troubleshooting guide
   - Estimated: 6 hours
   - Output: Complete documentation

**Phase 5 Deliverables:**
- Comprehensive logging throughout pipeline
- Error reporting module with taxonomy support
- Layer 5 (Metric Aggregator) complete ← NEW
- Pipeline summary updates
- Dashboard support with trend analysis
- Data Health KPI calculation and reporting
- % Clean Run metrics ← NEW
- Log analysis tools
- Complete documentation

---

## 3. Detailed Task Specifications (Updated)

### 3.1 JSON Error Registry (`config/error_codes.json`)

**Structure:**
```json
{
  "version": "2.0",
  "last_updated": "2026-04-10",
  "errors": {
    "P-C-P-0101": {
      "legacy_code": "P101",
      "layer": "L3",
      "severity": "CRITICAL",
      "taxonomy": {
        "engine": "Processor",
        "engine_code": "P",
        "module": "Core",
        "module_code": "C",
        "function": "Process",
        "function_code": "P",
        "family": "Anchor"
      },
      "message_key": "error.anchor.null_project_code",
      "description": "Priority 1 column is null and cannot be forward-filled",
      "action_key": "action.fix_in_excel",
      "fail_fast": true,
      "log_level": "ERROR",
      "ui_severity": "critical",
      "example": "Project_Code is empty"
    },
    "P-C-P-0102": {
      "legacy_code": "P102",
      "layer": "L3",
      "severity": "CRITICAL",
      "taxonomy": {
        "engine": "Processor",
        "module": "Core",
        "function": "Process",
        "family": "Anchor"
      },
      "message_key": "error.anchor.invalid_session_format",
      "action_key": "action.fix_in_excel",
      "fail_fast": true,
      "log_level": "ERROR",
      "ui_severity": "critical"
    }
  },
  "metadata": {
    "total_errors": 24,
    "categories": ["P1xx", "P2xx", "L3xx", "F4xx", "V5xx", "C6xx"],
    "engines": ["P", "M", "I", "S", "R"],
    "modules": ["C", "V", "A", "D", "F", "M", "I", "L"],
    "functions": ["P", "V", "C", "F", "M", "A", "L", "T"]
  }
}
```

**Benefits:**
- No code changes needed to add/modify error codes
- Version controlled alongside application code
- Easy to validate and lint
- Supports localization keys
- Machine-readable for external tools

---

### 3.2 Error Code Anatomy (`core/anatomy.py`)

**Specification:**
```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class ErrorCode:
    """
    Structured error code with E-M-F-U anatomy.
    Format: P-C-P-0101 (Engine-Module-Function-UniqueID)
    """
    engine: str      # P=Processor, M=Mapper, I=Initiation, S=Schema, R=Reporting
    module: str      # C=Core, V=Validation, A=Aggregate, D=Date, F=Fill, M=Mapping, I=Input, L=Logic
    function: str    # P=Process, V=Validate, C=Calculate, F=Fill, M=Map, A=Analyze, L=Log, T=Transform
    unique_id: int   # 0001-9999
    
    def __post_init__(self):
        # Validation
        assert len(self.engine) == 1 and self.engine.isalpha()
        assert len(self.module) == 1 and self.module.isalpha()
        assert len(self.function) == 1 and self.function.isalpha()
        assert 1 <= self.unique_id <= 9999
    
    def to_string(self) -> str:
        """Convert to E-M-F-XXXX format."""
        return f"{self.engine}-{self.module}-{self.function}-{self.unique_id:04d}"
    
    @classmethod
    def from_string(cls, code: str) -> "ErrorCode":
        """Parse from E-M-F-XXXX format."""
        parts = code.split('-')
        return cls(
            engine=parts[0],
            module=parts[1],
            function=parts[2],
            unique_id=int(parts[3])
        )
    
    @classmethod
    def from_legacy(cls, legacy_code: str) -> Optional["ErrorCode"]:
        """Convert from legacy format (e.g., P101)."""
        # Lookup in registry mapping
        pass
    
    def get_taxonomy(self) -> Dict:
        """Get human-readable taxonomy."""
        return {
            "engine": ENGINE_NAMES[self.engine],
            "module": MODULE_NAMES[self.module],
            "function": FUNCTION_NAMES[self.function],
            "family": self._get_family()
        }
    
    def get_legacy_code(self) -> str:
        """Get legacy code for backward compatibility."""
        pass
```

**Acceptance Criteria:**
- Can parse and generate E-M-F-U format
- Validates all components
- Supports legacy code conversion
- Immutable (frozen dataclass)

---

### 3.3 Error Taxonomy (`core/taxonomy.py`)

**Specification:**
```python
class ErrorTaxonomy:
    """
    Provides hierarchical classification of errors.
    """
    
    ENGINE_NAMES = {
        "P": "Processor",
        "M": "Mapper", 
        "I": "Initiation",
        "S": "Schema",
        "R": "Reporting"
    }
    
    MODULE_NAMES = {
        "C": "Core",
        "V": "Validation",
        "A": "Aggregate",
        "D": "Date",
        "F": "Fill",
        "M": "Mapping",
        "I": "Input",
        "L": "Logic"
    }
    
    FUNCTION_NAMES = {
        "P": "Process",
        "V": "Validate",
        "C": "Calculate",
        "F": "Fill",
        "M": "Map",
        "A": "Analyze",
        "L": "Log",
        "T": "Transform"
    }
    
    ERROR_FAMILIES = {
        "Anchor": {"prefix": "P1", "layer": "L3", "severity": "CRITICAL"},
        "Identity": {"prefix": "P2", "layer": "L3", "severity": "CRITICAL"},
        "Logic": {"prefix": "L3", "layer": "L3", "severity": "HIGH"},
        "Fill": {"prefix": "F4", "layer": "L3", "severity": "LOW"},
        "Validation": {"prefix": "V5", "layer": "L2", "severity": "MEDIUM"},
        "Calculation": {"prefix": "C6", "layer": "L3", "severity": "HIGH"}
    }
    
    @classmethod
    def get_by_family(cls, family: str) -> List[str]:
        """Get all error codes in a family."""
        pass
    
    @classmethod
    def get_by_layer(cls, layer: str) -> List[str]:
        """Get all error codes for a validation layer."""
        pass
    
    @classmethod
    def get_by_engine(cls, engine: str) -> List[str]:
        """Get all error codes from an engine."""
        pass
```

---

### 3.4 Structured Logger (`core/logger.py`)

**Specification:**
```python
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredErrorLogger:
    """
    Logs errors in structured JSON format for analysis and monitoring.
    """
    
    def __init__(self, name: str, log_file: str = "errors.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # JSON formatter
        formatter = logging.Formatter(
            '%(message)s'  # We'll format the entire JSON ourselves
        )
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_error(
        self,
        error_code: str,
        message: str,
        layer: str,
        phase: Optional[str] = None,
        row_index: Optional[int] = None,
        column: Optional[str] = None,
        context: Optional[Dict] = None,
        stack_trace: Optional[str] = None
    ):
        """
        Log an error with full context.
        
        Output format:
        {
          "timestamp": "2026-04-10T20:45:00.123456Z",
          "level": "ERROR",
          "error_code": "P-C-P-0101",
          "layer": "L3",
          "phase": "P1",
          "row_index": 42,
          "column": "Project_Code",
          "message": "Null value in anchor column",
          "context": {
            "facility_code": "FC01",
            "submission_session": "001234"
          },
          "stack_trace": null
        }
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "error_code": error_code,
            "layer": layer,
            "phase": phase,
            "row_index": row_index,
            "column": column,
            "message": message,
            "context": context or {},
            "stack_trace": stack_trace
        }
        
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))
    
    def log_phase_transition(self, from_phase: str, to_phase: str, row_count: int):
        """Log phase transitions for debugging."""
        pass
    
    def log_detection(self, detector: str, errors_found: int, duration_ms: float):
        """Log detector performance metrics."""
        pass
```

---

### 3.5 JSON Registry Loader (`registry.py`)

**Specification:**
```python
import json
from typing import Dict, List, Optional
from pathlib import Path

class ErrorRegistry:
    """
    Loads and provides access to error definitions from JSON.
    """
    
    _instance = None
    _cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """Load error definitions from JSON file."""
        config_path = Path(__file__).parent / "config" / "error_codes.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._errors = data.get("errors", {})
        self._metadata = data.get("metadata", {})
    
    def get_error(self, code: str) -> Optional[Dict]:
        """Get error definition by code (E-M-F-U format)."""
        return self._errors.get(code)
    
    def get_by_legacy(self, legacy_code: str) -> Optional[Dict]:
        """Get error definition by legacy code (e.g., P101)."""
        for code, definition in self._errors.items():
            if definition.get("legacy_code") == legacy_code:
                return definition
        return None
    
    def get_by_taxonomy(self, engine: str = None, module: str = None, 
                       function: str = None, family: str = None) -> List[Dict]:
        """Get errors matching taxonomy criteria."""
        results = []
        for code, definition in self._errors.items():
            tax = definition.get("taxonomy", {})
            if engine and tax.get("engine_code") != engine:
                continue
            if module and tax.get("module_code") != module:
                continue
            if function and tax.get("function_code") != function:
                continue
            if family and tax.get("family") != family:
                continue
            results.append(definition)
        return results
    
    def get_by_layer(self, layer: str) -> List[Dict]:
        """Get all errors for a validation layer."""
        return [d for d in self._errors.values() if d.get("layer") == layer]
    
    def get_by_severity(self, severity: str) -> List[Dict]:
        """Get all errors by severity level."""
        return [d for d in self._errors.values() if d.get("severity") == severity]
    
    def get_all_codes(self) -> List[str]:
        """Get all error codes."""
        return list(self._errors.keys())
    
    def reload(self):
        """Reload registry from JSON (useful for hot updates)."""
        self._load()
```

**Acceptance Criteria:**
- Loads from JSON file correctly
- Provides multiple lookup methods
- Singleton pattern for performance
- Supports hot reload

---

### 3.2 Anchor Detector (`detectors/anchor.py`)

**Specification:**
```python
def detect_P101_null_anchor(
    df: pd.DataFrame,
    p1_columns: List[str] = None
) -> List[Tuple[int, str, str]]:
    """
    Detect null values in P1 (anchor) columns.
    
    Returns:
        List of (row_index, column_name, error_code) tuples
    """
    pass

def detect_P102_session_format(
    df: pd.DataFrame,
    pattern: str = r'^[0-9]{6}$'
) -> List[Tuple[int, str, str]]:
    """
    Detect invalid Submission_Session format.
    """
    pass

def detect_P103_date_invalid(
    df: pd.DataFrame,
    date_column: str = "Submission_Date"
) -> List[Tuple[int, str, str]]:
    """
    Detect invalid or unparseable dates.
    """
    pass
```

**Acceptance Criteria:**
- Detects nulls in all P1 columns
- Validates 6-digit pattern for Submission_Session
- Validates date parseability
- Returns standardized error tuples

---

### 3.3 Identity Detector (`detectors/identity.py`)

**Specification:**
```python
def detect_P201_id_uncertain(
    df: pd.DataFrame,
    document_id_col: str = "Document_ID"
) -> List[Tuple[int, str, str]]:
    """
    Detect rows where Document_ID could not be calculated.
    """
    pass

def detect_P202_rev_missing(
    df: pd.DataFrame,
    revision_col: str = "Document_Revision"
) -> List[Tuple[int, str, str]]:
    """
    Detect rows with missing revision.
    """
    pass

def detect_P203_duplicate_trans(
    df: pd.DataFrame,
    group_cols: List[str] = ["Submission_Session", "Document_ID"]
) -> List[Tuple[int, str, str]]:
    """
    Detect duplicate Document IDs within same session.
    """
    pass
```

**Acceptance Criteria:**
- Detects null/uncertain Document_ID
- Detects missing revisions
- Finds duplicates within Submission_Session

---

### 3.4 Aggregator (`aggregator.py`)

**Specification:**
```python
def aggregate_row_errors(
    df: pd.DataFrame,
    row_index: int,
    phase_errors: Dict[str, List[Tuple[int, str, str]]]
) -> str:
    """
    Aggregate all errors for a single row into CSV string.
    
    Args:
        df: DataFrame being processed
        row_index: Index of row to check
        phase_errors: Dict of phase_name -> list of (row, col, code)
    
    Returns:
        Comma-separated error codes string (or None if no errors)
    """
    pass

def aggregate_phase_errors(
    df: pd.DataFrame,
    phase_name: str,
    error_list: List[Tuple[int, str, str]]
) -> Dict[str, any]:
    """
    Generate summary statistics for a phase's errors.
    
    Returns:
        Dict with counts by error code, columns affected, etc.
    """
    pass
```

**Acceptance Criteria:**
- Correctly aggregates all error types per row
- Returns CSV format: "P101, V501, F401"
- Handles None/empty correctly
- Phase summaries include counts and breakdowns

---

### 3.5 Engine Integration

**Modification Points in `engine.py`:**

```python
# Add to imports
from ..error_handling.tracker import ErrorTracker
from ..error_handling.aggregator import aggregate_row_errors

class CalculationEngine:
    def __init__(self, ...):
        # ... existing init ...
        self.error_tracker = ErrorTracker()
    
    def apply_phased_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process columns by phase with error tracking.
        """
        # Initialize error tracking
        self.error_tracker.clear()
        
        # Phase 1 with error tracking
        df, p1_errors = self._apply_phase_with_tracking(
            df, phase_columns['P1'], 'P1'
        )
        self.error_tracker.add_phase_errors('P1', p1_errors)
        
        # Phase 2 with error tracking
        df, p2_errors = self._apply_phase_with_tracking(
            df, phase_columns['P2'], 'P2'
        )
        self.error_tracker.add_phase_errors('P2', p2_errors)
        
        # ... etc for P2.5, P3 ...
        
        # Aggregate errors into Validation_Errors column
        df = self._populate_validation_errors(df)
        
        return df
    
    def _populate_validation_errors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Populate Validation_Errors column with aggregated errors.
        """
        all_errors = self.error_tracker.get_all_errors()
        
        def get_row_errors(idx):
            return aggregate_row_errors(df, idx, all_errors)
        
        df['Validation_Errors'] = [get_row_errors(i) for i in range(len(df))]
        return df
```

**Acceptance Criteria:**
- Error tracking integrated into each phase
- Validation_Errors column populated correctly
- No significant performance degradation

---

## 4. Testing Strategy

### 4.1 Unit Testing

**Test Coverage Requirements:**
- 100% coverage for `registry.py`
- 90%+ coverage for each detector module
- 80%+ coverage for `aggregator.py` and `formatter.py`

**Test Data:**
```python
# test_data/error_scenarios.py
ERROR_SCENARIOS = {
    'P101_null_anchor': {
        'data': {'Project_Code': None, 'Facility_Code': 'FC01'},
        'expected_errors': ['P101']
    },
    'P102_invalid_session': {
        'data': {'Submission_Session': 'ABC123'},
        'expected_errors': ['P102']
    },
    # ... etc
}
```

### 4.2 Integration Testing

**Test Scenarios:**
1. Full pipeline with no errors (clean data)
2. Full pipeline with P1 errors only
3. Full pipeline with mixed errors (P1, P2, L3, V5, C6)
4. Full pipeline with only F4 warnings
5. Performance test with 10,000+ rows

**Success Criteria:**
- All error types detected and reported
- Validation_Errors column correctly populated
- Pipeline completes without crashing
- Error counts match expected values

### 4.3 Performance Testing

**Benchmarks:**
- Error detection adds < 10% to processing time
- Memory overhead < 50MB for 10,000 rows
- Error aggregation completes in < 1 second

### 4.4 Data Health KPI Testing ← NEW

**KPI Formula:**
```
Data Health Score = (Total Rows - Critical Errors - High Errors) / Total Rows × 100
```

**Test Scenarios:**
| Scenario | Total Rows | Critical | High | Medium/Low | Expected Score |
|----------|------------|----------|------|------------|----------------|
| Perfect data | 1000 | 0 | 0 | 0 | 100% |
| Clean data | 1000 | 0 | 10 | 50 | 99% |
| Moderate issues | 1000 | 5 | 20 | 100 | 97.5% |
| Poor quality | 1000 | 50 | 100 | 200 | 85% |
| Critical failure | 1000 | 200 | 300 | 500 | 50% |

**KPI Components:**
```python
@dataclass
class DataHealthKPI:
    total_rows: int
    critical_errors: int      # CRITICAL severity
    high_errors: int          # HIGH severity
    medium_errors: int        # MEDIUM severity (not in KPI)
    low_errors: int           # LOW severity (not in KPI)
    warnings: int             # WARNING severity (not in KPI)
    
    @property
    def health_score(self) -> float:
        """Calculate health score 0-100%"""
        bad_rows = self.critical_errors + self.high_errors
        return max(0, (self.total_rows - bad_rows) / self.total_rows * 100)
    
    @property
    def grade(self) -> str:
        """Letter grade based on score"""
        if self.health_score >= 99: return "A+"
        elif self.health_score >= 95: return "A"
        elif self.health_score >= 90: return "B"
        elif self.health_score >= 80: return "C"
        elif self.health_score >= 70: return "D"
        else: return "F"
```

**KPI Reporting:**
- Real-time health score during processing
- Grade displayed in UI dashboard
- Trend tracking over time
- Export to reporting engine

---

## 5. Timeline Summary (5-Phase Structure)

| Phase | Duration | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| **Phase 1** | 1 week | Foundation | JSON registry, anatomy, taxonomy, logger, localization |
| **Phase 2** | 1 week | Exception Handling | Global exceptions, Layer 1-2 detectors, fail-fast |
| **Phase 3** | 1 week | Business Logic | Layer 3 detectors (P1-P2-P2.5-P3), all 24 error types |
| **Phase 4** | 1 week | Integration | Aggregation, engine integration, localization (en/zh) |
| **Phase 5** | 1 week | Logging, Reporting, KPI | Structured logging, reports, dashboard, data health KPI |
| **Total** | **5 weeks** | | **Complete module** |

### Resource Requirements
- **Developer:** 1 FTE for 5 weeks
- **Tester:** 0.5 FTE for weeks 3-5
- **Documentation:** 0.25 FTE for week 5

---

## 6. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **JSON registry performance** | Low | Medium | Implement caching, lazy loading |
| **Localization complexity** | Medium | Medium | Use established i18n libraries, fallback chain |
| **Structured logging overhead** | Medium | Medium | Async logging, log rotation, sampling |
| **Fail-fast disruption** | Medium | High | Gradual rollout, feature flags, clear documentation |
| **Error code migration** | Low | Medium | Maintain legacy mapping, backward compatibility |
| **Performance degradation** | Medium | High | Profile code, optimize detectors |
| **False positives** | Medium | Medium | Thorough testing, adjustable thresholds |
| **Integration complexity** | Low | High | Incremental integration, extensive testing |

---

## 7. Success Metrics

### 7.1 Technical Metrics
- [ ] **Error Detection:** All 24 error codes detectable with E-M-F-U format
- [ ] **Error Status:** Error_Status column populated with correct lifecycle states
- [ ] **Suppression:** Suppression rules applied correctly with audit trail
- [ ] **Remediation:** 8 remediation types implemented and applied automatically
- [ ] **Interceptors:** All calculation handlers use decorator pattern (no inline if/else)
- [ ] **JSON Schema:** Taxonomy validated against JSON Schema (`taxonomy_schema.json`) ← NEW
- [ ] **Null Handling Errors:** F4xx errors captured for all null handling failures ← NEW
- [ ] **Data Health KPI:** Health score calculated and Data_Health_Score column populated ← NEW
- [ ] **Test Coverage:** > 90% unit test coverage, > 80% integration coverage
- [ ] **Performance:** < 10% processing overhead, < 50MB memory overhead
- [ ] **Logging:** 100% of errors logged with structured JSON format
- [ ] **Localization:** English and Chinese message files complete
- [ ] **Fail Fast:** Critical errors (P1xx, P2xx) stop processing immediately
- [ ] **Zero critical bugs** in production

### 7.2 Architecture Metrics
- [ ] **JSON Registry:** Hot-reloadable error definitions
- [ ] **Error Anatomy:** All codes follow E-M-F-U format
- [ ] **Multi-Layer:** All 3 validation layers (L1/L2/L3) implemented
- [ ] **Global Exceptions:** All exceptions caught and mapped to error codes
- [ ] **Structured Logging:** Searchable, filterable, exportable logs
- [ ] **Status Lifecycle:** 7-state error lifecycle (Open→Suppressed→Resolved→Archived)
- [ ] **Resolution Module:** Categorize, dispatch, remediate, archive workflow complete
- [ ] **Interceptor Pattern:** AOP-style decorators replace inline error handling

### 7.3 Business Metrics
- [ ] **Data Quality:** Error detection reduces data issues by 80%
- [ ] **User Efficiency:** Users identify and fix errors in < 5 minutes
- [ ] **Time Savings:** Error reporting saves 5+ hours per week
- [ ] **Localization:** Chinese-speaking users can view error messages
- [ ] **Suppression Workflow:** "Wrong but acceptable" errors tracked with justification
- [ ] **Auto-Remediation:** 50%+ of fixable errors resolved automatically
- [ ] **Error Archiving:** Complete audit trail for compliance and analysis

---

## 8. Next Steps

### Immediate Actions (This Week):
1. [ ] Review and approve work plan (v2.2)
2. [ ] ✅ **CONFIRMED:** Pure JSON architecture for all definitions
3. [ ] Confirm decorator/interceptor pattern approach
4. [ ] Set up `error_handling/` module directory structure
5. [ ] Begin Phase 1: Create all JSON config files:
   - `config/error_codes.json`
   - `config/taxonomy.json`
   - `config/status_lifecycle.json`
   - `config/anatomy_schema.json`
   - `config/remediation_types.json`
   - `config/suppression_rules.json`
6. [ ] Define E-M-F-U taxonomy codes for all engines/modules
7. [ ] Define suppression rule schema

### Approval Required:
- [ ] Work plan timeline (5 weeks)
- [ ] E-M-F-U error code format (vs. legacy P1xx format)
- [ ] ✅ **Pure JSON architecture** (all definitions in JSON, loaders in Python)
- [ ] Decorator/interceptor pattern for error handling
- [ ] Error status column (Error_Status) addition
- [ ] Suppression logic workflow
- [ ] Remediation types and auto-fix rules
- [ ] Data Health KPI column (Step 48) addition
- [ ] Localization scope (which languages beyond en/zh)
- [ ] Fail-fast implementation approach for critical errors
- [ ] Resource allocation (developer hours)
- [ ] Integration approach with existing pipeline

### Key Decisions Needed:
1. **Error Code Format:** Adopt E-M-F-U (P-C-P-0101) or keep legacy (P101)?
2. ✅ **Architecture:** Pure JSON for all definitions (selected)
3. **Decorator Pattern:** Use AOP-style interceptors vs. traditional if/else?
4. **Status Column:** Add Error_Status column (Step 47) to output?
5. **Suppression Rules:** Who can approve suppression rules? (admin/manager/user)
6. **Auto-Remediation:** Which error types should be auto-fixed vs. manual?
7. **Localization Priority:** English + Chinese sufficient for MVP?
8. **Fail Fast Scope:** Stop on P1xx only, or include P2xx?
9. **Logging Destination:** Single file or multiple files by layer?
10. **Archiving:** How long to keep archived errors? (1 year / 3 years / forever)?
11. **Data Health KPI:** Add Data_Health_Score column (Step 48)?
12. **JSON Schema:** Use JSON Schema for validation (anatomy_schema.json)?
13. **Null Handling:** Track all fill failures as F4xx errors?

---

**Document Version:** 2.2  
**Last Updated:** April 10, 2026  
**Status:** Ready for Review  
**Next Review:** Upon approval

**Change Log:**
- **v2.2** (April 10, 2026) - Added 3 more requirements + Pure JSON Architecture (16 total):
  - **ARCHITECTURE:** Selected Option B - Pure JSON for all definitions
    - `config/taxonomy.json`, `config/status_lifecycle.json`
    - `config/anatomy_schema.json`, `config/remediation_types.json`
    - Python loaders in `core/*_loader.py`
  - **NEW:** Data Health KPI ((Total - Critical - High) / Total × 100)
  - **NEW:** Null Handling Error Handling (F4xx via decorators)
  - **NEW:** JSON Schema for Taxonomy Validation (`taxonomy_schema.json`)

- **v2.1** (April 10, 2026) - Major revision with 13 requirements (5 NEW):
  - "Fail Fast, Inform Well, Resolve Smart" philosophy
  - **NEW:** Error Status Lifecycle (Open→Suppressed→Resolved→Archived)
  - **NEW:** Suppression Logic ("wrong but acceptable" with justification)
  - **NEW:** Remediation Types (8 strategies: AUTO_FIX, MANUAL_FIX, SUPPRESS, etc.)
  - **NEW:** Decorator/Interceptor Pattern (AOP-style, no inline if/else)
  - **NEW:** Resolution Module (categorize, dispatch, remediate, archive)
  - E-M-F-U error code anatomy
  - JSON-based error registry
  - Multi-layer validation strategy (L1/L2/L3)
  - Global exception handling
  - Structured logging ("Log Everything")
  - Localization framework (en/zh)
  - 5-phase implementation

- **v2.0** (April 10, 2026) - Major revision with 8 requirements:
  - "Fail Fast, Inform Well" philosophy
  - E-M-F-U error code anatomy
  - JSON-based error registry
  - Multi-layer validation strategy (L1/L2/L3)
  - Global exception handling
  - Structured logging ("Log Everything")
  - Localization framework (en/zh)
  - 5-phase implementation (reduced from 6)

**References:**
- Error Code Framework: `data_error_handling.md` (24 error codes defined)
- Pipeline Architecture: `processing_pipeline_issues.md` (phased processing P1→P2→P2.5→P3)
- Schema Definition: `config/schemas/dcc_register_enhanced.json` (46 columns)
