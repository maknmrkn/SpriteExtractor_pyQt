import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from .threading_utils import Worker, WorkerSignals
from PyQt6.QtCore import QThreadPool
import logging


class ExportOperations:
    def __init__(self, tree_manager):
        """
        Create an ExportOperations instance bound to the given tree manager.
        
        Parameters:
            tree_manager: The tree manager that provides access to the sprite tree and the application's main_window; stored as `self.tree_manager`. The initializer also caches `tree_manager.main_window` as `self.main_window` and acquires a global QThreadPool and logger for background work and logging.
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
        Export all non-group sprite items directly contained in `group_item` to image files in `dir_path`.
        
        Parameters:
            group_item: The tree group item whose direct (non-group) children will be exported. Must provide `.text(0)` for naming and optionally `get_original_pixmap()` for image data.
            dir_path (str): Destination directory path where image files will be written.
            progress_callback (callable, optional): Optional callback for progress updates; ignored if not provided.
        
        Returns:
            str: A human-readable success message for the exported group.
        
        Raises:
            Exception: Propagates any exception that occurs during the export process.
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
        Display a success message for a completed group export and record it in the log.
        
        Parameters:
            result (str): Message to log and show in the main window's status bar.
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage(result, 3000)

    def _export_group_error(self, error_info):
        """
        Handle an error raised during group export by reporting it to the UI and application log.
        
        Logs the exception message and displays it in the main window status bar and a critical message box.
        
        Parameters:
            error_info (tuple): Exception info tuple as (exc_type, value, traceback_str); the exception `value` is shown to the user.
        """
        exctype, value, tb_str = error_info
        self.logger.error(f"Failed to export group: {str(value)}")
        self.main_window.statusBar().showMessage(f"Failed to export group: {str(value)}", 5000)
        # Show error in a message box as well
        QMessageBox.critical(self.sprite_tree, "Error", f"Failed to export group: {str(value)}")

    def _export_group_as_gif(self, group_item):
        """
        Export the sprites in a group as an animated GIF file.
        
        Prompts the user for a destination GIF file and starts a background task to create an animated GIF from the group's sprite pixmaps. If the item is not a group or the user cancels the dialog, no action is taken.
        
        Parameters:
            group_item: Tree item representing the group to export.
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
        Export the given group's sprite frames as an animated GIF file.
        
        Collects all non-group sprite pixmaps from the provided group item, converts them to PIL Images, and saves them as an animated GIF at `path`. If no valid images are found, returns a short status message instead of writing a file.
        
        Parameters:
            group_item: The tree item representing a sprite group whose descendant sprites will be exported.
            path (str): The filesystem path where the resulting GIF will be written.
            progress_callback (callable, optional): Optional callback for progress updates; expected to accept a single numeric progress value.
        
        Returns:
            str: A status message describing the outcome. Examples include a success message with the output path, "No sprites found for GIF export", or "No valid images found for GIF export".
        
        Raises:
            ImportError: If the Pillow library is not available.
            Exception: Any unexpected error encountered during collection, conversion, or saving is re-raised.
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
                from PIL import Image
                images = []
                for i, pixmap in enumerate(sprite_pixmaps):
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
        Handle a successful GIF export by logging the result and notifying the user.
        
        Parameters:
            result (str): Success message to log and display to the user.
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage("GIF exported successfully", 3000)
        QMessageBox.information(self.sprite_tree, "Success", result)

    def _export_gif_error(self, error_info):
        """
        Handle an error that occurred during GIF export by logging the exception and notifying the user.
        
        Parameters:
            error_info (tuple): A tuple (exctype, value, tb_str) containing the exception type, exception value, and traceback string.
        """
        exctype, value, tb_str = error_info
        self.logger.error(f"Failed to export GIF: {str(value)}")
        self.main_window.statusBar().showMessage(f"Failed to export GIF: {str(value)}", 5000)
        QMessageBox.warning(self.sprite_tree, "Error", f"PIL (Pillow) library is required for GIF export.")

    def _export_selected_sprites(self, selected_rects):
        """
        Export canvas regions defined by selected rectangles to PNG files in a user-selected directory.
        
        If `selected_rects` is empty or no directory is chosen, no action is taken. Otherwise the method prompts the user to choose a target directory and dispatches a background worker that extracts each rectangle from the canvas and saves valid sprites as files named like `sprite_000.png`, `sprite_001.png`, etc.
        
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

        # Create a worker to handle the export in a background thread
        worker = Worker(self._export_selected_sprites_impl, selected_rects, dir_path)
        worker.signals.finished.connect(self._export_selected_success)
        worker.signals.error.connect(self._export_selected_error)
        self.thread_pool.start(worker)

    def _export_selected_sprites_impl(self, selected_rects, dir_path, progress_callback=None):
        """
        Export the given canvas rectangles as individual PNG files into the specified directory.
        
        Parameters:
            selected_rects (Iterable[QRect]): Iterable of QRect objects defining regions on the canvas to extract and save as separate sprite images.
            dir_path (str): Filesystem directory path where exported PNG files will be written.
            progress_callback (Optional[Callable[[int], None]]): Optional callable to report progress percentage; may be called with values 0–100.
        
        Returns:
            result (str): Summary message indicating how many sprites were exported, e.g. "Exported N sprites successfully".
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
        Handle a successful export of selected sprites by logging the result and showing it in the main window status bar.
        
        Parameters:
            result (str): Message describing the outcome of the export operation.
        """
        self.logger.info(result)
        self.main_window.statusBar().showMessage(result, 3000)

    def _export_selected_error(self, error_info):
        """
        Handle an error that occurred during export of selected sprites by logging the exception and showing an error message in the main window's status bar.
        
        Parameters:
            error_info (tuple): Exception information as (exc_type, value, traceback_str) where `value` is the exception instance or message used in the displayed/logged message.
        """
        exctype, value, tb_str = error_info
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
        Collect all non-group sprite items under the given tree item and append them to result_list.
        
        Traverses the subtree rooted at `item` recursively and appends each encountered non-group sprite item to `result_list` in traversal order.
        
        Parameters:
            item: The root tree item to traverse; no action if falsy.
            result_list: List to which found sprite items will be appended.
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