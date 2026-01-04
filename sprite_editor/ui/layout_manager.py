from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QGroupBox, QFormLayout, QSplitter, 
    QStatusBar, QFrame, QScrollArea, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class LayoutManager:
    """
    Manages the layout and widgets for the main window.
    """
    def __init__(self, main_window):
        """
        Initialize the layout manager with a reference to the main window.
        
        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self._setup_central_widget()
        self._setup_status_bar()

    def _setup_central_widget(self):
        """Set up the main layout and widgets."""
        # Create central widget with a vertical layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a horizontal splitter to separate canvas and right panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Canvas
        self.main_window.canvas.setSizePolicy(
            self.main_window.canvas.sizePolicy().Policy.Expanding, 
            self.main_window.canvas.sizePolicy().Policy.Expanding
        )
        splitter.addWidget(self.main_window.canvas)

        # Right panel containing the animation preview, properties, tree and thumbnails
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create the animation preview widget
        right_layout.addWidget(self.main_window.animation_preview)
        
        # Create a group box for sprite properties
        self.main_window.properties_group = QGroupBox("Sprite Properties")
        self.main_window.properties_group.setMaximumHeight(150)  # Limit height to keep space for tree
        properties_layout = QFormLayout(self.main_window.properties_group)
        
        # Add properties fields
        self.main_window.x_label = QLabel("-")
        self.main_window.y_label = QLabel("-")
        self.main_window.width_label = QLabel("-")
        self.main_window.height_label = QLabel("-")
        
        properties_layout.addRow("X:", self.main_window.x_label)
        properties_layout.addRow("Y:", self.main_window.y_label)
        properties_layout.addRow("Width:", self.main_window.width_label)
        properties_layout.addRow("Height:", self.main_window.height_label)
        
        right_layout.addWidget(self.main_window.properties_group)
        
        # Create the thumbnail grid widget
        right_layout.addWidget(self.main_window.thumbnail_grid)
        
        right_layout.addWidget(self.main_window.tree_manager.sprite_tree)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)  # Canvas takes 3/4 of space
        splitter.setStretchFactor(1, 1)  # Right panel takes 1/4 of space
        
        main_layout.addWidget(splitter)

    def _setup_status_bar(self):
        """Set up the status bar."""
        self.main_window.setStatusBar(QStatusBar())
        self.main_window.statusBar().showMessage("Ready")