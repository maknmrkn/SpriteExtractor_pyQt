from PyQt6.QtWidgets import QTreeWidgetItem, QTreeWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ..models.tree_item import ThumbnailTreeWidgetItem


class TreeUIManager:
    """
    Manages UI-related tree operations for the main window.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _add_group(self):
        """
        Create a new root-level group in the sprite tree.
        
        The new group is named "New Group", made editable, expanded in the tree view, and a per-group counter entry
        is initialized on self.group_counters using a unique key composed of the group's text and object id (initial value 1).
        """
        item = QTreeWidgetItem(self.main_window.tree_manager.sprite_tree)
        item.setText(0, "New Group")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.main_window.tree_manager.sprite_tree.expandItem(item)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.main_window.group_counters = getattr(self.main_window, 'group_counters', {})
        self.main_window.group_counters[item_id] = 1

    def _add_subgroup(self, parent):
        """
        Add a new editable subgroup item as a child of the given parent tree item and initialize its per-group counter.
        
        Parameters:
            parent (QTreeWidgetItem): The parent tree item under which the new subgroup will be created.
        """
        item = QTreeWidgetItem(parent)
        item.setText(0, "New Subgroup")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.main_window.tree_manager.sprite_tree.expandItem(parent)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.main_window.group_counters = getattr(self.main_window, 'group_counters', {})
        self.main_window.group_counters[item_id] = 1

    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        """
        Create and insert a new sprite item under the given parent group, assigning a unique name.
        
        Parameters:
        	parent: QTreeWidgetItem - The parent group or subgroup to contain the new sprite.
        	x (int, optional): X coordinate of the sprite within the source image (informational).
        	y (int, optional): Y coordinate of the sprite within the source image (informational).
        	width (int, optional): Width of the sprite (informational).
        	height (int, optional): Height of the sprite (informational).
        	pixmap (QPixmap or None, optional): Optional thumbnail image to attach to the new sprite item.
        
        Returns:
        	ThumbnailTreeWidgetItem: The newly created and editable tree item; its display name is generated using the parent group's name and a per-group counter, and the thumbnail is set if `pixmap` is provided.
        """
        print(f"DEBUG: _add_sprite_item called for parent '{parent.text(0)}' with ({x}, {y}, {width}x{height})")
        # Get or initialize counter for this parent group
        parent_id = f"{parent.text(0)}_{id(parent)}"
        self.main_window.group_counters = getattr(self.main_window, 'group_counters', {})
        if parent_id not in self.main_window.group_counters:
            # Initialize counter for this parent group
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
        """
        Handle keyboard interactions for the sprite tree.
        
        Pressing Delete prompts to delete the currently selected tree item with confirmation. Other keys are forwarded to the tree widget's default keyPressEvent handler.
        """
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.main_window.tree_manager.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.main_window.tree_manager._delete_item_with_confirmation(item)
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.main_window.tree_manager.sprite_tree, event)

    def _on_tree_item_clicked(self, item, _column):
        """
        Update the animation preview and the X/Y/Width/Height property labels based on the clicked tree item.
        
        If a group item is clicked (has children or is a top-level item), populate the animation preview with all sprite pixmaps under that group. If a sprite item is clicked, clear the preview and, when the item stores rectangle coordinates in its UserRole as a (x, y, width, height) tuple, set the X/Y/Width/Height labels to those values; otherwise reset the property display.
        
        Parameters:
            item: The clicked QTreeWidgetItem in the sprite tree.
            column: The column index that was clicked.
        """
        print(f"DEBUG: _on_tree_item_clicked called for item '{item.text(0)}'")
        # Check if the clicked item is a group (has children or is a top-level item)
        if item.childCount() > 0 or item.parent() is None:
            # This is a group - collect all sprite items under it for animation
            sprite_pixmaps = []
            self.main_window.tree_manager._collect_sprite_pixmaps(item, sprite_pixmaps)
            
            # Set the collected sprites to the animation preview
            self.main_window.animation_preview.set_sprites(sprite_pixmaps)
        else:
            # This is a sprite item - reset the animation preview
            self.main_window.animation_preview.set_sprites([])
            
            # Extract coordinates from the text if it contains coordinate info
            item.text(0)
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
            self._reset_properties_display()

    def _collect_sprite_pixmaps(self, item, sprite_list):
        """
        Collect all sprite QPixmap objects from a tree item and its descendants into the provided list.
        
        This traverses the given tree item and its children recursively. If an item exposes `get_original_pixmap()` and it returns a non-null QPixmap, that pixmap is appended to `sprite_list`.
        
        Parameters:
            item (QTreeWidgetItem): The root tree item to traverse.
            sprite_list (list): A list that will be extended in place with found `QPixmap` objects.
        """
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
        """
        Clear the sprite property display to indicate that no sprite is selected.
        
        Sets the X, Y, Width, and Height property labels to "-" so the UI shows an empty selection state.
        """
        self.main_window.x_label.setText("-")
        self.main_window.y_label.setText("-")
        self.main_window.y_label.setText("-")
        self.main_window.width_label.setText("-")
        self.main_window.height_label.setText("-")

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