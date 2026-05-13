# Excel Explorer Pro - UI Event Traceability Map

```mermaid
graph TD
 %% Status Box Components
 statusBox --> toggleStatusBox --> Toggle
 cancelOperationBtn --> cancelCurrentOperation --> Cancel
 warningSection --> toggleWarningHistory --> Warning
 warningHeader --> toggleWarningHistory --> Warning
 latestWarningText --> showWarning --> Display
 warningCount --> showWarning --> Update
 warningList --> clearWarnings --> Clear
 progressBar --> setProgressStatus --> Progress
 statusLoadFile --> setProgressStatus --> Load
 statusUpdateCharts --> setProgressStatus --> Charts
 statusUpdateTable --> setProgressStatus --> Table
 statusApplyFilters --> setProgressStatus --> Filters
 statusGroupBy --> setProgressStatus --> Group
 statusFunctionCall --> setFunctionCallStatus --> Function
 statusFileName --> setProgressStatus --> File
 statusWorksheet --> setProgressStatus --> Worksheet
 statusHeaderRow --> setProgressStatus --> Header
 statusColRange --> setProgressStatus --> Column
 statusFiltersApplied --> setProgressStatus --> Applied
 statusRecords --> updateStatusBox --> Records
 debugList --> clearDebugLog --> Debug
 
 %% Header Controls
 sidebarToggle --> toggleSidebar --> Sidebar
 themeBtn --> toggleTheme --> Theme
 devStatus --> toggleDevMode --> Dev
 
 %% AI Assistant
 aiFloatBtn --> toggleAIChat --> AI
 configureAI --> configureAI --> Config
 aiInput --> sendUserMessage --> Message
 sendUserMessage --> sendUserMessage --> Send
 
 %% File Upload Section
 upload --> FileUpload --> Load
 step1Header --> updateStep1Header --> Step1
 toggleStep1Btn --> toggleStep1Box --> Box1
 loadFilesContainer --> toggleStep1Box --> Container
 sheetSelector --> toggleSheetDropdown --> Dropdown
 sheetSelectorLabel --> updateSheetLabel --> Label
 sheetDropdown --> loadSelectedSheets --> Load
 sheetList --> updateSheetLabel --> List
 headerRowInput --> reloadCurrentSheet --> Header
 startColInput --> reloadCurrentSheet --> Start
 endColInput --> reloadCurrentSheet --> End
 refreshBtn --> reloadCurrentSheet --> Refresh
 
 %% Sheet Selection Controls
 sheetCheck --> updateSheetLabel --> Sheet
 controlBtn --> selectAllSheets --> All
 controlBtnClear --> selectAllSheets --> Clear
 controlBtnApply --> loadSelectedSheets --> Apply
 
 %% Column Selection Section
 step2Header --> updateStep2Header --> Step2
 toggleStep2Btn --> toggleStep2Box --> Box2
 headerListContainer --> toggleStep2Box --> HeaderContainer
 headerListWrapper --> buildInterface --> Wrapper
 headerList --> buildInterface --> HeaderList
 colCheck --> syncChip --> Chip
 colCheckBuild --> buildInterface --> ColBuild
 toggleChip --> buildInterface --> ToggleChip
 
 %% Filter Controls
 toggleFilterBtn --> toggleFilterBox --> FilterBox
 filterControlsWrapper --> toggleFilterBox --> FilterWrapper
 filterArea --> buildInterface --> FilterArea
 filterControls --> buildInterface --> FilterControls
 resetFilters --> resetFilters --> Reset
 resetActiveFilters --> resetActiveFilters --> ResetActive
 filterControlsGet --> buildInterface --> FilterGet
 
 %% Global Search
 globalSearch --> handleGlobalSearchInput --> GlobalInput
 globalSearchSelect --> selectSearchResult --> GlobalSelect
 globalSearchResults --> renderGlobalSearchResults --> GlobalResults
 globalSearchShow --> showGlobalSearchResultsIfNotEmpty --> GlobalShow
 globalSearchHide --> hideGlobalSearchResults --> GlobalHide
 
 %% Grouping Controls
 toggleGroupBtn --> toggleGroupBox --> GroupBox
 groupControlsContainer --> toggleGroupBox --> GroupContainer
 dashboardContainer --> toggleGroupBox --> DashboardContainer
 groupByWrapper --> buildInterface --> GroupWrapper
 groupByColumnList --> buildInterface --> GroupColumnList
 groupByColumns --> buildInterface --> GroupColumns
 resetGroupBy --> resetGroupBy --> ResetGroup
 aggColumn --> buildInterface --> AggColumn
 dateGranularity --> buildInterface --> DateGran
 aggColumnRun --> runFilter --> AggRun
 dateGranRun --> runFilter --> DateRun
 
 %% Chart Controls
 toggleChartsBtn --> toggleChartsContainer --> ChartsBtn
 chartsWrapper --> toggleChartsContainer --> ChartsWrapper
 chartType --> runFilter --> ChartType
 chartCanvasContainer --> updateChart --> ChartCanvas
 dataChart --> updateChart --> DataChart
 downloadChart --> downloadChart --> DownloadChart
 toggleDateRangeChartBtn --> toggleDateRangeChart --> DateRangeBtn
 dateRangeChartSection --> toggleDateRangeChart --> DateRangeSection
 dateRangeChart --> updateDateRangeChart --> DateRangeChart
 downloadDateRangeChart --> downloadDateRangeChart --> DownloadDateRange
 
 %% Data Table
 mainTable --> updateTable --> MainTable
 tBody --> updateTable --> TableBody
 headerListTable --> buildInterface --> HeaderTable
 columnSearchBox --> filterTableByColumn --> ColumnSearch
 columnSearchClose --> closeColumnSearchBox --> SearchClose
 columnSearchToggle --> toggleColumnSearch --> SearchToggle
 resizerStart --> resizeStart --> ResizeStart
 resizerMove --> resizeMove --> ResizeMove
 resizerEnd --> resizeEnd --> ResizeEnd
 selectAllColumns --> selectAllColumns --> SelectAll
 clearAllColumns --> clearAllColumns --> ClearAll
 toggleColumnMenu --> toggleColumnMenu --> ColumnMenu
 columnToggleMenu --> toggleCol --> ColumnToggle
 applyColumnChanges --> applyColumnChanges --> ColumnChanges
 
 %% Initialize Dashboard
 initializeDashboardBuild --> buildInterface --> InitBuild
 initializeDashboardRun --> runFilter --> InitRun
 
 %% Window Event Listeners
 windowUpload --> addEventListener --> WindowUpload
 windowClick --> addEventListener --> WindowClick
 windowToast --> addEventListener --> WindowToast
 
 %% Class-Based Event Handlers
 multiselectDisplay --> toggleSheetDropdown --> MultiDisplay
 multiselectOptions --> loadSelectedSheets --> MultiOptions
 optionItemSelect --> handleSelect --> OptionSelect
 optionItemFilter --> applyFilter --> OptionFilter
 filtersContainer --> buildInterface --> FiltersContainer
 innerControlBox --> buildInterface --> InnerControl
 btnToggleCompact1 --> toggleStep1Box --> BtnToggle1
 btnToggleCompact2 --> toggleStep2Box --> BtnToggle2
 btnToggleCompact3 --> toggleGroupBox --> BtnToggle3
 btnToggleCompact4 --> toggleChartsContainer --> BtnToggle4
 btnToggleCompact5 --> toggleFilterBox --> BtnToggle5
 btnInit --> buildInterface --> BtnInit
 btnSelectAll --> selectAllColumns --> BtnSelectAll
 btnClearAll --> clearAllColumns --> BtnClearAll
 btnResetFilters --> resetFilters --> BtnResetFilters
 btnResetGroup --> resetGroupBy --> BtnResetGroup
 btnOutlineChart --> downloadChart --> BtnChart
 btnOutlineExcel --> downloadExcel --> BtnExcel
 btnOutlineTheme --> toggleTheme --> BtnTheme
 btnOutlineDev --> toggleDevMode --> BtnDev
 statusBoxToggle --> toggleStatusBox --> StatusBoxToggle
 statusBoxHeader --> toggleWarningHistory --> StatusBoxHeader
 statusBoxContent --> clearWarnings --> StatusBoxContent
 statusItem --> setProgressStatus --> StatusItem
 statusValue --> setProgressStatus --> StatusValue
 statusIdle --> setProgressStatus --> StatusIdle
 aiMessages --> sendUserMessage --> AiMessages
 aiInputArea --> sendUserMessage --> AiInputArea
 aiMessage --> sendUserMessage --> AiMessage
 
 %% Dynamic Elements
 generatedOptions --> buildInterface --> GenOptions
 generatedChips --> buildInterface --> GenChips
 generatedFilters --> buildInterface --> GenFilters
 generatedTable --> updateTable --> GenTable
 generatedCharts --> updateChart --> GenCharts
 generatedDropdowns --> buildInterface --> GenDropdowns
 
 %% Data Processing Flow
 buildInterfaceFilter --> runFilter --> BuildFilter
 runFilterTable --> updateTable --> FilterTable
 runFilterChart --> updateChart --> FilterChart
 buildInterfaceGroup --> updateGroupBySelection --> BuildGroup
 buildInterfaceDate --> updateDateYLabel --> BuildDate
 
 %% Expected Outputs
 toggleStatusBoxOut --> StatusBoxOut
 toggleSidebarOut --> SidebarOut
 toggleThemeOut --> ThemeOut
 toggleDevModeOut --> DevModeOut
 toggleAIChatOut --> AIChatOut
 configureAIOut --> ConfigOut
 sendUserMessageOut --> MessageOut
 toggleSheetDropdownOut --> DropdownOut
 selectAllSheetsOut --> SheetsOut
 loadSelectedSheetsOut --> LoadOut
 updateSheetLabelOut --> LabelOut
 reloadCurrentSheetOut --> RefreshOut
 toggleStep1BoxOut --> Step1Out
 toggleStep2BoxOut --> Step2Out
 toggleGroupBoxOut --> GroupOut
 toggleChartsContainerOut --> ChartsOut
 toggleFilterBoxOut --> FiltersOut
 selectAllColumnsOut --> ColumnsOut
 clearAllColumnsOut --> ClearOut
 buildInterfaceOut --> DashboardOut
 resetFiltersOut --> ResetFiltersOut
 resetActiveFiltersOut --> ResetActiveOut
 runFilterOut --> ProcessingOut
 updateTableOut --> TableOut
 updateChartOut --> ChartsOut
 downloadChartOut --> ExportOut
 downloadExcelOut --> ExcelOut
 downloadDateRangeChartOut --> DateExportOut
 downloadDateRangeExcelOut --> DateExcelOut
```

