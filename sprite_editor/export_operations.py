import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt


class ExportOperations:
    def __init__(self, tree_manager):
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window

    @property
    def sprite_tree(self):
        return self.tree_manager.sprite_tree

    def _export_sprite(self, item):
        """Export a single sprite to file."""
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
        """Export all sprites in a group to individual files."""
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
        """Export group as animated GIF."""
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
        """Export selected sprites from canvas."""
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
        """Extract and save a sprite from coordinates."""
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
        """Copy sprite to clipboard."""
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
        """Recursively collect all sprite items from a tree item."""
        if not item:
            return
        
        if not self.tree_manager._is_group_item(item):
            result_list.append(item)
        else:
            for i in range(item.childCount()):
                child = item.child(i)
                self._collect_sprite_items(child, result_list)

    def _collect_sprite_pixmaps(self, item, result_list):
        """Recursively collect all sprite pixmaps from a tree item."""
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
        """Convert QImage to PIL Image."""
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