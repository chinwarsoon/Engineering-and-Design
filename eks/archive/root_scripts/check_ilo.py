with open('eks/log/phase1/p1_issue_log.md', 'rb') as f:
    content = f.read()
lines = content.split(b'\n')
# Look for I315 and I316 in the priority resolution sequence (lines 60+)
for i in range(58, len(lines)):
    line = lines[i].decode('utf-8', errors='replace')
    if 'I315' in line or 'I316' in line:
        # Check if it has the Seq/Priority format (table rows)
        if '|' in line and 'Seq' not in line:
            print(f'Line {i+1}: {line[:150]}')