from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QRect
from typing import List, Tuple


class SpriteExtractor:
    @staticmethod
    def detect_frames(pixmap: QPixmap, padding: int = 0) -> List[QRect]:
        """
        Automatically detect frames in a sprite sheet assuming uniform grid.
        Currently uses user-provided or auto-guessed grid size.
        Future: Add auto-detection via whitespace.
        """
        img: QImage = pixmap.toImage()
        width = img.width()
        height = img.height()

        # Placeholder: Assume 4x4 grid for now
        rows, cols = 4, 4
        frame_width = width // cols
        frame_height = height // rows

        frames = []
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frames.append(QRect(x, y, frame_width, frame_height))
        
        return frames

    @staticmethod
    def extract_frame(pixmap: QPixmap, rect: QRect) -> QPixmap:
        """Extract a single frame from the sprite sheet."""
        return pixmap.copy(rect)

    @staticmethod
    def save_frames(pixmap: QPixmap, frames: List[QRect], output_dir: str, prefix: str = "frame"):
        """Save all frames to directory as PNG files."""
        import os

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, rect in enumerate(frames):
            frame_pixmap = SpriteExtractor.extract_frame(pixmap, rect)
            if not frame_pixmap.isNull():
                frame_pixmap.save(os.path.join(output_dir, f"{prefix}_{i:03d}.png"), "PNG")