#!/usr/bin/env python3
"""Parse DCC log files and workplan files to generate dcc_log_graph.json"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent.parent  # dcc/
LOG_DIR = ROOT / "log"
WORKPLAN_DIR = ROOT / "workplan"
OUTPUT_FILE = ROOT / "output" / "dcc_log_graph.json"

nodes = []
edges = []
node_ids = set()

def add_node(nid, ntype, label, **kwargs):
    nid = str(nid).strip()
    if nid in node_ids:
        return
    node_ids.add(nid)
    node = {"id": nid, "type": ntype, "label": label}
    node.update(kwargs)
    nodes.append(node)

def add_edge(src, tgt, etype):
    src, tgt = str(src).strip(), str(tgt).strip()
    if src != tgt:
        edges.append({"from": src, "to": tgt, "type": etype})

def safe_id(s):
    return re.sub(r'[^a-zA-Z0-9_-]', '-', s.lower()).strip('-')

def normalize_path(p):
    if not p:
        return p
    p = p.strip().strip('`').strip("'").strip('"')
    for prefix in ["dcc/", "dcc\\", "workflow/", "workflow\\"]:
        if p.startswith(prefix):
            p = p[len(prefix):]
    return p

def parse_date(text):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    return m.group(1) if m else None

def parse_status(text):
    if not text:
        return "UNKNOWN"
    t = text.upper()
    if "RESOLVED" in t or "COMPLETE" in t:
        return "RESOLVED"
    if "IN PROGRESS" in t:
        return "IN PROGRESS"
    if "PENDING" in t:
        return "PENDING"
    if "OPEN" in t:
        return "OPEN"
    if "PASS" in t:
        return "PASS"
    if "FAIL" in t:
        return "FAIL"
    return text.strip()[:30]

def parse_severity(text):
    if not text:
        return None
    t = text.upper()
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "WARNING", "LOW", "INFO"]:
        if sev in t:
            return sev
    return None

def extract_files(text):
    files = []
    for m in re.findall(r'`([^`]+\.(?:py|json|md|html|css|yml|yaml|xlsx|csv|txt|sh|cfg|ini|toml))`', text):
        files.append(m)
    for m in re.findall(r'(?:dcc/)?(?:workflow|config|ui|output|log|workplan|docs)/[\w/.-]+\.\w+', text):
        files.append(m)
    return list(set(normalize_path(f) for f in files if f and len(f) > 3))

def extract_error_codes(text):
    return list(set(re.findall(r'[A-Z]\d-[A-Z]-[A-Z]-\d{4}(?:-[A-Z])?', text)))

def extract_sections(text):
    sections = []
    for m in re.finditer(r'\n#{1,4}\s+(.+?)(?:\n|$)', text):
        title = m.group(1).strip()
        start = m.end()
        next_m = re.search(r'\n#{1,4}\s+', text[start:])
        end = start + next_m.start() if next_m else len(text)
        content = text[start:end]
        sections.append({"title": title, "content": content, "offset": m.start()})
    return sections

# ============================================================
# PHASE 1.0: Build Folder Hierarchy
# ============================================================
print("=== Phase 1.0: Building Folder Hierarchy ===")

folder_ids = {}
all_wp_files = list(WORKPLAN_DIR.rglob("*.md"))
wp_main = [f for f in all_wp_files if '/reports/' not in str(f) and f.name != 'README.md']
rpt_files = [f for f in all_wp_files if '/reports/' in str(f)]

# Collect all unique folders
all_folders = set()
for f in all_wp_files:
    rel = f.relative_to(WORKPLAN_DIR)
    for parent in rel.parents:
        all_folders.add(str(parent))

# Create folder nodes (top-down)
for folder_path in sorted(all_folders):
    fid = f"folder-{safe_id(folder_path)}"
    folder_ids[folder_path] = fid
    parts = folder_path.split('/')
    label = parts[-1] if parts else folder_path
    add_node(fid, "folder", label, path=folder_path, depth=len(parts))
    
    # Link to parent folder
    if len(parts) > 1:
        parent_path = '/'.join(parts[:-1])
        if parent_path in folder_ids:
            add_edge(fid, folder_ids[parent_path], "contains")

print(f"  Folders: {len(folder_ids)}")

# ============================================================
# PHASE 1.1: Parse Log Files
# ============================================================
print("\n=== Phase 1.1: Parsing Log Files ===")

# --- gemini.md ---
gf = LOG_DIR / "gemini.md"
if gf.exists():
    text = gf.read_text()
    sids = re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", text)
    for sid in sids:
        add_node(f"session-{sid[:8]}", "session", f"Session {sid[:8]}", session_id=sid)
    print(f"  gemini.md: {len(sids)} sessions")

# --- issue_log.md ---
ifile = LOG_DIR / "issue_log.md"
if ifile.exists():
    text = ifile.read_text()
    sections = re.split(r'(?=<a id="issue-)', text)
    issues_found = 0
    for section in sections:
        anchor = re.search(r'<a id="(issue-[^"]+)"></a>', section)
        if not anchor:
            continue
        issue_id = anchor.group(1).replace('issue-', '')
        title_m = re.search(r'###\s+(Issue\s+.+?)(?:\n|$)', section)
        title = title_m.group(1).strip()[:80] if title_m else issue_id
        status_m = re.search(r'(?:\*\*Status:\*\*|\[Status:\])\s*([^\n]+)', section)
        status = parse_status(status_m.group(1)) if status_m else "UNKNOWN"
        date = parse_date(section)
        severity_m = re.search(r'(?:\*\*Severity:\*\*|Severity:)\s*([^\n]+)', section)
        severity = severity_m.group(1).strip()[:20] if severity_m else parse_severity(section)
        rc_m = re.search(r'(?:\*\*Root Cause:\*\*|Root Cause:)\s*(.+?)(?=\n\*\*|\n- \[|\n##|\n<a|$)', section, re.DOTALL)
        root_cause = rc_m.group(1).strip()[:200] if rc_m else ""
        rows_m = re.search(r'(\d[\d,]*)\s*rows?', section)
        rows_affected = int(rows_m.group(1).replace(',', '')) if rows_m else None
        files = extract_files(section)[:10]
        error_codes = extract_error_codes(section)[:5]
        upd_m = re.search(r'Link to Update Log.*?#([^\s"\)]+)', section)
        
        nid = f"issue-{issue_id}"
        add_node(nid, "issue", issue_id,
                 title=title, status=status, date=date, severity=severity,
                 root_cause=root_cause, rows_affected=rows_affected,
                 files_changed=files, error_codes=error_codes)
        issues_found += 1
        
        if upd_m:
            add_edge(nid, upd_m.group(1), "resolved_by")
        for ec in error_codes:
            ec_nid = f"ec-{ec}"
            add_node(ec_nid, "error_code", ec, severity=severity, status="fixed")
            add_edge(nid, ec_nid, "introduces")
    print(f"  issue_log.md: {issues_found} issues")

# --- update_log.md ---
ufile = LOG_DIR / "update_log.md"
if ufile.exists():
    text = ufile.read_text()
    sections = re.split(r'(?=<a id="update-)', text)
    updates_found = 0
    for section in sections:
        anchor = re.search(r'<a id="(update-[^"]+)"></a>', section)
        if not anchor:
            continue
        aid = anchor.group(1)
        title_m = re.search(r'##\s*(.+?)(?:\n|$)', section)
        title = title_m.group(1).strip()[:80] if title_m else aid
        date = parse_date(section)
        sum_m = re.search(r'(?:\*\*Summary:\*\*|Summary:)\s*(.+?)(?=\n\*\*|\n##|\n###|$)', section, re.DOTALL)
        summary = sum_m.group(1).strip()[:300] if sum_m else ""
        files = extract_files(section)[:10]
        phases = list(set(re.findall(r'(Phase\s+[\dA-Z.]+)', section)))[:5]
        issue_m = re.search(r'Link to Issue.*?#([^\s"\)]+)', section)
        test_m = re.search(r'(?:Test Log|Link to Test).*?#([^\s"\)]+)', section)
        error_codes = extract_error_codes(section)[:5]
        
        nid = f"update-{aid}" if not aid.startswith('update-') else aid
        add_node(nid, "update", title,
                 date=date, summary=summary, files_modified=files, phases=phases)
        updates_found += 1
        
        if issue_m:
            add_edge(f"issue-{issue_m.group(1)}", nid, "resolved_by")
        if test_m:
            add_edge(nid, test_m.group(1), "verified_by")
        for ec in error_codes:
            ec_nid = f"ec-{ec}"
            if ec_nid in node_ids:
                add_edge(nid, ec_nid, "fixes")
    
    date_sections = re.split(r'\n(?=## \d{4}-\d{2}-\d{2})', text)
    for section in date_sections:
        if '<a id="update-' in section:
            continue
        dm = re.search(r'## (\d{4}-\d{2}-\d{2})\s*[—-]\s*(.+?)(?:\n|$)', section)
        if not dm:
            continue
        date = dm.group(1)
        title = dm.group(2).strip()[:60]
        nid = f"update-{date}-{re.sub(r'[^a-zA-Z0-9]', '-', title[:20]).lower()}"
        if nid in node_ids:
            continue
        files = extract_files(section)[:10]
        phases = list(set(re.findall(r'(Phase\s+[\dA-Z.]+)', section)))[:5]
        sum_m = re.search(r'(?:\*\*Summary:\*\*|Summary:)\s*(.+?)(?=\n\*\*|\n##|$)', section, re.DOTALL)
        summary = sum_m.group(1).strip()[:300] if sum_m else ""
        add_node(nid, "update", title, date=date, summary=summary,
                 files_modified=files, phases=phases)
        updates_found += 1
    print(f"  update_log.md: {updates_found} updates")

# --- test_log.md ---
tfile = LOG_DIR / "test_log.md"
if tfile.exists():
    text = tfile.read_text()
    sections = re.split(r'(?=<a id="test-)', text)
    tests_found = 0
    for section in sections:
        anchor = re.search(r'<a id="(test-[^"]+)"></a>', section)
        if not anchor:
            continue
        aid = anchor.group(1)
        title_m = re.search(r'###\s*(.+?)(?:\n|$)', section)
        title = title_m.group(1).strip()[:80] if title_m else aid
        date = parse_date(section)
        if '✅' in section or 'PASS' in section.upper():
            status = "PASS"
        elif '❌' in section or 'FAIL' in section.upper():
            status = "FAIL"
        elif '⚠' in section or 'PARTIAL' in section.upper():
            status = "PARTIAL"
        else:
            status = "UNKNOWN"
        scope_m = re.search(r'(?:Scope|scope):\s*(.+?)(?:\n|$)', section)
        scope = scope_m.group(1).strip()[:200] if scope_m else ""
        issue_m = re.search(r'(?:Related Issue|Link to Issue).*?#([^\s"\)]+)', section)
        update_m = re.search(r'(?:Related Update|Link to Update).*?#([^\s"\)]+)', section)
        nid = f"test-{aid}"
        add_node(nid, "test", title, date=date, result=status, scope=scope)
        tests_found += 1
        if issue_m:
            add_edge(issue_m.group(1), nid, "tested_by")
        if update_m:
            add_edge(update_m.group(1), nid, "verified_by")
    
    date_sections = re.split(r'\n(?=## \d{4}-\d{2}-\d{2})', text)
    for section in date_sections:
        if '<a id="test-' in section:
            continue
        dm = re.search(r'## (\d{4}-\d{2}-\d{2})\s*(.+?)(?:\n|$)', section)
        if not dm:
            continue
        date = dm.group(1)
        title = dm.group(2).strip()[:60]
        nid = f"test-{date}-{re.sub(r'[^a-zA-Z0-9]', '-', title[:20]).lower()}"
        if nid in node_ids:
            continue
        if '✅' in section or 'PASS' in section.upper():
            status = "PASS"
        elif '❌' in section or 'FAIL' in section.upper():
            status = "FAIL"
        elif '⚠' in section or 'PARTIAL' in section.upper():
            status = "PARTIAL"
        else:
            status = "UNKNOWN"
        add_node(nid, "test", title, date=date, result=status)
        tests_found += 1
    print(f"  test_log.md: {tests_found} tests")

# ============================================================
# PHASE 1.2: Parse Workplan & Report Files with Rich Content
# ============================================================
print("\n=== Phase 1.2: Parsing Workplan & Report Files ===")

def parse_file_content(text, parent_nid, file_type, source_name):
    """Generic file content parser - extracts all context as sub-nodes"""
    sub_nodes_created = 0
    
    # --- Extract Sections ---
    sections = extract_sections(text)
    for si, sec in enumerate(sections):
        sid = f"section-{safe_id(source_name)}-{si}"
        add_node(sid, "section", sec["title"][:80],
                 file_type=file_type, source=source_name, order=si)
        add_edge(sid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Timestamps ---
    timestamps = re.findall(r'(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)', text)
    for ti, ts in enumerate(list(set(timestamps))[:10]):
        tsid = f"timestamp-{safe_id(source_name)}-{safe_id(ts)}"
        add_node(tsid, "timestamp", ts, file_type=file_type, source=source_name)
        add_edge(tsid, parent_nid, "mentioned_in")
        sub_nodes_created += 1
    
    # --- Extract Error Codes ---
    error_codes = extract_error_codes(text)
    for ec in error_codes[:15]:
        ec_nid = f"ec-{ec}"
        add_node(ec_nid, "error_code", ec, status="referenced")
        add_edge(ec_nid, parent_nid, "referenced_by")
        sub_nodes_created += 1
    
    # --- Extract Phases ---
    phase_refs = re.findall(r'(?:Phase|Sub-Phase|P)\s*([\dA-Z.]+)', text)
    for pi, pid in enumerate(list(set(phase_refs))[:15]):
        pid = pid.strip()
        if pid.lower() in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            pnid = f"phase-ref-{safe_id(source_name)}-{pid.lower()}"
            add_node(pnid, "phase", f"Phase {pid}", file_type=file_type, source=source_name, phase_id=pid)
            add_edge(pnid, parent_nid, "belongs_to")
            sub_nodes_created += 1
    
    # --- Extract Milestones ---
    milestone_tables = re.findall(r'\|\s*(M\d+[\d.]*)\s*\|\s*([^|]+)\|\s*([^|]+)', text)
    for mi, (mid, mdeliverable, mstatus) in enumerate(milestone_tables[:20]):
        ms = "COMPLETE" if '✅' in mstatus or 'DONE' in mstatus.upper() or 'COMPLETE' in mstatus.upper() else "PENDING"
        mnid = f"milestone-{safe_id(source_name)}-{safe_id(mid)}"
        add_node(mnid, "milestone", f"{mid}: {mdeliverable.strip()[:60]}",
                 milestone_id=mid, status=ms, file_type=file_type, source=source_name)
        add_edge(mnid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Success Criteria ---
    criteria_lines = re.findall(r'-\s*\[([ xX])\]\s*([^\n]+)', text)
    for ci, (ccheck, ctext) in enumerate(criteria_lines[:30]):
        ctext = ctext.strip()
        if not ctext or len(ctext) < 3:
            continue
        cid = f"criteria-{safe_id(source_name)}-{ci}"
        cstatus = "COMPLETE" if ccheck.lower() == 'x' else "PENDING"
        add_node(cid, "criteria", ctext[:80], status=cstatus, file_type=file_type, source=source_name)
        add_edge(cid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Deliverables ---
    del_items = re.findall(r'-\s*\*\*([^*]{3,})\*\*\s*[:\-]\s*([^\n]{3,})', text)
    for dli, (dtitle, ddesc) in enumerate(del_items[:20]):
        dnid = f"deliverable-{safe_id(source_name)}-{dli}"
        add_node(dnid, "deliverable", f"{dtitle.strip()[:60]}: {ddesc.strip()[:40]}",
                 description=ddesc.strip()[:200], file_type=file_type, source=source_name)
        add_edge(dnid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Findings ---
    finding_sections = re.findall(r'(?:Findings|Issues|Recommendations)[^\n]*\n(.+?)(?=\n##|\n---|\Z)', text, re.DOTALL)
    for fi_idx, fs_content in enumerate(finding_sections):
        findings = re.findall(r'\|\s*([^|]{5,})\s*\|\s*([^|]+)\s*\|', fs_content)
        for fi, (ffinding, fresolution) in enumerate(findings[:10]):
            ffinding = ffinding.strip()
            if ffinding.lower() in ['finding', 'issue', 'resolution', 'recommendation', 'finding', 'details']:
                continue
            fnid = f"finding-{safe_id(source_name)}-{fi_idx}-{fi}"
            add_node(fnid, "finding", ffinding[:80],
                     resolution=fresolution.strip()[:150], file_type=file_type, source=source_name)
            add_edge(fnid, parent_nid, "belongs_to")
            sub_nodes_created += 1
    
    # --- Extract Lessons ---
    lessons_sections = re.findall(r'(?:Lessons Learned|Lessons)[^\n]*\n(.+?)(?=\n##|\n---|\Z)', text, re.DOTALL)
    for ls_content in lessons_sections:
        lesson_lines = re.findall(r'-\s*([^\n]+)', ls_content)
        for li, lesson in enumerate(lesson_lines[:10]):
            lesson = lesson.strip()
            if not lesson or len(lesson) < 5:
                continue
            lnid = f"lesson-{safe_id(source_name)}-{li}"
            add_node(lnid, "lesson", lesson[:100], file_type=file_type, source=source_name)
            add_edge(lnid, parent_nid, "belongs_to")
            sub_nodes_created += 1
    
    # --- Extract Steps ---
    step_lines = re.findall(r'(?:\d+\.\s*)([^\n]{5,})', text)
    for sti, step in enumerate(step_lines[:20]):
        step = step.strip()
        if not step or len(step) < 5:
            continue
        stid = f"step-{safe_id(source_name)}-{sti}"
        add_node(stid, "step", step[:80], order=sti, file_type=file_type, source=source_name)
        add_edge(stid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Scopes ---
    scope_sections = re.findall(r'(?:Scope|scope)[:\s]*(.+?)(?:\n|$)', text)
    for sci, scope_text in enumerate(scope_sections[:5]):
        scope_text = scope_text.strip()
        if not scope_text or len(scope_text) < 5:
            continue
        scid = f"scope-{safe_id(source_name)}-{sci}"
        add_node(scid, "scope", scope_text[:80], file_type=file_type, source=source_name)
        add_edge(scid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Reasons ---
    reason_lines = re.findall(r'(?:Reason|reason|Rationale|rationale)[:\s]*(.+?)(?:\n|$)', text)
    for ri, reason in enumerate(reason_lines[:10]):
        reason = reason.strip()
        if not reason or len(reason) < 5:
            continue
        rnid = f"reason-{safe_id(source_name)}-{ri}"
        add_node(rnid, "reason", reason[:80], file_type=file_type, source=source_name)
        add_edge(rnid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Cases ---
    case_lines = re.findall(r'(?:Case|case|Test Case|use case)[:\s]*(.+?)(?:\n|$)', text)
    for cai, case in enumerate(case_lines[:10]):
        case = case.strip()
        if not case or len(case) < 3:
            continue
        cnid = f"case-{safe_id(source_name)}-{cai}"
        add_node(cnid, "case", case[:80], file_type=file_type, source=source_name)
        add_edge(cnid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Scenarios ---
    scenario_lines = re.findall(r'(?:Scenario|scenario)[:\s]*(.+?)(?:\n|$)', text)
    for sni, scenario in enumerate(scenario_lines[:10]):
        scenario = scenario.strip()
        if not scenario or len(scenario) < 3:
            continue
        snid = f"scenario-{safe_id(source_name)}-{sni}"
        add_node(snid, "scenario", scenario[:80], file_type=file_type, source=source_name)
        add_edge(snid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Tables ---
    tables = re.findall(r'(\|[\s\w\-\*\.\(\)/:,]+\|[\s\w\-\*\.\(\)/:,]+\|[\s\w\-\*\.\(\)/:,|]+\|)', text)
    for ti, table in enumerate(tables[:10]):
        # Get table header
        header_m = re.search(r'\|([^|]+)\|([^|]+)\|', table)
        if header_m:
            tlabel = f"Table: {header_m.group(1).strip()[:40]}"
            tnid = f"table-{safe_id(source_name)}-{ti}"
            add_node(tnid, "table", tlabel, file_type=file_type, source=source_name)
            add_edge(tnid, parent_nid, "belongs_to")
            sub_nodes_created += 1
    
    # --- Extract Analysis ---
    analysis_sections = re.findall(r'(?:Analysis|analysis|Detailed Evaluation|detailed evaluation)[^\n]*\n(.+?)(?=\n##|\n---|\Z)', text, re.DOTALL)
    for ai, analysis in enumerate(analysis_sections):
        analysis = analysis.strip()[:200]
        if not analysis or len(analysis) < 10:
            continue
        anid = f"analysis-{safe_id(source_name)}-{ai}"
        add_node(anid, "analysis", analysis[:80], file_type=file_type, source=source_name)
        add_edge(anid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Dependencies ---
    dep_lines = re.findall(r'(?:Depends on|depends on|Dependency|dependency|Requires|requires)[:\s]*(.+?)(?:\n|$)', text)
    for di, dep in enumerate(dep_lines[:10]):
        dep = dep.strip()
        if not dep or len(dep) < 3:
            continue
        dnid = f"dependency-{safe_id(source_name)}-{di}"
        add_node(dnid, "dependency", dep[:80], file_type=file_type, source=source_name)
        add_edge(dnid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Actions/Tasks ---
    task_lines = re.findall(r'(?:\d+\.\s*(?:✅\s*)?)([^\n]{5,})', text)
    for ti, task in enumerate(task_lines[:20]):
        task = task.strip()
        if not task or len(task) < 5:
            continue
        tid = f"action-{safe_id(source_name)}-{ti}"
        tstatus = "COMPLETE" if '✅' in task else "PENDING"
        add_node(tid, "action", task[:80], status=tstatus, file_type=file_type, source=source_name)
        add_edge(tid, parent_nid, "belongs_to")
        sub_nodes_created += 1
    
    # --- Extract Updates/Changes ---
    change_sections = re.findall(r'(?:Changes and Updates|What will be Updated|What Was Changed)[^\n]*\n(.+?)(?=\n\*\*|\n---|\n##|\Z)', text, re.DOTALL)
    for ci, cs_content in enumerate(change_sections):
        change_lines = re.findall(r'-\s*\*\*([^*]+)\*\*\s*[:\-]?\s*([^\n]*)', cs_content)
        if not change_lines:
            change_lines = [(line.strip().lstrip('- ').strip(), '') for line in cs_content.strip().split('\n') if line.strip().startswith('-')]
        for ui, (ul_title, ul_desc) in enumerate(change_lines[:10]):
            ul_title = ul_title.strip()
            if not ul_title:
                continue
            ulid = f"update-{safe_id(source_name)}-{ci}-{ui}"
            add_node(ulid, "update", f"{ul_title[:60]}" + (f": {ul_desc.strip()[:40]}" if ul_desc.strip() else ""),
                     summary=ul_desc.strip()[:200], file_type=file_type, source=source_name)
            add_edge(ulid, parent_nid, "belongs_to")
            sub_nodes_created += 1
    
    # --- Extract Files ---
    files = extract_files(text)
    for fi, fp in enumerate(files[:15]):
        fnid = f"file-{fp.replace('/', '-').replace('.', '_')}"
        if fnid not in node_ids:
            add_node(fnid, "file", fp.split('/')[-1], path=fp, touch_count=1)
        add_edge(fnid, parent_nid, "referenced_by")
        sub_nodes_created += 1
    
    # --- Extract Issues ---
    issue_refs = re.findall(r'(?:issue-?|Issue\s+)([\w-]+)', text)
    for ir in issue_refs[:10]:
        ir = ir.strip()
        if ir and len(ir) > 1 and ir.lower() not in ['log', 'linked', 'related', 'see', 'the', 'and', 'tracking']:
            ir_nid = f"issue-{ir.lower()}"
            if ir_nid in node_ids:
                add_edge(parent_nid, ir_nid, "addresses")
    
    return sub_nodes_created

# Parse workplans
wp_found = 0
for wf in wp_main:
    try:
        text = wf.read_text()
    except:
        continue
    
    wid_m = re.search(r'(?:Document ID|Workplan ID)[\s\*:]*([#\w-]+)', text)
    if not wid_m:
        wid_m = re.search(r'(WP-[\w-]+)', text)
    wid = wid_m.group(1) if wid_m else None
    if not wid and 'workplan' in wf.name.lower():
        wid = wf.stem.replace('_workplan', '').replace('_work_plan', '')
    if not wid:
        continue
    
    ver_m = re.search(r'(?:Current Version|Version)[:\s]*([\d.]+)', text)
    version = ver_m.group(1) if ver_m else "1.0"
    stat_m = re.search(r'\*\*Status:\*\*\s*([^\n*]+)', text)
    status = stat_m.group(1).strip()[:50] if stat_m else "UNKNOWN"
    title_m = re.search(r'#\s+(.+?)(?:\n|$)', text)
    title = title_m.group(1).strip()[:80] if title_m else wf.stem
    date_m = re.search(r'(?:Last Updated|Date)[:\s]*(\d{4}-\d{2}-\d{2})', text)
    date = date_m.group(1) if date_m else parse_date(text)
    rel = str(wf.relative_to(WORKPLAN_DIR))
    domain = rel.split('/')[0] if '/' in rel else "root"
    
    nid = f"wp-{wid.lower().replace(' ', '-')}" if not wid.lower().startswith('wp-') else f"wp-{wid.lower().replace(' ', '-')}"
    add_node(nid, "workplan", title,
             wid=wid, version=version, status=status, date=date,
             domain=domain, path=rel)
    wp_found += 1
    
    # Link to engine
    eng_nid = f"engine-{domain}"
    add_node(eng_nid, "engine", domain.replace('_', ' ').title(), name=domain)
    add_edge(nid, eng_nid, "belongs_to")
    
    # Link to folder
    folder_path = str(wf.parent.relative_to(WORKPLAN_DIR))
    if folder_path in folder_ids:
        add_edge(nid, folder_ids[folder_path], "contained_in")
    
    # Rich content parsing
    subs = parse_file_content(text, nid, "workplan", nid)

print(f"  Workplans parsed: {wp_found}")

# Parse reports
rpt_found = 0
for rf in rpt_files:
    try:
        text = rf.read_text()
    except:
        continue
    
    filename = rf.stem
    title_m = re.search(r'#\s+(.+?)(?:\n|$)', text)
    title = title_m.group(1).strip()[:80] if title_m else filename
    date = parse_date(text)
    rel = str(rf.relative_to(WORKPLAN_DIR))
    
    rpt_id_m = re.search(r'(?:Report ID)[:\s]*([^\n]+)', text)
    rpt_id = rpt_id_m.group(1).strip()[:30] if rpt_id_m else filename
    ver_m = re.search(r'(?:Version|version)[:\s]*([\d.]+)', text)
    version = ver_m.group(1) if ver_m else "1.0"
    stat_m = re.search(r'(?:\*\*Status:\*\*|Status)[:\s\*]*([^\n]+)', text)
    status = stat_m.group(1).strip().strip('*').strip()[:30] if stat_m else "UNKNOWN"
    
    # Find parent workplan
    parent_wp_nid = None
    search_dir = rf.parent
    for _ in range(4):
        wp_candidates = list(search_dir.glob("*workplan*.md")) + list(search_dir.glob("*_work_plan*.md"))
        if wp_candidates:
            for parent_wp in wp_candidates:
                try:
                    ptext = parent_wp.read_text()
                    pwid_m = re.search(r'(?:Document ID|Workplan ID)[\s\*:]*([#\w-]+)', ptext)
                    if pwid_m:
                        pwid = pwid_m.group(1)
                        parent_wp_nid = f"wp-{pwid.lower().replace(' ', '-')}"
                        if parent_wp_nid in node_ids:
                            break
                    pwid = parent_wp.stem.replace('_workplan', '').replace('_work_plan', '')
                    parent_wp_nid = f"wp-{pwid.lower().replace(' ', '-')}"
                    if parent_wp_nid in node_ids:
                        break
                except:
                    pass
            if parent_wp_nid and parent_wp_nid in node_ids:
                break
        if str(search_dir) == str(WORKPLAN_DIR):
            break
        search_dir = search_dir.parent
    
    if not parent_wp_nid:
        wp_ref_m = re.search(r'(?:Workplan Reference|workplan)[:\s]*\[([^\]]+)\]', text)
        if wp_ref_m:
            ref_stem = Path(wp_ref_m.group(1)).stem.replace('_workplan', '').replace('_work_plan', '')
            parent_wp_nid = f"wp-{ref_stem.lower().replace(' ', '-')}"
            if parent_wp_nid not in node_ids:
                parent_wp_nid = None
    
    if not parent_wp_nid:
        wp_id_m = re.search(r'(?:Workplan ID|WP-ID)[:\s\*]*([A-Z][\w-]+)', text)
        if wp_id_m:
            parent_wp_nid = f"wp-{wp_id_m.group(1).lower().replace(' ', '-')}"
            if parent_wp_nid not in node_ids:
                parent_wp_nid = None
    
    if not parent_wp_nid:
        domain = rel.split('/')[0] if '/' in rel else ""
        if domain:
            domain_wps = [n for n in nodes if n['type'] == 'workplan' and n.get('domain') == domain]
            if len(domain_wps) == 1:
                parent_wp_nid = domain_wps[0]['id']
    
    nid = f"report-{filename}"
    add_node(nid, "report", title, date=date, path=rel, filename=filename,
             report_id=rpt_id, version=version, status=status)
    rpt_found += 1
    
    if parent_wp_nid:
        add_edge(nid, parent_wp_nid, "belongs_to")
    
    # Link to folder
    folder_path = str(rf.parent.relative_to(WORKPLAN_DIR))
    if folder_path in folder_ids:
        add_edge(nid, folder_ids[folder_path], "contained_in")
    
    # Rich content parsing
    subs = parse_file_content(text, nid, "report", nid)

print(f"  Reports parsed: {rpt_found}")

# ============================================================
# PHASE 1.3: File Entities from Logs
# ============================================================
print("\n=== Phase 1.3: Extracting File Entities from Logs ===")

file_touch = {}
file_eng = {}
for n in nodes:
    for key in ['files_changed', 'files_modified']:
        for f in (n.get(key) or []):
            if f:
                file_touch[f] = file_touch.get(f, 0) + 1
                for eng in ['core_engine', 'initiation_engine', 'processor_engine', 'reporting_engine',
                            'utility_engine', 'schema_engine', 'mapper_engine', 'ai_ops_engine']:
                    if eng in f:
                        file_eng[f] = eng
                        break

files_added = 0
for fp, count in file_touch.items():
    if count >= 1:
        eng = file_eng.get(fp, "other")
        eng_nid = f"engine-{eng}"
        add_node(eng_nid, "engine", eng.replace('_', ' ').title(), name=eng)
        fnid = f"file-{fp.replace('/', '-').replace('.', '_')}"
        add_node(fnid, "file", fp.split('/')[-1], path=fp, touch_count=count, engine=eng)
        add_edge(fnid, eng_nid, "belongs_to")
        files_added += 1

print(f"  Files extracted: {files_added}")

# ============================================================
# PHASE 1.4: Engine Nodes
# ============================================================
print("\n=== Phase 1.4: Adding Engine Nodes ===")
for eng_id, eng_label in [
    ("core_engine", "Core Engine"), ("initiation_engine", "Initiation Engine"),
    ("processor_engine", "Processor Engine"), ("reporting_engine", "Reporting Engine"),
    ("utility_engine", "Utility Engine"), ("schema_engine", "Schema Engine"),
    ("mapper_engine", "Mapper Engine"), ("ai_ops_engine", "AI Ops Engine"),
]:
    nid = f"engine-{eng_id}"
    if nid in node_ids:
        cc = sum(1 for e in edges if e.get('to') == nid or e.get('from') == nid)
        for n in nodes:
            if n['id'] == nid:
                n['connection_count'] = cc
    else:
        add_node(nid, "engine", eng_label, name=eng_id, connection_count=0)

# ============================================================
# PHASE 1.5: Cross-References
# ============================================================
print("\n=== Phase 1.5: Adding Cross-References ===")

# Issue relationships
if ifile.exists():
    text = ifile.read_text()
    sections = re.split(r'(?=<a id="issue-)', text)
    for section in sections:
        anchor = re.search(r'<a id="(issue-[^"]+)"></a>', section)
        if not anchor:
            continue
        src = f"issue-{anchor.group(1).replace('issue-', '')}"
        if src not in node_ids:
            continue
        rel_m = re.search(r'(?:Related Issues?)[\s:]*\n?(.*?)(?=\n- \[|\n##|\n###|\n<a|$)', section, re.DOTALL)
        if rel_m:
            rids = re.findall(r'([\w-]+(?:-\d+)?)', rel_m.group(1))
            for rid in rids:
                if rid.lower() in ['related', 'issues', 'issue', 'to', 'see', 'and', 'the', 'for', 'workplan', 'link']:
                    continue
                tgt = f"issue-{rid}"
                if tgt in node_ids and tgt != src:
                    add_edge(src, tgt, "related_to")

# Cross-link nodes that reference the same files/phases/issues
print("  Building cross-links...")
file_to_nodes = defaultdict(list)
phase_to_nodes = defaultdict(list)
issue_to_nodes = defaultdict(list)

for e in edges:
    if e['type'] == 'referenced_by':
        file_to_nodes[e['from']].append(e['to'])
    if e['type'] == 'addresses':
        issue_to_nodes[e['to']].append(e['from'])

# Link nodes that reference the same file
for fid, referrers in file_to_nodes.items():
    if len(referrers) > 1:
        for i in range(len(referrers)):
            for j in range(i+1, len(referrers)):
                add_edge(referrers[i], referrers[j], "shares_file")

# Link nodes that address the same issue
for iid, addressers in issue_to_nodes.items():
    if len(addressers) > 1:
        for i in range(len(addressers)):
            for j in range(i+1, len(addressers)):
                add_edge(addressers[i], addressers[j], "related_to")

# ============================================================
# PHASE 1.6: Generate Output
# ============================================================
print("\n=== Phase 1.6: Generating dcc_log_graph.json ===")

type_counts = {}
for n in nodes:
    t = n['type']
    type_counts[t] = type_counts.get(t, 0) + 1

node_types = [
    {"id": "issue", "label": "Issue", "color": "#e74c3c", "shape": "dot", "icon": "🔴"},
    {"id": "update", "label": "Update", "color": "#3498db", "shape": "square", "icon": "🔵"},
    {"id": "test", "label": "Test", "color": "#2ecc71", "shape": "diamond", "icon": "🟢"},
    {"id": "file", "label": "File", "color": "#f1c40f", "shape": "triangle", "icon": "🟡"},
    {"id": "phase", "label": "Phase", "color": "#9b59b6", "shape": "hexagon", "icon": "🟣"},
    {"id": "error_code", "label": "Error Code", "color": "#bdc3c7", "shape": "dot", "icon": "⚪"},
    {"id": "engine", "label": "Engine", "color": "#e67e22", "shape": "dot", "icon": "🟠"},
    {"id": "workplan", "label": "Workplan", "color": "#1abc9c", "shape": "star", "icon": "⭐"},
    {"id": "report", "label": "Report", "color": "#34495e", "shape": "database", "icon": "📄"},
    {"id": "session", "label": "Session", "color": "#95a5a6", "shape": "database", "icon": "💾"},
    {"id": "action", "label": "Action", "color": "#16a085", "shape": "dot", "icon": "📋"},
    {"id": "criteria", "label": "Criteria", "color": "#8e44ad", "shape": "diamond", "icon": "✅"},
    {"id": "milestone", "label": "Milestone", "color": "#2980b9", "shape": "hexagon", "icon": "🏁"},
    {"id": "finding", "label": "Finding", "color": "#c0392b", "shape": "triangle", "icon": "⚠️"},
    {"id": "lesson", "label": "Lesson", "color": "#d35400", "shape": "square", "icon": "💡"},
    {"id": "deliverable", "label": "Deliverable", "color": "#27ae60", "shape": "square", "icon": "📦"},
    {"id": "folder", "label": "Folder", "color": "#7f8c8d", "shape": "box", "icon": "📁"},
    {"id": "section", "label": "Section", "color": "#3498db", "shape": "ellipse", "icon": "📑"},
    {"id": "step", "label": "Step", "color": "#2ecc71", "shape": "dot", "icon": "👣"},
    {"id": "scope", "label": "Scope", "color": "#9b59b6", "shape": "ellipse", "icon": "🎯"},
    {"id": "reason", "label": "Reason", "color": "#e67e22", "shape": "ellipse", "icon": "❓"},
    {"id": "case", "label": "Case", "color": "#1abc9c", "shape": "diamond", "icon": "📋"},
    {"id": "scenario", "label": "Scenario", "color": "#3498db", "shape": "diamond", "icon": "🎭"},
    {"id": "table", "label": "Table", "color": "#95a5a6", "shape": "box", "icon": "📊"},
    {"id": "analysis", "label": "Analysis", "color": "#8e44ad", "shape": "ellipse", "icon": "🔬"},
    {"id": "timestamp", "label": "Timestamp", "color": "#7f8c8d", "shape": "dot", "icon": "🕐"},
    {"id": "dependency", "label": "Dependency", "color": "#e74c3c", "shape": "triangle", "icon": "🔗"},
]

edge_types = [
    {"id": "resolved_by", "label": "Resolved By", "color": "#2ecc71", "dashes": False},
    {"id": "verified_by", "label": "Verified By", "color": "#3498db", "dashes": False},
    {"id": "tested_by", "label": "Tested By", "color": "#2ecc71", "dashes": True},
    {"id": "modifies", "label": "Modifies", "color": "#f1c40f", "dashes": False},
    {"id": "affects", "label": "Affects", "color": "#e74c3c", "dashes": False},
    {"id": "related_to", "label": "Related To", "color": "#95a5a6", "dashes": True},
    {"id": "blocks", "label": "Blocks", "color": "#e74c3c", "dashes": False, "arrows": "to"},
    {"id": "depends_on", "label": "Depends On", "color": "#f39c12", "dashes": False, "arrows": "to"},
    {"id": "implements", "label": "Implements", "color": "#9b59b6", "dashes": False},
    {"id": "belongs_to", "label": "Belongs To", "color": "#1abc9c", "dashes": True},
    {"id": "introduces", "label": "Introduces", "color": "#e74c3c", "dashes": False},
    {"id": "fixes", "label": "Fixes", "color": "#2ecc71", "dashes": False},
    {"id": "session_for", "label": "Session For", "color": "#95a5a6", "dashes": True},
    {"id": "addresses", "label": "Addresses", "color": "#1abc9c", "dashes": False, "arrows": "to"},
    {"id": "references", "label": "References", "color": "#95a5a6", "dashes": True, "arrows": "to"},
    {"id": "documented_by", "label": "Documented By", "color": "#34495e", "dashes": False},
    {"id": "contained_in", "label": "Contained In", "color": "#7f8c8d", "dashes": True},
    {"id": "contains", "label": "Contains", "color": "#7f8c8d", "dashes": False},
    {"id": "referenced_by", "label": "Referenced By", "color": "#f1c40f", "dashes": True},
    {"id": "mentioned_in", "label": "Mentioned In", "color": "#bdc3c7", "dashes": True},
    {"id": "shares_file", "label": "Shares File", "color": "#f1c40f", "dashes": True},
]

clean_nodes = [{k: v for k, v in n.items() if v is not None} for n in nodes]
valid_edges = [e for e in edges if e['from'] in node_ids and e['to'] in node_ids]

graph_data = {
    "$schema": "https://dcc-pipeline.internal/schemas/log_neurogram/v1",
    "metadata": {
        "generated": datetime.now().isoformat(),
        "source_logs": ["issue_log.md", "update_log.md", "test_log.md", "gemini.md"],
        "source_workplans": f"dcc/workplan/ ({len(wp_main)} files, {len(set(str(f.relative_to(WORKPLAN_DIR).parts[0]) for f in wp_main))} domain folders)",
        "date_range": {"start": "2026-04-12", "end": "2026-05-21"},
        "counts": {"nodes": len(clean_nodes), "edges": len(valid_edges), **type_counts}
    },
    "node_types": node_types,
    "edge_types": edge_types,
    "nodes": clean_nodes,
    "edges": valid_edges,
}

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(graph_data, f, indent=2, default=str)

print(f"\n=== Generation Complete ===")
print(f"  Output: {OUTPUT_FILE}")
print(f"  Nodes: {len(clean_nodes)}")
print(f"  Edges: {len(valid_edges)}")
print(f"  Type breakdown: {dict(sorted(type_counts.items()))}")

orphan = [e for e in edges if e['from'] not in node_ids or e['to'] not in node_ids]
if orphan:
    print(f"  Warning: {len(orphan)} orphan edges removed")
    for e in orphan[:5]:
        print(f"    {e['from']} -> {e['to']} ({e['type']})")
