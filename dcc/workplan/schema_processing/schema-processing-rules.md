# 📚 DCC Schema & Processing Rules Book

*Created: 2026-03-29*  
*Purpose: Comprehensive documentation of all schema and processing rules discussed during DCC project development*

---

## 🎯 Forward Fill Strategies

### **Rule 1: Forward Fill by Itself**
**When to use:** Original code uses `ffill()` without any grouping  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "forward_fill",
  "group_by": [],  // Empty array = forward fill by itself (sequential down column)
  "fill_value": "value",
  "description": "Forward fill by itself (sequential) per original logic"
}
```

**Example:** `Submission_Session` column
```python
# Original dcc_mdl.ipynb
df_cleaned_and_filtered['Submission_Session'] = df_cleaned_and_filtered['Submission_Session'].ffill().astype(int).astype(str).str.zfill(6)

# Enhanced Schema
"group_by": []
```

### **Rule 2: Forward Fill by Group**
**When to use:** Original code uses `groupby('Column').ffill()`  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "forward_fill", 
  "group_by": ["Column_Name"],  // Specific column = forward fill within groups
  "fill_value": "value",
  "na_fallback": true,
  "description": "Forward fill by [Column_Name] per original logic"
}
```

**Example:** `Submission_Session_Revision` column
```python
# Original dcc_mdl.ipynb
df_cleaned_and_filtered['Submission_Session_Revision'] = df_cleaned_and_filtered.groupby('Submission_Session')['Submission_Session_Revision'].ffill().fillna(0).astype(int).astype(str).str.zfill(2)

# Enhanced Schema
"group_by": ["Submission_Session"]
```

### **Rule 3: Forward Fill by Document_ID (Default)**
**When to use:** Most document-level columns, no specific grouping in original code  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "forward_fill",
  // No group_by specified = defaults to Document_ID grouping
  "fill_value": "value",
  "na_fallback": true,
  "description": "Forward fill within same document per original logic"
}
```

**Example:** `Submitted_By`, `Reviewer`, `Department` columns

---

## 🔧 Null Handling Strategies

### **Rule 4: Default Value Strategy**
**When to use:** Original code uses `fillna('value')` for Document_ID components  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "default_value",
  "default_value": "NA",
  "description": "Fill with NA for Document_ID calculation per original dcc_mdl.ipynb logic"
}
```

**Example:** Document_ID component columns
```python
# Original dcc_mdl.ipynb
df_cleaned_and_filtered['Project_Code'] = df_cleaned_and_filtered['Project_Code'].fillna('NA')
df_cleaned_and_filtered['Facility_Code'] = df_cleaned_and_filtered['Facility_Code'].fillna('NA')
df_cleaned_and_filtered['Document_Type'] = df_cleaned_and_filtered['Document_Type'].fillna('NA')
df_cleaned_and_filtered['Discipline'] = df_cleaned_and_filtered['Discipline'].fillna('NA')
df_cleaned_and_filtered['Document_Sequence_Number'] = df_cleaned_and_filtered['Document_Sequence_Number'].fillna('NA')

# Enhanced Schema - All use default_value strategy
```

