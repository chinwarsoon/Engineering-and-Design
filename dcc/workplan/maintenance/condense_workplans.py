"""Condense workplan knowledge — All workplan files and support docs.

This script scans the dcc/workplan directory for all Markdown files, extracts 
key metadata (ID, Version, Status, Scope, Phases), and generates a 
consolidated knowledge base in dcc/output/workplan_knowledge.md.

Standardized per agent_rule.md Section 5.
"""

import re, os, textwrap

# Path setup per agent_rule.md Section 4 (Module Design)
# Script is in dcc/workplan/maintenance/
MAINTENANCE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKPLAN_DIR = os.path.dirname(MAINTENANCE_DIR) # dcc/workplan/
DCC_DIR = os.path.dirname(WORKPLAN_DIR)         # dcc/
OUTPUT_DIR = os.path.join(DCC_DIR, 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'workplan_knowledge.md')

def find_targets():
    """Find all .md files in the workplan directory recursively.
    
    Returns:
        list: A list of tuples containing (relative_path, absolute_path).
        
    Breadcrumbs:
    - WORKPLAN_DIR: dcc/workplan/
    """
    targets = []
    for root, dirs, files in os.walk(WORKPLAN_DIR):
        parts = root.split(os.sep)
        # Ignore pycache but process reports and all other subfolders
        if '__pycache__' in parts:
            continue
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, WORKPLAN_DIR)
                targets.append((rel, path))
    return targets

