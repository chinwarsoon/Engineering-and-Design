# Appendix J — Schema-Driven File Property Parser (Universal Class)

**Document ID**: WP-EKS-P1-APX-J  
**Version**: 0.3  
**Last Updated**: 2026-07-20  
**Phase**: 1 — Foundation  
**Status**: ✅ Implemented — See [J14 Implementation Record](#j14-implementation-record--complete) below  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) §20 (Document Registry & Revision Management)  
**Related Appendices**:
- [Appendix B — Document Registry](appendix_b_document_registry.md) — registry columns (B3), ontology triggers (B3.1), file_type_registry (B3.3)
- [Appendix D — Pipeline Messages & Errors](appendix_d_pipeline_messages_errors.md) — D5-PROP-* error codes, D7.1 health scoring
- [Appendix F — Pipeline Architecture](appendix_f_pipeline_architecture_design.md) — Phase B orchestration flow
- [Appendix I — Filename Parser](appendix_i_filename_parser.md) — schema-driven parser design pattern, FilenameParseResult dataclass, boundary definition

**Related Files**:
- [`eks/engine/parsers/pdf_parser.py`](../engine/parsers/pdf_parser.py) — `extract_metadata()` returns 8 fields (L32–47)
- [`eks/engine/parsers/docx_parser.py`](../engine/parsers/docx_parser.py) — `extract_metadata()` returns 6 fields (L53–63)
- [`eks/engine/parsers/xlsx_parser.py`](../engine/parsers/xlsx_parser.py) — `extract_metadata()` returns 6 fields (L39–52)
- [`eks/engine/parsers/dgn_parser.py`](../engine/parsers/dgn_parser.py) — `extract_metadata()` stub (L21–27)
- [`eks/engine/parsers/dwg_parser.py`](../engine/parsers/dwg_parser.py) — `extract_metadata()` stub (L21–27)
- [`eks/engine/core/pipeline_orchestrator.py`](../engine/core/pipeline_orchestrator.py) — Phase B: captures metadata at L552, assigns to `pout.metadata` at L575, but **never writes to registry**
- [`eks/engine/core/file_scanner.py`](../engine/core/file_scanner.py) — Phase A: `build_placeholder_metadata()` (L123–143), only 2 filename fields
- [`eks/engine/core/registry.py`](../engine/core/registry.py) — `register_document()`, `update_document_status()`
- [`eks/engine/parsers/io_contracts.py`](../engine/parsers/io_contracts.py) — `ParserOutput.metadata` field defined but unused downstream
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — `document_metadata_def` (L45–83), `file_type_code` (L19–23)
- [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — `file_type_registry` (L92–108)
- [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — `file_type_registry` values (L50–56)

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.3 | 2026-07-20 | CodeBuddy | Added J14 Implementation Record (relocated from main workplan §43): 14 closed issues, 13 new registry columns, 2-layer extraction pipeline integration, cross-references. Updated status to ✅ Implemented. |
| 0.2 | 2026-07-18 | CodeBuddy | Added §J1.1 boundary definition: explicit separation from FilenameParser (Appendix I), system-values breakdown table (3 categories), why OS+embedded stay together, why filename is separate |
| 0.1 | 2026-07-18 | CodeBuddy | Initial draft: J1–J14 covering OS-level + embedded property extraction, schema-driven `file_property_patterns` config, `FilePropertyExtractor` class, 5 file-type capability matrix, registry column alignment, pipeline integration, error taxonomy, and implementation plan |

---

## J1. Overview

The file property parser extracts structured metadata about each source file beyond its filename. Two layers of properties exist:

**Layer 1 — OS-level properties** (available for all 5 file types via `pathlib.Path.stat()`):
- `file_size` — bytes, critical for upload validation and data quality checks
- `fs_created` — file-system creation timestamp
- `fs_modified` — file-system last-modified timestamp (**most useful for tampering detection**)
- `fs_accessed` — file-system last-accessed timestamp
- `file_mode` — permission bits
- `file_hash` — content hash (MD5/SHA256) for integrity verification and deduplication

**Layer 2 — Format-specific embedded properties** (available per parser via `extract_metadata()`):

| Property | PDF | DOCX | XLSX | DGN | DWG | Maps to Registry |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `author` | ✅ | ✅ | ✅ | ❌ | ❌ | `created_by` (existing) |
| `title` | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_title` (new) |
| `subject` | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_subject` (new) |
| `creator_app` | ✅ | — | — | ❌ | ❌ | `embedded_creator_app` (new) |
| `producer_lib` | ✅ | — | — | ❌ | ❌ | `embedded_producer` (new) |
| `embedded_created` | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_created_date` (new) |
| `embedded_modified` | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_modified_date` (new) |
| `page_count` | ✅ | — | — | ❌ | ❌ | `page_count` (existing) |
| `sheet_count` | — | — | ✅ | ❌ | ❌ | `embedded_sheet_count` (new) |
| `last_modified_by` | — | ✅ | ✅ | ❌ | ❌ | `embedded_last_modified_by` (new) |
| `revision_number` | — | ✅ | — | ❌ | ❌ | *(not mapped — conflicts with doc revision)* |

✅ = library supports extraction  
❌ = stub (no metadata until Phase 3)  
— = not applicable to format

### Current Gap

All 5 parsers implement `extract_metadata()`, and the pipeline captures the result at `pipeline_orchestrator.py:552` into `pout.metadata`. However, this data is **never written to the registry**. Only `extract_status`, `extraction_confidence`, and `extraction_notes` are persisted via `update_document_status()`.

Furthermore, no code anywhere in EKS calls `os.stat()` or `Path.stat()`. OS-level file properties are completely absent.

The registry has `created_by` and `page_count` columns (B3 table) that remain null because the parser metadata is discarded.

### Design Principles

| Principle | Description |
|:---|:---|
| **Schema-driven** | All property extraction rules, field mappings, and OS-property collector configuration defined in `eks_doc_config.json` under `file_property_patterns`; no hardcoded field lists in Python |
| **Universal class** | Single `FilePropertyExtractor` class; instantiated once per pipeline run, reused across all files |
| **Two-layer** | OS-level properties always collected first (free, no library dependencies); format-specific properties collected only when parser provides them |
| **Fail-safe** | Missing/invalid properties → `None`, never raise; OS-level extraction failure logs warning but does not block registration |
| **Null-tolerant** | All extracted fields are `Optional`; registry accepts nulls per existing schema defaults |
| **Dual-date collection** | Both OS `st_mtime` and embedded `modified` dates collected for forensic value (they can differ, which is significant) |
| **Backward compatible** | Existing registry columns (`created_by`, `page_count`) populated from parser metadata via schema mapping; no breaking changes to existing API |

### J1.1 Boundary: What the File Property Extractor Does and Does NOT Handle

The file property extractor handles **all properties that require the file to actually exist on disk** — either through OS system calls (`Path.stat()`) or by reading and parsing the file content (embedded metadata via parser libraries).

It does **not** handle filename-derived values. Those are extracted by `FilenameParser` (Appendix I) using pure string operations on `Path.stem`, without any disk I/O.

The full set of "system-related" values that describe a file come from **3 distinct sources** with **3 distinct failure modes**:

| Category | Source | Field Count | I/O Type | Pipeline Stage | Failure Domain | Handled By |
|:---|:---|:---:|:---|:---|:---|:---|
| **A. Filename-derived** | String parsing (`Path.stem`) | 7 | None — pure string operation | P0 (scan) | D5-PARSE-001..007 | **`FilenameParser`** (Appendix I) |
| **B. OS-level** | `Path.stat()` / `hashlib` | 6 | Disk I/O, system calls | P0 / Phase B | D5-PROP-001, 002, 005 | **`FilePropertyExtractor`** (this appendix, Layer 1) |
| **C. Embedded metadata** | Parser `extract_metadata()` | 11+ | File open, parsing libraries | Phase B | D5-PROP-003, 004 | **`FilePropertyExtractor`** (this appendix, Layer 2) |

#### Why Categories B and C Are Together in This Class

Both Layer 1 (OS) and Layer 2 (embedded) share the same fundamental requirement: **the file must exist and be accessible on disk**. This is the clean dividing line from `FilenameParser`, which only needs a string.

| Shared trait | Rationale for keeping B + C together |
|:---|:---|
| Same precondition | Both require a real file path; both fail with `D5-PROP-001` if the file doesn't exist |
| Same error domain | `D5-PROP-*` covers both OS failures and embedded metadata gaps |
| Same pipeline stage | Both are extracted during Phase B (OS props can optionally be collected in Phase A, but the canonical extraction happens post-parse) |
| Same config block | `file_property_patterns` defines both `os_properties` and `by_file_type` in a single config hierarchy |
| Single entry point | Caller only needs one `self._prop_extractor.extract(file_path, file_type, parser_metadata)` call to get all 17+ fields |

#### Why Category A Is Separate (and Must Stay Separate)

See Appendix I §I1.1 for the full rationale. In summary:

1. **Different input type** — `str` vs. real file path
2. **Different pipeline timing** — Phase A vs. Phase B
3. **Different error domains** — D5-PARSE-* vs. D5-PROP-*
4. **Different dependencies** — pure stdlib vs. I/O + parser libraries

#### Integration Point

The orchestrator calls both and merges the results. See Appendix I §I1.1 for the full integration pseudocode. The single point of assembly is `PipelineOrchestrator._process_file()`.

### Design Decision: Class vs. Module-Level Function

| Factor | Module-Level Function | Universal Class | Decision |
|:---|:---|:---|:---|
| **Internal state** | Stateless | Caches resolved config, per-file-type mappings, compiled validators | **Class** — avoids repeated config resolution per file |
| **Return complexity** | Flat dict | `FilePropertyResult` dataclass with typed fields + `.to_registry_dict()` | **Class** — type safety, convenience method for registry write |
| **Two-phase extraction** | Two calls needed | `.extract(file_path, file_type, parser=None)` does OS first, then optional format-specific | **Class** — single call point, no scattered logic |
| **Testability** | Parameterized function | Construct once, call `.extract()` per file | **Class** — natural for batch processing |
| **Extensibility** | Add parameters → break signature | New parser metadata keys → add config entry only; new OS property → add to `os_properties.collect` | **Class** — config-driven, no code changes |

**Conclusion**: `FilePropertyExtractor` is implemented as a **universal class** in `eks/engine/core/file_property_parser.py`. A module-level convenience function `extract_file_properties()` is provided for one-shot usage.

---

## J2. Schema Design — Three-Tier Inheritance

### J2.1 Base Schema Changes (`eks_doc_base_schema.json`)

**Add to `definitions`** (sibling to `filename_pattern_def` added in Appendix I):

```json
"file_property_source_def": {
    "type": "object",
    "description": "Definition of a single file property source (OS or parser metadata). Maps source key to registry column. (Appendix J v0.1)",
    "properties": {
        "source_key": {
            "type": "string",
            "description": "Key in the source data dict. For OS: 'file_size', 'fs_created', etc. For parser: 'author', 'title', etc."
        },
        "maps_to": {
            "type": "string",
            "description": "Target registry column name per Appendix B §B3 and new columns defined in this appendix §J3."
        },
        "required": { "type": "boolean", "default": false },
        "null_handling": {
            "type": "object",
            "properties": {
                "strategy": { "type": "string", "enum": ["skip", "default_value"] },
                "default_value": {}
            },
            "required": ["strategy"],
            "additionalProperties": false
        }
    },
    "required": ["source_key", "maps_to"],
    "additionalProperties": false
},

"file_property_pattern_def": {
    "type": "object",
    "description": "Per-file-type property extraction rules (Appendix J v0.1)",
    "properties": {
        "enabled": { "type": "boolean", "default": true },
        "extraction_method": {
            "type": "string",
            "enum": ["parser_metadata", "os_only"],
            "description": "'parser_metadata': parse file then extract metadata; 'os_only': OS-level properties only (for stubs DGN/DWG)"
        },
        "property_mapping": {
            "type": "array",
            "items": { "$ref": "#/definitions/file_property_source_def" },
            "description": "Ordered list of property mappings for this file type."
        }
    },
    "required": ["enabled", "extraction_method", "property_mapping"],
    "additionalProperties": false
},

"file_property_os_def": {
    "type": "object",
    "description": "OS-level property collection configuration (Appendix J v0.1)",
    "properties": {
        "enabled": { "type": "boolean", "default": true },
        "collect": {
            "type": "array",
            "items": { "type": "string", "enum": ["file_size", "fs_created", "fs_modified", "fs_accessed", "file_mode", "file_hash"] },
            "description": "Which OS-level properties to collect for every file."
        },
        "hash_algorithm": { "type": "string", "enum": ["md5", "sha256"], "default": "md5" },
        "source_date_preference": { "type": "string", "enum": ["mtime", "ctime"], "default": "mtime" }
    },
    "required": ["enabled", "collect", "hash_algorithm"],
    "additionalProperties": false
}
```

**Add new properties to `document_metadata_def`** (after existing fields, before `additionalProperties: false`):

```json
"file_size": { "type": "integer", "minimum": 0, "description": "File size in bytes (OS-level, Appendix J)" },
"file_created_at": { "type": "string", "format": "date-time", "description": "File-system creation timestamp (OS-level, Appendix J)" },
"file_modified_at": { "type": "string", "format": "date-time", "description": "File-system last-modified timestamp (OS-level, Appendix J)" },
"file_hash": { "type": "string", "description": "Content hash for integrity verification (OS-level, Appendix J). Algorithm per file_property_patterns.os_properties.hash_algorithm." },
"embedded_title": { "type": "string", "description": "Document title from embedded metadata (Appendix J)" },
"embedded_subject": { "type": "string", "description": "Document subject from embedded metadata (Appendix J)" },
"embedded_created_date": { "type": "string", "format": "date-time", "description": "Internal creation date from embedded metadata (Appendix J)" },
"embedded_modified_date": { "type": "string", "format": "date-time", "description": "Internal modification date from embedded metadata (Appendix J)" },
"embedded_creator_app": { "type": "string", "description": "Creating application (e.g., 'AutoCAD 2024') from embedded metadata (Appendix J)" },
"embedded_producer": { "type": "string", "description": "PDF producer library (e.g., 'pdfTeX-1.40.25') from embedded metadata (Appendix J)" },
"embedded_last_modified_by": { "type": "string", "description": "Last editor username from embedded metadata (Appendix J)" },
"embedded_keywords": { "type": "string", "description": "Keywords from embedded metadata (Appendix J)" },
"embedded_sheet_count": { "type": "integer", "minimum": 0, "description": "Number of sheets from embedded XLSX metadata (Appendix J)" }
```

And add `file_size`, `file_created_at`, `file_modified_at` to `required`? No — these must remain optional because:
- Stub parsers (DGN/DWG) won't produce OS props if `enabled: false`
- Some OS environments may not have accessible file timestamps

### J2.2 Setup Schema Changes (`eks_doc_setup_schema.json`)

**Add to `properties`** (sibling to `filename_patterns`):

```json
"file_property_patterns": {
    "type": "object",
    "description": "Per-file-type property extraction rules for OS-level and embedded metadata. Keys are file_type_code values from file_type_registry. (Appendix J v0.1)",
    "properties": {
        "description": { "type": "string" },
        "processing_phase": { "type": "string", "enum": ["P0"] },
        "os_properties": { "$ref": "eks_doc_base_schema.json#/definitions/file_property_os_def" },
        "by_file_type": {
            "type": "object",
            "description": "Per-file-type property extraction rules. Keys must match file_type_code enum values.",
            "propertyNames": {
                "pattern": "^(pdf|dgn|docx|xlsx|dwg)$"
            },
            "additionalProperties": {
                "$ref": "eks_doc_base_schema.json#/definitions/file_property_pattern_def"
            },
            "minProperties": 1
        }
    },
    "required": ["description", "processing_phase", "os_properties", "by_file_type"],
    "additionalProperties": false
}
```

### J2.3 Config Block (`eks_doc_config.json`)

**Add top-level key** `"file_property_patterns"` (sibling to `filename_patterns`):

```json
"file_property_patterns": {
    "description": "File property extraction rules for OS-level attributes (all file types) and format-specific embedded metadata (PDF/DOCX/XLSX). Phase P0 — runs during Phase B processing before registry write. Appendix J v0.1.",
    "processing_phase": "P0",
    "os_properties": {
        "enabled": true,
        "collect": ["file_size", "fs_created", "fs_modified", "file_hash"],
        "hash_algorithm": "md5",
        "source_date_preference": "mtime"
    },
    "by_file_type": {
        "pdf": {
            "enabled": true,
            "extraction_method": "parser_metadata",
            "property_mapping": [
                { "source_key": "author",        "maps_to": "created_by",              "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "title",         "maps_to": "embedded_title",          "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "subject",       "maps_to": "embedded_subject",        "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "creator",       "maps_to": "embedded_creator_app",    "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "producer",      "maps_to": "embedded_producer",       "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "creation_date", "maps_to": "embedded_created_date",   "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "mod_date",      "maps_to": "embedded_modified_date",  "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "page_count",    "maps_to": "page_count",              "required": false, "null_handling": { "strategy": "skip" } }
            ]
        },
        "docx": {
            "enabled": true,
            "extraction_method": "parser_metadata",
            "property_mapping": [
                { "source_key": "author",         "maps_to": "created_by",                  "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "title",          "maps_to": "embedded_title",              "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "subject",        "maps_to": "embedded_subject",            "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "created",        "maps_to": "embedded_created_date",       "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "modified",       "maps_to": "embedded_modified_date",      "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "revision",       "maps_to": "embedded_revision_number",    "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "last_modified_by", "maps_to": "embedded_last_modified_by", "required": false, "null_handling": { "strategy": "skip" } }
            ]
        },
        "xlsx": {
            "enabled": true,
            "extraction_method": "parser_metadata",
            "property_mapping": [
                { "source_key": "author",         "maps_to": "created_by",                   "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "title",          "maps_to": "embedded_title",               "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "subject",        "maps_to": "embedded_subject",             "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "created",        "maps_to": "embedded_created_date",        "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "modified",       "maps_to": "embedded_modified_date",       "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "sheet_count",    "maps_to": "embedded_sheet_count",         "required": false, "null_handling": { "strategy": "skip" } },
                { "source_key": "last_modified_by","maps_to": "embedded_last_modified_by",    "required": false, "null_handling": { "strategy": "skip" } }
            ]
        },
        "dgn": {
            "enabled": true,
            "extraction_method": "os_only",
            "property_mapping": []
        },
        "dwg": {
            "enabled": true,
            "extraction_method": "os_only",
            "property_mapping": []
        }
    }
}
```

---

## J3. Registry Column Alignment

### J3.1 Existing Columns Populated by File Property Parser

| Registry Column | Current Source | New Source (Appendix J) | Property Layer |
|:---|:---|:---|:---|
| `created_by` | Never populated | `author` from PDF/DOCX/XLSX embedded metadata | Layer 2 |
| `page_count` | Never populated | `page_count` from PDF embedded metadata | Layer 2 |

### J3.2 New Registry Columns

| Column | Type | Property Layer | Source Key(s) | Description |
|:---|:---|:---|:---|:---|
| `file_size` | INTEGER | Layer 1 (OS) | `stat().st_size` | File size in bytes |
| `file_created_at` | VARCHAR (ISO 8601) | Layer 1 (OS) | `stat().st_ctime` | File-system creation timestamp |
| `file_modified_at` | VARCHAR (ISO 8601) | Layer 1 (OS) | `stat().st_mtime` | File-system last-modified timestamp |
| `file_hash` | VARCHAR | Layer 1 (OS) | MD5 hex digest | Content hash for integrity/dedup |
| `embedded_title` | VARCHAR | Layer 2 (embedded) | `title` (PDF/DOCX/XLSX) | Document title from internal metadata |
| `embedded_subject` | VARCHAR | Layer 2 (embedded) | `subject` (PDF/DOCX/XLSX) | Document subject from internal metadata |
| `embedded_created_date` | VARCHAR (ISO 8601) | Layer 2 (embedded) | `creation_date` (PDF) / `created` (DOCX/XLSX) | Internal creation date |
| `embedded_modified_date` | VARCHAR (ISO 8601) | Layer 2 (embedded) | `mod_date` (PDF) / `modified` (DOCX/XLSX) | Internal last-saved date |
| `embedded_creator_app` | VARCHAR | Layer 2 (embedded) | `creator` (PDF only) | Creating application (e.g., "AutoCAD 2024") |
| `embedded_producer` | VARCHAR | Layer 2 (embedded) | `producer` (PDF only) | PDF producer library (e.g., "pdfTeX-1.40.25") |
| `embedded_last_modified_by` | VARCHAR | Layer 2 (embedded) | `last_modified_by` (DOCX/XLSX) | Last editor username |
| `embedded_keywords` | VARCHAR | Layer 2 (embedded) | `keywords` (PDF/DOCX/XLSX) | Embedded keywords |
| `embedded_sheet_count` | INTEGER | Layer 2 (embedded) | `sheet_count` (XLSX only) | Number of sheets |
| `embedded_revision_number` | VARCHAR | Layer 2 (embedded) | `revision` (DOCX only) | Internal revision number from Word (NOT doc revision) |

### J3.3 Forensic Value: Dual-Date Collection

The pipeline collects **both** OS-level `file_modified_at` (from `stat().st_mtime`) **and** embedded `embedded_modified_date` (from parser metadata). These can differ and the delta is significant:

| Scenario | `file_modified_at` | `embedded_modified_date` | Interpretation |
|:---|:---|:---|:---|
| Fresh save | 2024-03-15 | 2024-03-15 | Normal — file unchanged since save |
| File copied | 2025-01-10 | 2024-03-15 | File was duplicated/relocated later but content unchanged |
| Metadata stripped | 2025-06-01 | null | File reprocessed; internal metadata was removed |
| Back-dated | 2026-01-01 | 2024-12-15 | Suspicious — OS timestamp newer than internal |

Both dates are stored; the health scorer (Appendix D §D7.1) can flag discrepancies in the `consistency` dimension.

---

## J4. Class Design — `FilePropertyExtractor`

### J4.1 Module Location

New file: `eks/engine/core/file_property_parser.py`

```
eks/engine/core/
├── filename_parser.py        # Appendix I — filename parsing
├── file_property_parser.py   # NEW: Appendix J — file property extraction
├── file_scanner.py            # UPDATED: holds FilePropertyExtractor instance
├── pipeline_orchestrator.py  # UPDATED: calls extractor during Phase B
└── ...
```

### J4.2 Return Dataclass — `FilePropertyResult`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import datetime


@dataclass
class FilePropertyResult:
    """
    Immutable result of extracting file properties from a single file.

    Layer 1 (OS-level): always extracted when os_properties.enabled.
    Layer 2 (embedded): extracted only when by_file_type[ext].enabled
                         and extraction_method is 'parser_metadata'.

    All fields are Optional[str|int|float] — null means
    "not extractable from this file/format."
    """
    # ---- Layer 1: OS-level ----
    file_size: Optional[int] = None
    fs_created: Optional[datetime.datetime] = None
    fs_modified: Optional[datetime.datetime] = None
    fs_accessed: Optional[datetime.datetime] = None
    file_mode: Optional[int] = None
    file_hash: Optional[str] = None

    # ---- Layer 2: Embedded metadata (format-specific) ----
    created_by: Optional[str] = None          # maps to registry: created_by
    embedded_title: Optional[str] = None
    embedded_subject: Optional[str] = None
    embedded_created_date: Optional[str] = None
    embedded_modified_date: Optional[str] = None
    embedded_creator_app: Optional[str] = None
    embedded_producer: Optional[str] = None
    embedded_last_modified_by: Optional[str] = None
    embedded_keywords: Optional[str] = None
    page_count: Optional[int] = None          # maps to registry: page_count
    embedded_sheet_count: Optional[int] = None
    embedded_revision_number: Optional[str] = None

    # ---- Diagnostics ----
    extract_status: str = "ok"                # "ok" | "partial" | "failed"
    extract_errors: List[str] = field(default_factory=list)

    def to_registry_dict(self) -> Dict[str, Any]:
        """
        Convert to a flat dict for register_document() / update_document_status().

        Key design: uses the configured 'maps_to' names, not the dataclass field names.
        This ensures schema-to-registry alignment is validated at extract time.

        Excludes None-valued fields so the registry's schema defaults apply.
        Excludes internal diagnostics (extract_status, extract_errors).
        """
        result: Dict[str, Any] = {}

        # Layer 1
        if self.file_size is not None:
            result["file_size"] = self.file_size
        if self.fs_created is not None:
            result["file_created_at"] = self.fs_created.isoformat()
        if self.fs_modified is not None:
            result["file_modified_at"] = self.fs_modified.isoformat()

        if self.file_hash is not None:
            result["file_hash"] = self.file_hash

        # Layer 2
        if self.created_by is not None:
            result["created_by"] = self.created_by
        if self.embedded_title is not None:
            result["embedded_title"] = self.embedded_title
        if self.embedded_subject is not None:
            result["embedded_subject"] = self.embedded_subject
        if self.embedded_created_date is not None:
            result["embedded_created_date"] = self.embedded_created_date
        if self.embedded_modified_date is not None:
            result["embedded_modified_date"] = self.embedded_modified_date
        if self.embedded_creator_app is not None:
            result["embedded_creator_app"] = self.embedded_creator_app
        if self.embedded_producer is not None:
            result["embedded_producer"] = self.embedded_producer
        if self.embedded_last_modified_by is not None:
            result["embedded_last_modified_by"] = self.embedded_last_modified_by
        if self.embedded_keywords is not None:
            result["embedded_keywords"] = self.embedded_keywords
        if self.page_count is not None:
            result["page_count"] = self.page_count
        if self.embedded_sheet_count is not None:
            result["embedded_sheet_count"] = self.embedded_sheet_count
        if self.embedded_revision_number is not None:
            result["embedded_revision_number"] = self.embedded_revision_number

        return result
```

### J4.3 Main Class — `FilePropertyExtractor`

```python
import hashlib
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class FilePropertyExtractor:
    """
    Schema-driven file property extractor — universal class shared by all EKS call sites.

    Design:
      - Instantiated once per pipeline run with the 'file_property_patterns' config block.
      - .extract(file_path, file_type, parser_metadata=None) → FilePropertyResult (never raises).
      - Layer 1 (OS properties): always collected if os_properties.enabled.
      - Layer 2 (embedded metadata): collected per file_type if enabled and extraction_method
        is 'parser_metadata', using the property_mapping from config.
      - Call sites: PipelineOrchestrator (Phase B), FileScanner (Phase A optional).

    Revision: 0.1
    Date: 2026-07-18
    Author: CodeBuddy
    Summary: Schema-driven two-layer property extraction, FilePropertyResult dataclass,
             OS-level always-on, format-specific parser-driven via config mapping.
    """

    def __init__(
        self,
        file_property_patterns: Optional[Dict[str, Any]] = None,
        logger: Optional[Any] = None,
    ):
        """
        Args:
            file_property_patterns: The 'file_property_patterns' block from eks_doc_config.json.
                                    If None, extractor is effectively disabled (returns empty result).
            logger: Optional logger instance for diagnostics.
        """
        self._config = file_property_patterns or {}
        self._logger = logger
        self._os_config = self._config.get("os_properties", {})
        self._by_type = self._config.get("by_file_type", {})
        self._os_enabled = self._os_config.get("enabled", True)
        self._os_collect = set(self._os_config.get("collect", []))
        self._hash_algorithm = self._os_config.get("hash_algorithm", "md5")

    # ---- Main Entry Point ----

    def extract(
        self,
        file_path: str,
        file_type: str,
        parser_metadata: Optional[Dict[str, Any]] = None,
    ) -> FilePropertyResult:
        """
        Extract all available file properties for a single file.

        Args:
            file_path: Absolute or relative path to the file on disk.
            file_type: File extension code (pdf, docx, xlsx, dgn, dwg).
            parser_metadata: Optional dict from parser.extract_metadata().
                             Must be provided to extract Layer 2 properties.

        Returns:
            FilePropertyResult with all extractable fields populated.
            Never raises — errors are captured in extract_errors.
        """
        result = FilePropertyResult()

        # Layer 1: OS-level properties (always attempted)
        self._extract_os_properties(file_path, result)

        # Layer 2: Format-specific embedded properties
        self._extract_embedded_properties(file_type, parser_metadata, result)

        # Finalize status
        if not result.extract_errors:
            result.extract_status = "ok"
        elif result.file_size is not None:
            # At least OS-level extraction succeeded
            result.extract_status = "partial"
        else:
            result.extract_status = "failed"

        return result

    # ---- Layer 1: OS-Level ----

    def _extract_os_properties(self, file_path: str, result: FilePropertyResult) -> None:
        """Collect OS-level properties per os_properties.collect config."""
        if not self._os_enabled:
            return

        path = Path(file_path)
        if not path.exists():
            result.extract_errors.append(f"D5-PROP-001: File not found at '{file_path}'")
            result.extract_status = "failed"
            return

        try:
            stat = path.stat()

            if "file_size" in self._os_collect:
                result.file_size = stat.st_size
            if "fs_created" in self._os_collect:
                result.fs_created = datetime.datetime.fromtimestamp(stat.st_ctime, tz=datetime.timezone.utc)
            if "fs_modified" in self._os_collect:
                result.fs_modified = datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc)
            if "fs_accessed" in self._os_collect:
                result.fs_accessed = datetime.datetime.fromtimestamp(stat.st_atime, tz=datetime.timezone.utc)
            if "file_mode" in self._os_collect:
                result.file_mode = stat.st_mode

            if "file_hash" in self._os_collect:
                result.file_hash = self._compute_hash(path)
        except OSError as e:
            result.extract_errors.append(
                f"D5-PROP-002: OS stat failed for '{file_path}': {e}"
            )

    def _compute_hash(self, path: Path) -> Optional[str]:
        """Compute content hash per configured algorithm."""
        try:
            hasher = hashlib.new(self._hash_algorithm)
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, ValueError) as e:
            if self._logger:
                self._logger.warning(
                    f"Hash computation failed for '{path}': {e}",
                    context="FilePropertyExtractor._compute_hash"
                )
            return None

    # ---- Layer 2: Format-Specific Embedded Properties ----

    def _extract_embedded_properties(
        self,
        file_type: str,
        parser_metadata: Optional[Dict[str, Any]],
        result: FilePropertyResult,
    ) -> None:
        """
        Extract embedded properties using the per-file-type property_mapping from config.

        The mapping defines which parser output keys map to which registry columns.
        """
        type_config = self._by_type.get(file_type, {})
        if not type_config.get("enabled", False):
            return

        extraction_method = type_config.get("extraction_method", "os_only")
        if extraction_method != "parser_metadata":
            return

        if not parser_metadata:
            result.extract_errors.append(
                f"D5-PROP-003: No parser metadata provided for file_type='{file_type}'"
            )
            return

        property_mapping = type_config.get("property_mapping", [])
        for mapping in property_mapping:
            source_key = mapping.get("source_key")
            maps_to = mapping.get("maps_to")
            if not source_key or not maps_to:
                continue

            value = parser_metadata.get(source_key)
            if value is None or value == "":
                null_strategy = mapping.get("null_handling", {}).get("strategy", "skip")
                if null_strategy == "default_value":
                    default = mapping.get("null_handling", {}).get("default_value")
                    self._set_result_field(result, maps_to, default)
                # 'skip' strategy: leave field as None (default)
                continue

            self._set_result_field(result, maps_to, value)

    def _set_result_field(
        self, result: FilePropertyResult, field_name: str, value: Any
    ) -> None:
        """Set a field on FilePropertyResult by its mapped registry column name."""
        # Map registry column names to FilePropertyResult attribute names
        registry_to_attr: Dict[str, str] = {
            "created_by": "created_by",
            "page_count": "page_count",
            "embedded_title": "embedded_title",
            "embedded_subject": "embedded_subject",
            "embedded_created_date": "embedded_created_date",
            "embedded_modified_date": "embedded_modified_date",
            "embedded_creator_app": "embedded_creator_app",
            "embedded_producer": "embedded_producer",
            "embedded_last_modified_by": "embedded_last_modified_by",
            "embedded_keywords": "embedded_keywords",
            "embedded_sheet_count": "embedded_sheet_count",
            "embedded_revision_number": "embedded_revision_number",
        }
        attr_name = registry_to_attr.get(field_name)
        if attr_name and hasattr(result, attr_name):
            setattr(result, attr_name, value)


# ---- Module-Level Convenience Function ----

def extract_file_properties(
    file_path: str,
    file_type: str,
    file_property_patterns: Optional[Dict[str, Any]] = None,
    parser_metadata: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
) -> FilePropertyResult:
    """
    One-shot convenience wrapper — instantiates FilePropertyExtractor per call.

    Prefer instantiating FilePropertyExtractor once and calling .extract() in a loop
    for batch operations (Phase B pipeline processing).
    """
    extractor = FilePropertyExtractor(file_property_patterns, logger)
    return extractor.extract(file_path, file_type, parser_metadata)
```

### J4.4 Extraction Algorithm (Step-by-Step)

```
Input:  file_path, file_type, parser_metadata (optional)
Output: FilePropertyResult

Step 1: [__init__]: Load config
    Resolve os_properties block (collect set, hash_algorithm)
    Resolve by_file_type block (per-extension mappings)
    Validate: if config is empty → no-op mode (all fields None)

Step 2: [extract] Layer 1 — OS-level properties
    If os_properties.enabled is false → skip
    Path.stat() the file
    For each key in os_properties.collect:
        "file_size"    → result.file_size = stat.st_size
        "fs_created"   → result.fs_created = datetime.fromtimestamp(stat.st_ctime, UTC)
        "fs_modified"  → result.fs_modified = datetime.fromtimestamp(stat.st_mtime, UTC)
        "fs_accessed"  → result.fs_accessed = datetime.fromtimestamp(stat.st_atime, UTC)
        "file_mode"    → result.file_mode = stat.st_mode
        "file_hash"    → result.file_hash = compute_hash(path, algorithm)
    On OSError → D5-PROP-002, extract_status = "failed", abort

Step 3: [extract] Layer 2 — Embedded (format-specific) properties
    Look up file_type in by_file_type config
    If not found or enabled=false → skip
    If extraction_method is "os_only" → skip (DGN/DWG stubs)
    If extraction_method is "parser_metadata":
        If parser_metadata is None → D5-PROP-003, skip
        For each entry in property_mapping:
            value = parser_metadata.get(source_key)
            If value is None/empty → apply null_handling strategy
                "skip" → leave field as None
                "default_value" → set to configured default
            Else → set result.{maps_to} = value

Step 4: Finalize extract_status
    No errors → "ok"
    Errors but file_size populated → "partial"
    Neither → "failed"
```

---

## J5. Capability Matrix — All File Types

| Property | Layer | PDF | DOCX | XLSX | DGN | DWG | Maps to Registry |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `file_size` | 1 (OS) | ✅ | ✅ | ✅ | ✅ | ✅ | `file_size` (new) |
| `fs_created` | 1 (OS) | ✅ | ✅ | ✅ | ✅ | ✅ | `file_created_at` (new) |
| `fs_modified` | 1 (OS) | ✅ | ✅ | ✅ | ✅ | ✅ | `file_modified_at` (new) |
| `file_hash` | 1 (OS) | ✅ | ✅ | ✅ | ✅ | ✅ | `file_hash` (new) |
| `author` | 2 (embedded) | ✅ | ✅ | ✅ | ❌ | ❌ | `created_by` (existing) |
| `title` | 2 (embedded) | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_title` (new) |
| `subject` | 2 (embedded) | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_subject` (new) |
| `creator_app` | 2 (embedded) | ✅ | — | — | ❌ | ❌ | `embedded_creator_app` (new) |
| `producer_lib` | 2 (embedded) | ✅ | — | — | ❌ | ❌ | `embedded_producer` (new) |
| `embedded_created` | 2 (embedded) | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_created_date` (new) |
| `embedded_modified` | 2 (embedded) | ✅ | ✅ | ✅ | ❌ | ❌ | `embedded_modified_date` (new) |
| `page_count` | 2 (embedded) | ✅ | — | — | ❌ | ❌ | `page_count` (existing) |
| `sheet_count` | 2 (embedded) | — | — | ✅ | ❌ | ❌ | `embedded_sheet_count` (new) |
| `last_modified_by` | 2 (embedded) | — | ✅ | ✅ | ❌ | ❌ | `embedded_last_modified_by` (new) |
| `revision_number` | 2 (embedded) | — | ✅ | — | ❌ | ❌ | `embedded_revision_number` (new) |

✅ = Library supports extraction  
❌ = Stub parser (no metadata until Phase 3)  
— = Not applicable to format

---

## J6. Worked Examples

### Example 1: Standard PDF Drawing

```
Input:
  file_path = "eks/data/twrp/drawings/131101-WSW41-SP-SG-0101.pdf"
  file_type = "pdf"
  parser_metadata = {
      "author": "John Smith",
      "title": None,
      "subject": None,
      "creator": "AutoCAD 2024",
      "producer": "pdfplot15.hdi 15.2.1.0",
      "creation_date": "D:20240315120000+08'00'",
      "mod_date": "D:20240315120000+08'00'",
      "page_count": 1
  }

Layer 1 (OS):
  file_size     = 245678      (st_size)
  fs_created    = 2024-06-01T10:30:00Z  (st_ctime, UTC)
  fs_modified   = 2024-06-01T10:30:00Z  (st_mtime, UTC)
  file_hash     = "a3f8b2c1d4e5..."    (MD5)

Layer 2 (PDF embedded, per config mapping):
  "author"        → created_by                = "John Smith"
  "title"         → None (null_handling: skip)
  "subject"       → None (null_handling: skip)
  "creator"       → embedded_creator_app      = "AutoCAD 2024"
  "producer"      → embedded_producer         = "pdfplot15.hdi 15.2.1.0"
  "creation_date" → embedded_created_date     = "D:20240315120000+08'00'"
  "mod_date"      → embedded_modified_date    = "D:20240315120000+08'00'"
  "page_count"    → page_count                = 1

Result:
  FilePropertyResult(
      file_size=245678,
      fs_created=datetime(2024,6,1,10,30,0,tz=UTC),
      fs_modified=datetime(2024,6,1,10,30,0,tz=UTC),
      file_hash="a3f8b2c1d4e5...",
      created_by="John Smith",
      embedded_creator_app="AutoCAD 2024",
      embedded_producer="pdfplot15.hdi 15.2.1.0",
      embedded_created_date="D:20240315120000+08'00'",
      embedded_modified_date="D:20240315120000+08'00'",
      page_count=1,
      extract_status="ok",
      extract_errors=[]
  )

Registry write (via to_registry_dict()):
  {
      "file_size": 245678,
      "file_created_at": "2024-06-01T10:30:00+00:00",
      "file_modified_at": "2024-06-01T10:30:00+00:00",
      "file_hash": "a3f8b2c1d4e5...",
      "created_by": "John Smith",
      "embedded_creator_app": "AutoCAD 2024",
      "embedded_producer": "pdfplot15.hdi 15.2.1.0",
      "embedded_created_date": "D:20240315120000+08'00'",
      "embedded_modified_date": "D:20240315120000+08'00'",
      "page_count": 1
  }
```

### Example 2: DOCX Specification

```
Input:
  file_path = "eks/data/twrp/spec/SPC-001.docx"
  file_type = "docx"
  parser_metadata = {
      "author": "Alice Chen",
      "title": "Technical Specification — Pump P-101",
      "subject": None,
      "created": "2024-02-10T09:00:00",
      "modified": "2024-03-20T14:30:00",
      "revision": "5",
      "last_modified_by": "Bob Wang"
  }

Layer 1 (OS):
  file_size     = 524288
  fs_modified   = 2024-03-21T08:00:00Z  ← NOTICE: different from embedded modified!

Layer 2 (DOCX embedded):
  "author"           → created_by                 = "Alice Chen"
  "title"            → embedded_title             = "Technical Specification — Pump P-101"
  "subject"          → None (skip)
  "created"          → embedded_created_date      = "2024-02-10T09:00:00"
  "modified"         → embedded_modified_date     = "2024-03-20T14:30:00"
  "revision"         → embedded_revision_number   = "5"
  "last_modified_by" → embedded_last_modified_by  = "Bob Wang"

Result:
  FilePropertyResult(
      file_size=524288,
      fs_modified=datetime(2024,3,21,8,0,0,tz=UTC),
      file_hash="b4c9d3e5f6a7...",
      created_by="Alice Chen",
      embedded_title="Technical Specification — Pump P-101",
      embedded_created_date="2024-02-10T09:00:00",
      embedded_modified_date="2024-03-20T14:30:00",
      embedded_revision_number="5",
      embedded_last_modified_by="Bob Wang",
      extract_status="ok"
  )

Forensic note: fs_modified (2024-03-21) > embedded_modified (2024-03-20) by 1 day.
Possible file copy or system metadata update after last save.
```

### Example 3: DGN Stub (OS-Only)

```
Input:
  file_path = "eks/data/twrp/cad/131101-WSW41-PI-PID-0001.dgn"
  file_type = "dgn"
  parser_metadata = None  (not invoked — os_only extraction method)

Layer 1 (OS):
  file_size   = 1048576
  fs_modified = 2024-01-15T12:00:00Z
  file_hash   = "c5d4e3f2a1b0..."

Layer 2:
  extraction_method = "os_only" → skipped

Result:
  FilePropertyResult(
      file_size=1048576,
      fs_modified=datetime(2024,1,15,12,0,0,tz=UTC),
      file_hash="c5d4e3f2a1b0...",
      extract_status="ok",
      extract_errors=[]
  )
```

### Example 4: File Not Found

```
Input:
  file_path = "/nonexistent/path/file.pdf"
  file_type = "pdf"

Layer 1 (OS):
  Path.stat() → FileNotFoundError → D5-PROP-002

Result:
  FilePropertyResult(
      extract_status="failed",
      extract_errors=["D5-PROP-002: OS stat failed for '/nonexistent/path/file.pdf': [Errno 2] No such file or directory"]
  )
```

---

## J7. Pipeline Integration

### J7.1 Current Flow (Broken)

```
Phase B: PipelineOrchestrator._process_file()
  │
  ├─ parser.parse() → content_blocks
  ├─ parser.extract_metadata() → metadata (L552)
  │     │
  │     └─ pout.metadata = metadata  (L575)  ← STORED but NEVER WRITTEN to registry
  │
  └─ self._update_doc_status(file_path, "success", confidence=..., notes=...)
        ← writes extract_status, extraction_confidence, extraction_notes
        ← metadata dict DISCARDED
```

### J7.2 Proposed Flow (Fixed)

```
Phase B: PipelineOrchestrator._process_file()
  │
  ├─ parser.parse() → content_blocks
  ├─ parser.extract_metadata() → parser_metadata
  │
  ├─ [NEW] result = self._property_extractor.extract(
  │           file_path, file_type, parser_metadata
  │       )
  │     │
  │     └─ FilePropertyResult with 16+ fields
  │
  ├─ [NEW] registry_props = result.to_registry_dict()
  │
  ├─ self._update_document_status(file_path, "success",
  │       confidence=...,
  │       notes=...,
  │       extra_properties=registry_props   ← NEW: writes to registry
  │   )
  │
  └─ pout.metadata = {**parser_metadata, **registry_props}
```

### J7.3 `update_document_status()` Change

Current signature (`registry.py`):

```python
def update_document_status(
    self,
    file_path: str,
    extract_status: str,
    confidence: Optional[float] = None,
    notes: Optional[str] = None,
) -> None:
```

Proposed new parameter:

```python
def update_document_status(
    self,
    file_path: str,
    extract_status: str,
    confidence: Optional[float] = None,
    notes: Optional[str] = None,
    extra_properties: Optional[Dict[str, Any]] = None,  # NEW: from FilePropertyResult.to_registry_dict()
) -> None:
```

If `extra_properties` is provided, `UPDATE documents SET ...` for each key whose column exists in `COLUMN_ALLOWLIST` and is not None.

### J7.4 Instance Lifecycle

```python
# PipelineOrchestrator.__init__:
self._property_extractor = FilePropertyExtractor(
    file_property_patterns=self.doc_config.get("file_property_patterns"),
    logger=self.logger,
)

# FileScanner.__init__ (optional — Phase A may also collect OS-level properties):
self._property_extractor = FilePropertyExtractor(
    file_property_patterns=self.doc_config.get("file_property_patterns"),
    logger=self.logger,
)
```

### J7.5 Export

Add to `eks/engine/core/__init__.py`:

```python
from .file_property_parser import FilePropertyExtractor, FilePropertyResult, extract_file_properties
```

---

## J8. Error Code Taxonomy — Appendix D Alignment

### J8.1 D5-PROP-* Codes

From Appendix D §D2 convention: `D{phase}-{module}-{sequential_id}`.

| Code | Name | Severity | Trigger | Pipeline Impact |
|:---|:---|:---|:---|:---|
| `D5-PROP-001` | File not found for property extraction | WARNING | `Path.stat()` fails with FileNotFoundError | Skip property extraction for this file; continue registration |
| `D5-PROP-002` | OS stat failed | WARNING | OSError during `Path.stat()` (permissions, disk error) | Set `extract_status: "failed"`; OS-level fields remain None |
| `D5-PROP-003` | No parser metadata provided | WARNING | Parser metadata dict is None but extraction_method is "parser_metadata" | Skip Layer 2; Layer 1 (OS) properties still extracted |
| `D5-PROP-004` | Property mapping value invalid | WARNING | Embedded property value fails type coercion (e.g., non-integer for page_count) | Skip that specific property; others mapped normally |
| `D5-PROP-005` | Hash computation failed | WARNING | OSError or ValueError during file hash computation | `file_hash` remains None; other OS properties extracted normally |

### J8.2 Registration in `eks_error_config.json`

Each code must be registered under `data_logic_errors`:

```json
{
    "code": "D5-PROP-001",
    "name": "File not found for property extraction",
    "severity": "WARNING",
    "description": "The file path resolved during Phase B does not exist on disk. OS-level file properties cannot be collected. The file will still be registered with extract_status='failed'.",
    "module": "file_property_parser",
    "pipeline_phase": "P0",
    "dcc_parallel": "DCC: Code D (file access error)"
}
```

(Repeat for D5-PROP-002 through D5-PROP-005.)

---

## J9. Health Scoring Impact (Appendix D §D7.1)

The new file properties feed into 3 of the 6 health scoring dimensions:

| Dimension | Weight | Property | Scoring Rule |
|:---|:---|:---|:---|
| **completeness** | 0.20 | `file_size`, `file_hash`, `created_by`, `page_count` | % of non-null fields / total expected fields |
| **source_quality** | 0.15 | `embedded_creator_app`, `embedded_producer`, `file_modified_at` | Bonus if creator app is known (e.g., "AutoCAD") and dates agree |
| **consistency** | 0.10 | `file_modified_at` vs `embedded_modified_date` | Penalty if timestamps diverge by >24h (see §J3.3) |

---

## J10. Cross-Appendix Alignment

| Concept | Appendix B (Registry) | Appendix D (Errors) | Appendix I (Filename) | Appendix J (Properties) | DCC (Reference) |
|:---|:---|:---|:---|:---|:---|
| `file_size` | B3 / J3.2 (new column) | — | — | OS-level, all types | DCC: File size metadata |
| `file_hash` | B3 / J3.2 (new column) | D5-PROP-005 | — | OS-level MD5/SHA256 | DCC: integrity check |
| `created_by` | B3: Account (existing, never populated) | — | — | Layer 2: `author` mapping | DCC: author field |
| `page_count` | B3: Technical (existing, never populated) | — | — | Layer 2: PDF `page_count` | DCC: page count |
| `file_type` | B3.3: file_type_registry | D5-PARSE-001 | Extension-based | Used to select per-type property mapping | DCC: file format |
| `document_type` | B3.2: document_type_registry | — | I3: segment[2] | Indirectly helps verify file_type→doc_type alignment | DCC: doc type |
| Dual dates | B3 / J3.3 (forensic) | D7.1 (consistency) | — | `file_modified_at` + `embedded_modified_date` | DCC: date discrepancy flag |
| OS properties | J3.2 (new columns) | D5-PROP-001, 002 | — | Always-on Layer 1 | — |
| Embedded props | J3.2 (new columns) | D5-PROP-003, 004 | — | Per-type Layer 2, parser-driven | — |

---

## J11. Per-File-Type Property Key Reference

This section documents the exact keys returned by each parser's `extract_metadata()` method, as they are the `source_key` values referenced in `file_property_patterns.by_file_type.{ext}.property_mapping`.

### J11.1 PDF (`pdf_parser.py` L36–44)

| `source_key` | Type | Description | Reliability |
|:---|:---|:---|:---|
| `author` | `str\|None` | Document author | Medium — often set by CAD/Word |
| `title` | `str\|None` | Document title | Medium — often empty |
| `subject` | `str\|None` | Document subject | Low — rarely populated in engineering PDFs |
| `creator` | `str\|None` | Creating application (e.g., `"AutoCAD 2024"`) | **High** — valuable for provenance |
| `producer` | `str\|None` | PDF producer library (e.g., `"pdfTeX-1.40.25"`) | **High** — identifies conversion toolchain |
| `creation_date` | `str\|None` | PDF internal creation date | Medium — as ISO datetime |
| `mod_date` | `str\|None` | PDF internal modification date | Medium |
| `page_count` | `int` | Number of pages (from `doc.page_count`) | **High** — always present |

### J11.2 DOCX (`docx_parser.py` L57–62)

| `source_key` | Type | Description | Reliability |
|:---|:---|:---|:---|
| `author` | `str\|None` | Original author (from `core_properties.author`) | **High** |
| `title` | `str\|None` | Document title | Medium |
| `subject` | `str\|None` | Document subject | Low |
| `created` | `str\|None` | Created date (ISO, from `core_properties.created`) | **High** |
| `modified` | `str\|None` | Last-saved date (ISO, from `core_properties.modified`) | **High** |
| `revision` | `int\|None` | Word internal revision number (from `core_properties.revision`) | Medium — NOT document revision |

**Note**: python-docx also exposes `last_modified_by`, `category`, `keywords`, `comments`, `content_status`, `identifier`, `language`, `version` on `core_properties`. These are NOT currently returned by `extract_metadata()` but can be added to the parser's output tuple without schema changes — only config needs updating.

### J11.3 XLSX (`xlsx_parser.py` L43–49)

| `source_key` | Type | Description | Reliability |
|:---|:---|:---|:---|
| `author` | `str\|None` | Creator (from `properties.creator`) | **High** |
| `title` | `str\|None` | Workbook title | Medium |
| `subject` | `str\|None` | Workbook subject | Low |
| `created` | `str\|None` | Created date (ISO, from `properties.created`) | **High** |
| `modified` | `str\|None` | Modified date (ISO, from `properties.modified`) | **High** |
| `sheet_count` | `int` | Number of sheets (from `len(wb.sheetnames)`) | **High** |

**Note**: openpyxl also exposes `last_modified_by`, `category`, `keywords`, `description`, `identifier`, `language`, `version`, `revision` on `wb.properties`. These are NOT currently returned by `extract_metadata()` but can be added similarly.

### J11.4 DGN (`dgn_parser.py` L22–27) — Stub

| `source_key` | Type | Description |
|:---|:---|:---|
| `file_path` | `str` | Path to DGN file |
| `format` | `str` | `"dgn"` |
| `status` | `str` | `"stub"` |

No embedded metadata extraction. Only OS-level properties apply.

### J11.5 DWG (`dwg_parser.py` L22–27) — Stub

| `source_key` | Type | Description |
|:---|:---|:---|
| `file_path` | `str` | Path to DWG file |
| `format` | `str` | `"dwg"` |
| `status` | `str` | `"stub"` |

No embedded metadata extraction. Only OS-level properties apply.

---

## J12. Implementation Plan

### J12.1 Task Breakdown

| Task | Description | Files | Depends On |
|:---|:---|:---|:---|
| **T-J.1** | Add `file_property_source_def`, `file_property_pattern_def`, `file_property_os_def` to `eks_doc_base_schema.json` definitions; add 13 new optional columns to `document_metadata_def` | `eks_doc_base_schema.json` | — |
| **T-J.2** | Add `file_property_patterns` schema declaration to `eks_doc_setup_schema.json` | `eks_doc_setup_schema.json` | T-J.1 |
| **T-J.3** | Add `file_property_patterns` config block to `eks_doc_config.json` with OS config + per-file-type property mappings (5 entries: pdf, docx, xlsx, dgn, dwg) | `eks_doc_config.json` | T-J.1, T-J.2 |
| **T-J.4** | Create `file_property_parser.py` with `FilePropertyResult` dataclass + `FilePropertyExtractor` class + `extract_file_properties()` convenience function | `file_property_parser.py` (new), `__init__.py` | T-J.3 |
| **T-J.5** | Integrate into `PipelineOrchestrator._process_file()`: call extractor after `parse_result` metadata capture, before `update_document_status()` | `pipeline_orchestrator.py` | T-J.4 |
| **T-J.6** | Update `DocumentRegistry.update_document_status()` to accept and persist `extra_properties` | `registry.py` | T-J.5 |
| **T-J.7** | Update `DocumentRegistry._init_db()` / `_migrate_schema()` to add 13 new columns via `ALTER TABLE IF NOT EXISTS` | `registry.py` | T-J.1 |
| **T-J.8** | Register `D5-PROP-001` through `D5-PROP-005` in error catalog + setup schema | `eks_error_config.json`, `eks_error_base.json`, `eks_error_setup_schema.json` | — |
| **T-J.9** | Extend parser `extract_metadata()` methods: (a) DOCX: add `last_modified_by` key; (b) XLSX: add `last_modified_by` key; (c) PDF: add `keywords` key | `pdf_parser.py`, `docx_parser.py`, `xlsx_parser.py` | — |
| **T-J.10** | Add unit tests for `FilePropertyExtractor`: OS-level extraction, per-type embedded mapping, null handling, file-not-found, hash computation, `to_registry_dict()` format | `test_t132_modules.py` or new test file | T-J.4–T-J.6 |
| **T-J.11** | Pipeline verification: run Phase A + Phase B on TWRP dataset; verify all 171 files have `file_size`, `file_hash`, `file_modified_at` populated; verify PDFs have `created_by`, `page_count`, `embedded_creator_app` populated | — | T-J.1–T-J.10 |
| **T-J.12** | Update `update_log.md`, update Appendix B §B3 to include 13 new columns, close related issues | `update_log.md`, `appendix_b_document_registry.md` | T-J.11 |

### J12.2 Success Criteria

1. All 171 TWRP files have `file_size`, `file_hash`, and `file_modified_at` populated in registry after Phase A scan
2. PDF files have `created_by`, `page_count`, `embedded_creator_app`, `embedded_producer` populated from parser metadata
3. DOCX files have `created_by`, `embedded_title`, `embedded_created_date`, `embedded_modified_date`, `embedded_last_modified_by` populated
4. XLSX files have `created_by`, `embedded_sheet_count`, `embedded_created_date`, `embedded_modified_date` populated
5. DGN/DWG files have only OS-level properties (no embedded metadata available)
6. Registry `page_count` column (Appendix B §B3) is populated for all PDF files
7. Registry `created_by` column (Appendix B §B3) is populated for all PDF/DOCX/XLSX files
8. `file_modified_at` and `embedded_modified_date` are both stored when available (dual-date collection)
9. `D5-PROP-001` through `D5-PROP-005` present in error catalog
10. No file silently dropped — OS extraction failure logs `D5-PROP-002` but registration continues

### J12.3 Risks

| Risk | Likelihood | Mitigation |
|:---|:---|:---|
| Large files: hash computation blocks pipeline | Medium | Use chunked reading (8192-byte buffer); configurable `hash_algorithm` allows faster MD5 vs SHA256 |
| `page_count` type mismatch: parser returns int but registry expects INTEGER | Low | `to_registry_dict()` preserves int type; DuckDB coerces safely |
| PDF `creation_date` format varies (D: prefix, timezone) | Medium | Store raw string from PyMuPDF; format normalization is a future Phase 3 concern |
| `ALTER TABLE` migration conflicts with existing DuckDB schema | Low | Use `ALTER TABLE IF NOT EXISTS` pattern (already in `_migrate_schema()`) |
| Performance: `file_hash` computed for every file doubles Phase A time | Medium | Config allows omitting `"file_hash"` from `os_properties.collect`; hash is optional per schema |
| DOCX `revision` key conflicts with document `revision` column | Low | Mapped to `embedded_revision_number` (not `revision`); clear naming distinction |
| Extending parser `extract_metadata()` changes existing output format | Low | Adding new keys is backward-compatible (dict keys are additive); existing consumers ignore unknown keys |

---

## J13. References

- [Appendix B — Document Registry](appendix_b_document_registry.md) — B3 column table, B3.1 ontology triggers, B3.3 file_type_registry
- [Appendix D — Pipeline Messages & Errors](appendix_d_pipeline_messages_errors.md) — D5 error taxonomy, D7.1 health scoring dimensions
- [Appendix F — Pipeline Architecture](appendix_f_pipeline_architecture_design.md) — Phase A/B orchestration, `_process_file()`
- [Appendix I — Filename Parser](appendix_i_filename_parser.md) — design pattern reference (universal class, dataclass, config-driven)
- [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) §20 — Document Registry & Revision Management
- [`eks/engine/parsers/io_contracts.py`](../engine/parsers/io_contracts.py) — `ParserOutput.metadata` field (currently unused downstream)
- [`eks/engine/core/pipeline_orchestrator.py`](../engine/core/pipeline_orchestrator.py) — L552 metadata capture, L575 pout assignment, L577 `update_document_status()` call

---

## J14. Implementation Record — ✅ COMPLETE

> **Relocated from [main workplan §43](phase_1_foundation_workplan.md#43-file-property-extraction--appendix-j-implementation-i147i162--complete).** Canonical source is now here.

### J14.1 Objective

Implement the schema-driven file property extractor defined in this appendix, closing 14 open issues (I147–I154, I156, I158–I162). This module is the **first code anywhere in EKS** to call `os.stat()` / `Path.stat()` and `hashlib` — OS-level file properties are completely absent today. It also closes the **data-dropping pipeline gap**: parser `extract_metadata()` results are captured at `_process_file()` L552 but never persisted to the Document Registry.

**What changes**: Two-layer extraction (OS stat + embedded parser metadata) runs inside Phase B `_process_file()`. Results flow through `update_document_status(extra_properties=...)` → DuckDB `INSERT`/`UPDATE` with dynamically-built column lists. 13 new registry columns are added via auto-migration. All extraction rules are schema-driven via `file_property_patterns` config.

### J14.2 Scope Summary

| Dimension | Detail |
|:---|:---|
| **Issues closed** | I147–I154, I156, I158–I162 (14 total) |
| **New registry columns** | 13: `file_size`, `file_created_at`, `file_modified_at`, `file_hash`, `embedded_title`, `embedded_subject`, `embedded_created_date`, `embedded_modified_date`, `embedded_creator_app`, `embedded_producer`, `embedded_last_modified_by`, `embedded_keywords`, `embedded_sheet_count` |
| **Existing columns populated** | `created_by` (from parser `author`), `page_count` (from PDF parser) |
| **Files created** | `eks/engine/core/file_property_parser.py` — `FilePropertyExtractor` class + `FilePropertyResult` dataclass |
| **Files modified** | `pipeline_orchestrator.py` (Phase B wiring), `registry.py` (`update_document_status()` + `extra_properties` param), `eks_doc_base_schema.json` (13 new columns + 3 definitions), `eks_doc_setup_schema.json` (`file_property_patterns`), `eks_doc_config.json` (5 per-type mappings), `eks_error_config.json` (D5-PROP-001..005) |

### J14.3 Cross-References

| Ref | Location | Detail |
|:---|:---|:---|
| I147–I162 | `eks/log/issue_log.md` | 14 file property extraction issues |
| U183 | `eks/log/update_log.md` | Implementation update entry |
| [P1.1 §5.3](appendix_p1.1_architecture.md#53-option-a2--unified-p-prefix-error-codes--appendix-i-filename-parser-i133i146-i155-i157-i163--complete) | P-prefix error code rename (D5-PROP → P5) |
| [Appendix I](appendix_i_filename_parser.md) | FilenameParser — boundary definition (J1.1) |
