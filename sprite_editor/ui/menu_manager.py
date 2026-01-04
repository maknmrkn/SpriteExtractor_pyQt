from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence


class MenuManager:
    """
    Manages the menu bar and its associated actions for the main window.
    """
    def __init__(self, main_window):
        """
        Initialize the menu manager with a reference to the main window.
        
        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self._create_menu_bar()

    def _create_menu_bar(self):
        """Create and configure the menu bar."""
        menu_bar = self.main_window.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        open_action = file_menu.addAction("Open Sprite Sheet...")
        open_action.setShortcut(QKeySequence.fromString("Ctrl+O"))
        open_action.triggered.connect(self.main_window.open_file)

        save_action = file_menu.addAction("Save Frames As...")
        save_action.setShortcut(QKeySequence.fromString("Ctrl+S"))
        # TODO: Connect to save_frames method

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence.fromString("Ctrl+Q"))
        exit_action.triggered.connect(self.main_window.close)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        extract_action = edit_menu.addAction("Auto-detect Frames")
        extract_action.triggered.connect(self.main_window._auto_detect_frames)