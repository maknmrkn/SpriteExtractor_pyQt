from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QCursor


class TreeContextMenu:
    def __init__(self, tree_manager):
        """
        Initialize the TreeContextMenu with the provided tree manager and cache the main application window.
        
        Parameters:
            tree_manager (TreeManager): Manager that owns the sprite/tree state and provides access to the main application window via its `main_window` attribute.
        """
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window

    @property
    def sprite_tree(self):
        """
        Access the sprite tree widget provided by the associated TreeManager.
        
        Returns:
            QTreeWidget: The tree widget displaying groups and sprite items.
        """
        return self.tree_manager.sprite_tree

    def _show_tree_context_menu(self, position):
        """
        Show a context menu for the sprite tree at the given widget-local position.
        
        Displays a context-sensitive menu for the sprite tree based on the current selection:
        - If a group is selected, presents actions to add subgroups/sprites, move selected canvas sprites into the group (when applicable), rename, delete, and export the group.
        - If a sprite item is selected, presents actions to edit, rename, show in canvas, delete, and export the sprite.
        - If nothing is selected, presents actions to add a new root-level group or a default group.
        Selecting a menu action delegates the operation to the associated TreeManager methods.
        
        Parameters:
            position (QPoint): Position in the sprite tree widget's viewport where the menu should be shown.
        """
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
        """
        Show a context menu for a single grid cell offering group association, group creation, sprite editing, and sprite extraction actions.
        
        Parameters:
            x (int): X coordinate of the grid cell (column index or pixel X depending on caller).
            y (int): Y coordinate of the grid cell (row index or pixel Y depending on caller).
            width (int): Width of the grid cell in pixels.
            height (int): Height of the grid cell in pixels.
        
        Description:
            The menu lists existing groups (if any) under "Add to Group" to add the sprite at the specified coordinates to a chosen group, provides an option to create a new group with the sprite at these coordinates, and exposes actions to edit the sprite at the coordinates or extract and save it. The menu is displayed at the current cursor position.
        """
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
        """
        Show a context menu for a multi-cell grid selection with actions to create groups, add sprites to existing groups, and export the selection.
        
        Displays a styled menu at the current cursor position that:
        - Offers "Add to Group" submenu listing existing groups (adds all selected cells to the chosen group).
        - Provides actions to create a new group from the selected cells.
        - Provides an action to export all selected sprites.
        
        Parameters:
            selected_rects (Sequence): A sequence of grid rectangles or coordinate tuples representing the selected cells to operate on.
        """
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