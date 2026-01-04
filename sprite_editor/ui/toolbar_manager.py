"""
مدیریت toolbarهای برنامه
"""

from PyQt6.QtWidgets import (
    QToolBar, QLabel, QSpinBox, QWidget, 
    QHBoxLayout, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QColor


class ToolbarManager:
    """مدیریت toolbarهای برنامه"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbars = {}
        self.widgets = {}
        
    def setup_toolbars(self):
        """تنظیم toolbarهای برنامه"""
        self._create_grid_toolbar()
        self._create_auto_detect_toolbar()
    
    def _create_grid_toolbar(self):
        """ایجاد toolbar تنظیمات grid"""
        toolbar = QToolBar("Grid Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(toolbar)
        self.toolbars['grid'] = toolbar
        
        # Show Grid Toggle
        show_grid_action = toolbar.addAction("Show Grid")
        show_grid_action.setCheckable(True)
        show_grid_action.setChecked(True)
        show_grid_action.triggered.connect(self._on_toggle_grid)
        self.widgets['show_grid_action'] = show_grid_action
        
        toolbar.addSeparator()
        
        # Grid Size Controls
        self._add_grid_size_controls(toolbar)
        
        # Padding Controls
        self._add_padding_controls(toolbar)
        
        # Spacing Controls
        self._add_spacing_controls(toolbar)
        
        # Line Style
        self._add_line_style_control(toolbar)
        
        # Color Controls
        self._add_color_controls(toolbar)
    
    def _add_grid_size_controls(self, toolbar):
        """اضافه کردن کنترل‌های اندازه grid"""
        toolbar.addWidget(QLabel("Grid:"))
        
        # Grid Width
        width_spin = QSpinBox()
        width_spin.setRange(8, 2048)
        width_spin.setValue(32)
        width_spin.setSingleStep(8)
        width_spin.setMaximumWidth(70)
        width_spin.valueChanged.connect(self._on_grid_width_changed)
        
        width_widget = QWidget()
        width_widget.setLayout(QHBoxLayout())
        width_widget.layout().addWidget(width_spin)
        width_widget.setMaximumWidth(80)
        toolbar.addWidget(width_widget)
        
        toolbar.addWidget(QLabel("×"))
        
        # Grid Height
        height_spin = QSpinBox()
        height_spin.setRange(8, 2048)
        height_spin.setValue(32)
        height_spin.setSingleStep(8)
        height_spin.setMaximumWidth(70)
        height_spin.valueChanged.connect(self._on_grid_height_changed)
        
        height_widget = QWidget()
        height_widget.setLayout(QHBoxLayout())
        height_widget.layout().addWidget(height_spin)
        height_widget.setMaximumWidth(80)
        toolbar.addWidget(height_widget)
        
        self.widgets['grid_width'] = width_spin
        self.widgets['grid_height'] = height_spin
        
        toolbar.addSeparator()
    
    def _add_padding_controls(self, toolbar):
        """اضافه کردن کنترل‌های padding"""
        toolbar.addWidget(QLabel("Pad X:"))
        
        pad_x_spin = QSpinBox()
        pad_x_spin.setRange(0, 128)
        pad_x_spin.setValue(0)
        pad_x_spin.setMaximumWidth(60)
        pad_x_spin.valueChanged.connect(self._on_padding_x_changed)
        toolbar.addWidget(pad_x_spin)
        
        toolbar.addWidget(QLabel("Pad Y:"))
        
        pad_y_spin = QSpinBox()
        pad_y_spin.setRange(0, 128)
        pad_y_spin.setValue(0)
        pad_y_spin.setMaximumWidth(60)
        pad_y_spin.valueChanged.connect(self._on_padding_y_changed)
        toolbar.addWidget(pad_y_spin)
        
        self.widgets['padding_x'] = pad_x_spin
        self.widgets['padding_y'] = pad_y_spin
        
        toolbar.addSeparator()
    
    def _add_spacing_controls(self, toolbar):
        """اضافه کردن کنترل‌های spacing"""
        toolbar.addWidget(QLabel("Space X:"))
        
        space_x_spin = QSpinBox()
        space_x_spin.setRange(0, 128)
        space_x_spin.setValue(0)
        space_x_spin.setMaximumWidth(60)
        space_x_spin.valueChanged.connect(self._on_spacing_x_changed)
        toolbar.addWidget(space_x_spin)
        
        toolbar.addWidget(QLabel("Space Y:"))
        
        space_y_spin = QSpinBox()
        space_y_spin.setRange(0, 128)
        space_y_spin.setValue(0)
        space_y_spin.setMaximumWidth(60)
        space_y_spin.valueChanged.connect(self._on_spacing_y_changed)
        toolbar.addWidget(space_y_spin)
        
        self.widgets['spacing_x'] = space_x_spin
        self.widgets['spacing_y'] = space_y_spin
        
        toolbar.addSeparator()
    
    def _add_line_style_control(self, toolbar):
        """اضافه کردن کنترل style خطوط"""
        toolbar.addWidget(QLabel("Line:"))
        
        line_combo = QComboBox()
        line_combo.addItems(["Solid", "Dotted"])
        line_combo.currentTextChanged.connect(self._on_line_style_changed)
        toolbar.addWidget(line_combo)
        
        self.widgets['line_style'] = line_combo
        
        toolbar.addSeparator()
    
    def _add_color_controls(self, toolbar):
        """اضافه کردن کنترل‌های رنگ"""
        # Grid Color Button
        grid_color_btn = QPushButton("Grid Color")
        grid_color_btn.setFixedSize(90, 24)
        grid_color_btn.clicked.connect(self._on_choose_grid_color)
        toolbar.addWidget(grid_color_btn)
        
        # Background Color Button
        bg_color_btn = QPushButton("BG Color")
        bg_color_btn.setFixedSize(90, 24)
        bg_color_btn.clicked.connect(self._on_choose_bg_color)
        toolbar.addWidget(bg_color_btn)
        
        self.widgets['grid_color_btn'] = grid_color_btn
        self.widgets['bg_color_btn'] = bg_color_btn
        
        # Set default colors
        self._update_grid_color_button(QColor(0, 255, 0))
        self._update_bg_color_button(QColor(25, 25, 25))
    
    def _create_auto_detect_toolbar(self):
        """ایجاد toolbar تشخیص خودکار"""
        toolbar = QToolBar("Auto Detection Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.setVisible(False)
        self.toolbars['auto_detect'] = toolbar
        
        # Auto Detection Mode Toggle
        auto_detect_action = toolbar.addAction("Auto Detection Mode")
        auto_detect_action.setCheckable(True)
        auto_detect_action.setChecked(False)
        auto_detect_action.triggered.connect(self.main_window._toggle_auto_detect_mode)
        self.widgets['auto_detect_action'] = auto_detect_action
        
        toolbar.addSeparator()
        
        # Min Width
        toolbar.addWidget(QLabel("Min Width:"))
        min_width_spin = QSpinBox()
        min_width_spin.setRange(1, 2048)
        min_width_spin.setValue(8)
        min_width_spin.setSingleStep(1)
        min_width_spin.setMaximumWidth(70)
        self.widgets['min_width'] = min_width_spin
        toolbar.addWidget(min_width_spin)
        
        # Min Height
        toolbar.addWidget(QLabel("Min Height:"))
        min_height_spin = QSpinBox()
        min_height_spin.setRange(1, 2048)
        min_height_spin.setValue(8)
        min_height_spin.setSingleStep(1)
        min_height_spin.setMaximumWidth(70)
        self.widgets['min_height'] = min_height_spin
        toolbar.addWidget(min_height_spin)
        
        # Detect Sprites Button
        detect_action = toolbar.addAction("Detect Sprites")
        detect_action.triggered.connect(self.main_window._auto_detect_frames)
        self.widgets['detect_action'] = detect_action
        
        # Clear Detections Button
        clear_action = toolbar.addAction("Clear Detections")
        clear_action.triggered.connect(self.main_window._clear_detections)
        self.widgets['clear_action'] = clear_action
    
    # ====== Color Management ======
    
    def _update_grid_color_button(self, color):
        """آپدیت نمایش رنگ grid"""
        self.widgets['grid_color_btn'].setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'black' if color.lightness() > 128 else 'white'};"
        )
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_color = color
            self.main_window.canvas.update_display()
    
    def _update_bg_color_button(self, color):
        """آپدیت نمایش رنگ background"""
        self.widgets['bg_color_btn'].setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'black' if color.lightness() > 128 else 'white'};"
        )
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.background_color = color
            self.main_window.canvas.update_display()
    
    # ====== Slot Methods ======
    
    def _on_toggle_grid(self, checked):
        """تغییر visibility grid"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.show_grid = checked
            self.main_window.canvas.update_display()
    
    def _on_grid_width_changed(self, value):
        """تغییر عرض grid"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_width = value
            self.main_window.canvas.update_display()
    
    def _on_grid_height_changed(self, value):
        """تغییر ارتفاع grid"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_height = value
            self.main_window.canvas.update_display()
    
    def _on_padding_x_changed(self, value):
        """تغییر padding در محور X"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_x = value
            self.main_window.canvas.update_display()
    
    def _on_padding_y_changed(self, value):
        """تغییر padding در محور Y"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_y = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_x_changed(self, value):
        """تغییر spacing در محور X"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_x = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_y_changed(self, value):
        """تغییر spacing در محور Y"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_y = value
            self.main_window.canvas.update_display()
    
    def _on_line_style_changed(self, text):
        """تغییر style خطوط"""
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.line_style = text
            self.main_window.canvas.update_display()
    
    def _on_choose_grid_color(self):
        """انتخاب رنگ grid"""
        from PyQt6.QtWidgets import QColorDialog
        
        if hasattr(self.main_window, 'canvas'):
            color = QColorDialog.getColor(
                self.main_window.canvas.grid_color, 
                self.main_window, 
                "Choose Grid Color"
            )
            if color.isValid():
                self._update_grid_color_button(color)
    
    def _on_choose_bg_color(self):
        """انتخاب رنگ background"""
        from PyQt6.QtWidgets import QColorDialog
        
        if hasattr(self.main_window, 'canvas'):
            color = QColorDialog.getColor(
                self.main_window.canvas.background_color, 
                self.main_window, 
                "Choose Background Color"
            )
            if color.isValid():
                self._update_bg_color_button(color)
    
    # ====== Public Methods ======
    
    def toggle_auto_detect_toolbar(self, visible):
        """تغییر visibility auto-detect toolbar"""
        if 'auto_detect' in self.toolbars:
            self.toolbars['auto_detect'].setVisible(visible)
    
    def get_min_width(self):
        """دریافت مقدار min width"""
        min_width_widget = self.widgets.get('min_width')
        return min_width_widget.value() if min_width_widget else 8
    
    def get_min_height(self):
        """دریافت مقدار min height"""
        min_height_widget = self.widgets.get('min_height')
        return min_height_widget.value() if min_height_widget else 8