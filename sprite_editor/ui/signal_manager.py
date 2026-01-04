"""
مدیریت اتصال signalها و slotها
"""

from PyQt6.QtCore import Qt


class SignalManager:
    """مدیریت اتصال signalهای برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the SignalManager with a reference to the application's main window.
        
        Stores the provided main_window reference and initializes an empty list used to track established signal-slot connections.
        
        Parameters:
            main_window: Reference to the application's main window object whose UI components (canvas, tree_manager, thumbnail_grid, sprite_detector, menus) will be wired by this manager.
        """
        self.main_window = main_window
        self.connections = []
    
    def setup_connections(self):
        """
        Initialize and attach all primary UI signal-slot connections for the main window.
        
        Calls internal helpers to wire canvas, sprite tree, thumbnail grid, sprite detector, and menu signals and records each connection for introspection.
        """
        self._connect_canvas_signals()
        self._connect_tree_signals()
        self._connect_thumbnail_signals()
        self._connect_sprite_detector_signals()
        self._connect_menu_signals()
    
    def _connect_canvas_signals(self):
        """
        Wire available canvas signals to their corresponding handlers and record each connection.
        
        If the main window has no `canvas` attribute, this method returns without action. When present, it performs the following observable connections and appends a tuple of (signal_name, handler_name) to `self.connections` for each successful connection:
        - Connects `canvas.grid_cell_clicked` to `self._on_grid_cell_clicked`.
        - Connects `canvas.grid_cell_right_clicked` to `main_window.tree_manager._on_grid_cell_right_clicked`.
        - Connects `canvas.multi_grid_selection` to `main_window.tree_manager._on_multi_grid_selection`.
        """
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
        """
        Wire the sprite tree's Qt signals to the tree manager's handlers and install a custom key press handler.
        
        Sets the sprite tree's context menu policy to CustomContextMenu, connects customContextMenuRequested, itemClicked, and itemDoubleClicked signals to the corresponding tree_manager methods, records those connections in self.connections, and replaces the sprite tree's keyPressEvent with a handler produced by _create_tree_key_press_handler.
        """
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
        """
        Wire the thumbnail grid's click signal to the main window's thumbnail handler.
        
        If the main window exposes a `thumbnail_grid` object that has a `thumbnail_clicked`
        signal, connect that signal to `main_window._on_thumbnail_clicked` and record
        the connection in `self.connections`.
        """
        if hasattr(self.main_window, 'thumbnail_grid'):
            thumbnail_grid = self.main_window.thumbnail_grid
            
            if hasattr(thumbnail_grid, 'thumbnail_clicked'):
                thumbnail_grid.thumbnail_clicked.connect(
                    self.main_window._on_thumbnail_clicked
                )
                self.connections.append(('thumbnail_grid.thumbnail_clicked',
                                       '_on_thumbnail_clicked'))
    
    def _connect_sprite_detector_signals(self):
        """
        Connects the sprite detector's finished signal to the main window's detection handler and records the connection.
        
        If the main window has a `sprite_detector` with a `finished` signal, connects that signal to `main_window._on_detection_finished` and appends a descriptive tuple to `self.connections`.
        """
        if hasattr(self.main_window, 'sprite_detector'):
            sprite_detector = self.main_window.sprite_detector
            
            if hasattr(sprite_detector, 'finished'):
                sprite_detector.finished.connect(
                    self.main_window._on_detection_finished
                )
                self.connections.append(('sprite_detector.finished',
                                       '_on_detection_finished'))
    
    def _connect_menu_signals(self):
        """
        Set up signal connections for application menus.
        
        This placeholder wires menu action signals to their corresponding handlers when implemented; currently no connections are created and subclasses or callers should add menu-specific wiring as needed.
        """
        # اگر نیاز به اتصال signalهای خاص منوها باشد
        pass
    
    def _create_tree_key_press_handler(self, original_handler, tree_manager):
        """
        Create a key press event handler for the tree that forwards events to the tree manager.
        
        Parameters:
            original_handler (callable): The original tree widget keyPressEvent handler (kept for reference; not invoked).
            tree_manager: Object that provides `_on_tree_key_press(event)` to handle key events.
        
        Returns:
            callable: A function that accepts a key event and forwards it to `tree_manager._on_tree_key_press`.
        """
        def key_press_handler(event):
            """
            Forward a key press event to the tree manager's key press handler.
            
            Parameters:
                event (QKeyEvent): The key event to forward.
            """
            tree_manager._on_tree_key_press(event)
        
        return key_press_handler
    
    # ====== Slot Methods ======
    
    def _on_grid_cell_clicked(self, x, y, width, height):
        """
        Log coordinates and size of a clicked grid cell.
        
        Parameters:
            x (int): Column index of the clicked cell.
            y (int): Row index of the clicked cell.
            width (int): Width of the clicked cell (pixels).
            height (int): Height of the clicked cell (pixels).
        """
        # فقط لاگ می‌کنیم، منطق اصلی در canvas انجام می‌شود
        print(f"Grid cell clicked: ({x}, {y}, {width}x{height})")
    
    def disconnect_all(self):
        """
        Disconnects all signal-slot connections tracked by this manager.
        
        This is a placeholder implementation; when implemented it should remove or disconnect every connection recorded in self.connections. Currently it performs no action.
        """
        # در صورت نیاز می‌توان تمام اتصالات را قطع کرد
        pass
    
    def get_connections_info(self):
        """
        Return a shallow copy of the recorded signal-to-slot connection entries.
        
        Each entry is a tuple (signal_name, slot_name).
        
        Returns:
            list[tuple[str, str]]: A copy of the connections list.
        """
        return self.connections.copy()