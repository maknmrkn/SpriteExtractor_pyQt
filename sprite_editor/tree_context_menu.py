from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor


class TreeContextMenu:
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window

    @property
    def sprite_tree(self):
        return self.tree_manager.sprite_tree

    def _show_tree_context_menu(self, position):
        """Show context menu for the sprite tree."""
        menu = QMenu()
        
        # Add actions based on selection
        selected_items = self.sprite_tree.selectedItems()
        
        if selected_items:
            item = selected_items[0]
            
            # Check if the selected item is a group or a sprite
            if self.tree_manager._is_group_item(item):
                # For groups, allow adding subgroups and sprite items
                menu.addAction("📁 Add Subgroup", lambda: self.tree_manager._add_subgroup(item))
                menu.addAction("➕ Add Sprite Item", lambda: self.tree_manager._add_sprite_item_to_group(item))
                
                # If we have selected sprites in canvas, allow moving them to this group
                if hasattr(self.main_window.canvas, 'selected_cells') and len(self.main_window.canvas.selected_cells) > 0:
                    menu.addAction("📥 Move Selected Sprites to Group", 
                                 lambda: self.tree_manager._move_selected_sprites_to_group(item))
                
                menu.addSeparator()
                menu.addAction("✏️ Rename", lambda: self.tree_manager._rename_item(item))
                menu.addAction("🗑️ Delete", lambda: self.tree_manager._delete_item_with_confirmation(item))
                
                # Export options
                menu.addSeparator()
                export_menu = menu.addMenu("💾 Export")
                export_menu.addAction("Export Group as PNG", lambda: self.tree_manager._export_group(item))
                export_menu.addAction("Export Group as GIF", lambda: self.tree_manager._export_group_as_gif(item))
                
            else:
                # For sprite items
                menu.addAction("✏️ Edit Sprite", lambda: self.tree_manager._edit_sprite_item(item))
                menu.addAction("✏️ Rename", lambda: self.tree_manager._rename_item(item))
                menu.addAction("🔍 Show in Canvas", lambda: self.tree_manager._show_sprite_in_canvas(item))
                menu.addAction("🗑️ Delete", lambda: self.tree_manager._delete_item_with_confirmation(item))
                
                # Export options
                menu.addSeparator()
                export_menu = menu.addMenu("💾 Export")
                export_menu.addAction("Save as PNG", lambda: self.tree_manager._export_sprite(item))
                export_menu.addAction("Copy to Clipboard", lambda: self.tree_manager._copy_sprite_to_clipboard(item))
        else:
            # No selection - add root level group
            menu.addAction("📁 Add Group", self.tree_manager._add_group)
            menu.addAction("📁 Add Default Group", lambda: self.tree_manager._add_default_sprites_group())
        
        # Always show refresh option
        menu.addSeparator()
        menu.addAction("🔄 Refresh Tree", lambda: self.tree_manager._refresh_tree())
        
        menu.exec(self.sprite_tree.viewport().mapToGlobal(position))

    def _on_grid_cell_right_clicked(self, x, y, width, height):
        """Handle grid cell right-click and show group selection dialog."""
        # Create context menu for single sprite
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)
        
        # Get all groups in the tree
        groups = self.tree_manager._get_all_groups()
        
        if not groups:
            menu.addAction("📁 Create New Group", 
                         lambda: self.tree_manager._create_sprite_with_coords(x, y, width, height))
        else:
            # Add groups to menu
            group_menu = menu.addMenu("📤 Add to Group")
            
            for group in groups:
                # Create action with group icon
                action = group_menu.addAction(f"📁 {group.text(0)}")
                action.triggered.connect(lambda checked, g=group: 
                                       self.tree_manager._add_sprite_to_group(g, x, y, width, height))
            
            # Add separator
            menu.addSeparator()
        
        # Add option to create new group
        menu.addAction("📁＋ Create New Group", 
                     lambda: self.tree_manager._create_sprite_with_coords(x, y, width, height))
        
        # Add edit option
        menu.addSeparator()
        menu.addAction("✏️ Edit Sprite", 
                     lambda: self.tree_manager._edit_sprite_at_coords(x, y, width, height))
        
        # Add extract option
        menu.addAction("💾 Extract Sprite", 
                     lambda: self.tree_manager._extract_and_save_sprite(x, y, width, height))
        
        menu.exec(QCursor.pos())

    def _on_multi_grid_selection(self, selected_rects):
        """Handle multi-grid selection with Ctrl key."""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
        """)
        
        groups = self.tree_manager._get_all_groups()
        
        if not groups:
            menu.addAction("📁 Create New Group", 
                         lambda: self.tree_manager._create_sprites_with_coords(selected_rects))
        else:
            # Add groups to menu
            group_menu = menu.addMenu("📤 Add to Group")
            
            for group in groups:
                action = group_menu.addAction(f"📁 {group.text(0)}")
                action.triggered.connect(lambda checked, g=group: 
                                       self.tree_manager._add_sprites_to_group(g, selected_rects))
            
            menu.addSeparator()
        
        menu.addAction("📁＋ Create New Group", 
                     lambda: self.tree_manager._create_sprites_with_coords(selected_rects))
        
        # Add extract option for all selected
        menu.addSeparator()
        menu.addAction("💾 Export All Selected", 
                     lambda: self.tree_manager._export_selected_sprites(selected_rects))
        
        menu.exec(QCursor.pos())