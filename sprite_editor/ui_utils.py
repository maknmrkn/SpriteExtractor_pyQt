from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget, QFileDialog, QSizePolicy, QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidgetAction, QComboBox, QPushButton, QColorDialog, QDockWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView, QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox, QFrame, QSplitter, QGroupBox, QFormLayout
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon


class UIUtils:
    """
    Contains UI utility methods that were previously in MainWindow
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def _reset_properties_display(self):
        """Reset the properties display"""
        self.main_window.x_label.setText("-")
        self.main_window.y_label.setText("-")
        self.main_window.width_label.setText("-")
        self.main_window.height_label.setText("-")
    
    def _update_grid_color_button(self, color: QColor):
        self.main_window.grid_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.main_window.canvas.grid_color = color
        self.main_window.canvas.update_display()

    def _update_bg_color_button(self, color: QColor):
        self.main_window.bg_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.main_window.canvas.background_color = color
        self.main_window.canvas.update_display()

    def _on_choose_grid_color(self):
        color = QColorDialog.getColor(self.main_window.canvas.grid_color, self.main_window, "Choose Grid Color")
        if color.isValid():
            self._update_grid_color_button(color)

    def _on_choose_bg_color(self):
        color = QColorDialog.getColor(self.main_window.canvas.background_color, self.main_window, "Choose Background Color")
        if color.isValid():
            self._update_bg_color_button(color)

    def _on_line_style_changed(self, text):
        self.main_window.canvas.line_style = text
        self.main_window.canvas.update_display()

    def _on_grid_toggled(self, checked):
        self.main_window.canvas.show_grid = checked
        self.main_window.canvas.update_display()

    def _on_grid_width_changed(self, value):
        self.main_window.canvas.grid_width = value
        self.main_window.canvas.update_display()

    def _on_grid_height_changed(self, value):
        self.main_window.canvas.grid_height = value
        self.main_window.canvas.update_display()

    def _on_padding_x_changed(self, value):
        self.main_window.canvas.padding_x = value
        self.main_window.canvas.update_display()

    def _on_padding_y_changed(self, value):
        self.main_window.canvas.padding_y = value
        self.main_window.canvas.update_display()

    def _on_spacing_x_changed(self, value):
        self.main_window.canvas.spacing_x = value
        self.main_window.canvas.update_display()

    def _on_spacing_y_changed(self, value):
        self.main_window.canvas.spacing_y = value
        self.main_window.canvas.update_display()