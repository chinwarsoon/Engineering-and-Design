# Document_ID Affix Handling - Implementation Workplan

## 1. Business Rules for Affix Handling

1. **Identify affixes** in the Document_ID that appear after the standard 5-segment format
2. **Strip affixes** from Document_ID before validation against schema pattern
3. **Store affixes** in a separate data field named `Document_ID_Affixes` (string)
4. **Validate base ID** using `dcc_register_enhanced.json` schema `derived_pattern` (without affixes)
5. **Dynamic affix detection** - affixes may start with `_`, `-`, or other separator characters
6. **Affix location** - always at the end of Document_ID, user input may contain any characters
7. **Data preservation** - follow `dcc_register_enhanced.json` overwriting rules for user input
8. **Column placement** - `Document_ID_Affixes` immediately after `Document_ID` column
9. **Processing phase** - Phase 2.5 (same as Document_ID validation)

---

## 2. Examples of Document_ID with Affixes

| Raw Input | Base Document_ID | Affix | Notes |
|-----------|------------------|-------|-------|
| `131242-WSD11-CL-P-0009_ST607` | `131242-WSD11-CL-P-0009` | `"_ST607"` | Single underscore affix |
| `131242-WSD11-CL-P-0009_ST608_BCA` | `131242-WSD11-CL-P-0009` | `"_ST608_BCA"` | Underscore with multiple segments |
| `131242-WSD11-CL-P-0009_MS2` | `131242-WSD11-CL-P-0009` | `"_MS2"` | Status/tracking code |
| `131242-WSD11-CL-P-0009_Withdrawn` | `131242-WSD11-CL-P-0009` | `"_Withdrawn"` | Workflow status |
| `131242-WSD11-CL-P-0009-V1` | `131242-WSD11-CL-P-0009` | `"-V1"` | Hyphen separator (revision suffix) |

---

## 3. Technical Implementation Plan

### Phase 1: Schema Updates

**File:** `dcc_register_enhanced.json`

1. Add new column `Document_ID_Affixes` after `Document_ID` in `column_sequence`
   - `data_type`: `string`
   - `is_calculated`: `true`
   - `processing_phase`: `P2.5`
   - `calculation.type`: `extract_affixes`
   - `calculation.source_column`: `Document_ID`
   - `null_handling.strategy`: `default_value`
   - `null_handling.default_value`: `""` (empty string)

2. Update `Document_ID` column strategy
   - Add `affix_extraction` to `calculation` configuration
   - Ensure validation happens on base ID (without affixes)

### Phase 2: Core Extraction Logic

**New File:** `processor_engine/calculations/affix_extractor.py`

```python
def extract_document_id_affixes(
    document_id: str,
    delimiter: str = '-',
    sequence_length: int = 4
) -> Tuple[str, str]:
    """
    Extract affixes from Document_ID using schema-driven parameters.
    
    Algorithm:
    1. Split Document_ID by delimiter (from schema)
    2. Extract Document_Sequence_Number from last segment (first N chars)
    3. Remaining chars in last segment = affix
    4. Return base Document_ID and affix string
    
    Schema Parameters:
        - delimiter: from Document_ID.validation.derived_pattern.separator (default: "-")
        - sequence_length: from Document_Sequence_Number validation pattern (default: 4)
    
    Returns:
        (base_document_id, affix)
    """
```

**Affix Detection Rules:**
- Base pattern: 5 segments separated by `-`
- Segment 5 (Document_Sequence_Number): exactly 4 digits
- Affix separator: first non-matching character after valid base
- Common separators: `_`, `-`, ` `, `.`
- Affix may contain any characters after separator

### Phase 3: Integration Points ✅ COMPLETE

**File:** `processor_engine/error_handling/detectors/identity.py`

✅ Implemented: `_detect_invalid_id_format()` modifications
   - Added `extract_document_id_affixes` import with HAS_AFFIX_EXTRACTOR flag
   - Added `_get_affix_extraction_params()` method to read from schema:
     - `delimiter` from `Document_ID.validation.derived_pattern.separator`
     - `sequence_length` from `Document_Sequence_Number.validation.pattern` (parse `^[0-9]{4}$` → 4)
   - Modified `_detect_invalid_id_format()` to:
     - Call `extract_document_id_affixes()` with schema parameters
     - Validate base ID (without affix) using `get_derived_pattern_regex()`
     - Include affix info in error context for debugging
   - Updated docstring to reference Issue #16

### Phase 4: Column Calculation 

**File:** `processor_engine/calculations/validation.py` 

