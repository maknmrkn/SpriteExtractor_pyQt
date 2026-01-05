from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtCore import Qt
from .tree_ui_manager import TreeUIManager
from .tree_context_manager import TreeContextManager


class TreeContextManager:
    """
    Manages context menu and related operations for the sprite tree.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _show_tree_context_menu(self, position):
        """Display a context menu for the sprite tree at the given viewport position."""
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
        """Enter in-place edit mode for the given tree item."""
        self.main_window.tree_manager.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group):
        """Move each selected canvas rectangle into the given sprite group as a new sprite item."""
        # Process each selected cell in the canvas
        for rect in self.main_window.canvas.selected_cells:
            # Extract coordinates from the rectangle
            x = rect.x()
            y = rect.y()
            width = rect.width()
            height = rect.height()
            
            # Extract the sprite from the canvas
            sprite_pixmap = self.main_window.tree_manager._extract_sprite_pixmap(x, y, width, height)
            
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
        """Prompt the user for confirmation when necessary and delete the specified tree item."""
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
        """Remove a tree item from the sprite tree and delete its per-group counter if present."""
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
class TreeUIManager:
    """
    Manages UI-related operations for the sprite tree.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _add_group(self):
        """Create a new root-level group in the sprite tree."""
        item = self.main_window.tree_manager.sprite_tree.invisibleRootItem()
        child = self._create_group_item("New Group")
        item.addChild(child)
        self.main_window.tree_manager.sprite_tree.expandItem(child)
        return child

    def _add_subgroup(self, parent):
        """Add a new editable subgroup item as a child of the given parent."""
        child = self._create_group_item("New Subgroup")
        parent.addChild(child)
        self.main_window.tree_manager.sprite_tree.expandItem(parent)
        return child

    def _create_group_item(self, name):
        """Create a new group item with the given name."""
        item = self.main_window.tree_manager._create_item(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.main_window.group_counters = getattr(self.main_window, 'group_counters', {})
        self.main_window.group_counters[item_id] = 1
        return item

    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        """Create and insert a new sprite item under the given parent group."""
        from ..models.tree_item import ThumbnailTreeWidgetItem
        
        print(f"DEBUG: _add_sprite_item called for parent '{parent.text(0)}' with ({x}, {y}, {width}x{height})")
        # Get or initialize counter for this parent group
        parent_id = f"{parent.text(0)}_{id(parent)}"
        self.main_window.group_counters = getattr(self.main_window, 'group_counters', {})
        if parent_id not in self.main_window.group_counters:
            self.main_window.group_counters[parent_id] = 1
        
        # Create the sprite name with parent group name and counter
        parent_name = parent.text(0)
        sprite_name = f"{parent_name} {self.main_window.group_counters[parent_id]}"
        self.main_window.group_counters[parent_id] += 1  # Increment for next sprite
        
        item = ThumbnailTreeWidgetItem(parent, sprite_name, pixmap)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        if pixmap:
            item.set_thumbnail(pixmap)
        return item

    def _on_tree_key_press(self, event):
        """Handle keyboard interactions for the sprite tree."""
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.main_window.tree_manager.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.main_window.tree_manager._delete_item_with_confirmation(item)
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.main_window.tree_manager.sprite_tree, event)

    def _on_tree_item_clicked(self, item, _column):
        """Update the animation preview and property labels based on clicked item."""
        print(f"DEBUG: _on_tree_item_clicked called for item '{item.text(0)}'")
        # Check if the clicked item is a group (has children or is a top-level item)
        if item.childCount() > 0 or item.parent() is None:
            # This is a group - collect all sprite items under it for animation
            sprite_pixmaps = []
            self._collect_sprite_pixmaps(item, sprite_pixmaps)
            
            # Set the collected sprites to the animation preview
            self.main_window.animation_preview.set_sprites(sprite_pixmaps)
        else:
            # This is a sprite item - reset the animation preview
            self.main_window.animation_preview.set_sprites([])
            
            # Extract coordinates from the text if it contains coordinate info
            if hasattr(item, 'data') and item.data(0, Qt.ItemDataRole.UserRole) is not None:
                coords = item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(coords, tuple) and len(coords) == 4:
                    x, y, w, h = coords
                    self.main_window.x_label.setText(str(x))
                    self.main_window.y_label.setText(str(y))
                    self.main_window.width_label.setText(str(w))
                    self.main_window.height_label.setText(str(h))
                    return
            
            # Reset if we can't extract coordinates
            self._reset_properties_display()

    def _collect_sprite_pixmaps(self, item, sprite_list):
        """Collect all sprite QPixmap objects from a tree item and its descendants."""
        # Check if this is a ThumbnailTreeWidgetItem with an original pixmap
        if hasattr(item, 'get_original_pixmap'):
            original_pixmap = item.get_original_pixmap()
            if original_pixmap and not original_pixmap.isNull():
                sprite_list.append(original_pixmap)
        
        # Recursively process all children
        for i in range(item.childCount()):
            child = item.child(i)
            self._collect_sprite_pixmaps(child, sprite_list)

    def _reset_properties_display(self):
        """Clear the sprite property display to indicate no selection."""
        self.main_window.x_label.setText("-")
        self.main_window.y_label.setText("-")
        self.main_window.width_label.setText("-")
        self.main_window.height_label.setText("-")

    def _extract_sprite_pixmap(self, x, y, width, height):
        """Extract a cropped QPixmap for the specified rectangle from the canvas image."""
        if not self.main_window.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            from PyQt6.QtCore import QRect
            sprite_rect = QRect(x, y, width, height)
            return self.main_window.canvas.pixmap.copy(sprite_rect)
        return None
