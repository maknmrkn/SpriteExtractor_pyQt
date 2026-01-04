from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


class StyleManager:
    """
    Manages the styling and theming for the application.
    """
    def __init__(self, main_window):
        """
        Initialize the style manager with a reference to the main window.
        
        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self._apply_initial_styles()

    def _apply_initial_styles(self):
        """Apply initial styling to the application."""
        # Set application-wide styles
        self.main_window.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 4px 0px 4px;
            }
        """)