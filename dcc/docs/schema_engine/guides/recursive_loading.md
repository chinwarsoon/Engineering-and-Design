# Guide: Recursive Schema Loading

Recursive loading is the process of automatically fetching and resolving all dependencies referenced within a JSON schema. This guide explains how to use this feature effectively.

---

## The Problem: Fragmented Schemas
In large systems like the DCC Pipeline, schemas are broken into small, maintainable fragments (e.g., `department_schema.json`, `facility_schema.json`). A main configuration schema might reference dozens of these fragments.

**Manual loading** is tedious and error-prone. **Recursive loading** solves this by walking the tree for you.

---

## How to Use `load_recursive()`

The `SchemaLoader.load_recursive()` method is the entry point for this feature.

### 1. Simple Usage
```python
from dcc.workflow.schema_engine.loader.schema_loader import SchemaLoader

loader = SchemaLoader(project_setup_path="dcc/config/schemas/project_config.json")

# Load and resolve everything automatically
schema = loader.load_recursive("dcc_register_config")
```

### 2. Resolution Modes

#### Full Resolution (`auto_resolve=True`) - Default
The loader replaces every `{"$ref": "..."}` key with the actual content of the referenced schema.
- **Result**: A single, monolithic JSON object with no external links.
- **Use Case**: When you need to validate data against a complete rule set without making further lookups.

#### Dependency-Only (`auto_resolve=False`)
The loader ensures all dependencies are **loaded into the cache**, but leaves the `$ref` keys in the JSON.
- **Result**: A JSON object with `$ref` keys, but the targets are guaranteed to be in memory.
- **Use Case**: For specialized validators that handle `$ref` themselves or for performance-critical path analysis.

---

## Behind the Scenes

When you call `load_recursive("my_schema")`:

1.  **Graph Analysis**: The engine checks the `SchemaDependencyGraph` to find all schemas referenced by "my_schema".
2.  **Topological Sort**: It determines the correct order (e.g., if A refs B, load B first).
3.  **Ordered Load**: It loads each schema in order, putting them into the `SchemaCache`.
4.  **Deep Resolution**: If `auto_resolve` is True, the `RefResolver` performs a recursive walk of the JSON structure, replacing links with data from the cache.

---

## Handling Deep Nesting

The engine supports deep recursion (default limit: 100 levels). If your schema structure is extremely deep, you can increase this limit:

```python
schema = loader.load_recursive("deep_schema", max_depth=200)
```

---

## Best Practices

### Avoid Redundant Loads
The `SchemaLoader` automatically uses the `SchemaCache`. If you need to load multiple schemas in a single script, reuse the same `SchemaLoader` instance.

### Validation Loop
To verify that your entire schema catalog is healthy, use a loop:

```python
for name in loader._registered_schemas:
    try:
        loader.load_recursive(name)
        print(f"✅ {name} is healthy")
    except Exception as e:
        print(f"❌ {name} failed: {e}")
```

### Check for Cycles
While the engine handles self-references, you should avoid circular references between *different* files. If you encounter a `CircularDependencyError`, refactor common definitions into a separate `base` file.