## Event Handler Mapping Summary

### **1. Status Box Events**
- **Toggle Visibility**: `toggleStatusBox()` - Shows/hides status box with auto-collapse timer
- **Cancel Operations**: `cancelCurrentOperation()` - Cancels active long-running operations
- **Warning Management**: `showWarning()`, `toggleWarningHistory()`, `clearWarnings()` - Handle warning display and history
- **Progress Updates**: `setProgressStatus()` - Updates all status indicators and progress bars

### **2. File Upload Events**
- **File Selection**: `addEventListener("change")` on `#upload` - Triggers Excel file parsing with XLSX.js
- **Sheet Management**: `loadSelectedSheets()`, `reloadCurrentSheet()` - Handle multi-sheet loading and refresh

### **3. UI Toggle Events**
- **Sidebar**: `toggleSidebar()` - Collapses/expands main sidebar
- **Theme**: `toggleTheme()` - Switches between dark/light modes
- **Dev Mode**: `toggleDevMode()` - Enables/disables development features
- **Section Toggles**: `toggleStep1Box()`, `toggleStep2Box()`, `toggleGroupBox()`, `toggleChartsContainer()`, `toggleFilterBox()` - Control section visibility

### **4. AI Assistant Events**
- **Chat Toggle**: `toggleAIChat()` - Shows/hides AI chat window
- **Configuration**: `configureAI()` - Opens API key configuration
- **Message Handling**: `sendUserMessage()` - Processes user input and sends to AI

