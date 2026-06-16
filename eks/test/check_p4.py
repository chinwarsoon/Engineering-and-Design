with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Show context around R38 scope area
idx = c.find('R38 | Retrieval Pipeline')
print("R38 context:")
print(repr(c[idx:idx+300]))
print()

# Check if R40 scope row already present in any form
print("R40 in file:", 'R40' in c)
idx2 = c.find('Status Legend')
print("Status Legend context:")
print(repr(c[idx2-200:idx2+50]))
