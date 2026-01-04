"""
مدیریت استایل و theme برنامه
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class StyleManager:
    """مدیریت استایل و ظاهر برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the StyleManager for a main application window.
        
        Sets the initial theme to 'dark', prepares the stylesheets container, and populates it by calling _init_stylesheets.
        
        Parameters:
        	main_window (QWidget): The main application window (e.g., QMainWindow) that stylesheets and palettes will be applied to.
        """
        self.main_window = main_window
        self.current_theme = 'dark'
        self.stylesheets = {}
        
        self._init_stylesheets()
    
    def _init_stylesheets(self):
        """
        Initialize the manager's stylesheets for built-in 'dark' and 'light' themes.
        
        Populates self.stylesheets with CSS strings for 'dark' and 'light' keys, defining widget appearance (QMainWindow, QGroupBox, QTreeWidget, QLabel, QScrollArea, etc.). This method does not return a value.
        """
        # Dark Theme
        self.stylesheets['dark'] = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTreeWidget {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #4a4a4a;
            }
            QLabel {
                color: #ffffff;
            }
            QScrollArea {
                border: 1px solid #555;
                border-radius: 3px;
            }
        """
        
        # Light Theme
        self.stylesheets['light'] = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTreeWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
            }
            QLabel {
                color: #000000;
            }
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """
    
    def apply_theme(self, theme_name='dark'):
        """
        Apply a named theme to the application's main window and update the palette to match.
        
        Parameters:
            theme_name (str): Name of the theme to apply; must be a key in self.stylesheets.
        
        Returns:
            bool: `True` if the theme was found and applied, `False` otherwise.
        """
        if theme_name in self.stylesheets:
            self.current_theme = theme_name
            self.main_window.setStyleSheet(self.stylesheets[theme_name])
            
            # تنظیم palette برای consistency بهتر
            self._apply_palette(theme_name)
            
            return True
        return False
    
    def _apply_palette(self, theme_name):
        """
        Apply a QPalette to the main window based on the given theme name.
        
        For 'dark', configures a dark color palette (window, text, base, alternate base, tooltip,
        button, links, highlights, etc.). For any other value, applies the default palette.
        
        Parameters:
            theme_name (str): Theme identifier; 'dark' selects the dark palette, other values use the default palette.
        """
        palette = QPalette()
        
        if theme_name == 'dark':
            palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:
            # Light theme - استفاده از palette پیش‌فرض
            palette = QPalette()
        
        self.main_window.setPalette(palette)
    
    def get_available_themes(self):
        """
        Return the names of themes available in the manager.
        
        Returns:
            list[str]: A list of available theme names.
        """
        return list(self.stylesheets.keys())
    
    def get_current_theme(self):
        """
        Get the name of the currently applied theme.
        
        Returns:
            str: The current theme name (for example, 'dark' or 'light').
        """
        return self.current_theme
    
    def set_custom_style(self, style_sheet):
        """
        Apply a custom Qt stylesheet to the main window.
        
        Parameters:
            style_sheet (str): Qt stylesheet string to apply to the application's main window.
        """
        self.main_window.setStyleSheet(style_sheet)
    
    def reset_to_default(self):
        """
        Reset the theme to the default ('dark').
        
        Returns:
            bool: True if the default theme was successfully applied, False otherwise.
        """
        return self.apply_theme('dark')