def read_file(path):
    """Read file content with UTF-8 encoding.
    
    Args:
        path (str): Absolute path to the file.
        
    Returns:
        str: Content of the file.
    """
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def extract_meta(text):
    """Extract metadata (ID, Version, Status, Date) from Markdown content.
    
    Args:
        text (str): Markdown content.
        
    Returns:
        dict: Extracted metadata.
    """
    meta = {}
    # Table format: | **Field** | **Value** |
    m = re.search(r'\|\s*\*\*Field\*\*\s*\|\s*\*\*Value\*\*\s*\|(.+?)(?=\n#|\n##|\n---)', text, re.DOTALL)
    if m:
        for k, v in re.findall(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', m.group(1)):
            meta[re.sub(r'\*\*', '', k).strip().lower()] = re.sub(r'\*\*', '', v).strip()
    
    # Inline bold metadata patterns
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
    
    # Fallback version detection from history tables or generic strings
    if not meta.get('version'):
        m = re.search(r'\|\s*(\d+\.\d+(?:\.\d+)?)\s*\|', text)
        if m:
            meta['version'] = m.group(1)
    if not meta.get('version'):
        m = re.search(r'Version[:\s]+(\d+\.\d+(?:\.\d+)?)', text)
        if m:
            meta['version'] = m.group(1)
            
    return meta

def extract_phases(text):
    """Extract implementation phases and their status.
    
    Args:
        text (str): Markdown content.
        
    Returns:
        list: List of phase dictionaries.
    """
    completed_phases = set()
    # Check for "Phase X COMPLETE" markers in history
    for m in re.finditer(r'Phase\s+(\w+)\s+COMPLET', text, re.IGNORECASE):
        completed_phases.add(m.group(1).upper())
    
    # Check for "Phases all complete"
    for m in re.finditer(r'Phases?\s+[\d,\s–-]+\s+(?:all\s+)?complete', text, re.IGNORECASE):
        for n in re.findall(r'\b([1-8])\b', text[:m.start()]):
            completed_phases.add(str(n))

    phases = []
    # Identify Phase headers: ## Phase X: Title
    for m in re.finditer(r'#{2,3}\s+Phase\s+([\w]+)[:\s]+(.*?)(?=\n)', text):
        num = m.group(1)
        title = m.group(2).strip()[:80]
        block_start = m.end()
        next_m = re.search(r'#{1,3}\s', text[block_start:])
        block = text[block_start:block_start + (next_m.start() if next_m else 4000)]
        
        # Determine status from block content or heading markers
        status = ''
        sm = re.search(r'\*\*Status\*\*[:\]]+\s*(.+?)(?:\n)', block)
        if sm:
            status = sm.group(1).strip()
        
        if not status:
            heading_line = m.group(0)
            if '✅' in heading_line or 'COMPLETE' in heading_line.upper():
                status = '✅ COMPLETE'
        
        if not status and num.upper() in completed_phases:
            status = '✅ COMPLETE'
            
        files = []
        fs = re.search(r'(?:Files? Modified|Files? Changed)[:\]]+\s*(.*?)(?=\n#{1,3}|\Z)', block, re.DOTALL)
        if fs:
            files = re.findall(r'`([^`]+)`', fs.group(1))
            
        emoji = '✅' if ('✅' in status or 'COMPLETE' in status.upper()) else \
                ('🔄' if ('🟡' in status or 'ACTIVE' in status.upper() or 'IN PROGRESS' in status.upper()) else \
                ('📝' if ('📝' in status or 'PENDING' in status.upper()) else '⏳'))
        
        phases.append({'num': num, 'title': title, 'status': status[:60], 'emoji': emoji, 'files': files[:8]})
    return phases

def extract_scope(text):
    """Extract the scope or objective section summary.
    
    Args:
        text (str): Markdown content.
        
    Returns:
        str: Summarized scope text.
    """
    m = re.search(r'##\s+\d+\.?\s*(?:Scope|Objective|Object)\s+(.*?)(?=\n##\s+\d+\.)', text, re.DOTALL)
    if not m:
        # Fallback for documents without numbered Scope headers
        m = re.search(r'##\s*(?:Scope|Objective|Object)\s+(.*?)(?=\n##|\Z)', text, re.DOTALL)
    
    if not m:
        return ''
        
    lines = [l.strip() for l in m.group(1).split('\n') if l.strip() and not l.strip().startswith('|') and '---' not in l]
    return ' '.join(lines)[:200].strip()

def extract_deps(text):
    """Extract internal workplan dependencies.
    
    Args:
        text (str): Markdown content.
        
    Returns:
        list: List of dependency names.
    """
    deps = []
    m = re.search(r'##\s+\d+\.?\s*Dependenc(?:ies|y)\s+(.*?)(?=\n##\s+\d+\.)', text, re.DOTALL)
    if m:
        for name, link in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', m.group(1)):
            if '_workplan' in link:
                deps.append(name[:50])
    return deps[:5]

def format_entry(rel, text):
    """Format extracted data into a standardized Markdown entry.
    
    Args:
        rel (str): Relative path to the file.
        text (str): File content.
        
    Returns:
        str: Formatted Markdown entry.
    """
    meta = extract_meta(text)
    phases = extract_phases(text)
    scope = extract_scope(text)
    deps = extract_deps(text)
    fname = os.path.splitext(os.path.basename(rel))[0]
    
    out = [f"## {fname}", f"  Path: {rel}"]
    if meta.get('id'): 
        out.append(f"  ID: {re.sub(r'\*\*', '', meta['id']).strip()}")
    
    ver = meta.get('version', '?').replace('**', '').strip()
    st = re.sub(r'\*\*', '', meta.get('status', '?')).strip()[:80]
    out.append(f"  Ver: {ver}  Status: {st}")
    
    if meta.get('date'): 
        out.append(f"  Date: {re.sub(r'\*\*', '', meta['date']).strip()}")
    if scope: 
        out.append(f"  Scope: {scope}")
        
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
    """Main execution entry point."""
    print(f"Scanning workplan directory: {WORKPLAN_DIR}")
    targets = find_targets()
    entries = []
    
    for rel, path in sorted(targets):
        text = read_file(path)
        entries.append(format_entry(rel, text))
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# DCC Workplan Knowledge Base (Condensed)\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(entries)} documents\n\n---\n\n")
        for e in entries:
            f.write(e)
            f.write('\n')

    chars = sum(len(e) for e in entries)
    print(f"Wrote {len(entries)} documents to {OUTPUT_FILE}")
    print(f"Characters: {chars:,} (~{chars // 4:,} estimated tokens)")

if __name__ == '__main__':
    from datetime import datetime
    main()
