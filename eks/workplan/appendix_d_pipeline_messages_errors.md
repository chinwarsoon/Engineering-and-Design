# Appendix D — Pipeline Messages & Error Codes

**Version**: 0.3  
**Last Updated**: 2026-06-19  
**Phase**: 1 — Foundation (schema) / 3 (runtime)  
**Status**: ✅ Implemented & Tested  
**Related Files**:
- [`eks/engine/logging/logger.py`](../engine/logging/logger.py)
- [`eks/engine/core/registry.py`](../engine/core/registry.py) — document_elements table
- [`dcc/config/schemas/error_code_base.json`](../../dcc/config/schemas/error_code_base.json) — DCC reference pattern
- [`dcc/config/schemas/pipeline_message_base.json`](../../dcc/config/schemas/pipeline_message_base.json) — DCC reference pattern

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-06-19 | opencode | Initial draft: D1–D10 (Overview, Error Code Format, Taxonomy, System/Data Catalogs, Messages, Health Scoring, Status Lifecycle, Implementation Files) |
| 0.2 | 2026-06-19 | opencode | Revised D7: All-column health scoring (18 scorable columns, 3 weight tiers, 5 dimensions with weighted composite formula, extraction_notes JSON format, 3 worked examples) |
| 0.3 | 2026-06-19 | opencode | Added D7.10 Structural Elements Table (`document_elements`); revised D7 to 6-dimension composite (added structural completeness); added 8 structural error codes (D5), 8 structural messages (D6); updated D9 implementation files; updated D8 status lifecycle |

---

## D1. Overview

The EKS pipeline messaging and error system follows the DCC pattern (per AGENTS.md §19: "Each business logic must have an independent error code defined to trace related errors"). It consists of three components:

1. **Error Codes** — Unique identifiers for every system and data error, enabling precise tracing
2. **Pipeline Messages** — Schema-driven user-facing status/milestone/warning messages
3. **Health Scoring** — Per-document extraction confidence and pipeline-level quality metrics

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Schema-driven** | Error codes and messages defined in JSON config files, not hardcoded |
| **Two error domains** | System-status (pipeline execution) vs data-handling (quality/integrity) |
| **Unique per business logic** | Each distinct error condition gets its own code (AGENTS.md §19) |
| **Fail-fast metadata** | Critical errors stop the pipeline; warnings accumulate |
| **Traceable** | Every error links to its source module, function, and phase |
| **Health-aware** | Errors impact health scores; scores drive quality gates |

### DCC Alignment

EKS adopts the DCC error code taxonomy pattern with domain-specific adaptations:

| Aspect | DCC | EKS |
|--------|-----|-----|
| Data error format | `LL-M-F-XXXX` | `P{phase}-{module}-{function}-{id}` |
| System error format | `S-C-S-XXXX` | `S-C-S-XXXX` (identical) |
| Error domains | System + Data | System + Data |
| Health scoring | Per-row (tabular) | Per-document (registry) |
| Status lifecycle | NEW → IN_PROGRESS → RESOLVED → CLOSED | NEW → EXTRACTED → REGISTERED → VERIFIED |

---

## D2. Error Code Format

### Data Errors

**Format**: `P{phase}-{module}-{function}-{id}`

```
P  3  -  E  -  E  -  0001
│  │     │     │     │
│  │     │     │     └── 4-digit sequential ID (0001–9999)
│  │     │     └──────── Function code (R/P/E/V/L/F/S)
│  │     └────────────── Module code (R/P/E/G/V/X/C)
│  └──────────────────── Phase number (1–5)
└─────────────────────── Prefix: P = Phase
```

**Example**: `P3-E-E-0001` = Phase 3, Extractor module, Extract function, error #1

### System Errors

**Format**: `S-{category}-S-{id}`

```
S  -  F  -  S  -  0201
│     │     │     │
│     │     │     └── 4-digit sequential ID (0001–9999)
│     │     └──────── S = System
│     └────────────── Category (E/F/C/R/D)
└──────────────────── S = System prefix
```

**Example**: `S-F-S-0201` = System, File category, error #201

---

## D3. Error Code Taxonomy

### Phase Codes (Data Errors)

| Code | Phase | Description |
|------|-------|-------------|
| `P1` | Phase 1 — Foundation | Schema, registry, config |
| `P2` | Phase 2 — Chunking & Embedding | Parsing, chunking, embedding |
| `P3` | Phase 3 — Knowledge Graph | Extraction, ingestion, graph |
| `P4` | Phase 4 — Retrieval | Query, retrieval, scoring |
| `P5` | Phase 5 — UI | Interface, display |

### Module Codes

| Code | Module | Phase(s) | Description |
|------|--------|----------|-------------|
| `R` | Registry | 1, 3 | Document registry CRUD |
| `P` | Parser | 2 | File parsing (PDF, DOCX, XLSX) |
| `E` | Extractor | 3 | Metadata extraction (cover sheet, filename) |
| `G` | Graph | 3, 4 | Neo4j graph operations |
| `V` | Validator | 1, 3 | Schema/data validation |
| `X` | CrossRef | 3 | Cross-reference (datadrop, asset tags) |
| `C` | Config | 1 | Configuration loading |

### Function Codes

| Code | Function | Description |
|------|----------|-------------|
| `R` | Register | Registration / write operations |
| `P` | Parse | File parsing operations |
| `E` | Extract | Metadata extraction operations |
| `V` | Validate | Validation operations |
| `L` | Load | Load / ingest operations |
| `F` | Format | Format / output operations |
| `S` | System | System-level operations |

### Severity Levels

