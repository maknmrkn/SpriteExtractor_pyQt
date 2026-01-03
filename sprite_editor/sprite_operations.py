from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class SpriteOperations:
    def __init__(self, tree_manager):
        """
        Initialize the SpriteOperations instance with a tree manager and cache its main window.
        
        Parameters:
            tree_manager: Object responsible for managing the sprite tree and providing access to the application's main window and tree-related helper methods.
        """
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window
        self.current_editing_item = None

    @property
    def sprite_tree(self):
        """
        Access the sprite tree provided by the associated tree manager.
        
        Returns:
            The sprite tree object used to store groups and sprite items.
        """
        return self.tree_manager.sprite_tree

    def _get_all_groups(self):
        """
        Collects all group items from the sprite tree, including top-level groups and nested subgroups.
        
        Returns:
            list: All group items found in the sprite tree (top-level and nested subgroup items).
        """
        groups = []
        
        # Get top-level items (root groups)
        for i in range(self.sprite_tree.topLevelItemCount()):
            item = self.sprite_tree.topLevelItem(i)
            # Check if it's a group (has children or would be a top-level item)
            if self.tree_manager._is_group_item(item):
                groups.append(item)
        
        # Recursively get subgroups
        def find_subgroups(parent_item):
            """
            Recursively traverse parent_item's descendants and append any group items to the enclosing `groups` list.
            
            Parameters:
                parent_item: Tree item whose child hierarchy will be searched for group items.
            """
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                if self.tree_manager._is_group_item(child):
                    groups.append(child)
                find_subgroups(child)
        
        # Check subgroups for each top-level item
        for i in range(self.sprite_tree.topLevelItemCount()):
            item = self.sprite_tree.topLevelItem(i)
            find_subgroups(item)
        
        return groups

    def _add_sprite_to_group(self, group, x, y, width, height):
        """
        Add a sprite item to the given group using the specified canvas coordinates.
        
        Stores the coordinates (x, y, width, height) in the item's UserRole. If a pixmap is extracted from the canvas, sets the item's thumbnail and updates the size column to "width×height". Ensures the target group is expanded.
        
        Parameters:
        	group: The target group/tree item to receive the new sprite.
        	x (int): X coordinate on the canvas (pixels).
        	y (int): Y coordinate on the canvas (pixels).
        	width (int): Sprite width in pixels.
        	height (int): Sprite height in pixels.
        
        Returns:
        	sprite_item: The newly created sprite tree item.
        """
        # Extract the sprite from canvas
        pixmap = self.tree_manager._extract_sprite_from_canvas(x, y, width, height)
        
        # Create sprite item
        sprite_item = self.tree_manager._create_sprite_item(group, x, y, width, height, pixmap)
        
        # Store coordinates in the item
        sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
        
        if pixmap:
            sprite_item.set_thumbnail(pixmap)
            # Update size column
            sprite_item.setText(1, f"{width}×{height}")
        
        # Expand the group
        group.setExpanded(True)
        
        return sprite_item

    def _add_sprites_to_group(self, group, selected_rects):
        """
        Add multiple sprites to the given group from a sequence of rectangle descriptors.
        
        Parameters:
            group: The target group item in the sprite tree to which new sprite items will be added.
            selected_rects: An iterable of rectangle descriptors; each entry may be a QRect-like object
                (providing x(), y(), width(), height()) or a 4-tuple (x, y, width, height).
        """
        for rect in selected_rects:
            # Handle both QRect objects and tuples
            if hasattr(rect, 'x'):
                # QRect object
                x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                # Tuple (x, y, width, height)
                x, y, width, height = rect
            self._add_sprite_to_group(group, x, y, width, height)

    def _create_sprite_with_coords(self, x, y, width, height):
        """
        Create a new root group and add a sprite using the provided canvas coordinates.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner on the canvas (pixels).
            y (int): Y coordinate of the sprite's top-left corner on the canvas (pixels).
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        # Create a new root group
        new_group = self.tree_manager._add_group()
        
        # Add the sprite to this group
        self._add_sprite_to_group(new_group, x, y, width, height)

    def _create_sprites_with_coords(self, selected_rects):
        """
        Create a new root group and add sprites for each provided rectangle.
        
        Parameters:
            selected_rects (iterable): An iterable of rectangles where each element is either a QRect-like object
                (with .x(), .y(), .width(), .height()) or a 4-tuple (x, y, width, height) specifying coordinates
                for a sprite to add to the new group.
        """
        # Create a new root group
        new_group = self.tree_manager._add_group()
        
        # Add each sprite to this group
        for rect in selected_rects:
            # Handle both QRect objects and tuples
            if hasattr(rect, 'x'):
                # QRect object
                x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                # Tuple (x, y, width, height)
                x, y, width, height = rect
            self._add_sprite_to_group(new_group, x, y, width, height)

    def _edit_sprite_at_coords(self, x, y, width, height):
        """
        Open the sprite editor for the sprite located at the specified canvas rectangle.
        
        If a sprite image exists at (x, y, width, height), sets that image into the main window's sprite editor, shows the editor dock, switches the right panel to the editor view, stores the editing coordinates in `current_editing_coords`, and clears `current_editing_item`.
        
        Parameters:
            x (int): X coordinate of the sprite rectangle on the canvas.
            y (int): Y coordinate of the sprite rectangle on the canvas.
            width (int): Width of the sprite rectangle.
            height (int): Height of the sprite rectangle.
        """
        pixmap = self.tree_manager._extract_sprite_from_canvas(x, y, width, height)
        if pixmap and hasattr(self.main_window, 'sprite_editor'):
            boundary = self.tree_manager._find_sprite_rect_in_canvas(x, y, width, height)
            self.main_window.sprite_editor.set_sprite(pixmap, boundary)
            self.main_window.sprite_editor_dock.show()
            self.main_window.right_stacked.setCurrentIndex(1)
            
            # Store current editing context
            self.current_editing_item = None
            self.current_editing_coords = (x, y, width, height)

    def _edit_sprite_item(self, item):
        """
        Open the sprite editor for the given sprite tree item.
        
        If the item provides an original pixmap, that pixmap is loaded into the application's sprite editor. If the item's UserRole data is a 4-tuple (x, y, width, height), that rectangle is converted to a canvas boundary and passed to the editor. The item is recorded as the current editing target; if the editor exists, its dock is shown and the right-hand UI stack is switched to the editor page.
        
        Parameters:
            item: A tree item representing a sprite. The item is expected to expose `get_original_pixmap()` and may store a 4-tuple (x, y, width, height) in UserRole data to indicate the sprite's canvas coordinates.
        """
        if hasattr(item, 'get_original_pixmap'):
            pixmap = item.get_original_pixmap()
            if pixmap and not pixmap.isNull():
                # Get boundary from item data
                boundary = None
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(data, tuple) and len(data) == 4:
                    x, y, w, h = data
                    boundary = self.tree_manager._find_sprite_rect_in_canvas(x, y, w, h)
                
                # Store reference to item being edited
                self.current_editing_item = item
                
                # Set sprite in editor
                if hasattr(self.main_window, 'sprite_editor'):
                    self.main_window.sprite_editor.set_sprite(pixmap, boundary)
                    self.main_window.sprite_editor_dock.show()
                    self.main_window.right_stacked.setCurrentIndex(1)

    def _show_sprite_in_canvas(self, item):
        """
        Highlight the sprite represented by the given tree item and show it in the canvas.
        
        If the item is a sprite (not a group) and contains stored coordinates (x, y, width, height),
        the corresponding sprite rectangle in the canvas is selected and the canvas display is updated.
        If the canvas is not currently in autodetect mode, this will toggle the canvas into autodetect mode.
        
        Parameters:
            item: The tree item representing either a group or a sprite; for sprites it must contain a
                4-tuple `(x, y, width, height)` in its user data to identify the sprite in the canvas.
        """
        if not self.tree_manager._is_group_item(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple) and len(data) == 4:
                x, y, w, h = data
                
                # Find corresponding sprite in canvas
                sprite_rect = self.tree_manager._find_sprite_rect_in_canvas(x, y, w, h)
                if sprite_rect:
                    # Select this sprite in canvas
                    self.main_window.canvas.selected_cells = [sprite_rect]
                    self.main_window.canvas.update_display()
                    
                    # Switch to auto-detect mode if needed
                    if hasattr(self.main_window.canvas, 'in_autodetect_mode') and not self.main_window.canvas.in_autodetect_mode:
                        self.main_window._toggle_mode()

    def _move_selected_sprites_to_group(self, target_group):
        """Move selected sprites from canvas to the target group."""
        if not hasattr(self.main_window.canvas, 'selected_cells'):
            return
        
        # Process each selected cell in the canvas
        for rect in self.main_window.canvas.selected_cells:
            # Handle both QRect objects and tuples
            if hasattr(rect, 'x'):
                # QRect object
                x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
            else:
                # Tuple (x, y, width, height)
                x, y, width, height = rect
            
            # Add sprite to target group
            self._add_sprite_to_group(target_group, x, y, width, height)
        
        # Clear the canvas selections
        self.main_window.canvas.selected_cells = []
        self.main_window.canvas.update_display()
        
        # Expand the target group to show the new sprites
        target_group.setExpanded(True)