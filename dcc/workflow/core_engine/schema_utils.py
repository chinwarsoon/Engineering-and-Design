"""
Schema Utilities - Shared logic for schema structure resolution.
"""
from typing import Dict, Any

def resolve_schema_root(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve the root of the schema document containing the 'columns' key.
    
    Supports:
    1. New architecture: Top-level 'columns' key.
    2. Legacy architecture: 'enhanced_schema' key containing 'columns'.
    
    Returns the dictionary containing the 'columns' key.
    """
    if not schema_data:
        return {}
    if "columns" in schema_data:
        return schema_data
    return schema_data.get("enhanced_schema", {})