### **Rule 5: Leave Null Strategy**
**When to use:** Primary data columns that should not be modified or calculated  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "leave_null",
  "description": "Leave null as this is primary data from Excel"
}
```

**Example:** `Document_Revision`, `Submission_Session_Subject` when available in Excel

### **Rule 6: Calculate If Null Strategy**
**When to use:** Calculated columns like Document_ID  
**Schema configuration:**
```json
"null_handling": {
  "strategy": "calculate_if_null",
  "calculation": {
    "type": "composite",
    "method": "build_document_id",
    "source_columns": ["Project_Code", "Facility_Code", "Document_Type", "Document_Sequence_Number"],
    "format": "{Project_Code}-{Facility_Code}-{Document_Type}-{Document_Sequence_Number}",
    "fallback_value": "UNKNOWN-DOC-ID"
  }
}
```

---

## 📊 Column Requirements

### **Rule 7: Document_ID Component Columns**
**Rule:** All Document_ID components must be `required: true` and `allow_null: false`  
**Schema configuration:**
```json
{
  "required": true,
  "allow_null": false,
  "null_handling": {
    "strategy": "default_value",
    "default_value": "NA"
  }
}
```

**Columns:** `Project_Code`, `Facility_Code`, `Document_Type`, `Discipline`, `Document_Sequence_Number`

### **Rule 8: Missing Columns in Data**
**Rule:** Columns not available in actual Excel data should be `required: false` and `allow_null: true`  
**Schema configuration:**
```json
{
  "required": false,
  "allow_null": true,
  "null_handling": {
    "strategy": "leave_null",
    "description": "Leave null as this column is not available in current data structure"
  }
}
```

**Example:** `Document_Title` (missing from current Excel data)

---

## 🔢 Data Formatting Rules

### **Rule 9: Zero Padding (zfill)**
**When to use:** Original code uses `.str.zfill(n)` after type conversion  
**Processing flow in enhanced schema:**
1. Apply null handling strategy
2. Convert to int
3. Convert to string  
4. Apply zfill formatting

**Examples:**
- `Document_Sequence_Number`: zfill(4) → "0001"
- `Submission_Session`: zfill(6) → "000123"
- `Submission_Session_Revision`: zfill(2) → "01"

### **Rule 10: Type Conversion Pattern**
**Original pattern:** `.astype(int).astype(str).str.zfill(n)`  
**Enhanced schema equivalent:** Configure appropriate null handling + validation pattern

---

## 🎯 Column Sequence Rules

### **Rule 11: Processing Order Priority**
**Rule:** Columns must be sequenced to respect data dependencies  
**Optimal sequence:**
1. **Document_ID Components** (Project_Code, Facility_Code, Document_Type, Discipline, Document_Sequence_Number)
2. **Primary Document ID** (Document_ID)
3. **Document Details** (Document_Revision, Document_Title)
4. **Submission Session Data** (Submission_Session, Submission_Session_Revision, Submission_Session_Subject)
5. **Primary Data Columns** (Transmittal_Number, Department, Submitted_By, Submission_Date)
6. **Calculated Submission Data** (First_*, Latest_*, All_*)
7. **Review Information** (Reviewer, Review_Return_Actual_Date, Review_Status)
8. **Calculated Approvals** (Approval_Code, Latest_Approval_Status, All_Approval_Code)
9. **Status & Resubmission** (Submission_Closed, Resubmission_Required, Resubmission_Plan_Date)
10. **References & Notes** (Submission_Reference_1, Internal_Reference, Notes)
11. **This Submission Calculations** (This_Submission_*, This_Review_*, This_Submission_Approval_*)

---

## 🚫 Error Prevention Rules

### **Rule 12: KeyError Prevention**
**Rule:** Never reference non-existent columns in null handling copy_from strategies  
**Wrong:**
```json
"null_handling": {
  "strategy": "copy_from",
  "source_column": "Document_Title"  // If Document_Title doesn't exist
}
```

**Right:**
```json
"null_handling": {
  "strategy": "leave_null"
}
```

### **Rule 13: Column Renaming Requirement**
**Rule:** Always rename DataFrame columns to schema names before processing  
**Processing flow:**
1. Load Excel data with original headers
2. Apply column mapping (fuzzy matching)
3. **Rename columns to schema names** (critical step)
4. Apply document processing

### **Rule 20: Review_Status vs Approval_Status Distinction**
**Rule:** Review_Status and Approval_Status are different concepts and should not be confused  
**Key Differences:**
- **Review_Status**: Current review status of a specific submission (Approved, Rejected, Pending, etc.)
- **Approval_Status**: Overall approval status of the entire document (may aggregate multiple reviews)

**Schema Configuration:**
```json
// Review_Status - Primary data column with forward fill
"Review_Status": {
  "data_type": "categorical",
  "is_calculated": false,
  "null_handling": {
    "strategy": "forward_fill",
    "group_by": ["Submission_Session", "Submission_Session_Revision"],
    "fill_value": "Pending"
  }
}

// Approval_Status - Calculated aggregate column
"Approval_Status": {
  "data_type": "categorical", 
  "is_calculated": true,
  "calculation": {
    "type": "aggregate",
    "method": "latest_by_date",
    "source_column": "Review_Status"
  }
}
```

**Processing Logic:**
- **Review_Status**: Forward filled within submission sessions, represents current review state
- **Approval_Status**: Latest review status for the document, may come from any submission

**Common Mistake to Avoid:**
```json
// WRONG - Don't use Review_Status as Approval_Status
"Approval_Status": {
  "source_column": "Review_Status"  // This confuses the concepts
}

