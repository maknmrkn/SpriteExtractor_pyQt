from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox


class SpriteOperations:
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window
        self.current_editing_item = None

    @property
    def sprite_tree(self):
        return self.tree_manager.sprite_tree

    def _get_all_groups(self):
        """Get all group items in the tree."""
        groups = []
        
        # Get top-level items (root groups)
        for i in range(self.sprite_tree.topLevelItemCount()):
            item = self.sprite_tree.topLevelItem(i)
            # Check if it's a group (has children or would be a top-level item)
            if self.tree_manager._is_group_item(item):
                groups.append(item)
        
        # Recursively get subgroups
        def find_subgroups(parent_item):
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
        """Add a sprite to the specified group with coordinates."""
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
        """Add multiple sprites to the specified group."""
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
        """Create a new group and add sprite with coordinates."""
        # Create a new root group
        new_group = self.tree_manager._add_group()
        
        # Add the sprite to this group
        self._add_sprite_to_group(new_group, x, y, width, height)

    def _create_sprites_with_coords(self, selected_rects):
        """Create a new group and add multiple sprites with coordinates."""
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
        """Edit sprite at given coordinates."""
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
        """Edit a sprite item in the tree."""
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
        """Highlight and show sprite in canvas."""
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