| Level | Description | Pipeline Impact |
|-------|-------------|-----------------|
| `FATAL` | Unrecoverable error, pipeline cannot continue | Stops execution immediately |
| `CRITICAL` | Major failure, requires intervention | Stops execution, allows cleanup |
| `HIGH` | Significant issue, degraded output | Logs error, continues with fallback |
| `MEDIUM` | Moderate issue, partial impact | Logs warning, continues |
| `WARNING` | Minor issue, no data loss | Logs warning, continues |
| `INFO` | Informational, no error | Logs info, continues |

### System Error Categories

| Code | Category | Range | Description |
|------|----------|-------|-------------|
| `E` | Environment | `S-E-S-0100–0199` | Python, packages, OS |
| `F` | File | `S-F-S-0200–0299` | File I/O, paths, permissions |
| `C` | Config | `S-C-S-0300–0399` | Schema, config, parameters |
| `R` | Runtime | `S-R-S-0400–0499` | Exceptions, memory, fail-fast |
| `D` | Database | `S-D-S-0500–0599` | DuckDB/PostgreSQL/Neo4j |

---

## D4. System Error Catalog

### S-E: Environment Errors (0100–0199)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-E-S-0101` | PYTHON_VERSION_WRONG | FATAL | Python version below 3.10 | Yes |
| `S-E-S-0102` | PACKAGE_MISSING | FATAL | Required package not installed | Yes |
| `S-E-S-0103` | PACKAGE_VERSION_CONFLICT | CRITICAL | Package version incompatible | Yes |
| `S-E-S-0104` | IMPORT_ERROR | CRITICAL | Module import failed | Yes |
| `S-E-S-0105` | MEMORY_LOW | HIGH | Available memory below threshold | No |
| `S-E-S-0106` | DISK_LOW | HIGH | Available disk below threshold | No |

### S-F: File I/O Errors (0200–0299)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-F-S-0201` | FILE_NOT_FOUND | FATAL | Input file does not exist | Yes |
| `S-F-S-0202` | FILE_READ_ERROR | CRITICAL | File exists but cannot be read | Yes |
| `S-F-S-0203` | FILE_WRITE_ERROR | CRITICAL | Cannot write output file | Yes |
| `S-F-S-0204` | FILE_PERMISSION_DENIED | FATAL | No read/write permission | Yes |
| `S-F-S-0205` | FILE_ENCODING_ERROR | HIGH | File encoding not supported | No |
| `S-F-S-0206` | FILE_CORRUPT | HIGH | File is corrupted or truncated | No |
| `S-F-S-0207` | PATH_NOT_FOUND | FATAL | Directory path does not exist | Yes |
| `S-F-S-0208` | PATH_CREATE_FAIL | CRITICAL | Cannot create output directory | Yes |
| `S-F-S-0209` | FILE_TOO_LARGE | WARNING | File exceeds size threshold | No |
| `S-F-S-0210` | FILE_EMPTY | WARNING | File exists but is empty | No |
| `S-F-S-0211` | SYMLINK_BROKEN | WARNING | Symbolic link target missing | No |
| `S-F-S-0212` | LOCK_CONFLICT | HIGH | File locked by another process | No |

### S-C: Config Errors (0300–0399)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-C-S-0301` | CONFIG_FILE_MISSING | FATAL | Config file not found | Yes |
| `S-C-S-0302` | CONFIG_PARSE_ERROR | FATAL | Config file is invalid JSON | Yes |
| `S-C-S-0303` | CONFIG_SCHEMA_INVALID | CRITICAL | Config fails schema validation | Yes |
| `S-C-S-0304` | CONFIG_KEY_MISSING | CRITICAL | Required config key absent | Yes |
| `S-C-S-0305` | CONFIG_VALUE_INVALID | CRITICAL | Config value out of range | Yes |
| `S-C-S-0306` | SCHEMA_FILE_MISSING | FATAL | Schema file not found | Yes |
| `S-C-S-0307` | SCHEMA_PARSE_ERROR | FATAL | Schema file is invalid JSON | Yes |
| `S-C-S-0308` | SCHEMA_VALIDATION_FAIL | CRITICAL | Data fails schema validation | Yes |
| `S-C-S-0309` | CONFIG_ENV_OVERRIDE_CONFLICT | WARNING | Environment variable conflicts with config | No |
| `S-C-S-0310` | CONFIG_FALLBACK_USED | INFO | Default config value used | No |
| `S-C-S-0311` | CONFIG_DEPRECATED_KEY | WARNING | Deprecated config key found | No |

### S-R: Runtime Errors (0400–0499)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-R-S-0401` | UNHANDLED_EXCEPTION | FATAL | Uncaught exception | Yes |
| `S-R-S-0402` | TYPE_ERROR | CRITICAL | Unexpected type encountered | Yes |
| `S-R-S-0403` | VALUE_ERROR | CRITICAL | Invalid value encountered | Yes |
| `S-R-S-0404` | KEY_ERROR | HIGH | Expected key not found in dict | No |
| `S-R-S-0405` | INDEX_ERROR | HIGH | Index out of range | No |
| `S-R-S-0406` | TIMEOUT | CRITICAL | Operation timed out | Yes |
| `S-R-S-0407` | FAIL_FAST_TRIGGERED | FATAL | Fail-fast threshold exceeded | Yes |

### S-D: Database Errors (0500–0599)

