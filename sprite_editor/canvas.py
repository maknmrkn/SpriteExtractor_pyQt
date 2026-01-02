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
        """Load an image from file path."""
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
            self.current_path = image_path  # Store the path for sprite detection
            self.update_display()
            return True
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
        """Draw detected sprites as rectangles"""
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
        """Handle mouse clicks to detect grid cell selection."""
        pos = event.pos()
        # Account for any scrolling in the QScrollArea
        scroll_x = self.horizontalScrollBar().value()
        scroll_y = self.verticalScrollBar().value()
        # Adjust position relative to image
        x = pos.x() + scroll_x - self.image_label.x()
        y = pos.y() + scroll_y - self.image_label.y()
        
        print(f"DEBUG: mousePressEvent at ({x}, {y}), modifiers: {event.modifiers()}, in_autodetect_mode: {self.in_autodetect_mode}")
        
        # In auto-detection mode, handle clicks differently
        if self.in_autodetect_mode:
            # Check if the click is on a detected sprite rectangle
            clicked_rect = None
            for rect in self.detected_sprites:
                if rect.contains(x, y):
                    clicked_rect = rect
                    break
            
            print(f"DEBUG: clicked_rect is {clicked_rect}, total detected_sprites: {len(self.detected_sprites)}, total selected_cells: {len(self.selected_cells)}")
            
            if clicked_rect:
                # Toggle selection in multi-selection list if Ctrl is pressed
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    print("DEBUG: Control key is pressed - toggling selection")
                    if clicked_rect in self.selected_cells:
                        # If it's in the selection, remove it
                        self.selected_cells.remove(clicked_rect)
                        print(f"DEBUG: Removed rect from selection, now {len(self.selected_cells)} selected")
                    else:
                        # If it's not in the selection, add it
                        self.selected_cells.append(clicked_rect)
                        print(f"DEBUG: Added rect to selection, now {len(self.selected_cells)} selected")
                    
                    # Update display to show highlights
                    self.update_display()
                    
                    # Emit multi-selection signal if right-clicking or if we have multiple selected
                    if event.button() == Qt.MouseButton.RightButton and len(self.selected_cells) > 0:
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        self.multi_grid_selection.emit(all_coords)
                else:
                    # Single selection - just highlight the clicked sprite
                    if event.button() == Qt.MouseButton.LeftButton:
                        # Don't clear other sprites, just set this one as the current selection
                        self.selected_cell_rect = clicked_rect
                        
                        # Update display to show highlights
                        self.update_display()
                        
                        # Emit grid_cell_clicked for the selected rectangle
                        print(f"DEBUG: Emitting grid_cell_clicked for auto-detected rect at ({clicked_rect.x()}, {clicked_rect.y()}, {clicked_rect.width()}x{clicked_rect.height()})")
                        self.grid_cell_clicked.emit(
                            clicked_rect.x(), 
                            clicked_rect.y(), 
                            clicked_rect.width(), 
                            clicked_rect.height()
                        )
                    elif event.button() == Qt.MouseButton.RightButton:
                        # Right click on detected sprite - emit the signal for single sprite
                        print(f"DEBUG: Emitting grid_cell_right_clicked for auto-detected rect at ({clicked_rect.x()}, {clicked_rect.y()}, {clicked_rect.width()}x{clicked_rect.height()})")
                        self.grid_cell_right_clicked.emit(
                            clicked_rect.x(), 
                            clicked_rect.y(), 
                            clicked_rect.width(), 
                            clicked_rect.height()
                        )
            else:
                print("DEBUG: Clicked outside detected sprites")
                # Clicked outside detected sprites
                if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    # Clear the current selection highlight if not using Ctrl
                    self.selected_cell_rect = None
                    print("DEBUG: Cleared selected_cell_rect")
                    self.update_display()
                
                # Handle right-click outside detected sprites
                if event.button() == Qt.MouseButton.RightButton and len(self.selected_cells) > 0:
                    # If we have multi-selection and right-click outside detected sprites, emit multi-selection
                    all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                    # Emit multi-selection signal with all coordinates
                    self.multi_grid_selection.emit(all_coords)
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
                
                # Check if Ctrl key is pressed for multi-selection
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Toggle selection in multi-selection list
                    if clicked_rect in self.selected_cells:
                        self.selected_cells.remove(clicked_rect)
                    else:
                        self.selected_cells.append(clicked_rect)
                    
                    # Update display to show highlights
                    self.update_display()
                    
                    # If right-clicking during multi-selection, emit multi-selection signal
                    if event.button() == Qt.MouseButton.RightButton and len(self.selected_cells) > 0:
                        # Calculate the coordinates for all selected cells
                        all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                        
                        # Emit multi-selection signal with all coordinates
                        self.multi_grid_selection.emit(all_coords)
                else:
                    # Single selection - clear multi-selection if not right-clicking
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.selected_cells = [clicked_rect]  # Select only this cell
                        # Update display to show highlight
                        self.update_display()
                        
                        # Only emit grid_cell_clicked for left clicks (for highlighting)
                        print(f"DEBUG: Emitting grid_cell_clicked for left click at ({int(cell_x)}, {int(cell_y)}, {self.grid_width}x{self.grid_height})")
                        self.grid_cell_clicked.emit(int(cell_x), int(cell_y), 
                                                   self.grid_width, self.grid_height)
                    
                    # For right click, check if we have multi-selection
                    elif event.button() == Qt.MouseButton.RightButton:
                        if len(self.selected_cells) > 0:
                            # If we have multi-selection, right-click should use the multi-selection
                            all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                            
                            # Emit multi-selection signal with all coordinates
                            self.multi_grid_selection.emit(all_coords)
                        else:
                            # If no multi-selection, emit single cell right-click
                            print(f"DEBUG: Emitting grid_cell_right_clicked for right click at ({int(cell_x)}, {int(cell_y)}, {self.grid_width}x{self.grid_height})")
                            # Emit right-click signal to show group selection dialog
                            self.grid_cell_right_clicked.emit(int(cell_x), int(cell_y), 
                                                             self.grid_width, self.grid_height)
            else:
                # Click was outside any grid cell
                if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    # Clear selections only if Ctrl is not pressed
                    self.selected_cell_rect = None
                    self.selected_cells = []
                    self.update_display()
                
                # Handle right-click outside grid cells
                if event.button() == Qt.MouseButton.RightButton and len(self.selected_cells) > 0:
                    # If we have multi-selection and right-click outside grid, use multi-selection
                    all_coords = [(rect.x(), rect.y(), rect.width(), rect.height()) for rect in self.selected_cells]
                    
                    # Emit multi-selection signal with all coordinates
                    self.multi_grid_selection.emit(all_coords)
    def _draw_grid(self, painter: QPainter):
        """Draw a grid overlay as separate cells with spacing between them, creating a Unity-like sprite editor appearance."""
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