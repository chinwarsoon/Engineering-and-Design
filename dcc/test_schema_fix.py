
import json
from pathlib import Path
from workflow.schema_engine import SchemaValidator

def test_schema_resolution():
    schema_path = Path("config/schemas/dcc_register_config.json")
    validator = SchemaValidator(schema_path)
    resolved = validator.load_resolved_schema()
    
    parameters = resolved.get("parameters", {})
    dyn_creation = parameters.get("dynamic_column_creation", {})
    
    print(f"Parameters type: {type(parameters)}")
    print(f"Dynamic column creation: {dyn_creation}")
    
    columns = resolved.get("columns", {})
    doc_title = columns.get("Document_Title", {})
    reviewer = columns.get("Reviewer", {})
    
    print(f"Document_Title required: {doc_title.get('required')}")
    print(f"Reviewer required: {reviewer.get('required')}")

if __name__ == "__main__":
    test_schema_resolution()
