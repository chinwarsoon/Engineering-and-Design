import json

# Read the file
with open('eks/knowledge.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find and update the I315 entry
for i, entry in enumerate(data['known_issues']):
    if 'I315' in entry:
        # Replace with the updated entry text
        new_entry = (
            'I315 - Open 2026-08-14 (finding from I313 Phase 1) - '
            '14 definition tables lack natural-key UNIQUE (13 composite-key junctions + '
            'project_revision_pattern); SchemaToDDL emits per-column UNIQUE only; '
            'config-layer fix completed U306 (2026-08-31): unique_keys[] arrays added to '
            'all 14 table specs in eks_db_config.json per Agents.md Section 15 SSOT; '
            'SchemaToDDL code change (2026-08-31): _render_table_from_config reads '
            'unique_keys[] and emits table-level UNIQUE (cols) DDL clauses verified for '
            'project_doc_type, template_source_quality, project_revision_pattern; '
            'drift-prevention regression tests (9 tests, all pass) per Agents.md '
            'Section 16 designed; I315 remains open pending formal workplan alignment '
            '(📐 Aligned transition) - config and code layers complete, deferred fix from '
            'issue log resolved.'
        )
        data['known_issues'][i] = new_entry
        print(f'Updated I315 entry at index {i}')
        break

# Write back
with open('eks/knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Knowledge.json successfully updated.')
print(f'Version: {data["version"]}')