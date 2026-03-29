# Stage 7: Data Processing

```mermaid
graph TD
    %% Stage Definition
    Stage7[Stage 7: Data Processing] --> Input7[Input: Raw Data + Filters]
    Input7 --> Process7[Processing: runFilter]
    Process7 --> Output7[Output: Filtered Data]
    
    %% Core Processing Function
    runFilter[runFilter Function] --> ApplyFilters[Apply All Active Filters]
    ApplyFilters --> FilterData[Filter Raw Data Array]
    FilterData --> UpdateViews[Update All Data Views]
    UpdateViews --> FilteredResult[Final Filtered Data]
    
    %% Filter Application Process
    RawData[Raw Data Array] --> TextFiltering[Apply Text Filters]
    TextFiltering --> NumberFiltering[Apply Numeric Filters]
    NumberFiltering --> DateFiltering[Apply Date Filters]
    DateFiltering --> CategoryFiltering[Apply Category Filters]
    CategoryFiltering --> GlobalSearchFiltering[Apply Global Search]
    GlobalSearchFiltering --> FilteredData[Filtered Data Array]
    
    %% Data Processing Flow
    FilteredData --> Grouping[Apply Grouping Logic]
    Grouping --> Sorting[Apply Sorting Logic]
    Sorting --> Aggregation[Apply Aggregation Functions]
    Aggregation --> Pagination[Apply Pagination]
    Pagination --> ProcessedData[Final Processed Data]
    
    %% Performance Optimization
    LargeDataset[Large Dataset Detection] --> Virtualization[Apply Virtualization]
    Virtualization --> Debouncing[Apply Input Debouncing]
    Debouncing --> Caching[Apply Result Caching]
    Caching --> OptimizedProcessing[Optimized Data Processing]
    
    %% Expected Outputs
    ProcessedData --> FilteredArray[Filtered Data Array]
    ProcessedData --> GroupedData[Grouped Data Structure]
    ProcessedData --> AggregatedData[Aggregated Results]
    ProcessedData --> RecordCount[Filtered Record Count]
```

## Event Handlers

### **Core Processing Events**
- **Run Filter**: `runFilter` - Main function that applies all active filters
- **Apply Filters**: Internal function that processes each filter type
- **Update Views**: Updates table, charts, and status after filtering
- **Process Large Data**: Special handling for datasets exceeding performance thresholds

### **Filter Processing**
- **Text Filters**: Contains, starts with, ends with, exact match
- **Numeric Filters**: Range filters, greater than, less than, equals
- **Date Filters**: Date ranges, relative dates (last 30 days, etc.)
- **Category Filters**: Multi-select, single-select, exclude options
- **Global Search**: Full-text search across all columns

### **Data Operations**
- **Grouping**: Groups data by specified columns
- **Sorting**: Sorts by multiple columns with custom order
- **Aggregation**: Calculates sum, count, avg, min, max functions
- **Pagination**: Implements virtual scrolling for large datasets

### **Performance Features**
- **Debouncing**: Prevents excessive re-filtering during rapid input
- **Virtualization**: Only renders visible rows for large datasets
- **Caching**: Stores filter results to avoid reprocessing
- **Progress Indicators**: Shows progress for long-running operations

### **Expected Outputs**
- **Filtered Data Array**: Data after all filters applied
- **Grouped Data**: Data structured by grouping criteria
- **Aggregated Results**: Summary statistics and calculations
- **Record Count**: Total number of records after filtering
- **Processing Status**: Current state and progress information

### **Error Handling**
- **Invalid Filters**: Handles malformed filter criteria
- **Performance Issues**: Detects and handles slow operations
- **Memory Limits**: Manages large dataset processing
- **Data Corruption**: Validates data integrity during processing
