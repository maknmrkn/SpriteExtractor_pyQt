import cv2
import numpy as np
from PyQt6.QtCore import QRect, QObject, pyqtSignal
from .threading_utils import Worker, WorkerSignals
from PyQt6.QtCore import QThreadPool
import logging


class SpriteDetector(QObject):
    """
    A class for automatically detecting sprites in a sprite sheet image.
    """
    # Signal emitted when detection is finished
    finished = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_detection(self, image_path, min_width=8, min_height=8):
        """
        Start asynchronous sprite detection in a background thread.
        
        Args:
            image_path: Path to the sprite sheet image
            min_width: Minimum width of a sprite to be detected
            min_height: Minimum height of a sprite to be detected
        """
        # Create a worker for the detection task
        worker = Worker(self._detect_sprites_impl, image_path, min_width, min_height)
        worker.signals.finished.connect(self._on_detection_complete)
        worker.signals.error.connect(self._on_detection_error)
        self.thread_pool.start(worker)

    def _detect_sprites_impl(self, image_path, min_width=8, min_height=8):
        """
        Internal implementation of sprite detection that runs in a background thread.
        """
        try:
            self.logger.info(f"Starting sprite detection on {image_path}")
            # Load image with alpha channel if it exists
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            
            if img is None:
                self.logger.error(f"Could not load image from {image_path}")
                return []
            
            # Check if image has alpha channel
            if len(img.shape) == 3 and img.shape[2] == 4:
                # Use alpha channel to detect sprites
                alpha_channel = img[:, :, 3]
            else:
                # Convert to grayscale for processing
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Invert to make sprites white and background black
                _, alpha_channel = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            
            # Find contours in the alpha channel
            contours, _ = cv2.findContours(alpha_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_sprites = []
            for contour in contours:
                # Get bounding rectangle of the contour
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by minimum size
                if w >= min_width and h >= min_height:
                    detected_sprites.append(QRect(x, y, w, h))
            
            # Sort sprites by position (top to bottom, left to right)
            detected_sprites.sort(key=lambda r: (r.y(), r.x()))
            
            self.logger.info(f"Detection complete. Found {len(detected_sprites)} sprites.")
            return detected_sprites
        except Exception as e:
            self.logger.error(f"Error during sprite detection: {str(e)}")
            raise e

    def _on_detection_complete(self, result):
        """Handle completion of detection"""
        self.finished.emit(result)

    def _on_detection_error(self, error_info):
        """Handle errors during detection"""
        exctype, value, tb_str = error_info
        self.logger.error(f"An error occurred during sprite detection: {str(value)}")
        print(tb_str)
        # Emit empty result to avoid hanging the UI
        self.finished.emit([])

    def detect_sprites(self, image_path, min_width=8, min_height=8):
        """
        Detect sprites in an image by finding connected components or transparent boundaries.
        This is the synchronous version - for UI responsiveness, use start_detection with the finished signal instead.
        
        Args:
            image_path: Path to the sprite sheet image
            min_width: Minimum width of a sprite to be detected
            min_height: Minimum height of a sprite to be detected
            
        Returns:
            List of QRect objects representing detected sprite rectangles
        """
        return self._detect_sprites_impl(image_path, min_width, min_height)

    def detect_by_grid_pattern(self, image_path, min_width=8, min_height=8):
        """
        Alternative method to detect sprites by looking for grid-like patterns.
        Note: This is still a synchronous method, but it's not currently used in the main UI flow.
        
        Args:
            image_path: Path to the sprite sheet image
            min_width: Minimum width of a sprite to be detected
            min_height: Minimum height of a sprite to be detected
            
        Returns:
            List of QRect objects representing detected sprite rectangles
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return []
        
        # Threshold the image
        _, thresh = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)
        
        # Find horizontal and vertical lines to detect grid
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (thresh.shape[1]//2, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, thresh.shape[0]//2))
        
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Combine horizontal and vertical lines
        grid_lines = cv2.addWeighted(horizontal_lines, 1, vertical_lines, 1, 0.0)
        
        # Find contours of the grid cells
        contours, _ = cv2.findContours(grid_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_sprites = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            if w >= min_width and h >= min_height:
                detected_sprites.append(QRect(x, y, w, h))
        
        return detected_sprites