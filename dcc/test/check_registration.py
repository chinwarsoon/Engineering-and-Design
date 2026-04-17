import json
from pathlib import Path
from dcc.workflow.schema_engine.loader.schema_loader import SchemaLoader
from dcc.workflow.schema_engine.loader.ref_resolver import SchemaNotRegisteredError

def check_strict_registration():
    # Paths
    project_root = Path("/workspaces/Engineering-and-Design/dcc")
    schema_dir = project_root / "config" / "schemas"
    engine_config_dir = project_root / "workflow" / "processor_engine" / "error_handling" / "config"
    project_config_path = schema_dir / "project_config.json"
    
    # Initialize SchemaLoader
    loader = SchemaLoader(
        base_path=schema_dir,
        project_setup_path=project_config_path
    )
    
    print(f"\n[+] Total registered schemas: {len(loader._registered_schemas)}")
    print(f"[+] Registered schemas: {sorted(list(loader._registered_schemas))}")
    
    # 1. Collect all actual schema files
    actual_schemas = {}
    for f in schema_dir.glob("*.json"):
        actual_schemas[f.stem] = f
    for f in engine_config_dir.glob("*.json"):
        actual_schemas[f.stem] = f
        
    # 2. Check for discrepancies
    unregistered = []
    for schema_name in actual_schemas:
        if schema_name not in loader._registered_schemas:
            unregistered.append(schema_name)
            
    if unregistered:
        print("\n[!] UNREGISTERED SCHEMAS FOUND (Strict Registration Violation):")
        for name in sorted(unregistered):
            print(f"  - {name} ({actual_schemas[name]})")
    else:
        print("\n[+] SUCCESS: All schema files are correctly registered.")
        
    # 3. Try to load each recursive
    print("\n--- Testing Recursive Load & $ref Resolution ---")
    success_count = 0
    fail_count = 0
    
    # Clear cache to ensure clean test
    loader.cache.clear()
    
    for name in sorted(loader._registered_schemas):
        try:
            print(f"Processing {name}...", end=" ", flush=True)
            # Load with recursive $ref resolution
            schema = loader.load_recursive(name, auto_resolve=True)
            
            # Basic sanity check: if it's project_config, check if it has metadata
            if name == "project_config" and "project_metadata" not in schema:
                print("FAILED (Metadata missing)")
                fail_count += 1
                continue
                
            print("OK")
            success_count += 1
        except Exception as e:
            print(f"FAILED: {type(e).__name__}: {e}")
            fail_count += 1

    print(f"\nSummary: {success_count} succeeded, {fail_count} failed.")
    
    # 4. Check Cache Metrics
    metrics = loader.cache.get_metrics()
    print(f"\nCache Metrics: {metrics}")

if __name__ == "__main__":
    check_strict_registration()
