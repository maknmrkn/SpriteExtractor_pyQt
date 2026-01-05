from PyQt6.QtWidgets import QMenuBar, QToolBar, QSpinBox, QLabel, QHBoxLayout, QComboBox, QPushButton, QColorDialog, QStatusBar, QFileDialog, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor


class MenuToolbarManager:
    """
    Manages menu and toolbar functionality for the main window.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self._create_menu_bar()
        self._create_grid_toolbar()
        self._create_auto_detect_toolbar()
        self.auto_detect_toolbar.setVisible(False)

    def _create_menu_bar(self):
        """
        Create the main window's menu bar with File and Edit menus and their actions.
        
        Adds a File menu containing:
        - "Open Sprite Sheet..." (Ctrl+O) — opens a file dialog and loads an image via open_file.
        - "Save Frames As..." (Ctrl+S) — placeholder action (not yet connected).
        - "Exit" (Ctrl+Q) — closes the window.
        
        Adds an Edit menu containing:
        - "Auto-detect Frames" — triggers the auto-detection workflow via _auto_detect_frames.
        """
        menu_bar: QMenuBar = self.main_window.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        open_action = file_menu.addAction("Open Sprite Sheet...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.main_window.open_file)

        save_action = file_menu.addAction("Save Frames As...")
        save_action.setShortcut("Ctrl+S")
        # TODO: Connect to save_frames method

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.main_window.close)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        extract_action = edit_menu.addAction("Auto-detect Frames")
        extract_action.triggered.connect(self.main_window._auto_detect_frames)

    def _create_grid_toolbar(self):
        """
        Create and add the "Grid Settings" toolbar with controls for configuring the canvas grid and related visual options.
        
        The toolbar provides:
        - a Show Grid toggle (checked by default);
        - grid size controls for width and height (default 32, range 8–2048, step 8);
        - padding X/Y and spacing X/Y spinboxes (default 0, range 0–128);
        - a line style selector with "Solid" and "Dotted" options;
        - a Grid Color button (default green) and a BG Color button (default dark gray).
        
        Each control is connected to the MainWindow handlers that update the canvas state when changed.
        """
        toolbar = QToolBar("Grid Settings")
        toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(toolbar)

        # Show Grid Toggle
        self.main_window.show_grid_toggle = toolbar.addAction("Show Grid")
        self.main_window.show_grid_toggle.setCheckable(True)
        self.main_window.show_grid_toggle.setChecked(True)  # Default to checked
        self.main_window.show_grid_toggle.triggered.connect(self.main_window._on_grid_toggled)

        toolbar.addSeparator()

        # Grid Size (Width and Height)
        toolbar.addWidget(QLabel("Grid:"))
        
        # Grid Width
        self.main_window.grid_width_spinbox = QSpinBox()
        self.main_window.grid_width_spinbox.setRange(8, 2048)
        self.main_window.grid_width_spinbox.setValue(32)
        self.main_window.grid_width_spinbox.setSingleStep(8)
        self.main_window.grid_width_spinbox.valueChanged.connect(self.main_window._on_grid_width_changed)
        width_widget = QWidget()
        width_widget.setLayout(QHBoxLayout())
        width_widget.layout().addWidget(self.main_window.grid_width_spinbox)
        width_widget.setMaximumWidth(70)
        toolbar.addWidget(width_widget)
        
        toolbar.addWidget(QLabel("×"))  # Multiplication sign
        
        # Grid Height
        self.main_window.grid_height_spinbox = QSpinBox()
        self.main_window.grid_height_spinbox.setRange(8, 2048)
        self.main_window.grid_height_spinbox.setValue(32)
        self.main_window.grid_height_spinbox.setSingleStep(8)
        self.main_window.grid_height_spinbox.valueChanged.connect(self.main_window._on_grid_height_changed)
        height_widget = QWidget()
        height_widget.setLayout(QHBoxLayout())
        height_widget.layout().addWidget(self.main_window.grid_height_spinbox)
        height_widget.setMaximumWidth(70)
        toolbar.addWidget(height_widget)

        toolbar.addSeparator()

        # Padding X
        toolbar.addWidget(QLabel("Padding X:"))
        self.main_window.padding_x_spinbox = QSpinBox()
        self.main_window.padding_x_spinbox.setRange(0, 128)
        self.main_window.padding_x_spinbox.setValue(0)
        self.main_window.padding_x_spinbox.valueChanged.connect(self.main_window._on_padding_x_changed)
        padx_widget = QWidget()
        padx_widget.setLayout(QHBoxLayout())
        padx_widget.layout().addWidget(self.main_window.padding_x_spinbox)
        padx_widget.setMaximumWidth(80)
        toolbar.addWidget(padx_widget)

        # Padding Y
        toolbar.addWidget(QLabel("Padding Y:"))
        self.main_window.padding_y_spinbox = QSpinBox()
        self.main_window.padding_y_spinbox.setRange(0, 128)
        self.main_window.padding_y_spinbox.setValue(0)
        self.main_window.padding_y_spinbox.valueChanged.connect(self.main_window._on_padding_y_changed)
        pady_widget = QWidget()
        pady_widget.setLayout(QHBoxLayout())
        pady_widget.layout().addWidget(self.main_window.padding_y_spinbox)
        pady_widget.setMaximumWidth(80)
        toolbar.addWidget(pady_widget)

        toolbar.addSeparator()

        # Spacing X
        toolbar.addWidget(QLabel("Spacing X:"))
        self.main_window.spacing_x_spinbox = QSpinBox()
        self.main_window.spacing_x_spinbox.setRange(0, 128)
        self.main_window.spacing_x_spinbox.setValue(0)
        self.main_window.spacing_x_spinbox.valueChanged.connect(self.main_window._on_spacing_x_changed)
        spacex_widget = QWidget()
        spacex_widget.setLayout(QHBoxLayout())
        spacex_widget.layout().addWidget(self.main_window.spacing_x_spinbox)
        spacex_widget.setMaximumWidth(80)
        toolbar.addWidget(spacex_widget)

        # Spacing Y
        toolbar.addWidget(QLabel("Spacing Y:"))
        self.main_window.spacing_y_spinbox = QSpinBox()
        self.main_window.spacing_y_spinbox.setRange(0, 128)
        self.main_window.spacing_y_spinbox.setValue(0)
        self.main_window.spacing_y_spinbox.valueChanged.connect(self.main_window._on_spacing_y_changed)
        spacey_widget = QWidget()
        spacey_widget.setLayout(QHBoxLayout())
        spacey_widget.layout().addWidget(self.main_window.spacing_y_spinbox)
        spacey_widget.setMaximumWidth(80)
        toolbar.addWidget(spacey_widget)

        toolbar.addSeparator()

        # Grid Line Style
        toolbar.addWidget(QLabel("Line:"))
        self.main_window.line_style_combo = QComboBox()
        self.main_window.line_style_combo.addItems(["Solid", "Dotted"])
        self.main_window.line_style_combo.currentTextChanged.connect(self.main_window._on_line_style_changed)
        toolbar.addWidget(self.main_window.line_style_combo)

        toolbar.addSeparator()

        # Grid Color Button
        self.main_window.grid_color_button = QPushButton("Grid Color")
        self.main_window.grid_color_button.setFixedSize(90, 24)
        self.main_window.grid_color_button.clicked.connect(self.main_window._on_choose_grid_color)
        toolbar.addWidget(self.main_window.grid_color_button)
        self._update_grid_color_button(QColor(0, 255, 0))  # Default green

        # Background Color Button
        self.main_window.bg_color_button = QPushButton("BG Color")
        self.main_window.bg_color_button.setFixedSize(90, 24)
        self.main_window.bg_color_button.clicked.connect(self.main_window._on_choose_bg_color)
        toolbar.addWidget(self.main_window.bg_color_button)
        self._update_bg_color_button(QColor(25, 25, 25))  # Default dark gray

    def _update_grid_color_button(self, color: QColor):
        """
        Update the grid color control and apply the color to the canvas.
        
        Parameters:
            color (QColor): The color to use for the grid; updates the grid color button's appearance and sets the canvas's grid color, then refreshes the canvas display.
        """
        self.main_window.grid_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")

    def _update_bg_color_button(self, color: QColor):
        """
        Update the background-color button's appearance and apply the chosen color to the canvas.
        
        Parameters:
            color (QColor): New background color; this updates the button's background and text color for legibility, sets the canvas background_color, and refreshes the canvas display.
        """
        self.main_window.bg_color_button.setStyleSheet(f"background-color: {color.name()}; color: {'black' if color.lightness() > 128 else 'white'};")

    def _create_auto_detect_toolbar(self):
        """
        Add the auto-detection toolbar to the main window.
        
        Creates and configures the "Auto Detection Settings" toolbar with:
        - a checkable "Auto Detection Mode" toggle connected to _toggle_auto_detect_mode,
        - spin boxes for minimum detection width and height (1–2048, default 8),
        - a "Detect Sprites" action connected to _auto_detect_frames,
        - a "Clear Detections" action connected to _clear_detections.
        
        The toolbar is added to the top tool bar area and its widgets are stored as instance attributes for later access.
        """
        self.auto_detect_toolbar = QToolBar("Auto Detection Settings")
        self.auto_detect_toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.auto_detect_toolbar)

        # Toggle for auto-detection mode
        self.main_window.auto_detect_toggle = self.auto_detect_toolbar.addAction("Auto Detection Mode")
        self.main_window.auto_detect_toggle.setCheckable(True)
        self.main_window.auto_detect_toggle.setChecked(False)
        self.main_window.auto_detect_toggle.triggered.connect(self.main_window._toggle_auto_detect_mode)

        self.auto_detect_toolbar.addSeparator()

        # Min width for detection
        self.auto_detect_toolbar.addWidget(QLabel("Min Width:"))
        self.main_window.min_width_spinbox = QSpinBox()
        self.main_window.min_width_spinbox.setRange(1, 2048)
        self.main_window.min_width_spinbox.setValue(8)
        self.main_window.min_width_spinbox.setSingleStep(1)
        self.main_window.min_width_spinbox.setMaximumWidth(70)
        self.auto_detect_toolbar.addWidget(self.main_window.min_width_spinbox)

        # Min height for detection
        self.auto_detect_toolbar.addWidget(QLabel("Min Height:"))
        self.main_window.min_height_spinbox = QSpinBox()
        self.main_window.min_height_spinbox.setRange(1, 2048)
        self.main_window.min_height_spinbox.setValue(8)
        self.main_window.min_height_spinbox.setSingleStep(1)
        self.main_window.min_height_spinbox.setMaximumWidth(70)
        self.auto_detect_toolbar.addWidget(self.main_window.min_height_spinbox)

        # Auto-detect button
        self.main_window.auto_detect_button = self.auto_detect_toolbar.addAction("Detect Sprites")
        self.main_window.auto_detect_button.triggered.connect(self.main_window._auto_detect_frames)

        # Clear detections button
        self.main_window.clear_detections_button = self.auto_detect_toolbar.addAction("Clear Detections")
        self.main_window.clear_detections_button.triggered.connect(self.main_window._clear_detections)