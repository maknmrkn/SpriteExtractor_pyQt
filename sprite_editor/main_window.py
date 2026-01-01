from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget, QFileDialog, QSizePolicy, QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidgetAction, QComboBox, QPushButton, QColorDialog, QDockWidget, QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu, QAbstractItemView
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor
from .canvas import Canvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprite Editor")
        self.resize(1024, 768)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Canvas
        self.canvas = Canvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)

        # Menu Bar
        self._create_menu_bar()

        # Toolbar for Grid Settings
        self._create_grid_toolbar()

        # Create and add the tree view for sprite organization
        self._create_sprite_tree_dock()

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

    def _create_sprite_tree_dock(self):
        """Create a dock widget with a tree view for organizing sprites in groups and subgroups."""
        # Create dock widget
        self.tree_dock = QDockWidget("Sprite Organization", self)
        self.tree_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create tree widget
        self.sprite_tree = QTreeWidget()
        self.sprite_tree.setHeaderLabels(["Sprites"])
        self.sprite_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sprite_tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.sprite_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Set header properties
        header = self.sprite_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Add tree to dock
        self.tree_dock.setWidget(self.sprite_tree)
        
        # Add dock to main window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tree_dock)

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

    def _add_subgroup(self, parent):
        """Add a subgroup under the selected parent."""
        item = QTreeWidgetItem(parent)
        item.setText(0, "New Subgroup")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.sprite_tree.expandItem(parent)

    def _add_sprite_item(self, parent):
        """Add a sprite item under the selected parent."""
        item = QTreeWidgetItem(parent)
        item.setText(0, "Sprite Item")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

    def _delete_item(self, item):
        """Delete the selected item from the tree."""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            # Root item
            index = self.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.sprite_tree.takeTopLevelItem(index)

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
                # Add a default group with sprites when image is loaded
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
            
        # Add a few sprite items to the group (you might want to detect sprites automatically later)
        for i in range(4):
            sprite_item = QTreeWidgetItem(group_item)
            sprite_item.setText(0, f"Sprite {i+1}")
            sprite_item.setFlags(sprite_item.flags() | Qt.ItemFlag.ItemIsEditable)
            
        self.sprite_tree.expandItem(group_item)