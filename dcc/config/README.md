# dcc/config README

This folder contains configuration definitions used by the DCC project processing workflows. Only `dcc/config/schemas/*.json` files are used by runtime flows; `dcc/config/schemas/backup/` is intentionally excluded from this summary and should be treated as archival backup data.

## Schema files

### `approval_code_schema.json`
- Purpose: Normalize approval status text variations into standardized codes.
- Structure:
  - `schema_name`: approval_code_schema
  - `type`: status_to_code_mapping
  - `approval`: array of objects with `code`, `status`, and `aliases`
  - `description`, `created`, `version`

### `department_schema.json`
- Purpose: Define accepted department classifications for DCC metadata fields.
- Structure:
  - `schema_name`: department_choices
  - `type`: standard_choices
  - `choices`: allowed department values (Project, QAQC, Contract, etc.)
  - `description`, `created`, `version`

### `discipline_schema.json`
- Purpose: Define accepted discipline classifications for DCC metadata fields.
- Structure:
  - `schema_name`: discipline_choices
  - `type`: standard_choices
  - `choices`: allowed discipline values (Process, Piping, Civil, Structural, etc.)
  - `description`, `created`, `version`

### `document_type_schema.json`
- Purpose: Define accepted document type classifications for DCC metadata fields.
- Structure:
  - `schema_name`: document_type_choices
  - `type`: standard_choices
  - `choices`: allowed document type values (Drawing, Specification, Report, Calculation, etc.)
  - `description`, `created`, `version`

### `master_registry.json`
- Purpose: Top-level registry for document types, tools, workflows, documentation and project structure.
- Notes:
  - `document_types` maps document type IDs (`DCC_SUBMITTAL`, `DCC_SUBMITTAL_ENHANCED`, `RFI_TRACKER`) to schema paths and descriptions.
  - `tools`, `workflows`, `documentation` provide metadata for orchestration utilities and notebooks.
  - `project_structure` enforces required folders and schema files for environment validation.
  - `environment` links to `dcc.yml` with setup and activation instructions.

## Naming and update policy
- If you rename a document type key (e.g., `DCC_SUBMITTAL_ENHANCED`), update all references in `dcc/workflow/*` code and notebooks (search for `registry['document_types']["..."`] and `registry.get(...)`).
- Do not edit files under `config/schemas/backup/`; they are historical snapshots and not part of active runtime schema loading.

## How to use
1. Ensure environment is active:
   - `conda activate dcc` (after `conda env create/update -f dcc.yml`)
2. Load and validate schemas via tooling in `dcc/tools` and `dcc/workflow`.
3. Update the corresponding JSON schema list in `master_registry.json` when adding a new document type or schema file.
