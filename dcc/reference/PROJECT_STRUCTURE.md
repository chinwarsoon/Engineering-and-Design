# DCC Project Structure & Required Files

> **Last Updated:** March 29, 2026  
> **Purpose:** Distribution checklist for DCC (Document Control Center) project

## Quick Setup

```bash
# 1. Create conda environment
conda env create -f dcc.yml
conda activate dcc

# 2. Validate project structure
python tools/project_setup_tools.py validate_structure

# 3. Run main workflow
jupyter notebook workflow/dcc_register_processor_main.ipynb
```

---

## Folder Structure Overview

```
dcc/
├── config/
│   └── schemas/              # JSON schema definitions
├── data/                     # Input Excel files
├── output/                   # Generated outputs (auto-created)
├── reference/                # Documentation & guides
├── tools/                    # Setup & utility scripts
└── workflow/                 # Main processing notebooks & modules
```

---

## Detailed File Requirements

### 📁 `config/schemas/` - Schema Definitions

| File | Required | Size | Purpose |
|------|----------|------|---------|
| `dcc_register_enhanced.json` | ✅ Yes | ~56KB | Main schema with column definitions, aliases, null handling |
| `department_schema.json` | ✅ Yes | ~454B | Department validation rules |
| `discipline_schema.json` | ✅ Yes | ~379B | Discipline validation rules |
| `document_type_schema.json` | ✅ Yes | ~350B | Document type validation rules |
| `approval_code_mapping.json` | ✅ Yes | ~763B | Status code mappings (APP, REJ, PEN, etc.) |

**Dependencies:**
- `dcc_register_enhanced.json` references all other schema files
- Used by: `universal_document_processor.py`, `universal_column_mapper.py`

---

### 📁 `data/` - Input Data Files

| File | Required | Purpose |
|------|----------|---------|
| `*.xlsx` | ⚠️ At least 1 | Excel files with raw submission data |

**Expected Excel Structure:**
- Sheet name: `"Prolog Submittals "` (with trailing space)
- Header row: Row 4 (0-indexed: `header_row=4`)
- Column range: `P:AP` (configurable)

**Sample Data File:**
- `Submittal and RFI Tracker Lists.xlsx` (4.1MB)

---

### 📁 `reference/` - Documentation (Optional but Recommended)

| File Type | Purpose |
|-----------|---------|
| `README.md` | Project overview and quick start |
| `USAGE.md` | Detailed usage instructions |
| `SCHEMA.md` | Schema documentation |
| `TROUBLESHOOTING.md` | Common issues & solutions |
| `project-plan.md` | Project roadmap |

**Existing Documentation:**
- `traceability.md` - Complete workflow traceability
- `traceability_simple.md` - Simplified traceability
- `class-based-events.md` - Event documentation
- `dynamic-elements-events.md` - Dynamic UI events

---

### 📁 `tools/` - Setup & Utilities

| File | Required | Purpose |
|------|----------|---------|
| `project_setup_tools.py` | ✅ Yes | **Main validation tool** - Checks all required files and folders |

**Usage:**
```bash
# Complete project validation
python tools/project_setup_tools.py validate_structure

# Or run all checks
python tools/project_setup_tools.py complete
```

**Functions:**
- `validate_project_structure()` - Validates folders, files, schemas
- `analyze_columns()` - Compares Excel columns vs schema
- `check_workflow_dependencies()` - Checks Python imports
- `reorganize_schema_columns()` - Reorders schema columns

---

### 📁 `workflow/` - Main Processing

| File | Required | Size | Purpose |
|------|----------|------|---------|
| `dcc_register_main.ipynb` | ✅ Yes | ~85KB | **Main orchestration notebook** - Step-by-step processing |
| `universal_document_processor.py` | ✅ Yes | ~25KB | Schema-driven processing engine |
| `universal_column_mapper.py` | ✅ Yes | ~20KB | Fuzzy column name mapping |

**Additional Notebooks (Optional):**
- `dcc_mdl.ipynb` - Original processing workflow
- `common_json_tools.ipynb` - JSON utilities
- `pdf_transmittal_extraction.ipynb` - PDF processing

