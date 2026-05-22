"""Condense workplan knowledge — strict workplan files only + key support docs."""

import re, os, textwrap

WORKPLAN_DIR = os.path.dirname(os.path.abspath(__file__))

# Only process actual workplan files, plus a few critical support docs
KEY_SUPPORT_DOCS = {
    'ui_design/html_design_rule.md',
    'ui_design/web_interface/web_interface_workplan.md',
    'column_processing/column_update_logic.md',
    'column_processing/column_priority_reference.md',
    'error_handling/error_handling_taxonomy.md',
    'data_validation/dcc_register_rule.md',
    'data_validation/row_validation_workplan.md',
    'data_validation/col_validation_workplan.md',
}

def find_targets():
    targets = []
    for root, dirs, files in os.walk(WORKPLAN_DIR):
        parts = root.split(os.sep)
        if 'reports' in parts or '__pycache__' in parts:
            continue
        for f in files:
            if f == 'README.md':
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, WORKPLAN_DIR)
            # Include workplan files
            if f.endswith('_workplan.md'):
                targets.append((rel, path))
            # Include key support docs
            elif rel in KEY_SUPPORT_DOCS:
                targets.append((rel, path))
    return targets

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def extract_meta(text):
    meta = {}
    # Table format: | **Field** | **Value** |
    m = re.search(r'\|\s*\*\*Field\*\*\s*\|\s*\*\*Value\*\*\s*\|(.+?)(?=\n#|\n##|\n---)', text, re.DOTALL)
    if m:
        for k, v in re.findall(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', m.group(1)):
            meta[re.sub(r'\*\*', '', k).strip().lower()] = re.sub(r'\*\*', '', v).strip()
    # Inline bold metadata
    for pat, key in [
        (r'\*\*(?:Workplan|Document)\s*ID[:\]]+\s*(.+?)(?:\n)', 'id'),
        (r'\*\*(?:Version|Current Version)[:\]]+\s*(.+?)(?:\n)', 'version'),
        (r'\*\*(?:Status)[:\]]+\s*(.+?)(?:\n)', 'status'),
        (r'\*\*(?:Created|Date|Last Updated)[:\]]+\s*(.+?)(?:\n)', 'date'),
    ]:
        if key not in meta or not meta.get(key):
            m = re.search(pat, text)
            if m:
                meta[key] = m.group(1).strip()
    # Version from revision history table
    if not meta.get('version'):
        m = re.search(r'\|\s*(\d+\.\d+(?:\.\d+)?)\s*\|', text)
        if m:
            meta['version'] = m.group(1)
    # Version from "Version: X.Y.Z" anywhere
    if not meta.get('version'):
        m = re.search(r'Version[:\s]+(\d+\.\d+(?:\.\d+)?)', text)
        if m:
            meta['version'] = m.group(1)
    return meta

def extract_phases(text):
    # Build set of completed phases from revision history
    completed_phases = set()
    for m in re.finditer(r'Phase\s+(\w+)\s+COMPLET', text, re.IGNORECASE):
        completed_phases.add(m.group(1).upper())
    for m in re.finditer(r'Phases?\s+[\d,\s–-]+\s+(?:all\s+)?complete', text, re.IGNORECASE):
        # Mark all numeric phases 1-8 as complete
        for n in re.findall(r'\b([1-8])\b', text[:m.start()]):
            completed_phases.add(str(n))

    phases = []
    for m in re.finditer(r'#{2,3}\s+Phase\s+([\w]+)[:\s]+(.*?)(?=\n)', text):
        num = m.group(1)
        title = m.group(2).strip()[:80]
        block_start = m.end()
        next_m = re.search(r'#{1,3}\s', text[block_start:])
        block = text[block_start:block_start + (next_m.start() if next_m else 4000)]
        # Status from inline **Status**: field
        status = ''
        sm = re.search(r'\*\*Status\*\*[:\]]+\s*(.+?)(?:\n)', block)
        if sm:
            status = sm.group(1).strip()
        # Check heading itself
        if not status:
            heading_line = m.group(0)
            if '✅' in heading_line or 'COMPLETE' in heading_line.upper():
                status = '✅ COMPLETE'
        # Check phase title
        if not status and ('✅' in title or 'COMPLETE' in title.upper()):
            status = '✅ COMPLETE'
        # Check revision history
        if not status and num.upper() in completed_phases:
            status = '✅ COMPLETE'
        # Files modified
        files = []
        fs = re.search(r'(?:Files? Modified|Files? Changed)[:\]]+\s*(.*?)(?=\n#{1,3}|\Z)', block, re.DOTALL)
        if fs:
            files = re.findall(r'`([^`]+)`', fs.group(1))
        # Emoji
        emoji = '✅' if ('✅' in status or 'COMPLETE' in status.upper()) else \
                ('🔄' if ('🟡' in status or 'ACTIVE' in status.upper() or 'IN PROGRESS' in status.upper()) else \
                ('📝' if ('📝' in status or 'PENDING' in status.upper()) else '⏳'))
        phases.append({'num': num, 'title': title, 'status': status[:60], 'emoji': emoji, 'files': files[:8]})
    return phases

def extract_scope(text):
    m = re.search(r'##\s+\d+\.?\s*(?:Scope|Objective|Object)\s+(.*?)(?=\n##\s+\d+\.)', text, re.DOTALL)
    if not m:
        return ''
    lines = [l.strip() for l in m.group(1).split('\n') if l.strip() and not l.strip().startswith('|') and '---' not in l]
    return ' '.join(lines)[:200].strip()

def extract_deps(text):
    deps = []
    m = re.search(r'##\s+\d+\.?\s*Dependenc(?:ies|y)\s+(.*?)(?=\n##\s+\d+\.)', text, re.DOTALL)
    if m:
        for name, link in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', m.group(1)):
            if '_workplan' in link:
                deps.append(name[:50])
    return deps[:5]

def format_workplan(rel, text):
    meta = extract_meta(text)
    phases = extract_phases(text)
    scope = extract_scope(text)
    deps = extract_deps(text)
    fname = os.path.splitext(os.path.basename(rel))[0]
    out = [f"## {fname}", f"  Path: {rel}"]
    if meta.get('id'): out.append(f"  ID: {re.sub(r'\*\*', '', meta['id']).strip()}")
    ver = meta.get('version', '?').replace('**', '').strip()
    st = re.sub(r'\*\*', '', meta.get('status', '?')).strip()[:80]
    out.append(f"  Ver: {ver}  Status: {st}")
    if meta.get('date'): out.append(f"  Date: {re.sub(r'\*\*', '', meta['date']).strip()}")
    if scope: out.append(f"  Scope: {scope}")
    if phases:
        parts = []
        for p in phases:
            p_str = f"{p['emoji']}P{p['num']}"
            if p['title']:
                p_str += f":{p['title'][:40]}"
            parts.append(p_str)
        out.append(f"  Phases: {' '.join(parts[:12])}")
        done = sum(1 for p in phases if p['emoji'] == '✅')
        active = sum(1 for p in phases if p['emoji'] == '🔄')
        pend = sum(1 for p in phases if p['emoji'] == '📝')
        out.append(f"  Summary: {done}/{len(phases)} done, {active} active, {pend} pending")
    if deps:
        out.append(f"  Deps: {', '.join(deps)}")
    out.append('')
    return '\n'.join(out)

def main():
    targets = find_targets()
    entries = []
    for rel, path in sorted(targets):
        text = read_file(path)
        entries.append(format_workplan(rel, text))
    
    out = os.path.join(WORKPLAN_DIR, 'workplan_knowledge.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write("# DCC Workplan Knowledge Base (Condensed)\n")
        f.write(f"# Generated: 2026-05-22 | {len(entries)} documents\n\n---\n\n")
        for e in entries:
            f.write(e)
            f.write('\n')

    chars = sum(len(e) for e in entries)
    print(f"Wrote {len(entries)} documents to {out}")
    print(f"Characters: {chars:,} (~{chars // 4:,} estimated tokens)")

if __name__ == '__main__':
    main()