| Code | Name | Severity | Description | Stops Pipeline |
|------|------|----------|-------------|:--------------:|
| `S-D-S-0501` | DB_CONN_FAIL | FATAL | Cannot connect to database | Yes |
| `S-D-S-0502` | DB_QUERY_FAIL | CRITICAL | SQL query execution failed | Yes |
| `S-D-S-0503` | DB_TABLE_MISSING | CRITICAL | Expected table not found | Yes |
| `S-D-S-0504` | DB_COLUMN_MISSING | CRITICAL | Expected column not found | Yes |
| `S-D-S-0505` | DB_CONSTRAINT_VIOLATION | HIGH | Unique/PK constraint violated | No |
| `S-D-S-0506` | DB_TRANSACTION_FAIL | CRITICAL | Transaction commit failed | Yes |
| `S-D-S-0507` | DB_LOCK_TIMEOUT | HIGH | Database lock timeout | No |

---

## D5. Data Error Catalog

### Phase 1 — Registry Errors (P1-R)

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P1-R-R-0001` | DOC_ID_DUPLICATE | WARNING | Document ID already exists with same revision | -1 |
| `P1-R-R-0002` | DOC_ID_MISSING | CRITICAL | document_number is null or empty | -5 |
| `P1-R-R-0003` | REVISION_MISSING | HIGH | revision field is null | -3 |
| `P1-R-R-0004` | SCHEMA_VALIDATION_FAIL | CRITICAL | Metadata fails schema validation | -5 |
| `P1-R-R-0005` | ASSET_TAGS_INVALID | WARNING | asset_tags is not a valid JSON array | -1 |
| `P1-V-V-0001` | FIELD_TYPE_MISMATCH | WARNING | Field value does not match expected type | -1 |
| `P1-V-V-0002` | FIELD_ENUM_INVALID | WARNING | Field value not in allowed enum | -1 |
| `P1-C-C-0001` | CONFIG_LOAD_FAIL | CRITICAL | Failed to load project config | -5 |

### Phase 2 — Parser Errors (P2-P)

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P2-P-P-0001` | FILE_NOT_FOUND | FATAL | Source file does not exist | -10 |
| `P2-P-P-0002` | FILE_READ_ERROR | CRITICAL | File exists but cannot be parsed | -5 |
| `P2-P-P-0003` | PDF_NO_TEXT_LAYER | WARNING | Scanned PDF, no extractable text | -2 |
| `P2-P-P-0004` | PDF_PARSE_PARTIAL | WARNING | PDF parsed but some pages failed | -1 |
| `P2-P-P-0005` | XLSX_SHEET_MISSING | HIGH | Expected sheet not found in workbook | -3 |
| `P2-P-P-0006` | XLSX_CELL_ERROR | WARNING | Cell value cannot be read | -1 |
| `P2-P-P-0007` | DOCX_PARSE_FAIL | HIGH | DOCX structure invalid | -3 |
| `P2-P-P-0008` | DGN_UNSUPPORTED | HIGH | DGN file format not supported | -3 |

### Phase 3 — Extraction Errors (P3-E)

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P3-E-E-0001` | COVERSHEET_UNRECOGNIZED | WARNING | Cover sheet format not identified | -2 |
| `P3-E-E-0002` | DOC_NUMBER_EXTRACT_FAIL | WARNING | Could not extract document number | -2 |
| `P3-E-E-0003` | REVISION_EXTRACT_FAIL | WARNING | Could not extract revision | -2 |
| `P3-E-E-0004` | DISCIPLINE_EXTRACT_FAIL | WARNING | Could not extract discipline code | -1 |
| `P3-E-E-0005` | STATUS_EXTRACT_FAIL | WARNING | Could not extract approval status | -1 |
| `P3-E-E-0006` | CREATED_BY_EXTRACT_FAIL | INFO | Could not extract author | 0 |
| `P3-E-E-0007` | ORIGINATOR_EXTRACT_FAIL | INFO | Could not extract originator company | 0 |
| `P3-E-E-0008` | METADATA_INCOMPLETE | INFO | Some optional fields missing | 0 |
| `P3-E-E-0009` | CONFIDENCE_LOW | WARNING | Extraction confidence below threshold | -2 |
| `P3-E-E-0010` | COVER_PAGE_MISSING | WARNING | No cover page / title block detected | -3 |
| `P3-E-E-0011` | REVISION_TABLE_MISSING | WARNING | No revision history table detected | -2 |
| `P3-E-E-0012` | SECTIONS_MISSING | INFO | No section headings detected | 0 |
| `P3-E-E-0013` | TABLES_EMPTY | INFO | No data tables detected in body | 0 |
| `P3-E-E-0014` | IMAGES_DETECTED | INFO | Document contains images/charts | 0 |
| `P3-E-E-0015` | SCANNED_PAGES_FOUND | WARNING | Some pages have no text layer | -2 |
| `P3-E-E-0016` | ELEMENT_STORAGE_FAIL | WARNING | Detected element failed to store in DB | -1 |
| `P3-E-E-0017` | STRUCTURE_LOW_SCORE | WARNING | Structural completeness below 0.5 | -2 |

### Phase 3 — Cross-Reference Errors (P3-X)

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P3-X-X-0001` | KEYTAG_NO_MATCH | WARNING | asset_tag has no matching datadrop keytag | -1 |
| `P3-X-X-0002` | KEYTAG_AMBIGUOUS | WARNING | asset_tag matches multiple keytags | -1 |
| `P3-X-X-0003` | KEYTAG_FORMAT_INVALID | WARNING | asset_tag format does not match expected pattern | -1 |
| `P3-X-X-0004` | DATADROP_LOAD_FAIL | CRITICAL | Cannot load datadrop Excel file | -5 |
| `P3-X-X-0005` | DATADROP_SHEET_MISSING | HIGH | Expected datadrop sheet not found | -3 |

### Phase 3 — Graph Errors (P3-G)

