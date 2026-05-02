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
  - `dcc_parameters`: Moved from project_setup_base; contains register-specific parameters (renamed from global_parameters per naming convention).
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
  - `dcc_parameters` (renamed from global_parameters).
  - `dcc_register_enhanced` (later deleted after migration).

---

## Phase 1.6: Create `dcc_register_config.json`
**Objective**: Consolidate actual data values for the register layer.

### Items to be defined:
- **ID**: `https://dcc-pipeline.internal/schemas/dcc-register-config`
- **Source of Data**:
  - `column_sequence`, `column_groups`: Migrated from `column_configuration.json`.
  - `dcc_parameters`: Extracted actual values (renamed from global_parameters).
  - References to fragment schemas for `departments`, `disciplines`, etc.
- **Cleanup**:
  - Archive `column_configuration.json` (Moved to `archive/`).

---

## Phase 2: Refactor `project_setup_base.json` - **COMPLETED**
**Objective**: Strip data-specific definitions to leave a lean infrastructure schema.

### Items Removed:
- [x] `dcc_parameters` (moved to dcc_register_base, renamed from global_parameters)
- [x] `column_types`, `validation_patterns`, `null_handling_strategies` (moved to dcc_register_base)
- [x] `department_entry`, `discipline_entry`, `facility_entry`, `document_type_entry`, `project_entry` (moved to dcc_register_base)

### Items Retained:
- [x] `file_entry`, `typed_file_entry`, `python_module_entry`, `path_entry`, `folder_entry`, `root_file_entry`.
- [x] `pattern_rule`, `validation_rule`, `validation_rule_entry`.
- [x] `dependency_entry`, `engine_dependency`, `dependencies_config`, `environment_entry`, `engine_entry`.
- [x] `project_metadata`, `schema_registry`.

---

## Phase 3: Refactor `project_setup.json` - **COMPLETED**
**Objective**: Remove register-specific properties and focus strictly on infrastructure.

### Items Removed:
- [x] `departments`, `disciplines`, `facilities`, `document_types`, `projects`.
- [x] `column_types`, `column_patterns`, `column_strategies`.
- [x] `column_groups`, `column_sequence`.
- [x] `dcc_register_enhanced` (deleted after migration), `dcc_parameters` (renamed from global_parameters).

### Items Retained:
- [x] `folders`, `root_files`, `schema_files`, `discovery_rules`.
- [x] `workflow_files`, `tool_files`, `processor_engine`, `mapper_engine`, etc.
- [x] `environment`, `validation_rules`, `dependencies`, `registry`, `project_metadata`.

---

## Phase 4: Update Data Schemas - **COMPLETED**
**Objective**: Align individual lookup schemas with the new register base.

### Files Modified:
- [x] `department_schema.json`
- [x] `discipline_schema.json`
- [x] `facility_schema.json`
- [x] `document_type_schema.json`
- [x] `project_code_schema.json`

### Change:
- [x] Updated `allOf` references from `project-setup-base` to `dcc-register-base`.

---

## Phase 5: Verification - **COMPLETED**
**Objective**: Ensure URI resolution and schema integrity.

### Validation Results:
- [x] Verified `$id` uniqueness across all schemas.
- [x] Checked all `$ref` URI resolution - all valid.
- [x] Confirmed zero duplicate definitions and properties.
- [x] Confirmed `dcc_register_enhanced.json` properly migrated and deleted.
- [x] Confirmed infrastructure/data separation achieved.

---

## Phase 6: Cleanup Summary - **COMPLETED**
**Objective**: Document the completed decoupling work.

### Cleanup Results:
- **Duplicates Removed**: 12 total (1 definition + 11 properties)
- **Infrastructure Schema (project_setup_base)**: 15 definitions retained
- **Data Schema (dcc_register_base)**: 10 definitions properly located
- **Infrastructure Properties (project_setup)**: 16 properties retained
- **Data Properties (dcc_register_setup)**: 12 properties properly located

### Architecture Compliance:
- **Success Criteria 1**: `project_setup_base.json` contains ZERO data-column or classification definitions - **ACHIEVED**
- **Success Criteria 2**: `dcc_register_base.json` acts as the single source of truth for all register data structures - **ACHIEVED**
- **Success Criteria 3**: All schema cross-references are updated and valid - **ACHIEVED**

---

## Success Criteria - **ALL ACHIEVED**
1. [x] `project_setup_base.json` contains ZERO data-column or classification definitions.
2. [x] `dcc_register_base.json` acts as the single source of truth for all register data structures.
3. [x] All schema cross-references are updated and valid.

---

## Project Status: **DECOUPLING COMPLETE**
**Date Completed**: 2026-04-16
**Total Phases**: 6/6 Completed
**Architecture State**: Infrastructure and Data properly separated
**Next Steps**: All subsequent work complete (Phase 10 testing ✅, schema_consolidation ✅). Architecture stable.
