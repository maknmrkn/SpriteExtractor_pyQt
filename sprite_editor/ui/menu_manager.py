"""
مدیریت منوهای برنامه
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction


class MenuManager:
    """مدیریت منوها و actions برنامه"""
    
    def __init__(self, main_window):
        """
        Create a MenuManager bound to a main window and initialize its menu state.
        
        Parameters:
            main_window: The application's main window (QMainWindow or compatible) that MenuManager will control. It is expected to implement UI handlers used by menu actions (for example: `open_file`, `save_frames`, `export_selection`, `show_grid_settings`, `clear_selection`, `toggle_grid_toolbar`, `toggle_detect_toolbar`, and `close`).
        
        Attributes set:
            main_window: Reference to the provided main window.
            menu_bar: Placeholder for the window's menu bar (initialized to None).
        """
        self.main_window = main_window
        self.menu_bar = None
        
    def setup_menus(self):
        """
        Initialize and attach the application's main menu bar to the main window.
        
        This sets the MenuManager.menu_bar from the main window and creates the File, Edit, View, and Help menus.
        """
        self.menu_bar = self.main_window.menuBar()
        
        # ایجاد منوها
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """
        Create the "File" menu on the menu bar and populate it with common file actions.
        
        Adds the following actions and wiring:
        - "Open Sprite Sheet..." (Ctrl+O) → calls main_window.open_file.
        - "Save Frames As..." (Ctrl+S) → calls this manager's _on_save_frames.
        - "Export" submenu containing "Export Selection..." → calls this manager's _on_export_selection.
        - "Exit" (Ctrl+Q) → calls main_window.close.
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
        Create the Edit menu and populate it with edit-related actions.
        
        Adds "Auto-detect Frames", "Grid Settings...", and "Clear Selection" (shortcut Ctrl+D) actions, with triggers connected to the main window or MenuManager slot handlers.
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
        Create the View menu and populate it with view-related actions.
        
        Adds a checkable "Show Grid" action (checked by default) that toggles the main window's grid visibility, and two checkable toolbar visibility actions: "Grid Toolbar" (checked by default) which invokes the manager's grid-toolbar toggle handler, and "Detection Toolbar" (unchecked by default) which invokes the detection-toolbar toggle handler.
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
        Create the Help menu on the menu bar and add About and Documentation actions.
        
        Adds an "About Sprite Editor" action that triggers the _on_about handler and a "Documentation" action that triggers the _on_documentation handler.
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
        Trigger saving of frames through the main window.
        
        If the main window implements a `save_frames` method, calls it to perform the save operation; otherwise does nothing.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'save_frames'):
            self.main_window.save_frames()
    
    def _on_export_selection(self):
        """
        Invoke the main window's export_selection handler if implemented.
        
        Calls self.main_window.export_selection() when the main window provides that method; no action is taken if it is absent.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'export_selection'):
            self.main_window.export_selection()
    
    def _on_grid_settings(self):
        """
        Open the main window's grid settings dialog if available.
        
        If the main window provides a grid settings handler, this method triggers it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'show_grid_settings'):
            self.main_window.show_grid_settings()
    
    def _on_clear_selection(self):
        """
        Clear the current selection in the main window.
        
        If the main window implements a `clear_selection` method, this method invokes it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'clear_selection'):
            self.main_window.clear_selection()
    
    def _on_toggle_grid_toolbar(self, checked):
        """
        Set visibility of the grid toolbar.
        
        Parameters:
            checked (bool): True to show the grid toolbar, False to hide it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'toggle_grid_toolbar'):
            self.main_window.toggle_grid_toolbar(checked)
    
    def _on_toggle_detect_toolbar(self, checked):
        """
        Handle toggling of the detection toolbar visibility.
        
        Calls the main window's `toggle_detect_toolbar` method with the given state if that method exists.
        
        Parameters:
            checked (bool): `True` to show the detection toolbar, `False` to hide it.
        """
        # این متد باید در MainWindow پیاده‌سازی شود
        if hasattr(self.main_window, 'toggle_detect_toolbar'):
            self.main_window.toggle_detect_toolbar(checked)
    
    def _on_about(self):
        """
        Show the application's About dialog.
        
        Displays an "About Sprite Editor" dialog containing the application name, version (v1.0), and a brief description.
        """
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(self.main_window, 
                         "About Sprite Editor",
                         "Sprite Editor v1.0\n\nA powerful sprite sheet extraction tool.")
    
    def _on_documentation(self):
        """
        Show a modal informational dialog that points to the project's documentation.
        
        Displays a message box titled "Documentation" containing the documentation URL for the application.
        """
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.information(self.main_window,
                               "Documentation",
                               "Documentation is available at: \n\nhttps://github.com/your-repo/docs")