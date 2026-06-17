import sys
from pathlib import Path
from eks.engine.core.schema_loader import SchemaLoader

def test_loader_ontology_validation():
    try:
        loader = SchemaLoader(config_dir="eks/config")
        loader.load_all()
        print("SchemaLoader Full Validation: PASS")
    except Exception as e:
        print(f"SchemaLoader Full Validation: FAIL - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_loader_ontology_validation()
