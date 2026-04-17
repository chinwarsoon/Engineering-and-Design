# SchemaDependencyGraph API

The `SchemaDependencyGraph` analyzes the relationships between schemas by scanning for `$ref` keys. It builds a directed graph to manage loading order and detect circular dependencies.

---

## Class: `SchemaDependencyGraph`

```python
class SchemaDependencyGraph:
    def __init__(self, resolver: RefResolver)
```

---

## Key Methods

### `build_graph()`
Scans all schemas registered in the `RefResolver` and builds the dependency adjacency list.
- **Cycle Detection**: Automatically identifies circular reference loops during the build process.

### `get_load_order() -> List[str]`
Performs a **topological sort** on the graph.
- **Returns**: A list of schema names in the order they must be loaded to ensure all dependencies are available before their parents.

### `get_all_dependencies(schema_name: str) -> Set[str]`
Finds every schema referenced directly or indirectly by the target.
- **Recursive**: Traverses the entire subtree from the target node.

---

## Cycle Handling

JSON schemas naturally support circular references (e.g., self-referencing tree structures).
- **Internal Cycles**: Self-references within a single file are ignored by the graph builder to allow recursive definitions.
- **External Cycles**: References between different files that form a loop will raise a `CircularDependencyError` to prevent infinite loading loops.

---

## Integration with SchemaLoader

The `SchemaLoader` uses the graph to optimize the `load_recursive` workflow:
1. It requests the `load_order`.
2. It filters the order to only include schemas relevant to the current request.
3. It loads schemas in that specific sequence, ensuring no `$ref` resolution fails due to a missing component.

---

## Example Usage

```python
from dcc.workflow.schema_engine.loader.dependency_graph import SchemaDependencyGraph

# Initialize graph with resolver
graph = SchemaDependencyGraph(my_resolver)
graph.build_graph()

# Get optimal loading sequence
order = graph.get_load_order()
print(f"Loading order: {order}")

# Check dependencies for a specific schema
deps = graph.get_all_dependencies("dcc_register_config")
```
