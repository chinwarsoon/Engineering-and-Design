# Appendix I — Schema-Driven Filename Parser (Universal Class)

**Document ID**: WP-EKS-P1-APX-I  
**Version**: 0.3  
**Last Updated**: 2026-07-18  
**Phase**: 1 — Foundation  
**Status**: 📋 Proposed for Review  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) §20 (Document Registry & Revision Management)  
**Related Issues**: [I133](../log/issue_log.md), [I134](../log/issue_log.md), [I135](../log/issue_log.md), [I136](../log/issue_log.md), [I137](../log/issue_log.md)  
**Related Appendices**:
- [Appendix B — Document Registry](appendix_b_document_registry.md) — registry columns, SUPERSEDES chains, ontology triggers
- [Appendix D — Pipeline Messages & Errors](appendix_d_pipeline_messages_errors.md) — D5-PARSE-* error code taxonomy, D7.1 health scoring
- [Appendix F — Pipeline Architecture](appendix_f_pipeline_architecture_design.md) — Phase A/B orchestration flow
- [Appendix J — File Property Parser](appendix_j_file_property_parser.md) — OS-level + embedded property extraction, boundary definition

**Related Files**:
- [`eks/engine/core/file_scanner.py`](../engine/core/file_scanner.py) — current `_parse_filename()` (L145–174)
- [`eks/engine/core/pipeline_orchestrator.py`](../engine/core/pipeline_orchestrator.py) — inline duplicate extraction (L567, L645)
- [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — target for `filename_patterns` block
- [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — schema declarations
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — shared definitions
- [`eks/config/schemas/eks_error_config.json`](../config/schemas/eks_error_config.json) — D5-PARSE-* error code registration
- [`eks/engine/core/registry.py`](../engine/core/registry.py) — `register_document()` / `get_document()`
- [`eks/ui/backend/phase1_server.py`](../ui/backend/phase1_server.py) — UI-side filename parsing

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.3 | 2026-07-18 | CodeBuddy | Added §I1.1 boundary definition: explicit separation from FilePropertyExtractor (Appendix J), system-values breakdown table (3 categories, 3 sources), clean-architecture rationale |
| 0.2 | 2026-07-18 | CodeBuddy | Major redesign: universal class (`FilenameParser` + `FilenameParseResult`), segment-based field extraction aligned with Appendix B registry columns, 9-field output, full D5-PARSE-001–007 error taxonomy, cross-appendix alignment table |
| 0.1 | 2026-07-18 | CodeBuddy | Initial draft: I1–I10 (Overview, Problems, Filename Analysis, Schema Design, Algorithm, Shared Parser Module, Null-Tolerant Registration, Call-Site Migration, Per-Project Configuration, Implementation Plan) |

---

## I1. Overview

The filename parser extracts structured metadata from source filenames during Phase A (file discovery + registration) and Phase B (pipeline processing). Currently the logic is duplicated across 4 call sites using 2 divergent algorithms, with hardcoded rules that cannot be customized per project, extracts only 2 of 5 available fields, and has no support for null-registration when extraction fails.

This appendix defines a **schema-driven**, **universal-class**, **null-tolerant** filename parser that:

1. Moves extraction rules into `eks_doc_config.json` as a `filename_patterns` block with segment-level field mapping (per-project, per I136)
2. Consolidates all parsing logic into a single `FilenameParser` class in a shared module (per I135)
3. Extracts all 7 filename-derived fields (`document_number`, `revision`, `project_number`, `area`, `document_type`, `discipline`, `sequence_number`) identified in Appendix B §B3
4. Supports null returns when extraction genuinely fails, with pipeline layers relaxed to accept nulls (per I134)
5. Eliminates the Phase A/Phase B algorithm divergence (root cause of I133/D5-PARSE-003)
6. Registers error codes `D5-PARSE-001` through `D5-PARSE-007` in the formal error catalog (per I137)

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Schema-driven** | Per-project filename patterns + segment definitions in config JSON, not hardcoded in Python |
| **Universal class** | Single `FilenameParser` class shared by all call sites; one instantiation per project, reused across all files in a scan |
| **Fail-safe** | Never drop a file — return `parse_status: "unresolvable"` with synthetic keys; register with degraded quality markers |
| **Project hierarchy** | `{project_code}` pattern overrides `"*"` catch-all default |
| **Segment-aware** | Filename is decomposed into positional segments; each maps to a registry column per Appendix B |
| **Suffix-aware** | Strip known non-revision suffixes (`_AddN`, `_2-Stage`, `_HAC`) before segment/revision extraction |
| **Length-guarded** | Dash-suffix revision detection uses configurable `dash_revision_max_len` |
| **Backward compatible** | Default `"*"` pattern replicates current hardcoded behavior |

### I1.1 Boundary: What the Filename Parser Does and Does NOT Handle

The filename parser is a **string-level operation only**. It operates on `Path.stem` — zero I/O, zero disk access. It does not verify file existence, does not open files, and does not depend on any parsing library.

The full set of "system-related" values that describe a file come from **3 distinct sources** with **3 distinct failure modes** and **3 distinct lifecycle stages**. Only Source A belongs in this class.

| Category | Source | Field Count | I/O Type | Pipeline Stage | Failure Domain | Handled By |
|:---|:---|:---:|:---|:---|:---|:---|
| **A. Filename-derived** | String parsing (`Path.stem`) | 7 | None — pure string operation | P0 (scan) | D5-PARSE-001..007 | **`FilenameParser`** (this appendix) |
| **B. OS-level** | `Path.stat()` / `hashlib` | 6 | Disk I/O, system calls | P0 / Phase B | D5-PROP-001, 002, 005 | **`FilePropertyExtractor`** (Appendix J) |
| **C. Embedded metadata** | Parser `extract_metadata()` | 11+ | File open, parsing libraries | Phase B | D5-PROP-003, 004 | **`FilePropertyExtractor`** (Appendix J) |

#### Why Categories B and C Must NOT Be in FilenameParser

**1. Different input type.** `FilenameParser.parse()` accepts a `str` — the filename. It does not need a real file to exist on disk:

```python
parser.parse("131101-WSW41-SP-SG-0101.pdf")  # file need not exist
```

OS properties and embedded metadata require a **real, accessible file path**:

```python
Path.stat()           # requires OS permissions on a real file
pdfplumber.open()     # requires opening and parsing a real file on disk
```

Adding these to `FilenameParser` would turn a pure string parser into a side-effect-producing I/O class — a fundamental change in its nature.

**2. Different pipeline timing.** In Phase A, the file has not yet been parsed — embedded metadata is unavailable. In Phase B, all three sources are available. If merged into one class, the same method would return different results depending on when it is called — a fragile pattern.

**3. Different error domains.** Naming-convention violations (D5-PARSE-*) have fundamentally different severity and recovery strategies than disk permission errors (D5-PROP-*). Mixing them would force a single `try/except` to handle both simultaneously.

**4. Different dependency profiles.** `FilenameParser` depends only on `re`, `dataclasses`, and `pathlib.Path` (only `.stem`). It is safe to import at PRESTART without any guards. `FilePropertyExtractor` requires `hashlib`, `datetime`, `os.stat`, and parser libraries — it needs `_preload_infrastructure()` guards for Python 3.13.

#### Clean Architecture Decision

| Concern | Handler | Rationale |
|:---|:---|:---|
| Extract structured fields from naming convention | `FilenameParser` | Pure string operation, testable without I/O |
| Collect filesystem timestamps, size, permissions | `FilePropertyExtractor` Layer 1 | Requires OS calls, unrelated to naming |
| Extract author, page count, title | `FilePropertyExtractor` Layer 2 | Requires parsed metadata, format-specific |
| Merge all into registry row | `PipelineOrchestrator` or `FileScanner` | Only the orchestrator sees the full picture |

**Integration point:** `PipelineOrchestrator._process_file()` calls both and merges the results:

```python
# Phase A: FileScanner
parse_result = self._filename_parser.parse(file_name)     # string → 7 fields
os_props = self._prop_extractor.extract(file_path,        # disk → 6 fields
               file_type, parser_metadata=None)
metadata = {**parse_result.to_metadata_dict(),
            **os_props.to_registry_dict()}

# Phase B: PipelineOrchestrator
parse_result = self._filename_parser.parse(file_name)     # re-parse for consistency
parser_metadata = parser.extract_metadata()               # now available
full_props = self._prop_extractor.extract(file_path,      # OS + embedded
                file_type, parser_metadata)
registry_update = {**parse_result.to_metadata_dict(),
                   **full_props.to_registry_dict()}
```

**No third class needed. No merging needed.** The boundary is clean, coupling is low in both directions.

### Design Decision: Class vs. Module-Level Function

| Factor | Module-Level Function | Universal Class | Decision |
|--------|----------------------|-----------------|----------|
| **Internal state** | None (stateless) | Caches compiled regex, resolved pattern, error list | **Class** — segment validation requires compiled patterns; caching avoids re-compile per file |
| **Return complexity** | Dict with 2 keys | `FilenameParseResult` dataclass with 9 fields + type safety | **Class** — IDE autocomplete, type checking, `.to_metadata_dict()` convenience |
| **Testability** | Parameterized function | Construct once, call `.parse(fname)` in loop | **Class** — natural for scan-loop usage; one instantiation, many calls |
| **Extensibility** | Add parameters → break signature | Add methods: `.parse_batch()`, `.generate_filename()` | **Class** — future methods fit naturally |
| **Call-site ergonomics** | `parse_filename(f, patterns, code)` | `parser = FilenameParser(patterns, code); parser.parse(f)` | **Class** — callers hold a reference; no repeated config passing |

**Conclusion**: The filename parser is implemented as a **universal class** (`FilenameParser`) in a standalone module (`eks/engine/core/filename_parser.py`). A module-level convenience function `parse_filename()` is also provided for one-shot usage.

---

## I2. Problem Analysis

### I2.1 Current State — 4 Call Sites, 2 Algorithms

| # | Location | Algorithm | Length Guard | Output Fields |
|---|----------|-----------|--------------|---------------|
| **A** | `FileScanner._parse_filename()` L145–174 | 3-path: `_rev` split → `rsplit("-", 1)` only if `≤3` chars → fallback full stem | ✅ Yes | 2 (`doc_number`, `revision`) |
| **A** | `phase1_server.py` L393 | Calls `scanner.build_placeholder_metadata()` → uses algorithm A | ✅ Yes (via A) | 2 |
| **B** | `PipelineOrchestrator._process_file()` L567 | Inline: `stem.split("_rev")[0].rsplit("-", 1)[0]` | ❌ No | 1 (`doc_number` only) |
| **B** | `PipelineOrchestrator._update_doc_status()` L645 | Identical inline one-liner | ❌ No | 1 |

### I2.2 Divergent Outputs — Root Cause of D5-PARSE-003

For file `131101-WSW41-SP-SP-0801_Add3.pdf`:

| Phase | Algorithm | Extracted `doc_number` | Reason |
|-------|-----------|------------------------|--------|
| **Phase A** (register) | A — `_parse_filename()` | `"131101-WSW41-SP-SP-0801_Add3"` | `_Add3` = 4 chars > 3 → falls through dash-split → full stem fallback |
| **Phase B** (lookup) | B — inline one-liner | `"131101-WSW41-SP-SP-0801"` | Unconditionally strips after last `-` → drops `-0801` → keeps parent |

Phase B looks up `"131101-WSW41-SP-SP-0801"` in the registry → not found (registered as `"131101-WSW41-SP-SP-0801_Add3"`) → **D5-PARSE-003**.

### I2.3 Missing Field Extraction — Appendix B Gap

The registry (Appendix B §B3) defines 5 columns sourced from the filename. Only 2 are currently extracted:

| Registry Column | Source | Health Tier | Currently Extracted? |
|:---|:---|:---|:---|
| `project_number` | Filename segment 0 | T1 | ❌ No |
| `area` | Filename segment 1 | T2 | ❌ No |
| `document_type` | Filename segment 2 (→ ontology trigger) | T1 | ❌ No |
| `discipline` | Filename segment 3 | T1 | ❌ No |
| `document_number` | All segments rejoined | T1 | ✅ Yes |
| `revision` | Suffix | T1 | ✅ Yes |

Phase 3 (ontology) waits for `document_type` to assign classes. If it's in the filename, it should be extracted at Phase A.

### I2.4 Gaps Mapped to Issues

| Gap | Issue | Severity |
|-----|-------|----------|
| Phase A/B algorithm divergence | I133 | 🟠 High |
| No null-registration support (3 layers) | I134 | 🟠 High |
| No shared parser module (4 call sites) | I135 | 🟡 Medium |
| Hardcoded patterns, no per-project config | I136 | 🟠 High |
| `D5-PARSE-003` not in error catalog | I137 | 🟢 Low |
| Only 2/5 filename-derived columns extracted | (this appendix) | 🟠 High |

---

## I3. TWRP Filename Analysis (Ground Truth)

Analysis of all 171 files under `eks/data/twrp/` reveals 3 filename families.

### I3.1 Family A — Standard TenderSpec (project code 131101)

**Pattern**: `{project_code}-{contract}-{type_code}-{discipline}-{seq_number}[_{suffix}].{ext}`

**Segment-to-Column Mapping** (aligned with Appendix B §B3):

| Position | Segment | Example Value | `maps_to` Column | Appendix B Tier | Notes |
|:---------|:--------|:--------------|:-----------------|:----------------|:------|
| 0 | `project_code` | `131101` | `project_number` | T1 (Project) | 6-digit project ID |
| 1 | `contract` | `WSW41` | `area` | T2 (Project) | Contract/area code |
| 2 | `type_code` | `SP` | `document_type` | T1 (Document) | Maps to ontology class per B3.1: `SPC→Specification` |
| 3 | `discipline` | `SG` / `SP` | `discipline` | T1 (Project) | SG=General Works, SP=Specific Works |
| 4 | `seq_number` | `0101`–`1300` | *(no maps_to — rejoined)* | — | 4-digit sequence, used in `document_number` |
| — | `suffix` | `_Add1`, `_Add3`, `_2-Stage`, `_HAC` | *(stripped)* | — | Non-revision qualifier, stripped before parse |

**Subtypes**:

| Subtype | Pattern | Count | Example |
|---------|---------|-------|---------|
| A1 — Clean | `131101-WSW41-SP-SG-0101.pdf` | ~140 | Standard, no suffix |
| A2 — Addendum | `131101-WSW41-SP-SP-0801_Add3.pdf` | 4 | `_Add1`, `_Add3` |
| A3 — Two-stage | `131101-WSW41-SP-SP-0202_2-Stage.pdf` | 7 | `_2-Stage`, `_2-stage` |
| A4 — HAC | `131101-WSW41-SP-SP-0501_HAC.pdf` | 1 | `_HAC` suffix |

**Known suffixes for Family A (TWRP 131101)**:

| Suffix | Meaning | Is Revision? | Count |
|--------|---------|-------------|-------|
| `_Add1`, `_Add3` | Addendum 1, Addendum 3 | ❌ No | 4 |
| `_2-Stage`, `_2-stage` | Two-stage tender | ❌ No | 7 |
| `_HAC` | Unknown qualifier | ❌ No | 1 |

### I3.2 Family B — Cover / Contents Pages

**Pattern**: `{prefix}_{descriptor}-{vol_info}[_{suffix}].{ext}`

| Subtype | Example | Count |
|---------|---------|-------|
| B1 — Cover | `00a_CoverPage_Vol2_C4B.pdf` | 3 |
| B2 — Contents | `00c_Contents - Vol 2_C4B.pdf` | 3 |
| B3 — Two-Stage Cover | `00a_Cover Page - Vol 3_C4B_2-Stage.pdf` | 4 |

**Parsing target**: No standard `{project_code}-{contract}-...` prefix. Fallback to full stem as `doc_number`, all segment fields `null`, `parse_status: "unresolvable"`.

### I3.3 Family C — SOP / Preamble

**Pattern**: `{seq}_{TWRP}_{C4B}_{type}_{discipline}[_{qualifier}].{ext}`

| Example | Count |
|---------|-------|
| `02_TWRP_C4B_SOP1_PG_pwp.xlsx` | 8 |
| `17_TWRP_C4B_Preamble_FSOR _Work.pdf` | 2 |

**Parsing target**: Fallback to full stem as `doc_number`, all segment fields `null`, `parse_status: "unresolvable"`.

### I3.4 Summary Distribution

| Family | Count | Segments extractable? | `revision` extractable? | `parse_status` |
|--------|-------|-----------------------|------------------------|----------------|
| A1 (clean) | ~140 | ✅ All 5 segments | ✅ null (no rev suffix) | `ok` |
| A2 (addendum) | 4 | ✅ After suffix strip | ✅ null | `ok` |
| A3 (two-stage) | 7 | ✅ After suffix strip | ✅ null | `ok` |
| A4 (HAC) | 1 | ✅ After suffix strip | ✅ null | `ok` |
| B (cover/contents) | ~10 | ❌ Fallback only | ❌ null | `unresolvable` |
| C (SOP/Preamble) | ~10 | ❌ Fallback only | ❌ null | `unresolvable` |
| **TOTAL** | **171** | — | — | — |

**Key finding**: No file in the TWRP dataset contains a genuine revision in the filename. All files use `revision = null` (per I134). The `revision_validation` regex (`^[A-Z0-9]{1,2}$`) applies to post-extraction validation, not filename parsing.

---

## I4. Schema Design — `filename_patterns` with Segments

### I4.1 Location

New top-level key `filename_patterns` in `eks_doc_config.json`, sibling to `revision_validation`, `ontology_triggers`, etc.

### I4.2 Structure — Full Config Block

```json
"filename_patterns": {
    "131101": {
        "description": "TWRP WSD11 tenderspec naming: {project}-{area}-{type}-{disc}-{seq}[_suffix].ext",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 5,
        "max_segments": 5,
        "segments": [
            {
                "position": 0,
                "maps_to": "project_number",
                "label": "project_code",
                "required": true,
                "null_handling": { "strategy": "default_value", "default_value": "131101" },
                "validation": { "type": "pattern", "pattern": "^\\d{6}$" }
            },
            {
                "position": 1,
                "maps_to": "area",
                "label": "contract_or_area",
                "required": true,
                "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
                "validation": { "type": "pattern", "pattern": "^[A-Z0-9]{3,6}$" }
            },
            {
                "position": 2,
                "maps_to": "document_type",
                "label": "type_code",
                "required": true,
                "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
                "validation": { "type": "schema_reference", "reference": "document_type_registry" }
            },
            {
                "position": 3,
                "maps_to": "discipline",
                "label": "discipline_code",
                "required": true,
                "null_handling": { "strategy": "default_value", "default_value": "UNKNOWN" },
                "validation": { "type": "pattern", "pattern": "^[A-Z]{2}$" }
            },
            {
                "position": 4,
                "maps_to": null,
                "label": "sequence_number",
                "required": true,
                "null_handling": { "strategy": "default_value", "default_value": "0000" },
                "validation": { "type": "pattern", "pattern": "^\\d{4}$" }
            }
        ],
        "rejoin_separator": "-",
        "strip_suffixes": ["_Add1", "_Add2", "_Add3", "_2-Stage", "_2-stage", "_HAC"],
        "revision_separators": ["_rev"],
        "dash_revision_max_len": 3,
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": null,
            "preservation_mode": "overwrite_existing"
        },
        "error_subcodes": {
            "too_few_segments": "D5-PARSE-004",
            "too_many_segments": "D5-PARSE-005",
            "segment_validation_failed": "D5-PARSE-006",
            "unresolvable": "D5-PARSE-007"
        },
        "processing_phase": "P0"
    },
    "*": {
        "description": "Default: generic dash-suffix revision detection (backward compatible)",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 1,
        "max_segments": null,
        "segments": [],
        "rejoin_separator": "-",
        "strip_suffixes": [],
        "revision_separators": ["_rev"],
        "dash_revision_max_len": 3,
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": "00",
            "preservation_mode": "overwrite_existing"
        },
        "error_subcodes": {},
        "processing_phase": "P0"
    }
}
```

### I4.3 Field Definitions

#### Top-Level Pattern Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | `string` | Yes | Human-readable explanation of this project's naming convention |
| `parser_type` | `enum["delimited"]` | Yes | Parser strategy. Currently only `"delimited"` (split by separator). Future: `"regex"`, `"template"`. |
| `separator` | `string` | Yes | Character used to split the stem into segments |
| `min_segments` | `integer` | Yes | Minimum expected segment count. Fewer → `D5-PARSE-004`. |
| `max_segments` | `integer` or `null` | Yes | Maximum expected segment count. More → `D5-PARSE-005`. `null` = unlimited. |
| `segments` | `array[segment_def]` | Yes | Ordered segment definitions (see §I4.4). Empty array `[]` for fallback-only patterns. |
| `rejoin_separator` | `string` | Yes | Separator used when rejoining segments into `document_number` |
| `strip_suffixes` | `array[string]` | Yes | Suffixes to remove from stem **before** parsing. Applied in declaration order. Case-sensitive. |
| `revision_separators` | `array[string]` | Yes | Separators that indicate a revision follows (e.g., `["_rev"]`). |
| `dash_revision_max_len` | `integer` | Yes | Max length for trailing dash-segment to be considered revision. `0` = disabled. |
| `output` | `object` | Yes | Output control (see §I4.5) |
| `error_subcodes` | `object` | Yes | Maps error conditions to specific D5-PARSE-* codes |
| `processing_phase` | `enum["P0"]` | Yes | Phase when filename parsing runs. Always `"P0"` (pre-registration). |

#### I4.4 Segment Definition Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `position` | `integer` | Yes | Zero-based index into the split stem parts |
| `maps_to` | `string` or `null` | Yes | Target registry column name (per Appendix B §B3). `null` = used in `document_number` rejoining only. |
| `label` | `string` | Yes | Human-readable segment name for logging/errors |
| `required` | `boolean` | Yes | Whether this segment must be present |
| `null_handling` | `object` | Yes | Strategy + fallback when segment is missing or invalid (see §I4.6) |
| `validation` | `object` | Yes | Validation rule for the segment value (see §I4.7) |

#### I4.5 Output Control Fields

| Field | Type | Description |
|-------|------|-------------|
| `document_number_source` | `enum["rejoin_segments"]` | How `document_number` is constructed. Currently `"rejoin_segments"` = join all split parts with `rejoin_separator`. |
| `fallback_doc_number` | `enum["full_stem"]` | Strategy when segment extraction fails entirely. `"full_stem"` = use the entire cleaned stem. |
| `fallback_revision` | `string` or `null` | Revision value when none extracted. `null` for I134 null-registration; `"00"` for backward compat. |
| `preservation_mode` | `enum["overwrite_existing"]` | How filename-derived values interact with existing registry values. Always `"overwrite_existing"` at P0. |

#### I4.6 Null-Handling Strategies

| Strategy | Behavior |
|----------|----------|
| `"default_value"` | Use `default_value` when segment missing or invalid |
| `"skip_segment"` | Omit from output (future) |
| `"raise_error"` | Treat as hard failure (future) |

#### I4.7 Validation Types

| Type | Fields | Description |
|------|--------|-------------|
| `"pattern"` | `pattern` (regex string) | Match segment value against regex. Fail → log `D5-PARSE-006`, use `null_handling`. |
| `"schema_reference"` | `reference` (config key) | Look up segment value in named registry (e.g., `document_type_registry`). Fail → log `D5-PARSE-006`, use `null_handling`. |

#### I4.8 `maps_to` ↔ Appendix B Registry Column Alignment

| `maps_to` Value | Registry Column (B3) | B3 Group | D7.1 Health Tier | Phase 3 Ontology Trigger |
|:---|:---|:---|:---|:---|
| `"project_number"` | `project_number` (VARCHAR) | Project | T1 | — |
| `"area"` | `area` (VARCHAR) | Project | T2 | — |
| `"document_type"` | `document_type` (VARCHAR) | Document | T1 | Class assignment (B3.1): `SPC→Specification`, `DWG→Drawing` |
| `"discipline"` | `discipline` (VARCHAR) | Project | T1 | — |
| `null` | *(only used in rejoined `document_number`)* | — | — | SUPERSEDES chains (B3.1) |

### I4.9 Matching Priority

When the parser is invoked, it selects the pattern as follows:

```
1. If project_code is known → use filename_patterns[project_code]
2. Else → use filename_patterns["*"]
3. If filename_patterns is absent from config → use hardcoded defaults matching current "*"
```

**Note on project_code discovery**: In Phase A, project_code is extracted from the data folder structure (`eks/data/twrp/` → project "TWRP" → code "131101"). A future task (beyond I136 scope) will implement formal `project_folder → project_code` mapping. Until then, the parser receives `project_code` as an optional parameter; when not provided, `"*"` is used.

### I4.10 Schema Validation — Setup Schema Changes

In `eks_doc_setup_schema.json`, add to `properties`:

```json
"filename_patterns": {
    "type": "object",
    "description": "Per-project filename parsing patterns with segment definitions. Keys are project codes or '*' for default. (Appendix I v0.2)",
    "propertyNames": {
        "pattern": "^(\\*|\\d{6})$"
    },
    "additionalProperties": {
        "type": "object",
        "properties": {
            "description": { "type": "string" },
            "parser_type": { "type": "string", "enum": ["delimited"] },
            "separator": { "type": "string", "minLength": 1 },
            "min_segments": { "type": "integer", "minimum": 1 },
            "max_segments": {
                "oneOf": [
                    { "type": "integer", "minimum": 1 },
                    { "type": "null" }
                ]
            },
            "segments": {
                "type": "array",
                "items": { "$ref": "#/definitions/filename_segment_def" }
            },
            "rejoin_separator": { "type": "string" },
            "strip_suffixes": {
                "type": "array",
                "items": { "type": "string" }
            },
            "revision_separators": {
                "type": "array",
                "items": { "type": "string" }
            },
            "dash_revision_max_len": { "type": "integer", "minimum": 0 },
            "output": {
                "type": "object",
                "properties": {
                    "document_number_source": { "type": "string", "enum": ["rejoin_segments"] },
                    "fallback_doc_number": { "type": "string", "enum": ["full_stem"] },
                    "fallback_revision": {
                        "oneOf": [
                            { "type": "string" },
                            { "type": "null" }
                        ]
                    },
                    "preservation_mode": { "type": "string", "enum": ["overwrite_existing"] }
                },
                "required": ["document_number_source", "fallback_doc_number", "fallback_revision", "preservation_mode"],
                "additionalProperties": false
            },
            "error_subcodes": {
                "type": "object",
                "properties": {
                    "too_few_segments": { "type": "string" },
                    "too_many_segments": { "type": "string" },
                    "segment_validation_failed": { "type": "string" },
                    "unresolvable": { "type": "string" }
                },
                "additionalProperties": false
            },
            "processing_phase": { "type": "string", "enum": ["P0"] }
        },
        "required": ["description", "parser_type", "separator", "min_segments", "max_segments",
                     "segments", "rejoin_separator", "strip_suffixes", "revision_separators",
                     "dash_revision_max_len", "output", "error_subcodes", "processing_phase"],
        "additionalProperties": false
    },
    "minProperties": 1
}
```

In `eks_doc_base_schema.json`, add the shared definitions:

```json
"filename_pattern_def": {
    "type": "object",
    "description": "Per-project filename parsing pattern definition (Appendix I v0.2)",
    "properties": {
        "description": { "type": "string" },
        "parser_type": { "type": "string", "enum": ["delimited"] },
        "separator": { "type": "string", "minLength": 1 },
        "min_segments": { "type": "integer", "minimum": 1 },
        "max_segments": {
            "oneOf": [
                { "type": "integer", "minimum": 1 },
                { "type": "null" }
            ]
        },
        "segments": {
            "type": "array",
            "items": { "$ref": "#/definitions/filename_segment_def" }
        },
        "rejoin_separator": { "type": "string" },
        "strip_suffixes": { "type": "array", "items": { "type": "string" } },
        "revision_separators": { "type": "array", "items": { "type": "string" } },
        "dash_revision_max_len": { "type": "integer", "minimum": 0 },
        "output": { "$ref": "#/definitions/filename_output_def" },
        "error_subcodes": { "$ref": "#/definitions/filename_error_subcodes_def" },
        "processing_phase": { "type": "string", "enum": ["P0"] }
    },
    "required": ["description", "parser_type", "separator", "min_segments", "max_segments",
                 "segments", "rejoin_separator", "strip_suffixes", "revision_separators",
                 "dash_revision_max_len", "output", "error_subcodes", "processing_phase"],
    "additionalProperties": false
},
"filename_segment_def": {
    "type": "object",
    "description": "A positional segment extracted from a delimited filename (Appendix I v0.2)",
    "properties": {
        "position": { "type": "integer", "minimum": 0 },
        "maps_to": {
            "oneOf": [
                { "type": "string" },
                { "type": "null" }
            ]
        },
        "label": { "type": "string" },
        "required": { "type": "boolean" },
        "null_handling": {
            "type": "object",
            "properties": {
                "strategy": { "type": "string", "enum": ["default_value", "skip_segment", "raise_error"] },
                "default_value": { "type": "string" }
            },
            "required": ["strategy"],
            "additionalProperties": false
        },
        "validation": {
            "type": "object",
            "properties": {
                "type": { "type": "string", "enum": ["pattern", "schema_reference"] },
                "pattern": { "type": "string" },
                "reference": { "type": "string" }
            },
            "required": ["type"],
            "additionalProperties": false
        }
    },
    "required": ["position", "maps_to", "label", "required", "null_handling", "validation"],
    "additionalProperties": false
},
"filename_output_def": {
    "type": "object",
    "description": "Output control for filename parsing (Appendix I v0.2)",
    "properties": {
        "document_number_source": { "type": "string", "enum": ["rejoin_segments"] },
        "fallback_doc_number": { "type": "string", "enum": ["full_stem"] },
        "fallback_revision": {
            "oneOf": [
                { "type": "string" },
                { "type": "null" }
            ]
        },
        "preservation_mode": { "type": "string", "enum": ["overwrite_existing"] }
    },
    "required": ["document_number_source", "fallback_doc_number", "fallback_revision", "preservation_mode"],
    "additionalProperties": false
},
"filename_error_subcodes_def": {
    "type": "object",
    "description": "Error subcode mapping for filename parsing failures (Appendix I v0.2)",
    "properties": {
        "too_few_segments": { "type": "string" },
        "too_many_segments": { "type": "string" },
        "segment_validation_failed": { "type": "string" },
        "unresolvable": { "type": "string" }
    },
    "additionalProperties": false
}
```

---

## I5. Parsing Algorithm

### I5.1 Class Design — `FilenameParser`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re


@dataclass
class FilenameParseResult:
    """
    Immutable result of parsing a single filename.

    All filename-derived fields are Optional[str] — null means
    "not extractable from this filename."  The Registry always
    receives a complete result; null fields trigger per-segment
    null_handling defaults downstream.

    Fields are ordered per Appendix B §B3 column priority.
    """
    document_number: Optional[str] = None
    revision: Optional[str] = None
    project_number: Optional[str] = None
    area: Optional[str] = None
    document_type: Optional[str] = None
    discipline: Optional[str] = None
    sequence_number: Optional[str] = None
    parse_status: str = "unresolvable"   # "ok" | "partial" | "unresolvable"
    parse_errors: List[str] = field(default_factory=list)

    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Convert to the flat dict expected by register_document().

        Excludes parse_status and parse_errors (internal fields).
        Excludes None-valued fields so the registry's schema defaults apply.
        """
        return {
            k: v for k, v in {
                "document_number": self.document_number,
                "revision": self.revision,
                "project_number": self.project_number,
                "area": self.area,
                "document_type": self.document_type,
                "discipline": self.discipline,
                "sequence_number": self.sequence_number,
            }.items() if v is not None
        }


class FilenameParser:
    """
    Schema-driven filename parser — universal class shared by all EKS call sites.

    Design:
      - Instantiated once per project per pipeline run.
      - Caches compiled regex patterns and resolved schema references.
      - .parse(file_name) → FilenameParseResult (never raises).
      - Call sites: FileScanner (Phase A), PipelineOrchestrator (Phase B),
                    phase1_server.py (UI endpoint).

    Revision: 0.2
    Date: 2026-07-18
    Author: CodeBuddy
    Summary: Universal class with segment-based field extraction,
             FilenameParseResult dataclass, cached validators.
    """

    # Hardcoded default when no config is available (backward compat with v0.1)
    _HARDCODED_DEFAULT: Dict[str, Any] = {
        "description": "Hardcoded default (backward-compatible)",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 1,
        "max_segments": None,
        "segments": [],
        "rejoin_separator": "-",
        "strip_suffixes": [],
        "revision_separators": ["_rev"],
        "dash_revision_max_len": 3,
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": "00",
            "preservation_mode": "overwrite_existing",
        },
        "error_subcodes": {},
        "processing_phase": "P0",
    }

    def __init__(
        self,
        filename_patterns: Optional[Dict[str, Any]] = None,
        project_code: Optional[str] = None,
        document_type_registry: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Args:
            filename_patterns: The 'filename_patterns' block from eks_doc_config.json.
                               If None, use _HARDCODED_DEFAULT.
            project_code: Optional project code to select project-specific pattern.
                          Falls back to '*' pattern if not found.
            document_type_registry: Optional list of document type entries for
                                    schema_reference validation (maps_to: "document_type").
        """
        self._patterns = filename_patterns or {}
        self._project_code = project_code
        self._doc_type_registry = document_type_registry or []
        self._pattern = self._resolve_pattern()
        self._compiled_validators: Dict[int, re.Pattern] = {}
        self._doc_type_codes: Optional[set] = None
        self._precompile_validators()

    # ---- Pattern Resolution ----

    def _resolve_pattern(self) -> Dict[str, Any]:
        """Resolve the active pattern: project_code → '*' → hardcoded default."""
        if not self._patterns:
            return dict(self._HARDCODED_DEFAULT)
        pattern = self._patterns.get(self._project_code) if self._project_code else None
        if pattern is None:
            pattern = self._patterns.get("*", self._HARDCODED_DEFAULT)
        # Merge with hardcoded default for any missing keys
        merged = dict(self._HARDCODED_DEFAULT)
        merged.update(pattern)
        return merged

    def _precompile_validators(self) -> None:
        """Pre-compile regex patterns for segment validation to avoid re-compile per file."""
        for seg in self._pattern.get("segments", []):
            validation = seg.get("validation", {})
            if validation.get("type") == "pattern" and validation.get("pattern"):
                self._compiled_validators[seg["position"]] = re.compile(validation["pattern"])
        # Pre-build document_type lookup set for schema_reference validation
        if self._doc_type_registry:
            self._doc_type_codes = {entry.get("code", "") for entry in self._doc_type_registry}

    # ---- Main Entry Point ----

    def parse(self, file_name: str) -> FilenameParseResult:
        """
        Parse a single filename into structured metadata.

        Never raises — always returns FilenameParseResult
        with parse_status indicating extraction quality.

        Args:
            file_name: Full filename (basename or path; Path.stem will be used).

        Returns:
            FilenameParseResult with all extractable fields populated.
        """
        result = FilenameParseResult()
        stem = Path(file_name).stem

        # Step 3: Strip known non-revision suffixes
        stem = self._strip_suffixes(stem)

        # Step 4: Revision separator split
        doc_stem, revision = self._extract_revision(stem)
        if revision is not None:
            result.revision = revision

        # Step 6: Segment extraction (on the stem after revision removal)
        segments_extracted = self._extract_segments(doc_stem, result)

        # Step 7: Construct document_number
        self._build_document_number(doc_stem, segments_extracted, result)

        # Finalize parse_status
        if not result.parse_errors:
            result.parse_status = "ok"
        elif result.parse_status == "unresolvable":
            pass  # keep unresolvable
        else:
            result.parse_status = "partial"

        return result

    # ---- Step 3: Suffix Stripping ----

    def _strip_suffixes(self, stem: str) -> str:
        """Strip the first matching non-revision suffix from the stem."""
        for suffix in self._pattern.get("strip_suffixes", []):
            if stem.endswith(suffix):
                return stem[:-len(suffix)]
        return stem

    # ---- Step 4: Revision Extraction ----

    def _extract_revision(self, stem: str) -> Tuple[str, Optional[str]]:
        """
        Try to extract a revision from the stem.

        Returns (remaining_stem, revision_or_None).
        """
        # 4a: Check explicit revision separators
        for sep in self._pattern.get("revision_separators", []):
            if sep in stem:
                parts = stem.split(sep, 1)
                return parts[0], parts[1]

        # 4b: Dash-suffix revision detection
        max_len = self._pattern.get("dash_revision_max_len", 0)
        if max_len > 0:
            parts = stem.rsplit("-", 1)
            if len(parts) == 2 and len(parts[1]) <= max_len:
                return parts[0], parts[1]

        return stem, None

    # ---- Step 6: Segment Extraction ----

    def _extract_segments(self, stem: str, result: FilenameParseResult) -> bool:
        """
        Split stem by separator and extract mapped fields into result.

        Returns True if at least one segment was successfully extracted.
        """
        segments = self._pattern.get("segments", [])
        if not segments:
            return False

        parts = stem.split(self._pattern.get("separator", "-"))

        # Check segment count bounds
        min_seg = self._pattern.get("min_segments", 1)
        max_seg = self._pattern.get("max_segments")

        if len(parts) < min_seg:
            err_code = self._pattern.get("error_subcodes", {}).get("too_few_segments", "D5-PARSE-004")
            result.parse_errors.append(
                f"{err_code}: Expected >= {min_seg} segments, got {len(parts)} in '{stem}'"
            )
            result.parse_status = "partial"
            # Still try to extract what we have

        if max_seg is not None and len(parts) > max_seg:
            err_code = self._pattern.get("error_subcodes", {}).get("too_many_segments", "D5-PARSE-005")
            result.parse_errors.append(
                f"{err_code}: Expected <= {max_seg} segments, got {len(parts)} in '{stem}'"
            )
            result.parse_status = "partial"

        any_extracted = False
        for seg_def in segments:
            pos = seg_def["position"]
            maps_to = seg_def.get("maps_to")
            label = seg_def.get("label", f"seg_{pos}")

            if pos >= len(parts):
                # Segment not present — apply null_handling
                self._apply_null_handling(seg_def, result, maps_to, label, reason="missing")
                continue

            raw_value = parts[pos]

            # Validate
            if not self._validate_segment(seg_def, raw_value):
                err_code = self._pattern.get("error_subcodes", {}).get(
                    "segment_validation_failed", "D5-PARSE-006"
                )
                result.parse_errors.append(
                    f"{err_code}: Segment validation failed at position {pos} "
                    f"('{label}' = '{raw_value}')"
                )
                result.parse_status = "partial"
                self._apply_null_handling(seg_def, result, maps_to, label,
                                          reason=f"validation_failed:{raw_value}")
                continue

            # Store the value
            if maps_to:
                setattr(result, maps_to, raw_value)
                any_extracted = True
            else:
                # maps_to is null — value used only in rejoined document_number
                # Store in sequence_number for reference
                result.sequence_number = raw_value
                any_extracted = True

        if not any_extracted:
            result.parse_status = "unresolvable"

        return any_extracted

    def _validate_segment(self, seg_def: Dict[str, Any], value: str) -> bool:
        """Validate a single segment value against its validation rule."""
        validation = seg_def.get("validation", {})
        vtype = validation.get("type")

        if vtype == "pattern":
            compiled = self._compiled_validators.get(seg_def["position"])
            if compiled:
                return bool(compiled.match(value))
            # Fallback: compile on the fly
            pattern = validation.get("pattern", "")
            if pattern:
                return bool(re.match(pattern, value))
            return True  # no pattern = no validation

        if vtype == "schema_reference":
            reference = validation.get("reference", "")
            if reference == "document_type_registry" and self._doc_type_codes is not None:
                return value in self._doc_type_codes
            # If registry not available, skip validation (warn via parse_status = "partial")
            return True

        return True  # unknown validation type → pass

    def _apply_null_handling(
        self,
        seg_def: Dict[str, Any],
        result: FilenameParseResult,
        maps_to: Optional[str],
        label: str,
        reason: str,
    ) -> None:
        """Apply the segment's null_handling strategy."""
        nh = seg_def.get("null_handling", {})
        strategy = nh.get("strategy", "default_value")

        if strategy == "default_value":
            default = nh.get("default_value", "UNKNOWN")
            if maps_to:
                setattr(result, maps_to, default)
        elif strategy == "skip_segment":
            pass  # leave field as None
        elif strategy == "raise_error":
            # Degrade gracefully — log as error but don't raise
            result.parse_errors.append(
                f"raise_error strategy triggered for segment '{label}' ({reason})"
            )

    # ---- Step 7: Document Number Construction ----

    def _build_document_number(
        self, stem: str, segments_extracted: bool, result: FilenameParseResult
    ) -> None:
        """Build the final document_number from segments or fallback."""
        output = self._pattern.get("output", {})

        if segments_extracted and output.get("document_number_source") == "rejoin_segments":
            # Rejoin all parts of the stem (after suffix/revision stripping)
            separator = self._pattern.get("rejoin_separator", "-")
            # Use the stem as-is since it's already cleaned of suffixes and revisions
            result.document_number = stem
        else:
            # Fallback
            if output.get("fallback_doc_number") == "full_stem":
                result.document_number = stem
            else:
                result.document_number = None

        # Apply fallback revision if none extracted
        if result.revision is None:
            result.revision = output.get("fallback_revision")


# ---- Module-Level Convenience Function ----

def parse_filename(
    file_name: str,
    filename_patterns: Optional[Dict[str, Any]] = None,
    project_code: Optional[str] = None,
    document_type_registry: Optional[List[Dict[str, Any]]] = None,
) -> FilenameParseResult:
    """
    One-shot convenience wrapper — instantiates FilenameParser per call.

    Prefer instantiating FilenameParser once and calling .parse() in a loop
    for batch operations (Phase A scan, pipeline processing).
    """
    parser = FilenameParser(filename_patterns, project_code, document_type_registry)
    return parser.parse(file_name)
```

### I5.2 Algorithm Steps (Detailed)

```
Input:  file_name, pattern (resolved at __init__)
Output: FilenameParseResult

Step 1: [__init__]: Resolve pattern
    pattern = patterns.get(project_code) or patterns.get("*") or _HARDCODED_DEFAULT
    Pre-compile segment validation regex patterns
    Pre-build document_type_registry lookup set

Step 2: [parse]: Extract stem
    stem = Path(file_name).stem

Step 3: Strip known non-revision suffixes
    for suffix in pattern["strip_suffixes"]:
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
            break

Step 4: Revision extraction
    4a. Check revision_separators: split on first match
        → left = doc_stem, right = revision
    4b. If dash_revision_max_len > 0:
        rsplit("-", 1); if suffix ≤ max_len → revision
    If no revision found → revision = None

Step 5: doc_stem = stem after revision removal (for segment extraction)

Step 6: Segment extraction (if pattern.segments is non-empty)
    6a. Split doc_stem by pattern.separator
    6b. Check min/max segment counts → D5-PARSE-004 / D5-PARSE-005 if violated
    6c. For each segment in pattern.segments:
        - If position ≥ len(parts) → apply null_handling (default_value)
        - Validate against segment.validation:
            - "pattern": regex match → D5-PARSE-006 on failure
            - "schema_reference": lookup in registry → D5-PARSE-006 on failure
        - If maps_to is not null → set result.{maps_to} = value
        - If maps_to is null → set result.sequence_number = value
    6d. If no segments extracted → parse_status = "unresolvable"

Step 7: Document number construction
    7a. If segments extracted → document_number = doc_stem (segments rejoined)
    7b. Else → fallback_doc_number strategy (full_stem)
    7c. If revision is still None → apply output.fallback_revision

Step 8: Finalize parse_status
    - No errors → "ok"
    - Errors but segments extracted → "partial"
    - No segments extracted → "unresolvable"
```

### I5.3 Worked Examples — TWRP (131101 Pattern)

#### Example 1: Clean Standard File

```
Input:  131101-WSW41-SP-SG-0101.pdf

Step 2: stem = "131101-WSW41-SP-SG-0101"
Step 3: Strip suffixes → no match
Step 4: _rev split → no _rev; dash-revision: "0101" = 4 chars > 3 → skip
Step 5: doc_stem = "131101-WSW41-SP-SG-0101"
Step 6: Split by "-" → ["131101", "WSW41", "SP", "SG", "0101"]
  6b: count=5, min=5, max=5 → OK
  6c: Segment[0]="131101" → pattern ^\d{6}$ → ✓ → project_number = "131101"
      Segment[1]="WSW41"  → pattern ^[A-Z0-9]{3,6}$ → ✓ → area = "WSW41"
      Segment[2]="SP"     → schema_ref document_type_registry → "SP" in registry? ✓ → document_type = "SP"
      Segment[3]="SG"     → pattern ^[A-Z]{2}$ → ✓ → discipline = "SG"
      Segment[4]="0101"   → pattern ^\d{4}$ → ✓ → sequence_number = "0101" (maps_to=null)
Step 7: document_number = "131101-WSW41-SP-SG-0101", revision = null
Step 8: 0 errors → parse_status = "ok"

Result:
  FilenameParseResult(
      document_number="131101-WSW41-SP-SG-0101",
      revision=None,
      project_number="131101",
      area="WSW41",
      document_type="SP",
      discipline="SG",
      sequence_number="0101",
      parse_status="ok",
      parse_errors=[]
  )
```

#### Example 2: Addendum Suffix

```
Input:  131101-WSW41-SP-SP-0801_Add3.pdf

Step 2: stem = "131101-WSW41-SP-SP-0801_Add3"
Step 3: Strip "_Add3" → stem = "131101-WSW41-SP-SP-0801"
Step 4: No _rev; dash-revision: "0801" = 4 > 3 → skip
Step 5: doc_stem = "131101-WSW41-SP-SP-0801"
Step 6: Split("-") → ["131101", "WSW41", "SP", "SP", "0801"]
  All 5 segments pass validation → same field mapping as Example 1
  discipline = "SP", sequence_number = "0801"
Step 7: document_number = "131101-WSW41-SP-SP-0801"  (Add3 stripped; stable across addenda)
Step 8: parse_status = "ok"

Result:
  FilenameParseResult(
      document_number="131101-WSW41-SP-SP-0801",
      revision=None,
      project_number="131101",
      area="WSW41",
      document_type="SP",
      discipline="SP",
      sequence_number="0801",
      parse_status="ok",
      parse_errors=[]
  )
```

#### Example 3: Invalid Segment

```
Input:  131101-WSD11-??-P-0001.pdf

Step 2: stem = "131101-WSD11-??-P-0001"
Step 3: No suffix match
Step 4: No _rev; dash-revision: "0001" = 4 > 3 → skip
Step 5: doc_stem = "131101-WSD11-??-P-0001"
Step 6: Split("-") → ["131101", "WSD11", "??", "P", "0001"]
  Segment[0]="131101" → ✓ → project_number = "131101"
  Segment[1]="WSD11"  → ✓ → area = "WSD11"
  Segment[2]="??"     → pattern ^[A-Z]{2}$ → FAIL → D5-PARSE-006
    null_handling: default_value = "UNKNOWN" → document_type = "UNKNOWN"
  Segment[3]="P"      → pattern ^[A-Z]{2}$ → FAIL → D5-PARSE-006
    null_handling: default_value = "UNKNOWN" → discipline = "UNKNOWN"
  Segment[4]="0001"   → ✓ → sequence_number = "0001"
Step 7: document_number = "131101-WSD11-??-P-0001"  (preserved as-is for traceability)
Step 8: 2 errors → parse_status = "partial"

Result:
  FilenameParseResult(
      document_number="131101-WSD11-??-P-0001",
      revision=None,
      project_number="131101",
      area="WSD11",
      document_type="UNKNOWN",
      discipline="UNKNOWN",
      sequence_number="0001",
      parse_status="partial",
      parse_errors=[
          "D5-PARSE-006: Segment validation failed at position 2 ('type_code' = '??')",
          "D5-PARSE-006: Segment validation failed at position 3 ('discipline_code' = 'P')"
      ]
  )
```

#### Example 4: Cover Page (Family B — unresolvable)

```
Input:  00a_CoverPage_Vol2_C4B.pdf

Step 2: stem = "00a_CoverPage_Vol2_C4B"
Step 3: No suffix match (suffix list is for Family A)
Step 4: No _rev; dash-revision: "C4B" = 3 ≤ 3 → WOULD match as revision!
Step 5: doc_stem = "00a_CoverPage_Vol2"  ← WRONG for Family B
Step 6: Split("-") → ["00a_CoverPage_Vol2"] = 1 segment, min=5
  → D5-PARSE-004: Expected >=5 segments, got 1
  → All 5 segments: position ≥ len(parts) → apply default_value
  → project_number = "131101", area = "UNKNOWN", document_type = "UNKNOWN",
    discipline = "UNKNOWN", sequence_number = "0000"
Step 7: document_number = "00a_CoverPage_Vol2" (from fallback)
Step 8: parse_status = "partial"

Known issue: The "*" pattern would handle this better (no segment expectations,
dash_revision_max_len=3 gives "C4B" as revision). Family B files are NOT a
good fit for the 131101 pattern. Mitigation: detect project_code mismatch
and fall back to "*" pattern when filename doesn't match expected format.
```

#### Example 5: Hypothetical Revision File (Default "*" Pattern)

```
Input:  DOC-001_revA.pdf
Pattern: "*"

Step 2: stem = "DOC-001_revA"
Step 3: No suffixes to strip
Step 4a: _rev split → left="DOC-001", right="A" → revision extracted
Step 5: doc_stem = "DOC-001"
Step 6: No segments defined → skip
Step 7: document_number = "DOC-001", revision = "A"
Step 8: parse_status = "ok"

Result:
  FilenameParseResult(
      document_number="DOC-001",
      revision="A",
      project_number=None,
      area=None,
      document_type=None,
      discipline=None,
      sequence_number=None,
      parse_status="ok",
      parse_errors=[]
  )
```

#### Example 6: Hypothetical Dash Revision (Default "*" Pattern)

```
Input:  DOC-001-A.pdf
Pattern: "*"

Step 2: stem = "DOC-001-A"
Step 3: No suffixes
Step 4b: dash_revision_max_len=3; rsplit("-",1) → "A"=1 ≤ 3 → revision="A"
Step 5: doc_stem = "DOC-001"
Step 7: document_number = "DOC-001", revision = "A"
Step 8: parse_status = "ok"

Result:
  FilenameParseResult(
      document_number="DOC-001",
      revision="A",
      ...
      parse_status="ok"
  )
```

---

## I6. Shared Parser Module

### I6.1 Location

New file: `eks/engine/core/filename_parser.py`

```
eks/engine/core/
├── filename_parser.py      # NEW: FilenameParser class + FilenameParseResult + parse_filename()
├── file_scanner.py          # UPDATED: holds FilenameParser instance, delegates .parse()
├── pipeline_orchestrator.py # UPDATED: holds FilenameParser instance, replaces 2 inline one-liners
└── ...
```

### I6.2 Module Structure

The module exports three public symbols:

| Symbol | Type | Purpose |
|--------|------|---------|
| `FilenameParseResult` | `@dataclass` | Immutable 9-field parse result with `.to_metadata_dict()` |
| `FilenameParser` | `class` | Stateful parser: caches compiled regex, resolved pattern. Instantiate once, call `.parse()` per file. |
| `parse_filename` | `function` | One-shot convenience wrapper. Instantiates `FilenameParser` internally. |

### I6.3 Export

Add to `eks/engine/core/__init__.py`:

```python
from .filename_parser import FilenameParser, FilenameParseResult, parse_filename
```

---

## I7. Null-Tolerant Registration (I134)

### I7.1 Three-Layer Relaxation

| Layer | Current | Required Change |
|-------|---------|-----------------|
| **L1 — Parser** | Fallback returns `{"document_number": stem, "revision": "00"}` — never null | `FilenameParseResult` allows `None` on all fields. `fallback_revision: null` in 131101 pattern. Segment `null_handling.default_value` fills per-segment gaps. |
| **L2 — Application** | `register_placeholders()` L190: `if not doc_number: continue` — skips file | Log warning; still register. Use `result.document_number`; if still None, generate synthetic key. |
| **L2 — Application** | `phase1_server.py` L396–399: identical skip | Same as above |
| **L3 — Store** | `register_document()` L257: `raise KeyError("document_number is required")` | Accept null; generate a stable synthetic key from `file_path` hash. |

### I7.2 L1 — Parser Change

Handled by `FilenameParseResult` — all fields are `Optional[str]`. Segment-level `null_handling.default_value` fills gaps before they reach the registry. If a segment is missing and has no `null_handling`, the field remains `None` and the registry's schema default applies.

### I7.3 L2 — Application Change (`register_placeholders`)

```python
# BEFORE (current):
doc_number = metadata.get("document_number")
if not doc_number:
    self.logger.warning(...)
    continue  # ← DROPS the file

# AFTER (proposed):
doc_number = metadata.get("document_number")
if not doc_number:
    # Generate a stable synthetic document_number from file_path
    import hashlib
    file_path = metadata.get("file_path", "")
    doc_number = f"UNRESOLVED-{hashlib.md5(file_path.encode()).hexdigest()[:8]}"
    metadata["document_number"] = doc_number
    self.logger.warning(
        f"Generated synthetic document_number for unresolvable filename: "
        f"{file_path} → {doc_number}",
        context="FileScanner.register_placeholders"
    )
# Always register — file is never silently dropped.
```

### I7.4 L3 — Store Change (`register_document`)

```python
# BEFORE (current):
if not document_number:
    raise KeyError("document_number is required")

# AFTER (proposed):
if not document_number:
    # Generate a stable synthetic document_number from file_path
    import hashlib
    file_path = metadata.get("file_path", "")
    document_number = f"UNRESOLVED-{hashlib.md5(file_path.encode()).hexdigest()[:8]}"
    metadata["document_number"] = document_number
    logger.warning(
        f"Generated synthetic document_number for unresolved filename: "
        f"{file_path} → {document_number}"
    )
```

### I7.5 Rationale

The user requirement is: files should always be registered even if parsing fails. The synthetic key:
- Derives from `file_path` so it is stable across runs (same file → same key)
- Is clearly prefixed (`UNRESOLVED-`) for downstream filtering
- Prevents silent data loss (no file silently dropped)

---

## I8. Call-Site Migration (I133 + I135)

### I8.1 Migration Map

| # | File | Current | Change |
|---|------|---------|--------|
| 1 | `file_scanner.py` | `parsed = self._parse_filename(file_name)` | `self._parser = FilenameParser(doc_config.get("filename_patterns"), project_code, doc_config.get("document_type_registry")); result = self._parser.parse(file_name); metadata = result.to_metadata_dict()` |
| 2 | `pipeline_orchestrator.py:567` | `doc_number = Path(file_path).stem.split("_rev")[0].rsplit("-", 1)[0]` | `result = self._parser.parse(Path(file_path).name); doc_number = result.document_number` |
| 3 | `pipeline_orchestrator.py:645` | Identical inline to L567 | Same as #2 |
| 4 | `phase1_server.py` | Uses `scanner._parse_filename()` indirectly | Already flows through #1 — verify |

### I8.2 Removal of Old Code

- **Delete** `FileScanner._parse_filename()` method (L145–174) — replaced by `FilenameParser` instance
- **Remove** 2 inline one-liners in `pipeline_orchestrator.py` (L567, L645)
- **Keep** `FileScanner.build_placeholder_metadata()` — update its internal call to use `self._parser.parse()`

### I8.3 Instance Lifecycle

```python
# FileScanner.__init__:
self._parser = FilenameParser(
    filename_patterns=self.doc_config.get("filename_patterns"),
    project_code=None,  # resolved during scan
    document_type_registry=self.doc_config.get("document_type_registry"),
)

# PipelineOrchestrator.__init__:
self._parser = FilenameParser(
    filename_patterns=self.doc_config.get("filename_patterns"),
    project_code=None,  # resolved during bootstrap
    document_type_registry=self.doc_config.get("document_type_registry"),
)
```

### I8.4 test/t132 Update

Update `eks/test/test_t132_modules.py` to test the `FilenameParser` class directly, covering:

- **TWRP 131101 pattern**: clean, addendum, two-stage, HAC suffixes — verify all 7 fields
- **Default `"*"` pattern**: `_rev` split, dash-suffix ≤3, dash-suffix >3 fallback
- **Segment validation**: valid segments, invalid regex, invalid schema_reference
- **Null handling**: `fallback_revision: null` vs `"00"`, segment `default_value` strategy
- **Missing config**: fallback to `_HARDCODED_DEFAULT`
- **parse_status**: `"ok"`, `"partial"`, `"unresolvable"` for each family
- **to_metadata_dict()**: verify output format matches `register_document()` expectations
- **Class reuse**: instantiate once, call `.parse()` 10 times — verify cached validators work

---

## I9. Error Code Taxonomy — Appendix D Alignment

### I9.1 D5-PARSE-* Codes

From Appendix D §D2, D5 = Phase 5 data errors. Format: `D{phase}-{module}-{sequential_id}`.

| Code | Name | Severity | Trigger | Pipeline Impact |
|:---|:---|:---|:---|:---|
| `D5-PARSE-001` | File type not supported | WARNING | Extension not in `file_type_registry` (B3.3) | Skip file |
| `D5-PARSE-002` | File not found / unreadable | HIGH | OSError on file access | Skip file |
| `D5-PARSE-003` | Document not registered | WARNING | Phase B lookup miss (divergent doc_number from Phase A) | Partial result |
| `D5-PARSE-004` | Too few filename segments | WARNING | `len(segments) < min_segments` | Partial; apply `null_handling` defaults |
| `D5-PARSE-005` | Too many filename segments | WARNING | `len(segments) > max_segments` | Partial; process first N segments |
| `D5-PARSE-006` | Segment validation failed | WARNING | Per-segment pattern/schema_ref mismatch | Partial; apply `null_handling` default for that segment |
| `D5-PARSE-007` | Unresolvable filename | WARNING | No pattern matches, fallback exhausted, no segments extracted | Register with synthetic key |

**Existing codes**: 001–002 already in use in `pipeline_orchestrator.py`. 003 is the orphan per I137. 004–007 are new.

### I9.2 Registration in eks_error_config.json

Each code must be registered in `eks_error_config.json` under `data_logic_errors`:

```json
{
    "code": "D5-PARSE-004",
    "name": "Too few filename segments",
    "severity": "WARNING",
    "description": "Filename segment count is below the minimum defined in filename_patterns[project].segments. Missing segments will use null_handling defaults.",
    "module": "filename_parser",
    "pipeline_phase": "P0",
    "dcc_parallel": "DCC: code G (malformed filename)"
}
```

(Repeat for 005–007 with appropriate descriptions.)

### I9.3 DCC Parallel Mapping

| EKS Code | DCC Equivalent | DCC Description |
|:---------|:---------------|:----------------|
| `D5-PARSE-004` | Code G | File name format mismatch — too few components |
| `D5-PARSE-005` | Code G | File name format mismatch — too many components |
| `D5-PARSE-006` | Codes E/F/H | Component validation failed — invalid segment value |
| `D5-PARSE-007` | Code D | Unrecognized naming convention — no pattern matched |

---

## I10. Cross-Appendix Alignment

| Concept | Appendix B (Registry) | Appendix D (Errors) | Appendix I (Parser) | DCC (Reference) |
|:---|:---|:---|:---|:---|
| `document_type` | B3.1: ontology trigger, B3.2: type registry | D7.1: T1 scorable, P3-E-E-0004 | Extracted from filename segment 2 | DCC: `Document_Type` source column |
| `discipline` | B3 column list, D7.1 T1 scorable | P3-E-E-0004 | Extracted from filename segment 3 | DCC: `Discipline` source column |
| `project_number` | B3 column list, D7.1 T1 scorable | — | Extracted from filename segment 0 | DCC: `Project_Code` source column |
| `area` | B3 column list, D7.1 T2 scorable | — | Extracted from filename segment 1 | DCC: `Facility_Code` source column |
| `document_number` | B3.1: SUPERSEDES chains, D7.1 T1 scorable | D7.1 T1 scorable, D5-PARSE-003 | Rejoined from all segments | DCC: composite format string |
| `revision` | B3: PK component `{doc_num}-{rev}`, D7.1 T1 scorable | D7.1 T1 scorable | Suffix detection (_rev, dash-suffix) | DCC: not in composite |
| `file_type` | B3.3: file type → parser registry | D5-PARSE-001 | Extension-based (pre-existing) | DCC: implicit from file |
| Segment bounds | B3 column definitions | D5-PARSE-004, D5-PARSE-005 | `min_segments`, `max_segments` | DCC: Code G |
| Segment validation | B3.2: document_type_registry | D5-PARSE-006 | `validation.type: "pattern"` or `"schema_reference"` | DCC: Codes E/F/H |
| Unresolvable files | B6.2: registration fallback | D5-PARSE-007 | `parse_status: "unresolvable"`, synthetic key | DCC: Code D |

---

## I11. Per-Project Configuration

### I11.1 Config Loading

`filename_patterns` is loaded from `eks_doc_config.json` at bootstrap time alongside other config blocks. Both `FileScanner` and `PipelineOrchestrator` instantiate a `FilenameParser` once with the config block and hold the reference for the pipeline duration.

### I11.2 project_code Resolution

Currently, `project_code` is not automatically inferred from the data folder structure. The proposed flow:

```
Phase A (scan):
  - data_path = /path/to/eks/data/twrp/...
  - project_code = extract_project_code(data_path)  # future: folder→code mapping
  - parser = FilenameParser(filename_patterns, project_code="131101")
  - parser.parse(file_name)  # for each file

If project_code is None:
  - parser = FilenameParser(filename_patterns, project_code=None)
  - Falls back to "*" pattern
```

### I11.3 Adding a New Project

To add a project with a different naming convention:

1. Add a new entry to `filename_patterns` in `eks_doc_config.json`:

```json
"filename_patterns": {
    "131101": { ... },
    "999999": {
        "description": "Example: project X naming convention — {proj}-{area}-{type}-{disc}-{seq}",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 5,
        "max_segments": 5,
        "segments": [
            { "position": 0, "maps_to": "project_number", "label": "project_code",
              "required": true, "null_handling": {"strategy": "default_value", "default_value": "999999"},
              "validation": {"type": "pattern", "pattern": "^\\d{6}$"} },
            { "position": 1, "maps_to": "area", "label": "area_code",
              "required": true, "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
              "validation": {"type": "pattern", "pattern": "^[A-Z0-9]{3,6}$"} },
            { "position": 2, "maps_to": "document_type", "label": "type_code",
              "required": true, "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
              "validation": {"type": "schema_reference", "reference": "document_type_registry"} },
            { "position": 3, "maps_to": "discipline", "label": "discipline_code",
              "required": true, "null_handling": {"strategy": "default_value", "default_value": "UNKNOWN"},
              "validation": {"type": "pattern", "pattern": "^[A-Z]{2}$"} },
            { "position": 4, "maps_to": null, "label": "sequence_number",
              "required": true, "null_handling": {"strategy": "default_value", "default_value": "0000"},
              "validation": {"type": "pattern", "pattern": "^\\d{4}$"} }
        ],
        "rejoin_separator": "-",
        "strip_suffixes": ["_draft", "_final"],
        "revision_separators": ["_r", "_rev"],
        "dash_revision_max_len": 2,
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": null,
            "preservation_mode": "overwrite_existing"
        },
        "error_subcodes": {
            "too_few_segments": "D5-PARSE-004",
            "too_many_segments": "D5-PARSE-005",
            "segment_validation_failed": "D5-PARSE-006",
            "unresolvable": "D5-PARSE-007"
        },
        "processing_phase": "P0"
    },
    "*": { ... }
}
```

2. Add corresponding `revision_validation` entry if the project validates revisions:

```json
"revision_validation": {
    "131101": { "pattern": "^[A-Z0-9]{1,2}$" },
    "999999": { "pattern": "^[A-Z]{1}$" }
}
```

3. No code changes needed — the parser uses the pattern from config.

### I11.4 Future: project_folder → project_code Mapping

A dedicated mapping (beyond Appendix I scope) will associate data folders with project codes:

```json
"project_folder_map": {
    "twrp": "131101",
    "project_x": "999999"
}
```

This enables auto-selection of the correct `filename_patterns` entry during Phase A scan.

---

## I12. Implementation Plan

### I12.1 Task Breakdown

| Task | Description | Files | Depends On |
|------|-------------|-------|------------|
| **T-I.1** | Add `filename_patterns` to `eks_doc_config.json` (131101 + `"*"` entries with segment definitions) | `eks_doc_config.json` | — |
| **T-I.2** | Add schema validation for `filename_patterns` (3-tier: base, setup, config with segment definitions) | `eks_doc_base_schema.json`, `eks_doc_setup_schema.json` | T-I.1 |
| **T-I.3** | Create `filename_parser.py` with `FilenameParser` class + `FilenameParseResult` dataclass + `parse_filename()` convenience function | `filename_parser.py` (new), `__init__.py` | — |
| **T-I.4** | Migrate `FileScanner` to hold `FilenameParser` instance; delete `_parse_filename()`; update `build_placeholder_metadata()` | `file_scanner.py` | T-I.3 |
| **T-I.5** | Replace 2 inline one-liners in `PipelineOrchestrator` with `self._parser.parse()` | `pipeline_orchestrator.py` | T-I.3 |
| **T-I.6** | Relax null-registration at 3 layers (parser already done via `FilenameParseResult`; app + store) | `file_scanner.py`, `registry.py`, `phase1_server.py` | T-I.1 (for null fallback) |
| **T-I.7** | Register `D5-PARSE-001` through `D5-PARSE-007` in error catalog | `eks_error_config.json`, `eks_error_base.json` | — |
| **T-I.8** | Update/add tests for `FilenameParser` class: segment extraction, validation, null-handling, parse_status, class reuse | `test_t132_modules.py` | T-I.3–T-I.6 |
| **T-I.9** | Pipeline verification run (171 files, TWRP) | — | T-I.1–T-I.8 |
| **T-I.10** | Update `update_log.md`, close I133–I137, update Appendix B §B6.2 (Phase A now populates 5 fields) | `update_log.md`, `issue_log.md`, `appendix_b_document_registry.md` | T-I.9 |

### I12.2 Success Criteria

1. `FilenameParser.parse()` produces identical `document_number` and `revision` whether called from Phase A or Phase B
2. All 171 TWRP files register successfully — no file silently dropped
3. `131101-WSW41-SP-SP-0801_Add3.pdf` → `document_number = "131101-WSW41-SP-SP-0801"`, `revision = null`, all 4 segment fields populated
4. `_AddN`, `_2-Stage`, `_HAC` suffixes stripped correctly
5. Segment fields (`project_number`, `area`, `document_type`, `discipline`, `sequence_number`) populated for Family A files, `null`/default for Family B/C
6. `parse_status` correctly reflects extraction quality: `"ok"` (Family A clean), `"partial"` (Family A with validation failures), `"unresolvable"` (Family B/C)
7. Default `"*"` pattern backward-compatible with existing `_rev` + dash-suffix behavior
8. `D5-PARSE-001` through `D5-PARSE-007` present in `eks_error_config.json`
9. Single shared `FilenameParser` instance used at all 4 call sites
10. Pipeline: 19/19 Phase A, 19/19 Phase B (no D5-PARSE-003 false positives)

### I12.3 Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Other projects have dash-suffix ≤3 chars that are NOT revisions | Medium | Per-project `dash_revision_max_len` can be set to 0; `"*"` default conservatively set to 3 for backward compat |
| Synthetic `UNRESOLVED-` keys collide | Low | 8-char MD5 hash over file_path is collision-resistant for a single project |
| `project_code` not available during Phase A scan | High | Default to `"*"` pattern; log warning; register with fallback pattern |
| Schema validation rejects null `fallback_revision` | Low | Use `oneOf: [string, null]` in JSON Schema |
| Family B/C files matched against Family A segment definitions → false D5-PARSE-004 | Medium | `parse_status` degrades to `"partial"`/`"unresolvable"` gracefully; no data loss. Future: per-family pattern detection |
| `document_type_registry` not loaded when `FilenameParser` is instantiated | Medium | `schema_reference` validation degrades gracefully (returns True when registry unavailable) |
| Segment count mismatch with legacy projects | Low | Default `"*"` pattern has `segments: []` — no segment extraction, backward compatible |

---

## I13. References

- [Appendix B — Document Registry](appendix_b_document_registry.md) — registry columns (B3), SUPERSEDES chains (B3.1), document_type_registry (B3.2), file_type_registry (B3.3), health scoring tiers (D7.1)
- [Appendix D — Pipeline Messages & Errors](appendix_d_pipeline_messages_errors.md) — D5-PARSE-* error code taxonomy (D2), health scoring (D7.1)
- [Appendix F — Pipeline Architecture](appendix_f_pipeline_architecture_design.md) — Phase A/B orchestration flow
- [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) §20 — Document Registry & Revision Management
- [issue_log.md](../log/issue_log.md) — I133 (divergent extraction), I134 (null-registration), I135 (shared parser), I136 (per-project patterns), I137 (orphan D5-PARSE-003)
