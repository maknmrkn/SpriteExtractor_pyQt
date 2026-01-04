"""
مدیریت استایل و theme برنامه
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class StyleManager:
    """مدیریت استایل و ظاهر برنامه"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_theme = 'dark'
        self.stylesheets = {}
        
        self._init_stylesheets()
    
    def _init_stylesheets(self):
        """مقداردهی اولیه stylesheetها"""
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
        """اعمال theme به برنامه"""
        if theme_name in self.stylesheets:
            self.current_theme = theme_name
            self.main_window.setStyleSheet(self.stylesheets[theme_name])
            
            # تنظیم palette برای consistency بهتر
            self._apply_palette(theme_name)
            
            return True
        return False
    
    def _apply_palette(self, theme_name):
        """اعمال palette به برنامه"""
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
        """دریافت لیست themeهای موجود"""
        return list(self.stylesheets.keys())
    
    def get_current_theme(self):
        """دریافت theme فعلی"""
        return self.current_theme
    
    def set_custom_style(self, style_sheet):
        """تنظیم stylesheet سفارشی"""
        self.main_window.setStyleSheet(style_sheet)
    
    def reset_to_default(self):
        """بازنشانی به theme پیش‌فرض"""
        return self.apply_theme('dark')