### **5. Sheet Selection Events**
- **Dropdown Toggle**: `toggleSheetDropdown()` - Opens/closes sheet selection dropdown
- **Selection Management**: `selectAllSheets()`, `updateSheetLabel()` - Handle bulk selection and label updates
- **Loading**: `loadSelectedSheets()` - Loads selected sheets with auto-range detection

### **6. Column Selection Events**
- **Chip Interface**: `syncChip()`, `buildInterface()` - Handle column toggle chips and build interface
- **Selection Controls**: `selectAllColumns()`, `clearAllColumns()` - Bulk column selection operations
- **Initialize Dashboard**: `buildInterface()` - Main trigger for dashboard initialization

### **7. Filter and Search Events**
- **Global Search**: `handleGlobalSearchInput()`, `renderGlobalSearchResults()`, `selectSearchResult()` - Handle global search functionality
- **Column Filters**: `filterDrop()`, `applyFilter()`, `handleFilterSearchEnter()` - Manage column-specific filters
- **Filter Controls**: `resetFilters()`, `resetActiveFilters()` - Reset filter states
- **Apply Filters**: `runFilter()` - Main filter application function

### **8. Grouping and Analytics Events**
- **Group By**: `updateGroupBySelection()`, `handleGroupByChange()` - Handle grouping column selection
- **Date Processing**: `updateDateYLabel()` - Manage date range chart Y-axis selection
- **Reset Grouping**: `resetGroupBy()` - Clear grouping configuration

