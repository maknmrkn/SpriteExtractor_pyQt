from PyQt6.QtWidgets import QMainWindow, QStatusBar, QVBoxLayout, QWidget, QFileDialog, QSizePolicy, QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidgetAction, QComboBox, QPushButton, QColorDialog, QDockWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView, QDialog, QVBoxLayout, QTreeWidget, QDialogButtonBox, QMessageBox, QFrame, QSplitter, QGroupBox, QFormLayout
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QTimer
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon
from .canvas import Canvas
from .thumbnail_grid import ThumbnailWidget
from .animation_preview import AnimationPreviewWidget
from .tree_manager import TreeManager
from .ui_utils import UIUtils
from .tree_item import ThumbnailTreeWidgetItem
from .sprite_detector import SpriteDetector
from .ui.menu_manager import MenuManager
from .ui.toolbar_manager import ToolbarManager
from .ui.layout_manager import LayoutManager
from .ui.signal_manager import SignalManager
from .ui.style_manager import StyleManager


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main application window, construct and arrange the editor UI components, and wire core interactions.
        
        Sets window title and size; creates and lays out the canvas, right-side panel (animation preview, sprite properties, thumbnail grid, and sprite tree), and splitter. Initializes runtime attributes used by the UI (including `group_counters`, `tree_manager`, `ui_utils`, and `sprite_detector`), creates menu and toolbars (grid and auto-detect), configures the status bar, and connects relevant signals between the canvas, thumbnail grid, and tree manager.
        """
        super().__init__()
        self.setWindowTitle("Sprite Editor")
        self.resize(1200, 800)

        # Initialize group counters
        self.group_counters = {}

        # Initialize UI components
        self.canvas = Canvas(self)
        self.thumbnail_grid = ThumbnailWidget()
        self.animation_preview = AnimationPreviewWidget()
        self.tree_manager = TreeManager(self)
        self.ui_utils = UIUtils(self)

        # Initialize managers
        self.tree_manager.setup_tree()
        self.layout_manager = LayoutManager(self)
        self.menu_manager = MenuManager(self)
        self.toolbar_manager = ToolbarManager(self)
        self.signal_manager = SignalManager(self)
        self.style_manager = StyleManager(self)

        # Initialize sprite detector
        self.sprite_detector = SpriteDetector()
        # Connect the finished signal to the handler
        self.sprite_detector.finished.connect(self._on_detection_finished)

        # Auto-detection toolbar (initially hidden)
        self.auto_detect_toolbar.setVisible(False)

    def _create_menu_bar(self):
        pass  # Handled by MenuManager

    def _create_grid_toolbar(self):
        pass  # Handled by ToolbarManager

    def _create_auto_detect_toolbar(self):
        pass  # Handled by ToolbarManager

    def _toggle_auto_detect_mode(self, checked):
        """
        Switch the editor between auto-detection mode and grid mode.
        
        When enabling auto-detection, the grid is disabled, the canvas is put into auto-detect mode, and the status bar is updated. When disabling auto-detection, the grid is enabled, the canvas exits auto-detect mode, and the status bar is updated.
        
        Parameters:
            checked (bool): If True, enable auto-detection mode; if False, enable grid mode.
        """
        if checked:
            # Switch to auto-detection mode
            self.show_grid_toggle.setChecked(False)  # Disable grid mode
            self._on_grid_toggled(False)  # Update canvas
            self.canvas.in_autodetect_mode = True
            self.statusBar().showMessage("Auto-detection mode enabled")
        else:
            # Switch back to grid mode
            self.show_grid_toggle.setChecked(True)  # Enable grid mode
            self._on_grid_toggled(True)  # Update canvas
            self.canvas.in_autodetect_mode = False
            self.statusBar().showMessage("Grid mode enabled")

    def _show_tree_context_menu(self, position):
        """
        Show a context menu for the sprite tree at the given viewport position.
        
        @param position: Position (in the sprite tree viewport coordinates) where the context menu should be shown.
        """
        menu = QMenu()
        
        # Add actions based on selection
        selected_items = self.tree_manager.sprite_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            
            # Check if the selected item is a group or a sprite
            if self.tree_manager._is_group_item(item):
                # For groups, allow adding subgroups and sprite items
                menu.addAction("Add Subgroup", lambda: self.tree_manager._add_subgroup(item))
                menu.addAction("Add Sprite Item", lambda: self.tree_manager._add_sprite_item(item))
                
                # If we have selected sprites in canvas, allow moving them to this group
                if hasattr(self.canvas, 'selected_cells') and len(self.canvas.selected_cells) > 0:
                    menu.addAction("Move Selected Sprites to Group", lambda: self.tree_manager._move_selected_sprites_to_group(item))
                
                menu.addSeparator()
                menu.addAction("Delete", lambda: self.tree_manager._delete_item(item))
            else:
                # For sprite items, allow renaming and deleting
                menu.addAction("Rename", lambda: self.tree_manager._rename_item(item))
                menu.addAction("Delete", lambda: self.tree_manager._delete_item(item))
        else:
            # No selection - add root level group
            menu.addAction("Add Group", self.tree_manager._add_group)
        
        menu.exec(self.tree_manager.sprite_tree.viewport().mapToGlobal(position))

    def _rename_item(self, item):
        """
        Start in-place editing of the given tree item.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to put into edit mode.
        """
        # Use the built-in editing capability of QTreeWidget
        self.tree_manager.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group):
        """
        Move currently selected rectangles on the canvas into the specified tree group as sprite items.
        
        For each selected canvas rectangle this creates a new sprite item under target_group, stores the rectangle coordinates on the item using the UserRole, and assigns the cropped pixmap as the item's thumbnail when available. After moving sprites the canvas selections are cleared, the display is refreshed, and the target group is expanded in the tree.
        
        Parameters:
            target_group (QTreeWidgetItem): The group item in the sprite tree that will receive the new sprite items.
        """
        # Process each selected cell in the canvas
        for rect in self.canvas.selected_cells:
            # Extract coordinates from the rectangle
            x = rect.x()
            y = rect.y()
            width = rect.width()
            height = rect.height()
            
            # Extract the sprite from the canvas
            sprite_pixmap = self._extract_sprite_pixmap(x, y, width, height)
            
            # Create a sprite item with details and thumbnail
            sprite_item = self.tree_manager._add_sprite_item(target_group, x, y, width, height, sprite_pixmap)
            
            # Store coordinates in the item
            sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
            
            if sprite_pixmap:
                sprite_item.set_thumbnail(sprite_pixmap)
        
        # Clear the canvas selections
        self.canvas.selected_cells = []
        self.canvas.update_display()
        
        # Expand the target group to show the new sprites
        self.tree_manager.sprite_tree.expandItem(target_group)

    def _add_group(self):
        """
        Create a new root-level group in the sprite tree.
        
        The new group is named "New Group", made editable, expanded in the tree view, and a per-group counter entry
        is initialized on self.group_counters using a unique key composed of the group's text and object id (initial value 1).
        """
        item = QTreeWidgetItem(self.tree_manager.sprite_tree)
        item.setText(0, "New Group")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.tree_manager.sprite_tree.expandItem(item)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[item_id] = 1

    def _add_subgroup(self, parent):
        """
        Add a new editable subgroup item as a child of the given parent tree item and initialize its per-group counter.
        
        Parameters:
            parent (QTreeWidgetItem): The parent tree item under which the new subgroup will be created.
        """
        item = QTreeWidgetItem(parent)
        item.setText(0, "New Subgroup")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.tree_manager.sprite_tree.expandItem(parent)
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
        """
        Handle keyboard interactions for the sprite tree.
        
        Pressing Delete prompts to delete the currently selected tree item with confirmation. Other keys are forwarded to the tree widget's default keyPressEvent handler.
        """
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.tree_manager.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.tree_manager._delete_item_with_confirmation(item)
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.tree_manager.sprite_tree, event)

    def _delete_item_with_confirmation(self, item):
        """
        Prompt for confirmation when necessary and delete the given tree item.
        
        If the item is a group, shows a confirmation dialog; the prompt includes that the group's contents will be deleted when the group has children. If the user confirms, removes the item via the TreeManager; otherwise no action is taken.
        
        Parameters:
            item (QTreeWidgetItem): The tree item (group or sprite) to delete.
        """
        # Check if it's a group (has children or is a top-level item)
        is_group = self.tree_manager._is_group_item(item)
        
        if is_group and item.childCount() > 0:
            # Show confirmation dialog for groups with children
            reply = QMessageBox.question(
                self,
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
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the group '{item.text(0)}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Perform the actual deletion
        self.tree_manager._delete_item(item)

    def _delete_item(self, item):
        """
        Remove a tree item from the sprite tree and remove any associated per-group counter.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to delete; if the item has a parent it is removed from that parent, otherwise it is removed from the tree's top-level items. If a matching entry exists in self.group_counters (keyed as "<item text>_<id(item)>"), that entry is deleted.
        """
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            # Also remove any counter associated with this item
            item_id = f"{item.text(0)}_{id(item)}"
            if hasattr(self, 'group_counters') and item_id in self.group_counters:
                del self.group_counters[item_id]
        else:
            # Root item
            index = self.tree_manager.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.tree_manager.sprite_tree.takeTopLevelItem(index)
                # Also remove any counter associated with this item
                item_id = f"{item.text(0)}_{id(item)}"
                if hasattr(self, 'group_counters') and item_id in self.group_counters:
                    del self.group_counters[item_id]

    def _on_grid_cell_clicked(self, x, y, width, height):
        """Handle grid cell click for highlighting only."""
        print(f"DEBUG: _on_grid_cell_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just for handling the highlight
        # The actual logic is handled in Canvas class
        pass

    def _on_tree_item_clicked(self, item, column):
        """
        Handle selection of a tree item and update the animation preview and property display accordingly.
        
        When a group item is selected (has children or is a top-level item), collect all sprite pixmaps under that group and set them in the animation preview. When a sprite item is selected, clear the animation preview and, if the item stores rectangle coordinates in its UserRole data as a (x, y, width, height) tuple, populate the X/Y/Width/Height property labels; otherwise reset the property display.
        
        Parameters:
            item: The clicked QTreeWidgetItem.
            column: The column index that was clicked.
        """
        print(f"DEBUG: _on_tree_item_clicked called for item '{item.text(0)}'")
        # Check if the clicked item is a group (has children or is a top-level item)
        if item.childCount() > 0 or item.parent() is None:
            # This is a group - collect all sprite items under it for animation
            sprite_pixmaps = []
            self.tree_manager._collect_sprite_pixmaps(item, sprite_pixmaps)
            
            # Set the collected sprites to the animation preview
            self.animation_preview.set_sprites(sprite_pixmaps)
        else:
            # This is a sprite item - reset the animation preview
            self.animation_preview.set_sprites([])
            
            # Extract coordinates from the text if it contains coordinate info
            text = item.text(0)
            # If the item was created from grid selection, it might have coordinates in its data
            if hasattr(item, 'data') and item.data(0, Qt.ItemDataRole.UserRole) is not None:
                coords = item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(coords, tuple) and len(coords) == 4:
                    x, y, w, h = coords
                    self.x_label.setText(str(x))
                    self.y_label.setText(str(y))
                    self.width_label.setText(str(w))
                    self.height_label.setText(str(h))
                    return
            
            # Reset if we can't extract coordinates
            self._reset_properties_display()

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
        """
        Reset the sprite property labels in the UI to indicate no selection.
        
        Sets the X, Y, Width, and Height labels to "-" to show that no sprite is currently selected.
        """
        self.x_label.setText("-")
        self.y_label.setText("-")
        self.y_label.setText("-")
        self.width_label.setText("-")
        self.height_label.setText("-")

    def _on_thumbnail_clicked(self, item):
        """Handle when a thumbnail is clicked"""
        # For now, just print the item details
        print(f"Thumbnail clicked: {item.text(0)}")
        # You can add more functionality here as needed

    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """
        Handle right-click on a grid cell.
        
        In normal use this triggers the UI flow for selecting or assigning a group for the cell; in auto-detection mode the handler is a proxy for multi-selection behavior.
        
        Parameters:
            x (int): X coordinate of the cell (pixels).
            y (int): Y coordinate of the cell (pixels).
            width (int): Width of the cell (pixels).
            height (int): Height of the cell (pixels).
        """
        print(f"DEBUG: _on_grid_cell_right_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just a proxy to the tree manager
        # In auto-detection mode, we'll use multi-selection instead
        pass

    def _extract_sprite_pixmap(self, x, y, width, height):
        """
        Return a cropped QPixmap representing the rectangle at (x, y, width, height) from the canvas image.
        
        Parameters:
            x (int): X coordinate of the top-left corner in canvas pixels.
            y (int): Y coordinate of the top-left corner in canvas pixels.
            width (int): Width of the rectangle in pixels.
            height (int): Height of the rectangle in pixels.
        
        Returns:
            QPixmap or None: Cropped pixmap for the specified rectangle, or `None` if the canvas has no loaded pixmap.
        """
        if not self.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            sprite_rect = QRect(x, y, width, height)
            return self.canvas.pixmap.copy(sprite_rect)
        return None

    def _update_grid_color_button(self, color: QColor):
        self.grid_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.canvas.grid_color = color
        self.canvas.update_display()

    def _update_bg_color_button(self, color: QColor):
        self.bg_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.canvas.background_color = color
        self.canvas.update_display()

    def _on_choose_grid_color(self):
        color = QColorDialog.getColor(self.canvas.grid_color, self, "Choose Grid Color")
        if color.isValid():
            self._update_grid_color_button(color)

    def _on_choose_bg_color(self):
        color = QColorDialog.getColor(self.canvas.background_color, self, "Choose Background Color")
        if color.isValid():
            self._update_bg_color_button(color)

    def _on_line_style_changed(self, text):
        self.canvas.line_style = text
        self.canvas.update_display()

    def _on_grid_toggled(self, checked):
        self.canvas.show_grid = checked
        self.canvas.update_display()

    def _on_grid_width_changed(self, value):
        self.canvas.grid_width = value
        self.canvas.update_display()

    def _on_grid_height_changed(self, value):
        self.canvas.grid_height = value
        self.canvas.update_display()

    def _on_padding_x_changed(self, value):
        self.canvas.padding_x = value
        self.canvas.update_display()

    def _on_padding_y_changed(self, value):
        self.canvas.padding_y = value
        self.canvas.update_display()

    def _on_spacing_x_changed(self, value):
        self.canvas.spacing_x = value
        self.canvas.update_display()

    def _on_spacing_y_changed(self, value):
        self.canvas.spacing_y = value
        self.canvas.update_display()

    def _auto_detect_frames(self):
        """
        Start asynchronous detection of sprite frames in the currently loaded image.
        
        If no image is loaded, updates the status bar and returns. Otherwise, sets up for detection by disabling the grid,
        enabling auto-detect mode, and starting the detection process in a separate thread. Shows a "Detecting..." message
        while processing.
        """
        if not self.canvas.pixmap or self.canvas.pixmap.isNull():
            self.statusBar().showMessage("No image loaded to detect frames from.")
            return

        # Get min dimensions from spinboxes
        min_width = self.min_width_spinbox.value()
        min_height = self.min_height_spinbox.value()

        # Disable grid while detecting sprites
        self.show_grid_toggle.setChecked(False)
        self.canvas.show_grid = False
        self.canvas.in_autodetect_mode = True
        self.auto_detect_toggle.setChecked(True)  # Enable auto-detect mode
        self.canvas.update_display()

        # Show busy message
        self.statusBar().showMessage("Detecting sprites...")

        # Start async detection
        if hasattr(self.canvas, 'current_path') and self.canvas.current_path:
            # Connect the finished signal to our handler
            self.sprite_detector.finished.connect(self._on_detection_finished)
            # Start detection in background thread
            self.sprite_detector.start_detection(self.canvas.current_path, min_width, min_height)
        else:
            self.statusBar().showMessage("Could not detect sprites: image path not available.")

    def _on_detection_finished(self, detected_sprites):
        """
        Handle completion of asynchronous sprite detection.
        
        Called when the sprite detector thread completes. Processes the detected sprites by adding them to the canvas,
        updating the display, and showing a status message. If no sprites were detected, shows an appropriate message.
        
        Parameters:
            detected_sprites (list): List of QRect objects representing detected sprite frames, or None if detection failed.
        """
        if detected_sprites:
            # Clear any existing selections and detections
            self.canvas.selected_cells = []
            self.canvas.detected_sprites = []
            
            # Add detected sprites to the canvas as detected (not selected)
            for rect in detected_sprites:
                self.canvas.detected_sprites.append(rect)
            
            # Update canvas display
            self.canvas.update_display()
            
            # Don't add to tree automatically - just show on canvas
            self.statusBar().showMessage(f"Auto-detected {len(detected_sprites)} sprites. Click on them to work with them.")
        else:
            self.statusBar().showMessage("No sprites detected in the image.")

    def _clear_detections(self):
        """
        Clear all auto-detected sprites and refresh the canvas and status bar.
        
        This removes any detected sprite rectangles and selection state from the canvas, triggers a display refresh, and updates the status bar with a confirmation message.
        """
        self.canvas.selected_cells = []
        self.canvas.update_display()
        self.statusBar().showMessage("Cleared all detections.")

    def open_file(self):
        """
        Open a file dialog, load the selected image into the canvas, and update related UI state.
        
        If an image is successfully loaded, updates the status bar with the loaded path, adds a default sprites group to the sprite tree, and makes the auto-detect toolbar visible. If loading fails, updates the status bar with an error message. If the dialog is canceled, no changes are made.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Sprite Sheet",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            if self.canvas.load_image(path):
                self.statusBar().showMessage(f"Loaded: {path}")
                # Add a default group with individual sprite items when image is loaded
                self.tree_manager._add_default_sprites_group()
                
                # Show the auto-detect toolbar
                self.auto_detect_toolbar.setVisible(True)
            else:
                self.statusBar().showMessage("Failed to load image.")