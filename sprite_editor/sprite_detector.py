import cv2
import numpy as np
from PyQt6.QtCore import QRect


class SpriteDetector:
    """
    A class for automatically detecting sprites in a sprite sheet image.
    """
    
    def __init__(self):
        pass
    
    def detect_sprites(self, image_path, min_width=8, min_height=8):
        """
        Detect sprites in an image by finding connected components or transparent boundaries.
        
        Args:
            image_path: Path to the sprite sheet image
            min_width: Minimum width of a sprite to be detected
            min_height: Minimum height of a sprite to be detected
            
        Returns:
            List of QRect objects representing detected sprite rectangles
        """
        # Load image with alpha channel if it exists
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
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
        
        return detected_sprites

    def detect_by_grid_pattern(self, image_path, min_width=8, min_height=8):
        """
        Alternative method to detect sprites by looking for grid-like patterns.
        
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