### **9. Chart and Visualization Events**
- **Chart Updates**: `updateChart()`, `updateDateRangeChart()` - Update chart displays
- **Chart Controls**: `toggleChartsContainer()`, `toggleDateRangeChart()` - Manage chart section visibility
- **Chart Type**: `runFilter()` triggered by chart type change - Updates chart based on selection
- **Export**: `downloadChart()`, `downloadDateRangeChart()` - Export charts as PNG

### **10. Data Table Events**
- **Table Updates**: `updateTable()`, `finishUpdateTable()` - Render and finalize table display
- **Column Resize**: `resizeStart()`, `resizeMove()`, `resizeEnd()` - Handle interactive column resizing
- **Column Search**: `toggleColumnSearch()`, `filterTableByColumn()`, `closeColumnSearchBox()` - In-table column search
- **Column Menu**: `toggleColumnMenu()`, `toggleCol()`, `applyColumnChanges()` - Column visibility management

### **11. Window-Level Event Listeners**
- **Click Outside**: `addEventListener("click")` - Closes dropdowns, search boxes, and menus when clicking outside
- **Toast Dismissal**: `addEventListener("click")` - Dismisses toast notifications
- **File Upload**: `addEventListener("change")` - Handles file selection changes

### **12. Dynamic Element Events**
- **Generated Elements**: All dynamically created options, chips, filters, and table cells trigger their respective handler functions
- **Event Delegation**: Many events use event delegation for dynamically created elements
- **State Management**: Functions maintain global state variables and update UI accordingly

## Key Event Patterns

### **Direct Event Handlers**
- `onclick="functionName()"` - Direct function calls on static HTML elements
- `onchange="functionName()"` - Change events for form inputs
- `onkeyup="condition ? functionName()"` - Keyboard events with conditions

### **Programmatic Event Listeners**
- `addEventListener("event", handler)` - Dynamic event binding for file uploads and global interactions
- Event delegation patterns for dynamically created elements

### **State-Driven Updates**
- Most functions read current state from DOM elements
- Update global state variables
- Trigger dependent UI updates through function calls

This simplified version should render properly in any Mermaid-compatible viewer while maintaining the complete traceability mapping between UI elements, their event handlers, and expected outputs.
