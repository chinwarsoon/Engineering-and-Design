"""Temporary test script to debug get_document behavior."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pathlib import Path
from eks.engine.core import DocumentRegistry

db_path = Path('eks/output/eks_registry.db')
if db_path.exists():
    db_path.unlink()

reg = DocumentRegistry()
reg.register_document({
    'document_number': 'STATUS-001', 'revision': 'A',
    'document_type': 'SPEC', 'extract_status': 'pending'
})
reg.update_document_status('STATUS-001-A', 'success', confidence=0.95, notes='test')

doc = reg.get_document('STATUS-001', revision='A')
print(f'doc = {doc!r}')
print(f'type = {type(doc)}')

import duckdb
conn = duckdb.connect(str(reg.db_path))
res = conn.execute("SELECT * FROM documents WHERE document_number = 'STATUS-001' AND revision = 'A'").fetchone()
print(f'raw fetchone: {res!r}')
print(f'raw type: {type(res)}')
cols = [d[0] for d in conn.description] if res else []
print(f'cols: {cols}')

if res:
    for row in res:
        print(f'  row var: {row!r}')
conn.close()
