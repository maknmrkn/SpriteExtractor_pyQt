import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from .threading_utils import Worker
from PyQt6.QtCore import QThreadPool
import logging


class ExportOperations:
    def __init__(self, tree_manager):
        """
        Create an ExportOperations instance bound to a tree manager.
        
        Parameters:
            tree_manager: The tree manager that provides access to the sprite tree and the application's main_window. Stored as `self.tree_manager`; its `main_window` is cached as `self.main_window` for dialogs and status updates. The instance also acquires a global `QThreadPool` and configures a module logger for background tasks and reporting.
        """
        self.tree_manager = tree_manager
        self.main_window = tree_manager.main_window
        self.thread_pool = QThreadPool.globalInstance()
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
                self.logger.error(f"Failed to save sprite: {str(e)}")
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
        
        # Create a worker to handle the export in a background thread
        worker = Worker(self._export_group_impl, group_item, dir_path)
        worker.signals.finished.connect(self._export_group_success)
        worker.signals.error.connect(self._export_group_error)
        self.thread_pool.start(worker)

    def _export_group_impl(self, group_item, dir_path, progress_callback=None):
        """
        Export all non-group child sprites of the given group item to image files in the specified directory.
        
        Intended to run in a background thread; iterates the group's direct children, skips subgroup items, obtains each child's original QPixmap (if available), and saves each valid pixmap to a file in dir_path using the child's text as the filename (PNG by default, JPEG at 90% quality when the filename ends with .jpg/.jpeg).
        
        Parameters:
        	group_item: The tree item representing a group; only its direct (non-group) children are exported.
        	dir_path: The directory path where exported image files will be written.
        :param progress_callback:
        	progress_callback (callable, optional): Optional callback for progress updates (not required).
        
        Returns:
        	result_message (str): A success message describing the exported group when the operation completes.
        """
        try:
            self.logger.info(f"Starting export of group '{group_item.text(0)}' to {dir_path}")
            
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
                    success = pixmap.save(file_path, "JPEG", 90)  # 90% quality for JPEG
                else:
                    success = pixmap.save(file_path, "PNG")
                
                if not success:
                    self.logger.warning(f"Failed to save {file_path}")
            
            self.logger.info(f"Successfully exported group '{group_item.text(0)}'")
            return f"Group '{group_item.text(0)}' exported successfully"
        except Exception as e:
            self.logger.error(f"Error during group export: {str(e)}")
            raise e

    def _export_group_success(self, result):
        """
        Handle a successful group export by notifying the UI and logging the outcome.
        
        Parameters:
            result (str): Message describing the successful export; shown in the main window's status bar and written to the logger.
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage(result, 3000)

    def _export_group_error(self, error_info):
        """
        Handle an error that occurred during a group export by logging and notifying the user.
        
        Parameters:
            error_info (tuple): A tuple (exc_type, value, traceback_str) describing the error; `value` is the exception instance whose message is shown to the user.
        """
        _exctype, value, _tb_str = error_info
        self.logger.error(f"Failed to export group: {str(value)}")
        self.main_window.statusBar().showMessage(f"Failed to export group: {str(value)}", 5000)
        # Show error in a message box as well
        QMessageBox.critical(self.sprite_tree, "Error", f"Failed to export group: {str(value)}")

    def _export_group_as_gif(self, group_item):
        """
        Export the specified group as an animated GIF by prompting the user for a destination file and running the export in a background thread.
        
        Prompts the user to choose a GIF file path; if a path is chosen, starts a background worker that collects the group's sprite frames, converts them to images, and writes an animated GIF. If the item is not a group, the user cancels, or the group contains no sprites, no action is taken and no error is raised.
        
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
        
        # Create a worker to handle the GIF export in a background thread
        worker = Worker(self._export_group_as_gif_impl, group_item, path)
        worker.signals.finished.connect(self._export_gif_success)
        worker.signals.error.connect(self._export_gif_error)
        self.thread_pool.start(worker)

    def _export_group_as_gif_impl(self, group_item, path, progress_callback=None):
        """
        Export all non-group sprite children of `group_item` as an animated GIF saved to `path`.
        
        Collects sprite pixmaps from the provided group, converts them to PIL Images, and writes an animated GIF (100 ms frame duration, looping). If no sprite pixmaps or no valid images are found, returns a descriptive message instead of creating a file.
        
        Parameters:
            group_item: A tree item representing the group whose descendant sprite items will be exported.
            path (str): Filesystem path where the animated GIF will be written.
            progress_callback (callable, optional): Optional callable to receive progress updates (implementation may call with a numeric progress value).
        
        Returns:
            str: A human-readable result message. Examples:
                - "GIF exported successfully to:\n{path}" on success,
                - "No sprites found for GIF export" if the group contains no sprites,
                - "No valid images found for GIF export" if conversion fails for all images.
        
        Raises:
            ImportError: If the Pillow library is not available.
            Exception: Re-raises unexpected errors that occur during processing.
        """
        try:
            self.logger.info(f"Starting GIF export of group '{group_item.text(0)}' to {path}")
            
            # Collect all sprite pixmaps
            sprite_pixmaps = []
            self.tree_manager._collect_sprite_pixmaps(group_item, sprite_pixmaps)
            
            if not sprite_pixmaps:
                self.logger.warning("No sprites found for GIF export")
                return "No sprites found for GIF export"
            
            # Save as GIF (you might need to implement GIF saving)
            try:
                # Convert QPixmap to QImage and save
                images = []
                for _, pixmap in enumerate(sprite_pixmaps):
                    image = pixmap.toImage()
                    if not image.isNull():
                        # Convert to PIL Image
                        pil_image = self._qimage_to_pil(image)
                        if pil_image:
                            images.append(pil_image)
                
                if images:
                    images[0].save(path, save_all=True, append_images=images[1:], 
                                 duration=100, loop=0)
                    
                    self.logger.info(f"GIF exported successfully to {path}")
                    return f"GIF exported successfully to:\n{path}"
                else:
                    self.logger.warning("No valid images found for GIF export")
                    return "No valid images found for GIF export"
            except ImportError:
                error_msg = "PIL (Pillow) library is required for GIF export."
                self.logger.error(error_msg)
                raise ImportError(error_msg)
        except Exception as e:
            self.logger.error(f"Error during GIF export: {str(e)}")
            raise e

    def _export_gif_success(self, result):
        """
        Notify the user and log a message when a GIF export completes successfully.
        
        Parameters:
            result (str): Human-readable success message (for example, the output file path or confirmation text).
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage("GIF exported successfully", 3000)
        QMessageBox.information(self.sprite_tree, "Success", result)

    def _export_gif_error(self, error_info):
        """
        Handle an error raised during GIF export.
        
        Parameters:
            error_info (tuple): A tuple (exc_type, value, tb_str) describing the exception; `value` is the exception instance.
        
        Description:
            Logs the error, shows the error message in the main window status bar for 5 seconds, and displays a warning dialog informing the user that the Pillow library is required for GIF export.
        """
        _exctype, value, _tb_str = error_info
        self.logger.error(f"Failed to export GIF: {str(value)}")
        self.main_window.statusBar().showMessage(f"Failed to export GIF: {str(value)}", 5000)
        QMessageBox.warning(self.sprite_tree, "Error", f"PIL (Pillow) library is required for GIF export.")

    def _export_selected_sprites(self, selected_rects):
        """
        Export the sprites encompassed by the given canvas rectangles to PNG files in a user-selected directory.
        
        Prompts the user to choose a target directory; if a directory is selected, schedules a background worker that extracts each rectangle from the canvas and saves valid pixmaps as files named `sprite_000.png`, `sprite_001.png`, etc. If `selected_rects` is empty or the directory selection is cancelled, no action is taken. Invalid or null pixmaps are skipped. The worker's completion and error signals are connected to the class's success and error handlers.
        
        Parameters:
            selected_rects (iterable): An iterable of rectangle-like objects exposing `x()`, `y()`, `width()`, and `height()` methods that define the regions to export.
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

        # Create a worker to handle the export in a background thread
        worker = Worker(self._export_selected_sprites_impl, selected_rects, dir_path)
        worker.signals.finished.connect(self._export_selected_success)
        worker.signals.error.connect(self._export_selected_error)
        self.thread_pool.start(worker)

    def _export_selected_sprites_impl(self, selected_rects, dir_path, progress_callback=None):
        """
        Export sprites defined by a sequence of rectangles to PNG files in the given directory.
        
        Iterates over `selected_rects`, extracts each sprite from the canvas using the tree manager, and saves valid pixmaps as files named `sprite_000.png`, `sprite_001.png`, ... in `dir_path`. Invalid or null pixmaps are skipped and a warning is logged for any failed save operations. Returns a short success message when complete.
        
        Parameters:
            selected_rects (Iterable): Sequence of rectangle-like objects with `x()`, `y()`, `width()`, and `height()` methods specifying sprite regions.
            dir_path (str): Destination directory path where exported PNG files will be written.
            progress_callback (callable, optional): Ignored by this implementation; present for compatibility with worker progress reporting.
        
        Returns:
            str: A brief success message indicating how many sprites were exported.
        
        Raises:
            Exception: Propagates any exception raised during extraction or file saving.
        """
        try:
            self.logger.info(f"Starting export of {len(selected_rects)} selected sprites to {dir_path}")
            
            # Export each selected sprite
            for i, rect in enumerate(selected_rects):
                pixmap = self.tree_manager._extract_sprite_from_canvas(rect.x(), rect.y(), 
                                                         rect.width(), rect.height())
                if pixmap and not pixmap.isNull():
                    file_name = f"sprite_{i:03d}.png"
                    file_path = os.path.join(dir_path, file_name)
                    success = pixmap.save(file_path, "PNG")
                    if not success:
                        self.logger.warning(f"Failed to save {file_path}")
            
            self.logger.info(f"Successfully exported {len(selected_rects)} sprites")
            return f"Exported {len(selected_rects)} sprites successfully"
        except Exception as e:
            self.logger.error(f"Error during selected sprites export: {str(e)}")
            raise e

    def _export_selected_success(self, result):
        """
        Handle successful export of selected sprites by logging the result and displaying it in the main window's status bar.
        
        Parameters:
            result (str): Message describing the export outcome to display.
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage(result, 3000)

    def _export_selected_error(self, error_info):
        """
        Handle an error that occurred while exporting selected sprites by logging the failure and notifying the user via the main window's status bar.
        
        Parameters:
            error_info (tuple): A tuple of (exception type, exception value, traceback string) describing the error.
        """
        _exctype, value, _tb_str = error_info
        self.logger.error(f"Failed to export selected sprites: {str(value)}")
        self.main_window.statusBar().showMessage(f"Failed to export selected sprites: {str(value)}", 5000)

    def _extract_and_save_sprite(self, x, y, width, height):
        """
        Extract the sprite at the given canvas coordinates and prompt the user to save it to a file.
        
        Prompts a Save File dialog with a default name based on the coordinates and size. If the user selects a path and a valid sprite image exists at the specified rectangle, saves the image as PNG by default or as JPEG when the filename ends with `.jpg`/`.jpeg` (JPEG saved with 90% quality). If the dialog is cancelled or no valid image is found, no file is written.
        
        Parameters:
            x (int): X coordinate of the top-left corner of the sprite on the canvas.
            y (int): Y coordinate of the top-left corner of the canvas.
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
        
        Traverses the tree rooted at `item` recursively; when a non-group sprite item is encountered it is appended to `result_list` in traversal order.
        
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