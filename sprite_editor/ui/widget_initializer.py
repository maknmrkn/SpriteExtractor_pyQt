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
        Initialize the WidgetInitializer with a reference to the main application window.
        
        Parameters:
            main_window: The main application window used as the parent for created widgets; stored on the instance as `self.main_window`.
        """
        self.main_window = main_window
        self.widgets = {}
        
    def initialize_widgets(self):
        """
        Create and initialize all main application widgets and register them in the instance widget store.
        
        The method constructs the canvas, animation preview, thumbnail grid, tree manager (and its sprite tree), sprite detector, and property labels, storing each under a descriptive key in self.widgets, then returns that dictionary.
        
        Returns:
            dict: Mapping of widget names (e.g., 'canvas', 'animation_preview', 'thumbnail_grid', 'tree_manager', 'sprite_tree', 'sprite_detector', 'x_label', 'y_label', 'width_label', 'height_label') to their created widget instances.
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
        Create and configure the main drawing canvas and store it in the widgets registry.
        
        Creates a Canvas attached to the main window, sets its size policy to expand horizontally and vertically, and stores it under the 'canvas' key in self.widgets.
        """
        canvas = Canvas(self.main_window)
        canvas.setSizePolicy(canvas.sizePolicy().Policy.Expanding, 
                           canvas.sizePolicy().Policy.Expanding)
        self.widgets['canvas'] = canvas
    
    def _create_animation_preview(self):
        """
        Create and register the animation preview widget.
        
        Instantiates an AnimationPreviewWidget and stores it in self.widgets under the key 'animation_preview'.
        """
        preview = AnimationPreviewWidget()
        self.widgets['animation_preview'] = preview
    
    def _create_thumbnail_grid(self):
        """
        Create and register the thumbnail grid widget.
        
        Instantiates a ThumbnailWidget and stores it in self.widgets under the key 'thumbnail_grid'.
        """
        thumbnail_grid = ThumbnailWidget()
        self.widgets['thumbnail_grid'] = thumbnail_grid
    
    def _create_tree_manager(self):
        """
        Create and initialize the tree manager and store it in the widget registry.
        
        Instantiates a TreeManager for the main window, calls its setup_tree() method to initialize the tree structure, and stores the manager under 'tree_manager' and its sprite_tree reference under 'sprite_tree' in self.widgets.
        """
        tree_manager = TreeManager(self.main_window)
        tree_manager.setup_tree()
        self.widgets['tree_manager'] = tree_manager
        self.widgets['sprite_tree'] = tree_manager.sprite_tree
    
    def _create_sprite_detector(self):
        """
        Create and register a SpriteDetector instance.
        
        Instantiates a SpriteDetector and stores it in self.widgets under the key 'sprite_detector'.
        """
        sprite_detector = SpriteDetector()
        self.widgets['sprite_detector'] = sprite_detector
    
    def _create_property_labels(self):
        """
        Create and store four QLabel instances representing sprite property values.
        
        Creates QLabel widgets initialized with "-" and stores them in self.widgets under the keys 'x_label', 'y_label', 'width_label', and 'height_label'.
        """
        from PyQt6.QtWidgets import QLabel
        
        self.widgets['x_label'] = QLabel("-")
        self.widgets['y_label'] = QLabel("-")
        self.widgets['width_label'] = QLabel("-")
        self.widgets['height_label'] = QLabel("-")