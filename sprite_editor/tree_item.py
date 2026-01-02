from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt


class ThumbnailTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent=None, text="", pixmap=None):
        super().__init__(parent)
        self.setText(0, text)
        self.original_pixmap = pixmap  # Store the original pixmap
        if pixmap:
            self.setIcon(0, QIcon(pixmap))
    
    def set_thumbnail(self, pixmap):
        """Set the thumbnail icon for this item"""
        self.original_pixmap = pixmap
        if pixmap:
            # Scale the pixmap to a small size for the thumbnail
            scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setIcon(0, QIcon(scaled_pixmap))
    
    def get_original_pixmap(self):
        """Get the original pixmap for this item"""
        return self.original_pixmap