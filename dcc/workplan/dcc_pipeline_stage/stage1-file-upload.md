# Stage 1: File Upload

```mermaid
graph TD
    %% Stage Definition
    Stage1[Stage 1: File Upload] --> Input1[Input: Excel File]
    Input1 --> Process1[Processing: XLSX Parsing]
    Process1 --> Output1[Output: Workbook Object]
    
    %% UI Components
    upload --> FileUpload[File Upload Handler]
    FileUpload --> addEventListener[addEventListener change]
    addEventListener --> LoadExcel[Load Excel File]
    
    %% Data Flow
    ExcelFile[User Selects Excel File] --> FileUpload
    LoadExcel --> XLSXParser[XLSX Library]
    XLSXParser --> Workbook[Workbook Object]
    Workbook --> Sheets[Sheet Collection]
    
    %% Expected Outputs
    FileUpload --> ParseSuccess[File Successfully Parsed]
    ParseSuccess --> WorkbookReady[Workbook Object Ready]
    WorkbookReady --> SheetList[Available Sheets List]
```

## Event Handlers

### **File Upload Events**
- **File Selection**: `addEventListener change` on `#upload` - Triggers when user selects Excel file
- **File Parsing**: XLSX automatically parses the uploaded file
- **Workbook Creation**: Creates workbook object containing all sheets

### **Expected Outputs**
- **Workbook Object**: Complete Excel file structure with all sheets
- **Sheet Collection**: Array of all available worksheets
- **File Status**: Updated status showing successful file upload

### **Error Handling**
- **Invalid File Type**: Shows warning if file is not Excel format
- **Corrupted File**: Displays error if file cannot be parsed
- **Large File**: Shows warning for files exceeding size limits
