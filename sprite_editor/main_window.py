from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget, QFileDialog, QSizePolicy, QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidgetAction, QComboBox, QPushButton, QColorDialog, QDockWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView, QDialog, QVBoxLayout, QTreeWidget, QDialogButtonBox, QMessageBox, QFrame, QSplitter, QGroupBox, QFormLayout
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QTimer
from PyQt6.QtGui import QColor, QAction, QPixmap, QIcon
from .canvas import Canvas
from .thumbnail_grid import ThumbnailWidget
from .animation_preview import AnimationPreviewWidget
from .tree_manager import TreeManager
from .ui_utils import UIUtils
from .tree_item import ThumbnailTreeWidgetItem


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

        # Right panel containing the animation preview, properties, tree and thumbnails
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create the animation preview widget
        self.animation_preview = AnimationPreviewWidget()
        right_layout.addWidget(self.animation_preview)
        
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
        
        # Initialize managers
        self.tree_manager = TreeManager(self)
        self.tree_manager.setup_tree()
        self.ui_utils = UIUtils(self)
        
        right_layout.addWidget(self.sprite_tree)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)  # Canvas takes 3/4 of space
        splitter.setStretchFactor(1, 1)  # Right panel takes 1/4 of space
        
        main_layout.addWidget(splitter)

        # Connect to the grid cell clicked signal (for highlighting)
        self.canvas.grid_cell_clicked.connect(self._on_grid_cell_clicked)
        # Connect to the grid cell right-clicked signal (for moving to group)
        self.canvas.grid_cell_right_clicked.connect(self.tree_manager._on_grid_cell_right_clicked)
        # Connect to the multi-grid selection signal
        self.canvas.multi_grid_selection.connect(self.tree_manager._on_multi_grid_selection)
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
            
            # Check if the selected item is a group or a sprite
            if self._is_group_item(item):
                # For groups, allow adding subgroups and sprite items
                menu.addAction("Add Subgroup", lambda: self._add_subgroup(item))
                menu.addAction("Add Sprite Item", lambda: self._add_sprite_item(item))
                
                # If we have selected sprites in canvas, allow moving them to this group
                if hasattr(self.canvas, 'selected_cells') and len(self.canvas.selected_cells) > 0:
                    menu.addAction("Move Selected Sprites to Group", lambda: self._move_selected_sprites_to_group(item))
                
                menu.addSeparator()
                menu.addAction("Delete", lambda: self._delete_item(item))
            else:
                # For sprite items, allow renaming and deleting
                menu.addAction("Rename", lambda: self._rename_item(item))
                menu.addAction("Delete", lambda: self._delete_item(item))
        else:
            # No selection - add root level group
            menu.addAction("Add Group", self._add_group)
        
        menu.exec(self.sprite_tree.viewport().mapToGlobal(position))

    def _rename_item(self, item):
        """Rename the selected item."""
        # Use the built-in editing capability of QTreeWidget
        self.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group):
        """Move selected sprites from canvas to the target group."""
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
            sprite_item = self._add_sprite_item(target_group, x, y, width, height, sprite_pixmap)
            
            # Store coordinates in the item
            sprite_item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
            
            if sprite_pixmap:
                sprite_item.set_thumbnail(sprite_pixmap)
        
        # Clear the canvas selections
        self.canvas.selected_cells = []
        self.canvas.update_display()
        
        # Expand the target group to show the new sprites
        self.sprite_tree.expandItem(target_group)

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
            selected_items = self.sprite_tree.selectedItems()
            if selected_items:
                item = selected_items[0]
                self._delete_item_with_confirmation(item)
        else:
            # Call the original keyPressEvent for other keys
            QTreeWidget.keyPressEvent(self.sprite_tree, event)

    def _delete_item_with_confirmation(self, item):
        """Delete the selected item from the tree with confirmation for groups."""
        # Check if it's a group (has children or is a top-level item)
        is_group = self._is_group_item(item)
        
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
            index = self.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.sprite_tree.takeTopLevelItem(index)
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
        """Handle when a tree item is clicked"""
        print(f"DEBUG: _on_tree_item_clicked called for item '{item.text(0)}'")
        # Check if the clicked item is a group (has children or is a top-level item)
        if item.childCount() > 0 or item.parent() is None:
            # This is a group - collect all sprite items under it for animation
            sprite_pixmaps = []
            self._collect_sprite_pixmaps(item, sprite_pixmaps)
            
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
        print(f"DEBUG: _on_grid_cell_right_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just a proxy to the tree manager
        pass

    def _extract_sprite_pixmap(self, x, y, width, height):
        """Extract a sprite pixmap from the canvas pixmap."""
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
                self.tree_manager._add_default_sprites_group()
            else:
                self.statusBar().showMessage("Failed to load image.")