# Workplan: Appendix B B2.1 and B3.2 Alignment Fix

**Created**: 2026-08-04  
**Author**: Franklin Song  
**Phase**: Documentation Alignment  
**Status**: 🔷 Pending Approval  
**Related Appendix**: `appendix_b_document_registry.md`

---

## Background

Cross-source alignment audit (AGENTS.md §5.13) identified critical misalignment between:
- **Section B2.1** (Registry Structure) - Registry/database-centric structure
- **Section B3.2** (Enrich Document Type into a knowledge ontology) - Semantic/ontology-centric structure

These sections describe the same document type system with inconsistent terminology, missing cross-references, and structural model mismatch. This violates the SSOT principle and creates implementation confusion.

---

## Objectives

1. Unify B2.1 and B3.2 into a single coherent structure serving both registry and ontology purposes
2. Standardize terminology across both sections
3. Add cross-references between classification hierarchy (B3.1) and detailed definition (B2.1)
4. Align component coverage - ensure all components from both sections are preserved
5. Clarify scope between registry implementation and semantic ontology concerns

---

## Proposed Changes

### 1. Create Unified B2.1 Structure

Replace current B2.1 with 7 functional domains:

```
Document Type Definition
├── 1. Identity & Classification
├── 2. Structural Characteristics
├── 3. Document Semantics
├── 4. Processing Profiles
├── 5. Knowledge Relationships
├── 6. Lifecycle & Governance
└── 7. Capabilities & Extensions
```

**Component Mapping**:
- Identity & Classification: B2.1 Identity + Classification + B3.2 Document Identity
- Structural Characteristics: B2.1 Structure + B3.2 Structural Characteristics
- Document Semantics: B3.2 Document Semantics (new, not in B2.1)
- Processing Profiles: B2.1 Processing Profile Registry + B3.2 Extraction Strategy + Retrieval Behaviour
- Knowledge Relationships: B2.1 Relationships + B3.2 Knowledge Relationships
- Lifecycle & Governance: B2.1 Lifecycle + Governance + B3.2 Document Identity (partial)
- Capabilities & Extensions: B2.1 Capabilities

### 2. Deprecate B3.2 Section

Remove B3.2 as a separate section. Add migration note:
> "The content previously in B3.2 has been merged into B2.1 §Unified Document Type Definition."

### 3. Update B3.1 Cross-References

Add cross-reference in B3.1:
> "For detailed document type definition structure, see B2.1 §Unified Document Type Definition."

### 4. Update B4 Schema References

Add mapping table in B4 showing how registry columns map to the unified document type definition structure.

### 5. Archive Current Version

Move current `appendix_b_document_registry.md` to `eks/archive/appendix_b_document_registry_v2.0.0_2026-08-04.md` before creating new version.

---

## Implementation Steps

| Step | Action | Status |
|:-----|:-------|:--------|
| 1 | Archive current appendix_b_document_registry.md to archive/ | 🔷 Pending Approval |
| 2 | Create new appendix B with unified B2.1 structure | 🔷 Pending Approval |
| 3 | Remove deprecated B3.2 content, add migration note | 🔷 Pending Approval |
| 4 | Update B3.1 cross-references to B2.1 | 🔷 Pending Approval |
| 5 | Update B4 schema references to unified structure | 🔷 Pending Approval |
| 6 | Add revision metadata (v2.1.0, 2026-08-04, Franklin Song) | 🔷 Pending Approval |
| 7 | Cross-source alignment audit verification | 🔷 Pending Approval |
| 8 | Update configuration files if needed (eks_doc_config.json) | 🔷 Pending Approval |

---

## Risk Assessment

| Risk | Mitigation |
|:-----|:-----------|
| Breaking existing code references | Keep field names from B2.1 where possible; add migration notes |
| Configuration file misalignment | Audit eks_doc_config.json after merge; update field names if needed |
| Test failures | Run full test suite after changes; update tests if field names changed |
| Documentation confusion | Add clear revision history and migration notes |

---

## Success Criteria

- [ ] Single unified B2.1 structure with all 7 functional domains
- [ ] B3.2 deprecated with migration note
- [ ] B3.1 cross-references B2.1
- [ ] B4 schema references aligned with unified structure
- [ ] All components from both original sections preserved
- [ ] Terminology standardized across document
- [ ] Cross-source alignment audit passes
- [ ] Configuration files aligned (if changes needed)
- [ ] User review and approval obtained

---

## References

- AGENTS.md §5.13: Cross-source alignment audit
- AGENTS.md §5.2: No edits without approval
- AGENTS.md §5.3: Archive before delete
- Appendix B §B2.1: Registry Structure (current)
- Appendix B §B3.2: Enrich Document Type into a knowledge ontology (current)
