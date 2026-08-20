import json

with open('eks/config/schemas/eks_db_config.json') as f:
    cfg = json.load(f)

tables = cfg.get('db_tables', [])
for t in tables:
    print(f'Table: {t.get("table_name")}')
    print(f'  Columns: {[c["name"] for c in t.get("columns", [])]}')
    print(f'  Unique cols: {[c["name"] for c in t.get("columns", []) if c.get("unique")]}')
    print()