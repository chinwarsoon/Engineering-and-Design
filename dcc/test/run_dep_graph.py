import json
import sys
from pathlib import Path

# Setup paths to import from dcc/workflow
ROOT = Path("/workspaces/Engineering-and-Design/dcc")
WORKFLOW_PATH = ROOT / "workflow"
if str(WORKFLOW_PATH) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_PATH))

# Mocking initiation_engine logging
class MockLogging:
    @staticmethod
    def status_print(msg, **kwargs): print(f"STATUS: {msg}")
    @staticmethod
    def debug_print(msg, **kwargs): print(f"DEBUG: {msg}")

sys.modules['initiation_engine'] = MockLogging

from schema_engine.loader import RefResolver, SchemaDependencyGraph

def run():
    project_setup_path = ROOT / "config" / "schemas" / "project_setup.json"
    schema_dirs = [
        ROOT / "config" / "schemas",
        ROOT / "workflow" / "processor_engine" / "error_handling" / "config"
    ]
    
    print(f"--- Initializing RefResolver ---")
    resolver = RefResolver(project_setup_path, schema_dirs)
    
    print(f"\n--- Building Dependency Graph ---")
    graph_builder = SchemaDependencyGraph(resolver)
    graph = graph_builder.build_graph()
    
    print("\n--- Direct Dependencies ---")
    for schema, deps in sorted(graph.items()):
        if deps:
            print(f"{schema} -> {', '.join(sorted(deps))}")
        else:
            print(f"{schema} -> (no dependencies)")
            
    print("\n--- Resolution Order (Topological Sort) ---")
    try:
        order = graph_builder.get_resolution_order()
        for i, name in enumerate(order, 1):
            print(f"{i}. {name}")
    except Exception as e:
        print(f"Error determining resolution order: {e}")

if __name__ == "__main__":
    run()
