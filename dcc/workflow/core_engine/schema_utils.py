"""
Schema Utilities - Shared logic for schema structure resolution.
"""
from typing import Dict, Any


def resolve_schema_root(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve the root of the schema document containing the 'columns' key.

    The current schema architecture stores columns at the top level:
        schema_data['columns']

    Args:
        schema_data: Full resolved schema dictionary.
                     Breadcrumb: SchemaValidator.load_resolved_schema() → here.

    Returns:
        The dictionary that contains the 'columns' key, or an empty dict
        if schema_data is empty or has no 'columns' key.
    """
    if not schema_data:
        return {}
    return schema_data if "columns" in schema_data else {}