✅ Implemented: Modified `derived_pattern` validation for Document_ID
   - Added import for `extract_document_id_affixes` with `HAS_AFFIX_EXTRACTOR` flag
   - Added helper function `_get_sequence_length_from_schema()` to extract sequence length from `Document_Sequence_Number.validation.pattern`
   - Modified `derived_pattern` validation block (lines 270-344) to:
     - Check if affix extraction enabled: `HAS_AFFIX_EXTRACTOR && column_name == 'Document_ID' && 'Document_ID_Affixes' in df`
     - Extract affixes for all rows using `extract_document_id_affixes()` with schema-driven `delimiter` and `sequence_length`
     - Store affixes in `Document_ID_Affixes` column
     - Use base ID (without affix) for `derived_pattern` validation
     - Cleanup temp columns after validation
   - Enhanced error logging to include sample bases and affixes for debugging

**File:** `processor_engine/calculations/calculation_engine.py`  

1. Add `extract_affixes` calculation method (if needed for explicit calculation)
2. Current implementation: Affix extraction runs during validation phase (P4), which executes after calculations

### Calculation Flow

```
Input: Document_ID with affixes
  ↓
[Step 1] Extract affixes → (base_id, affixes)
  ↓
[Step 2] Store affixes in Document_ID_Affixes column
  ↓
[Step 3] Validate base_id against derived_pattern
  ↓
[Step 4] Store validated base_id back to Document_ID
```

---

## 4. Implementation Phases

| Phase | Task | Estimated Effort | Dependencies |
|-------|------|------------------|--------------|
| 1 | Schema: Add Document_ID_Affixes column | 30 min | None |
| 2 | Logic: Create affix_extractor.py | 1 hour | None |
| 3 | Integration: Update identity.py validation | 1 hour | Phase 2 |
| 4 | Integration: Update validation.py | 1 hour | Phase 2 |
| 5 | Integration: Add to CalculationEngine | 1 hour | Phase 2,3,4 |
| 6 | Testing: Unit tests for affix extraction | 1 hour | Phase 2 |
| 7 | Testing: Pipeline integration test | 30 min | Phase 5 |
| 8 | Documentation: Update logs (issue/update/test) | 30 min | Phase 7 |

**Total Estimated Time:** ~6 hours

---

## 5. Validation & Testing Plan

### Test Cases

| Test ID | Input | Expected Base | Expected Affixes | Pass Criteria |
|---------|-------|---------------|------------------|---------------|
| AFF-001 | `131242-WSD11-CL-P-0009_ST607` | `131242-WSD11-CL-P-0009` | `"_ST607"` | Base passes validation |
| AFF-002 | `131242-WSD11-CL-P-0009_ST608_BCA` | `131242-WSD11-CL-P-0009` | `"_ST608_BCA"` | Base passes validation |
| AFF-003 | `131242-WSD11-CL-P-0009` | `131242-WSD11-CL-P-0009` | `""` | No affix, normal case |
| AFF-004 | `131242-WSD11-CL-P-0009_Withdrawn` | `131242-WSD11-CL-P-0009` | `"_Withdrawn"` | Text affix handled |
| AFF-005 | `131242-WSD11-CL-P-0009-V1` | `131242-WSD11-CL-P-0009` | `"-V1"` | Hyphen separator |
| AFF-006 | `INVALID-ID_ST607` | (validation fails) | `"_ST607"` | Invalid base ID still extracts affix |

### Error Handling

- **Invalid base format**: Still extract affixes, report P2-I-V-0204 error
- **Multiple affixes**: Store as single string (e.g., `_ST608_BCA`)
- **Empty affix**: Return empty string `""`
- **Null input**: Return `""` or handle per null strategy

---

## 6. Related Files

- `dcc/config/schemas/dcc_register_enhanced.json` - Schema definition
- `dcc/workflow/processor_engine/calculations/affix_extractor.py` - New extraction logic
- `dcc/workflow/processor_engine/calculations/validation.py` - Validation integration
- `dcc/workflow/processor_engine/error_handling/detectors/identity.py` - Phase 2 validation
- `dcc/workflow/processor_engine/core/engine.py` - Calculation engine integration
- `dcc/Log/issue_log.md` - Issue #16 tracking
- `dcc/Log/update_log.md` - Implementation changelog
- `dcc/Log/test_log.md` - Test results

---

## 7. Success Criteria

1. ✅ Document_IDs with affixes pass validation (base ID validated)
2. ✅ Affixes extracted and stored in `Document_ID_Affixes` column
3. ✅ No P2-I-V-0204 false positives for valid IDs with affixes
4. ✅ Pipeline processes 11,099 rows without errors
5. ✅ Original Document_ID preserved with affixes intact (or per overwrite rules)
6. ✅ Backward compatible: IDs without affixes work as before

---

*Last Updated: 2026-04-12*
*Related Issue: #16*

