# Appendix B — Document Registry

**Version**: 0.5  
**Last Updated**: 2026-06-16  
**Phase**: 1 — Foundation  
**Status**: ✅ Implemented & Tested  
**Related Files**:
- [`eks/engine/core/registry.py`](../engine/core/registry.py)
- [`eks/engine/core/revision.py`](../engine/core/revision.py)
- [`eks/engine/core/config_registry.py`](../engine/core/config_registry.py)
- [`eks/config/eks_config.json`](../config/eks_config.json)
- [`eks/config/eks_base_schema.json`](../config/eks_base_schema.json)

---

## B1. Overview

The Document Registry is the central metadata store for all engineering documents ingested into EKS. It is backed by DuckDB (configurable to PostgreSQL) and managed through the `DocumentRegistry` class in `engine/core/registry.py`. It records every document revision that enters the system, tracks which revision is current (`is_latest`), and provides filtered query access for the retrieval pipeline.

The registry is config-driven — the DB path and backend type are read from `eks_config.json` at startup via `ConfigRegistry`. No hardcoded paths or connection strings exist in the implementation.

---

## B2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   DocumentRegistry                        │
│                  (registry.py)                           │
│                                                          │
│  COLUMN_ALLOWLIST = {...}                                │
│                                                          │
│  __init__(logger)                                        │
│    └─ ConfigRegistry() ──► eks_config.json               │
│    └─ _init_db() ──► CREATE TABLE IF NOT EXISTS docs     │
│    └─ _migrate_schema() ──► ALTER TABLE (G1 + Ext Meta)  │
│                                                          │
│  register_document(metadata) ──► doc_id                  │
│    └─ UPDATE is_latest = FALSE                           │
│    └─ json.dumps(asset_tags) if list                     │
│    └─ INSERT OR REPLACE                                  │
│                                                          │
│  get_document(doc_number, revision=None) ──► dict|None   │
│                                                          │
│  list_documents(filters, latest_only, order_by) ──► list │
│    └─ COLUMN_ALLOWLIST validation for keys/order_by      │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│                   RevisionManager                         │
│                  (revision.py)                           │
│                                                          │
│  get_revision_history(document_number) ──► list[dict]    │
│    └─ list_documents(order_by="ingested_at DESC")        │
│    └─ sorted at SQL level (G3 Fix ✅)                    │
└──────────────────────────────────────────────────────────┘
```

---

## B3. Database Schema

**Table**: `documents`  
**Backend**: DuckDB (`data/eks_registry.db`) — configurable to PostgreSQL  
**Created by**: `_init_db()` on first instantiation (`CREATE TABLE IF NOT EXISTS`)

| Group | Column | Type | Nullable | Default | Description |
| :--- | :----- | :--- | :------: | :------ | :---------- |
| **Identity** | `id` | VARCHAR | NOT NULL | — | Primary key. Format: `{doc_num}-{rev}` |
| | `source_type` | VARCHAR | YES | 'ingested' | Source: `ingested`, `referenced`, `stub` (G1 ✅) |
| **Project** | `project_title` | VARCHAR | YES | NULL | Project full name |
| | `project_number` | VARCHAR | YES | NULL | Project code e.g. `WSD11` |
| | `area` | VARCHAR | YES | NULL | Plant area or zone |
| | `discipline` | VARCHAR | YES | NULL | Engineering discipline code (PI, EL, etc.) |
| | `department` | VARCHAR | YES | NULL | Originating department |
| **Document** | `document_type` | VARCHAR | YES | NULL | Document type code (DWG, SPC, RPT, etc.) |
| | `document_number` | VARCHAR | YES | NULL | Document identifier |
| | `revision` | VARCHAR | YES | NULL | Revision identifier (A, B, 0, 1, etc.) |
| | `status` | VARCHAR | YES | NULL | Workflow status (APPROVED, IFR, IFC, etc.) |
| | `is_latest` | BOOLEAN | YES | TRUE | TRUE for current active revision only |
| | `file_path` | VARCHAR | YES | NULL | Relative path to source file |
| | `ingested_at` | TIMESTAMP | YES | CURRENT_TIMESTAMP | UTC timestamp of ingestion |
| **Account** | `created_by` | VARCHAR | YES | NULL | Author (Auto-extracted) |
| | `checked_by` | VARCHAR | YES | NULL | Reviewer (Auto-extracted) |
| | `approved_by` | VARCHAR | YES | NULL | Approver (Auto-extracted) |
| **Origin** | `originator_company`| VARCHAR | YES | NULL | Producing company (Auto-extracted) |
| | `security_class` | VARCHAR | YES | NULL | Security classification (Manual) |
| | **`asset_tags`** | **VARCHAR** | YES | NULL | **List of asset tags found (e.g. `["P-101", "V-202"]`). Stored as a JSON-serialized string in DuckDB VARCHAR column. Python lists are auto-serialized via `json.dumps()` on write and deserialized via `json.loads()` on read. DuckDB's native JSON type is not used to maintain PostgreSQL compatibility.** |
| **Technical** | `page_count` | INTEGER | YES | NULL | Total pages (Auto-extracted) |
| **Quality** | `extract_status` | VARCHAR | YES | 'pending' | Enum: `pending`, `success`, `partial`, `failed` |
| | `extraction_confidence`| DOUBLE | YES | NULL | Confidence score (0.0 - 1.0) |
| | `extraction_notes` | TEXT | YES | NULL | Extraction logs or failure reasons |
| | `verified_by` | VARCHAR | YES | NULL | Name of manual validator |

**Primary key**: `id` (`{document_number}-{revision}`) — guarantees one row per document+revision pair.

---

## B4. Function Reference

### B4.1 `DocumentRegistry.__init__(logger)`

Initialises the registry. Implements **Automatic Schema Migration**: checks for missing columns (e.g. `source_type` or extended metadata) and executes `ALTER TABLE` to upgrade existing databases without data loss.

### B4.2 `DocumentRegistry.register_document(metadata) → str`

Registers a new revision. If keys like `asset_tags` are provided as Python lists, the registry automatically serializes them to JSON strings (`json.dumps()`) for storage in the VARCHAR column. On read, callers receive the raw JSON string and should deserialize with `json.loads()` if a list is needed.

**Metadata Keys (Extended):**
- `source_type`: `ingested`, `referenced`, `stub`
- `asset_tags`: List of strings — auto-serialized to JSON string on write (e.g. `'["P-101", "V-202"]'`)
- `extract_status`: `pending` (default), `success`, `partial`, `failed`
- `extraction_confidence`: Float 0.0 - 1.0
- `verified_by`: String (null until manual verification)

---

## B5. Extraction & Verification Workflow

The extended metadata fields support a hybrid automated/manual workflow implemented across Phase 3 and Phase 5.

1.  **Automated Extraction (Phase 3)**:
    *   The Ingestion Engine uses LLM/Regex logic to extract cover sheet metadata.
    *   Fields `created_by`, `originator_company`, `asset_tags`, and `page_count` are populated.
    *   `extract_status` is set to `success` or `partial`.
    *   `extraction_confidence` is recorded.
2.  **Manual Verification (Phase 5)**:
    *   Users access the "Manual Verification Dashboard" in the EKS UI.
    *   Auto-extracted values are presented for review.
    *   User sets `security_class` and corrects any auto-extracted errors.
    *   Upon submission, the UI sets `verified_by` to the current user's name.
    *   A record is considered "Project Final" only when `verified_by` is NOT NULL.

---

## B6. References

1. [`registry.py`](../engine/core/registry.py) — DocumentRegistry implementation
2. [Phase 1 Foundation Workplan](phase_1_foundation_workplan.md) — T1.21, T1.22
3. [Phase 3 Knowledge Graph Workplan](phase_3_knowledge_graph_workplan.md) — T3.21 (Extraction)
4. [Phase 5 UI Integration Workplan](phase_5_ui_integration_workplan.md) — T5.18 (Verification UI)