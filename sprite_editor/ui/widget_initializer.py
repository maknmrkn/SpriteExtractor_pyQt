"""
مدیریت ایجاد و مقداردهی اولیه ویجت‌های اصلی برنامه
"""

from PyQt6.QtCore import Qt
from ..canvas import Canvas
from ..thumbnail_grid import ThumbnailWidget
from ..animation_preview import AnimationPreviewWidget
from ..tree_manager import TreeManager
from ..sprite_detector import SpriteDetector


class WidgetInitializer:
    """کلاس مسئول ایجاد و مقداردهی اولیه ویجت‌های اصلی"""
    
    def __init__(self, main_window):
        """
        Initialize the WidgetInitializer with the application's main window and prepare the widget storage.
        
        Parameters:
            main_window: The application's main window object used as parent/context when creating widgets.
        """
        self.main_window = main_window
        self.widgets = {}
        
    def initialize_widgets(self):
        """
        Create and initialize all main UI widgets for the application.
        
        Returns:
            widgets (dict): Mapping of widget keys (e.g., 'canvas', 'animation_preview', 'thumbnail_grid',
            'tree_manager', 'sprite_tree', 'sprite_detector', 'x_label', 'y_label', 'width_label', 'height_label')
            to their corresponding widget instances.
        """
        self._create_canvas()
        self._create_animation_preview()
        self._create_thumbnail_grid()
        self._create_tree_manager()
        self._create_sprite_detector()
        self._create_property_labels()
        
        return self.widgets
    
    def _create_canvas(self):
        """
        Create a Canvas widget, configure it to expand in both directions, and store it in self.widgets under the key 'canvas'.
        """
        canvas = Canvas(self.main_window)
        canvas.setSizePolicy(canvas.sizePolicy().Policy.Expanding, 
                           canvas.sizePolicy().Policy.Expanding)
        self.widgets['canvas'] = canvas
    
    def _create_animation_preview(self):
        """
        Create and store the animation preview widget.
        
        Creates an AnimationPreviewWidget instance and places it in self.widgets under the key 'animation_preview'.
        """
        preview = AnimationPreviewWidget()
        self.widgets['animation_preview'] = preview
    
    def _create_thumbnail_grid(self):
        """
        Create and register the thumbnail grid widget.
        
        Creates a ThumbnailWidget instance and stores it in self.widgets under the key 'thumbnail_grid'.
        """
        thumbnail_grid = ThumbnailWidget()
        self.widgets['thumbnail_grid'] = thumbnail_grid
    
    def _create_tree_manager(self):
        """
        Initialize and register the TreeManager and its sprite tree in the widget registry.
        
        Creates a TreeManager bound to the main window, initializes its tree, and stores the manager under 'tree_manager' and its `sprite_tree` under 'sprite_tree' in self.widgets.
        """
        tree_manager = TreeManager(self.main_window)
        tree_manager.setup_tree()
        self.widgets['tree_manager'] = tree_manager
        self.widgets['sprite_tree'] = tree_manager.sprite_tree
    
    def _create_sprite_detector(self):
        """
        Create a SpriteDetector instance and register it in the initializer's widgets dictionary.
        
        The created SpriteDetector is stored under the 'sprite_detector' key in self.widgets.
        """
        sprite_detector = SpriteDetector()
        self.widgets['sprite_detector'] = sprite_detector
    
    def _create_property_labels(self):
        """
        Create QLabel widgets for sprite property display and store them in self.widgets.
        
        Each label is initialized with "-" and stored under the keys 'x_label', 'y_label', 'width_label', and 'height_label'.
        """
        from PyQt6.QtWidgets import QLabel
        
        self.widgets['x_label'] = QLabel("-")
        self.widgets['y_label'] = QLabel("-")
        self.widgets['width_label'] = QLabel("-")
        self.widgets['height_label'] = QLabel("-")