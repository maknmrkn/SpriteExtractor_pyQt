from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QPaintDevice
from PyQt6.QtCore import Qt, QRect, pyqtSignal


class Canvas(QScrollArea):
    # Signal emitted when a region is selected (future use)
    selection_changed = pyqtSignal(QRect)

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
