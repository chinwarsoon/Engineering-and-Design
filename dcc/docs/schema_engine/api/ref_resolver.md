# RefResolver API

The `RefResolver` is the engine responsible for resolving all types of JSON Schema references (`$ref`). It handles the translation of internal URIs to physical file paths and implements custom DCC object-based references.

---

## Class: `RefResolver`

```python
class RefResolver:
    def __init__(
        self,
        project_setup_path: Path,
        schema_directories: List[Path],
        cache: Optional[SchemaCache] = None
    )
```

### Purpose
Implements **Universal Reference Resolution** (agent_rule.md Section 2.4) ensuring that any schema can reference any other schema regardless of its location in the file system.

---

## Key Methods

### `resolve_schema_references(schema_refs: Dict[str, str]) -> Dict[str, Dict[str, Any]]`
Resolves a dictionary of schema fragments (Type 1 Custom DCC Ref).
- **Args**: `schema_refs`: Dict mapping fragment name to relative filename or URI.
- **Returns**: Dict mapping fragment name to the fully loaded and parsed JSON data.

### `resolve_all_refs(data: Any, current_schema: Dict[str, Any], path: str = "", max_depth: int = 100) -> Any`
The core recursive resolution method that walks through any JSON structure (Type 2 & 3 Refs).
- **Args**:
  - `data`: The JSON fragment to scan for `$ref` keys.
  - `current_schema`: The root schema being processed (for relative fragments).
  - `path`: Internal recursion path (breadcrumb).
  - `max_depth`: Prevention for runaway recursion.
- **Returns**: Deeply resolved JSON structure where `$ref` keys are replaced by their target data.

---

## Supported Reference Types

| Type | Format | Example |
| :--- | :--- | :--- |
| **Internal** | String | `{"$ref": "#/definitions/item"}` |
| **URI-based** | String | `{"$ref": "https://dcc-pipeline.internal/schemas/facility_schema"}` |
| **Pointer** | String | `{"$ref": "https://.../schema#/properties/name"}` |
| **Custom Obj** | Object | `{"schema": "facility_schema", "code": "HOS", "field": "name"}` |

---

## Features

### 1. Unified Schema Registry
The resolver scans all registered directories for `$id` declarations. It builds a mapping of permanent URIs to temporary file system paths, allowing schemas to be moved without breaking links.

### 2. Strict Registration
The resolver enforces compliance with **agent_rule.md Section 2.3**. It will only resolve schemas that are either:
- Explicitly listed in the `schema_files` array of `project_setup.json`.
- Automatically discovered via `discovery_rules`.

### 3. Discovery Rules
Supports pattern-based registration in `project_setup.json`:
```json
"discovery_rules": [
    {
        "pattern": "*_schema.json",
        "directory": "config/schemas",
        "category": "validation_schema"
    }
]
```

---

## Error Handling
- `RefResolutionError`: Raised when a `$ref` path is invalid or the target property is missing.
- `SchemaNotRegisteredError`: Raised when attempting to access a schema file that hasn't been cataloged in the project setup.
- `CircularDependencyError`: Managed in conjunction with the `DependencyGraph`.