| Code | Name | Severity | Description | Health Impact |
|------|------|----------|-------------|:-------------:|
| `P3-G-L-0001` | NEO4J_CONN_FAIL | FATAL | Cannot connect to Neo4j | -10 |
| `P3-G-L-0002` | NODE_CREATE_FAIL | CRITICAL | Node creation failed | -5 |
| `P3-G-L-0003` | EDGE_CREATE_FAIL | CRITICAL | Edge creation failed | -3 |
| `P3-G-L-0004` | ONTOLOGY_CLASS_MISSING | WARNING | Target ontology class not found | -1 |
| `P3-G-L-0005` | RELATIONSHIP_DUPLICATE | WARNING | Duplicate relationship already exists | 0 |
| `P3-G-L-0006` | NODE_PROPERTY_MISSING | WARNING | Required node property absent | -1 |

---

## D6. Pipeline Message Catalog

### Message Schema

Each message is defined with:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier (UPPER_SNAKE_CASE) |
| `category` | enum | `milestone`, `status`, `progress`, `warning`, `error` |
| `level` | integer | Verbosity: 0=quiet, 1=normal, 2=debug, 3=trace |
| `template` | string | Python-style template with `{placeholders}` |
| `icon` | string | Display icon/emoji |

### Milestone Messages

| ID | Level | Template | Icon |
|----|-------|----------|------|
| `MILESTONE_SETUP_VALIDATED` | 1 | `Setup validated: {config_count} configs loaded` | ✓ |
| `MILESTONE_REGISTRATION_START` | 1 | `Starting document registration...` | ▶ |
| `MILESTONE_REGISTRATION_COMPLETE` | 1 | `Registered {count} documents ({success} OK, {fail} failed)` | ✓ |
| `MILESTONE_PARSING_START` | 1 | `Starting batch parse of {path}...` | ▶ |
| `MILESTONE_PARSING_COMPLETE` | 1 | `Parse complete: {count} files processed` | ✓ |
| `MILESTONE_INGESTION_START` | 1 | `Starting bulk ingestion of {path}...` | ▶ |
| `MILESTONE_INGESTION_COMPLETE` | 1 | `Ingestion complete: {count} documents ({success} OK, {fail} failed, {skip} skipped)` | ✓ |
| `MILESTONE_GRAPH_START` | 1 | `Building knowledge graph...` | ▶ |
| `MILESTONE_GRAPH_COMPLETE` | 1 | `Graph built: {nodes} nodes, {edges} edges` | ✓ |

### Status Messages

| ID | Level | Template | Icon |
|----|-------|----------|------|
| `STATUS_CONFIG_LOADED` | 1 | `Config loaded: {path}` | ℹ |
| `STATUS_DB_INITIALIZED` | 1 | `Database initialized: {path}` | ℹ |
| `STATUS_PARSING_FILE` | 1 | `Parsing: {filename}` | ⚙ |
| `STATUS_EXTRACTING_METADATA` | 1 | `Extracting metadata from {filename}` | ⚙ |
| `STATUS_REGISTERING_DOC` | 1 | `Registering: {doc_id} Rev {revision}` | ⚙ |
| `STATUS_CROSS_REF` | 2 | `Cross-referencing {count} asset tags...` | ⚙ |
| `STATUS_GRAPH_NODE` | 2 | `Creating node: {node_type} ({label})` | ⚙ |
| `STATUS_GRAPH_EDGE` | 2 | `Creating edge: {source} → {edge_type} → {target}` | ⚙ |
| `STATUS_DETECTING_STRUCTURE` | 2 | `Detecting structural elements in {filename}` | ⚙ |
| `STATUS_STORING_ELEMENTS` | 2 | `Storing {count} elements for {doc_id}` | ⚙ |
| `STRUCTURE_COVER_PAGE` | 3 | `Cover page detected: {fields_found} fields, confidence {score}` | ℹ |
| `STRUCTURE_REVISION_TABLE` | 3 | `Revision table: {rows} rows, confidence {score}` | ℹ |
| `STRUCTURE_SECTIONS` | 3 | `Sections detected: {count} (max level {max_level})` | ℹ |

### Progress Messages

| ID | Level | Template | Icon |
|----|-------|----------|------|
| `PROGRESS_INGESTION` | 1 | `[{current}/{total}] {filename}` | ◐ |
| `PROGRESS_EXTRACTION` | 2 | `Extracted {field}: {value} (confidence: {score}%)` | ◑ |

### Warning Messages

| ID | Level | Template | Icon |
|----|-------|----------|------|
| `WARNING_SCANNED_PDF` | 1 | `Scanned PDF detected (no text layer): {filename}` | ⚠ |
| `WARNING_LOW_CONFIDENCE` | 1 | `Low extraction confidence ({score}%): {filename}` | ⚠ |
| `WARNING_NO_MATCH` | 2 | `Asset tag "{tag}" has no datadrop match` | ⚠ |
| `WARNING_AMBIGUOUS_MATCH` | 2 | `Asset tag "{tag}" matches {count} keytags: {matches}` | ⚠ |
| `WARNING_SKIPPED_FILE` | 1 | `Skipped: {filename} — {reason}` | ⚠ |
| `WARNING_NO_COVER_PAGE` | 1 | `No cover page detected: {filename}` | ⚠ |
| `WARNING_NO_REVISION_TABLE` | 1 | `No revision history table: {filename}` | ⚠ |
| `WARNING_STRUCTURE_LOW` | 1 | `Low structural completeness ({score}%): {filename}` | ⚠ |

### Error Messages

| ID | Level | Template | Icon |
|----|-------|----------|------|
| `ERROR_EXTRACTION_FAILED` | 0 | `Extraction failed for {filename}: {detail}` | ✗ |
| `ERROR_REGISTRATION_FAILED` | 0 | `Registration failed for {doc_id}: {detail}` | ✗ |
| `ERROR_GRAPH_FAILED` | 0 | `Graph operation failed: {detail}` | ✗ |
| `ERROR_INGESTION_ABORTED` | 0 | `Ingestion aborted at [{current}/{total}]: {detail}` | ✗ |

