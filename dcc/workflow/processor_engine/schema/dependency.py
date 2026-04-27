"""
The dependency resolution methods, _extract_column_dependencies and _find_cycle_path, 
which currently handle circular dependency detection, will reside here.
"""

import logging
from typing import Dict, List, Set, Optional

# Import hierarchical logging functions from utility_engine
from utility_engine.console import status_print, debug_print

def resolve_calculation_order(columns: Dict[str, Dict]) -> List[str]:
    """
    Validates that calculated columns can be processed in schema order.
    Ensures no circular dependencies and no forward-references.

    Args:
        columns: The dictionary of column definitions from the schema.

    Returns:
        A list of column names in the order they should be calculated.

    Raises:
        ValueError: If a circular dependency or order violation is detected.
    """
    # 1. Identify which columns actually require calculation
    calculated_columns = [
        name for name, definition in columns.items()
        if definition.get('is_calculated', False)
    ]

    # 2. Build the dependency graph
    dependency_graph: Dict[str, Set[str]] = {
        name: {
            dep for dep in _extract_column_dependencies(name, columns[name], columns)
            if columns.get(dep, {}).get('is_calculated', False)
        }
        for name in calculated_columns
    }

    # 3. Check for circular dependencies (e.g., A -> B -> A)
    cycle = _find_cycle_path(dependency_graph)
    if cycle:
        raise ValueError(
            f"Circular calculated-column dependency detected: {' -> '.join(cycle)}"
        )

    # 4. Check for schema order violations
    # A column cannot depend on a column that appears later in the schema list.
    original_index = {name: idx for idx, name in enumerate(columns.keys())}
    schema_order_violations = []
    
    for column_name, deps in dependency_graph.items():
        later_dependencies = [
            dep for dep in deps
            if original_index.get(dep, -1) > original_index.get(column_name, -1)
        ]
        if later_dependencies:
            schema_order_violations.append(
                f"{column_name} depends on later calculated columns {later_dependencies}"
            )

    if schema_order_violations:
        raise ValueError(
            "Schema column processing order violation detected. "
            "A column cannot depend on a later schema column. "
            + " | ".join(schema_order_violations)
        )

    status_print(f"Validated calculation sequence for {len(calculated_columns)} columns.", min_level=3)
    return calculated_columns

def _extract_column_dependencies(column_name: str, column_def: Dict, all_columns: Dict) -> Set[str]:
    """
    Scans a column definition to find other columns it relies on.
    """
    dependencies = set()
    calculation = column_def.get('calculation', {})

    # Keys that usually contain lists of columns
    dependency_keys = ['dependencies', 'source_columns', 'group_by', 'sort_by']
    # Keys that usually contain a single column name
    scalar_keys = ['source_column', 'target_column']

    for key in dependency_keys:
        value = calculation.get(key, [])
        if isinstance(value, list):
            dependencies.update(value)

    for key in scalar_keys:
        value = calculation.get(key)
        if isinstance(value, str):
            dependencies.add(value)

    # Remove self-references (they are treated as input seeds, not recursive dependencies)
    dependencies.discard(column_name)

    return {dep for dep in dependencies if dep in all_columns}

def _find_cycle_path(dependency_graph: Dict[str, Set[str]]) -> List[str]:
    """
    Depth-First Search (DFS) to detect if any cycles exist in the graph.
    """
    visiting = set()
    visited = set()
    stack: List[str] = []

    def dfs(node: str) -> List[str]:
        visiting.add(node)
        stack.append(node)

        for dep in dependency_graph.get(node, set()):
            if dep in visiting:
                cycle_start = stack.index(dep)
                return stack[cycle_start:] + [dep]
            if dep not in visited:
                cycle = dfs(dep)
                if cycle:
                    return cycle

        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in dependency_graph:
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                return cycle

    return []
