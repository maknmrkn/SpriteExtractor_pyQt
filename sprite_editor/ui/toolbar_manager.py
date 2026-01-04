from PyQt6.QtWidgets import QToolBar, QSpinBox, QLabel, QHBoxLayout, QWidget, QComboBox, QPushButton
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor


class ToolbarManager:
    """
    Manages the toolbars for the main window.
    """
    def __init__(self, main_window):
        """
        Initialize the toolbar manager with a reference to the main window.
        
        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self._create_grid_toolbar()
        self._create_auto_detect_toolbar()

    def _create_grid_toolbar(self):
        """
        Create and attach the "Grid Settings" toolbar that exposes controls for configuring the canvas grid and related visual options.
        
        The toolbar includes:
        - a "Show Grid" toggle (checked by default);
        - grid size controls (width and height, default 32, range 8–2048, step 8);
        - padding X/Y and spacing X/Y controls (default 0, range 0–128);
        - a line style selector with "Solid" and "Dotted" options;
        - a Grid Color button (default green) and a BG Color button (default dark gray).
        
        Each control is wired to the corresponding MainWindow handler to update the canvas when changed.
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
        self.main_window._update_grid_color_button(QColor(0, 255, 0))  # Default green

        # Background Color Button
        self.main_window.bg_color_button = QPushButton("BG Color")
        self.main_window.bg_color_button.setFixedSize(90, 24)
        self.main_window.bg_color_button.clicked.connect(self.main_window._on_choose_bg_color)
        toolbar.addWidget(self.main_window.bg_color_button)
        self.main_window._update_bg_color_button(QColor(25, 25, 25))  # Default dark gray

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
        self.main_window.auto_detect_toolbar = QToolBar("Auto Detection Settings")
        self.main_window.auto_detect_toolbar.setIconSize(QSize(16, 16))
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_window.auto_detect_toolbar)

        # Toggle for auto-detection mode
        self.main_window.auto_detect_toggle = self.main_window.auto_detect_toolbar.addAction("Auto Detection Mode")
        self.main_window.auto_detect_toggle.setCheckable(True)
        self.main_window.auto_detect_toggle.setChecked(False)
        self.main_window.auto_detect_toggle.triggered.connect(self.main_window._toggle_auto_detect_mode)

        self.main_window.auto_detect_toolbar.addSeparator()

        # Min width for detection
        self.main_window.auto_detect_toolbar.addWidget(QLabel("Min Width:"))
        self.main_window.min_width_spinbox = QSpinBox()
        self.main_window.min_width_spinbox.setRange(1, 2048)
        self.main_window.min_width_spinbox.setValue(8)
        self.main_window.min_width_spinbox.setSingleStep(1)
        self.main_window.min_width_spinbox.setMaximumWidth(70)
        self.main_window.auto_detect_toolbar.addWidget(self.main_window.min_width_spinbox)

        # Min height for detection
        self.main_window.auto_detect_toolbar.addWidget(QLabel("Min Height:"))
        self.main_window.min_height_spinbox = QSpinBox()
        self.main_window.min_height_spinbox.setRange(1, 2048)
        self.main_window.min_height_spinbox.setValue(8)
        self.main_window.min_height_spinbox.setSingleStep(1)
        self.main_window.min_height_spinbox.setMaximumWidth(70)
        self.main_window.auto_detect_toolbar.addWidget(self.main_window.min_height_spinbox)

        # Auto-detect button
        self.main_window.auto_detect_button = self.main_window.auto_detect_toolbar.addAction("Detect Sprites")
        self.main_window.auto_detect_button.triggered.connect(self.main_window._auto_detect_frames)

        # Clear detections button
        self.main_window.clear_detections_button = self.main_window.auto_detect_toolbar.addAction("Clear Detections")
        self.main_window.clear_detections_button.triggered.connect(self.main_window._clear_detections)