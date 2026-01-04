class SignalManager:
    """
    Manages the signal connections for the main window.
    """
    def __init__(self, main_window):
        """
        Initialize the signal manager with a reference to the main window.
        
        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self._connect_signals()

    def _connect_signals(self):
        """Connect all signals to their respective slots."""
        # Connect to the grid cell clicked signal (for highlighting)
        self.main_window.canvas.grid_cell_clicked.connect(self.main_window._on_grid_cell_clicked)
        # Connect to the grid cell right-clicked signal (for moving to group)
        self.main_window.canvas.grid_cell_right_clicked.connect(self.main_window.tree_manager._on_grid_cell_right_clicked)
        # Connect to the multi-grid selection signal
        self.main_window.canvas.multi_grid_selection.connect(self.main_window.tree_manager._on_multi_grid_selection)
        # Connect thumbnail clicked signal
        self.main_window.thumbnail_grid.thumbnail_clicked.connect(self.main_window._on_thumbnail_clicked)