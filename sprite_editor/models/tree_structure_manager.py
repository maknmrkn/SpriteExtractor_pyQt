"""
Main module for managing the sprite tree structure.
This class acts as a facade, orchestrating the core tree operations,
context menu, and various logic modules.
"""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QHeaderView, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .tree_item import ThumbnailTreeWidgetItem


class TreeStructureManager:
    def __init__(self, main_window):
        """
        Initialize the TreeStructureManager with a reference to the application's main window.
        
        Parameters:
            main_window: The main application window object used for accessing the canvas, group counters, and any extraction or UI helpers the manager relies on.
        
        Attributes set:
            main_window: Stored reference to the provided main window.
            sprite_tree: Initialized to None; will hold the QTreeWidget instance after setup.
            current_editing_item: Initialized to None; tracks the item currently being edited.
        """
        self.main_window = main_window
        self.sprite_tree = None
        self.current_editing_item = None

    def setup_tree(self):
        """
        Initialize and configure the QTreeWidget used to display sprite groups and items.
        
        Creates and assigns a QTreeWidget to self.sprite_tree, sets header labels to "Name" and "Size", enables extended selection, and configures column count and header resize behavior for proper display of item names and sizes.
        """
        self.sprite_tree = QTreeWidget()
        self.sprite_tree.setHeaderLabel("Sprites")
        self.sprite_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Set header properties
        header = self.sprite_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        # Set column count to 2 for better display
        self.sprite_tree.setColumnCount(2)
        self.sprite_tree.setHeaderLabels(["Name", "Size"])

    def _add_group(self, name=None):
        """
        Create and add a new root-level group item to the sprite tree.
        
        Parameters:
            name (str | None): Optional display name for the new group. If None, defaults to "New Group".
        
        Returns:
            QTreeWidgetItem: The created root group item (editable, expanded, and registered with a per-group counter).
        """
        if name is None:
            name = "New Group"
        
        item = QTreeWidgetItem(self.sprite_tree)
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Set group icon
        icon = self._get_group_icon()
        if icon:
            item.setIcon(0, icon)
        
        # Initialize counter for this group
        group_id = f"{name}_{id(item)}"
        self.main_window.group_counters[group_id] = 1
        
        # Expand the item
        self.sprite_tree.expandItem(item)
        
        return item

    def _add_subgroup(self, parent):
        """
        Create a new editable subgroup item under the given parent group.
        
        Parameters:
        	parent (QTreeWidgetItem): The parent group item under which the subgroup will be created. If the parent is not a group, no item is created.
        
        Returns:
        	QTreeWidgetItem or None: The newly created subgroup item, or `None` if the parent was not a group.
        
        Notes:
        	Initializes a per-group counter entry in main_window.group_counters for the new subgroup.
        """
        if not self._is_group_item(parent):
            return
        
        name = "New Subgroup"
        item = QTreeWidgetItem(parent)
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Set group icon
        icon = self._get_group_icon()
        if icon:
            item.setIcon(0, icon)
        
        # Initialize counter for this group
        group_id = f"{name}_{id(item)}"
        self.main_window.group_counters[group_id] = 1
        
        # Expand parent
        parent.setExpanded(True)
        
        return item

    def _add_sprite_item_to_group(self, parent):
        """
        Create and add a new editable sprite item under the given group using the group's naming counter.
        
        Parameters:
        	parent (QTreeWidgetItem): Group item to receive the new sprite; must be a group (root or has children).
        
        Returns:
        	ThumbnailTreeWidgetItem or None: The newly created sprite item, or `None` if `parent` is not a group.
        """
        if not self._is_group_item(parent):
            return
        
        # Get or initialize counter for this parent group
        parent_id = f"{parent.text(0)}_{id(parent)}"
        if parent_id not in self.main_window.group_counters:
            self.main_window.group_counters[parent_id] = 1
        
        # Create sprite name
        sprite_name = f"{parent.text(0)} {self.main_window.group_counters[parent_id]}"
        self.main_window.group_counters[parent_id] += 1
        
        # Create sprite item
        item = ThumbnailTreeWidgetItem(parent, sprite_name, None)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Expand parent
        parent.setExpanded(True)
        
        return item

    def _create_sprite_item(self, parent, x, y, width, height, pixmap=None):
        """
        Create and add a sprite item as a child of the given parent group.
        
        Parameters:
            parent (QTreeWidgetItem): Parent group/item under which the sprite will be created.
            x (int): X coordinate of the sprite region in the canvas.
            y (int): Y coordinate of the sprite region in the canvas.
            width (int): Width of the sprite region.
            height (int): Height of the sprite region.
            pixmap (QPixmap | None): Optional thumbnail pixmap for the sprite.
        
        Returns:
            ThumbnailTreeWidgetItem: The newly created tree item representing the sprite.
        
        Notes:
            - Stores the tuple (x, y, width, height) in the item's UserRole data.
            - If a pixmap is provided, sets the item's thumbnail and displays the size as "width×height".
            - Increments and/or initializes a per-group counter in main_window.group_counters to generate the sprite name.
        """
        # Get or initialize counter for this parent group
        parent_id = f"{parent.text(0)}_{id(parent)}"
        if parent_id not in self.main_window.group_counters:
            self.main_window.group_counters[parent_id] = 1
        
        # Create the sprite name
        sprite_name = f"{parent.text(0)} {self.main_window.group_counters[parent_id]}"
        self.main_window.group_counters[parent_id] += 1
        
        # Create the sprite item
        item = ThumbnailTreeWidgetItem(parent, sprite_name, pixmap)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Store coordinates
        item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
        
        if pixmap:
            item.set_thumbnail(pixmap)
            item.setText(1, f"{width}×{height}")
        
        return item

    def _delete_item_with_confirmation(self, item):
        """
        Prompt the user to confirm and delete the given tree item (group or sprite).
        
        If `item` is falsy, no action is taken. Presents a confirmation dialog that indicates whether the target is a group (including the number of child items when applicable) or a sprite; the item and its children (for groups) are removed if the user confirms.
        
        Parameters:
            item (QTreeWidgetItem | None): The tree item to delete; if it is a group, its child items will also be removed upon confirmation.
        """
        if not item:
            return
        
        is_group = self._is_group_item(item)
        
        # Prepare confirmation message
        if is_group:
            if item.childCount() > 0:
                msg = f"Are you sure you want to delete the group '{item.text(0)}' and all its {item.childCount()} items?"
            else:
                msg = f"Are you sure you want to delete the group '{item.text(0)}'?"
        else:
            msg = f"Are you sure you want to delete the sprite '{item.text(0)}'?"
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self.sprite_tree,
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._delete_item(item)

    def _delete_item(self, item):
        """
        Remove an item from the sprite tree and clean up any associated group counter.
        
        If the item represents a group, its counter entry in main_window.group_counters (keyed by "<group_name>_<id>") is removed. The item is then removed from its parent if present, or from the tree's top-level items if it is a root.
        Parameters:
            item (QTreeWidgetItem): The tree item to remove; if falsy, the function does nothing.
        """
        if not item:
            return
        
        parent = item.parent()
        
        # Remove counter if it's a group
        if self._is_group_item(item):
            item_id = f"{item.text(0)}_{id(item)}"
            if item_id in self.main_window.group_counters:
                del self.main_window.group_counters[item_id]
        
        if parent:
            parent.removeChild(item)
        else:
            # Root item
            index = self.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.sprite_tree.takeTopLevelItem(index)

    def _is_group_item(self, item):
        """
        Determine whether a QTreeWidgetItem represents a group in the sprite tree.
        
        Parameters:
            item (QTreeWidgetItem | None): The tree item to test.
        
        Returns:
            True if the item is a group, False otherwise.
        """
        if not item:
            return False
        
        # An item is considered a group if:
        # 1. It has children, OR
        # 2. It's a top-level item, OR
        # 3. It has no parent (should not happen but just in case)
        return (item.childCount() > 0 or 
                item.parent() is None or 
                self.sprite_tree.indexOfTopLevelItem(item) >= 0)

    def _rename_item(self, item):
        """
        Prompt the user to rename the given tree item and apply the new name.
        
        Displays an input dialog prefilled with the item's current name. If the user confirms with a non-empty name, updates the item's text. If the item is a group, also updates child sprite names to follow the group's naming scheme.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to rename; if falsy, no action is performed.
        """
        if item:
            # Use input dialog for better control
            new_name, ok = QInputDialog.getText(
                self.sprite_tree, 
                "Rename Item",
                "Enter new name:",
                text=item.text(0)
            )
            
            if ok and new_name.strip():
                item.setText(0, new_name.strip())
                
                # If it's a group, update all child sprite names
                if self._is_group_item(item):
                    self._update_child_sprite_names(item)

    def _update_child_sprite_names(self, group_item):
        """
        Update names of sprite items contained in a group to follow "<group_name> N" sequence.
        
        Parameters:
            group_item (QTreeWidgetItem): The group item whose non-group children will be renamed in order starting at 1.
        """
        if not self._is_group_item(group_item):
            return
        
        group_name = group_item.text(0)
        counter = 1
        
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            if not self._is_group_item(child):
                child.setText(0, f"{group_name} {counter}")
                counter += 1

    def _get_group_icon(self):
        """
        Return an icon to represent group items in the tree.
        
        Returns:
            QIcon: Icon used for group items; an empty `QIcon` indicates no custom icon and allows default icon behavior.
        """
        # You can implement custom icon loading here
        # For now, return None (default folder icon will be used)
        # Returning QIcon() to avoid NoneType error
        return QIcon()

    def _add_default_sprites_group(self, detected_sprites=None):
        """
        Create a root group named "Detected Sprites" and populate it with sprite items for each provided rectangle.
        
        Parameters:
            detected_sprites (iterable[QRect] | None): Optional sequence of QRect-like objects describing detected sprite regions; each rect's x, y, width, and height are used to create corresponding sprite items. If None or empty, an empty group is created.
        
        Returns:
            QTreeWidgetItem: The created root group item representing "Detected Sprites".
        """
        # Create root group
        root_group = self._add_group("Detected Sprites")
        
        # If we have detected sprites, add them
        if detected_sprites:
            for rect in detected_sprites:
                x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
                pixmap = self._extract_sprite_from_canvas(x, y, width, height)
                
                # Create sprite item
                sprite_item = self._create_sprite_item(root_group, x, y, width, height, pixmap)
                
                if pixmap:
                    sprite_item.set_thumbnail(pixmap)
        
        return root_group

    def _refresh_tree(self):
        """Refresh the tree view."""
        self.sprite_tree.viewport().update()

    def _extract_sprite_from_canvas(self, x, y, width, height):
        """
        Return the pixmap for the sprite region specified by coordinates and size.
        
        Returns:
            QPixmap or None: Extracted sprite pixmap if available; `None` when no valid pixmap can be produced.
        """
        if hasattr(self.main_window, '_extract_sprite_pixmap'):
            return self.main_window._extract_sprite_pixmap(x, y, width, height)
        elif not self.main_window.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            sprite_rect = self._find_sprite_rect_in_canvas(x, y, width, height)
            if sprite_rect:
                return self.main_window.canvas.pixmap.copy(sprite_rect)
        return None

    def _find_sprite_rect_in_canvas(self, x, y, width, height):
        """
        Create a QRect representing the sprite region in canvas coordinates.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner in canvas coordinates.
            y (int): Y coordinate of the sprite's top-left corner in canvas coordinates.
            width (int): Width of the sprite region.
            height (int): Height of the sprite region.
        
        Returns:
            QRect: Rectangle with top-left (x, y) and size (width, height) corresponding to the sprite area on the canvas.
        """
        # This is a simple implementation - you might need to adjust based on your actual data
        from PyQt6.QtCore import QRect
        return QRect(x, y, width, height)

    def clear_tree(self):
        """
        Clear the sprite tree and reset per-group counters in the main window.
        
        Removes all items from the tree widget and clears main_window.group_counters.
        """
        self.sprite_tree.clear()
        self.main_window.group_counters.clear()

    def expand_all(self):
        """
        Expand all items in the sprite tree.
        """
        self.sprite_tree.expandAll()

    def collapse_all(self):
        """
        Collapse all items in the sprite tree view.
        """
        self.sprite_tree.collapseAll()
