from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget, QFileDialog, QSizePolicy, QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidgetAction, QComboBox, QPushButton, QColorDialog, QDockWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView, QDialog, QVBoxLayout, QTreeWidget, QDialogButtonBox, QSplitter, QGroupBox, QFormLayout
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon
from .canvas import Canvas
from .thumbnail_grid import ThumbnailWidget


class ThumbnailTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent=None, text="", pixmap=None):
        super().__init__(parent)
        self.setText(0, text)
        if pixmap:
            self.setIcon(0, QIcon(pixmap))
    
    def set_thumbnail(self, pixmap):
        """Set the thumbnail icon for this item"""
        if pixmap:
            # Scale the pixmap to a small size for the thumbnail
            scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setIcon(0, QIcon(scaled_pixmap))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprite Editor")
        self.resize(1200, 800)

        # Create central widget with a vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a horizontal splitter to separate canvas and right panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Canvas
        self.canvas = Canvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.canvas)

        # Right panel containing the tree, properties and thumbnails
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create a group box for sprite properties
        self.properties_group = QGroupBox("Sprite Properties")
        self.properties_group.setMaximumHeight(150)  # Limit height to keep space for tree
        properties_layout = QFormLayout(self.properties_group)
        
        # Add properties fields
        self.x_label = QLabel("-")
        self.y_label = QLabel("-")
        self.width_label = QLabel("-")
        self.height_label = QLabel("-")
        
        properties_layout.addRow("X:", self.x_label)
        properties_layout.addRow("Y:", self.y_label)
        properties_layout.addRow("Width:", self.width_label)
        properties_layout.addRow("Height:", self.height_label)
        
        right_layout.addWidget(self.properties_group)
        
        # Create the thumbnail grid widget
        self.thumbnail_grid = ThumbnailWidget()
        right_layout.addWidget(self.thumbnail_grid)
        
        # Create tree widget for groups
        self.sprite_tree = QTreeWidget()
        self.sprite_tree.setHeaderLabels(["Groups"])
        self.sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sprite_tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.sprite_tree.itemClicked.connect(self._on_tree_item_clicked)  # Connect to handle item selection
        right_layout.addWidget(self.sprite_tree)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)  # Canvas takes 3/4 of space
        splitter.setStretchFactor(1, 1)  # Right panel takes 1/4 of space
        
        main_layout.addWidget(splitter)

        # Connect to the grid cell clicked signal (for highlighting)
        self.canvas.grid_cell_clicked.connect(self._on_grid_cell_clicked)
        # Connect to the grid cell right-clicked signal (for moving to group)
        self.canvas.grid_cell_right_clicked.connect(self._on_grid_cell_right_clicked)
        # Connect thumbnail clicked signal
        self.thumbnail_grid.thumbnail_clicked.connect(self._on_thumbnail_clicked)

        # Menu Bar
        self._create_menu_bar()

        # Toolbar for Grid Settings
        self._create_grid_toolbar()

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        menu_bar: QMenuBar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        open_action = file_menu.addAction("Open Sprite Sheet...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = file_menu.addAction("Save Frames As...")
        save_action.setShortcut("Ctrl+S")
        # TODO: Connect to save_frames method

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        extract_action = edit_menu.addAction("Auto-detect Frames")
        # TODO: Connect to frame detection logic

    def _create_grid_toolbar(self):
        toolbar = QToolBar("Grid Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Show Grid Toggle
        self.show_grid_toggle = toolbar.addAction("Show Grid")
        self.show_grid_toggle.setCheckable(True)
        self.show_grid_toggle.setChecked(False)
        self.show_grid_toggle.triggered.connect(self._on_grid_toggled)

        toolbar.addSeparator()

        # Grid Size (Width and Height)
        toolbar.addWidget(QLabel("Grid:"))
        
        # Grid Width
        self.grid_width_spinbox = QSpinBox()
        self.grid_width_spinbox.setRange(8, 2048)
        self.grid_width_spinbox.setValue(32)
        self.grid_width_spinbox.setSingleStep(8)
        self.grid_width_spinbox.valueChanged.connect(self._on_grid_width_changed)
        width_widget = QWidget()
        width_widget.setLayout(QHBoxLayout())
        width_widget.layout().addWidget(self.grid_width_spinbox)
        width_widget.setMaximumWidth(70)
        toolbar.addWidget(width_widget)
        
        toolbar.addWidget(QLabel("×"))  # Multiplication sign
        
        # Grid Height
        self.grid_height_spinbox = QSpinBox()
        self.grid_height_spinbox.setRange(8, 2048)
        self.grid_height_spinbox.setValue(32)
        self.grid_height_spinbox.setSingleStep(8)
        self.grid_height_spinbox.valueChanged.connect(self._on_grid_height_changed)
        height_widget = QWidget()
        height_widget.setLayout(QHBoxLayout())
        height_widget.layout().addWidget(self.grid_height_spinbox)
        height_widget.setMaximumWidth(70)
        toolbar.addWidget(height_widget)

        toolbar.addSeparator()

        # Padding X
        toolbar.addWidget(QLabel("Padding X:"))
        self.padding_x_spinbox = QSpinBox()
        self.padding_x_spinbox.setRange(0, 128)
        self.padding_x_spinbox.setValue(0)
        self.padding_x_spinbox.valueChanged.connect(self._on_padding_x_changed)
        padx_widget = QWidget()
        padx_widget.setLayout(QHBoxLayout())
        padx_widget.layout().addWidget(self.padding_x_spinbox)
        padx_widget.setMaximumWidth(80)
        toolbar.addWidget(padx_widget)

        # Padding Y
        toolbar.addWidget(QLabel("Padding Y:"))
        self.padding_y_spinbox = QSpinBox()
        self.padding_y_spinbox.setRange(0, 128)
        self.padding_y_spinbox.setValue(0)
        self.padding_y_spinbox.valueChanged.connect(self._on_padding_y_changed)
        pady_widget = QWidget()
        pady_widget.setLayout(QHBoxLayout())
        pady_widget.layout().addWidget(self.padding_y_spinbox)
        pady_widget.setMaximumWidth(80)
        toolbar.addWidget(pady_widget)

        toolbar.addSeparator()

        # Spacing X
        toolbar.addWidget(QLabel("Spacing X:"))
        self.spacing_x_spinbox = QSpinBox()
        self.spacing_x_spinbox.setRange(0, 128)
        self.spacing_x_spinbox.setValue(0)
        self.spacing_x_spinbox.valueChanged.connect(self._on_spacing_x_changed)
        spacex_widget = QWidget()
        spacex_widget.setLayout(QHBoxLayout())
        spacex_widget.layout().addWidget(self.spacing_x_spinbox)
        spacex_widget.setMaximumWidth(80)
        toolbar.addWidget(spacex_widget)

        # Spacing Y
        toolbar.addWidget(QLabel("Spacing Y:"))
        self.spacing_y_spinbox = QSpinBox()
        self.spacing_y_spinbox.setRange(0, 128)
        self.spacing_y_spinbox.setValue(0)
        self.spacing_y_spinbox.valueChanged.connect(self._on_spacing_y_changed)
        spacey_widget = QWidget()
        spacey_widget.setLayout(QHBoxLayout())
        spacey_widget.layout().addWidget(self.spacing_y_spinbox)
        spacey_widget.setMaximumWidth(80)
        toolbar.addWidget(spacey_widget)

        toolbar.addSeparator()

        # Grid Line Style
        toolbar.addWidget(QLabel("Line:"))
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(["Solid", "Dotted"])
        self.line_style_combo.currentTextChanged.connect(self._on_line_style_changed)
        toolbar.addWidget(self.line_style_combo)

        toolbar.addSeparator()

        # Grid Color Button
        self.grid_color_button = QPushButton("Grid Color")
        self.grid_color_button.setFixedSize(90, 24)
        self.grid_color_button.clicked.connect(self._on_choose_grid_color)
        toolbar.addWidget(self.grid_color_button)
        self._update_grid_color_button(QColor(0, 255, 0))  # Default green

        # Background Color Button
        self.bg_color_button = QPushButton("BG Color")
        self.bg_color_button.setFixedSize(90, 24)
        self.bg_color_button.clicked.connect(self._on_choose_bg_color)
        toolbar.addWidget(self.bg_color_button)
        self._update_bg_color_button(QColor(25, 25, 25))  # Default dark gray


    def _show_tree_context_menu(self, position):
        """Show context menu for the sprite tree."""
        menu = QMenu()
        
        # Add actions based on selection
        selected_items = self.sprite_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            menu.addAction("Add Subgroup", lambda: self._add_subgroup(item))
            menu.addAction("Add Sprite Item", lambda: self._add_sprite_item(item))
            menu.addSeparator()
            menu.addAction("Delete", lambda: self._delete_item(item))
        else:
            # No selection - add root level group
            menu.addAction("Add Group", self._add_group)
        
        menu.exec(self.sprite_tree.viewport().mapToGlobal(position))

    def _add_group(self):
        """Add a new root-level group to the tree."""
        item = QTreeWidgetItem(self.sprite_tree)
        item.setText(0, "New Group")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.sprite_tree.expandItem(item)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[item_id] = 1

    def _add_subgroup(self, parent):
        """Add a subgroup under the selected parent."""
        item = QTreeWidgetItem(parent)
        item.setText(0, "New Subgroup")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.sprite_tree.expandItem(parent)
        # Initialize counter for this group using the item's unique text and memory address
        item_id = f"{item.text(0)}_{id(item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[item_id] = 1

    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        """Add a sprite item under the selected parent."""
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
            index = self.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.sprite_tree.takeTopLevelItem(index)
                # Also remove any counter associated with this item
                item_id = f"{item.text(0)}_{id(item)}"
                if hasattr(self, 'group_counters') and item_id in self.group_counters:
                    del self.group_counters[item_id]

    def _on_grid_cell_clicked(self, x, y, width, height):
        """Handle grid cell click for highlighting only."""
        # This method is now just for handling the highlight
        # The actual logic is handled in Canvas class
        pass

    def _on_tree_item_clicked(self, item, column):
        """Handle when a tree item is clicked"""
        # Check if the clicked item is a sprite (doesn't start with the group's name followed by a space and number)
        parent_item = item.parent()
        if parent_item is not None:  # It's a child item (sprite)
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
        else:
            # It's a group, reset the display
            self._reset_properties_display()

    def _reset_properties_display(self):
        """Reset the properties display"""
        self.x_label.setText("-")
        self.y_label.setText("-")
        self.width_label.setText("-")
        self.height_label.setText("-")

    def _on_thumbnail_clicked(self, item):
        """Handle when a thumbnail is clicked"""
        # For now, just print the item details
        print(f"Thumbnail clicked: {item.text(0)}")
        # You can add more functionality here as needed

    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """Handle grid cell right-click and show group selection dialog."""
        # Show dialog to select a group for the sprite
        self._show_group_selection_dialog(x, y, width, height)

    def _show_group_selection_dialog(self, x, y, width, height):
        """Show a dialog with tree view to select a group for the sprite."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Group for Sprite")
        dialog.resize(300, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create a tree widget for group selection
        group_tree = QTreeWidget()
        group_tree.setHeaderLabel("Groups")
        
        # Copy the structure from the main sprite tree
        self._copy_tree_structure(self.sprite_tree, group_tree)
        
        # Connect to item double click
        group_tree.itemDoubleClicked.connect(lambda item, column: self._add_sprite_to_group(item, x, y, width, height, dialog))
        
        layout.addWidget(group_tree)
        
        # Add buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self._add_sprite_to_selected_group(group_tree, x, y, width, height, dialog))
        buttons.rejected.connect(dialog.close)  # Cancel button
        
        layout.addWidget(buttons)
        
        dialog.exec()

    def _copy_tree_structure(self, source_tree, target_tree):
        """Copy the tree structure from source to target tree, excluding sprite items."""
        # Clear target tree
        target_tree.clear()
        
        # Copy all items recursively, excluding sprite items
        for i in range(source_tree.topLevelItemCount()):
            item = source_tree.topLevelItem(i)
            # Only copy groups/subgroups, not sprite items
            if self._is_group_item(item):
                cloned_item = item.clone()
                # Clone only the group structure, excluding sprite items
                self._clone_group_structure(item, cloned_item)
                target_tree.addTopLevelItem(cloned_item)

    def _is_group_item(self, item):
        """Check if an item is a group (doesn't start with 'Sprite (')"""
        text = item.text(0)
        return not text.startswith("Sprite (")

    def _clone_group_structure(self, source_item, target_item):
        """Recursively clone only group items, excluding sprite items."""
        for i in range(source_item.childCount()):
            child = source_item.child(i)
            # Only clone if it's a group item, not a sprite
            if self._is_group_item(child):
                cloned_child = child.clone()
                target_item.addChild(cloned_child)
                # Recursively clone the group structure
                self._clone_group_structure(child, cloned_child)

    def _add_sprite_to_group(self, group_item, x, y, width, height, dialog):
        """Add a sprite item to the selected group with thumbnail."""
        # Extract the sprite from the canvas
        sprite_pixmap = self._extract_sprite_pixmap(x, y, width, height)
        
        # Create a sprite item with details
        sprite_item = self._add_sprite_item(group_item, x, y, width, height, sprite_pixmap)
        
        # Store coordinates in the item
        sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
        
        if sprite_pixmap:
            sprite_item.set_thumbnail(sprite_pixmap)
        
        # Expand the group to show the new sprite
        self.sprite_tree.expandItem(group_item)
        
        # Close the dialog
        dialog.accept()

    def _add_sprite_to_selected_group(self, group_tree, x, y, width, height, dialog):
        """Add sprite to the selected group in the group selection dialog."""
        selected_items = group_tree.selectedItems()
        if selected_items:
            # Find the corresponding item in the main tree
            selected_group = selected_items[0]
            main_tree_item = self._find_main_tree_item(selected_group, self.sprite_tree)
            if main_tree_item:
                # Extract the sprite from the canvas
                sprite_pixmap = self._extract_sprite_pixmap(x, y, width, height)
                
                # Create a sprite item with details and thumbnail
                sprite_item = self._add_sprite_item(main_tree_item, x, y, width, height, sprite_pixmap)
                
                # Store coordinates in the item
                sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
                
                if sprite_pixmap:
                    sprite_item.set_thumbnail(sprite_pixmap)
                
                # Expand the group to show the new sprite
                self.sprite_tree.expandItem(main_tree_item)
                
                # Close the dialog
                dialog.accept()
        else:
            dialog.close()

    def _extract_sprite_pixmap(self, x, y, width, height):
        """Extract a sprite pixmap from the canvas pixmap."""
        if not self.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            sprite_rect = QRect(x, y, width, height)
            return self.canvas.pixmap.copy(sprite_rect)
        return None

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

    def open_file(self):
        """Open a file dialog to select an image and load it into the canvas."""
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
                self._add_default_sprites_group()
            else:
                self.statusBar().showMessage("Failed to load image.")
    
    def _add_default_sprites_group(self):
        """Add a default group with individual sprite items when an image is loaded."""
        # Clear previous items
        self.sprite_tree.clear()
        
        # Add a default group
        group_item = QTreeWidgetItem(self.sprite_tree)
        group_item.setText(0, "Sprite Sheet")
        group_item.setFlags(group_item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Initialize counter for this group using the item's unique text and memory address
        group_item_id = f"{group_item.text(0)}_{id(group_item)}"
        self.group_counters = getattr(self, 'group_counters', {})
        self.group_counters[group_item_id] = 1
        
        # Do not add default sprite items, just the group
        self.sprite_tree.expandItem(group_item)