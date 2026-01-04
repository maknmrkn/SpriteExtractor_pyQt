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
from .sprite_detector import SpriteDetector


class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main application window, build and arrange the editor UI (central canvas and right-side panel with animation preview, sprite properties, thumbnail grid, and sprite tree), initialize runtime state, create menus and toolbars, and connect component signals.
        
        Initializes runtime attributes used by the UI (including `group_counters`, `tree_manager`, `ui_utils`, and `sprite_detector`), configures the horizontal splitter layout, creates the grid and auto-detect toolbars (auto-detect toolbar hidden by default), sets up the status bar with an initial "Ready" message, and wires signals between the canvas, thumbnail grid, sprite detector, and tree manager.
        """
        super().__init__()
        self.setWindowTitle("Sprite Editor")
        self.resize(1200, 800)

        # Initialize group counters
        self.group_counters = {}

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
        
        right_layout.addWidget(self.tree_manager.sprite_tree)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)  # Canvas takes 3/4 of space
        splitter.setStretchFactor(1, 1)  # Right panel takes 1/4 of space
        
        main_layout.addWidget(splitter)

        # Initialize sprite detector
        self.sprite_detector = SpriteDetector()
        # Connect the finished signal to the handler
        self.sprite_detector.finished.connect(self._on_detection_finished)

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

        # Auto-detection toolbar (initially hidden)
        self._create_auto_detect_toolbar()
        self.auto_detect_toolbar.setVisible(False)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        """
        Create the main window's menu bar with File and Edit menus and their actions.
        
        Adds a File menu containing:
        - "Open Sprite Sheet..." (Ctrl+O) — opens a file dialog and loads an image via open_file.
        - "Save Frames As..." (Ctrl+S) — placeholder action (not yet connected).
        - "Exit" (Ctrl+Q) — closes the window.
        
        Adds an Edit menu containing:
        - "Auto-detect Frames" — triggers the auto-detection workflow via _auto_detect_frames.
        """
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
        extract_action.triggered.connect(self._auto_detect_frames)

    def _create_grid_toolbar(self):
        """
        Create and add the "Grid Settings" toolbar with controls for configuring the canvas grid and related visual options.
        
        The toolbar provides:
        - a Show Grid toggle (checked by default);
        - grid size controls for width and height (default 32, range 8–2048, step 8);
        - padding X/Y and spacing X/Y spinboxes (default 0, range 0–128);
        - a line style selector with "Solid" and "Dotted" options;
        - a Grid Color button (default green) and a BG Color button (default dark gray).
        
        Each control is connected to the MainWindow handlers that update the canvas state when changed.
        """
        toolbar = QToolBar("Grid Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Show Grid Toggle
        self.show_grid_toggle = toolbar.addAction("Show Grid")
        self.show_grid_toggle.setCheckable(True)
        self.show_grid_toggle.setChecked(True)  # Default to checked
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

    def _create_auto_detect_toolbar(self):
        """
        Add the auto-detection toolbar to the main window.
        
        Creates and configures the "Auto Detection Settings" toolbar with:
        - a checkable "Auto Detection Mode" toggle connected to _toggle_auto_detect_mode,
        - spin boxes for minimum detection width and height (1–2048, default 8),
        - a "Detect Sprites" action connected to _auto_detect_frames,
        - a "Clear Detections" action connected to _clear_detections.
        
        The toolbar is added to the top tool bar area and its widgets are stored as instance attributes for later access.
        """
        self.auto_detect_toolbar = QToolBar("Auto Detection Settings")
        self.auto_detect_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.auto_detect_toolbar)

        # Toggle for auto-detection mode
        self.auto_detect_toggle = self.auto_detect_toolbar.addAction("Auto Detection Mode")
        self.auto_detect_toggle.setCheckable(True)
        self.auto_detect_toggle.setChecked(False)
        self.auto_detect_toggle.triggered.connect(self._toggle_auto_detect_mode)

        self.auto_detect_toolbar.addSeparator()

        # Min width for detection
        self.auto_detect_toolbar.addWidget(QLabel("Min Width:"))
        self.min_width_spinbox = QSpinBox()
        self.min_width_spinbox.setRange(1, 2048)
        self.min_width_spinbox.setValue(8)
        self.min_width_spinbox.setSingleStep(1)
        self.min_width_spinbox.setMaximumWidth(70)
        self.auto_detect_toolbar.addWidget(self.min_width_spinbox)

        # Min height for detection
        self.auto_detect_toolbar.addWidget(QLabel("Min Height:"))
        self.min_height_spinbox = QSpinBox()
        self.min_height_spinbox.setRange(1, 2048)
        self.min_height_spinbox.setValue(8)
        self.min_height_spinbox.setSingleStep(1)
        self.min_height_spinbox.setMaximumWidth(70)
        self.auto_detect_toolbar.addWidget(self.min_height_spinbox)

        # Auto-detect button
        self.auto_detect_button = self.auto_detect_toolbar.addAction("Detect Sprites")
        self.auto_detect_button.triggered.connect(self._auto_detect_frames)

        # Clear detections button
        self.clear_detections_button = self.auto_detect_toolbar.addAction("Clear Detections")
        self.clear_detections_button.triggered.connect(self._clear_detections)

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
        Enter in-place edit mode for the given tree item in the sprite tree.
        
        Parameters:
            item (QTreeWidgetItem): The tree item whose text should be edited.
        """
        # Use the built-in editing capability of QTreeWidget
        self.tree_manager.sprite_tree.editItem(item, 0)

    def _move_selected_sprites_to_group(self, target_group):
        """
        Move each selected canvas rectangle into the given sprite group as a new sprite item.
        
        For each selected rectangle, create a sprite item under target_group, store the rectangle coordinates on the item using the UserRole, set the cropped pixmap as the item's thumbnail when available, clear the canvas selection, refresh the canvas display, and expand target_group in the tree.
        
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
        Prompt the user for confirmation when necessary and delete the specified tree item.
        
        If the item is a group, a confirmation dialog is shown. If the group has children, the prompt specifies that all contents will be deleted. If the user confirms, the item is removed; otherwise no action is taken.
        
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
        Remove a tree item from the sprite tree and delete its per-group counter if present.
        
        Parameters:
            item (QTreeWidgetItem): The tree item to remove. If the item has a parent it is removed from that parent; otherwise it is removed from the tree's top-level items. If a matching entry exists in self.group_counters (keyed as "<item text>_<id(item)>") that entry is deleted.
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
        """
        Update the UI highlight for the clicked grid cell.
        
        Parameters:
            x (int): X coordinate of the cell's top-left corner.
            y (int): Y coordinate of the cell's top-left corner.
            width (int): Width of the cell in pixels.
            height (int): Height of the cell in pixels.
        """
        print(f"DEBUG: _on_grid_cell_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just for handling the highlight
        # The actual logic is handled in Canvas class
        pass

    def _on_tree_item_clicked(self, item, column):
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
        self.x_label.setText("-")
        self.y_label.setText("-")
        self.y_label.setText("-")
        self.width_label.setText("-")
        self.height_label.setText("-")

    def _on_thumbnail_clicked(self, item):
        """
        Respond to a thumbnail click in the thumbnail widget.
        
        Currently logs the clicked thumbnail's label to stdout; intended as the hook for future thumbnail selection behavior.
        
        Parameters:
            item (QTreeWidgetItem): The thumbnail tree item that was clicked.
        """
        # For now, just print the item details
        print(f"Thumbnail clicked: {item.text(0)}")
        # You can add more functionality here as needed

    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """
        Handle a right-click on a grid cell.
        
        Triggers the UI flow to assign or select a sprite group for the clicked cell; when auto-detection mode is active, acts as a proxy to support multi-selection behavior.
        """
        print(f"DEBUG: _on_grid_cell_right_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just a proxy to the tree manager
        # In auto-detection mode, we'll use multi-selection instead
        pass

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
        if not self.canvas.pixmap.isNull():
            # Crop the sprite from the original pixmap
            sprite_rect = QRect(x, y, width, height)
            return self.canvas.pixmap.copy(sprite_rect)
        return None

    def _update_grid_color_button(self, color: QColor):
        """
        Update the grid color control and apply the color to the canvas.
        
        Parameters:
            color (QColor): The color to use for the grid; updates the grid color button's appearance and sets the canvas's grid color, then refreshes the canvas display.
        """
        self.grid_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.canvas.grid_color = color
        self.canvas.update_display()

    def _update_bg_color_button(self, color: QColor):
        """
        Update the background-color button's appearance and apply the chosen color to the canvas.
        
        Parameters:
            color (QColor): New background color; this updates the button's background and text color for legibility, sets the canvas background_color, and refreshes the canvas display.
        """
        self.bg_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")
        self.canvas.background_color = color
        self.canvas.update_display()

    def _on_choose_grid_color(self):
        """
        Open a color picker and apply the selected color to the canvas grid.
        
        If the user selects a valid color, update the grid color button and the canvas grid color via the update helper.
        """
        color = QColorDialog.getColor(self.canvas.grid_color, self, "Choose Grid Color")
        if color.isValid():
            self._update_grid_color_button(color)

    def _on_choose_bg_color(self):
        """
        Open a color picker to choose a canvas background color and apply it if valid.
        
        If the user selects a valid color, update the background color button and the canvas background.
        """
        color = QColorDialog.getColor(self.canvas.background_color, self, "Choose Background Color")
        if color.isValid():
            self._update_bg_color_button(color)

    def _on_line_style_changed(self, text):
        """
        Set the canvas grid line style and refresh the display.
        
        Parameters:
            text (str): The name of the line style to apply (e.g., "Solid", "Dotted").
        """
        self.canvas.line_style = text
        self.canvas.update_display()

    def _on_grid_toggled(self, checked):
        """
        Enable or disable the canvas grid and refresh the canvas display.
        
        Parameters:
            checked (bool): True to show the grid, False to hide it.
        """
        self.canvas.show_grid = checked
        self.canvas.update_display()

    def _on_grid_width_changed(self, value):
        """
        Set the canvas grid cell width and refresh the canvas display.
        
        Parameters:
            value (int): New grid cell width in pixels.
        """
        self.canvas.grid_width = value
        self.canvas.update_display()

    def _on_grid_height_changed(self, value):
        """
        Set the canvas grid cell height and refresh the canvas display.
        
        Parameters:
            value (int): New grid cell height in pixels.
        """
        self.canvas.grid_height = value
        self.canvas.update_display()

    def _on_padding_x_changed(self, value):
        """
        Set the horizontal padding between grid cells on the canvas and refresh the view.
        
        Parameters:
            value (int): New horizontal padding in pixels to apply between grid cells.
        """
        self.canvas.padding_x = value
        self.canvas.update_display()

    def _on_padding_y_changed(self, value):
        """
        Update the canvas vertical grid padding and refresh the display.
        
        Parameters:
            value (int): New vertical padding value for the grid.
        """
        self.canvas.padding_y = value
        self.canvas.update_display()

    def _on_spacing_x_changed(self, value):
        """
        Update the canvas horizontal grid spacing and refresh the display.
        
        Parameters:
            value (int): New horizontal spacing in pixels between grid cells.
        """
        self.canvas.spacing_x = value
        self.canvas.update_display()

    def _on_spacing_y_changed(self, value):
        """
        Set the vertical grid spacing for the canvas and refresh the display.
        
        Parameters:
            value (int): New vertical spacing (in pixels) between grid cells.
        """
        self.canvas.spacing_y = value
        self.canvas.update_display()

    def _auto_detect_frames(self):
        """
        Initiate sprite-frame detection for the currently loaded image.
        
        If no image is loaded, updates the status bar and returns. If the image is loaded but its file path is unavailable, updates the status bar and returns. Otherwise, reads minimum width/height from the UI controls, puts the UI into auto-detection state, starts detection in the background, and updates the status bar to "Detecting sprites...".
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
        Apply the results of a completed sprite-detection run to the canvas and update UI state.
        
        If `detected_sprites` contains rectangles, clear current selections and detections, store the detected rectangles on the canvas, refresh the canvas display, and show a status message with the number of detected sprites and next steps. If `detected_sprites` is empty or None, update the status to indicate that no sprites were detected.
        
        Parameters:
            detected_sprites (list[QRect] | None): List of QRect objects representing detected sprite frames, or None if detection produced no results.
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
        Clear all auto-detected sprite rectangles from the canvas and update the UI.
        
        Removes detected selections, refreshes the canvas display, and sets the status bar message to confirm the action.
        """
        self.canvas.selected_cells = []
        self.canvas.update_display()
        self.statusBar().showMessage("Cleared all detections.")

    def open_file(self):
        """
        Open an image file into the canvas and update UI state.
        
        If a file is selected and successfully loaded, updates the status bar with the file path, adds the default sprites group to the sprite tree, and makes the auto-detect toolbar visible. If loading fails, shows an error message in the status bar. If the dialog is cancelled, no changes are made.
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