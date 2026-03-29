# Stage 5: Column Selection

```mermaid
graph TD
    %% Stage Definition
    Stage5[Stage 5: Column Selection] --> Input5[Input: Raw Data Array]
    Input5 --> Process5[Processing: buildInterface]
    Process5 --> Output5[Output: Filterable Columns]
    
    %% UI Components
    step2Header --> UpdateStep2[Update Step 2 Header]
    toggleStep2Btn --> ToggleStep2Box[Toggle Step 2 Box]
    headerListContainer --> ToggleHeaderContainer[Toggle Header List]
    headerList --> PopulateHeaders[Populate Header List]
    
    %% Column Selection Controls
    colCheck --> SyncChip[Sync Chip Visual State]
    toggleChip --> UpdateChipState[Update Toggle Chip State]
    selectAllColumns --> SelectAllCols[Select All Table Columns]
    clearAllColumns --> ClearAllCols[Clear All Table Columns]
    
    %% Interface Building
    RawData[Raw Data Array] --> ExtractHeaders[Extract Column Headers]
    ExtractHeaders --> GenerateChips[Generate Column Toggle Chips]
    GenerateChips --> CreateCheckboxes[Create Checkbox Elements]
    CreateCheckboxes --> BuildInterface[Complete Column Interface]
    
    %% Column Selection Flow
    ColumnHeaders[Column Headers Array] --> HeaderList[Header List Element]
    HeaderList --> ColumnChips[Column Toggle Chips]
    ColumnChips --> ChipInteraction[User Chip Interaction]
    ChipInteraction --> ColumnState[Column Selection State]
    ColumnState --> FilterableColumns[Filterable Columns Array]
    
    %% Expected Outputs
    FilterableColumns --> SelectedColumns[Selected Columns Array]
    FilterableColumns --> HiddenColumns[Hidden Columns Array]
    FilterableColumns --> ColumnVisibility[Column Visibility States]
    FilterableColumns --> InterfaceReady[Interface Ready for Filtering]
```

## Event Handlers

### **Column Selection Events**
- **Build Interface**: `buildInterface` - Main function for building column selection UI
- **Sync Chip**: `syncChip` - Synchronizes chip visual state with checkbox
- **Toggle Step 2**: `toggleStep2Box` - Shows/hides column selection section
- **Select All Columns**: `selectAllColumns` - Selects all available columns
- **Clear All Columns**: `clearAllColumns` - Deselects all columns

### **UI Components**
- **Header List**: Container for column selection checkboxes
- **Column Chips**: Toggle switches for each column
- **Select/Clear All**: Bulk selection controls
- **Initialize Dashboard**: Button to proceed to filtering stage

### **Data Flow**
1. **Header Extraction**: Get column names from raw data array
2. **Chip Generation**: Create toggle elements for each column
3. **Interface Building**: Assemble complete selection interface
4. **User Interaction**: Handle clicks on column toggles
5. **State Management**: Track selected vs hidden columns
6. **Output Preparation**: Prepare arrays for filtering stage

### **Expected Outputs**
- **Filterable Columns**: Array of columns available for filtering
- **Selected Columns**: Array of columns chosen for display
- **Hidden Columns**: Array of columns hidden from view
- **Column States**: Object tracking visibility for each column
- **Interface State**: Complete UI ready for filtering operations

### **User Experience**
- **Visual Feedback**: Immediate visual response to column selection
- **Bulk Operations**: Quick select/clear all functionality
- **Persistent State**: Selections maintained during refresh
- **Intuitive Layout**: Clear organization of available columns
