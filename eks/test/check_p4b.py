with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('R38 | Retrieval Pipeline')
context = c[idx:idx+400] if idx != -1 else "R38 NOT FOUND"

with open('eks/test/p4_context.txt', 'w', encoding='utf-8') as f:
    f.write(context)

# R40 already present anywhere?
with open('eks/test/p4_r40_check.txt', 'w', encoding='utf-8') as f:
    f.write(f"R40 present: {'R40' in c}\n")
    f.write(f"R40 | Retrieval: {'R40 | Retrieval Pipeline' in c}\n")
    # Try adding R40 scope row if not present
    target = '**Status Legend:** ✅ PASS | 🔶 PARTIAL | ❌ FAIL | 🔷 PLANNED'
    f.write(f"Status Legend found: {target in c}\n")

print("done")
