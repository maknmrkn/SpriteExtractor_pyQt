# SpriteExtractor_pyQt

A PyQt6-based sprite sheet editor and extractor tool that allows users to load sprite sheets, detect and extract individual sprites, and manage them in a tree structure. The application provides a visual interface for working with sprite sheets commonly used in game development.

## Features

- **Load Sprite Sheets**: Load image files containing multiple sprites (sprite sheets)
- **Grid-based Extraction**: Visual grid overlay for selecting individual sprites
- **Auto-detection**: Automatic detection of sprites based on transparency boundaries
- **Thumbnail Grid**: Visual representation of extracted sprites
- **Tree Structure**: Organize sprites in a hierarchical tree structure
- **Animation Preview**: Preview sprites as animations
- **Export Functionality**: Export individual sprites or groups to image files
- **Customizable Grid**: Adjustable grid size, padding, and spacing
- **Sprite Properties**: View and edit properties of individual sprites

## Requirements

- Python 3.7+
- PyQt6
- OpenCV (cv2)
- NumPy

## Installation

1. Clone or download the repository
2. Install the required dependencies:

```bash
pip install PyQt6 opencv-python numpy
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Load a sprite sheet using the "Open" button or menu option
3. Use the grid overlay to select individual sprites or use the auto-detect feature
4. Extract sprites and organize them in the tree structure
5. Preview animations and export sprites as needed

## Key Components

### Main Window
The main application window contains:
- Canvas area for displaying the sprite sheet with grid overlay
- Animation preview panel
- Sprite properties panel
- Thumbnail grid for extracted sprites
- Tree structure for organizing sprites

### Canvas
- Displays the loaded sprite sheet
- Grid overlay for selecting sprites
- Support for different grid configurations (size, padding, spacing)
- Multiple selection support

### Sprite Detection
- Automatic detection of sprites based on transparency
- Configurable minimum dimensions for detection
- Uses OpenCV for contour detection

### Export Operations
- Export individual sprites to image files
- Export sprite groups
- Support for multiple image formats (PNG, JPEG)

## Controls

- **Left-click**: Select a grid cell
- **Right-click**: Context menu for grid cell operations
- **Drag selection**: Select multiple grid cells
- **Animation controls**: Play/pause animations with adjustable frame rate

## Project Structure

- [main.py](file:///g%3A/SpriteExtractor_pyQt/main.py): Application entry point
- [sprite_editor/](file:///g%3A/SpriteExtractor_pyQt/sprite_editor): Main application modules
  - [main_window.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/main_window.py): Main application window
  - [canvas.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/canvas.py): Canvas with grid overlay for sprite selection
  - [sprite_detector.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/sprite_detector.py): Automatic sprite detection functionality
  - [animation_preview.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/animation_preview.py): Animation preview widget
  - [export_operations.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/export_operations.py): Export functionality for sprites
  - [thumbnail_grid.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/thumbnail_grid.py): Thumbnail grid display
  - [tree_manager.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/tree_manager.py): Management of sprite tree structure
  - [ui_utils.py](file:///g%3A/SpriteExtractor_pyQt/sprite_editor/ui_utils.py): Utility functions for UI operations

## License

This project is open source, but no specific license was provided in the repository. Please check with the original author for licensing information.