// RIGHT - Use proper aggregation for Approval_Status  
"Approval_Status": {
  "calculation": {
    "type": "aggregate",
    "method": "latest_by_date",
    "source_column": "Review_Status",
    "group_by": ["Document_ID"]
  }
}
```

---

## 📝 Schema Validation Rules

### **Rule 14: Pattern Matching**
**Rule:** Use appropriate regex patterns for column validation  
**Common patterns:**
- Document identifiers: `^[A-Z0-9-]+$`
- Numbers: `^[0-9]*$`
- Revision numbers: `^[A-Z0-9.]*$`
- Alphanumeric codes: `^[A-Z0-9-]*$`

### **Rule 15: Required vs Allow_Null**
**Rule:** Be explicit about column requirements  
- **Primary data from Excel**: `required: false`, `allow_null: true`
- **Document_ID components**: `required: true`, `allow_null: false` (with default_value)
- **Calculated columns**: `required: false`, `allow_null: true`
- **Missing columns**: `required: false`, `allow_null: true`

---

## 🔍 Debugging Rules

### **Rule 16: Column Analysis**
**Rule:** Always analyze actual Excel columns before schema updates  
**Analysis steps:**
1. Extract actual Excel column headers
2. Compare with schema requirements
3. Identify missing vs available columns
4. Update schema accordingly

### **Rule 17: Schema Validation**
**Rule:** Validate schema against original dcc_mdl.ipynb logic  
**Validation checklist:**
- [ ] Column mapping matches original aliases
- [ ] Null handling strategies match original processing
- [ ] Data formatting matches original type conversions
- [ ] Column sequence respects dependencies
- [ ] No references to non-existent columns

---

## 🛠️ Tool Usage Rules

### **Rule 18: Consolidated Setup Tools**
**Rule:** Use `tools/project_setup_tools.py` for all setup and analysis tasks  
**Available commands:**
```bash
python tools/project_setup_tools.py complete     # Full analysis
python tools/project_setup_tools.py analyze     # Column analysis
python tools/project_setup_tools.py compare     # Handling comparison
python tools/project_setup_tools.py validate    # Document_ID validation
python tools/project_setup_tools.py sequence    # Column sequence
python tools/project_setup_tools.py reorganize  # Schema reorganization
```

### **Rule 19: Master Registry**
**Rule:** All components must be registered in `config/master_registry.json`  
**Registry sections:**
- `document_types`: All schema files
- `tools`: All processing tools with functions
- `workflows`: All notebook workflows
- `documentation`: All documentation files

### **Rule 21: Schema Column Addition Rule**
**Rule:** When adding new column schemas, always update project_setup_tools.py  
**Required Updates:**
```python
# 1. Add to original_schema dictionary in DCCProjectSetupTools.__init__
self.original_schema = {
    # ... existing columns ...
    "New_Column": ["Excel Header 1", "Excel Header 2"],
}

# 2. Add to new_sequence list
self.new_sequence = [
    # ... existing columns ...
    "New_Column",  # Add in appropriate position
]

# 3. Update analyze_columns() method if needed
# 4. Update compare_column_handling() method if needed
# 5. Update validate_document_id_logic() method if needed
```

**Update Checklist:**
- [ ] Add column aliases to `original_schema`
- [ ] Add column to `new_sequence` in correct position
- [ ] Update column analysis if column has special handling
- [ ] Update validation logic if column affects Document_ID or calculations
- [ ] Test with `python tools/project_setup_tools.py complete`

**Why This Rule:**
- Ensures setup tools recognize new columns
- Maintains consistency between schema and tools
- Prevents analysis gaps for new columns
- Enables proper validation and comparison

---

## 📋 Quick Reference

### **Forward Fill Decision Tree:**
```
Original code: df['col'].ffill() → Use group_by: []
Original code: df.groupby('X')['col'].ffill() → Use group_by: ["X"]
Original code: No specific ffill → Use default (Document_ID)
```

### **Null Handling Decision Tree:**
```
Original code: fillna('value') → Use default_value strategy
Original code: No null handling → Use leave_null strategy
Original code: Calculation needed → Use calculate_if_null strategy
```

### **Column Requirements Decision Tree:**
```
Column in Excel data → required: false, allow_null: true
Column missing from data → required: false, allow_null: true
Document_ID component → required: true, allow_null: false
```

---

## 🎯 Summary

This rule book captures all schema and processing rules established during DCC project development. Always reference these rules when:

1. **Updating schema configurations**
2. **Adding new columns**  
3. **Debugging processing issues**
4. **Validating against original logic**
5. **Setting up new document types**

**Key Principle:** Always match the original dcc_mdl.ipynb logic exactly when configuring enhanced schema processing.

---

*Last Updated: 2026-03-29*  
*Total Rules: 19*
