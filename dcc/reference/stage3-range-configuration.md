# Stage 3: Range Configuration

```mermaid
graph TD
    %% Stage Definition
    Stage3[Stage 3: Range Configuration] --> Input3[Input: Selected Sheets]
    Input3 --> Process3[Processing: Range Detection]
    Process3 --> Output3[Output: Sheet Range Settings]
    
    %% UI Components
    headerRowInput --> GetHeaderRow[Get Header Row Value]
    startColInput --> GetStartCol[Get Start Column Value]
    endColInput --> GetEndCol[Get End Column Value]
    refreshBtn[Refresh Sheet Button] --> ReloadCurrent[Reload Current Sheet]
    
    %% Range Controls Flow
    SelectedSheets[Selected Sheets Array] --> AnalyzeSheets[Analyze Sheet Structure]
    AnalyzeSheets --> DetectHeaders[Detect Header Row]
    AnalyzeSheets --> DetectColumns[Detect Column Range]
    DetectHeaders --> HeaderRowDefault[Default Header Row: 1]
    DetectColumns --> ColumnRangeDefault[Default Column Range: A-Z]
    
    %% User Input Processing
    HeaderRowDefault --> HeaderRowInput[User Header Row Input]
    ColumnRangeDefault --> StartColInput[User Start Column Input]
    ColumnRangeDefault --> EndColInput[User End Column Input]
    
    %% Range Validation
    HeaderRowInput --> ValidateHeader[Validate Header Row]
    StartColInput --> ValidateStart[Validate Start Column]
    EndColInput --> ValidateEnd[Validate End Column]
    ValidateHeader --> RangeSettings[Final Range Settings]
    ValidateStart --> RangeSettings
    ValidateEnd --> RangeSettings
    
    %% Expected Outputs
    RangeSettings --> HeaderRowValue[Header Row Value]
    RangeSettings --> StartColValue[Start Column Value]
    RangeSettings --> EndColValue[End Column Value]
    RangeSettings --> RangeString[Range String: A1:Z100]
```

## Event Handlers

### **Range Configuration Events**
- **Header Row Input**: `reloadCurrentSheet` - Triggered when header row value changes
- **Start Column Input**: `reloadCurrentSheet` - Triggered when start column changes
- **End Column Input**: `reloadCurrentSheet` - Triggered when end column changes
- **Refresh Button**: `reloadCurrentSheet` - Manual refresh with current settings

### **Auto-Detection Logic**
- **Header Detection**: Automatically identifies first non-empty row as header
- **Column Range**: Detects used columns across all selected sheets
- **Default Values**: Provides sensible defaults for user convenience
- **Validation**: Ensures inputs are within valid ranges

### **UI Components**
- **Header Row Input**: Numeric input for header row number
- **Start Column Input**: Text input for starting column (A, B, etc.)
- **End Column Input**: Text input for ending column
- **Refresh Button**: Reloads sheets with current range settings

### **Expected Outputs**
- **Range Settings**: Complete configuration for data extraction
- **Header Row**: Row number to use as column headers
- **Column Range**: Start and end columns for data extraction
- **Range String**: Human-readable range format (A1:Z100)

### **Data Flow**
1. Analyze selected sheets to detect structure
2. Set default header row and column range
3. Allow user to override defaults
4. Validate user inputs
5. Create final range settings for data loading
