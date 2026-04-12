```mermaid
graph TD
 %% Status Box Components
 statusBox[statusBox ID] -- "toggleStatusBox()" --> statusBox{Toggle Visibility}
 cancelOperationBtn[Cancel Current Operation] -- "cancelCurrentOperation()" --> cancelOperationBtn{id="cancelOperationBtn"}
 warningSection[Toggle Warning History] -- "toggleWarningHistory()" --> warningSection{id="warningSection"}
 warningHeader[Toggle Warning History] -- "toggleWarningHistory()" --> warningHeader{id="warningHeader"}
 latestWarningText[Display Warning Message] -- "showWarning()" --> latestWarningText{id="latestWarningText"}
 warningCount[Update Warning Count] -- "showWarning()" --> warningCount{id="warningCount"}
 warningList[Clear All Warnings] -- "clearWarnings()" --> warningList{id="warningList"}
 progressBar[Update Progress Bar] -- "setProgressStatus()" --> progressBar{id="progressBar"}
 statusLoadFile[Update Load File Status] -- "setProgressStatus()" --> statusLoadFile{id="statusLoadFile"}
 statusUpdateCharts[Update Chart Status] -- "setProgressStatus()" --> statusUpdateCharts{id="statusUpdateCharts"}
 statusUpdateTable[Update Table Status] -- "setProgressStatus()" --> statusUpdateTable{id="statusUpdateTable"}
 statusApplyFilters[Update Filter Status] -- "setProgressStatus()" --> statusApplyFilters{id="statusApplyFilters"}
 statusGroupBy[Update Group By Status] -- "setProgressStatus()" --> statusGroupBy{id="statusGroupBy"}
 statusFunctionCall[Update Function Call Status] -- "setFunctionCallStatus()" --> statusFunctionCall{id="statusFunctionCall"}
 statusFileName[Update File Name] -- "setProgressStatus()" --> statusFileName{id="statusFileName"}
 statusWorksheet[Update Worksheet Name] -- "setProgressStatus()" --> statusWorksheet{id="statusWorksheet"}
 statusHeaderRow[Update Header Row] -- "setProgressStatus()" --> statusHeaderRow{id="statusHeaderRow"}
 statusColRange[Update Column Range] -- "setProgressStatus()" --> statusColRange{id="statusColRange"}
 statusFiltersApplied[Update Filters Applied] -- "setProgressStatus()" --> statusFiltersApplied{id="statusFiltersApplied"}
 statusRecords[Update Record Count] -- "updateStatusBox()" --> statusRecords{id="statusRecords"}
 debugList[Clear Debug Log] -- "clearDebugLog()" --> debugList{id="debugList"}
 
 %% Header Controls
 sidebarToggle[Toggle Sidebar Visibility] -- "toggleSidebar()" --> sidebarToggle{id="sidebarToggle"}
 themeBtn[Toggle Dark/Light Theme] -- "toggleTheme()" --> themeBtn{id="themeBtn"}
 devStatus[Toggle Development Mode] -- "toggleDevMode()" --> devStatus{id="devStatus"}
 
 %% AI Assistant
 aiFloatBtn[id="aiFloatBtn"] --> |toggleAIChat()|onclick="toggleAIChat()"|Toggle AI Chat Window
 configureAI[id="configureAI"] --> |configureAI()|onclick="configureAI()"|Configure AI API Key
 aiInput[id="aiInput"] --> |sendUserMessage()|onkeyup="if(event.key==='Enter')|Send AI Message
 sendUserMessage --> |sendUserMessage()|onclick="sendUserMessage()"|Send AI Message
 
 %% File Upload Section
 upload[id="upload"] --> |File Upload Handler|addEventListener("change")|Load Excel File
 step1Header[id="step1Header"] --> |updateStep1Header()|Function Call|Update Step 1 Header
 toggleStep1Btn[Toggle Step 1] -- "toggleStep1Box()" --> toggleStep1Btn{id="toggleStep1Btn"}
 loadFilesContainer[Toggle Load Files Container] -- "toggleStep1Box()" --> loadFilesContainer{id="loadFilesContainer"}
 sheetSelector[Toggle Sheet Dropdown] -- "toggleSheetDropdown()" --> sheetSelector{id="sheetSelector"}
 sheetSelectorLabel[Update Sheet Selector Label] -- "updateSheetLabel()" --> sheetSelectorLabel{id="sheetSelectorLabel"}
 sheetDropdown[Load Selected Sheets] -- "loadSelectedSheets()" --> sheetDropdown{id="sheetDropdown"}
 sheetList[Update Sheet List] -- "updateSheetLabel()" --> sheetList{id="sheetList"}
 headerRowInput[Get Header Row Value] -- "reloadCurrentSheet()" --> headerRowInput{id="headerRowInput"}
 startColInput[Get Start Column Value] -- "reloadCurrentSheet()" --> startColInput{id="startColInput"}
 endColInput[Get End Column Value] -- "reloadCurrentSheet()" --> endColInput{id="endColInput"}
 refreshBtn[Refresh Sheet with Current Settings] -- "reloadCurrentSheet()" --> refreshBtn{Refresh Sheet}
 
 %% Sheet Selection Controls
 sheet-check[Update Sheet Selection] -- "updateSheetLabel()" --> sheet-check{class="sheet-check"}
 control-btn[Select All Sheets] -- "selectAllSheets()" --> control-btn{class="control-btn"}
 control-btn[Clear All Sheets] -- "selectAllSheets()" --> control-btn{class="control-btn"}
 control-btn--apply[Load Selected Sheets] -- "loadSelectedSheets()" --> control-btn--apply{class="control-btn--apply"}
 
 %% Column Selection Section
 step2Header[Update Step 2 Header] -- "updateStep2Header()" --> step2Header{id="step2Header"}
 toggleStep2Btn[Toggle Step 2 Visibility] -- "toggleStep2Box()" --> toggleStep2Btn{id="toggleStep2Btn"}
 headerListContainer[Toggle Header List Container] -- "toggleStep2Box()" --> headerListContainer{id="headerListContainer"}
 headerListWrapper[Get Header List Wrapper] -- "buildInterface()" --> headerListWrapper{id="headerListWrapper"}
 headerList[Populate Header List] -- "buildInterface()" --> headerList{id="headerList"}
 col-check[Sync Chip Visual State] -- "syncChip()" --> col-check{class="col-check"}
 col-check[Get Column Selection State] -- "buildInterface()" --> col-check{class="col-check"}
 toggle-chip[Update Toggle Chip State] -- "buildInterface()" --> toggle-chip{class="toggle-chip"}
 
 %% Filter Controls
 toggleFilterBtn[Toggle Filter Box] -- "toggleFilterBox()" --> toggleFilterBtn{id="toggleFilterBtn"}
 filterControlsWrapper[Toggle Filter Controls Wrapper] -- "toggleFilterBox()" --> filterControlsWrapper{id="filterControlsWrapper"}
 filterArea[Populate Filter Area] -- "buildInterface()" --> filterArea{id="filterArea"}
 filterControls[Populate Filter Controls] -- "buildInterface()" --> filterControls{class="filter-controls"}
 resetFilters[Reset All Filters] -- "resetFilters()" --> resetFilters{onclick="resetFilters()"|Reset All Filters}
 resetActiveFilters[Reset Active Filters] -- "resetActiveFilters()" --> resetActiveFilters{onclick="resetActiveFilters()"|Reset Active Filters}
 filterControls[Get Filter Controls] -- "buildInterface()" --> filterControls{class="filter-controls"}
 
 %% Global Search
 globalSearch[Handle Global Search Input] -- "handleGlobalSearchInput()" --> globalSearch{id="globalSearch"}
 globalSearch[Select Search Result] -- "selectSearchResult()" --> globalSearch{Global Search}
 globalSearchResults[Render Search Results] -- "renderGlobalSearchResults()" --> globalSearchResults{id="globalSearchResults"}
 globalSearch[Show Search Results] -- "showGlobalSearchResultsIfNotEmpty()" --> globalSearch{Global Search}
 globalSearch[Hide Search Results] -- "hideGlobalSearchResults()" --> globalSearch{Global Search}
 
 %% Grouping Controls
 toggleGroupBtn[Toggle Group Box] -- "toggleGroupBox()" --> toggleGroupBtn{id="toggleGroupBtn"}
 groupControlsContainer[Toggle Group Controls Container] -- "toggleGroupBox()" --> groupControlsContainer{id="groupControlsContainer"}
 dashboardContainer[Toggle Dashboard Container] -- "toggleGroupBox()" --> dashboardContainer{id="dashboardContainer"}
 groupByWrapper[Get Group By Wrapper] -- "buildInterface()" --> groupByWrapper{id="groupByWrapper"}
 groupByColumnList[Populate Group By List] -- "buildInterface()" --> groupByColumnList{id="groupByColumnList"}
 groupByColumns[Get Group By Columns] -- "buildInterface()" --> groupByColumns{class="groupByColumns"}
 resetGroupBy[Reset Group By] -- "resetGroupBy()" --> resetGroupBy{onclick="resetGroupBy()"|Reset Group By}
 aggColumn[Get Aggregator Column] -- "buildInterface()" --> aggColumn{id="aggColumn"}
 dateGranularity[Get Date Granularity] -- "buildInterface()" --> dateGranularity{id="dateGranularity"}
 aggColumn[Run Filter with Aggregator] -- "runFilter()" --> aggColumn{onchange="runFilter()"|Run Filter with Aggregator}
 dateGranularity[Run Filter with Date Binning] -- "runFilter()" --> dateGranularity{onchange="runFilter()"|Run Filter with Date Binning}
 
 %% Chart Controls
 toggleChartsBtn[Toggle Charts Container] -- "toggleChartsContainer()" --> toggleChartsBtn{id="toggleChartsBtn"}
 chartsWrapper[Toggle Charts Wrapper] -- "toggleChartsContainer()" --> chartsWrapper{id="chartsWrapper"}
 chartType[Update Chart Type] -- "runFilter()" --> chartType{id="chartType"}
 chartCanvasContainer[Get Chart Canvas Container] -- "updateChart()" --> chartCanvasContainer{id="chartCanvasContainer"}
 dataChart[Update Data Chart] -- "updateChart()" --> dataChart{id="dataChart"}
 downloadChart[Download Chart as PNG] -- "downloadChart()" --> downloadChart{Download Chart}
 toggleDateRangeChartBtn[Toggle Date Range Chart] -- "toggleDateRangeChart()" --> toggleDateRangeChartBtn{Toggle Date Range Chart}
 dateRangeChartSection[Toggle Date Range Chart Section] -- "toggleDateRangeChart()" --> dateRangeChartSection{Toggle Date Range Chart Section}
 dateRangeChart[Update Date Range Chart] -- "updateDateRangeChart()" --> dateRangeChart{id="dateRangeChart"}
 downloadDateRangeChart[Download Date Range Chart] -- "downloadDateRangeChart()" --> downloadDateRangeChart{Download Date Range Chart}
 
 %% Data Table
 mainTable[Update Main Table] -- "updateTable()" --> mainTable{id="mainTable"}
 tBody[Update Table Body] -- "updateTable()" --> tBody{id="tBody"}
 headerList[Get Header List for Table] -- "buildInterface()" --> headerList{id="headerList"}
 column-search-box[Column Search Input] -- "filterTableByColumn()" --> column-search-box{class="column-search-box"}
 column-search-box[Close Column Search Box] -- "closeColumnSearchBox()" --> column-search-box{class="column-search-box"}
 column-search-box[Toggle Column Search] -- "toggleColumnSearch()" --> column-search-box{class="column-search-box"}
 resizer[Start Column Resize] -- "resizeStart()" --> resizer{class="resizer"}
 resizer[Handle Column Resize] -- "resizeMove()" --> resizer{class="resizer"}
 resizer[End Column Resize] -- "resizeEnd()" --> resizer{class="resizer"}
 selectAllColumns[Select All Table Columns] -- "selectAllColumns()" --> selectAllColumns{Select All Table Columns}
 clearAllColumns[Clear All Table Columns] -- "clearAllColumns()" --> clearAllColumns{Clear All Table Columns}
 toggleColumnMenu[Toggle Column Menu] -- "toggleColumnMenu()" --> toggleColumnMenu{Toggle Column Menu}
 columnToggleMenu[Toggle Column Visibility] -- "toggleCol()" --> columnToggleMenu{Toggle Column Menu}
 applyColumnChanges[Apply Column Changes] -- "applyColumnChanges()" --> applyColumnChanges{Apply Column Changes}
 
 %% Initialize Dashboard
 initializeDashboard[Build Complete Dashboard Interface] -- "buildInterface()" --> initializeDashboard{Build Complete Dashboard Interface}
 initializeDashboard[Apply All Filters and Update Views] -- "runFilter()" --> initializeDashboard{Apply All Filters and Update Views}
 
 %% Window Event Listeners
 Window[Handle File Upload] -- addEventListener("change") --> Window{Handle File Upload}
 Window[Click Outside] -- addEventListener("click") --> Window{Click Outside}
 Window[Click Outside] -- addEventListener("click") --> Window{Click Outside}
 Window[Click Outside] -- addEventListener("click") --> Window{Click Outside}
 Window[Toast Dismissal] -- addEventListener("click") --> Window{Toast Dismissal}
 
 %% Class-Based Event Handlers
 multiselect-display[Toggle Multiselect Display] -- "toggleSheetDropdown()" --> multiselect-display{class="multiselect-display"}
 multiselect-options[Load from Multiselect Options] -- "loadSelectedSheets()" --> multiselect-options{class="multiselect-options"}
 option-item[Handle Option Selection] -- "handleSelect()" --> option-item{class="option-item"}
 option-item[Apply Filter from Option] -- "applyFilter()" --> option-item{class="option-item"}
 filters-container[Populate Filters Container] -- "buildInterface()" --> filters-container{class="filters-container"}
 inner-control-box[Populate Inner Control Box] -- "buildInterface()" --> inner-control-box{class="inner-control-box"}
 btn-toggle-compact[Toggle Step Box] -- "toggleStep1Box()" --> btn-toggle-compact{class="btn-toggle-compact"}
 btn-toggle-compact[Toggle Step Box] -- "toggleStep2Box()" --> btn-toggle-compact{class="btn-toggle-compact"}
 btn-toggle-compact[Toggle Group Box] -- "toggleGroupBox()" --> btn-toggle-compact{class="btn-toggle-compact"}
 btn-toggle-compact[Toggle Charts Container] -- "toggleChartsContainer()" --> btn-toggle-compact{class="btn-toggle-compact"}
 btn-toggle-compact[Toggle Filter Box] -- "toggleFilterBox()" --> btn-toggle-compact{class="btn-toggle-compact"}
 btn[Initialize Dashboard] -- "buildInterface()" --> btn{Initialize Dashboard}
 btn[Select All Columns] -- "selectAllColumns()" --> btn{Select All Table Columns}
 btn[Clear All Columns] -- "clearAllColumns()" --> btn{Clear All Table Columns}
 btn[Reset Filters] -- "resetFilters()" --> btn{Reset Filters}
 btn[Reset Group By] -- "resetGroupBy()" --> btn{Reset Group By}
 btn-outline[Download Chart] -- "downloadChart()" --> btn-outline{Download Chart}
 btn-outline[Download Excel] -- "downloadExcel()" --> btn-outline{Download Excel}
 btn-outline[Toggle Theme] -- "toggleTheme()" --> btn-outline{Toggle Theme}
 btn-outline[Toggle Dev Mode] -- "toggleDevMode()" --> btn-outline{Toggle Dev Mode}
 status-box[Toggle Status Box] -- "toggleStatusBox()" --> status-box{class="status-box"}
 status-box-header[Toggle Warning History] -- "toggleWarningHistory()" --> status-box-header{class="status-box-header"}
 status-box-content[Clear Warnings] -- "clearWarnings()" --> status-box-content{class="status-box-content"}
 status-item[Update Status Item] -- "setProgressStatus()" --> status-item{class="status-item"}
 status-value[Update Status Value] -- "setProgressStatus()" --> status-value{class="status-value"}
 status-idle[Set Idle Status] -- "setProgressStatus()" --> status-idle{class="status-idle"}
 ai-messages[Send AI Message] -- "sendUserMessage()" --> ai-messages{class="ai-messages"}
 ai-input-area[Send AI Message] -- "sendUserMessage()" --> ai-input-area{class="ai-input-area"}
 ai-message[Display AI Message] -- "sendUserMessage()" --> ai-message{class="ai-message"}
 
 %% Dynamic Elements (Generated by JavaScript)
 generatedOptions[Generate Filter Options] -- "buildInterface()" --> generatedOptions{Generate Filter Options}
 generatedChips[Generate Column Chips] -- "buildInterface()" --> generatedChips{Generate Column Chips}
 generatedFilters[Generate Filter Controls] -- "buildInterface()" --> generatedFilters{Generate Filter Controls}
 generatedTable[Generate Data Table] -- "updateTable()" --> generatedTable{Generate Data Table}
 generatedCharts[Generate Charts] -- "updateChart()" --> generatedCharts{Generate Charts}
 generatedDropdowns[Generate Multiselect Dropdowns] -- "buildInterface()" --> generatedDropdowns{Generate Multiselect Dropdowns}
 
 %% Data Processing Flow
 buildInterface[Apply All Filters] -- "runFilter()" --> buildInterface{Function Call}
 runFilter[Update Data Table] -- "updateTable()" --> runFilter{Function Call}
 runFilter[Update Charts] -- "updateChart()" --> runFilter{Function Call}
 buildInterface[Update Group By Selection] -- "updateGroupBySelection()" --> buildInterface{Function Call}
 buildInterface[Update Date Y Label] -- "updateDateYLabel()" --> buildInterface{Function Call}
 
 %% Expected Outputs
 toggleStatusBox[Show/Hide Status Box] --> toggleStatusBox{Status Box}
 toggleSidebar[Show/Hide Sidebar] --> toggleSidebar{Sidebar}
 toggleTheme[Switch Dark/Light Mode] --> toggleTheme{Theme}
 toggleDevMode[Enable/Disable Development Mode] --> toggleDevMode{Dev Mode}
 toggleAIChat[Show/Hide AI Assistant] --> toggleAIChat{AI Chat}
 configureAI[Open AI Configuration] --> configureAI{AI Config}
 sendUserMessage[Send Message to AI] --> sendUserMessage{AI Chat}
 toggleSheetDropdown[Show/Hide Sheet Selection] --> toggleSheetDropdown{Sheet Dropdown}
 selectAllSheets[Select/Clear All Sheets] --> selectAllSheets{Sheet Selection}
 loadSelectedSheets[Load Selected Sheets] --> loadSelectedSheets{Sheet Loading}
 updateSheetLabel[Update Sheet Selection Label] --> updateSheetLabel{Sheet UI}
 reloadCurrentSheet[Reload Sheets with Current Settings] --> reloadCurrentSheet{Sheet Refresh}
 toggleStep1Box[Show/Hide File Upload Section] --> toggleStep1Box{Step 1}
 toggleStep2Box[Show/Hide Column Selection Section] --> toggleStep2Box{Step 2}
 toggleGroupBox[Show/Hide Grouping Controls] --> toggleGroupBox{Grouping}
 toggleChartsContainer[Show/Hide Chart Section] --> toggleChartsContainer{Charts}
 toggleFilterBox[Show/Hide Filter Controls] --> toggleFilterBox{Filters}
 selectAllColumns[Select All Table Columns] --> selectAllColumns{Column Selection}
 clearAllColumns[Clear All Table Columns] --> clearAllColumns{Column Selection}
 buildInterface[Initialize Complete Dashboard] --> buildInterface{Dashboard}
 resetFilters[Reset All Active Filters] --> resetFilters{Filters}
 resetActiveFilters[Reset Active Filters] --> resetActiveFilters{Filters}
 runFilter[Apply Filters and Update All Views] --> runFilter{Data Processing}
 updateTable[Update Data Table with Current Filters] --> updateTable{Table}
 updateChart[Update Charts with Current Data] --> updateChart{Charts}
 downloadChart[Download Chart as PNG] --> downloadChart{Export}
 downloadExcel[Download Filtered Data as Excel] --> downloadExcel{Export}
 downloadDateRangeChart[Download Date Range Chart as PNG] --> downloadDateRangeChart{Export}
 downloadDateRangeExcel[Download Date Range Filtered Data as Excel] --> downloadDateRangeExcel{Export}
 
 %% Function Categories
 classDef ui fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px
 classDef data fill:#2196F3,stroke:#1976D2,stroke-width:2px
 classDef function fill:#FF9800,stroke:#F57C00,stroke-width:2px
 classDef event fill:#4CAF50,stroke:#388E3C,stroke-width:2px
```

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

This traceability map provides complete visibility into how each UI element connects to its event handlers and what outputs to expect from each interaction.
