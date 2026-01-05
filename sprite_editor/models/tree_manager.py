from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal
from .tree_structure_manager import TreeStructureManager
from .tree_operations_manager import TreeOperationsManager
from .tree_event_handler import TreeEventHandler
from .tree_context_manager import TreeContextManager
from .tree_init_manager import TreeInitManager
from .tree_operations_delegator import TreeOperationsDelegator


class TreeManager:
    def __init__(self, main_window):
        self.main_window = main_window
        
        self.structure_manager = TreeStructureManager(main_window)
        
        self.context_manager = TreeContextManager(self)
        self.operations_manager = TreeOperationsManager(self)
        self.event_handler = TreeEventHandler(self)
        self.init_manager = TreeInitManager(self)
        self.operations_delegator = TreeOperationsDelegator(self)
        
        self.sprite_tree = self.structure_manager.sprite_tree
        
        self.sprite_edited = pyqtSignal(QTreeWidgetItem)
        self.group_added = pyqtSignal(QTreeWidgetItem)

    def setup_tree(self):
        self.init_manager.setup_tree()
        self.sprite_tree = self.init_manager.sprite_tree

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
        self.context_manager._show_tree_context_menu(position)
    
    def _on_grid_cell_right_clicked(self, x, y, width, height):
        self.context_manager._on_grid_cell_right_clicked(x, y, width, height)
    
    def _on_multi_grid_selection(self, selected_rects):
        self.context_manager._on_multi_grid_selection(selected_rects)
    
    def _get_all_groups(self):
        return self.operations_delegator._get_all_groups()
    
    def _add_sprite_to_group(self, group, x, y, width, height):
        return self.operations_delegator._add_sprite_to_group(group, x, y, width, height)
    
    def _add_sprites_to_group(self, group, selected_rects):
        self.operations_delegator._add_sprites_to_group(group, selected_rects)
    
    def _create_sprite_with_coords(self, x, y, width, height):
        self.operations_delegator._create_sprite_with_coords(x, y, width, height)
    
    def _create_sprites_with_coords(self, selected_rects):
        self.operations_delegator._create_sprites_with_coords(selected_rects)
    
    def _edit_sprite_at_coords(self, x, y, width, height):
        self.operations_delegator._edit_sprite_at_coords(x, y, width, height)
    
    def _edit_sprite_item(self, item):
        self.operations_delegator._edit_sprite_item(item)
    
    def _show_sprite_in_canvas(self, item):
        self.operations_delegator._show_sprite_in_canvas(item)
    
    def _move_selected_sprites_to_group(self, target_group):
        self.operations_delegator._move_selected_sprites_to_group(target_group)
    
    def _export_sprite(self, item):
        self.operations_delegator._export_sprite(item)
    
    def _export_group(self, group_item):
        self.operations_delegator._export_group(group_item)
    
    def _export_group_as_gif(self, group_item):
        self.operations_delegator._export_group_as_gif(group_item)
    
    def _export_selected_sprites(self, selected_rects):
        self.operations_delegator._export_selected_sprites(selected_rects)
    
    def _extract_and_save_sprite(self, x, y, width, height):
        self.operations_delegator._extract_and_save_sprite(x, y, width, height)
    
    def _copy_sprite_to_clipboard(self, item):
        self.operations_delegator._copy_sprite_to_clipboard(item)
    
    def _collect_sprite_items(self, item, result_list):
        self.operations_delegator._collect_sprite_items(item, result_list)
    
    def _collect_sprite_pixmaps(self, item, result_list):
        self.operations_delegator._collect_sprite_pixmaps(item, result_list)
    
    def _qimage_to_pil(self, qimage):
        return self.operations_delegator._qimage_to_pil(qimage)
    
    def get_selected_sprite_items(self):
        return self.event_handler.get_selected_sprite_items()

    def get_selected_group_items(self):
        return self.event_handler.get_selected_group_items()

    def update_sprite_item(self, item, new_boundary):
        return self.event_handler.update_sprite_item(item, new_boundary)

    def _on_tree_item_clicked(self, item, column):
        self.event_handler._on_tree_item_clicked(item, column)

    def _on_tree_item_double_clicked(self, item):
        self.event_handler._on_tree_item_double_clicked(item)

    def _on_tree_key_press(self, event):
        self.event_handler._on_tree_key_press(event)
