from ..controllers.tree_context_menu import TreeContextMenu



class TreeContextManager:
    """
    Manages tree context menu functionality for the main window.
    """
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window
        self.context_menu = TreeContextMenu(tree_manager)

    def _show_tree_context_menu(self, position):
        """
        Show the tree's context menu at the given position.
        
        Parameters:
            position (QPoint): Position, in the tree widget's coordinate space, where the context menu should appear.
        """
        self.context_menu._show_tree_context_menu(position)
    
    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """
        Show the context menu for a grid cell at the specified canvas coordinates and size.
        
        Parameters:
            x (int): X coordinate of the cell's top-left corner in canvas pixels.
            y (int): Y coordinate of the cell's top-left corner in canvas pixels.
            width (int): Width of the cell in pixels.
            height (int): Height of the cell in pixels.
        """
        self.context_menu._on_grid_cell_right_clicked(x, y, width, height)
    
    def _on_multi_grid_selection(self, selected_rects):
        """
        Process multiple selected grid rectangles and add the corresponding sprites to groups.
        
        Parameters:
            selected_rects (iterable): An iterable of rectangles representing selections. Each rectangle should be a tuple (x, y, width, height) or an equivalent object describing the selected area.
        """
        # This method now handles adding multiple selected sprites to groups
        self.context_menu._on_multi_grid_selection(selected_rects)