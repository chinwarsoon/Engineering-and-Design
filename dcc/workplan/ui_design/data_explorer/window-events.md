# Window Event Listeners

```mermaid
graph TD
    %% Window Level Events
    Window --> FileUploadListener[File Upload Event Listener]
    Window --> ClickOutsideListener[Click Outside Event Listener]
    Window --> ToastDismissalListener[Toast Dismissal Event Listener]
    
    %% File Upload Event
    FileUploadListener --> UploadChange[addEventListener change]
    UploadChange --> FileSelected[File Selected Event]
    FileSelected --> ValidateFile[Validate File Type]
    ValidateFile --> ParseExcel[Parse Excel File]
    ParseExcel --> UpdateUI[Update File Upload UI]
    
    %% Click Outside Event
    ClickOutsideListener --> DocumentClick[addEventListener click]
    DocumentClick --> CheckTarget[Check Click Target]
    CheckTarget --> IsOutsideClick[Is Click Outside Element]
    IsOutsideClick --> CloseDropdowns[Close All Dropdowns]
    IsOutsideClick --> CloseSearchBoxes[Close All Search Boxes]
    IsOutsideClick --> CloseMenus[Close All Menus]
    
    %% Toast Dismissal Event
    ToastDismissalListener --> ToastClick[addEventListener click]
    ToastClick --> FindToastElement[Find Toast Element]
    FindToastElement --> IsToastClick[Is Click on Toast]
    IsToastClick --> DismissToast[Dismiss Toast Notification]
    IsToastClick --> RemoveToast[Remove Toast from DOM]
    
    %% Event Delegation
    DocumentClick --> DynamicElements[Handle Dynamic Elements]
    DynamicElements --> CheckGeneratedElements[Check Generated Elements]
    CheckGeneratedElements --> ApplyEventDelegation[Apply Event Delegation]
    ApplyEventDelegation --> HandleDynamicEvents[Handle Dynamic Events]
    
    %% Expected Outputs
    CloseDropdowns --> DropdownsClosed[All Dropdowns Closed]
    CloseSearchBoxes --> SearchBoxesClosed[All Search Boxes Closed]
    CloseMenus --> MenusClosed[All Menus Closed]
    DismissToast --> ToastDismissed[Toast Notification Dismissed]
    RemoveToast --> ToastRemoved[Toast Removed from View]
```

## Event Handlers

### **Window-Level Events**
- **File Upload Listener**: `addEventListener("change")` on document - Handles file selection
- **Click Outside Listener**: `addEventListener("click")` on document - Closes UI elements
- **Toast Dismissal Listener**: `addEventListener("click")` on document - Handles toast clicks

### **Click Outside Logic**
- **Target Detection**: Checks if click is outside specified elements
- **Element Closing**: Closes dropdowns, search boxes, menus
- **Multiple Elements**: Handles various UI components simultaneously
- **Prevent Conflicts**: Avoids closing when clicking inside elements

### **Toast Management**
- **Auto-Dismiss**: Click anywhere on toast to dismiss
- **DOM Removal**: Cleanly removes toast from page
- **Animation**: Smooth fade-out effect
- **Queue Management**: Handles multiple toasts in sequence

### **Event Delegation**
- **Dynamic Elements**: Handles events for dynamically created elements
- **Performance**: Efficient single listener for multiple elements
- **Future-Proof**: Works for elements added after page load
- **Maintenance**: Easy to update and manage

### **Expected Outputs**
- **Clean UI State**: All floating elements properly closed
- **Responsive Behavior**: Natural user interaction patterns
- **Memory Efficiency**: Single listener handles multiple elements
- **Consistent Experience**: Predictable UI behavior

### **Advanced Features**
- **Debouncing**: Prevents rapid successive triggers
- **Context Awareness**: Differentiates between various UI contexts
- **Accessibility**: Keyboard support for closing elements
- **Mobile Optimization**: Touch-friendly interaction patterns
