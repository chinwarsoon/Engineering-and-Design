# DCC Schema Framework README

This directory contains the core configuration and validation logic for the DCC (Document Control Center) Pipeline. The framework is designed using a **Unified Schema Registry** pattern, enabling strict validation, modular inheritance, and absolute URI-based resolution.

## 1. Architectural Framework

### Unified Schema Registry
All schemas follow a standardized metadata pattern:
- **`$schema`**: Points to `http://json-schema.org/draft-07/schema#`.
- **`$id`**: A unique absolute URI following the pattern `https://dcc-pipeline.internal/schemas/{name}`.
- **Strict Validation**: All key objects use `additionalProperties: false` to prevent configuration drift and ensure data integrity.
- **URI Resolution**: Schemas reference each other using absolute URIs rather than relative paths, allowing the `RefResolver` to walk the dependency tree regardless of file location.

### Design Patterns
- **Fragment Pattern**: Large schemas (like `project_setup.json`) are broken into reusable fragments (base, structure, environment, etc.) to minimize redundancy.
- **Inheritance Pattern**: Fragments are composed using `allOf` and `$ref` to create specialized configurations from base definitions.
- **Dual-Purpose Data Schemas**: Lookup schemas (e.g., `discipline_schema.json`) contain both validation rules (`field_definitions`) and the actual lookup data (`discipline` array), serving as a single source of truth for the engine.

---

## 2. Schema Catalog

### 2.1 Core Infrastructure Schemas
These schemas define the rules for the DCC environment and project distribution.

| File | Purpose | Key Definitions/Properties |
| :--- | :--- | :--- |
| `project_setup.json` | Main entry point for project validation. | `folders`, `root_files`, `schema_files`, `discovery_rules`. |
| `project_setup_base.json` | Reusable types for the setup ecosystem. | `file_entry`, `python_module_entry`, `pattern_rule`. |
| `project_setup_structure.json`| Defines required folder hierarchies. | `folder_entry`, `root_file_entry`. |
| `project_setup_discovery.json`| Rules for auto-registering schema files. | `discovery_rules` (glob-based auto-discovery). |
| `project_setup_dependencies.json`| Python environment and engine requirements. | `engine_dependency`, `dependencies_config`. |

### 2.2 Registry & Orchestration
| File | Purpose | Key Properties |
| :--- | :--- | :--- |
| `master_registry.json` | Global catalog of types and tools. | `document_types`, `tools`, `workflows`, `project_structure`. |

### 2.3 Enhanced Processing Schema
| File | Purpose | Key Components |
| :--- | :--- | :--- |
| `dcc_register_enhanced.json`| The "Brain" of the universal processor. | `parameters`, `column_sequence`, `columns` (nested validation/calc). |

### 2.4 Data Lookup Schemas
These schemas serve as the source of truth for categorical metadata.

| File | URI `$id` | Content Description |
| :--- | :--- | :--- |
| `project_schema.json` | `.../schemas/project` | Valid project codes (e.g., 131242 - TWRP). |
| `facility_schema.json` | `.../schemas/facility` | Facility codes, work areas, and plant area orders. |
| `discipline_schema.json` | `.../schemas/discipline` | Engineering disciplines (A, B, C, I, M, P, S, etc.). |
| `document_type_schema.json` | `.../schemas/document-type` | Standard doc classifications (DR, DS, MS, RT, etc.). |
| `department_schema.json` | `.../schemas/department` | Internal department list (QAQC, CSA, PMT, etc.). |
| `approval_code_schema.json` | `.../schemas/approval-code` | Normalization mapping for status strings to codes. |
| `calculation_strategies.json`| `.../schemas/calculation-strategies`| Definitions for data preservation and null handling. |

### 2.5 Error Handling (Engine) Schemas
Located in `dcc/workflow/processor_engine/error_handling/config/`.

| File | Purpose |
| :--- | :--- |
| `taxonomy.json` | E-M-F-U code hierarchy (Engine-Module-Function-Unique). |
| `error_codes.json` | The master registry of all 30+ potential pipeline errors. |
| `remediation_types.json` | Rules for `AUTO_FIX`, `MANUAL_FIX`, `SUPPRESS`, etc. |
| `suppression_rules.json` | "Wrong but acceptable" scenarios with approval workflows. |
| `status_lifecycle.json` | State machine for error states (OPEN → RESOLVED → ARCHIVED). |
| `approval_workflow.json` | Human-in-the-loop review roles and SLA rules. |

---

## 3. Workflow & Correlation

### Data Flow
1.  **Initiation**: `project_setup.json` verifies the environment and loads fragments.
2.  **Discovery**: `project_setup_discovery.json` scans `config/schemas/` to register active data schemas.
3.  **Resolution**: `RefResolver` parses `$ref` links across files using URI IDs.
4.  **Processing**: `UniversalDocumentProcessor` loads `dcc_register_enhanced.json`, which pulls in data lookups (Step 2.4) for fuzzy matching and validation.
5.  **Error Tracking**: Any failures trigger lookups in `error_codes.json` and follow the `status_lifecycle.json`.

### Key Functions
- **`RefResolver.resolve(schema_uri)`**: Fetches a schema by its `$id` from the internal registry.
- **`SchemaLoader.load_all()`**: Performs recursive drill-down from `project_setup.json`.
- **`Validator.validate_field(value, schema_ref)`**: Cross-validates data against lookup schemas.

## 4. Developer Policy
- **Adding a Schema**: Must include `$schema`, `$id`, and `additionalProperties: false`. Register it in `project_setup.json` or ensure it matches a discovery pattern.
- **Referencing**: Use absolute URIs: `{"$ref": "https://dcc-pipeline.internal/schemas/project-setup-base#/definitions/file_entry"}`.
- **Strictness**: Always define `type: "object"` and explicit `properties` at the top level of new schemas.
