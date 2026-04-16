# Workplan: Register Definition Decoupling

## Overview
This workplan details the architectural decoupling of **Project Infrastructure** (Setup) from **Data Column Requirements** (Register). We will move all register-specific definitions from `project_setup_base.json` into a new `dcc_register_base.json` to create a specialized foundation for document control registers.

## Target Architecture

### 1. `project_setup_base.json` (Infrastructure Base)
Focus: Files, Folders, Paths, Dependencies, and Global System Parameters.

### 2. `dcc_register_base.json` (Register Base - NEW)
Focus: Data Column Types, Validation Patterns, Null Handling, and Domain Classifications (Facility, Discipline, etc.).

---

## Phase 1: Create `dcc_register_base.json`
**Objective**: Establish the new foundation for data-centric definitions.

### Items to be defined:
- **ID**: `https://dcc-pipeline.internal/schemas/dcc-register-base`
- **Definitions to Create/Move**:
  - `department_entry`: Department code and description validation.
  - `discipline_entry`: Engineering discipline code and description validation.
  - `facility_entry`: Comprehensive facility/building metadata structure.
  - `document_type_entry`: Document type code and description validation.
  - `project_entry`: Project code and description validation.
  - `column_types`: Reusable logic for ID, Code, Date, Sequence, and Status columns.
  - `validation_patterns`: Pattern, Schema, and Range validation logic.
  - `null_handling_strategies`: Forward fill and multi-level filling logic.
  - `global_parameters`: Moved from project_setup_base; contains register-specific parameters.
  - `column_groups_entry`: Structural definition for logical column groupings.
  - `column_sequence_entry`: Structural definition for column processing sequence.

---

## Phase 1.5: Create `dcc_register_setup.json`
**Objective**: Establish the structure for register-specific properties.

### Items to be defined:
- **ID**: `https://dcc-pipeline.internal/schemas/dcc-register-setup`
- **Inheritance**: `allOf` pointing to `dcc-register-base`.
- **Properties to Move from `project_setup.json`**:
  - `departments`, `disciplines`, `facilities`, `document_types`, `projects`.
  - `column_types`, `column_patterns`, `column_strategies`.
  - `column_groups`, `column_sequence`.
  - `global_parameters`.
  - `dcc_register_enhanced`.

---

## Phase 1.6: Create `dcc_register_config.json`
**Objective**: Consolidate actual data values for the register layer.

### Items to be defined:
- **ID**: `https://dcc-pipeline.internal/schemas/dcc-register-config`
- **Source of Data**:
  - `column_sequence`, `column_groups`: Migrated from `column_configuration.json`.
  - `global_parameters`: Extracted actual values.
  - References to fragment schemas for `departments`, `disciplines`, etc.
- **Cleanup**:
  - Archive `column_configuration.json` (Moved to `archive/`).

---

## Phase 2: Refactor `project_setup_base.json`
**Objective**: Strip data-specific definitions to leave a lean infrastructure schema.

### Items to Remove:
- `department_entry`, `discipline_entry`, `facility_entry`, `document_type_entry`, `project_entry`.
- `column_types`, `validation_patterns`, `null_handling_strategies`.

### Items to Retain:
- `file_entry`, `typed_file_entry`, `python_module_entry`, `path_entry`, `folder_entry`, `root_file_entry`.
- `pattern_rule`, `validation_rule`, `validation_rule_entry`.
- `dependency_entry`, `engine_dependency`, `dependencies_config`, `environment_entry`, `engine_entry`.
- `project_metadata`, `schema_registry`, `global_parameters`.

---

## Phase 3: Refactor `project_setup.json`
**Objective**: Remove register-specific properties and focus strictly on infrastructure.

### Items to Remove:
- `departments`, `disciplines`, `facilities`, `document_types`, `projects`.
- `column_types`, `column_patterns`, `column_strategies`.
- `column_groups`, `column_sequence`.
- `dcc_register_enhanced`.

### Items to Retain:
- `folders`, `root_files`, `schema_files`, `discovery_rules`.
- `workflow_files`, `tool_files`, `processor_engine`, `mapper_engine`, etc.
- `environment`, `validation_rules`, `dependencies`, `registry`, `project_metadata`, `global_parameters`.

---

## Phase 4: Update Data Schemas
**Objective**: Align individual lookup schemas with the new register base.

### Files to Modify:
- `department_schema.json`
- `discipline_schema.json`
- `facility_schema.json`
- `document_type_schema.json`
- `project_code_schema.json`

### Change:
- Update `allOf` references from `project-setup-base` to `dcc-register-base`.

---

## Phase 5: Verification
**Objective**: Ensure URI resolution and schema integrity.

### Validation Tasks:
- [ ] Verify `$id` uniqueness.
- [ ] Check all `$ref` URI resolution.
- [ ] Run `jsonschema` validation against `project_config.json`.
- [ ] Verify `dcc_register_enhanced.json` inherited properties remain valid.

---

## Success Criteria
1. `project_setup_base.json` contains ZERO data-column or classification definitions.
2. `dcc_register_base.json` acts as the single source of truth for all register data structures.
3. All schema cross-references are updated and valid.
