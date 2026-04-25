# Document Control Center (DCC)

Modular data processing pipeline for engineering document management.

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Status** | ✅ ACTIVE |
| **Related** | [Project Structure](PROJECT_STRUCTURE.md) \| [Workflow Docs](workflow/README.md) \| [Agent Rules](../agent_rule.md) |

---

## What is DCC?

A 7-engine pipeline that transforms raw document registers into validated, analysis-ready outputs:

```
Input (Excel) → Validation → Mapping → Processing → Reports (Excel/JSON)
```

**Key capabilities:**
- Multi-engine architecture — [`workflow/README.md`](workflow/README.md)
- 3-tier schema system — [`workplan/schema_processing/README.md`](workplan/schema_processing/README.md)
- 15+ interactive dashboards — [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- Standardized error codes — [`workplan/error_handling/error_handling_taxonomy.md`](workplan/error_handling/error_handling_taxonomy.md)

---

## Quick Start

```bash
# Setup
conda env create -f dcc.yml && conda activate dcc

# Run pipeline
python workflow/dcc_engine_pipeline.py --verbose normal

# View dashboards
python serve.py
```

See [`workflow/README.md`](workflow/README.md) for full setup, CLI options, and troubleshooting.

---

## Documentation

| Topic | File/Path |
|-------|-----------|
| **Architecture & CLI** | [`workflow/README.md`](workflow/README.md) |
| **Folder Structure** | [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) |
| **Error Codes** | [`workplan/error_handling/error_handling_taxonomy.md`](workplan/error_handling/error_handling_taxonomy.md) |
| **User Guides** | [`docs/user_guide/`](docs/user_guide/) |
| **Developer Guides** | [`docs/developer_guide/`](docs/developer_guide/) |
| **Change Log** | [`log/update_log.md`](log/update_log.md) |
| **Issues** | [`log/issue_log.md`](log/issue_log.md) |

---

*Maintained by Engineering Team | Updated 2026-04-25*

