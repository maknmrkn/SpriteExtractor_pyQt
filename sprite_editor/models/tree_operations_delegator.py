class TreeOperationsDelegator:
    """
    Handles delegation of operations methods for TreeManager
    """
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager

    def _get_all_groups(self):
        """
        Return all group items in the sprite tree.
        
        Returns:
            list[QTreeWidgetItem]: A list of group items representing all groups in the tree.
        """
        return self.tree_manager.operations_manager._get_all_groups()
    
    def _add_sprite_to_group(self, group, x, y, width, height):
        """
        Add a new sprite (defined by coordinates) into the specified group in the tree.
        
        Parameters:
            group (QTreeWidgetItem): The group item to which the sprite will be added.
            x (int): X coordinate of the sprite within the canvas.
            y (int): Y coordinate of the sprite within the canvas.
            width (int): Width of the sprite.
            height (int): Height of the sprite.
        
        Returns:
            QTreeWidgetItem: The newly created sprite tree item that was added to the group.
        """
        return self.tree_manager.operations_manager._add_sprite_to_group(group, x, y, width, height)
    
    def _add_sprites_to_group(self, group, selected_rects):
        """
        Add multiple sprite regions to the specified group.
        
        Parameters:
            group: The group item to receive the new sprites (e.g., a QTreeWidgetItem representing a group).
            selected_rects: An iterable of rectangles specifying sprites to add. Each rectangle is given as (x, y, width, height).
        """
        self.tree_manager.operations_manager._add_sprites_to_group(group, selected_rects)
    
    def _create_sprite_with_coords(self, x, y, width, height):
        """
        Create a new sprite using the specified canvas coordinates and add it to the sprite collection.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner in pixels.
            y (int): Y coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.tree_manager.operations_manager._create_sprite_with_coords(x, y, width, height)
    
    def _create_sprites_with_coords(self, selected_rects):
        """
        Create sprite items from a list of rectangular coordinates.
        
        Parameters:
            selected_rects (Iterable[tuple[int, int, int, int]]): Iterable of (x, y, width, height) tuples defining sprite regions to create.
        """
        self.tree_manager.operations_manager._create_sprites_with_coords(selected_rects)
    
    def _edit_sprite_at_coords(self, x, y, width, height):
        """
        Edit the sprite defined by the given bounding box on the canvas.
        
        Parameters:
            x (int): X coordinate of the sprite's top-left corner in pixels.
            y (int): Y coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.tree_manager.operations_manager._edit_sprite_at_coords(x, y, width, height)
    
    def _edit_sprite_item(self, item):
        """
        Open a sprite editor for the specified sprite tree item.
        
        Parameters:
            item (QTreeWidgetItem): The tree item representing the sprite to edit.
        """
        self.tree_manager.operations_manager._edit_sprite_item(item)
    
    def _show_sprite_in_canvas(self, item):
        """
        Display the sprite represented by the given tree item in the main canvas.
        
        Parameters:
            item (QTreeWidgetItem): Tree item that represents the sprite to show in the canvas.
        """
        self.tree_manager.operations_manager._show_sprite_in_canvas(item)
    
    def _move_selected_sprites_to_group(self, target_group):
        """
        Move the currently selected sprite items into the specified group.
        
        Parameters:
            target_group (QTreeWidgetItem): The group item that will receive the selected sprite items.
        """
        self.tree_manager.operations_manager._move_selected_sprites_to_group(target_group)
    
    def _export_sprite(self, item):
        """
        Export the given sprite tree item to the configured export targets.
        
        Parameters:
            item (QTreeWidgetItem): The sprite item to export; must represent a non-group sprite.
        """
        self.tree_manager.operations_manager._export_sprite(item)
    
    def _export_group(self, group_item):
        """
        Export all sprites contained in the specified group using the configured export operations.
        
        Parameters:
            group_item (QTreeWidgetItem): Tree item representing the group whose sprites should be exported.
        """
        self.tree_manager.operations_manager._export_group(group_item)
    
    def _export_group_as_gif(self, group_item):
        """
        Export all sprites in the given group as an animated GIF.
        
        Parameters:
            group_item (QTreeWidgetItem): Tree item representing the sprite group to export.
        """
        self.tree_manager.operations_manager._export_group_as_gif(group_item)
    
    def _export_selected_sprites(self, selected_rects):
        """
        Export multiple sprites specified by their bounding rectangles.
        
        Parameters:
            selected_rects (Iterable[tuple[int, int, int, int]]): Sequence of rectangles where each tuple is (x, y, width, height) describing a sprite region to export.
        """
        self.tree_manager.operations_manager._export_selected_sprites(selected_rects)
    
    def _extract_and_save_sprite(self, x, y, width, height):
        """
        Extract the sprite located at the given rectangle in the canvas and save it to disk.
        
        Parameters:
            x (int): X-coordinate of the sprite's top-left corner in pixels.
            y (int): Y-coordinate of the sprite's top-left corner in pixels.
            width (int): Width of the sprite in pixels.
            height (int): Height of the sprite in pixels.
        """
        self.tree_manager.operations_manager._extract_and_save_sprite(x, y, width, height)
    
    def _copy_sprite_to_clipboard(self, item):
        """
        Copy the image represented by a sprite tree item to the system clipboard.
        
        Parameters:
            item (QTreeWidgetItem): Tree item representing the sprite whose image will be copied.
        """
        self.tree_manager.operations_manager._copy_sprite_to_clipboard(item)
    
    def _collect_sprite_items(self, item, result_list):
        """
        Collects sprite items from the given tree item into the provided list.
        
        Parameters:
            item: The tree item (root or group) to traverse for sprite items.
            result_list: A list that will be appended with found sprite items.
        """
        self.tree_manager.operations_manager._collect_sprite_items(item, result_list)
    
    def _collect_sprite_pixmaps(self, item, result_list):
        """
        Collects QPixmap objects for the given tree item and appends them to result_list.
        
        Parameters:
            item (QTreeWidgetItem): The tree item (sprite or group) whose sprite pixmaps should be collected.
            result_list (list): A list to which discovered QPixmap objects will be appended.
        """
        self.tree_manager.operations_manager._collect_sprite_pixmaps(item, result_list)
    
    def _qimage_to_pil(self, qimage):
        """
        Convert the given QImage into an equivalent PIL Image.
        
        Parameters:
            qimage (QImage): Source image to convert.
        
        Returns:
            PIL.Image.Image: The converted PIL Image.
        """
        return self.tree_manager.operations_manager._qimage_to_pil(qimage)