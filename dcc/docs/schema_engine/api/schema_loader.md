# SchemaLoader API

The `SchemaLoader` is the primary interface for loading JSON schemas in the DCC Pipeline. It orchestrates the `RefResolver`, `DependencyGraph`, and `SchemaCache` to provide a seamless, recursive loading experience.

---

## Class: `SchemaLoader`

```python
class SchemaLoader:
    def __init__(
        self,
        base_path: str | Path | None = None,
        project_setup_path: str | Path | None = None,
        auto_resolve_refs: bool = True,
        max_recursion_depth: int = 100,
        cache: Optional[SchemaCache] = None
    )
```

### Purpose
Provides a single entry point for schema access. Complies with **agent_rule.md Section 2.3** by using `project_setup.json` as the mandatory catalog for all schema files.

---

## Key Methods

### `load_recursive(schema_name: str, auto_resolve: bool = True) -> Dict[str, Any]`
Loads a schema and all its dependencies in the correct topological order.
- **Args**:
  - `schema_name`: The stem name of the schema (e.g., "project_config").
  - `auto_resolve`: Whether to replace `$ref` keys with their target content.
- **Returns**: Fully expanded JSON object.

### `load_schema(schema_name: str) -> Dict[str, Any]`
Loads a single schema from the base path.
- **Note**: This method uses the multi-level cache. It checks L1, then L2 before hitting the disk.

### `get_schema_dependencies(schema_name: str) -> Set[str]`
Returns the set of all schemas referenced (directly or indirectly) by the target schema.

---

## Core Workflows

### 1. Initialization with Strict Registration
When `project_setup_path` is provided, the loader initializes a `RefResolver` and `SchemaDependencyGraph`. This enables:
- Topological sort for loading order.
- Detection of circular references.
- Pattern-based auto-discovery of schemas.

### 2. Recursive Expansion
The loader doesn't just resolve links; it builds a full dependency tree. If `schema_a` references `schema_b`, calling `load_recursive("schema_a")` ensures that `schema_b` is loaded and cached first.

### 3. Integrated Caching
The loader shares its `SchemaCache` instance with the `RefResolver`. This ensures that if a schema is loaded once during a recursive walk, it is served from memory for all subsequent references in the same session.

---

## Example Usage

```python
from dcc.workflow.schema_engine.loader.schema_loader import SchemaLoader

# 1. Setup loader
loader = SchemaLoader(project_setup_path="dcc/config/schemas/project_config.json")

# 2. Perform deep load
# Automatically handles cross-references between fragments
full_config = loader.load_recursive("dcc_register_config")

# 3. Access resolved data
print(full_config["departments"]["ENT"]["name"]) # Resolved from department_schema.json
```

---

## Best Practices
- **Use `load_recursive`**: Prefer this over `load_schema` for complex schemas that use `$ref`.
- **Provide Cache**: For batch processing, pass a single `SchemaCache` instance to multiple loaders to maximize hits.
- **Absolute Paths**: The loader resolves all relative paths to absolute paths internally to ensure consistency.
