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
        self.main_window = main_window
        self.widgets = {}
        
    def initialize_widgets(self):
        """ایجاد و مقداردهی اولیه تمام ویجت‌های اصلی"""
        self._create_canvas()
        self._create_animation_preview()
        self._create_thumbnail_grid()
        self._create_tree_manager()
        self._create_sprite_detector()
        self._create_property_labels()
        
        return self.widgets
    
    def _create_canvas(self):
        """ایجاد و تنظیم canvas"""
        canvas = Canvas(self.main_window)
        canvas.setSizePolicy(canvas.sizePolicy().Policy.Expanding, 
                           canvas.sizePolicy().Policy.Expanding)
        self.widgets['canvas'] = canvas
    
    def _create_animation_preview(self):
        """ایجاد و تنظیم animation preview"""
        preview = AnimationPreviewWidget()
        self.widgets['animation_preview'] = preview
    
    def _create_thumbnail_grid(self):
        """ایجاد و تنظیم thumbnail grid"""
        thumbnail_grid = ThumbnailWidget()
        self.widgets['thumbnail_grid'] = thumbnail_grid
    
    def _create_tree_manager(self):
        """ایجاد و تنظیم tree manager"""
        tree_manager = TreeManager(self.main_window)
        tree_manager.setup_tree()
        self.widgets['tree_manager'] = tree_manager
        self.widgets['sprite_tree'] = tree_manager.sprite_tree
    
    def _create_sprite_detector(self):
        """ایجاد و تنظیم sprite detector"""
        sprite_detector = SpriteDetector()
        self.widgets['sprite_detector'] = sprite_detector
    
    def _create_property_labels(self):
        """ایجاد labelهای properties"""
        from PyQt6.QtWidgets import QLabel
        
        self.widgets['x_label'] = QLabel("-")
        self.widgets['y_label'] = QLabel("-")
        self.widgets['width_label'] = QLabel("-")
        self.widgets['height_label'] = QLabel("-")