"""
مدیریت toolbarهای برنامه
"""

from PyQt6.QtWidgets import (
    QToolBar, QLabel, QSpinBox, QWidget, 
    QHBoxLayout, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QColor


class ToolbarManager:
    """مدیریت toolbarهای برنامه"""
    
    def __init__(self, main_window):
        """
        Initialize the ToolbarManager with a reference to the main application window and empty state containers.
        
        Parameters:
            main_window: The main window instance to which toolbars will be attached and whose `canvas` may be queried or updated. Initializes `self.main_window`, `self.toolbars` (dict), and `self.widgets` (dict).
        """
        self.main_window = main_window
        self.toolbars = {}
        self.widgets = {}
        
    def setup_toolbars(self):
        """
        Create and configure the toolbars used by the main window.
        
        Initializes the grid settings toolbar and the auto-detect toolbar, attaches them to the main window, and stores toolbar instances in self.toolbars and related control widgets in self.widgets.
        """
        self._create_grid_toolbar()
        self._create_auto_detect_toolbar()
    
    def _create_grid_toolbar(self):
        """
        Create and attach the "Grid Settings" toolbar to the main window.
        
        The toolbar is stored in self.toolbars['grid'], includes a checkable "Show Grid" action (checked by default)
        connected to self._on_toggle_grid, and populates controls for grid size, padding, spacing, line style, and colors
        by invoking the corresponding helper methods.
        """
        toolbar = QToolBar("Grid Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(toolbar)
        self.toolbars['grid'] = toolbar
        
        # Show Grid Toggle
        show_grid_action = toolbar.addAction("Show Grid")
        show_grid_action.setCheckable(True)
        show_grid_action.setChecked(True)
        show_grid_action.triggered.connect(self._on_toggle_grid)
        self.widgets['show_grid_action'] = show_grid_action
        
        toolbar.addSeparator()
        
        # Grid Size Controls
        self._add_grid_size_controls(toolbar)
        
        # Padding Controls
        self._add_padding_controls(toolbar)
        
        # Spacing Controls
        self._add_spacing_controls(toolbar)
        
        # Line Style
        self._add_line_style_control(toolbar)
        
        # Color Controls
        self._add_color_controls(toolbar)
    
    def _add_grid_size_controls(self, toolbar):
        """
        Add grid size controls (width and height) to the given toolbar.
        
        Creates labeled spin boxes for grid width and grid height with range 8–2048, default 32, step 8, and constrained widget widths. The controls' valueChanged signals are connected to update the manager's grid settings, and the spin box instances are stored in self.widgets['grid_width'] and self.widgets['grid_height']. A separator is added after the controls.
        
        Parameters:
            toolbar (QToolBar): Toolbar to which the grid size controls will be added.
        """
        toolbar.addWidget(QLabel("Grid:"))
        
        # Grid Width
        width_spin = QSpinBox()
        width_spin.setRange(8, 2048)
        width_spin.setValue(32)
        width_spin.setSingleStep(8)
        width_spin.setMaximumWidth(70)
        width_spin.valueChanged.connect(self._on_grid_width_changed)
        
        width_widget = QWidget()
        width_widget.setLayout(QHBoxLayout())
        width_widget.layout().addWidget(width_spin)
        width_widget.setMaximumWidth(80)
        toolbar.addWidget(width_widget)
        
        toolbar.addWidget(QLabel("×"))
        
        # Grid Height
        height_spin = QSpinBox()
        height_spin.setRange(8, 2048)
        height_spin.setValue(32)
        height_spin.setSingleStep(8)
        height_spin.setMaximumWidth(70)
        height_spin.valueChanged.connect(self._on_grid_height_changed)
        
        height_widget = QWidget()
        height_widget.setLayout(QHBoxLayout())
        height_widget.layout().addWidget(height_spin)
        height_widget.setMaximumWidth(80)
        toolbar.addWidget(height_widget)
        
        self.widgets['grid_width'] = width_spin
        self.widgets['grid_height'] = height_spin
        
        toolbar.addSeparator()
    
    def _add_padding_controls(self, toolbar):
        """
        Add horizontal and vertical padding controls to the given toolbar.
        
        Adds labeled QSpinBox controls for "Pad X" and "Pad Y", configures their ranges (0–128),
        default values (0), maximum width, and connects their valueChanged signals to the
        manager's padding change handlers. Stores the created spin boxes in self.widgets
        under 'padding_x' and 'padding_y' and appends a separator to the toolbar.
        
        Parameters:
            toolbar (QToolBar): The toolbar to which the padding controls will be added.
        """
        toolbar.addWidget(QLabel("Pad X:"))
        
        pad_x_spin = QSpinBox()
        pad_x_spin.setRange(0, 128)
        pad_x_spin.setValue(0)
        pad_x_spin.setMaximumWidth(60)
        pad_x_spin.valueChanged.connect(self._on_padding_x_changed)
        toolbar.addWidget(pad_x_spin)
        
        toolbar.addWidget(QLabel("Pad Y:"))
        
        pad_y_spin = QSpinBox()
        pad_y_spin.setRange(0, 128)
        pad_y_spin.setValue(0)
        pad_y_spin.setMaximumWidth(60)
        pad_y_spin.valueChanged.connect(self._on_padding_y_changed)
        toolbar.addWidget(pad_y_spin)
        
        self.widgets['padding_x'] = pad_x_spin
        self.widgets['padding_y'] = pad_y_spin
        
        toolbar.addSeparator()
    
    def _add_spacing_controls(self, toolbar):
        """
        Add horizontal and vertical spacing controls to the given toolbar.
        
        Adds "Space X" and "Space Y" QSpinBox widgets (range 0–128, default 0, max width 60) to control horizontal and vertical spacing, connects their valueChanged signals to the manager's handlers, stores the spin boxes in self.widgets under 'spacing_x' and 'spacing_y', and appends a separator to the toolbar.
        
        Parameters:
            toolbar (QToolBar): The toolbar to which the spacing controls will be added.
        """
        toolbar.addWidget(QLabel("Space X:"))
        
        space_x_spin = QSpinBox()
        space_x_spin.setRange(0, 128)
        space_x_spin.setValue(0)
        space_x_spin.setMaximumWidth(60)
        space_x_spin.valueChanged.connect(self._on_spacing_x_changed)
        toolbar.addWidget(space_x_spin)
        
        toolbar.addWidget(QLabel("Space Y:"))
        
        space_y_spin = QSpinBox()
        space_y_spin.setRange(0, 128)
        space_y_spin.setValue(0)
        space_y_spin.setMaximumWidth(60)
        space_y_spin.valueChanged.connect(self._on_spacing_y_changed)
        toolbar.addWidget(space_y_spin)
        
        self.widgets['spacing_x'] = space_x_spin
        self.widgets['spacing_y'] = space_y_spin
        
        toolbar.addSeparator()
    
    def _add_line_style_control(self, toolbar):
        """
        Add a line style control group to the given toolbar.
        
        Parameters:
            toolbar (QToolBar): Toolbar to receive the "Line:" label and a combo box for selecting the line style.
        """
        toolbar.addWidget(QLabel("Line:"))
        
        line_combo = QComboBox()
        line_combo.addItems(["Solid", "Dotted"])
        line_combo.currentTextChanged.connect(self._on_line_style_changed)
        toolbar.addWidget(line_combo)
        
        self.widgets['line_style'] = line_combo
        
        toolbar.addSeparator()
    
    def _add_color_controls(self, toolbar):
        """
        Add color selection controls to the provided toolbar.
        
        Adds two fixed-size QPushButton widgets labeled "Grid Color" and "BG Color" to the toolbar, connects their clicked signals to the corresponding color-picker handlers, and stores the buttons in self.widgets under 'grid_color_btn' and 'bg_color_btn'. Also initializes the buttons' visual state by setting the default grid color to RGB(0, 255, 0) and the default background color to RGB(25, 25, 25).
        
        Parameters:
            toolbar (QToolBar): The toolbar to which the color controls will be added.
        """
        # Grid Color Button
        grid_color_btn = QPushButton("Grid Color")
        grid_color_btn.setFixedSize(90, 24)
        grid_color_btn.clicked.connect(self._on_choose_grid_color)
        toolbar.addWidget(grid_color_btn)
        
        # Background Color Button
        bg_color_btn = QPushButton("BG Color")
        bg_color_btn.setFixedSize(90, 24)
        bg_color_btn.clicked.connect(self._on_choose_bg_color)
        toolbar.addWidget(bg_color_btn)
        
        self.widgets['grid_color_btn'] = grid_color_btn
        self.widgets['bg_color_btn'] = bg_color_btn
        
        # Set default colors
        self._update_grid_color_button(QColor(0, 255, 0))
        self._update_bg_color_button(QColor(25, 25, 25))
    
    def _create_auto_detect_toolbar(self):
        """
        Create and configure the "Auto Detection Settings" toolbar and register its controls.
        
        The toolbar is added to the main window but hidden by default. It provides:
        - a checkable "Auto Detection Mode" action (stored as 'auto_detect_action') that toggles detection mode on the main window,
        - two spin boxes for minimum width and height (stored as 'min_width' and 'min_height') with range 1–2048 and default value 8,
        - a "Detect Sprites" action (stored as 'detect_action') that triggers automatic frame detection on the main window,
        - a "Clear Detections" action (stored as 'clear_action') that clears detection results on the main window.
        
        All created widgets and the toolbar itself are stored in self.widgets and self.toolbars respectively.
        """
        toolbar = QToolBar("Auto Detection Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.setVisible(False)
        self.toolbars['auto_detect'] = toolbar
        
        # Auto Detection Mode Toggle
        auto_detect_action = toolbar.addAction("Auto Detection Mode")
        auto_detect_action.setCheckable(True)
        auto_detect_action.setChecked(False)
        auto_detect_action.triggered.connect(self.main_window._toggle_auto_detect_mode)
        self.widgets['auto_detect_action'] = auto_detect_action
        
        toolbar.addSeparator()
        
        # Min Width
        toolbar.addWidget(QLabel("Min Width:"))
        min_width_spin = QSpinBox()
        min_width_spin.setRange(1, 2048)
        min_width_spin.setValue(8)
        min_width_spin.setSingleStep(1)
        min_width_spin.setMaximumWidth(70)
        self.widgets['min_width'] = min_width_spin
        toolbar.addWidget(min_width_spin)
        
        # Min Height
        toolbar.addWidget(QLabel("Min Height:"))
        min_height_spin = QSpinBox()
        min_height_spin.setRange(1, 2048)
        min_height_spin.setValue(8)
        min_height_spin.setSingleStep(1)
        min_height_spin.setMaximumWidth(70)
        self.widgets['min_height'] = min_height_spin
        toolbar.addWidget(min_height_spin)
        
        # Detect Sprites Button
        detect_action = toolbar.addAction("Detect Sprites")
        detect_action.triggered.connect(self.main_window._auto_detect_frames)
        self.widgets['detect_action'] = detect_action
        
        # Clear Detections Button
        clear_action = toolbar.addAction("Clear Detections")
        clear_action.triggered.connect(self.main_window._clear_detections)
        self.widgets['clear_action'] = clear_action
    
    # ====== Color Management ======
    
    def _update_grid_color_button(self, color):
        """
        Update the grid color button appearance and apply the color to the canvas if available.
        
        Parameters:
            color (QColor): The color to display on the grid color button and to set on the canvas.
        """
        self.widgets['grid_color_btn'].setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'black' if color.lightness() > 128 else 'white'};"
        )
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_color = color
            self.main_window.canvas.update_display()
    
    def _update_bg_color_button(self, color):
        """
        Update the background color button's appearance and apply the color to the main canvas if available.
        
        Sets the button's stylesheet to the provided color and chooses a readable text color (black or white) based on the color's lightness. If the main window has a `canvas` attribute, updates `canvas.background_color` and triggers a display refresh.
        
        Parameters:
            color (QColor): The color to display and apply as the canvas background.
        """
        self.widgets['bg_color_btn'].setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'black' if color.lightness() > 128 else 'white'};"
        )
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.background_color = color
            self.main_window.canvas.update_display()
    
    # ====== Slot Methods ======
    
    def _on_toggle_grid(self, checked):
        """
        Set the canvas grid visibility and refresh the display if a canvas is present.
        
        Parameters:
            checked (bool): If True, show the grid; if False, hide it.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.show_grid = checked
            self.main_window.canvas.update_display()
    
    def _on_grid_width_changed(self, value):
        """
        Set the grid width on the main canvas and refresh the display.
        
        Parameters:
            value (int): New grid width in pixels to apply to the canvas.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_width = value
            self.main_window.canvas.update_display()
    
    def _on_grid_height_changed(self, value):
        """
        Set the canvas grid height to the given value and refresh the canvas display.
        
        If the main window has no canvas attribute, the call has no effect.
        
        Parameters:
            value (int): New grid height in pixels (typically in the range 8–2048).
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_height = value
            self.main_window.canvas.update_display()
    
    def _on_padding_x_changed(self, value):
        """
        Set the canvas horizontal padding and refresh the display.
        
        If the main window has a canvas, updates the canvas's horizontal padding to the given value and requests a display refresh.
        
        Parameters:
            value (int): New horizontal padding in pixels.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_x = value
            self.main_window.canvas.update_display()
    
    def _on_padding_y_changed(self, value):
        """
        Set the canvas's vertical padding and refresh the display.
        
        If the main window has a `canvas` attribute, updates `canvas.padding_y` to the given value and calls the canvas display update.
        
        Parameters:
            value (int): New vertical padding in pixels.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_y = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_x_changed(self, value):
        """
        Set the horizontal grid spacing on the main window's canvas and refresh its display.
        
        Parameters:
            value (int): New horizontal spacing in pixels.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_x = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_y_changed(self, value):
        """
        Set the canvas's vertical spacing and refresh the display.
        
        If the main window has a canvas, updates its vertical (Y) spacing to `value` and triggers a display refresh.
        
        Parameters:
            value (int): New vertical spacing (pixels).
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_y = value
            self.main_window.canvas.update_display()
    
    def _on_line_style_changed(self, text):
        """
        Set the canvas line style and refresh the display.
        
        If the main window has a `canvas` attribute, sets `canvas.line_style` to `text` and triggers a display update.
        
        Parameters:
            text (str): The name of the line style (e.g., "Solid", "Dotted").
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.line_style = text
            self.main_window.canvas.update_display()
    
    def _on_choose_grid_color(self):
        """
        Open a color picker for the grid and apply the chosen color.
        
        If the main window has a `canvas`, presents a color dialog initialized with the canvas's current grid color. When the user selects a valid color, updates the grid color control and the canvas's grid color. Does nothing if no canvas is present.
        """
        from PyQt6.QtWidgets import QColorDialog
        
        if hasattr(self.main_window, 'canvas'):
            color = QColorDialog.getColor(
                self.main_window.canvas.grid_color, 
                self.main_window, 
                "Choose Grid Color"
            )
            if color.isValid():
                self._update_grid_color_button(color)
    
    def _on_choose_bg_color(self):
        """
        Prompt the user to choose a new background color and apply it to the UI.
        
        Opens a color chooser initialized with the current canvas background color (if the main window has a canvas). If the user selects a valid color, updates the background color button appearance and applies the chosen color to the canvas. If no canvas is present or the user cancels, no changes are made.
        """
        from PyQt6.QtWidgets import QColorDialog
        
        if hasattr(self.main_window, 'canvas'):
            color = QColorDialog.getColor(
                self.main_window.canvas.background_color, 
                self.main_window, 
                "Choose Background Color"
            )
            if color.isValid():
                self._update_bg_color_button(color)
    
    # ====== Public Methods ======
    
    def toggle_auto_detect_toolbar(self, visible):
        """
        Set the visibility of the auto-detect toolbar if it exists.
        
        Parameters:
            visible (bool): True to show the auto-detect toolbar, False to hide it.
        """
        if 'auto_detect' in self.toolbars:
            self.toolbars['auto_detect'].setVisible(visible)
    
    def get_min_width(self):
        """
        Get the current minimum width value used by the UI.
        
        Returns:
            int: The value from the 'min_width' widget, or 8 if that widget is not present.
        """
        min_width_widget = self.widgets.get('min_width')
        return min_width_widget.value() if min_width_widget else 8
    
    def get_min_height(self):
        """
        Return the current minimum tile height used by the grid.
        
        Returns:
            int: The value of the 'min_height' widget's spin box, or 8 if that widget is not available.
        """
        min_height_widget = self.widgets.get('min_height')
        return min_height_widget.value() if min_height_widget else 8