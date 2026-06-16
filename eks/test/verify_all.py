results = {}

with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()
results['p4_version_0.4']      = 'Current Version**: 0.4' in c
results['p4_R40_scope']        = 'R40 | Retrieval Pipeline' in c
results['p4_T4.19']            = 'T4.19' in c
results['p4_eks_assets']       = 'eks_assets' in c
results['p4_dual_criteria']    = 'dual-collection' in c

with open('eks/log/update_log.md', 'r', encoding='utf-8') as f:
    c = f.read()
results['log_U022']            = 'U022' in c

with open('eks/workplan/eks_system_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()
results['master_section10']    = '## 10. EKS Pipeline Architecture' in c
results['master_R40']          = 'R40 | Embedding' in c
results['master_R41']          = 'R41 | Knowledge Base' in c
results['master_R42']          = 'R42 | Knowledge Base' in c
results['master_version_0.7']  = 'Current Version**: 0.7' in c

with open('eks/workplan/phase_2_chunking_embedding_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()
results['p2_version_0.3']      = 'Current Version**: 0.3' in c
results['p2_T2.16']            = 'T2.16' in c
results['p2_T2.17']            = 'T2.17' in c
results['p2_T2.18']            = 'T2.18' in c

with open('eks/workplan/phase_3_knowledge_graph_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()
results['p3_version_0.5']      = 'Current Version**: 0.5' in c
results['p3_T3.20']            = 'T3.20' in c
results['p3_R42']              = 'R42 | Knowledge Base' in c

with open('eks/test/verify_results.txt', 'w', encoding='utf-8') as f:
    all_pass = True
    for k, v in results.items():
        status = 'PASS' if v else 'FAIL'
        if not v:
            all_pass = False
        f.write(f"{status}: {k}\n")
    f.write(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES FOUND'}\n")
print("Written to eks/test/verify_results.txt")
