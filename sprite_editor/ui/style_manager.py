"""
مدیریت استایل و theme برنامه
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class StyleManager:
    """مدیریت استایل و ظاهر برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the StyleManager with a reference to the application's main window, set the default theme to "dark", and load built-in stylesheets.
        
        Parameters:
            main_window: The application's main window (e.g., a QMainWindow) that styles and palettes will be applied to.
        """
        self.main_window = main_window
        self.current_theme = 'dark'
        self.stylesheets = {}
        
        self._init_stylesheets()
    
    def _init_stylesheets(self):
        """
        Initialize built-in QSS stylesheets for dark and light themes.
        
        Populates `self.stylesheets` with two entries, "dark" and "light", each containing a QSS string that styles common widgets (QMainWindow, QGroupBox and its title, QTreeWidget and its items, QLabel, and QScrollArea) to provide the corresponding visual themes.
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
        Apply a named stylesheet and corresponding palette to the main window.
        
        Apply the stylesheet identified by theme_name from the manager's known styles and update the current theme and window palette for visual consistency.
        
        Parameters:
            theme_name (str): The key of a stylesheet defined in the manager's stylesheets (e.g., 'dark', 'light').
        
        Returns:
            bool: `true` if the theme was found and applied, `false` otherwise.
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
        Apply a color palette to the main window according to the specified theme.
        
        For the 'dark' theme this configures window, text, base, alternate base, tooltip,
        button, link and highlight colors to a dark scheme; for any other theme the
        default (light) palette is used. The resulting palette is applied to
        self.main_window.
        
        Parameters:
            theme_name (str): Theme identifier to apply. Use 'dark' for the dark palette;
                any other value results in the default light palette.
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
        Retrieve the names of all registered themes.
        
        Returns:
            list[str]: Available theme names in the manager.
        """
        return list(self.stylesheets.keys())
    
    def get_current_theme(self):
        """
        Return the name of the currently active theme.
        
        Returns:
            current_theme (str): The name of the currently selected theme (e.g., 'dark' or 'light').
        """
        return self.current_theme
    
    def set_custom_style(self, style_sheet):
        """
        Apply a custom stylesheet to the main window without modifying the stored theme definitions.
        
        Parameters:
            style_sheet (str): QSS/CSS string to apply to the main window.
        """
        self.main_window.setStyleSheet(style_sheet)
    
    def reset_to_default(self):
        """
        Reset the UI theme to the default ("dark").
        
        Returns:
            True if the default theme was applied successfully, False otherwise.
        """
        return self.apply_theme('dark')