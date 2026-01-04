"""
مدیریت منوهای برنامه
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction


class MenuManager:
    """مدیریت منوها و actions برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the MenuManager with the application's main window.
        
        Parameters:
            main_window (QMainWindow): The application's main window used to attach menus and to call window-specific handlers (e.g., open_file, save_frames, toggle_grid_toolbar).
        """
        self.main_window = main_window
        self.menu_bar = None
        
    def setup_menus(self):
        """
        Initialize and populate the main window's menu bar.
        
        Creates the File, Edit, View, and Help menus and attaches them to the main window's menu bar.
        """
        self.menu_bar = self.main_window.menuBar()
        
        # ایجاد منوها
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """
        Create and add the File menu to the application's menu bar with standard file-related actions.
        
        The menu includes actions for opening a sprite sheet, saving frames, an Export submenu with "Export Selection...", and an Exit action; each action is connected to the appropriate handler on the main window.
        """
        file_menu = self.menu_bar.addMenu("&File")
        
        # Open action
        open_action = QAction("&Open Sprite Sheet...", self.main_window)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.main_window.open_file)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction("&Save Frames As...", self.main_window)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_frames)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu("&Export")
        export_action = QAction("Export Selection...", self.main_window)
        export_action.triggered.connect(self._on_export_selection)
        export_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self.main_window)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
    
    def _create_edit_menu(self):
        """
        Create the Edit menu and add its actions to the application's menu bar.
        
        Adds the following actions to the Edit menu:
        - "Auto-detect Frames": triggers main_window._auto_detect_frames.
        - "Grid Settings...": opens grid settings via _on_grid_settings.
        - "Clear Selection" (Ctrl+D): clears the current selection via _on_clear_selection.
        """
        edit_menu = self.menu_bar.addMenu("&Edit")
        
        # Auto-detect action
        detect_action = QAction("&Auto-detect Frames", self.main_window)
        detect_action.triggered.connect(self.main_window._auto_detect_frames)
        edit_menu.addAction(detect_action)
        
        edit_menu.addSeparator()
        
        # Grid settings action
        grid_action = QAction("&Grid Settings...", self.main_window)
        grid_action.triggered.connect(self._on_grid_settings)
        edit_menu.addAction(grid_action)
        
        # Clear selection action
        clear_action = QAction("&Clear Selection", self.main_window)
        clear_action.setShortcut("Ctrl+D")
        clear_action.triggered.connect(self._on_clear_selection)
        edit_menu.addAction(clear_action)
    
    def _create_view_menu(self):
        """
        Create the View menu and add its checkable actions to the application's menu bar.
        
        Adds a "Show Grid" action (checked by default) that controls grid visibility, a "Grid Toolbar" toggle (checked by default) that shows or hides the grid toolbar, and a "Detection Toolbar" toggle (unchecked by default) that shows or hides the detection toolbar. Each action is added to the View menu and wired to the corresponding handler on the main window or MenuManager.
        """
        view_menu = self.menu_bar.addMenu("&View")
        
        # Show grid action
        show_grid_action = QAction("&Show Grid", self.main_window)
        show_grid_action.setCheckable(True)
        show_grid_action.setChecked(True)
        show_grid_action.triggered.connect(self.main_window._toggle_grid_visibility)
        view_menu.addAction(show_grid_action)
        
        # Show toolbar actions
        view_menu.addSeparator()
        show_grid_toolbar = QAction("&Grid Toolbar", self.main_window)
        show_grid_toolbar.setCheckable(True)
        show_grid_toolbar.setChecked(True)
        show_grid_toolbar.triggered.connect(self._on_toggle_grid_toolbar)
        view_menu.addAction(show_grid_toolbar)
        
        show_detect_toolbar = QAction("&Detection Toolbar", self.main_window)
        show_detect_toolbar.setCheckable(True)
        show_detect_toolbar.setChecked(False)
        show_detect_toolbar.triggered.connect(self._on_toggle_detect_toolbar)
        view_menu.addAction(show_detect_toolbar)
    
    def _create_help_menu(self):
        """
        Create the Help menu and add About and Documentation actions.
        
        Adds an "&Help" menu to the menu bar with "About Sprite Editor" and "Documentation" actions and connects them to the `_on_about` and `_on_documentation` handlers respectively.
        """
        help_menu = self.menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About Sprite Editor", self.main_window)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
        # Documentation action
        docs_action = QAction("&Documentation", self.main_window)
        docs_action.triggered.connect(self._on_documentation)
        help_menu.addAction(docs_action)
    
    # ====== Slot Methods ======
    
    def _on_save_frames(self):
        """
        Invoke the main window's save action for frames.
        
        Calls main_window.save_frames() if that method exists on the main window; no action is taken otherwise.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'save_frames'):
            self.main_window.save_frames()
    
    def _on_export_selection(self):
        """
        Trigger export of the currently selected frames using the main window.
        
        If the main window implements an `export_selection` method, this method will call it; otherwise no action is taken.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'export_selection'):
            self.main_window.export_selection()
    
    def _on_grid_settings(self):
        """
        Open the main window's grid settings dialog.
        
        Calls main_window.show_grid_settings() if the main window implements it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'show_grid_settings'):
            self.main_window.show_grid_settings()
    
    def _on_clear_selection(self):
        """
        Clear the current selection in the main window.
        
        If the main window provides a `clear_selection` method, this handler invokes it; otherwise no action is taken.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'clear_selection'):
            self.main_window.clear_selection()
    
    def _on_toggle_grid_toolbar(self, checked):
        """
        Toggle the visibility of the grid toolbar on the main window.
        
        Parameters:
            checked (bool): True to show the grid toolbar, False to hide it. If the main window does not provide a `toggle_grid_toolbar` method, this call has no effect.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'toggle_grid_toolbar'):
            self.main_window.toggle_grid_toolbar(checked)
    
    def _on_toggle_detect_toolbar(self, checked):
        """
        Set the visibility of the detection toolbar.
        
        Parameters:
            checked (bool): True to show the detection toolbar, False to hide it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'toggle_detect_toolbar'):
            self.main_window.toggle_detect_toolbar(checked)
    
    def _on_about(self):
        """
        Show an "About Sprite Editor" dialog with the application name and a short description.
        
        Displays a modal About dialog titled "About Sprite Editor" containing the application version and a brief description of the tool.
        """
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(self.main_window, 
                         "About Sprite Editor",
                         "Sprite Editor v1.0\n\nA powerful sprite sheet extraction tool.")
    
    def _on_documentation(self):
        """
        Show an information dialog that directs the user to the application's documentation.
        
        Displays a modal message box titled "Documentation" containing the documentation URL:
        https://github.com/your-repo/docs
        """
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.information(self.main_window,
                               "Documentation",
                               "Documentation is available at: \n\nhttps://github.com/your-repo/docs")