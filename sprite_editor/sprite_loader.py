from PyQt6.QtGui import QPixmap
import os

SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']


class SpriteLoader:
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in SUPPORTED_FORMATS

    @staticmethod
    def load_pixmap(file_path: str) -> QPixmap:
        """Load QPixmap from file path."""
        if not os.path.isfile(file_path):
            return QPixmap()
        
        if not SpriteLoader.is_supported(file_path):
            return QPixmap()
        
        return QPixmap(file_path)

    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """Return metadata about the image."""
        pixmap = SpriteLoader.load_pixmap(file_path)
        if pixmap.isNull():
            return {}
        
        return {
            'width': pixmap.width(),
            'height': pixmap.height(),
            'format': os.path.splitext(file_path)[1].upper()[1:],
            'path': file_path
        }