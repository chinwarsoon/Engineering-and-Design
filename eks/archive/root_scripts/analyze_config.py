import json

with open('eks/config/schemas/eks_db_config.json') as f:
    cfg = json.load(f)

tables = cfg.get('db_tables', [])
# Show first 5 tables structure
for t in tables[:5]:
    name = t.get('table_name', 'N/A')
    print(f'Table: {name}')
    print(f'  Keys: {list(t.keys())}')
    # Show columns key if present
    cols = t.get('columns', [])
    print(f'  columns count: {len(cols)}')
    # Check if unique_keys already exists
    uk = t.get('unique_keys', 'NOT PRESENT')
    print(f'  unique_keys: {uk}')
    print()

# Now show all tables that need unique_keys added
target_tables = [
    'template_source_quality', 'template_elements', 'element_by_cover_type',
    'column_class', 'onto_class_fragment', 'fp_property_mapping',
    'project_doc_type', 'project_engineering_standard', 'project_allowed_discipline',
    'asset_fragment_field', 'asset_type_fragment', 'asset_column_normalization',
    'asset_trigger', 'project_revision_pattern'
]

print(f'\\n--- Checking target tables ---')
for t in tables:
    name = t.get('table_name', '')
    if name in target_tables:
        uk = t.get('unique_keys', 'NOT PRESENT')
        print(f'  {name}: unique_keys = {uk}')