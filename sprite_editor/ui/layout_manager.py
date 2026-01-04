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
        Initialize the LayoutManager with the main window and a registry of UI widgets.
        
        Parameters:
            main_window (QMainWindow): The application's main window where the layout will be applied.
            widgets (dict): A mapping of widget names to widget instances used to compose the layout.
        
        Detailed behavior:
            Stores `main_window` and `widgets` on the instance and initializes `central_widget` and `splitter` to `None`.
        """
        self.main_window = main_window
        self.widgets = widgets
        self.central_widget = None
        self.splitter = None
        
    def setup_layout(self):
        """
        Set up the main application layout.
        
        Creates and configures the central widget and the primary horizontal splitter that divides the canvas and right-side panel.
        """
        self._create_central_widget()
        self._create_main_splitter()
        
    def _create_central_widget(self):
        """
        Create and attach the main central widget for the window.
        
        Creates a QWidget, sets it as the main window's central widget, and installs a QVBoxLayout with zero margins and spacing. Stores the created widget on `self.central_widget` and the layout on `self.main_layout`.
        """
        self.central_widget = QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_layout = main_layout
    
    def _create_main_splitter(self):
        """
        Create and insert the main horizontal splitter into the central layout.
        
        Constructs a QSplitter oriented horizontally, adds the canvas widget on the left and the right-side panel on the right, configures their size ratio to 3:1, and appends the splitter to the manager's main layout.
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
        Builds the right-side panel containing auxiliary widgets.
        
        The panel arranges the animation preview, sprite properties group, thumbnail grid, and sprite tree vertically with 5px margins and 10px spacing.
        
        Returns:
            QWidget: A widget containing the assembled right-side layout.
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
        Create and return the "Sprite Properties" group box containing form rows for sprite geometry.
        
        The returned QGroupBox is titled "Sprite Properties", constrained to a maximum height of 150 pixels, and contains a QFormLayout with labeled rows for X, Y, Width, and Height populated from the manager's widget registry.
        
        Returns:
            QGroupBox: A configured group box widget containing the properties form.
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
        Access the main QSplitter that divides the central canvas and the right-side panel.
        
        Returns:
            QSplitter | None: The primary splitter instance, or `None` if the layout has not been created yet.
        """
        return self.splitter