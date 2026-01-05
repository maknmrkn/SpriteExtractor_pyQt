from PyQt6.QtCore import Qt


class TreeEventHandler:
    """
    Manages tree event handling functionality for the main window.
    """
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window

    def get_selected_sprite_items(self):
        """
        Return the selected sprite items from the tree, excluding group items.
        
        Returns:
            list[QTreeWidgetItem]: List of selected tree items that represent individual sprites.
        """
        selected_items = self.tree_manager.sprite_tree.selectedItems()
        sprite_items = []
        
        for item in selected_items:
            if not self.tree_manager._is_group_item(item):
                sprite_items.append(item)
        
        return sprite_items

    def get_selected_group_items(self):
        """
        Retrieve the currently selected group items from the sprite tree.
        
        Only items that are recognized as groups are included; non-group selected items are ignored.
        
        Returns:
            list[QTreeWidgetItem]: List of selected group items.
        """
        selected_items = self.tree_manager.sprite_tree.selectedItems()
        group_items = []
        
        for item in selected_items:
            if self.tree_manager._is_group_item(item):
                group_items.append(item)
        
        return group_items

    def update_sprite_item(self, item, new_boundary):
        """
        Update the given sprite tree item to reflect a new rectangular boundary and notify listeners.
        
        Parameters:
            item (QTreeWidgetItem): The sprite item to update; ignored if falsy or a group item.
            new_boundary (QRect): Rectangle providing x, y, width, and height to store on the item.
        
        Notes:
            - Stores the boundary as a tuple (x, y, width, height) in the item's UserRole data.
            - Updates the item's size text in the second column to "width×height".
            - Emits the `sprite_edited` signal with the updated item.
        """
        if not item or self.tree_manager._is_group_item(item):
            return
        
        # Update stored coordinates
        item.setData(0, Qt.ItemDataRole.UserRole, 
                    (new_boundary.x(), new_boundary.y(), 
                     new_boundary.width(), new_boundary.height()))
        
        # Update size display
        item.setText(1, f"{new_boundary.width()}×{new_boundary.height()}")
        
        # Emit signal
        self.tree_manager.sprite_edited.emit(item)

    # Tree event handlers
    def _on_tree_item_clicked(self, item, column):
        """
        Handle a click on a tree item, forward it to the main window, and update the canvas selection for sprite items when appropriate.
        
        If the main window defines `_on_tree_item_clicked`, forwards the event to it. If the clicked item is a sprite (not a group) and its UserRole contains a `(x, y, w, h)` tuple, then when the main window's canvas is in autodetect mode this clears the canvas selection, attempts to locate the corresponding rectangle on the canvas, adds it to the canvas selection if found, and requests a canvas display update. Exceptions raised while updating the canvas selection are caught and printed.
        
        Parameters:
            item (QTreeWidgetItem): The clicked tree item.
            column (int): The column index that was clicked.
        """
        # Update properties panel in main window
        if hasattr(self.main_window, '_on_tree_item_clicked'):
            self.main_window._on_tree_item_clicked(item, column)
        
        # If it's a sprite item, update the canvas selection
        if not self.tree_manager._is_group_item(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple) and len(data) == 4:
                x, y, w, h = data
                # Select this sprite in canvas (if in auto-detect mode)
                try:
                    if (hasattr(self.main_window, 'canvas') and 
                        hasattr(self.main_window.canvas, 'in_autodetect_mode') and 
                        self.main_window.canvas.in_autodetect_mode):
                        self.main_window.canvas.selected_cells = []
                        found_rect = self.tree_manager._find_sprite_rect_in_canvas(x, y, w, h)
                        if found_rect:
                            self.main_window.canvas.selected_cells.append(found_rect)
                            self.main_window.canvas.update_display()
                except Exception as e:
                    print(f"Error selecting sprite in canvas: {e}")

    def _on_tree_item_double_clicked(self, item):
        """
        Open the sprite editor for a double-clicked tree item.
        
        If the provided item represents a sprite (not a group), opens the sprite editor for that item; group items are ignored.
        
        Parameters:
            item (QTreeWidgetItem): The tree item that was double-clicked.
        """
        if not self.tree_manager._is_group_item(item):
            self.tree_manager._edit_sprite_item(item)

    def _on_tree_key_press(self, event):
        """
        Handle keyboard shortcuts and special keys for the sprite tree.
        
        Processes Delete to remove the first selected item with confirmation, F2 to rename the first selected item, and Ctrl+E to open the editor for the first selected sprite (ignoring group items). All other key events are forwarded to the tree's default keyPressEvent.
        
        Parameters:
            event (QKeyEvent): The key event received by the tree widget.
        """
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.tree_manager._delete_item_with_confirmation(item)
        elif event.key() == Qt.Key.Key_F2:
            selected_items = self.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.tree_manager._rename_item(item)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            selected_items = self.sprite_tree.selectedItems()
            if selected_items and not self.tree_manager._is_group_item(selected_items[0]):
                self.tree_manager._edit_sprite_item(selected_items[0])
        else:
            # Call the original keyPressEvent for other keys
            self.sprite_tree.keyPressEvent_original(event)