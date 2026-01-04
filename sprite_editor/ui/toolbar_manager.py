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
        Initialize the ToolbarManager.
        
        Parameters:
            main_window: The application's main window instance used to add toolbars, create actions, and access the canvas. The instance is stored as `self.main_window`. Also initializes `self.toolbars` and `self.widgets` as empty dictionaries for tracking created toolbars and widget references.
        """
        self.main_window = main_window
        self.toolbars = {}
        self.widgets = {}
        
    def setup_toolbars(self):
        """
        Initialize and add all toolbars to the main window.
        
        Creates and configures the Grid Settings and Auto Detection Settings toolbars and registers them with the main window.
        """
        self._create_grid_toolbar()
        self._create_auto_detect_toolbar()
    
    def _create_grid_toolbar(self):
        """
        Create and add the "Grid Settings" toolbar to the main window.
        
        Adds a checkable "Show Grid" action (checked by default) and stores it in
        self.widgets['show_grid_action']. Stores the created QToolBar in
        self.toolbars['grid'] and populates the toolbar with grid size, padding,
        spacing, line style, and color controls via the corresponding helper methods.
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
        Add grid width and height controls to the provided toolbar.
        
        Adds two QSpinBox widgets for grid width and height (range 8–2048, default 32, step 8), places them in compact containers, inserts a "×" separator between them, connects their valueChanged signals to the corresponding handlers, stores references in self.widgets under 'grid_width' and 'grid_height', and adds a toolbar separator.
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
        
        Adds labeled QSpinBox controls for "Pad X" and "Pad Y" (range 0–128, default 0, maximum width 60), connects their valueChanged signals to the corresponding handlers (_on_padding_x_changed and _on_padding_y_changed), stores the spin boxes in self.widgets under keys 'padding_x' and 'padding_y', and appends a separator to the toolbar.
        
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
        
        Adds labeled spin boxes for "Space X" and "Space Y", initializes their ranges and defaults, connects their value change signals to the manager's spacing handlers, and stores the widgets in self.widgets under 'spacing_x' and 'spacing_y'.
        
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
        Add a line-style selector to the given toolbar.
        
        Parameters:
            toolbar (QToolBar): The toolbar to which the "Line:" label, a combo box with options
                "Solid" and "Dotted", and a trailing separator will be added. The combo box's
                value change is connected to the instance's `_on_line_style_changed` and the
                widget is stored in `self.widgets['line_style']`.
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
        Add grid and background color selection buttons to the specified toolbar.
        
        Adds two fixed-size QPushButton widgets labeled "Grid Color" and "BG Color", connects them to their respective color-chooser handlers, stores the buttons in self.widgets under 'grid_color_btn' and 'bg_color_btn', and initializes their colors to green (QColor(0, 255, 0)) and dark gray (QColor(25, 25, 25)).
        
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
        Create and configure the "Auto Detection Settings" toolbar.
        
        Adds a hidden toolbar to the top toolbar area and populates it with:
        - a checkable "Auto Detection Mode" action (default unchecked) wired to main_window._toggle_auto_detect_mode and stored as 'auto_detect_action';
        - "Min Width" and "Min Height" QSpinBox controls (range 1–2048, default 8) stored as 'min_width' and 'min_height';
        - a "Detect Sprites" action wired to main_window._auto_detect_frames stored as 'detect_action';
        - a "Clear Detections" action wired to main_window._clear_detections stored as 'clear_action'.
        
        The toolbar instance is stored in self.toolbars['auto_detect'].
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
        Update the grid color button and apply the color to the canvas if present.
        
        Parameters:
            color (QColor): Color to set on the grid color button; also assigned to the main window's canvas.grid_color and triggers a display update when a canvas exists.
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
        Update the background color button's appearance and apply the color to the canvas.
        
        Updates the 'bg_color_btn' widget background and sets its text color to black or white based on the color's lightness. If the main window has a `canvas` attribute, sets `canvas.background_color` to the given color and triggers a display refresh via `canvas.update_display()`.
        
        Parameters:
            color (QColor): The background color to apply to the button and canvas.
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
        Toggle grid visibility on the main window's canvas.
        
        Parameters:
            checked (bool): Whether the grid should be shown (`True`) or hidden (`False`).
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.show_grid = checked
            self.main_window.canvas.update_display()
    
    def _on_grid_width_changed(self, value):
        """
        Update the canvas grid width and refresh the display.
        
        Parameters:
            value (int): New grid cell width in pixels.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_width = value
            self.main_window.canvas.update_display()
    
    def _on_grid_height_changed(self, value):
        """
        Update the canvas grid height and refresh the display.
        
        Parameters:
            value (int): New grid height in pixels to apply to the canvas.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.grid_height = value
            self.main_window.canvas.update_display()
    
    def _on_padding_x_changed(self, value):
        """
        Update the canvas horizontal padding and refresh the display if a canvas is present.
        
        Sets the main window canvas's `padding_x` to the given value and triggers a display update when a canvas exists.
        
        Parameters:
            value (int): New horizontal padding (pixels) to apply to the canvas.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_x = value
            self.main_window.canvas.update_display()
    
    def _on_padding_y_changed(self, value):
        """
        Set the vertical padding for the canvas grid and refresh the display.
        
        Parameters:
            value (int): New vertical padding (pixels) to apply to the canvas.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.padding_y = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_x_changed(self, value):
        """
        Update the canvas's horizontal spacing and refresh the display.
        
        If the manager's main window has a `canvas` attribute, sets the canvas's `spacing_x`
        to `value` and triggers a display update.
        
        Parameters:
            value (int): New horizontal spacing value (pixels).
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_x = value
            self.main_window.canvas.update_display()
    
    def _on_spacing_y_changed(self, value):
        """
        Update the canvas's vertical spacing setting and refresh the display.
        
        Parameters:
            value (int): New spacing value for the Y (vertical) axis, in pixels.
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.spacing_y = value
            self.main_window.canvas.update_display()
    
    def _on_line_style_changed(self, text):
        """
        Update the canvas line style and refresh the canvas display.
        
        Parameters:
            text (str): New line style name (e.g., "Solid", "Dotted").
        """
        if hasattr(self.main_window, 'canvas'):
            self.main_window.canvas.line_style = text
            self.main_window.canvas.update_display()
    
    def _on_choose_grid_color(self):
        """
        Open a color picker initialized to the current grid color and apply the chosen color.
        
        Opens a QColorDialog seeded with the canvas's current grid color. If the user selects a valid color, the toolbar's grid color control is updated and the canvas is updated to use the new color.
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
        Open a color picker to choose and apply the canvas background color.
        
        If the main window has a canvas, opens a color dialog initialized with the canvas's current background color. When the user selects a valid color, updates the background color button and applies the selected color to the canvas.
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
        Retrieve the configured minimum width used by the auto-detection toolbar.
        
        Returns:
            The integer value from the 'min_width' widget, or 8 if the widget is not present.
        """
        min_width_widget = self.widgets.get('min_width')
        return min_width_widget.value() if min_width_widget else 8
    
    def get_min_height(self):
        """
        Get the configured minimum detection height from the auto-detect toolbar.
        
        Returns:
            int: The value from the 'min_height' widget, or 8 if the widget is not present.
        """
        min_height_widget = self.widgets.get('min_height')
        return min_height_widget.value() if min_height_widget else 8