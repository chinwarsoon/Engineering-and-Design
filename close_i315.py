#!/usr/bin/env python
import json

# Read the knowledge.json
with open('eks/knowledge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find and update the I315 entry
for i, entry in enumerate(data['known_issues']):
    if 'I315' in entry:
        # Updated I315 entry reflecting resolution
        new_entry = (
            'I315 - Resolved 2026-08-31 (U306/U307) — composite natural-key UNIQUE gap resolved: '
            'config-layer (U306) `unique_keys[]` arrays added to all 14 definition tables in '
            'eks_db_config.json per Agents.md Section 15 SSOT; '
            'SchemaToDDL code change (2026-08-31): _render_table_from_config reads '
            'unique_keys[] and emits table-level UNIQUE (cols) DDL clauses verified for '
            'project_doc_type, template_source_quality, project_revision_pattern; '
            'drift-prevention regression tests (9 tests, all pass) per Agents.md '
            'Section 16 designed and verified; I315 formally closed and aligned '
            '(OA Aligned transition) - config and code layers complete, documentation synced.'
        )
        data['known_issues'][i] = new_entry
        print(f'Updated I315 entry at index {i}')
        break

# Write back
with open('eks/knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Knowledge.json successfully updated.')
print(f'Version: {data["version"]}')