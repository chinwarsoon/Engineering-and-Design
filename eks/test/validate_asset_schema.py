import json
from referencing import Registry
from referencing.jsonschema import DRAFT7
from jsonschema import validate

base   = json.load(open('eks/config/eks_asset_base_schema.json',  encoding='utf-8'))
setup  = json.load(open('eks/config/eks_asset_setup_schema.json', encoding='utf-8'))
config = json.load(open('eks/config/eks_asset_config.json',        encoding='utf-8'))

# 1. Fragment consistency check
base_frags   = set(base['definitions'].keys())
config_frags = set()
for at, entry in config['asset_type_registry'].items():
    for f in entry.get('fragments', []):
        config_frags.add(f)
    for rule in entry.get('conditional_fragments', []):
        config_frags.add(rule['fragment'])

missing = config_frags - base_frags
print('Fragment names in config not in base:', missing if missing else 'NONE — OK')
print('Base fragments   :', sorted(base_frags))
print('Config frags used:', sorted(config_frags))
print(f'Fragment count: base={len(base_frags)}, config_used={len(config_frags)}')

# 2. Validate config against setup schema
resources = {}
for schema in [base, setup]:
    sid = schema.get('$id')
    if sid:
        resources[sid] = DRAFT7.create_resource(schema)
registry = Registry().with_resources((uri, res) for uri, res in resources.items())
validate(instance=config, schema=setup, registry=registry)
print('Schema validation: PASS')

# 3. AT_ types with conditional_fragments
print('\nAT_ types with conditional_fragments:')
for at, entry in config['asset_type_registry'].items():
    if entry.get('conditional_fragments'):
        for rule in entry['conditional_fragments']:
            print(f'  {at}: apply [{rule["fragment"]}] when {rule["when"]} in {rule["in"]}')