---

## D7. Health Scoring

### D7.1 Column Classification — All 25 Registry Columns

Every registry column is classified as scorable or non-scorable, and assigned a weight tier.

| # | Group | Column | Scorable | Source | Tier |
|---|-------|--------|:--------:|--------|:----:|
| 1 | Identity | `id` | — | System (PK) | — |
| 2 | Identity | `source_type` | — | Config default | — |
| 3 | Project | `project_title` | ✓ | Cover sheet / config | T2 |
| 4 | Project | `project_number` | ✓ | Filename / cover sheet | T1 |
| 5 | Project | `area` | ✓ | Filename / cover sheet | T2 |
| 6 | Project | `discipline` | ✓ | Filename / cover sheet | T1 |
| 7 | Project | `department` | ✓ | Cover sheet | T3 |
| 8 | Document | `document_type` | ✓ | Filename / cover sheet | T1 |
| 9 | Document | `document_number` | ✓ | Filename / cover sheet | T1 |
| 10 | Document | `revision` | ✓ | Cover sheet | T1 |
| 11 | Document | `status` | ✓ | Cover sheet revision table | T2 |
| 12 | Document | `is_latest` | — | System-generated | — |
| 13 | Document | `file_path` | — | System-generated | — |
| 14 | Document | `ingested_at` | — | System-generated | — |
| 15 | Account | `created_by` | ✓ | Cover sheet | T2 |
| 16 | Account | `checked_by` | ✓ | Cover sheet | T2 |
| 17 | Account | `approved_by` | ✓ | Cover sheet | T2 |
| 18 | Origin | `originator_company` | ✓ | Cover sheet | T2 |
| 19 | Origin | `security_class` | ✓ | Manual (Phase 5) | T3 |
| 20 | Origin | `asset_tags` | ✓ | Regex / content extraction | T1 |
| 21 | Technical | `page_count` | ✓ | PDF metadata | T2 |
| 22 | Quality | `extract_status` | — | System-generated | — |
| 23 | Quality | `extraction_confidence` | — | Stores the score | — |
| 24 | Quality | `extraction_notes` | — | System-generated | — |
| 25 | Quality | `verified_by` | ✓ | Manual (Phase 5) | T3 |

**Summary**: 18 scorable columns, 7 non-scorable (system/meta).

### D7.2 Weight Tiers

| Tier | Columns | Count | Rationale |
|------|---------|:-----:|-----------|
| **T1 — Critical Identity** | `project_number`, `discipline`, `document_type`, `document_number`, `revision`, `asset_tags` | 6 | Must be correct for registry to function; wrong value = broken graph |
| **T2 — Important Context** | `project_title`, `area`, `status`, `created_by`, `checked_by`, `approved_by`, `originator_company`, `page_count` | 8 | Valuable for retrieval and display; missing reduces usefulness |
| **T3 — Optional / Manual** | `department`, `security_class`, `verified_by` | 4 | Often null at extraction; filled during verification or rarely used |

### D7.3 Scoring Dimensions (6)

#### Dimension 1: Completeness (20%)

What fraction of scorable columns are populated.

```
completeness = populated_scorable_columns / 18
```

| Population | Score |
|:----------:|:-----:|
| 18/18 | 1.00 |
| 15/18 | 0.83 |
| 12/18 | 0.67 |
| 9/18 | 0.50 |
| 6/18 | 0.33 |
| 3/18 | 0.17 |
| 0/18 | 0.00 |

#### Dimension 2: Extraction Confidence (20%)

Per-column regex/extraction match quality, weighted by tier.

**Per-field match scores**:

| Match Type | Score | Description |
|------------|:-----:|-------------|
| Exact regex match | 1.0 | Value matches expected pattern exactly |
| Fuzzy match | 0.8 | Minor format deviation (lowercase, extra space) |
| Heuristic match | 0.5 | Context-guessed value from surrounding text |
| No match / null | 0.0 | Field not extracted |

**Tier multipliers** (amplify critical fields):

| Tier | Multiplier | Rationale |
|------|:---------:|-----------|
| T1 | ×2.0 | Critical identity fields must be correct |
| T2 | ×1.0 | Standard weighting |
| T3 | ×0.5 | Optional fields, low penalty if null |

```
field_weighted_score = sum(field_score × tier_multiplier) / sum(tier_multiplier_for_present_fields)
```

#### Dimension 3: Source Quality (20%)

Reliability of the document format.

| Type | Score | Description |
|------|:-----:|-------------|
| A | 1.0 | Standard drawing cover sheet — full field block |
| E | 0.8 | Specification doc — rich PDF metadata |
| B | 0.7 | Standard detail — partial fields |
| D | 0.7 | Volume cover page — limited fields |
| C | 0.3 | Scanned/vector-only — no text layer |
| F | 0.0 | Parse failed entirely |

#### Dimension 4: Cross-Reference Quality (15%)

Validation of extracted values against known data and config.

| Check | Applies To | Score |
|-------|-----------|:-----:|
| `asset_tags` match datadrop keytags | `asset_tags` | matched/total |
| `project_number` matches config project | `project_number` | 1.0 or 0.0 |
| `discipline` in project discipline list | `discipline` | 1.0 or 0.0 |
| `document_number` format valid | `document_number` | 1.0 or 0.0 |
| `revision` matches project revision pattern | `revision` | 1.0 or 0.0 |

```
xref_score = sum(check_pass) / total_applicable_checks
```

