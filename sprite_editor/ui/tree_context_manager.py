from PyQt6.QtWidgets import QMenu, QTreeWidgetItem, QMessageBox


class TreeContextManager:
    """
    Manages context menu and tree operations for the main window.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _show_tree_context_menu(self, position):
        """
        Display a context menu for the sprite tree at the given viewport position.
        
        The menu contents depend on the current tree selection:
        - If a group is selected: options to add a subgroup, add a sprite item, move selected canvas sprites into the group (if any), and delete the group.
        - If a sprite item is selected: options to rename or delete the sprite.
        - If nothing is selected: option to add a new root-level group.
        
        Parameters:
            position (QPoint): Position in the sprite tree's viewport coordinates where the context menu should appear.
        """
        menu = QMenu()
        
        # Add actions based on selection
        selected_items = self.main_window.tree_manager.sprite_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            
            # Check if the selected item is a group or a sprite
            if self.main_window.tree_manager._is_group_item(item):
                # For groups, allow adding subgroups and sprite items
                menu.addAction("Add Subgroup", lambda: self.main_window.tree_manager._add_subgroup(item))
                menu.addAction("Add Sprite Item", lambda: self.main_window.tree_manager._add_sprite_item(item))
                
                # If we have selected sprites in canvas, allow moving them to this group
                if hasattr(self.main_window.canvas, 'selected_cells') and len(self.main_window.canvas.selected_cells) > 0:
                    menu.addAction("Move Selected Sprites to Group", lambda: self.main_window.tree_manager._move_selected_sprites_to_group(item))
                
                menu.addSeparator()
                menu.addAction("Delete", lambda: self.main_window.tree_manager._delete_item(item))
            else:
                # For sprite items, allow renaming and deleting
                menu.addAction("Rename", lambda: self.main_window.tree_manager._rename_item(item))
                menu.addAction("Delete", lambda: self.main_window.tree_manager._delete_item(item))
        else:
            # No selection - add root level group
            menu.addAction("Add Group", self.main_window.tree_manager._add_group)
        
        menu.exec(self.main_window.tree_manager.sprite_tree.viewport().mapToGlobal(position))

    def _rename_item(self, item):
        """
        Enter in-place edit mode for the given tree item in the sprite tree.
        
        Parameters:
            item (QTreeWidgetItem): The tree item whose text should be edited.
        """
        # Use the built-in editing capability of QTreeWidget
        self.main_window.tree_manager.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group):
        """
        Move each selected canvas rectangle into the given sprite group as a new sprite item.
        
        For each selected rectangle, create a sprite item under target_group, store the rectangle coordinates on the item using the UserRole, set the cropped pixmap as the item's thumbnail when available, clear the canvas selection, refresh the canvas display, and expand target_group in the tree.
        
        Parameters:
            target_group (QTreeWidgetItem): The group item in the sprite tree that will receive the new sprite items.
        """
        # Process each selected cell in the canvas
        for rect in self.main_window.canvas.selected_cells:
            # Extract coordinates from the rectangle
            x = rect.x()
            y = rect.y()
            width = rect.width()
            height = rect.height()
            
            # Extract the sprite from the canvas
            sprite_pixmap = self._extract_sprite_pixmap(x, y, width, height)
            
            # Create a sprite item with details and thumbnail
            sprite_item = self.main_window.tree_manager._add_sprite_item(target_group, x, y, width, height, sprite_pixmap)
            
            # Store coordinates in the item
            sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
            
            if sprite_pixmap:
                sprite_item.set_thumbnail(sprite_pixmap)
        
        # Clear the canvas selections
        self.main_window.canvas.selected_cells = []
        self.main_window.canvas.update_display()
        
        # Expand the target group to show the new sprites
        self.main_window.tree_manager.sprite_tree.expandItem(target_group)

    def _delete_item_with_confirmation(self, item):
        """
        Prompt the user for confirmation when necessary and delete the specified tree item.
        
        If the item is a group, a confirmation dialog is shown. If the group has children, the prompt specifies that all contents will be deleted. If the user confirms, the item is removed; otherwise no action is taken.
        
        Parameters:
            item (QTreeWidgetItem): The tree item (group or sprite) to delete.
        """
        # Check if it's a group (has children or is a top-level item)
        is_group = self.main_window.tree_manager._is_group_item(item)
        
        if is_group and item.childCount() > 0:
            # Show confirmation dialog for groups with children
            reply = QMessageBox.question(
                self.main_window,
                "Confirm Delete",
                f"Are you sure you want to delete the group '{item.text(0)}' and all its contents?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        elif is_group:
            # Show confirmation dialog for groups without children
            reply = QMessageBox.question(
                self.main_window,
                "Confirm Delete",
                f"Are you sure you want to delete the group '{item.text(0)}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Perform the actual deletion
        self.main_window.tree_manager._delete_item(item)

    def _delete_item(self, item):
        """
        Remove a tree item from the sprite tree and delete its per-group counter if present.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to remove. If the item has a parent it is removed from that parent; otherwise it is removed from the tree's top-level items. If a matching entry exists in self.group_counters (keyed as "<item text>_<id(item)>") that entry is deleted.
        """
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            # Also remove any counter associated with this item
            item_id = f"{item.text(0)}_{id(item)}"
            if hasattr(self.main_window, 'group_counters') and item_id in self.main_window.group_counters:
                del self.main_window.group_counters[item_id]
        else:
            # Root item
            index = self.main_window.tree_manager.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.main_window.tree_manager.sprite_tree.takeTopLevelItem(index)
                # Also remove any counter associated with this item
                item_id = f"{item.text(0)}_{id(item)}"
                if hasattr(self.main_window, 'group_counters') and item_id in self.main_window.group_counters:
                    del self.main_window.group_counters[item_id]

    def _extract_sprite_pixmap(self, x, y, width, height):
        """
        Extract a cropped QPixmap for the specified rectangle from the canvas image.
        
        Parameters:
            x (int): X coordinate of the top-left corner in canvas pixels.
            y (int): Y coordinate of the top-left corner in canvas pixels.
            width (int): Width of the rectangle in pixels.
            height (int): Height of the rectangle in pixels.
        
        Returns:
            QPixmap or None: The cropped pixmap for the given rectangle, or None if the canvas has no loaded image.
        """
        if not self.main_window.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            from PyQt6.QtCore import QRect
            sprite_rect = QRect(x, y, width, height)
            return self.main_window.canvas.pixmap.copy(sprite_rect)
        return None