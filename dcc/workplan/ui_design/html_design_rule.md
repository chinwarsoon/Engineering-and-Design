# apply the follow requirements to all HTML files

## dependencies
1. always consider interactive standalone webpage design.
2. maintain and seperate an independent css file.
3. schema driven


## overall layout and theme design
1. the layout will be similar as VS Code, having title/manue bar, side icon bar panel, toggelable left sidebar panel linked to side icon bar panel, bottom status bar, toggelable right sidebar panel.
2. color theme should be toggled by clicking the theme button in the top right corner in tile bare.
3. color theme should have light (bright backgorund), dark (dark background), sky (sky light blue background), ocean (ocean blue background), and presentation (light grey background) options. make sure the theme is saved in local storage.
4. height and width of all panels should be adjustable.
5. all HTML files should refer to same CSS file.
6. only show icons in side icon bar panel, tile bar, icon buttons.



## title base
1. title/manue bar should span the whole width of the screen. title bar can contain theme button, layout button, manue, global searching.
2. the layout button in the title bar can be used to switch between different layouts, such as single column, two columns, three columns, etc.
3. show layout toggle button.


## left side icon bar
1. lefe side icon bar should contain icons for left side panel and righ side panel.
2. icons for left side panel to be on the top.
3. icons for right side panel to be at the bottom. A divide line should be added before the first icon for right side panel.
4. click side icon bar to toggle left or right sidebar panel to show related content.

## left side panel
1. contents in a panel should be toggleable.
2. the panel should be resizable by dragging the right edge of the panel.
3. the panel should be collapsible by clicking the side icon bar.

## right side panel
1. contents in a panel should be toggleable.
2. the panel should be resizable by dragging the left edge of the panel.
3. right side panel should at the right of the screen.

## file loading panel
1. the file loading panel should be able to load files from local disk, or load the specific pipeline files.
2. the file loading panel should list all files loaded.
3. allow user to drag and drop files to the panel to load the files.
4. status bar should show which loaded file is selected.
5. the file loading panel should be collapsible by clicking the side icon bar.

## tree selection panel
1. the tree selection panel should show the hierarchical structure of the loaded content.
2. the tree selection panel should allow user to select any node in the tree to show the content in the main content panel.
3. the tree selection panel should be collapsible by clicking the side icon bar.
4. allow to expand all or collapse all nodes in the tree.

## icons
1. info icon is ℹ️
2. file load icon is 📂
3. help icon is ❓
4. setting icon is ⚙️
5. tree icon is 🌳

## Help
1. store following details in ui_help.json file. HTML file can load the value from this json file.:
- help text
- about text
- revision text
- default file names, folders, definitions


## main content panel



