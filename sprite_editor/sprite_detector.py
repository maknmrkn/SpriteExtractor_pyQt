import cv2
from PyQt6.QtCore import QRect, QObject, pyqtSignal
from .threading_utils import Worker
from PyQt6.QtCore import QThreadPool
import logging


class SpriteDetector(QObject):
    """
    A class for automatically detecting sprites in a sprite sheet image.
    """
    # Signal emitted when detection is finished
    finished = pyqtSignal(object)
    
    def __init__(self):
        """
        Initialize the SpriteDetector: obtain a global QThreadPool instance and configure basic logging for the object.
        
        Sets self.thread_pool to the global QThreadPool instance and creates a logger stored in self.logger. Also configures the basic logging level to INFO.
        """
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

    def _detect_sprites_impl(self, image_path, min_width=8, min_height=8, progress_callback=None):
        """
        Detects sprites in the given image and returns their bounding rectangles.
        
        Parameters:
            image_path (str): Filesystem path to the input image.
            min_width (int): Minimum width in pixels for a detected sprite to be kept.
            min_height (int): Minimum height in pixels for a detected sprite to be kept.
            progress_callback (callable|None): Optional callable for progress updates (may be unused).
        
        Returns:
            list[QRect]: List of bounding rectangles for detected sprites, sorted top-to-bottom then left-to-right.
        
        Raises:
            Exception: Re-raises any exception encountered during image loading or processing.
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
        """
        Emit the finished signal with the detection result.
        
        Parameters:
            result (list[QRect] | object): Detected sprite bounding rectangles (typically a list of QRect) or an empty list if detection failed.
        """
        self.finished.emit(result)

    def _on_detection_error(self, error_info):
        """
        Handle an exception raised by the background detection worker and notify listeners.
        
        Logs the exception message, prints the traceback string, and emits an empty list via the `finished` signal to ensure the UI does not hang.
        
        Parameters:
            error_info (tuple): A tuple of `(exc_type, value, tb_str)` where `exc_type` is the exception class, `value` is the exception instance, and `tb_str` is the formatted traceback string.
        """
        exctype, value, tb_str = error_info
        self.logger.error(f"An error occurred during sprite detection: {str(value)}")
        print(tb_str)
        # Emit empty result to avoid hanging the UI
        self.finished.emit([])

    def detect_sprites(self, image_path, min_width=8, min_height=8):
        """
        Detect sprites in an image and return their bounding rectangles. This is the synchronous version; use start_detection for non-blocking detection.
        
        Parameters:
            image_path (str): Path to the sprite sheet image.
            min_width (int): Minimum sprite width to include.
            min_height (int): Minimum sprite height to include.
        
        Returns:
            list[QRect]: Detected sprite bounding rectangles sorted by y (top-to-bottom) then x (left-to-right).
        """
        return self._detect_sprites_impl(image_path, min_width, min_height)

    def detect_by_grid_pattern(self, image_path, min_width=8, min_height=8):
        """
        Detects sprite bounding rectangles by identifying grid-like horizontal and vertical lines in a grayscale image.
        
        Parameters:
            image_path (str): Path to the sprite sheet image.
            min_width (int): Minimum width of a detected sprite (pixels).
            min_height (int): Minimum height of a detected sprite (pixels).
        
        Returns:
            list[QRect]: List of QRect objects for each detected sprite bounding box; returns an empty list if the image cannot be loaded or no suitable regions are found.
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