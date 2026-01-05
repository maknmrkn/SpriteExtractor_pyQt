from PyQt6.QtWidgets import QMainWindow, QStatusBar, QWidget, QSizePolicy, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSplitter
from PyQt6.QtCore import Qt
from .canvas import Canvas
from .thumbnail_grid import ThumbnailWidget
from .animation_preview import AnimationPreviewWidget
from ..models.tree_manager import TreeManager
from ..utils.ui_utils import UIUtils
from ..logic.sprite_detector import SpriteDetector
from .menu_toolbar_manager import MenuToolbarManager
from .grid_controls_manager import GridControlsManager
from .detection_manager import DetectionManager
from .tree_operations_manager import TreeOperationsManager


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

        # Initialize modular managers
        self.menu_toolbar_manager = MenuToolbarManager(self)
        self.grid_controls_manager = GridControlsManager(self)
        self.detection_manager = DetectionManager(self)
        self.tree_operations_manager = TreeOperationsManager(self)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def _on_grid_cell_clicked(self, x, y, width, height):
        """
        Update the UI highlight for the clicked grid cell.
        
        Parameters:
            x (int): X coordinate of the cell's top-left corner.
            y (int): Y coordinate of the top-left corner.
            width (int): Width of the cell in pixels.
            height (int): Height of the cell in pixels.
        """
        print(f"DEBUG: _on_grid_cell_clicked called with ({x}, {y}, {width}x{height})")
        # This method is now just for handling the highlight
        # The actual logic is handled in Canvas class

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

    # Delegate methods to the appropriate managers
    def _create_menu_bar(self):
        self.menu_toolbar_manager._create_menu_bar()
    
    def _create_grid_toolbar(self):
        self.menu_toolbar_manager._create_grid_toolbar()
    
    def _create_auto_detect_toolbar(self):
        self.menu_toolbar_manager._create_auto_detect_toolbar()
    
    def _update_grid_color_button(self, color):
        self.grid_controls_manager._update_grid_color_button(color)
    
    def _update_bg_color_button(self, color):
        self.grid_controls_manager._update_bg_color_button(color)
    
    def _on_choose_grid_color(self):
        self.grid_controls_manager._on_choose_grid_color()
    
    def _on_choose_bg_color(self):
        self.grid_controls_manager._on_choose_bg_color()
    
    def _on_line_style_changed(self, text):
        self.grid_controls_manager._on_line_style_changed(text)
    
    def _on_grid_toggled(self, checked):
        self.grid_controls_manager._on_grid_toggled(checked)
    
    def _on_grid_width_changed(self, value):
        self.grid_controls_manager._on_grid_width_changed(value)
    
    def _on_grid_height_changed(self, value):
        self.grid_controls_manager._on_grid_height_changed(value)
    
    def _on_padding_x_changed(self, value):
        self.grid_controls_manager._on_padding_x_changed(value)
    
    def _on_padding_y_changed(self, value):
        self.grid_controls_manager._on_padding_y_changed(value)
    
    def _on_spacing_x_changed(self, value):
        self.grid_controls_manager._on_spacing_x_changed(value)
    
    def _on_spacing_y_changed(self, value):
        self.grid_controls_manager._on_spacing_y_changed(value)
    
    def _toggle_auto_detect_mode(self, checked):
        self.detection_manager._toggle_auto_detect_mode(checked)
    
    def _auto_detect_frames(self):
        self.detection_manager._auto_detect_frames()
    
    def _on_detection_finished(self, detected_sprites):
        self.detection_manager._on_detection_finished(detected_sprites)
    
    def _clear_detections(self):
        self.detection_manager._clear_detections()
    
    def open_file(self):
        self.detection_manager.open_file()
    
    def _show_tree_context_menu(self, position):
        self.tree_operations_manager._show_tree_context_menu(position)
    
    def _rename_item(self, item):
        self.tree_operations_manager._rename_item(item)
    
    def _move_selected_sprites_to_group(self, target_group):
        self.tree_operations_manager._move_selected_sprites_to_group(target_group)
    
    def _add_group(self):
        self.tree_operations_manager._add_group()
    
    def _add_subgroup(self, parent):
        self.tree_operations_manager._add_subgroup(parent)
    
    def _add_sprite_item(self, parent, x=None, y=None, width=None, height=None, pixmap=None):
        return self.tree_operations_manager._add_sprite_item(parent, x, y, width, height, pixmap)
    
    def _on_tree_key_press(self, event):
        self.tree_operations_manager._on_tree_key_press(event)
    
    def _delete_item_with_confirmation(self, item):
        self.tree_operations_manager._delete_item_with_confirmation(item)
    
    def _delete_item(self, item):
        self.tree_operations_manager._delete_item(item)
    
    def _on_tree_item_clicked(self, item, _column):
        self.tree_operations_manager._on_tree_item_clicked(item, _column)
    
    def _collect_sprite_pixmaps(self, item, sprite_list):
        self.tree_operations_manager._collect_sprite_pixmaps(item, sprite_list)
    
    def _reset_properties_display(self):
        self.tree_operations_manager._reset_properties_display()
    
    def _extract_sprite_pixmap(self, x, y, width, height):
        return self.tree_operations_manager._extract_sprite_pixmap(x, y, width, height)
    
    @property
    def auto_detect_toolbar(self):
        return self.menu_toolbar_manager.auto_detect_toolbar