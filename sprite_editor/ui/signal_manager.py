"""
مدیریت اتصال signalها و slotها
"""

from PyQt6.QtCore import Qt


class SignalManager:
    """مدیریت اتصال signalهای برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the SignalManager with a reference to the main application window and prepare the internal connection registry.
        
        Parameters:
        	main_window: Reference to the application's main window object used to access GUI components (e.g., canvas, tree_manager, thumbnail_grid, sprite_detector) for wiring signal-slot connections.
        
        Attributes:
        	connections (list): Empty list initialized to store recorded connections as tuples (signal_name, slot_name).
        """
        self.main_window = main_window
        self.connections = []
    
    def setup_connections(self):
        """
        Set up the application's primary signal-slot connections for UI components.
        
        Establishes connections for the canvas, tree view, thumbnail grid, sprite detector, and menus by invoking the corresponding connector methods.
        """
        self._connect_canvas_signals()
        self._connect_tree_signals()
        self._connect_thumbnail_signals()
        self._connect_sprite_detector_signals()
        self._connect_menu_signals()
    
    def _connect_canvas_signals(self):
        """
        Set up signal-slot connections for the application's canvas components.
        
        Checks for a canvas on self.main_window; if present, connects available canvas signals to their respective handlers and records each connection in self.connections. Specifically:
        - Connects `grid_cell_clicked` to `self._on_grid_cell_clicked`.
        - Connects `grid_cell_right_clicked` to `self.main_window.tree_manager._on_grid_cell_right_clicked`.
        - Connects `multi_grid_selection` to `self.main_window.tree_manager._on_multi_grid_selection`.
        
        If no canvas is present, the method returns without making connections.
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
        Set up tree-related signal-slot connections and replace the tree widget's keyPressEvent handler.
        
        Configures the tree widget to use a custom context menu policy, connects its context-menu and item click/double-click signals to the tree manager's handlers, and records those connections in self.connections. Also replaces the widget's keyPressEvent with a wrapper that delegates key events to the tree manager.
        
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
        Connect thumbnail grid signals to their handlers on the main window.
        
        If the main window has a `thumbnail_grid` and that grid exposes a
        `thumbnail_clicked` signal, connect it to `main_window._on_thumbnail_clicked`
        and record the connection in `self.connections`.
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
        Connect sprite detector signals to the main window's handlers.
        
        If the main window has a `sprite_detector` with a `finished` signal, connect that signal to
        `main_window._on_detection_finished` and record the connection in `self.connections`.
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
        Register menu-related signals and record their connections.
        
        When menu widgets on the main window expose signals, connect those signals to their handlers
        and append (signal_name, slot_name) pairs to self.connections. Currently implemented as a placeholder
        that performs no connections.
        """
        # اگر نیاز به اتصال signalهای خاص منوها باشد
        pass
    
    def _create_tree_key_press_handler(self, original_handler, tree_manager):
        """
        Create a key press event handler for a tree widget.
        
        Parameters:
            original_handler (callable): The original key press handler (kept for compatibility; not invoked by the wrapper).
            tree_manager (object): Object that implements `_on_tree_key_press(event)` which will receive forwarded key events.
        
        Returns:
            callable: A handler function that forwards key press `event` to `tree_manager._on_tree_key_press`.
        """
        def key_press_handler(event):
            """
            Handle a key press event for the tree view by delegating it to the tree manager.
            
            Parameters:
                event (QEvent | QKeyEvent): The key event received from the tree widget.
            
            Returns:
                The value returned by the tree manager's key press handler.
            """
            tree_manager._on_tree_key_press(event)
        
        return key_press_handler
    
    # ====== Slot Methods ======
    
    def _on_grid_cell_clicked(self, x, y, width, height):
        """
        Handle a click on a canvas grid cell.
        
        Parameters:
            x (int): X-coordinate of the clicked cell.
            y (int): Y-coordinate of the clicked cell.
            width (int): Width of the clicked cell in pixels.
            height (int): Height of the clicked cell in pixels.
        """
        # فقط لاگ می‌کنیم، منطق اصلی در canvas انجام می‌شود
        print(f"Grid cell clicked: ({x}, {y}, {width}x{height})")
    
    def disconnect_all(self):
        """
        Disconnects all signal-slot connections tracked by this SignalManager.
        
        This will remove any established connections and clear the internal connection registry so the manager no longer reports or attempts to manage those connections.
        """
        # در صورت نیاز می‌توان تمام اتصالات را قطع کرد
        pass
    
    def get_connections_info(self):
        """
        Return a shallow copy of the manager's registered signal-slot connections.
        
        Returns:
            list[tuple[str, str]]: List of (signal_name, slot_name) pairs currently recorded in the manager.
        """
        return self.connections.copy()