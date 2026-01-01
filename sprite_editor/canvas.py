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

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setWidget(self.image_label)
        
        self.pixmap = QPixmap()
        self.scale_factor = 1.0

        # Grid settings - now with separate X and Y
        self.show_grid = False
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

    def load_image(self, image_path: str):
        """Load an image from file path."""
        self.pixmap = QPixmap(image_path)
        if not self.pixmap.isNull():
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
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter)
        
        # Highlight selected cell if exists
        if self.selected_cell_rect:
            highlight_pen = QPen(QColor(255, 255, 0), 2)  # Yellow highlight
            highlight_pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(highlight_pen)
            painter.drawRect(self.selected_cell_rect)
        
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
    
    def mousePressEvent(self, event):
        """Handle mouse clicks to detect grid cell selection."""
        pos = event.pos()
        # Account for any scrolling in the QScrollArea
        scroll_x = self.horizontalScrollBar().value()
        scroll_y = self.verticalScrollBar().value()
        # Adjust position relative to image
        x = pos.x() + scroll_x - self.image_label.x()
        y = pos.y() + scroll_y - self.image_label.y()
        
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
            self.selected_cell_rect = QRect(int(cell_x), int(cell_y), 
                                           self.grid_width, self.grid_height)
            
            # Update display to show highlight
            self.update_display()
            
            # Emit signal with cell coordinates for both clicks
            self.grid_cell_clicked.emit(int(cell_x), int(cell_y), 
                                       self.grid_width, self.grid_height)
            
            # Only show context menu for right-click
            if event.button() == Qt.MouseButton.RightButton:
                # Emit right-click signal to show group selection dialog
                self.grid_cell_right_clicked.emit(int(cell_x), int(cell_y), 
                                                 self.grid_width, self.grid_height)

    def _show_context_menu(self, position, cell_x, cell_y):
        """Show context menu for grid cell."""
        menu = QMenu(self)
        menu.addAction("Move to Group", lambda: self._handle_move_to_group(cell_x, cell_y))
        menu.exec(self.mapToGlobal(position))

    def _handle_move_to_group(self, cell_x, cell_y):
        """Emit signal to notify main window to show group selection dialog."""
        # This method is now just a placeholder since the signal is emitted in mousePressEvent
        # when the right-click is detected
        pass

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