class TreeOperationsManager:
    """
    Manages tree operations functionality for the main window.
    Delegates specific responsibilities to specialized manager classes.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.tree_ui_manager = TreeUIManager(main_window)
        self.tree_context_manager = TreeContextManager(main_window)

    def _show_tree_context_menu(self, position):
        """Display a context menu for the sprite tree at the given viewport position."""
        self.tree_context_manager._show_tree_context_menu(position)

    def _rename_item(self, item):
        """Enter in-place edit mode for the given tree item in the sprite tree."""
        self.tree_context_manager._rename_item(item)

    def _move_selected_sprites_to_group(self, target_group):
        """Move each selected canvas rectangle into the given sprite group as a new sprite item."""
        self.tree_context_manager._move_selected_sprites_to_group(target_group)

    def _add_group(self):
        """Create a new root-level group in the sprite tree."""
        return self.tree_ui_manager._add_group()

    def _add_subgroup(self, parent):
        """Add a new editable subgroup item as a child of the given parent tree item."""
        return self.tree_ui_manager._add_subgroup(parent)

    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        """Create and insert a new sprite item under the given parent group."""
        return self.tree_ui_manager._add_sprite_item(parent, x, y, width, height, pixmap)

    def _on_tree_key_press(self, event):
        """Handle keyboard interactions for the sprite tree."""
        self.tree_ui_manager._on_tree_key_press(event)

    def _delete_item_with_confirmation(self, item):
        """Prompt the user for confirmation when necessary and delete the specified tree item."""
        self.tree_context_manager._delete_item_with_confirmation(item)

    def _delete_item(self, item):
        """Remove a tree item from the sprite tree and delete its per-group counter if present."""
        self.tree_context_manager._delete_item(item)

    def _on_tree_item_clicked(self, item, _column):
        """Update the animation preview and the X/Y/Width/Height property labels based on the clicked tree item."""
        self.tree_ui_manager._on_tree_item_clicked(item, _column)

    def _collect_sprite_pixmaps(self, item, sprite_list):
        """Collect all sprite QPixmap objects from a tree item and its descendants into the provided list."""
        self.tree_ui_manager._collect_sprite_pixmaps(item, sprite_list)

    def _reset_properties_display(self):
        """Clear the sprite property display to indicate that no sprite is selected."""
        self.tree_ui_manager._reset_properties_display()

    def _extract_sprite_pixmap(self, x, y, width, height):
        """Extract a cropped QPixmap for the specified rectangle from the canvas image."""
        return self.tree_ui_manager._extract_sprite_pixmap(x, y, width, height)


from .tree_ui_manager import TreeUIManager
from .tree_context_manager import TreeContextManager