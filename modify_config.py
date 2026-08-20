import json

with open('eks/config/schemas/eks_db_config.json') as f:
    cfg = json.load(f)

tables = cfg.get('db_tables', [])

# Mapping of table_name -> unique_keys entry
unique_keys_map = {
    'template_source_quality': [['template_id', 'cover_type']],
    'template_elements': [['template_id', 'element_type']],
    'element_by_cover_type': [['element_type', 'cover_type']],
    'column_class': [['column_name']],
    'onto_class_fragment': [['class_id', 'fragment_id']],
    'fp_property_mapping': [['profile_id', 'source_key']],
    'project_doc_type': [['project_code', 'local_code']],
    'project_engineering_standard': [['project_code', 'standard_cat']],
    'project_allowed_discipline': [['project_code', 'discipline_code']],
    'asset_fragment_field': [['fragment_id', 'field_name']],
    'asset_type_fragment': [['asset_type_code', 'fragment_id']],
    'asset_column_normalization': [['asset_type_code', 'source_column_name']],
    'asset_trigger': [['asset_type_code', 'trigger_id']],
    'project_revision_pattern': [['project_code']],
}

# Add unique_keys to each target table
for table in tables:
    name = table.get('table_name', '')
    if name in unique_keys_map:
        table['unique_keys'] = unique_keys_map[name]
        print(f'Added unique_keys to {name}: {unique_keys_map[name]}')

# Verify all 14 were updated
updated = [t.get('table_name') for t in tables if t.get('table_name') in unique_keys_map]
expected = list(unique_keys_map.keys())
missing = [t for t in expected if t not in updated]

if missing:
    print(f'ERROR: These tables were not updated: {missing}')
else:
    print(f'Successfully updated {len(updated)} tables')
    
# Save the modified config
with open('eks/config/schemas/eks_db_config.json', 'w') as f:
    json.dump(cfg, f, indent=2)

print('\\nConfig file saved.')