If no checks are applicable (e.g. no asset_tags, no config project), defaults to 1.0.

#### Dimension 5: Consistency (15%)

Cross-field agreement and logical checks. Violations apply a multiplicative modifier.

| Check | Violation | Deduction |
|-------|-----------|:---------:|
| `created_by` ≠ `checked_by` (if both present) | Same person reviewed and checked | -0.10 |
| `checked_by` ≠ `approved_by` (if both present) | Same person checked and approved | -0.10 |
| `page_count` > 0 for non-stub documents | Zero pages | -0.10 |
| `project_title` contains project context | Mismatch with `project_number` | -0.10 |
| `discipline` matches `document_type` category | Inconsistent classification | -0.10 |

```
consistency_modifier = 1.0 - (0.1 × violation_count)
```

### D7.4 Composite Health Score Formula

```
health_score = (
    completeness              × 0.20 +
    extraction_confidence     × 0.20 +
    structural_completeness   × 0.20 +
    source_quality            × 0.15 +
    xref_quality              × 0.15 +
    consistency_quality       × 0.10
) × consistency_modifier
```

Clamped to [0.0, 1.0].

**Dimension summary**:

| Dimension | Weight | Description |
|-----------|:------:|-------------|
| Completeness | 20% | Fraction of scorable columns populated |
| Extraction Confidence | 20% | Per-column regex/extraction match quality |
| Structural Completeness | 20% | Fraction of expected structural elements detected |
| Source Quality | 15% | Cover sheet type quality baseline |
| Cross-Reference | 15% | Asset tag, datadrop, document number validation |
| Consistency | 10% | Cross-field validation checks |

### D7.5 Score → Status Mapping

| Health Score | `extract_status` | `extraction_notes` | Pipeline Action |
|:------------:|:----------------:|:-------------------:|:----------------|
| ≥ 0.90 | `success` | Full breakdown | Auto-register |
| 0.70 – 0.89 | `success` | Full breakdown | Auto-register, optional review |
| 0.50 – 0.69 | `partial` | Full breakdown | Register, flag for review |
| 0.20 – 0.49 | `partial` | Full breakdown | Register, mandatory review |
| < 0.20 | `failed` | Full breakdown | Reject, manual entry required |

### D7.6 Extraction Notes Format

The `extraction_notes` field stores the full dimension breakdown as JSON:

```json
{
  "health_score": 0.87,
  "dimensions": {
    "completeness": {"score": 0.83, "populated": 15, "total": 18},
    "extraction_confidence": {
      "score": 0.91,
      "tier1_avg": 0.95,
      "tier2_avg": 0.88,
      "tier3_avg": 0.67
    },
    "structural_completeness": {"score": 0.80, "detected": 4, "expected": 5, "elements": ["cover_page", "revision_table", "sections", "images"]},
    "source_quality": {"score": 1.0, "type": "A"},
    "xref_quality": {"score": 0.80, "checks_passed": 4, "checks_total": 5},
    "consistency": {"score": 1.0, "violations": 0}
  },
  "missing_columns": ["department", "security_class", "verified_by"],
  "tier1_fields": {"populated": 5, "total": 6}
}
```

### D7.7 Pipeline Health Score (Batch Level)

Calculated per ingestion batch after all documents are processed.

**Formula**:

```
pipeline_health = (total_docs - critical_errors - high_errors) / total_docs × 100
```

**Grade thresholds**:

| Grade | Score | Meaning |
|-------|:-----:|---------|
| A+ | ≥ 99% | Excellent — near-perfect extraction |
| A | ≥ 95% | Good — minor issues only |
| A- | ≥ 90% | Acceptable — some warnings |
| B+ | ≥ 85% | Fair — several warnings |
| B | ≥ 80% | Marginal — needs attention |
| C | ≥ 70% | Poor — significant issues |
| D | ≥ 60% | Bad — major problems |
| F | < 60% | Failed — pipeline needs investigation |

**Secondary metric** — Average document health across batch:

```
avg_document_health = sum(health_scores) / total_docs
```

### D7.8 Health Score Impact per Error

Each data error code includes a `health_score_impact` value (see D5 tables). Error impacts are additive per document:

```
document_penalty = sum(health_score_impact for errors on this document)
adjusted_health = max(0.0, raw_health_score + document_penalty / 100)
```

### D7.9 Worked Examples

#### Example 1: Type A Document (High Score)

**Input**: `131101-WSW41-DR-C-0001.pdf` (standard cover sheet)

| Column | Value | Tier | Present | Confidence | XRef |
|--------|-------|:----:|:-------:|:----------:|:----:|
| `project_number` | WSD11 | T1 | ✓ | 1.0 | ✓ |
| `discipline` | C | T1 | ✓ | 1.0 | ✓ |
| `document_type` | DWG | T1 | ✓ | 1.0 | ✓ |
| `document_number` | 131101-WSW41-DR-C-0001 | T1 | ✓ | 1.0 | ✓ |
| `revision` | T3 | T1 | ✓ | 1.0 | ✓ |
| `asset_tags` | ["P-101"] | T1 | ✓ | 1.0 | ✓ |
| `project_title` | TUAS WRP | T2 | ✓ | 1.0 | — |
| `area` | WSW41 | T2 | ✓ | 1.0 | — |
| `status` | APPROVED | T2 | ✓ | 1.0 | — |
| `created_by` | JS | T2 | ✓ | 1.0 | — |
| `checked_by` | PE | T2 | ✓ | 1.0 | — |
| `approved_by` | — | T2 | ✗ | — | — |
| `originator_company` | CH2M HILL | T2 | ✓ | 1.0 | — |
| `page_count` | 1 | T2 | ✓ | 1.0 | — |
| `department` | — | T3 | ✗ | — | — |
| `security_class` | — | T3 | ✗ | — | — |
| `verified_by` | — | T3 | ✗ | — | — |

