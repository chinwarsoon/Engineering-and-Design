import json
from referencing import Registry
from referencing.jsonschema import DRAFT7
from jsonschema import validate
from pathlib import Path

CONFIG_DIR = Path('eks/config/schemas')
if not CONFIG_DIR.exists():
    CONFIG_DIR = Path('eks/config')

def test_ontology_validation():
    base   = json.load(open(CONFIG_DIR / 'eks_ontology_base_schema.json',  encoding='utf-8'))
    setup  = json.load(open(CONFIG_DIR / 'eks_ontology_setup_schema.json', encoding='utf-8'))
    config = json.load(open(CONFIG_DIR / 'eks_ontology_config.json',       encoding='utf-8'))
    
    resources = {s['$id']: DRAFT7.create_resource(s) for s in [base, setup] if '$id' in s}
    registry = Registry().with_resources(resources.items())
    
    validate(instance=config, schema=setup, registry=registry)
    print("Ontology validation: PASS")

if __name__ == "__main__":
    try:
        test_ontology_validation()
    except Exception as e:
        print(f"Ontology validation: FAIL - {e}")
        import traceback
        traceback.print_exc()
        exit(1)
