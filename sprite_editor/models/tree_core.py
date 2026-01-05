from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QHeaderView, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .tree_item import ThumbnailTreeWidgetItem


class TreeCore:
    def __init__(self, main_window):
        self.main_window = main_window
        self.sprite_tree = None
        self.current_editing_item = None

    def setup_tree(self):
        self.sprite_tree = QTreeWidget()
        self.sprite_tree.setHeaderLabel("Sprites")
        self.sprite_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        header = self.sprite_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        self.sprite_tree.setColumnCount(2)
        self.sprite_tree.setHeaderLabels(["Name", "Size"])

    def _add_group(self, name=None):
        if name is None:
            name = "New Group"
        
        item = QTreeWidgetItem(self.sprite_tree)
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        icon = self._get_group_icon()
        if icon:
            item.setIcon(0, icon)
        
        group_id = f"{name}_{id(item)}"
        self.main_window.group_counters[group_id] = 1
        
        self.sprite_tree.expandItem(item)
        
        return item

    def _add_subgroup(self, parent):
        if not self._is_group_item(parent):
            return
        
        name = "New Subgroup"
        item = QTreeWidgetItem(parent)
        item.setText(0, name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        icon = self._get_group_icon()
        if icon:
            item.setIcon(0, icon)
        
        group_id = f"{name}_{id(item)}"
        self.main_window.group_counters[group_id] = 1
        
        parent.setExpanded(True)
        
        return item

    def _add_sprite_item_to_group(self, parent):
        if not self._is_group_item(parent):
            return
        
        parent_id = f"{parent.text(0)}_{id(parent)}"
        if parent_id not in self.main_window.group_counters:
            self.main_window.group_counters[parent_id] = 1
        
        sprite_name = f"{parent.text(0)} {self.main_window.group_counters[parent_id]}"
        self.main_window.group_counters[parent_id] += 1
        
        item = ThumbnailTreeWidgetItem(parent, sprite_name, None)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        parent.setExpanded(True)
        
        return item

    def _create_sprite_item(self, parent, x, y, width, height, pixmap=None):
        parent_id = f"{parent.text(0)}_{id(parent)}"
        if parent_id not in self.main_window.group_counters:
            self.main_window.group_counters[parent_id] = 1
        
        sprite_name = f"{parent.text(0)} {self.main_window.group_counters[parent_id]}"
        self.main_window.group_counters[parent_id] += 1
        
        item = ThumbnailTreeWidgetItem(parent, sprite_name, pixmap)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        item.setData(0, Qt.ItemDataRole.UserRole, (x, y, width, height))
        
        if pixmap:
            item.set_thumbnail(pixmap)
            item.setText(1, f"{width}×{height}")
        
        return item

    def _delete_item_with_confirmation(self, item):
        if not item:
            return
        
        is_group = self._is_group_item(item)
        
        if is_group:
            if item.childCount() > 0:
                msg = f"Are you sure you want to delete the group '{item.text(0)}' and all its {item.childCount()} items?"
            else:
                msg = f"Are you sure you want to delete the group '{item.text(0)}'?"
        else:
            msg = f"Are you sure you want to delete the sprite '{item.text(0)}'?"
        
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
        if not item:
            return
        
        parent = item.parent()
        
        if self._is_group_item(item):
            item_id = f"{item.text(0)}_{id(item)}"
            if item_id in self.main_window.group_counters:
                del self.main_window.group_counters[item_id]
        
        if parent:
            parent.removeChild(item)
        else:
            index = self.sprite_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.sprite_tree.takeTopLevelItem(index)

    def _is_group_item(self, item):
        if not item:
            return False
        
        return (item.childCount() > 0 or 
                item.parent() is None or 
                self.sprite_tree.indexOfTopLevelItem(item) >= 0)

    def _rename_item(self, item):
        if item:
            new_name, ok = QInputDialog.getText(
                self.sprite_tree, 
                "Rename Item",
                "Enter new name:",
                text=item.text(0)
            )
            
            if ok and new_name.strip():
                item.setText(0, new_name.strip())
                
                if self._is_group_item(item):
                    self._update_child_sprite_names(item)

    def _update_child_sprite_names(self, group_item):
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
        return QIcon()

    def _add_default_sprites_group(self, detected_sprites=None):
        root_group = self._add_group("Detected Sprites")
        
        if detected_sprites:
            for rect in detected_sprites:
                x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
                pixmap = self._extract_sprite_from_canvas(x, y, width, height)
                
                sprite_item = self._create_sprite_item(root_group, x, y, width, height, pixmap)
                
                if pixmap:
                    sprite_item.set_thumbnail(pixmap)
        
        return root_group

    def _refresh_tree(self):
        self.sprite_tree.viewport().update()

    def _extract_sprite_from_canvas(self, x, y, width, height):
        if hasattr(self.main_window, '_extract_sprite_pixmap'):
            return self.main_window._extract_sprite_pixmap(x, y, width, height)
        elif not self.main_window.canvas.pixmap.isNull():
            sprite_rect = self._find_sprite_rect_in_canvas(x, y, width, height)
            if sprite_rect:
                return self.main_window.canvas.pixmap.copy(sprite_rect)
        return None

    def _find_sprite_rect_in_canvas(self, x, y, width, height):
        from PyQt6.QtCore import QRect
        return QRect(x, y, width, height)

    def clear_tree(self):
        self.sprite_tree.clear()
        self.main_window.group_counters.clear()

    def expand_all(self):
        self.sprite_tree.expandAll()

    def collapse_all(self):
        self.sprite_tree.collapseAll()