| Dimension | Calculation | Score |
|-----------|-------------|:-----:|
| Completeness | 14/18 | 0.78 |
| Extraction Confidence | T1: 6/6×1.0×2.0=12.0, T2: 6/8×1.0×1.0=6.0, T3: 0/3×0.0×0.5=0 → 18.0/18.0 | 1.0 |
| Structural Completeness | 4/4 expected detected (cover, rev table, sections, image) | 1.0 |
| Source Quality | Type A | 1.0 |
| Cross-Reference | 5/5 checks pass | 1.0 |
| Consistency | 0 violations → modifier 1.0 | 1.0 |

```
health_score = (0.78×0.20 + 1.0×0.20 + 1.0×0.20 + 1.0×0.15 + 1.0×0.15 + 1.0×0.10) × 1.0
             = (0.156 + 0.20 + 0.20 + 0.15 + 0.15 + 0.10) × 1.0
             = 0.956
```

**Result**: `extract_status = "success"`, `extraction_confidence = 0.95`

#### Example 2: Type C Document (Low Score)

**Input**: `131101-WIL00-DR-E-7000.pdf` (scanned, no text layer)

| Column | Value | Tier | Present | Confidence | XRef |
|--------|-------|:----:|:-------:|:----------:|:----:|
| `discipline` | E (from filename) | T1 | ✓ | 1.0 | ✓ |
| `project_number` | — | T1 | ✗ | — | — |
| `document_type` | — | T1 | ✗ | — | — |
| `document_number` | — | T1 | ✗ | — | — |
| `revision` | — | T1 | ✗ | — | — |
| `asset_tags` | — | T1 | ✗ | — | — |
| All T2 fields | — | T2 | ✗ | — | — |
| All T3 fields | — | T3 | ✗ | — | — |

| Dimension | Calculation | Score |
|-----------|-------------|:-----:|
| Completeness | 1/18 | 0.06 |
| Extraction Confidence | T1: 1/6×1.0×2.0=2.0, T2: 0, T3: 0 → 2.0/12.0 | 0.17 |
| Structural Completeness | 0/0 expected (Type C: no structure expected) | 1.0 |
| Source Quality | Type C | 0.3 |
| Cross-Reference | 1/1 check pass | 1.0 |
| Consistency | 0 violations → modifier 1.0 | 1.0 |

```
health_score = (0.06×0.20 + 0.17×0.20 + 1.0×0.20 + 0.3×0.15 + 1.0×0.15 + 1.0×0.10) × 1.0
             = (0.012 + 0.034 + 0.20 + 0.045 + 0.15 + 0.10) × 1.0
             = 0.541
```

**Result**: `extract_status = "partial"`, `extraction_confidence = 0.54`, flagged for review

#### Example 3: Type B Document with Inconsistency

**Input**: `16023.pdf` (standard detail, `created_by` = `checked_by`)

| Dimension | Calculation | Score |
|-----------|-------------|:-----:|
| Completeness | 11/18 | 0.61 |
| Extraction Confidence | T1: 4/6×0.8×2.0=6.4, T2: 5/8×0.8×1.0=4.0, T3: 0 → 10.4/16.0 | 0.65 |
| Structural Completeness | 3/4 expected (missing image) | 0.75 |
| Source Quality | Type B | 0.7 |
| Cross-Reference | 3/4 checks pass | 0.75 |
| Consistency | 1 violation (created_by = checked_by) → modifier 0.9 | 0.9 |

```
health_score = (0.61×0.20 + 0.65×0.20 + 0.75×0.20 + 0.7×0.15 + 0.75×0.15 + 1.0×0.10) × 0.9
             = (0.122 + 0.13 + 0.15 + 0.105 + 0.1125 + 0.10) × 0.9
             = 0.7195 × 0.9
             = 0.648
```

**Result**: `extract_status = "partial"`, `extraction_confidence = 0.65`, flagged for review

---

### D7.10 Structural Elements Table (`document_elements`)

Each document in `document_registry` can have multiple structural elements stored in a separate table. This enables Phase 2 section-aware chunking, Phase 3 graph node creation, and Phase 4 structural queries.

**Table schema**:

| Column | Type | Nullable | Description |
|--------|------|:--------:|-------------|
| `doc_id` | VARCHAR | NO | FK → `document_registry.doc_id` |
| `element_type` | VARCHAR | NO | Type of structural element |
| `element_id` | VARCHAR | YES | Page number or location identifier |
| `title` | VARCHAR | YES | Heading, field name, or section title |
| `content` | VARCHAR | YES | Raw text or JSON (for complex structures) |
| `confidence` | DOUBLE | YES | 0.0–1.0 extraction confidence |
| `source` | VARCHAR | NO | Extraction method: `regex`, `ocr`, `heuristic`, `manual` |

**Element types**:

| `element_type` | Source | Content | Phase 2 Use | Phase 3 Use |
|----------------|--------|---------|:-----------:|:-----------:|
| `cover_page` | First page extraction | JSON: fields + values + confidence | Section anchor | Document-type node |
| `revision_table` | Table detection on page 1 | JSON: rows[{rev, date, by, desc}] | Change tracking | Revision nodes |
| `section` | Heading detection (regex `\d+\.\d+`) | Text of heading | Chunk boundary | Section nodes |
| `table` | `page.find_tables()` | HTML or Markdown | Context chunks | Table nodes |
| `image` | `page.get_images()` | Bounding box + page | Skip | Figure nodes |
| `link` | Regex on URLs/file paths | JSON: {url, text, type} | Skip | Reference edges |
| `legend` | Page location + heuristic | Text block | Skip | Legend nodes |
| `note` | Page 1 annotations | Text block | Skip | Annotation nodes |

