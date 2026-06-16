with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('Status Legend')
with open('eks/test/p4_legend.txt', 'w', encoding='utf-8') as f:
    f.write(repr(c[idx-250:idx+60]))
print("done")
