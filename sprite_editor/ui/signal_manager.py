"""
مدیریت اتصال signalها و slotها
"""

from PyQt6.QtCore import Qt


class SignalManager:
    """مدیریت اتصال signalهای برنامه"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.connections = []
    
    def setup_connections(self):
        """اتصال signalهای اصلی برنامه"""
        self._connect_canvas_signals()
        self._connect_tree_signals()
        self._connect_thumbnail_signals()
        self._connect_sprite_detector_signals()
        self._connect_menu_signals()
    
    def _connect_canvas_signals(self):
        """اتصال signalهای canvas"""
        if not hasattr(self.main_window, 'canvas'):
            return
        
        canvas = self.main_window.canvas
        
        # اتصال signalهای انتخاب سلول
        if hasattr(canvas, 'grid_cell_clicked'):
            canvas.grid_cell_clicked.connect(self._on_grid_cell_clicked)
            self.connections.append(('canvas.grid_cell_clicked', '_on_grid_cell_clicked'))
        
        if hasattr(canvas, 'grid_cell_right_clicked'):
            canvas.grid_cell_right_clicked.connect(
                self.main_window.tree_manager._on_grid_cell_right_clicked
            )
            self.connections.append(('canvas.grid_cell_right_clicked', 
                                   'tree_manager._on_grid_cell_right_clicked'))
        
        if hasattr(canvas, 'multi_grid_selection'):
            canvas.multi_grid_selection.connect(
                self.main_window.tree_manager._on_multi_grid_selection
            )
            self.connections.append(('canvas.multi_grid_selection',
                                   'tree_manager._on_multi_grid_selection'))
    
    def _connect_tree_signals(self):
        """اتصال signalهای tree"""
        if not hasattr(self.main_window, 'tree_manager'):
            return
        
        tree_manager = self.main_window.tree_manager
        sprite_tree = tree_manager.sprite_tree
        
        # تنظیم policy برای context menu
        sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # اتصال signalهای tree
        sprite_tree.customContextMenuRequested.connect(
            tree_manager._show_tree_context_menu
        )
        self.connections.append(('sprite_tree.customContextMenuRequested',
                               'tree_manager._show_tree_context_menu'))
        
        sprite_tree.itemClicked.connect(
            tree_manager._on_tree_item_clicked
        )
        self.connections.append(('sprite_tree.itemClicked',
                               'tree_manager._on_tree_item_clicked'))
        
        sprite_tree.itemDoubleClicked.connect(
            tree_manager._on_tree_item_double_clicked
        )
        self.connections.append(('sprite_tree.itemDoubleClicked',
                               'tree_manager._on_tree_item_double_clicked'))
        
        # جایگزینی keyPressEvent
        original_key_press = sprite_tree.keyPressEvent
        sprite_tree.keyPressEvent = self._create_tree_key_press_handler(
            original_key_press, tree_manager
        )
    
    def _connect_thumbnail_signals(self):
        """اتصال signalهای thumbnail grid"""
        if hasattr(self.main_window, 'thumbnail_grid'):
            thumbnail_grid = self.main_window.thumbnail_grid
            
            if hasattr(thumbnail_grid, 'thumbnail_clicked'):
                thumbnail_grid.thumbnail_clicked.connect(
                    self.main_window._on_thumbnail_clicked
                )
                self.connections.append(('thumbnail_grid.thumbnail_clicked',
                                       '_on_thumbnail_clicked'))
    
    def _connect_sprite_detector_signals(self):
        """اتصال signalهای sprite detector"""
        if hasattr(self.main_window, 'sprite_detector'):
            sprite_detector = self.main_window.sprite_detector
            
            if hasattr(sprite_detector, 'finished'):
                sprite_detector.finished.connect(
                    self.main_window._on_detection_finished
                )
                self.connections.append(('sprite_detector.finished',
                                       '_on_detection_finished'))
    
    def _connect_menu_signals(self):
        """اتصال signalهای منوها"""
        # اگر نیاز به اتصال signalهای خاص منوها باشد
        pass
    
    def _create_tree_key_press_handler(self, original_handler, tree_manager):
        """ایجاد handler برای key press events در tree"""
        def key_press_handler(event):
            tree_manager._on_tree_key_press(event)
        
        return key_press_handler
    
    # ====== Slot Methods ======
    
    def _on_grid_cell_clicked(self, x, y, width, height):
        """Handler برای کلیک روی سلول grid"""
        # فقط لاگ می‌کنیم، منطق اصلی در canvas انجام می‌شود
        print(f"Grid cell clicked: ({x}, {y}, {width}x{height})")
    
    def disconnect_all(self):
        """قطع تمام اتصالات"""
        # در صورت نیاز می‌توان تمام اتصالات را قطع کرد
        pass
    
    def get_connections_info(self):
        """دریافت اطلاعات اتصالات"""
        return self.connections.copy()