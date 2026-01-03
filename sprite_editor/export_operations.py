import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt


class ExportOperations:
    def __init__(self, tree_manager):
        """
        Initialize ExportOperations with a tree manager and cache the main window.
        
        Parameters:
            tree_manager: The tree manager that provides access to the sprite tree and owns the application main_window; stored as `self.tree_manager`. The initializer also stores `tree_manager.main_window` as `self.main_window` for use in dialogs and status updates.
        """
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window

    @property
    def sprite_tree(self):
        """
        Access the sprite tree managed by the associated tree manager.
        
        Returns:
            The sprite tree instance from self.tree_manager.
        """
        return self.tree_manager.sprite_tree

    def _export_sprite(self, item):
        """
        Export a single non-group sprite item to an image file.
        
        Prompts the user with a Save File dialog. If the user selects a path, saves the item's original pixmap as PNG or as JPEG (90% quality) when the filename ends with .jpg/.jpeg. The function returns without action if the item is missing, is a group, has no valid pixmap, or the dialog is cancelled. On save failure, an error message is shown.
        
        Parameters:
            item: The tree item representing the sprite to export; group items are ignored.
        """
        if not item or self.tree_manager._is_group_item(item):
            return
        
        # Get pixmap from item
        pixmap = None
        if hasattr(item, 'get_original_pixmap'):
            pixmap = item.get_original_pixmap()
        
        if not pixmap or pixmap.isNull():
            return
        
        # Get save path
        default_name = f"{item.text(0)}.png"
        path, _ = QFileDialog.getSaveFileName(
            self.sprite_tree,
            "Export Sprite",
            default_name,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*.*)"
        )
        
        if path:
            try:
                # Save the pixmap
                if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
                    pixmap.save(path, "JPEG", 90)  # 90% quality for JPEG
                else:
                    pixmap.save(path, "PNG")
            except Exception as e:
                QMessageBox.critical(self.sprite_tree, "Error", f"Failed to save sprite: {str(e)}")

    def _export_group(self, group_item):
        """
        Export all non-group sprites contained in the given group to individual image files.
        
        Prompts the user to select a directory, skips subgroup children and items without a valid pixmap, and saves each sprite as PNG (or as JPEG at 90% quality if the filename ends with `.jpg`/`.jpeg`). Shows an error message dialog if exporting fails.
        
        Parameters:
            group_item: The group tree item whose direct (non-group) children will be exported. If falsy or not a group item, the function returns without action.
        """
        if not group_item or not self.tree_manager._is_group_item(group_item):
            return
        
        # Get directory to save files
        dir_path = QFileDialog.getExistingDirectory(
            self.sprite_tree,
            "Select Directory to Export Group"
        )
        
        if not dir_path:
            return  # User cancelled
        
        try:
            # Process each child in the group
            for i in range(group_item.childCount()):
                child_item = group_item.child(i)
                
                # Skip if it's a subgroup
                if self.tree_manager._is_group_item(child_item):
                    continue
                
                # Get pixmap from item
                pixmap = None
                if hasattr(child_item, 'get_original_pixmap'):
                    pixmap = child_item.get_original_pixmap()
                
                if not pixmap or pixmap.isNull():
                    continue
                
                # Create file name based on item text
                file_name = f"{child_item.text(0)}.png"
                file_path = os.path.join(dir_path, file_name)
                
                # Save the pixmap
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    pixmap.save(file_path, "JPEG", 90)  # 90% quality for JPEG
                else:
                    pixmap.save(file_path, "PNG")
        except Exception as e:
            QMessageBox.critical(self.sprite_tree, "Error", f"Failed to export group: {str(e)}")

    def _export_group_as_gif(self, group_item):
        """
        Export the given group as an animated GIF.
        
        Prompts the user to choose a destination GIF file, collects all sprite pixmaps from the group,
        converts them to PIL Images, and saves them as an animated GIF (100ms frame duration, loop forever).
        If the user cancels, the group is empty, or the item is not a group, the function returns without action.
        Shows an informational message on success and a warning if Pillow (PIL) is not available.
        
        Parameters:
            group_item: The tree item representing the group to export; must be a group item.
        """
        if not group_item or not self.tree_manager._is_group_item(group_item):
            return
        
        # Get save path
        path, _ = QFileDialog.getSaveFileName(
            self.sprite_tree,
            "Export Group as GIF",
            f"{group_item.text(0)}.gif",
            "GIF Files (*.gif)"
        )
        
        if not path:
            return
        
        # Collect all sprite pixmaps
        sprite_pixmaps = []
        self.tree_manager._collect_sprite_pixmaps(group_item, sprite_pixmaps)
        
        if not sprite_pixmaps:
            return
        
        # Save as GIF (you might need to implement GIF saving)
        # This is a placeholder - you need to implement actual GIF saving
        try:
            # Convert QPixmap to QImage and save
            from PIL import Image
            images = []
            for pixmap in sprite_pixmaps:
                image = pixmap.toImage()
                if not image.isNull():
                    # Convert to PIL Image
                    pil_image = self._qimage_to_pil(image)
                    if pil_image:
                        images.append(pil_image)
            
            if images:
                images[0].save(path, save_all=True, append_images=images[1:], 
                             duration=100, loop=0)
                
                QMessageBox.information(self.sprite_tree, "Success", 
                                      f"GIF exported successfully to:\n{path}")
        except ImportError:
            QMessageBox.warning(self.sprite_tree, "Error", 
                              "PIL (Pillow) library is required for GIF export.")

    def _export_selected_sprites(self, selected_rects):
        """
        Export sprites corresponding to selected canvas rectangles into PNG files in a user-chosen directory.
        
        Prompts the user to select a target directory, then for each rectangle in `selected_rects` extracts a pixmap from the canvas via `tree_manager._extract_sprite_from_canvas(x, y, width, height)` and, if the pixmap is valid, saves it as a PNG named `sprite_000.png`, `sprite_001.png`, etc. Invalid or null pixmaps are skipped.
        
        Parameters:
            selected_rects: iterable
                An iterable of rectangle-like objects providing `x()`, `y()`, `width()`, and `height()` methods that define the regions to export.
        """
        if not selected_rects:
            return
        
        # Get directory to save files
        dir_path = QFileDialog.getExistingDirectory(
            self.sprite_tree,
            "Select Export Directory"
        )
        
        if not dir_path:
            return
        
        # Export each selected sprite
        for i, rect in enumerate(selected_rects):
            pixmap = self.tree_manager._extract_sprite_from_canvas(rect.x(), rect.y(), 
                                                     rect.width(), rect.height())
            if pixmap and not pixmap.isNull():
                file_name = f"sprite_{i:03d}.png"
                file_path = os.path.join(dir_path, file_name)
                pixmap.save(file_path, "PNG")

    def _extract_and_save_sprite(self, x, y, width, height):
        """
        Extract the sprite at the given canvas coordinates and prompt the user to save it to a file.
        
        Prompts a Save File dialog with a default name based on the coordinates and size. If the user selects a path and a valid sprite image exists at the specified rectangle, saves the image as PNG by default or as JPEG when the filename ends with `.jpg`/`.jpeg` (JPEG saved with 90% quality). If the dialog is cancelled or no valid image is found, no file is written.
        
        Parameters:
            x (int): X coordinate of the top-left corner of the sprite on the canvas.
            y (int): Y coordinate of the top-left corner of the sprite on the canvas.
            width (int): Width of the sprite to extract.
            height (int): Height of the sprite to extract.
        """
        # Get save path
        default_name = f"sprite_{x}_{y}_{width}x{height}.png"
        path, _ = QFileDialog.getSaveFileName(
            self.sprite_tree,
            "Save Sprite",
            default_name,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*.*)"
        )
        
        if path:
            pixmap = self.tree_manager._extract_sprite_from_canvas(x, y, width, height)
            if pixmap and not pixmap.isNull():
                if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
                    pixmap.save(path, "JPEG", 90)
                else:
                    pixmap.save(path, "PNG")

    def _copy_sprite_to_clipboard(self, item):
        """
        Copy a sprite's original pixmap to the system clipboard.
        
        If `item` is None, represents a group, or has no valid original pixmap, the function returns without action.
        On success, the item's pixmap is placed on the application clipboard and a status bar message is shown for 3 seconds.
        
        Parameters:
            item: Tree item representing a sprite. Must not be a group and should implement `get_original_pixmap()` which returns a valid QPixmap.
        """
        if not item or self.tree_manager._is_group_item(item):
            return
        
        if hasattr(item, 'get_original_pixmap'):
            pixmap = item.get_original_pixmap()
            if pixmap and not pixmap.isNull():
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setPixmap(pixmap)
                
                # Show notification
                self.main_window.statusBar().showMessage(f"Copied '{item.text(0)}' to clipboard", 3000)

    def _collect_sprite_items(self, item, result_list):
        """
        Collects all non-group sprite items under a tree item and appends them to result_list.
        
        Traverses the tree rooted at `item` recursively; when a non-group sprite item is encountered it is appended to `result_list` in traversal order. The function modifies `result_list` in place.
        
        Parameters:
            item: The tree item to traverse; traversal does nothing if falsy.
            result_list: A list to which found sprite items will be appended.
        """
        if not item:
            return
        
        if not self.tree_manager._is_group_item(item):
            result_list.append(item)
        else:
            for i in range(item.childCount()):
                child = item.child(i)
                self._collect_sprite_items(child, result_list)

    def _collect_sprite_pixmaps(self, item, result_list):
        """
        Collects and appends all non-group sprite QPixmap objects from the given tree item and its descendants into result_list.
        
        Parameters:
            item: The tree item to search; may be a group or a single sprite item. If falsy, the function returns without modifying result_list.
            result_list (list): Mutable list that will be extended with found QPixmap objects.
        """
        if not item:
            return
        
        if not self.tree_manager._is_group_item(item):
            if hasattr(item, 'get_original_pixmap'):
                pixmap = item.get_original_pixmap()
                if pixmap and not pixmap.isNull():
                    result_list.append(pixmap)
        else:
            for i in range(item.childCount()):
                child = item.child(i)
                self._collect_sprite_pixmaps(child, result_list)

    def _qimage_to_pil(self, qimage):
        """
        Convert a QImage to a PIL Image in RGBA mode.
        
        Parameters:
            qimage: QImage instance to convert.
        
        Returns:
            A PIL Image in 'RGBA' mode if conversion and required libraries (Pillow and numpy) are available, `None` if the Pillow or numpy imports fail.
        """
        try:
            from PIL import Image
            import numpy as np
            
            # Convert QImage to numpy array
            size = qimage.size()
            s = qimage.bits().asstring(size.width() * size.height() * 4)
            arr = np.frombuffer(s, dtype=np.uint8).reshape((size.height(), size.width(), 4))
            
            # Convert to PIL Image (RGBA)
            return Image.fromarray(arr, 'RGBA')
        except ImportError:
            return None