from PyQt6.QtCore import Qt


class TreeInitManager:
    """
    Manages tree initialization and setup functionality for the main window.
    """
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window
        self.sprite_tree = None

    def setup_tree(self):
        """
        Set up and wire the sprite tree widget for this manager.
        
        Builds the tree via the structure manager, updates the manager's sprite_tree reference, enables a custom context menu, connects handlers for context-menu requests, item clicks, and item double-clicks, and preserves the tree's original keyPressEvent while installing the manager's key handler.
        """
        self.tree_manager.structure_manager.setup_tree()
        # Update the reference after setup
        self.sprite_tree = self.tree_manager.structure_manager.sprite_tree
        
        # Save reference to original keyPressEvent
        self.sprite_tree.keyPressEvent_original = self.sprite_tree.keyPressEvent
        
        # Connect signals
        self.sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sprite_tree.customContextMenuRequested.connect(self.tree_manager.context_manager._show_tree_context_menu)
        self.sprite_tree.itemClicked.connect(self.tree_manager.event_handler._on_tree_item_clicked)
        self.sprite_tree.itemDoubleClicked.connect(self.tree_manager.event_handler._on_tree_item_double_clicked)
        # Save reference to original keyPressEvent
        self.sprite_tree.keyPressEvent_original = self.sprite_tree.keyPressEvent
        self.sprite_tree.keyPressEvent = self.tree_manager.event_handler._on_tree_key_press