**CRUD operations** (in `registry.py`):

| Method | Description |
|--------|-------------|
| `store_elements(doc_id, elements: list[dict])` | Insert elements for a document |
| `get_elements(doc_id) -> list[dict]` | Retrieve all elements for a document |
| `get_elements_by_type(doc_id, element_type) -> list[dict]` | Filter by type |
| `delete_elements(doc_id)` | Remove all elements for a document |

**Structural completeness scoring**:

```
expected_elements = {cover_page, revision_table, sections, table, image}
detected_count = count(elements where element_type in expected_elements)
structural_completeness = detected_count / len(expected_elements)
```

Document type expectations:

| Document Type | Expected Elements | Threshold |
|---------------|-------------------|:---------:|
| Type A (standard drawing) | cover_page, revision_table, sections, image | 4 |
| Type B (standard detail) | cover_page, revision_table, sections, image | 4 |
| Type C (scanned) | (none expected) | 0 |
| Type D (volume cover) | cover_page, sections | 2 |
| Type E (specification) | cover_page, sections, table | 3 |

---

## D8. Status Lifecycle

### Document Status States

Each document progresses through a lifecycle during ingestion:

```
NEW ──────► EXTRACTED ──────► REGISTERED ──────► VERIFIED
 │              │                   │                  │
 │ (parse)      │ (extract)         │ (register)       │ (human review)
 │              │                   │                  │
 ▼              ▼                   ▼                  ▼
pending      success/partial    success            verified_by set
```

| State | Meaning | Trigger | Next State |
|-------|---------|---------|------------|
| `NEW` | File discovered, not yet processed | File walk | EXTRACTED |
| `EXTRACTED` | Metadata extracted, not yet registered | Extraction pipeline | REGISTERED |
| `REGISTERED` | In document registry, not yet verified | `register_document()` | VERIFIED |
| `VERIFIED` | Human-validated, project-final | Manual verification (Phase 5) | — |

### Extract Status Values

Stored in `extract_status` column of document registry:

| Value | Meaning | Trigger |
|-------|---------|---------|
| `pending` | Not yet extracted (default) | `register_document()` |
| `success` | All auto-extractable fields populated | Extraction pipeline |
| `partial` | Some fields extracted, some missing | Extraction pipeline |
| `failed` | Extraction failed entirely | Extraction pipeline |

---

## D9. Implementation Files

### Phase 1 — Schema Design (T1.30, T1.31)

| File | Purpose | Pattern Reference |
|------|---------|-------------------|
| `eks/config/schemas/eks_error_code_base.json` | Error code taxonomy definitions | `dcc/config/schemas/error_code_base.json` |
| `eks/config/schemas/eks_error_config.json` | Error code catalog (all system + data codes) | `dcc/config/schemas/system_error_config.json` |
| `eks/config/schemas/eks_message_base.json` | Message schema definitions | `dcc/config/schemas/pipeline_message_base.json` |
| `eks/config/schemas/eks_message_config.json` | Message catalog (all pipeline messages) | `dcc/config/schemas/pipeline_message_config.json` |

### Phase 1 — Engine Modules (T1.32)

| File | Purpose | Pattern Reference |
|------|---------|-------------------|
| `eks/engine/core/error_manager.py` | Error handling utilities (handle_system_error, handle_data_error, fail-fast check) | `dcc/workflow/core_engine/errors/error_manager.py` |
| `eks/engine/core/message_manager.py` | Message catalog lookup, template hydration, verbosity control | `dcc/workflow/utility_engine/console/console_output.py` |
| `eks/engine/core/health_scorer.py` | Per-document 6-dimension health scoring (completeness, confidence, structural, source, xref, consistency) | `dcc/workflow/reporting_engine/core/report_health.py` |
| `eks/engine/core/structure_detector.py` | PDF structural element detection (cover page, revision table, sections, tables, images, links) | — |

---

## D10. References

1. [AGENTS.md §19](../../AGENTS.md) — "Each business logic must have an independent error code defined"
2. [AGENTS.md §12](../../AGENTS.md) — Debugging: tiered logging, debug object, fail-fast
3. [AGENTS.md §8](../../AGENTS.md) — Messaging and errors: status, errors, warnings, data quality
4. [Appendix B](appendix_b_document_registry.md) — Document registry schema (v0.7)
5. [DCC Error Code Pattern](../../dcc/config/schemas/error_code_base.json) — Reference for `P{phase}-{module}-{function}-{id}` format
6. [DCC Pipeline Messages](../../dcc/config/schemas/pipeline_message_base.json) — Reference for message catalog structure
4. [`dcc/config/schemas/error_code_base.json`](../../dcc/config/schemas/error_base.json) — DCC error code taxonomy
5. [`dcc/config/schemas/pipeline_message_base.json`](../../dcc/config/schemas/pipeline_message_base.json) — DCC message schema
6. [`dcc/workflow/core_engine/errors/error_manager.py`](../../dcc/workflow/core_engine/errors/error_manager.py) — DCC error manager
7. [`dcc/workflow/utility_engine/console/console_output.py`](../../dcc/workflow/utility_engine/console/console_output.py) — DCC console messaging
8. [`dcc/workflow/reporting_engine/core/report_health.py`](../../dcc/workflow/reporting_engine/core/report_health.py) — DCC health scoring
9. [`eks/engine/logging/logger.py`](../engine/logging/logger.py) — EKS tiered logger (existing)
10. [appendix_b_document_registry.md](appendix_b_document_registry.md) — Document registry schema (extraction fields)
