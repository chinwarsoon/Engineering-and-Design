import json
from jsonschema import validate
from referencing import Registry
from referencing.jsonschema import DRAFT7

def verify_schemas():
    try:
        # Load files
        with open('config/eks_base_schema.json', 'r') as f:
            base_schema = json.load(f)
        with open('config/eks_setup_schema.json', 'r') as f:
            setup_schema = json.load(f)
        with open('config/eks_config.json', 'r') as f:
            config = json.load(f)

        # Print Metadata
        print(f"Base Schema ID: {base_schema.get('$id')}")
        print(f"Base Schema Version: {base_schema.get('version')}")
        print(f"Setup Schema ID: {setup_schema.get('$id')}")
        print(f"Setup Schema Version: {setup_schema.get('version')}")

        # Setup Schema Registry for resolution
        resources = {}
        if base_schema.get('$id'):
            resources[base_schema['$id']] = DRAFT7.create_resource(base_schema)
        if setup_schema.get('$id'):
            resources[setup_schema['$id']] = DRAFT7.create_resource(setup_schema)

        registry = Registry().with_resources(
            (uri, resource) for uri, resource in resources.items()
        )

        # Validate
        validate(instance=config, schema=setup_schema, registry=registry)
        
        print("\n[SUCCESS] Enhanced Validation: eks_config.json is valid and references are resolved via Digital IDs.")

    except Exception as e:
        print(f"\n[FAILURE] Validation Error: {e}")
        exit(1)

if __name__ == "__main__":
    verify_schemas()