**Workflow Documentation:**
- `explaination/` folder contains detailed workflow guides
- `universal-column-mapping-workflow.md`
- `universal-document-processing-workflow.md`
- `universal-processing-workflow.md` (with Mermaid diagrams)

---

### 📁 Root Level Files

| File | Required | Purpose |
|------|----------|---------|
| `dcc.yml` | ✅ Yes | **Conda environment** - Python 3.13 + all dependencies |
| `README.md` | ⚠️ Recommended | Top-level project overview |

**Environment Dependencies:**
```yaml
Key Packages:
  - python=3.13
  - pandas (data processing)
  - numpy (numerical ops)
  - matplotlib, seaborn (visualization)
  - jupyter, ipykernel (notebooks)
  - duckdb (analytics)
  - openpyxl (Excel I/O)
```

---

## File Dependencies Map

```
dcc_register_main.ipynb
    ├── universal_column_mapper.py
    │   └── config/schemas/dcc_register_enhanced.json
    └── universal_document_processor.py
        └── config/schemas/dcc_register_enhanced.json
            ├── department_schema.json
            ├── discipline_schema.json
            ├── document_type_schema.json
            └── approval_code_mapping.json
```

---

## Validation Checklist

Use `project_setup_tools.py` to verify:

- [ ] ✅ All 6 required folders exist
- [ ] ✅ All 5 schema JSON files exist
- [ ] ✅ All 3 workflow files exist
- [ ] ✅ `dcc.yml` environment file exists
- [ ] ✅ At least 1 `.xlsx` data file in `data/`
- [ ] ✅ Schema references valid (no broken links)

**Run validation:**
```bash
python tools/project_setup_tools.py validate_structure
```

---

## Distribution Package Contents

**Minimum files required for distribution:**

```
dcc/
├── dcc.yml                      # Environment specification
├── config/schemas/              # 5 JSON schema files
├── data/                        # Excel input files
├── output/                      # Empty folder (created on run)
├── reference/                   # Documentation (optional)
├── tools/
│   └── project_setup_tools.py  # Validation script
└── workflow/
    ├── dcc_register_main.ipynb   # Main notebook
    ├── universal_document_processor.py
    └── universal_column_mapper.py
```

**Total size:** ~5-10MB (excluding data files)

---

## Configuration Files

### `master_registry.json`
- **Location:** `config/schemas/master_registry.json`
- **Purpose:** Central registry of all tools, workflows, and project structure
- **Sections:**
  - `document_types` - Schema file mappings
  - `tools` - Available Python tools with functions
  - `workflows` - Notebook and workflow documentation
  - `project_structure` - Required folders and files for validation
  - `environment` - Conda environment specification

---

## Common Issues

### Missing `dcc.yml`
**Error:** Users cannot recreate the Python environment  
**Fix:** Include `dcc.yml` in distribution root

### Missing Schema References
**Error:** `FileNotFoundError` for `department_schema.json` etc.  
**Fix:** Ensure all 5 schema files are in `config/schemas/`

### Excel File Not Found
**Error:** `FileNotFoundError` when loading data  
**Fix:** Place `.xlsx` files in `data/` folder

### Wrong Sheet Name
**Error:** `ValueError: Worksheet named 'Prolog Submittals' not found`  
**Note:** Sheet name has trailing space: `"Prolog Submittals "`

---

## Maintenance Notes

**When adding new columns to schema:**
1. Update `dcc_register_enhanced.json`
2. Update `project_setup_tools.py` → `new_sequence` list
3. Run `python tools/project_setup_tools.py reorganize` to reorder

**When distributing to new users:**
1. Run `validate_structure` to check completeness
2. Ensure `reference/` folder has usage documentation
3. Verify `dcc.yml` has all required dependencies

---

## Contact & Support

- **Validation Tool:** `python tools/project_setup_tools.py complete`
- **Schema Issues:** Check `config/schemas/` folder contents
- **Workflow Issues:** Review `workflow/explaination/*.md` guides
