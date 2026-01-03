from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAbstractItemView, QHeaderView, QInputDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from .tree_item import ThumbnailTreeWidgetItem
from .tree_structure_manager import TreeStructureManager
from .tree_context_menu import TreeContextMenu
from .sprite_operations import SpriteOperations
from .export_operations import ExportOperations


class TreeManager:
    def __init__(self, main_window):
        """
        Initialize the TreeManager and wire its modular components and UI references.
        
        Parameters:
        	main_window: The application's main window object; passed to and used by underlying managers and operations.
        
        Attributes:
        	structure_manager: TreeStructureManager instance managing the tree structure.
        	context_menu: TreeContextMenu instance providing the tree's context menu.
        	sprite_operations: SpriteOperations instance handling sprite creation/editing/movement.
        	export_operations: ExportOperations instance handling export-related functionality.
        	sprite_tree: Reference to the QTreeWidget managed by structure_manager.
        	sprite_edited: Signal emitted with a QTreeWidgetItem when a sprite is edited.
        	group_added: Signal emitted with a QTreeWidgetItem when a group is added.
        """
        self.main_window = main_window
        
        # Initialize modular components
        self.structure_manager = TreeStructureManager(main_window)
        
        # Initialize the context menu with a reference to self
        self.context_menu = TreeContextMenu(self)
        self.sprite_operations = SpriteOperations(self)
        self.export_operations = ExportOperations(self)
        
        # Make the sprite_tree available at the top level
        self.sprite_tree = self.structure_manager.sprite_tree
        
        # Signals
        self.sprite_edited = pyqtSignal(QTreeWidgetItem)  # Emitted when sprite is edited
        self.group_added = pyqtSignal(QTreeWidgetItem)    # Emitted when group is added

    def setup_tree(self):
        """
        Initialize and configure the sprite tree widget for the manager.
        
        Calls the structure manager to build the tree, updates the manager's sprite_tree reference, enables a custom context menu, connects handlers for context-menu requests, item clicks, and item double-clicks, and replaces the tree's keyPressEvent with the manager's key handler.
        """
        self.structure_manager.setup_tree()
        # Update the reference after setup
        self.sprite_tree = self.structure_manager.sprite_tree
        
        # Connect signals
        self.sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sprite_tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.sprite_tree.itemClicked.connect(self._on_tree_item_clicked)
        self.sprite_tree.itemDoubleClicked.connect(self._on_tree_item_double_clicked)
        self.sprite_tree.keyPressEvent = self._on_tree_key_press

    # Delegate method calls to the appropriate modules
    def _add_group(self, name=None):
        """
        Create a new group item in the sprite tree.
        
        Parameters:
        	name (str | None): Optional label for the new group. If omitted, a default name will be used.
        
        Returns:
        	group_item (QTreeWidgetItem): The created group tree item.
        """
        return self.structure_manager._add_group(name)
    
    def _add_subgroup(self, parent):
        """
        Create a new subgroup under the given parent group item.
        
        Parameters:
        	parent (QTreeWidgetItem): The parent group item under which the new subgroup will be created.
        
        Returns:
        	subgroup_item (QTreeWidgetItem): The newly created subgroup tree item.
        """
        return self.structure_manager._add_subgroup(parent)
    
    def _add_sprite_item_to_group(self, parent):
        """
        Add a new sprite item as a child of the specified group.
        
        Parameters:
            parent (QTreeWidgetItem): The group item to which the new sprite item will be added.
        
        Returns:
            QTreeWidgetItem: The newly created sprite item.
        """
        return self.structure_manager._add_sprite_item_to_group(parent)
    
    def _create_sprite_item(self, parent, x, y, width, height, pixmap=None):
        """
        Create a sprite tree item under the given parent using the specified rectangle and optional thumbnail.
        
        Parameters:
            parent (QTreeWidgetItem): The group or parent tree item to attach the new sprite to.
            x (int): X coordinate of the sprite within the source canvas.
            y (int): Y coordinate of the sprite within the source canvas.
            width (int): Width of the sprite.
            height (int): Height of the sprite.
            pixmap (QPixmap | None): Optional thumbnail to display for the sprite.
        
        Returns:
            QTreeWidgetItem: The newly created sprite item whose stored coordinates are (x, y, width, height).
        """
        return self.structure_manager._create_sprite_item(parent, x, y, width, height, pixmap)
    
    def _delete_item_with_confirmation(self, item):
        """
        Prompt the user for confirmation and delete the specified tree item if confirmed.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to remove (a group or a sprite).
        """
        self.structure_manager._delete_item_with_confirmation(item)
    
    def _delete_item(self, item):
        """
        Delete the given tree item from the underlying structure manager.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to remove (group or sprite).
        """
        self.structure_manager._delete_item(item)
    
    def _is_group_item(self, item):
        """
        Check whether a tree item represents a group.
        
        Parameters:
            item: The QTreeWidgetItem to inspect.
        
        Returns:
            `True` if the given item is a group item, `False` otherwise.
        """
        return self.structure_manager._is_group_item(item)
    
    def _rename_item(self, item):
        """
        Begin renaming the specified tree item.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to rename (group or sprite item).
        """
        self.structure_manager._rename_item(item)
    
    def _update_child_sprite_names(self, group_item):
        """
        Update the display names of all sprite items contained in the given group to reflect their current ordering.
        
        Parameters:
            group_item (QTreeWidgetItem): The group tree item whose child sprite items will have their names refreshed.
        """
        self.structure_manager._update_child_sprite_names(group_item)
    
    def _get_group_icon(self):
        """
        Return the icon used to represent group items in the sprite tree.
        
        Returns:
            QIcon: Icon used for group items.
        """
        return self.structure_manager._get_group_icon()
    
    def _add_default_sprites_group(self, detected_sprites=None):
        """
        Create and add a default "Detected Sprites" group to the sprite tree.
        
        If `detected_sprites` is provided, the new group will be populated with sprite items created from the given boundaries.
        
        Parameters:
            detected_sprites (iterable[tuple[int, int, int, int]] | None): Optional iterable of sprite boundaries as (x, y, width, height). If None, an empty default group is created.
        
        Returns:
            QTreeWidgetItem: The newly created group item in the sprite tree.
        """
        return self.structure_manager._add_default_sprites_group(detected_sprites)
    
    def _refresh_tree(self):
        """
        Refreshes the sprite tree UI to reflect the current structure and data.
        """
        self.structure_manager._refresh_tree()
    
    def _extract_sprite_from_canvas(self, x, y, width, height):
        """
        Extracts a sprite image from the main canvas at the specified rectangle.
        
        Parameters:
            x (int): X coordinate of the top-left corner in pixels.
            y (int): Y coordinate of the top-left corner in pixels.
            width (int): Width of the rectangle in pixels.
            height (int): Height of the rectangle in pixels.
        
        Returns:
            image: The image object representing the extracted sprite.
        """
        return self.structure_manager._extract_sprite_from_canvas(x, y, width, height)
    
    def _find_sprite_rect_in_canvas(self, x, y, width, height):
        """
        Locate the sprite's rectangle in the canvas that corresponds to the given coordinates and size.
        
        Returns:
            The matching rectangle object representing the sprite's position and size if found, otherwise None.
        """
        return self.structure_manager._find_sprite_rect_in_canvas(x, y, width, height)
    
    def clear_tree(self):
        """
        Remove all groups and sprite items from the sprite tree.
        
        This clears the tree view and any stored structure for sprites managed by this manager.
        """
        self.structure_manager.clear_tree()
    
    def expand_all(self):
        """
        Expand all groups and sprite items in the sprite tree view so every node is visible.
        """
        self.structure_manager.expand_all()
    
    def collapse_all(self):
        """
        Collapse all groups and their child items in the sprite tree.
        """
        self.structure_manager.collapse_all()
    
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
    
    def _get_all_groups(self):
        """
        Return all group items in the sprite tree.
        
        Returns:
            list[QTreeWidgetItem]: A list of group items representing all groups in the tree.
        """
        return self.sprite_operations._get_all_groups()
    
    def _add_sprite_to_group(self, group, x, y, width, height):
        """
        Add a new sprite (defined by coordinates) into the specified group in the tree.
        
        Parameters:
            group (QTreeWidgetItem): The group item to which the sprite will be added.
            x (int): X coordinate of the sprite within the canvas.
            y (int): Y coordinate of the sprite within the canvas.
            width (int): Width of the sprite.
            height (int): Height of the sprite.
        
        Returns:
            QTreeWidgetItem: The newly created sprite tree item that was added to the group.
        """
        return self.sprite_operations._add_sprite_to_group(group, x, y, width, height)
    
    def _add_sprites_to_group(self, group, selected_rects):
        """
        Add multiple sprite regions to the specified group.
        
        Parameters:
            group: The group item to receive the new sprites (e.g., a QTreeWidgetItem representing a group).
            selected_rects: An iterable of rectangles specifying sprites to add. Each rectangle is given as (x, y, width, height).
        """
        self.sprite_operations._add_sprites_to_group(group, selected_rects)
    
    def _create_sprite_with_coords(self, x, y, width, height):
        """
        Create a new sprite using the specified canvas coordinates and add it to the sprite collection.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner in pixels.
            y (int): Y coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.sprite_operations._create_sprite_with_coords(x, y, width, height)
    
    def _create_sprites_with_coords(self, selected_rects):
        """
        Create sprite items from a list of rectangular coordinates.
        
        Parameters:
            selected_rects (Iterable[tuple[int, int, int, int]]): Iterable of (x, y, width, height) tuples defining sprite regions to create.
        """
        self.sprite_operations._create_sprites_with_coords(selected_rects)
    
    def _edit_sprite_at_coords(self, x, y, width, height):
        """
        Edit the sprite defined by the given bounding box on the canvas.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner in pixels.
            y (int): Y coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.sprite_operations._edit_sprite_at_coords(x, y, width, height)
    
    def _edit_sprite_item(self, item):
        """
        Open a sprite editor for the specified sprite tree item.
        
        Parameters:
            item (QTreeWidgetItem): The tree item representing the sprite to edit.
        """
        self.sprite_operations._edit_sprite_item(item)
    
    def _show_sprite_in_canvas(self, item):
        """
        Display the sprite represented by the given tree item in the main canvas.
        
        Parameters:
            item (QTreeWidgetItem): Tree item that represents the sprite to show in the canvas.
        """
        self.sprite_operations._show_sprite_in_canvas(item)
    
    def _move_selected_sprites_to_group(self, target_group):
        """
        Move the currently selected sprite items into the specified group.
        
        Parameters:
            target_group (QTreeWidgetItem): The group item that will receive the selected sprite items.
        """
        self.sprite_operations._move_selected_sprites_to_group(target_group)
    
    def _export_sprite(self, item):
        """
        Export the given sprite tree item to the configured export targets.
        
        Parameters:
            item (QTreeWidgetItem): The sprite item to export; must represent a non-group sprite.
        """
        self.export_operations._export_sprite(item)
    
    def _export_group(self, group_item):
        """
        Export all sprites contained in the specified group using the configured export operations.
        
        Parameters:
            group_item (QTreeWidgetItem): Tree item representing the group whose sprites should be exported.
        """
        self.export_operations._export_group(group_item)
    
    def _export_group_as_gif(self, group_item):
        """
        Export all sprites in the given group as an animated GIF.
        
        Parameters:
            group_item (QTreeWidgetItem): Tree item representing the sprite group to export.
        """
        self.export_operations._export_group_as_gif(group_item)
    
    def _export_selected_sprites(self, selected_rects):
        """
        Export multiple sprites specified by their bounding rectangles.
        
        Parameters:
            selected_rects (Iterable[tuple[int, int, int, int]]): Sequence of rectangles where each tuple is (x, y, width, height) describing a sprite region to export.
        """
        self.export_operations._export_selected_sprites(selected_rects)
    
    def _extract_and_save_sprite(self, x, y, width, height):
        """
        Extract the sprite located at the given rectangle in the canvas and save it to disk.
        
        Parameters:
            x (int): X-coordinate of the sprite's top-left corner in pixels.
            y (int): Y-coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.export_operations._extract_and_save_sprite(x, y, width, height)
    
    def _copy_sprite_to_clipboard(self, item):
        """
        Copy the image represented by a sprite tree item to the system clipboard.
        
        Parameters:
            item (QTreeWidgetItem): Tree item representing the sprite whose image will be copied.
        """
        self.export_operations._copy_sprite_to_clipboard(item)
    
    def _collect_sprite_items(self, item, result_list):
        """
        Collects sprite items from the given tree item into the provided list.
        
        Parameters:
            item: The tree item (root or group) to traverse for sprite items.
            result_list: A list that will be appended with found sprite items.
        """
        self.export_operations._collect_sprite_items(item, result_list)
    
    def _collect_sprite_pixmaps(self, item, result_list):
        """
        Collects QPixmap objects for the given tree item and appends them to result_list.
        
        Parameters:
            item (QTreeWidgetItem): The tree item (sprite or group) whose sprite pixmaps should be collected.
            result_list (list): A list to which discovered QPixmap objects will be appended.
        """
        self.export_operations._collect_sprite_pixmaps(item, result_list)
    
    def _qimage_to_pil(self, qimage):
        """
        Convert the given QImage into an equivalent PIL Image.
        
        Parameters:
            qimage (QImage): Source image to convert.
        
        Returns:
            PIL.Image.Image: The converted PIL Image.
        """
        return self.export_operations._qimage_to_pil(qimage)
    
    def get_selected_sprite_items(self):
        """
        Return the selected sprite items from the tree, excluding group items.
        
        Returns:
            list[QTreeWidgetItem]: List of selected tree items that represent individual sprites.
        """
        selected_items = self.sprite_tree.selectedItems()
        sprite_items = []
        
        for item in selected_items:
            if not self._is_group_item(item):
                sprite_items.append(item)
        
        return sprite_items

    def get_selected_group_items(self):
        """
        Retrieve the currently selected group items from the sprite tree.
        
        Only items that are recognized as groups are included; non-group selected items are ignored.
        
        Returns:
            list[QTreeWidgetItem]: List of selected group items.
        """
        selected_items = self.sprite_tree.selectedItems()
        group_items = []
        
        for item in selected_items:
            if self._is_group_item(item):
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
        if not item or self._is_group_item(item):
            return
        
        # Update stored coordinates
        item.setData(0, Qt.ItemDataRole.UserRole, 
                    (new_boundary.x(), new_boundary.y(), 
                     new_boundary.width(), new_boundary.height()))
        
        # Update size display
        item.setText(1, f"{new_boundary.width()}×{new_boundary.height()}")
        
        # Emit signal
        self.sprite_edited.emit(item)

    # Tree event handlers
    def _on_tree_item_clicked(self, item, column):
        """
        Handle a click on a tree item and update UI selection accordingly.
        
        If the main window defines a `_on_tree_item_clicked` handler, forward the click to it. If the clicked item represents a sprite (not a group) and stores a bounding tuple (x, y, w, h) in its UserRole, then when the main window canvas is in autodetect mode this will clear the canvas selection, attempt to locate the corresponding rectangle in the canvas, add it to the canvas selection if found, and request a canvas display update. Any exceptions raised while updating the canvas selection are caught and printed.
        
        Parameters:
            item (QTreeWidgetItem): The clicked tree item.
            column (int): The column index that was clicked.
        """
        # Update properties panel in main window
        if hasattr(self.main_window, '_on_tree_item_clicked'):
            self.main_window._on_tree_item_clicked(item, column)
        
        # If it's a sprite item, update the canvas selection
        if not self._is_group_item(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple) and len(data) == 4:
                x, y, w, h = data
                # Select this sprite in canvas (if in auto-detect mode)
                try:
                    if (hasattr(self.main_window, 'canvas') and 
                        hasattr(self.main_window.canvas, 'in_autodetect_mode') and 
                        self.main_window.canvas.in_autodetect_mode):
                        self.main_window.canvas.selected_cells = []
                        found_rect = self._find_sprite_rect_in_canvas(x, y, w, h)
                        if found_rect:
                            self.main_window.canvas.selected_cells.append(found_rect)
                            self.main_window.canvas.update_display()
                except Exception as e:
                    print(f"Error selecting sprite in canvas: {e}")

    def _on_tree_item_double_clicked(self, item, column):
        """
        Open the sprite editor for the double-clicked sprite tree item.
        
        If the item represents a sprite (not a group), triggers editing of that sprite item. No action is taken for group items.
        """
        if not self._is_group_item(item):
            self._edit_sprite_item(item)

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
                self._delete_item_with_confirmation(item)
        elif event.key() == Qt.Key.Key_F2:
            selected_items = self.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self._rename_item(item)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            selected_items = self.sprite_tree.selectedItems()
            if selected_items and not self._is_group_item(selected_items[0]):
                self._edit_sprite_item(selected_items[0])
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.sprite_tree, event)