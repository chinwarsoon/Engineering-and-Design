"""
Utility functions for filtering and processing trace data.
"""

import os
import sys
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path


def should_trace_file(filename: str, 
                     include_paths: Optional[List[str]] = None,
                     exclude_paths: Optional[List[str]] = None,
                     exclude_stdlib: bool = True) -> bool:
    """
    Determine if a file should be traced based on inclusion/exclusion rules.
    
    Args:
        filename: Path to the file
        include_paths: List of path prefixes to include (None = include all)
        exclude_paths: List of path prefixes to exclude (None = exclude none)
        exclude_stdlib: Whether to exclude standard library files
        
    Returns:
        True if the file should be traced
    """
    # Convert to absolute path for consistent comparison
    abs_filename = os.path.abspath(filename)
    
    # Check exclusion paths first
    if exclude_paths:
        for exclude_path in exclude_paths:
            abs_exclude = os.path.abspath(exclude_path)
            if abs_filename.startswith(abs_exclude):
                return False
    
    # Check inclusion paths
    if include_paths:
        for include_path in include_paths:
            abs_include = os.path.abspath(include_path)
            if abs_filename.startswith(abs_include):
                break
        else:  # No break occurred, meaning no include path matched
            return False
    
    # Exclude standard library if requested
    if exclude_stdlib:
        # Check if it's in Python's standard library
        if abs_filename.startswith(sys.prefix):
            # Allow tracing of site-packages or user-specific paths
            site_prefix = os.path.join(sys.prefix, 'site-packages')
            if not abs_filename.startswith(site_prefix):
                # Also check for dist-packages (Debian/Ubuntu)
                dist_prefix = os.path.join(sys.prefix, 'dist-packages')
                if not abs_filename.startswith(dist_prefix):
                    return False
    
    return True


def filter_trace_data(trace_data: Dict[str, Any],
                     include_paths: Optional[List[str]] = None,
                     exclude_paths: Optional[List[str]] = None,
                     exclude_stdlib: bool = True) -> Dict[str, Any]:
    """
    Filter trace data based on file paths.
    
    Args:
        trace_data: Raw trace data from trace engine
        include_paths: List of path prefixes to include
        exclude_paths: List of path prefixes to exclude
        exclude_stdlib: Whether to exclude standard library files
        
    Returns:
        Filtered trace data
    """
    filtered_calls = {}
    filtered_tree = []
    
    # Filter calls
    for call_id, call_data in trace_data.get('calls', {}).items():
        filename = call_data.get('filename', '')
        if should_trace_file(filename, include_paths, exclude_paths, exclude_stdlib):
            filtered_calls[call_id] = call_data
    
    # Filter call tree (recursively)
    def filter_tree_node(node):
        filename = node.get('filename', '')
        if should_trace_file(filename, include_paths, exclude_paths, exclude_stdlib):
            # Filter children recursively
            filtered_children = [
                filter_tree_node(child) 
                for child in node.get('children', [])
                if filter_tree_node(child) is not None
            ]
            node_copy = node.copy()
            node_copy['children'] = filtered_children
            return node_copy
        return None
    
    for root_node in trace_data.get('call_tree', []):
        filtered_root = filter_tree_node(root_node)
        if filtered_root is not None:
            filtered_tree.append(filtered_root)
    
    return {
        'calls': filtered_calls,
        'call_tree': filtered_tree,
        'stats': trace_data.get('stats', {})
    }


def format_trace_for_display(trace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format trace data for display in UI components.
    
    Args:
        trace_data: Trace data from get_trace_data()
        
    Returns:
        List of formatted call records suitable for UI display
    """
    formatted_calls = []
    
    for call_id, call_data in trace_data.get('calls', {}).items():
        formatted_call = {
            'id': call_id,
            'function': call_data.get('function_name', 'unknown'),
            'file': os.path.basename(call_data.get('filename', 'unknown')),
            'line': call_data.get('lineno', 0),
            'depth': call_data.get('depth', 0),
            'status': 'exception' if call_data.get('exception') else 
                     ('return' if call_data.get('end_time') else 'active'),
            'duration': call_data.get('duration'),
            'timestamp': call_data.get('start_time'),
            'return_value': call_data.get('return_value'),
            'exception': call_data.get('exception'),
            'locals_count': len(call_data.get('locals', {})),
            'globals_count': len(call_data.get('globals', {}))
        }
        formatted_calls.append(formatted_call)
    
    # Sort by start time for chronological display
    formatted_calls.sort(key=lambda x: x.get('timestamp') or 0)
    
    return formatted_calls


def get_call_hierarchy(trace_data: Dict[str, Any], call_id: str) -> List[Dict[str, Any]]:
    """
    Get the hierarchy (parents to children) for a specific call.
    
    Args:
        trace_data: Trace data from get_trace_data()
        call_id: ID of the call to get hierarchy for
        
    Returns:
        List of calls from root to the specified call
    """
    calls = trace_data.get('calls', {})
    if call_id not in calls:
        return []
    
    hierarchy = []
    current_id = call_id
    
    # Build hierarchy from call to root
    while current_id is not None and current_id in calls:
        call_data = calls[current_id]
        hierarchy.insert(0, {
            'call_id': current_id,
            'function_name': call_data.get('function_name'),
            'filename': call_data.get('filename'),
            'lineno': call_data.get('lineno'),
            'depth': call_data.get('depth')
        })
        current_id = call_data.get('parent_id')
    
    return hierarchy


if __name__ == "__main__":
    # Simple test
    test_paths = [
        "/home/user/project/script.py",
        "/usr/lib/python3.8/os.py",
        "/home/user/.local/lib/python3.8/site-packages/requests/api.py",
        "/tmp/test.py"
    ]
    
    print("Testing file filtering:")
    for path in test_paths:
        result = should_trace_file(path, 
                                 include_paths=["/home/user/project"],
                                 exclude_paths=["/tmp"],
                                 exclude_stdlib=True)
        print(f"{path}: {result}")