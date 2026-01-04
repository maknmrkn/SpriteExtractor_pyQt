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
        """
        Initialize the LayoutManager with the main application window and a dictionary of child widgets.
        
        Parameters:
            main_window (QMainWindow): The application's main window; used as the parent and target for setting the central widget.
            widgets (dict): Mapping of pre-created widgets required to build the UI (expects keys like 'canvas', 'animation_preview', 'thumbnail_grid', 'sprite_tree', 'x_label', 'y_label', 'width_label', 'height_label').
        
        Attributes set:
            main_window: assigned from parameter.
            widgets: assigned from parameter.
            central_widget: initialized to None; created by setup_layout().
            splitter: initialized to None; created by setup_layout().
        """
        self.main_window = main_window
        self.widgets = widgets
        self.central_widget = None
        self.splitter = None
        
    def setup_layout(self):
        """
        Builds and attaches the application's central widget and main splitter layout to the main window.
        
        Creates the central widget and the primary horizontal splitter, then assembles and adds them to the window's layout.
        """
        self._create_central_widget()
        self._create_main_splitter()
        
    def _create_central_widget(self):
        """
        Create and install the central QWidget and its main vertical layout.
        
        Sets self.central_widget as the window's central widget and initializes self.main_layout
        as a QVBoxLayout on that widget with all margins and spacing set to 0.
        """
        self.central_widget = QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_layout = main_layout
    
    def _create_main_splitter(self):
        """
        Create and attach the main horizontal splitter containing the canvas and right-side panel.
        
        This method initializes and stores the splitter on self.splitter, adds the canvas and the right panel to it, sets the canvas-to-panel space ratio to 3:1, and appends the splitter to the main layout.
        """
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
        """
        Create the right-side panel containing preview, properties, thumbnails, and sprite tree.
        
        The panel uses a vertical layout with 10px spacing and 5px margins, and adds, from top to bottom: `animation_preview`, the properties group returned by `_create_properties_group()`, `thumbnail_grid`, and `sprite_tree` from `self.widgets`.
        
        Returns:
            QWidget: The configured right-side panel widget.
        """
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
        """
        Create a "Sprite Properties" group box containing labeled form rows for X, Y, Width, and Height.
        
        The returned QGroupBox is titled "Sprite Properties", limited to a maximum height of 150, and uses a QFormLayout with horizontal spacing 20 and vertical spacing 5. The form rows are populated with the widgets from self.widgets: 'x_label', 'y_label', 'width_label', and 'height_label'.
        
        Returns:
            QGroupBox: Configured group box ready to be added to a layout.
        """
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
        """
        Get the main splitter widget used by the layout manager.
        
        Returns:
            splitter (QSplitter | None): The main QSplitter instance, or `None` if it has not been created yet.
        """
        return self.splitter