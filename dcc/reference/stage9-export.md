# Stage 9: Export

```mermaid
graph TD
    %% Stage Definition
    Stage9[Stage 9: Export] --> Input9[Input: Filtered Data + Charts]
    Input9 --> Process9[Processing: downloadChart and downloadExcel]
    Process9 --> Output9[Output: Export Files]
    
    %% Chart Export Components
    downloadChart --> DownloadChartAsPNG[Download Chart as PNG]
    toggleDateRangeChartBtn --> DownloadDateRangeChart[Download Date Range Chart]
    chartCanvasContainer --> GetCanvasElement[Get Canvas Element]
    CanvasElement --> ConvertToImage[Convert to Image Data]
    
    %% Excel Export Components
    downloadExcel --> DownloadFilteredData[Download Filtered Data]
    downloadDateRangeExcel --> DownloadDateRangeData[Download Date Range Data]
    FilteredData --> PrepareExcelData[Prepare Excel Data Structure]
    
    %% Chart Export Process
    GetCanvasElement --> CanvasToBlob[Canvas to Blob Conversion]
    CanvasToBlob --> CreateDownloadLink[Create Download Link]
    CreateDownloadLink --> TriggerDownload[Trigger Download]
    TriggerDownload --> PNGFile[PNG File Download]
    
    %% Excel Export Process
    PrepareExcelData --> XLSXGeneration[XLSX Generation]
    XLSXGeneration --> CreateWorkbook[Create New Workbook]
    CreateWorkbook --> AddWorksheet[Add Worksheet with Data]
    AddWorksheet --> GenerateFile[Generate Excel File]
    GenerateFile --> ExcelDownload[Excel File Download]
    
    %% Export Options
    PNGFile --> SaveImage[Save Image File]
    ExcelDownload --> SaveExcel[Save Excel File]
    SaveImage --> ExportConfirmation[Export Confirmation Message]
    SaveExcel --> ExportConfirmation
    
    %% Expected Outputs
    ExportConfirmation --> DownloadStatus[Download Status Update]
    ExportConfirmation --> FileLocation[File Saved to Downloads]
    ExportConfirmation --> ExportComplete[Export Process Complete]
```

## Event Handlers

### **Export Events**
- **Download Chart**: `downloadChart` - Exports main chart as PNG
- **Download Date Range Chart**: `downloadDateRangeChart` - Exports date range chart
- **Download Excel**: `downloadExcel` - Exports filtered data as Excel
- **Download Date Range Excel**: `downloadDateRangeExcel` - Exports date-filtered data

### **Chart Export Features**
- **PNG Format**: High-quality image export
- **Canvas Capture**: Direct from HTML5 canvas element
- **Custom Filename**: Uses descriptive naming convention
- **Multiple Charts**: Supports both main and date range charts
- **Background Options**: Transparent or colored backgrounds

### **Excel Export Features**
- **XLSX Format**: Modern Excel file format
- **Filtered Data**: Only includes currently visible data
- **Preserve Formatting**: Maintains data types and formatting
- **Multiple Sheets**: Supports date range in separate sheet
- **Metadata**: Includes export timestamp and filter info

### **Export Process Flow**
1. **Data Collection**: Gather current filtered data
2. **Format Preparation**: Structure data for export format
3. **File Generation**: Create file in appropriate format
4. **Download Trigger**: Initiate browser download
5. **User Notification**: Confirm successful export
6. **File Management**: Handle download completion

### **Chart Export Details**
- **Canvas Extraction**: Gets image data from chart canvas
- **Blob Creation**: Converts canvas to downloadable blob
- **Download Link**: Creates temporary download link
- **Automatic Cleanup**: Removes temporary elements
- **Quality Settings**: High-resolution export options

### **Excel Export Details**
- **Data Validation**: Ensures data integrity
- **Type Detection**: Preserves numeric, date, text types
- **Column Headers**: Includes current column names
- **Filter Metadata**: Adds sheet with current filter settings
- **Large File Handling**: Progress indicators for big exports

### **Expected Outputs**
- **PNG Files**: Chart images saved locally
- **Excel Files**: Data files ready for analysis
- **Export Confirmation**: User feedback on completion
- **Download History**: Track of recent exports
- **Error Handling**: Clear messages for export failures

### **Advanced Features**
- **Batch Export**: Export multiple charts simultaneously
- **Custom Templates**: Predefined export formats
- **Email Integration**: Direct email sending option
- **Cloud Storage**: Save directly to cloud services
- **Scheduled Export**: Automated export capabilities
