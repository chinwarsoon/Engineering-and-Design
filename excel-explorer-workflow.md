# Excel Explorer Pro - Data Exploration Workflow Map

```mermaid
graph TD
    %% User Interface Components
    UI[Excel Explorer Pro Web Interface] --> Upload[File Upload Component]
    UI --> SheetSelector[Multi-Sheet Selector]
    UI --> RangeControls[Sheet Range Controls]
    UI --> ColumnSelector[Column Selection Interface]
    UI --> FilterInterface[Active Filters Section]
    UI --> GroupingInterface[Grouping & Analytics]
    UI --> ChartsSection[Charts & Visualizations]
    UI --> DataTable[Data Table Display]
    UI --> StatusBox[Status Box]
    UI --> AIAssistant[AI Assistant]
    
    %% Data Flow
    Upload --> Parse[Excel File Parsing]
    Parse --> Workbook[Workbook Object]
    Workbook --> Sheets[Sheet Collection]
    
    %% Sheet Selection Flow
    SheetSelector --> SelectSheets[User Selects Sheets]
    SelectSheets --> ValidateSelection[Validate Selection]
    ValidateSelection --> LoadMultiple[loadMultipleSheets Function]
    
    %% Range Configuration
    RangeControls --> HeaderRow[Header Row Input]
    RangeControls --> StartCol[Start Column Input]
    RangeControls --> EndCol[End Column Input]
    RangeControls --> RefreshBtn[Refresh Sheet Button]
    
    %% Data Loading Process
    LoadMultiple --> UpdateRange[updateSheetRangeValues]
    UpdateRange --> ExtractData[Extract Data from Sheets]
    ExtractData --> SanitizeHeaders[Header Sanitization]
    SanitizeHeaders --> MergeData[Multi-Sheet Data Merging]
    MergeData --> FilterBlanks[Remove Blank Rows/Columns]
    FilterBlanks --> RawData[Raw Data Array]
    
    %% Alternative Loading Path
    RefreshBtn --> LoadPreserved[loadMultipleSheetsWithPreservedInputs]
    LoadPreserved --> PreserveInputs[Preserve User Range Settings]
    PreserveInputs --> ExtractData
    
    %% Column Selection Process
    ColumnSelector --> BuildInterface[buildInterface Function]
    BuildInterface --> PopulateColumns[Populate Filterable Columns]
    PopulateColumns --> ColumnChips[Column Toggle Chips]
    ColumnChips --> SelectAll[Select All/Clear All]
    SelectAll --> InitializeDashboard[Initialize Dashboard Button]
    
    %% Filtering System
    FilterInterface --> GlobalSearch[Global Search]
    FilterInterface --> ColumnFilters[Column-Specific Filters]
    FilterInterface --> FilterControls[Filter Controls]
    
    %% Filter Processing
    GlobalSearch --> SearchLogic[Search Algorithm]
    ColumnFilters --> MultiSelectFilters[Multiselect Dropdowns]
    FilterControls --> RunFilter[runFilter Function]
    RunFilter --> ApplyFilters[Apply All Active Filters]
    ApplyFilters --> FilteredData[Filtered Data Array]
    
    %% Grouping and Analytics
    GroupingInterface --> GroupByColumns[Group By Selection]
    GroupingInterface --> Aggregator[Aggregator Selection]
    GroupingInterface --> DateBinning[Date Granularity]
    
    %% Group Processing
    GroupByColumns --> GroupData[Data Grouping Logic]
    Aggregator --> AggregateData[Aggregation Functions]
    DateBinning --> ProcessDates[Date Processing]
    GroupData --> GroupedData[Grouped Data Structure]
    
    %% Chart Generation
    ChartsSection --> ChartType[Chart Type Selection]
    ChartsSection --> MainChart[Data Trends Chart]
    ChartsSection --> DateRangeChart[Date Range Chart]
    
    %% Chart Processing
    ChartType --> UpdateChart[updateChart Function]
    MainChart --> RenderChart[Chart.js Rendering]
    DateRangeChart --> UpdateDateRange[updateDateRangeChart Function]
    RenderChart --> ChartDisplay[Interactive Charts]
    
    %% Data Table Display
    DataTable --> TableHeaders[Sticky Headers]
    DataTable --> TableBody[Dynamic Table Body]
    DataTable --> ColumnResize[Column Resizing]
    DataTable --> ColumnSearch[Column Search Boxes]
    
    %% Table Processing
    TableHeaders --> UpdateTable[updateTable Function]
    TableBody --> RenderRows[Row Rendering Logic]
    ColumnResize --> ResizerLogic[Column Width Management]
    ColumnSearch --> SearchBoxes[Column Search Implementation]
    
    %% Status and Feedback
    StatusBox --> ProgressIndicators[Progress Status]
    StatusBox --> FileStatus[File/Sheet Status]
    StatusBox --> FilterStatus[Filter Status]
    StatusBox --> RecordCount[Record Counts]
    
    %% AI Assistant Integration
    AIAssistant --> AIChat[AI Chat Interface]
    AIAssistant --> AIAdvice[AI Data Analysis]
    AIAssistant --> APIConfig[API Configuration]
    
    %% Export and Download
    ChartsSection --> DownloadChart[Download Chart as PNG]
    DataTable --> DownloadExcel[Download Filtered Data]
    StatusBox --> ExportFunctions[Export Utilities]
    
    %% Styling and UX
    UI --> ThemeToggle[Dark/Light Mode]
    UI --> CollapsibleSections[Expandable Sections]
    UI --> ResponsiveDesign[Mobile/Desktop Layout]
    
    %% Data Processing Pipeline
    RawData --> DataValidation[Data Validation]
    FilteredData --> SortData[Sorting Logic]
    GroupedData --> ChartPreparation[Chart Data Preparation]
    
    %% Error Handling
    LoadMultiple --> ErrorHandling[Warning System]
    RunFilter --> ValidationChecks[Input Validation]
    UpdateTable --> StatusUpdates[Status Box Updates]
    
    %% Performance Features
    DataTable --> Virtualization[Large Dataset Handling]
    FilterInterface --> Debouncing[Search Performance]
    ChartsSection --> LazyLoading[Chart Optimization]
    
    %% State Management
    GlobalSearch --> SearchState[Search State Management]
    ColumnFilters --> FilterState[Filter State Tracking]
    GroupingInterface --> GroupState[Grouping State]
    
    %% Key Functions Mapping
    LoadMultiple -.-> |loadMultipleSheets|Multi-sheet loading with auto-range detection|
    LoadPreserved -.-> |loadMultipleSheetsWithPreservedInputs|Preserve user range settings|
    BuildInterface -.-> |buildInterface|Initialize dashboard with selected columns|
    RunFilter -.-> |runFilter|Apply all filters and update views|
    UpdateChart -.-> |updateChart|Update charts with filtered data|
    UpdateTable -.-> |updateTable|Render data table with current filters|
    
    %% User Interaction Flow
    User[User] --> Upload[Upload Excel File]
    User --> SelectRange[Configure Range Settings]
    User --> SelectColumns[Choose Filterable Columns]
    User --> ApplyFilters[Set Filter Conditions]
    User --> GroupData[Configure Grouping]
    User --> ViewCharts[Analyze Visualizations]
    User --> ExportData[Download Results]
    
    %% Styling and Theme
    ThemeToggle --> CSSVariables[CSS Custom Properties]
    CollapsibleSections --> JavaScriptToggles[Dynamic Section Visibility]
    ResponsiveDesign --> MediaQueries[CSS Media Queries]
    
    %% Integration Points
    AIAssistant --> DataAnalysis[AI-Powered Insights]
    StatusBox --> UserFeedback[Real-time Feedback]
    DataTable --> UserInteraction[Interactive Data Exploration]
    
    %% Data Flow Summary
    ExcelFile --> ParsedData --> FilteredData --> VisualizedData --> ExportedData
    
    classDef user fill:#4CAF50,stroke:#388E3C,stroke-width:2px
    classDef data fill:#2196F3,stroke:#1976D2,stroke-width:2px
    classDef function fill:#FF9800,stroke:#F57C00,stroke-width:2px
    classDef ui fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px
```

