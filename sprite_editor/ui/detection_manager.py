from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog


class DetectionManager:
    """
    Manages sprite detection functionality for the main window.
    """
    def __init__(self, main_window):
        self.main_window = main_window

    def _toggle_auto_detect_mode(self, checked):
        """
        Switch the editor between auto-detection mode and grid mode.
        
        When enabling auto-detection, the grid is disabled, the canvas is put into auto-detect mode, and the status bar is updated. When disabling auto-detection, the grid is enabled, the canvas exits auto-detect mode, and the status bar is updated.
        
        Parameters:
            checked (bool): If True, enable auto-detection mode; if False, enable grid mode.
        """
        if checked:
            # Switch to auto-detection mode
            self.main_window.show_grid_toggle.setChecked(False)  # Disable grid mode
            self.main_window._on_grid_toggled(False)  # Update canvas
            self.main_window.canvas.in_autodetect_mode = True
            self.main_window.statusBar().showMessage("Auto-detection mode enabled")
        else:
            # Switch back to grid mode
            self.main_window.show_grid_toggle.setChecked(True)  # Enable grid mode
            self.main_window._on_grid_toggled(True)  # Update canvas
            self.main_window.canvas.in_autodetect_mode = False
            self.main_window.statusBar().showMessage("Grid mode enabled")

    def _auto_detect_frames(self):
        """
        Initiate sprite-frame detection for the currently loaded image.
        
        If no image is loaded, updates the status bar and returns. If the image is loaded but its file path is unavailable, updates the status bar and returns. Otherwise, reads minimum width/height from the UI controls, puts the UI into auto-detection state, starts detection in the background, and updates the status bar to "Detecting sprites...".
        """
        if not self.main_window.canvas.pixmap or self.main_window.canvas.pixmap.isNull():
            self.main_window.statusBar().showMessage("No image loaded to detect frames from.")
            return

        # Get min dimensions from spinboxes
        min_width = self.main_window.min_width_spinbox.value()
        min_height = self.main_window.min_height_spinbox.value()

        # Disable grid while detecting sprites
        self.main_window.show_grid_toggle.setChecked(False)
        self.main_window.canvas.show_grid = False
        self.main_window.canvas.in_autodetect_mode = True
        self.main_window.auto_detect_toggle.setChecked(True)  # Enable auto-detect mode
        self.main_window.canvas.update_display()

        # Show busy message
        self.main_window.statusBar().showMessage("Detecting sprites...")

        # Start async detection
        if hasattr(self.main_window.canvas, 'current_path') and self.main_window.canvas.current_path:
            # Connect the finished signal to our handler
            self.main_window.sprite_detector.finished.connect(self.main_window._on_detection_finished)
            # Start detection in background thread
            self.main_window.sprite_detector.start_detection(self.main_window.canvas.current_path, min_width, min_height)
        else:
            self.main_window.statusBar().showMessage("Could not detect sprites: image path not available.")

    def _on_detection_finished(self, detected_sprites):
        """
        Apply the results of a completed sprite-detection run to the canvas and update UI state.
        
        If `detected_sprites` contains rectangles, clear current selections and detections, store the detected rectangles on the canvas, refresh the canvas display, and show a status message with the number of detected sprites and next steps. If `detected_sprites` is empty or None, update the status to indicate that no sprites were detected.
        
        Parameters:
            detected_sprites (list[QRect] | None): List of QRect objects representing detected sprite frames, or None if detection produced no results.
        """
        if detected_sprites:
            # Clear any existing selections and detections
            self.main_window.canvas.selected_cells = []
            self.main_window.canvas.detected_sprites = []
            
            # Add detected sprites to the canvas as detected (not selected)
            for rect in detected_sprites:
                self.main_window.canvas.detected_sprites.append(rect)
            
            # Update canvas display
            self.main_window.canvas.update_display()
            
            # Don't add to tree automatically - just show on canvas
            self.main_window.statusBar().showMessage(f"Auto-detected {len(detected_sprites)} sprites. Click on them to work with them.")
        else:
            self.main_window.statusBar().showMessage("No sprites detected in the image.")

    def _clear_detections(self):
        """
        Clear all auto-detected sprite rectangles from the canvas and update the UI.
        
        Removes detected selections, refreshes the canvas display, and sets the status bar message to confirm the action.
        """
        self.main_window.canvas.selected_cells = []
        self.main_window.canvas.update_display()
        self.main_window.statusBar().showMessage("Cleared all detections.")

    def open_file(self):
        """
        Open an image file into the canvas and update UI state.
        
        If a file is selected and successfully loaded, updates the status bar with the file path, adds the default sprites group to the sprite tree, and makes the auto-detect toolbar visible. If loading fails, shows an error message in the status bar. If the dialog is cancelled, no changes are made.
        """
        path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Sprite Sheet",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            if self.main_window.canvas.load_image(path):
                self.main_window.statusBar().showMessage(f"Loaded: {path}")
                # Add a default group with individual sprite items when image is loaded
                self.main_window.tree_manager._add_default_sprites_group()
                
                # Show the auto-detect toolbar
                self.main_window.auto_detect_toolbar.setVisible(True)
            else:
                self.main_window.statusBar().showMessage("Failed to load image.")