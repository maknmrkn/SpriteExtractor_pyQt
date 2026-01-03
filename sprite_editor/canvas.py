from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy, QMenu
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QPaintDevice
from PyQt6.QtCore import Qt, QRect, pyqtSignal


class Canvas(QScrollArea):
    # Signal emitted when a region is selected (future use)
    selection_changed = pyqtSignal(QRect)
    # Signal emitted when a grid cell is clicked (for sprite extraction)
    grid_cell_clicked = pyqtSignal(int, int, int, int)  # x, y, width, height
    # Signal emitted when right-click occurs on a grid cell
    grid_cell_right_clicked = pyqtSignal(int, int, int, int)  # x, y, width, height
    # Signal emitted when multiple grid cells are selected
    multi_grid_selection = pyqtSignal(list)  # List of (x, y, width, height) tuples

    def __init__(self, parent=None):
        """
        Initialize the Canvas scroll area with its image label, display state, grid configuration, and selection/autodetect state.
        
        Sets up the inner QLabel used to display images, default visual properties (pixmap, scale factor, background color), grid parameters (separate X/Y cell size, padding, spacing, line style, and color), selection storage for single and multiple selections, the list of auto-detected sprite rectangles, an autodetect mode flag, and enables the custom context menu policy.
        """
        super().__init__(parent)
        
        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setWidget(self.image_label)
        
        self.pixmap = QPixmap()
        self.scale_factor = 1.0
        self.current_path = None  # Store the current image path

        # Grid settings - now with separate X and Y
        self.show_grid = True  # Default to showing grid
        self.grid_width = 32
        self.grid_height = 32
        self.padding_x = 0
        self.padding_y = 0
        self.spacing_x = 0
        self.spacing_y = 0
        self.line_style = "Dotted"  # or "Solid"
        self.grid_color = QColor(0, 255, 0, 100)  # Semi-transparent green
        self.background_color = QColor(25, 25, 25)  # Dark gray background
        
        # Currently selected cell
        self.selected_cell_rect = None
        # Multiple selected cells for multi-selection
        self.selected_cells = []
        # All detected sprites (these will always be shown on canvas when in auto-detect mode)
        self.detected_sprites = []
        
        # Auto-detection mode flag
        self.in_autodetect_mode = False
        
        # Enable multiple selection by default
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def load_image(self, image_path: str):
        """
        Load an image from the given filesystem path into the canvas.
        
        On success this sets the canvas pixmap, stores the path in `current_path`, updates the display, and prepares the image for sprite detection. If loading fails no state is changed other than ensuring no valid pixmap is set.
        
        Parameters:
            image_path (str): Filesystem path to the image file to load.
        
        Returns:
            bool: `True` if the image was loaded and displayed, `False` otherwise.
        """
        try:
            self.pixmap = QPixmap(image_path)
            if not self.pixmap.isNull():
                self.current_path = image_path  # Store the path for sprite detection
                self.update_display()
                return True
            return False
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def update_display(self):
        """Update the displayed pixmap and draw grid if enabled."""
        if self.pixmap.isNull():
            self.image_label.clear()
            return
        
        # Create a new pixmap for drawing
        display_pixmap = QPixmap(self.pixmap.size())
        display_pixmap.fill(self.background_color)
        
        painter = QPainter(display_pixmap)
        painter.drawPixmap(0, 0, self.pixmap)
        
        # Draw grid if enabled and not in auto-detection mode
        if self.show_grid and not self.in_autodetect_mode:
            self._draw_grid(painter)
        elif self.in_autodetect_mode:
            # When in auto-detection mode, draw all detected sprites
            self._draw_detected_sprites(painter)
        
        # Highlight selected cell if exists
        if self.selected_cell_rect:
            highlight_pen = QPen(QColor(255, 255, 0), 2)  # Yellow highlight
            highlight_pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(highlight_pen)
            painter.drawRect(self.selected_cell_rect)
        
        # Highlight multiple selected cells
        multi_select_pen = QPen(QColor(0, 255, 255), 2)  # Cyan highlight for multi selection
        multi_select_pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(multi_select_pen)
        for rect in self.selected_cells:
            painter.drawRect(rect)
        
        painter.end()
        
        self.image_label.setPixmap(display_pixmap)
        self.image_label.resize(display_pixmap.size())
        self.image_label.adjustSize()
        
        # Reset scroll bars
        self.verticalScrollBar().setValue(0)
        self.horizontalScrollBar().setValue(0)
        
        # Adjust scroll area size
        self.widget().updateGeometry()
        self.updateGeometry()
    
    def _draw_detected_sprites(self, painter: QPainter):
        """
        Render all auto-detected sprite bounding rectangles onto the provided painter.
        
        Rectangles are drawn using the canvas's current grid color and configured line style.
        
        Parameters:
            painter (QPainter): The painter used to draw the rectangles onto the canvas.
        """
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        
        if self.line_style == "Dotted":
            pen.setStyle(Qt.PenStyle.DotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
            
        painter.setPen(pen)
        
        # Draw all detected sprite rectangles
        for rect in self.detected_sprites:
            painter.drawRect(rect)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events for both grid and autodetection interaction modes.
        
        Processes clicks relative to the displayed image, updating single or multi-selection state,
        clearing selections when appropriate, and emitting selection-related signals:
        - Emits `grid_cell_clicked(x, y, width, height)` on left-click of a single grid cell.
        - Emits `grid_cell_right_clicked(x, y, width, height)` on right-click for a single cell/sprite.
        - Emits `multi_grid_selection(list_of_rect_tuples)` when a right-click targets an existing multi-selection
          or when requesting a context menu for multiple selected regions.
        
        Behavior differs by mode:
        - In autodetect mode, clicks operate on `detected_sprites` rectangles.
        - In grid mode, clicks operate on the computed grid cells using padding, spacing, and cell size.
        Ctrl-modified left-clicks toggle membership in the multi-selection; unmodified left-clicks set a single selection.
        The method updates visual highlights by calling `update_display()` as needed.
        
        Parameters:
            event: QMouseEvent
                The mouse event reporting button, position, and modifiers.
        """
        pos = event.pos()
        # Account for any scrolling in the QScrollArea
        scroll_x = self.horizontalScrollBar().value()
        scroll_y = self.verticalScrollBar().value()
        # Adjust position relative to image
        x = pos.x() + scroll_x - self.image_label.x()
        y = pos.y() + scroll_y - self.image_label.y()
        
        # In auto-detection mode, handle clicks differently
        if self.in_autodetect_mode:
            # Check if the click is on a detected sprite rectangle
            clicked_rect = None
            for rect in self.detected_sprites:
                if rect.contains(x, y):
                    clicked_rect = rect
                    break
            
            if clicked_rect:
                # Handle left clicks for selection
                if event.button() == Qt.MouseButton.LeftButton:
                    # Toggle selection in multi-selection list if Ctrl is pressed
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        if clicked_rect in self.selected_cells:
                            # If it's in the selection, remove it
                            self.selected_cells.remove(clicked_rect)
                        else:
                            # If it's not in the selection, add it
                            self.selected_cells.append(clicked_rect)
                    else:
                        # Single selection - set clicked sprite as the only selection
                        self.selected_cells = [clicked_rect]
                    
                    # Update display to show highlights
                    self.update_display()
                
                # Handle right clicks for context menu
                elif event.button() == Qt.MouseButton.RightButton:
                    # Rule 1: Right click on a sprite that IS ALREADY in the current selection
                    # Do NOT change the selection, keep ALL selected sprites highlighted
                    if clicked_rect in self.selected_cells:
                        # Context menu will be shown for the entire selection
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        self.multi_grid_selection.emit(all_coords)
                    
                    # Rule 2: Right click on a sprite that is NOT in the current selection
                    else:
                        # Select ONLY the clicked sprite
                        self.selected_cells = [clicked_rect]
                        self.update_display()
                        
                        # Emit signal for single sprite context menu
                        self.grid_cell_right_clicked.emit(
                            clicked_rect.x(), 
                            clicked_rect.y(), 
                            clicked_rect.width(), 
                            clicked_rect.height()
                        )
            else:
                # Clicked outside detected sprites
                
                # Handle right-click outside detected sprites
                if event.button() == Qt.MouseButton.RightButton:
                    # Rule 3: Right click on empty space - do NOT modify selection
                    if len(self.selected_cells) > 0:
                        # If we have multi-selection, show context menu for the multi-selection
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        # Emit multi-selection signal with all coordinates
                        self.multi_grid_selection.emit(all_coords)
                    else:
                        # Just show the empty context menu (no change to selection)
                        pass  # No action needed, just keeping selection unchanged
                
                # For left clicks outside sprites, clear selection if not holding Ctrl
                elif event.button() == Qt.MouseButton.LeftButton:
                    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        # Clear the multi-selection and current selection highlight if not using Ctrl
                        self.selected_cells = []
                        self.selected_cell_rect = None
                        self.update_display()
        else:
            # Grid mode - existing functionality
            # Calculate grid cell coordinates
            grid_x = (x - self.padding_x) // (self.grid_width + self.spacing_x)
            grid_y = (y - self.padding_y) // (self.grid_height + self.spacing_y)
            
            # Calculate actual pixel coordinates of the cell
            cell_x = self.padding_x + grid_x * (self.grid_width + self.spacing_x)
            cell_y = self.padding_y + grid_y * (self.grid_height + self.spacing_y)
            
            # Check if the click was inside the actual grid cell (not in spacing area)
            if (x >= cell_x and x < cell_x + self.grid_width and 
                y >= cell_y and y < cell_y + self.grid_height):
                
                # Create a QRect for the selected cell
                clicked_rect = QRect(int(cell_x), int(cell_y), 
                                    self.grid_width, self.grid_height)
                
                # Handle left clicks for selection
                if event.button() == Qt.MouseButton.LeftButton:
                    # Check if Ctrl key is pressed for multi-selection
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        # Toggle selection in multi-selection list
                        if clicked_rect in self.selected_cells:
                            self.selected_cells.remove(clicked_rect)
                        else:
                            self.selected_cells.append(clicked_rect)
                    else:
                        # Single selection - set clicked cell as the only selection
                        self.selected_cells = [clicked_rect]
                    
                    # Update display to show highlights
                    self.update_display()
                    
                    # Only emit grid_cell_clicked for left clicks (for highlighting)
                    self.grid_cell_clicked.emit(int(cell_x), int(cell_y), 
                                               self.grid_width, self.grid_height)
                
                # Handle right clicks for context menu
                elif event.button() == Qt.MouseButton.RightButton:
                    # Rule 1: Right click on a cell that IS ALREADY in the current selection
                    # Do NOT change the selection, keep ALL selected sprites highlighted
                    if clicked_rect in self.selected_cells and len(self.selected_cells) > 1:
                        # Context menu will be shown for the entire selection
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        self.multi_grid_selection.emit(all_coords)
                    
                    # Rule 2: Right click on a cell that is NOT in the current selection
                    else:
                        # Select ONLY the clicked cell
                        self.selected_cells = [clicked_rect]
                        self.update_display()
                        
                        # Emit signal for single cell context menu
                        # Emit right-click signal to show group selection dialog
                        self.grid_cell_right_clicked.emit(int(cell_x), int(cell_y), 
                                                         self.grid_width, self.grid_height)
            else:
                # Click was outside any grid cell
                
                # Handle right-click outside grid cells
                if event.button() == Qt.MouseButton.RightButton:
                    # Rule 3: Right click on empty space - do NOT modify selection
                    if len(self.selected_cells) > 0:
                        # If we have multi-selection, show context menu for the multi-selection
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        # Emit multi-selection signal with all coordinates
                        self.multi_grid_selection.emit(all_coords)
                    else:
                        # Just show the empty context menu (no change to selection)
                        pass  # No action needed, just keeping selection unchanged
                
                # For left clicks outside grid cells, clear selection if not holding Ctrl
                elif event.button() == Qt.MouseButton.LeftButton:
                    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        # Clear selections only if Ctrl is not pressed
                        self.selected_cell_rect = None
                        self.selected_cells = []
                        self.update_display()

    def _draw_grid(self, painter: QPainter):
        """
        Draws the grid overlay across the image using the instance's grid dimensions, padding, spacing, color, and line style.
        
        Parameters:
            painter (QPainter): Painter to draw the grid onto the display pixmap.
        """
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        
        if self.line_style == "Dotted":
            pen.setStyle(Qt.PenStyle.DotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
            
        painter.setPen(pen)

        rect = self.pixmap.rect()
        
        # Draw grid cells as separate rectangles with spacing
        y = self.padding_y
        while y < rect.height():
            x = self.padding_x
            while x < rect.width():
                # Draw a rectangle for each cell
                cell_rect = QRect(x, y, self.grid_width, self.grid_height)
                painter.drawRect(cell_rect)
                x += self.grid_width + self.spacing_x
            y += self.grid_height + self.spacing_y