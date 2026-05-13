# Header Controls Events

```mermaid
graph TD
    %% Header Control Components
    sidebarToggle --> toggleSidebar --> ToggleSidebarVisibility
    themeBtn --> toggleTheme --> ToggleDarkLightTheme
    devStatus --> toggleDevMode --> ToggleDevelopmentMode
    
    %% Sidebar Toggle Flow
    UserClickSidebar[User Clicks Sidebar Toggle] --> sidebarToggle
    sidebarToggle --> CheckSidebarState[Check Current Sidebar State]
    CheckSidebarState --> ToggleSidebarClass[Toggle Sidebar CSS Class]
    ToggleSidebarClass --> UpdateLayout[Update Page Layout]
    UpdateLayout --> SaveSidebarState[Save Sidebar State]
    
    %% Theme Toggle Flow
    UserClickTheme[User Clicks Theme Button] --> themeBtn
    themeBtn --> CheckCurrentTheme[Check Current Theme]
    CheckCurrentTheme --> SwitchTheme[Switch Between Dark/Light]
    SwitchTheme --> UpdateThemeClass[Update Theme CSS Class]
    UpdateThemeClass --> SaveThemePreference[Save Theme Preference]
    
    %% Dev Mode Toggle Flow
    UserClickDev[User Clicks Dev Status] --> devStatus
    devStatus --> CheckDevMode[Check Current Dev Mode]
    CheckDevMode --> ToggleDevFeatures[Toggle Development Features]
    ToggleDevFeatures --> UpdateDevStatus[Update Dev Status Display]
    UpdateDevStatus --> SaveDevMode[Save Dev Mode State]
    
    %% Expected Outputs
    ToggleSidebarVisibility --> SidebarShown[Sidebar Shown]
    ToggleSidebarVisibility --> SidebarHidden[Sidebar Hidden]
    ToggleDarkLightTheme --> DarkMode[Dark Mode Enabled]
    ToggleDarkLightTheme --> LightMode[Light Mode Enabled]
    ToggleDevelopmentMode --> DevEnabled[Development Mode Enabled]
    ToggleDevelopmentMode --> DevDisabled[Development Mode Disabled]
```

## Event Handlers

### **Header Control Events**
- **Toggle Sidebar**: `toggleSidebar()` - Shows/hides main sidebar
- **Toggle Theme**: `toggleTheme()` - Switches between dark and light modes
- **Toggle Dev Mode**: `toggleDevMode()` - Enables/disables development features

### **UI Components**
- **Sidebar Toggle**: Button to collapse/expand sidebar
- **Theme Button**: Button to switch between themes
- **Dev Status**: Indicator for development mode status

### **Expected Outputs**
- **Sidebar State**: Visible or hidden based on user preference
- **Theme State**: Dark or light mode applied to interface
- **Dev Mode State**: Development features enabled or disabled
- **Persistent Settings**: All preferences saved for future sessions

### **Data Flow**
1. User clicks header control button
2. Current state is checked
3. Appropriate CSS classes are toggled
4. Page layout is updated
5. New state is saved to localStorage

### **Advanced Features**
- **Responsive Design**: Sidebar adapts to screen size
- **Smooth Transitions**: CSS animations for state changes
- **Keyboard Shortcuts**: Alt+S for sidebar, Alt+T for theme
- **Accessibility**: Screen reader compatible state changes
