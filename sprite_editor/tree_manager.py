from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QDialog, QVBoxLayout, QDialogButtonBox, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from .tree_item import ThumbnailTreeWidgetItem


class TreeManager:
    """
    Handles all tree-related operations in the main window
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.group_counters = {}
        
    def setup_tree(self):
        """Initialize the sprite tree widget"""
        self.main_window.sprite_tree = QTreeWidget()
        self.main_window.sprite_tree.setHeaderLabels(["Groups"])
        self.main_window.sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.main_window.sprite_tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.main_window.sprite_tree.itemClicked.connect(self._on_tree_item_clicked)  # Connect to handle item selection
        
        # Add keyboard delete support
        self.main_window.sprite_tree.keyPressEvent = self._on_tree_key_press
    
    def _show_tree_context_menu(self, position):
        """Show context menu for the sprite tree."""
        menu = QMenu()
        
        # Add actions based on selection
        selected_items = self.main_window.sprite_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            
            # Check if the selected item is a group or a sprite
            if self._is_group_item(item):
                # For groups, allow adding subgroups and sprite items
                menu.addAction("Add Subgroup", lambda: self._add_subgroup(item))
                menu.addAction("Add Sprite Item", lambda: self._add_sprite_item(item))
                
                # If we have selected sprites in canvas, allow moving them to this group
                if hasattr(self.main_window.canvas, 'selected_cells') and len(self.main_window.canvas.selected_cells) > 0:
                    menu.addAction("Move Selected Sprites to Group", lambda: self._move_selected_sprites_to_group(item))
                
                menu.addSeparator()
                menu.addAction("Delete", lambda: self._delete_item_with_confirmation(item))
            else:
                # For sprite items, allow renaming and deleting
                menu.addAction("Rename", lambda: self._rename_item(item))
                menu.addAction("Delete", lambda: self._delete_item_with_confirmation(item))
        else:
            # No selection - add root level group
            menu.addAction("Add Group", self._add_group)
        
        menu.exec(self.main_window.sprite_tree.viewport().mapToGlobal(position))

    def _rename_item(self, item):
        """Rename the selected item."""
        # Use the built-in editing capability of QTreeWidget
        self.main_window.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group, coords_list=None):
        """Move selected sprites from canvas to the target group."""
        # Use coords_list if provided, otherwise use canvas selections
        coords_to_process = coords_list if coords_list is not None else [
            (rect.x(), rect.y(), rect.width(), rect.height()) 
            for rect in self.main_window.canvas.selected_cells
        ]
        
        # Process each coordinate tuple
        for x, y, width, height in coords_to_process:
            # Extract the sprite from the canvas
            sprite_pixmap = self.main_window._extract_sprite_pixmap(x, y, width, height)
            
            # Create a sprite item with details and thumbnail
            sprite_item = self._add_sprite_item(target_group, x, y, width, height, sprite_pixmap)
            
            # Store coordinates in the item
            sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
            
            if sprite_pixmap:
                sprite_item.set_thumbnail(sprite_pixmap)
        
        # Clear the canvas selections if we were using them
        if coords_list is None:
            self.main_window.canvas.selected_cells = []
            self.main_window.canvas.update_display()
        
        # Expand the target group to show the new sprites
        self.main_window.sprite_tree.expandItem(target_group)

    def _add_group(self):
        """Add a new root-level group to the tree."""
        item = QTreeWidgetItem(self.main_window.sprite_tree)
        item.setText(0, "New Group")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.main_window.sprite_tree.expandItem(item)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[item_id] = 1

    def _add_subgroup(self, parent):
        """Add a subgroup under the selected parent."""
        item = QTreeWidgetItem(parent)
        item.setText(0, "New Subgroup")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.main_window.sprite_tree.expandItem(parent)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[item_id] = 1

    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        """Add a sprite item under the selected parent."""
        print(f"DEBUG: _add_sprite_item called for parent '{parent.text(0)}' with ({x}, {y}, {width}x{height})")
        # Get or initialize counter for this parent group
        parent_id = f"{parent.text(0)}_{id(parent)}"
        self.group_counters = getattr(self, 'group_counters', {})
        if parent_id not in self.group_counters:
            # Initialize counter for this parent group
            self.group_counters[parent_id] = 1
        
        # Create the sprite name with parent group name and counter
        parent_name = parent.text(0)
        sprite_name = f"{parent_name} {self.group_counters[parent_id]}"
        self.group_counters[parent_id] += 1  # Increment for next sprite
        
        item = ThumbnailTreeWidgetItem(parent, sprite_name, pixmap)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        if pixmap:
            item.set_thumbnail(pixmap)
        return item

    def _on_tree_key_press(self, event):
        """Handle key press events in the tree widget."""
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.main_window.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self._delete_item_with_confirmation(item)
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.main_window.sprite_tree, event)

    def _delete_item_with_confirmation(self, item):
        """Delete the selected item from the tree with confirmation for groups."""
        # Check if it's a group (has children or is a top-level item)
        is_group = self._is_group_item(item)
        
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
        self._delete_item(item)

    def _delete_item(self, item):
        """Delete the selected item from the tree."""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            # Also remove any counter associated with this item
            item_id = f"{item.text(0)}_{id(item)}"
            if hasattr(self, 'group_counters') and item_id in self.group_counters:
                del self.group_counters[item_id]
        else:
            # Root item
            index = self.main_window.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.main_window.sprite_tree.takeTopLevelItem(index)
                # Also remove any counter associated with this item
                item_id = f"{item.text(0)}_{id(item)}"
                if hasattr(self, 'group_counters') and item_id in self.group_counters:
                    del self.group_counters[item_id]

    def _on_tree_item_clicked(self, item, column):
        """Handle when a tree item is clicked"""
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
            text = item.text(0)
            # If the item was created from grid selection, it might have coordinates in its data
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
            self.main_window._reset_properties_display()

    def _collect_sprite_pixmaps(self, item, sprite_list):
        """Recursively collect all sprite pixmaps from a tree item and its children"""
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
        """Reset the properties display"""
        self.main_window.x_label.setText("-")
        self.main_window.y_label.setText("-")
        self.main_window.width_label.setText("-")
        self.main_window.height_label.setText("-")

    def _is_group_item(self, item):
        """Check if an item is a group (not a sprite)"""
        text = item.text(0)
        print(f"DEBUG: _is_group_item checking: {text}")
        
        # Check if this item is a sprite by checking if it follows the naming pattern:
        # parent_name + space + number (e.g., "Sprite Sheet 1")
        parent_item = item.parent()
        if parent_item:
            parent_text = parent_item.text(0)
            # Check if text starts with parent name followed by a space and number
            if text.startswith(parent_text + " "):
                # Verify that after the parent name and space, there's a number
                remaining_text = text[len(parent_text)+1:]
                if remaining_text and remaining_text[0].isdigit():
                    print(f"DEBUG: Item {text} is a sprite (matches parent + number pattern)")
                    return False
        
        # If it's not a sprite, it's a group
        print(f"DEBUG: Item {text} is a group")
        return True

    def _show_group_selection_dialog(self, x, y, width, height):
        """Show a dialog with tree view to select a group for the sprite."""
        print(f"DEBUG: _show_group_selection_dialog called with ({x}, {y}, {width}x{height})")
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Select Group for Sprite")
        dialog.resize(300, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create a tree widget for group selection
        group_tree = QTreeWidget()
        group_tree.setHeaderLabel("Groups")
        
        # Copy the structure from the main sprite tree
        self._copy_tree_structure(self.main_window.sprite_tree, group_tree)
        
        layout.addWidget(group_tree)
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self._add_sprite_to_selected_group(group_tree, x, y, width, height, dialog))
        buttons.rejected.connect(dialog.close)  # Cancel button
        
        layout.addWidget(buttons)
        
        dialog.exec()

    def _copy_tree_structure(self, source_tree, target_tree):
        """Copy the tree structure from source to target tree, excluding sprite items."""
        print("DEBUG: _copy_tree_structure called")
        # Clear target tree
        target_tree.clear()
        
        # Copy all items recursively, excluding sprite items
        for i in range(source_tree.topLevelItemCount()):
            item = source_tree.topLevelItem(i)
            # Only copy groups/subgroups, not sprite items
            if self._is_group_item(item):
                print(f"DEBUG: Copying top level item: {item.text(0)}")
                cloned_item = item.clone()
                # Clone only the group structure, excluding sprite items
                self._clone_group_structure(item, cloned_item)
                target_tree.addTopLevelItem(cloned_item)
            else:
                print(f"DEBUG: Skipping top level item (not a group): {item.text(0)}")

    def _clone_group_structure(self, source_item, target_item):
        """Recursively clone only group items, excluding sprite items."""
        print(f"DEBUG: _clone_group_structure called for source: {source_item.text(0)}")
        for i in range(source_item.childCount()):
            child = source_item.child(i)
            # Only clone if it's a group item, not a sprite
            if self._is_group_item(child):
                print(f"DEBUG: Cloning child: {child.text(0)}")
                cloned_child = child.clone()
                target_item.addChild(cloned_child)
                # Recursively clone the group structure
                self._clone_group_structure(child, cloned_child)
            else:
                print(f"DEBUG: Skipping child (not a group): {child.text(0)}")

    def _add_sprite_to_selected_group(self, group_tree, x, y, width, height, dialog):
        """Add sprite to the selected group in the group selection dialog."""
        print(f"DEBUG: _add_sprite_to_selected_group called with ({x}, {y}, {width}x{height})")
        selected_items = group_tree.selectedItems()
        if selected_items:
            # Find the corresponding item in the main tree
            selected_group = selected_items[0]
            main_tree_item = self._find_main_tree_item(selected_group, self.main_window.sprite_tree)
            if main_tree_item:
                # Verify that the selected item is actually a group (not a sprite)
                if self._is_group_item(main_tree_item):
                    # Extract the sprite from the canvas
                    sprite_pixmap = self.main_window._extract_sprite_pixmap(x, y, width, height)
                    
                    # Create a sprite item with details and thumbnail
                    sprite_item = self._add_sprite_item(main_tree_item, x, y, width, height, sprite_pixmap)
                    
                    # Store coordinates in the item
                    sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
                    
                    if sprite_pixmap:
                        sprite_item.set_thumbnail(sprite_pixmap)
                    
                    # Expand the group to show the new sprite
                    self.main_window.sprite_tree.expandItem(main_tree_item)
                    
                    # Close the dialog
                    dialog.accept()
                else:
                    print(f"DEBUG: Selected item {main_tree_item.text(0)} is not a group, ignoring")
                    dialog.close()
        else:
            dialog.close()

    def _find_main_tree_item(self, source_item, main_tree):
        """Find the corresponding item in the main tree based on text and hierarchy."""
        # Get the path from root to the source item
        path = []
        current = source_item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()
        
        # Navigate the main tree using the path
        current_main_item = None
        for i in range(main_tree.topLevelItemCount()):
            if main_tree.topLevelItem(i).text(0) == path[0]:
                current_main_item = main_tree.topLevelItem(i)
                break
        
        if not current_main_item and len(path) == 1:  # Looking for root item
            for i in range(main_tree.topLevelItemCount()):
                if main_tree.topLevelItem(i).text(0) == path[0]:
                    return main_tree.topLevelItem(i)
        
        # Navigate down the tree to find the matching item
        for i in range(1, len(path)):
            found = False
            for j in range(current_main_item.childCount()):
                child = current_main_item.child(j)
                if child.text(0) == path[i]:
                    current_main_item = child
                    found = True
                    break
            if not found:
                return None
        
        return current_main_item

    def _add_default_sprites_group(self):
        """Add a default group with individual sprite items when an image is loaded."""
        # Clear previous items
        self.main_window.sprite_tree.clear()
        
        # Add a default group
        group_item = QTreeWidgetItem(self.main_window.sprite_tree)
        group_item.setText(0, "Sprite Sheet")
        group_item.setFlags(group_item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Initialize counter for this group using the item's unique text and memory address
        group_item_id = f"{group_item.text(0)}_{id(group_item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[group_item_id] = 1
        
        # Do not add default sprite items, just the group
        self.main_window.sprite_tree.expandItem(group_item)

    def _on_multi_grid_selection(self, coords_list):
        """Handle multi-grid selection right-click."""
        print(f"DEBUG: Multi-grid selection with {len(coords_list)} sprites selected")
        
        # Show a context menu when right-clicking on multi-selected sprites
        menu = QMenu()
        menu.addAction("Move Selected Sprites to Group", lambda: self._show_group_selection_for_multi_sprites(coords_list))
        menu.exec(QCursor.pos())

    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """Handle grid cell right-click and show group selection dialog."""
        print(f"DEBUG: _on_grid_cell_right_clicked called with ({x}, {y}, {width}x{height})")
        # Show dialog to select a group for the sprite
        self._show_group_selection_dialog(x, y, width, height)
        
    def _show_group_selection_for_multi_sprites(self, coords_list):
        """Show group selection dialog for multiple sprites."""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Select Group for Sprites")
        dialog.resize(300, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create a tree widget for group selection
        group_tree = QTreeWidget()
        group_tree.setHeaderLabel("Groups")
        
        # Copy the structure from the main sprite tree
        self._copy_tree_structure(self.main_window.sprite_tree, group_tree)
        
        layout.addWidget(group_tree)
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self._add_multi_sprites_to_selected_group(group_tree, coords_list, dialog))
        buttons.rejected.connect(dialog.close)  # Cancel button
        
        layout.addWidget(buttons)
        
        dialog.exec()

    def _add_multi_sprites_to_selected_group(self, group_tree, coords_list, dialog):
        """Add multiple sprites to the selected group."""
        selected_items = group_tree.selectedItems()
        if selected_items:
            # Find the corresponding item in the main tree
            selected_group = selected_items[0]
            main_tree_item = self._find_main_tree_item(selected_group, self.main_window.sprite_tree)
            if main_tree_item and self._is_group_item(main_tree_item):
                # Process each coordinate tuple
                for x, y, width, height in coords_list:
                    # Extract the sprite from the canvas
                    sprite_pixmap = self.main_window._extract_sprite_pixmap(x, y, width, height)
                    
                    # Create a sprite item with details and thumbnail
                    sprite_item = self._add_sprite_item(main_tree_item, x, y, width, height, sprite_pixmap)
                    
                    # Store coordinates in the item
                    sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
                    
                    if sprite_pixmap:
                        sprite_item.set_thumbnail(sprite_pixmap)
                
                # Expand the group to show the new sprites
                self.main_window.sprite_tree.expandItem(main_tree_item)
                
                # Clear the canvas selections
                self.main_window.canvas.selected_cells = []
                self.main_window.canvas.update_display()
                
                # Close the dialog
                dialog.accept()
        else:
            dialog.close()