## Component Descriptions

### 1. **File Upload & Sheet Selection**
- **File Upload Component**: Excel file input with XLSX.js parsing
- **Multi-Sheet Selector**: Dropdown with checkboxes for selecting multiple sheets
- **Sheet Range Controls**: Header row, start/end column inputs with refresh functionality

### 2. **Data Loading Pipeline**
- **loadMultipleSheets()**: Auto-detects column ranges, loads multiple sheets
- **loadMultipleSheetsWithPreservedInputs()**: Preserves user-defined range settings
- **updateSheetRangeValues()**: Automatically calculates optimal column ranges

### 3. **Column Selection Interface**
- **Filterable Columns**: Toggle chips for selecting columns to include in analysis
- **Initialize Dashboard**: Main trigger for building the analytical interface
- **Select All/Clear All**: Bulk selection controls

### 4. **Filtering System**
- **Global Search**: Search across all visible data
- **Column-Specific Filters**: Multiselect dropdowns for each column
- **Active Filters Section**: Real-time filter management with reset capability

### 5. **Grouping & Analytics**
- **Group By Selection**: Multi-column grouping with chip interface
- **Aggregator Selection**: Count, sum, average, min, max functions
- **Date Binning**: Month/quarter/year date granularity options

### 6. **Data Visualization**
- **Data Trends Chart**: Bar/line/pie charts with Chart.js
- **Date Range Chart**: Time-series analysis with date granularity
- **Chart Controls**: Type selection, export functionality

