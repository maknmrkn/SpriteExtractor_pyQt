"""
مدیریت layout و چیدمان ویجت‌ها
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QGroupBox, QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt


class LayoutManager:
    """مدیریت layout اصلی برنامه"""
    
    def __init__(self, main_window, widgets):
        self.main_window = main_window
        self.widgets = widgets
        self.central_widget = None
        self.splitter = None
        
    def setup_layout(self):
        """تنظیم layout اصلی برنامه"""
        self._create_central_widget()
        self._create_main_splitter()
        
    def _create_central_widget(self):
        """ایجاد ویجت مرکزی"""
        self.central_widget = QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_layout = main_layout
    
    def _create_main_splitter(self):
        """ایجاد splitter اصلی بین canvas و پنل سمت راست"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # اضافه کردن canvas به splitter
        canvas = self.widgets['canvas']
        self.splitter.addWidget(canvas)
        
        # اضافه کردن پنل سمت راست
        right_panel = self._create_right_panel()
        self.splitter.addWidget(right_panel)
        
        # تنظیم نسبت فضای splitter
        self.splitter.setStretchFactor(0, 3)  # Canvas: 75%
        self.splitter.setStretchFactor(1, 1)  # Right panel: 25%
        
        self.main_layout.addWidget(self.splitter)
    
    def _create_right_panel(self):
        """ایجاد پنل سمت راست"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # اضافه کردن animation preview
        right_layout.addWidget(self.widgets['animation_preview'])
        
        # اضافه کردن properties group
        properties_group = self._create_properties_group()
        right_layout.addWidget(properties_group)
        
        # اضافه کردن thumbnail grid
        right_layout.addWidget(self.widgets['thumbnail_grid'])
        
        # اضافه کردن sprite tree
        right_layout.addWidget(self.widgets['sprite_tree'])
        
        return right_panel
    
    def _create_properties_group(self):
        """ایجاد گروه properties"""
        properties_group = QGroupBox("Sprite Properties")
        properties_group.setMaximumHeight(150)
        
        properties_layout = QFormLayout(properties_group)
        properties_layout.setHorizontalSpacing(20)
        properties_layout.setVerticalSpacing(5)
        
        # اضافه کردن labelها
        properties_layout.addRow("X:", self.widgets['x_label'])
        properties_layout.addRow("Y:", self.widgets['y_label'])
        properties_layout.addRow("Width:", self.widgets['width_label'])
        properties_layout.addRow("Height:", self.widgets['height_label'])
        
        return properties_group
    
    def get_splitter(self):
        """دریافت splitter اصلی"""
        return self.splitter