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
        """Setup the sprite tree widget"""
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
        return self.structure_manager._add_group(name)
    
    def _add_subgroup(self, parent):
        return self.structure_manager._add_subgroup(parent)
    
    def _add_sprite_item_to_group(self, parent):
        return self.structure_manager._add_sprite_item_to_group(parent)
    
    def _create_sprite_item(self, parent, x, y, width, height, pixmap=None):
        return self.structure_manager._create_sprite_item(parent, x, y, width, height, pixmap)
    
    def _delete_item_with_confirmation(self, item):
        self.structure_manager._delete_item_with_confirmation(item)
    
    def _delete_item(self, item):
        self.structure_manager._delete_item(item)
    
    def _is_group_item(self, item):
        return self.structure_manager._is_group_item(item)
    
    def _rename_item(self, item):
        self.structure_manager._rename_item(item)
    
    def _update_child_sprite_names(self, group_item):
        self.structure_manager._update_child_sprite_names(group_item)
    
    def _get_group_icon(self):
        return self.structure_manager._get_group_icon()
    
    def _add_default_sprites_group(self, detected_sprites=None):
        return self.structure_manager._add_default_sprites_group(detected_sprites)
    
    def _refresh_tree(self):
        self.structure_manager._refresh_tree()
    
    def _extract_sprite_from_canvas(self, x, y, width, height):
        return self.structure_manager._extract_sprite_from_canvas(x, y, width, height)
    
    def _find_sprite_rect_in_canvas(self, x, y, width, height):
        return self.structure_manager._find_sprite_rect_in_canvas(x, y, width, height)
    
    def clear_tree(self):
        self.structure_manager.clear_tree()
    
    def expand_all(self):
        self.structure_manager.expand_all()
    
    def collapse_all(self):
        self.structure_manager.collapse_all()
    
    def _show_tree_context_menu(self, position):
        self.context_menu._show_tree_context_menu(position)
    
    def _on_grid_cell_right_clicked(self, x, y, width, height):
        self.context_menu._on_grid_cell_right_clicked(x, y, width, height)
    
    def _on_multi_grid_selection(self, selected_rects):
        self.context_menu._on_multi_grid_selection(selected_rects)
    
    def _get_all_groups(self):
        return self.sprite_operations._get_all_groups()
    
    def _add_sprite_to_group(self, group, x, y, width, height):
        return self.sprite_operations._add_sprite_to_group(group, x, y, width, height)
    
    def _add_sprites_to_group(self, group, selected_rects):
        self.sprite_operations._add_sprites_to_group(group, selected_rects)
    
    def _create_sprite_with_coords(self, x, y, width, height):
        self.sprite_operations._create_sprite_with_coords(x, y, width, height)
    
    def _create_sprites_with_coords(self, selected_rects):
        self.sprite_operations._create_sprites_with_coords(selected_rects)
    
    def _edit_sprite_at_coords(self, x, y, width, height):
        self.sprite_operations._edit_sprite_at_coords(x, y, width, height)
    
    def _edit_sprite_item(self, item):
        self.sprite_operations._edit_sprite_item(item)
    
    def _show_sprite_in_canvas(self, item):
        self.sprite_operations._show_sprite_in_canvas(item)
    
    def _move_selected_sprites_to_group(self, target_group):
        self.sprite_operations._move_selected_sprites_to_group(target_group)
    
    def _export_sprite(self, item):
        self.export_operations._export_sprite(item)
    
    def _export_group(self, group_item):
        self.export_operations._export_group(group_item)
    
    def _export_group_as_gif(self, group_item):
        self.export_operations._export_group_as_gif(group_item)
    
    def _export_selected_sprites(self, selected_rects):
        self.export_operations._export_selected_sprites(selected_rects)
    
    def _extract_and_save_sprite(self, x, y, width, height):
        self.export_operations._extract_and_save_sprite(x, y, width, height)
    
    def _copy_sprite_to_clipboard(self, item):
        self.export_operations._copy_sprite_to_clipboard(item)
    
    def _collect_sprite_items(self, item, result_list):
        self.export_operations._collect_sprite_items(item, result_list)
    
    def _collect_sprite_pixmaps(self, item, result_list):
        self.export_operations._collect_sprite_pixmaps(item, result_list)
    
    def _qimage_to_pil(self, qimage):
        return self.export_operations._qimage_to_pil(qimage)
    
    def get_selected_sprite_items(self):
        """Get all selected sprite items (non-groups)."""
        selected_items = self.sprite_tree.selectedItems()
        sprite_items = []
        
        for item in selected_items:
            if not self._is_group_item(item):
                sprite_items.append(item)
        
        return sprite_items

    def get_selected_group_items(self):
        """Get all selected group items."""
        selected_items = self.sprite_tree.selectedItems()
        group_items = []
        
        for item in selected_items:
            if self._is_group_item(item):
                group_items.append(item)
        
        return group_items

    def update_sprite_item(self, item, new_boundary):
        """Update a sprite item with new boundary."""
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
        """Handle when a tree item is clicked"""
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
        """Handle double click on tree item."""
        if not self._is_group_item(item):
            self._edit_sprite_item(item)

    def _on_tree_key_press(self, event):
        """Handle key press events in the tree widget."""
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