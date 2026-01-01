from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QPainter


class ThumbnailWidget(QScrollArea):
    """Widget to display thumbnails of sprites in a grid layout"""
    
    # Signal emitted when a thumbnail is clicked
    thumbnail_clicked = pyqtSignal(object)  # passes the sprite item
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main container widget
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        
        # Grid layout for thumbnails
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Store references to thumbnail labels
        self.thumbnail_labels = []
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFrameStyle(QFrame.Shadow.Sunken)
        
    def clear_thumbnails(self):
        """Clear all thumbnails from the grid"""
        for label in self.thumbnail_labels:
            label.setParent(None)
        self.thumbnail_labels = []
        # Clear the layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def add_thumbnail(self, pixmap, item_data):
        """Add a thumbnail to the grid"""
        # Create label for thumbnail
        label = QLabel()
        label.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Scale the pixmap to a thumbnail size
        scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        
        # Set a fixed size to ensure consistent layout
        label.setFixedSize(70, 70)
        
        # Store the item data in the label
        label.setProperty("item_data", item_data)
        
        # Connect click event
        label.mousePressEvent = lambda event, l=label: self._on_thumbnail_clicked(event, l)
        
        # Add to grid layout (arrange in 4 columns)
        row = len(self.thumbnail_labels) // 4
        col = len(self.thumbnail_labels) % 4
        
        self.grid_layout.addWidget(label, row, col)
        self.thumbnail_labels.append(label)
    
    def _on_thumbnail_clicked(self, event, label):
        """Handle thumbnail click event"""
        item_data = label.property("item_data")
        if item_data:
            self.thumbnail_clicked.emit(item_data)
    
    def update_thumbnails(self, sprite_items):
        """Update the thumbnails with the provided sprite items"""
        self.clear_thumbnails()
        for item in sprite_items:
            # Get pixmap from item
            pixmap = self._get_pixmap_from_item(item)
            if pixmap:
                self.add_thumbnail(pixmap, item)
    
    def _get_pixmap_from_item(self, item):
        """Extract pixmap from tree item if it exists"""
        # This method will be called from main_window to extract pixmap
        # Since we can't directly access the pixmap from the tree item,
        # we'll need to store the pixmap when the item is created
        if hasattr(item, 'pixmap'):
            return item.pixmap
        return None