### 7. **Data Table Display**
- **Sticky Headers**: Fixed headers with Excel-style borders
- **Dynamic Table Body**: Responsive rendering with hover effects
- **Column Resizing**: Interactive width adjustment
- **Column Search**: In-column search boxes for quick filtering

### 8. **Status & Feedback**
- **Progress Indicators**: Real-time operation status
- **File/Sheet Status**: Current data source information
- **Filter Status**: Active filter count and conditions
- **Record Counts**: Total/filtered record display

### 9. **AI Assistant Integration**
- **AI Chat Interface**: Natural language data analysis
- **AI Data Analysis**: Automated insights and recommendations
- **API Configuration**: Custom API key management

### 10. **Export & Download**
- **Chart Export**: PNG download with white background
- **Data Export**: Filtered data download as Excel
- **Status Integration**: Export progress and completion feedback

## Key Features

### **Multi-Sheet Support**
- Load and merge data from multiple Excel sheets
- Automatic header unification and null-filling
- Source sheet tracking for data provenance

### **Advanced Filtering**
- Real-time search with debouncing
- Multi-select column filters
- Global search across all visible data
- Filter state persistence

### **Interactive Visualizations**
- Dynamic chart type switching
- Responsive chart sizing
- Date-based analytics with multiple granularities
- Export capabilities for charts

### **User Experience**
- Collapsible sections for space management
- Dark/light theme toggle
- Responsive design for multiple devices
- Real-time status feedback
- AI-powered assistance

## Data Flow Summary

1. **Input**: Excel file upload → Sheet selection → Range configuration
2. **Processing**: Data extraction → Header sanitization → Multi-sheet merging
3. **Configuration**: Column selection → Filter setup → Grouping options
4. **Analysis**: Filter application → Data grouping → Chart generation
5. **Output**: Interactive table → Visual charts → Export capabilities

This workflow provides a comprehensive data exploration experience with real-time feedback, advanced filtering, and AI-assisted analysis capabilities.
