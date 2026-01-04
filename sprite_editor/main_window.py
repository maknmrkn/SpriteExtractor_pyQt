"""
Main Window اصلی برنامه - نسخه refactored
"""

from PyQt6.QtWidgets import QMainWindow, QStatusBar, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from .ui import (
    WidgetInitializer, LayoutManager, MenuManager,
    ToolbarManager, SignalManager, StyleManager
)


class MainWindow(QMainWindow):
    """ویندوز اصلی برنامه"""
    
    def __init__(self):
        """
        Initialize the MainWindow, configure UI managers, connect signals, apply styles, and prepare the status bar.
        
        This sets up the window defaults (title and sizes), initializes manager instances and widget layout, wires UI signals, applies the selected style, prepares the status bar, and initializes internal state such as group counters.
        """
        super().__init__()
        
        # تنظیمات اولیه ویندوز
        self._init_window()
        
        # مقداردهی اولیه group counters
        self.group_counters = {}
        
        # مقداردهی اولیه managerها
        self._init_managers()
        
        # راه‌اندازی UI
        self._setup_ui()
        
        # اتصال signalها
        self._connect_signals()
        
        # اعمال استایل
        self._apply_styles()
        
        # تنظیم status bar
        self._setup_status_bar()
        
        # نمایش پیام شروع
        self.statusBar().showMessage("Sprite Editor Ready")
    
    def _init_window(self):
        """
        Initialize the main window's basic geometry and title.
        
        Sets the window title to "Sprite Editor", the initial size to 1200×800, and the minimum allowed size to 800×600.
        """
        self.setWindowTitle("Sprite Editor")
        self.resize(1200, 800)
        
        # تنظیمات geometry
        self.setMinimumSize(800, 600)
        
    def _init_managers(self):
        """
        Instantiate and attach the manager objects used by the main window.
        
        Initializes and assigns these attributes on self:
        - widget_initializer: WidgetInitializer(self)
        - layout_manager: None (placeholder to be created later)
        - menu_manager: MenuManager(self)
        - toolbar_manager: ToolbarManager(self)
        - signal_manager: SignalManager(self)
        - style_manager: StyleManager(self)
        """
        # ایجاد managerها
        self.widget_initializer = WidgetInitializer(self)
        self.layout_manager = None
        self.menu_manager = MenuManager(self)
        self.toolbar_manager = ToolbarManager(self)
        self.signal_manager = SignalManager(self)
        self.style_manager = StyleManager(self)
    
    def _setup_ui(self):
        """
        Initialize the main window's user interface by creating widgets, assigning them to attributes, and configuring layout, menus, and toolbars.
        
        This performs widget instantiation, binds the created widgets to MainWindow attributes, builds the layout using the LayoutManager, and initializes menus and toolbars via their respective managers.
        """
        # مقداردهی اولیه ویجت‌ها
        widgets = self.widget_initializer.initialize_widgets()
        
        # اختصاص ویجت‌ها به attributes اصلی
        self._assign_widgets(widgets)
        
        # تنظیم layout
        self.layout_manager = LayoutManager(self, widgets)
        self.layout_manager.setup_layout()
        
        # تنظیم منوها
        self.menu_manager.setup_menus()
        
        # تنظیم toolbarها
        self.toolbar_manager.setup_toolbars()
    
    def _assign_widgets(self, widgets):
        """
        Assign widget objects from a mapping to attributes on the MainWindow instance.
        
        Parameters:
            widgets (dict[str, QObject]): Mapping of attribute names to widget instances; each key is the attribute name to set on self and each value is the corresponding widget object.
        """
        for name, widget in widgets.items():
            setattr(self, name, widget)
    
    def _connect_signals(self):
        """
        Establishes the main window's signal-slot connections.
        
        Sets up all required UI and application signal bindings so the window responds to user actions and internal events.
        """
        self.signal_manager.setup_connections()
    
    def _apply_styles(self):
        """
        Apply the light visual theme to the application's user interface.
        
        This updates the window and managed widgets to use the configured light theme.
        """
        self.style_manager.apply_theme('light ')
    
    def _setup_status_bar(self):
        """
        Configure and install the main window's status bar.
        
        Creates a QStatusBar for the window and applies a dark-themed stylesheet that sets background color, text color, and item border styling.
        """
        self.setStatusBar(QStatusBar())
        
        # تنظیمات status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #323232;
                color: white;
                border-top: 1px solid #555;
            }
            QStatusBar::item {
                border: none;
            }
        """)
    
    # ====== Public Methods ======
    
    def open_file(self):
        """
        Open an image file and load it into the canvas.
        
        If the user selects a file, attempts to load it into self.canvas. On success updates the status bar with the file path, adds a default sprites group to the tree manager, and shows the auto-detect toolbar. On failure updates the status bar and displays a warning dialog indicating the load error.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Sprite Sheet",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        
        if path:
            if self.canvas.load_image(path):
                self.statusBar().showMessage(f"Loaded: {path}")
                
                # اضافه کردن گروه پیش‌فرض
                self.tree_manager._add_default_sprites_group()
                
                # نمایش toolbar تشخیص خودکار
                self.toolbar_manager.toggle_auto_detect_toolbar(True)
                
                # لاگ
                print(f"Image loaded successfully: {path}")
            else:
                self.statusBar().showMessage("Failed to load image.")
                QMessageBox.warning(
                    self,
                    "Load Error",
                    f"Could not load image from:\n{path}"
                )
    
    def _auto_detect_frames(self):
        """
        Initiates automatic sprite/frame detection for the currently loaded image.
        
        If an image is loaded and its file path is available, this enables the canvas auto-detect mode, retrieves minimum width/height thresholds from the toolbar, updates the display and status bar, and starts an asynchronous detection run. If no image is loaded or the image path is unavailable, a status message is shown and detection is not started.
        """
        if not self.canvas.pixmap or self.canvas.pixmap.isNull():
            self.statusBar().showMessage("No image loaded to detect frames from.")
            return
        
        # دریافت مقادیر min dimensions
        min_width = self.toolbar_manager.get_min_width()
        min_height = self.toolbar_manager.get_min_height()
        
        # غیرفعال کردن grid در حین تشخیص
        self.canvas.show_grid = False
        self.canvas.in_autodetect_mode = True
        self.canvas.update_display()
        
        # نمایش پیام در حال پردازش
        self.statusBar().showMessage("Detecting sprites...")
        
        # شروع تشخیص غیرهمزمان
        if hasattr(self.canvas, 'current_path') and self.canvas.current_path:
            self.sprite_detector.start_detection(
                self.canvas.current_path,
                min_width,
                min_height
            )
        else:
            self.statusBar().showMessage(
                "Could not detect sprites: image path not available."
            )
    
    def _on_detection_finished(self, detected_sprites):
        """
        Handle completion of auto-detection by updating the canvas with detected sprite rectangles and notifying the user.
        
        If `detected_sprites` contains one or more rectangles, replaces current selections and detected sprites on the canvas with those rectangles, refreshes the canvas display, and shows a status message indicating how many sprites were found. If the list is empty, shows a status message and an information dialog notifying that no sprites were detected.
        
        Parameters:
            detected_sprites (Iterable): An iterable of rectangle objects (e.g., QRect or (x, y, width, height) tuples) representing detected sprite bounding boxes.
        """
        if detected_sprites:
            # پاک کردن selections و detections قبلی
            self.canvas.selected_cells = []
            self.canvas.detected_sprites = []
            
            # اضافه کردن sprites تشخیص داده شده به canvas
            for rect in detected_sprites:
                self.canvas.detected_sprites.append(rect)
            
            # آپدیت display
            self.canvas.update_display()
            
            # نمایش پیام
            count = len(detected_sprites)
            self.statusBar().showMessage(
                f"Auto-detected {count} sprites. Click on them to work with them."
            )
            
            # لاگ
            print(f"Detection finished: Found {count} sprites")
        else:
            self.statusBar().showMessage("No sprites detected in the image.")
            QMessageBox.information(
                self,
                "Detection Result",
                "No sprites were detected in the image."
            )
    
    def _clear_detections(self):
        """
        Clear all detected sprites and selected cells from the canvas.
        
        Also refreshes the canvas display and posts a "Cleared all detections." message to the status bar.
        """
        self.canvas.selected_cells = []
        self.canvas.detected_sprites = []
        self.canvas.update_display()
        
        self.statusBar().showMessage("Cleared all detections.")
    
    def _toggle_auto_detect_mode(self, checked):
        """
        Toggle between grid mode and auto-detect mode for the canvas.
        
        When enabled, disables the grid, enables auto-detect mode, updates the canvas display,
        and shows a status message. When disabled, enables the grid, disables auto-detect mode,
        updates the canvas display, and shows a status message.
        
        Parameters:
            checked (bool): `True` to enable auto-detect mode, `False` to enable grid mode.
        """
        if checked:
            # فعال کردن حالت auto-detect
            self.canvas.show_grid = False
            self.canvas.in_autodetect_mode = True
            self.statusBar().showMessage("Auto-detection mode enabled")
        else:
            # فعال کردن حالت grid
            self.canvas.show_grid = True
            self.canvas.in_autodetect_mode = False
            self.statusBar().showMessage("Grid mode enabled")
        
        self.canvas.update_display()
    
    def _toggle_grid_visibility(self, checked):
        """
        Toggle the canvas grid visibility.
        
        Parameters:
            checked (bool): True to show the grid, False to hide it.
        """
        self.canvas.show_grid = checked
        self.canvas.update_display()
        
        status = "visible" if checked else "hidden"
        self.statusBar().showMessage(f"Grid {status}")
    
    # ====== Event Handlers ======
    
    def _on_grid_cell_clicked(self, x, y, width, height):
        """
        Placeholder handler invoked when a grid cell is clicked; kept to satisfy signal connections.
        
        Parameters:
            x (int): X coordinate of the clicked cell (pixels).
            y (int): Y coordinate of the clicked cell (pixels).
            width (int): Width of the clicked cell (pixels).
            height (int): Height of the clicked cell (pixels)
        """
        # این متد برای consistency با signalها نگه داشته شده
        # منطق اصلی در کلاس Canvas پیاده‌سازی شده
        pass
    
    def _on_tree_item_clicked(self, item, column):
        """
        Handle clicks on items in the tree view and update the animation preview accordingly.
        
        If the clicked item is a group, collect all sprite pixmaps in that group and set them on the animation preview; if no sprites are found, the preview is cleared and a status message is shown. If the clicked item is an individual sprite, collect that sprite's pixmap(s) and display them in the preview with a status update.
        
        Parameters:
            item (QTreeWidgetItem): The tree item that was clicked.
            column (int): The index of the column that was clicked.
        """
        # چک کردن آیا آیتم یک گروه است یا خیر
        if self.tree_manager._is_group_item(item):
            # جمع آوری تمام اسپرایت های موجود در گروه
            sprite_pixmaps = []
            self.tree_manager.export_operations._collect_sprite_pixmaps(item, sprite_pixmaps)
            
            # تنظیم اسپرایت ها در پیش نمایش انیمیشن
            if sprite_pixmaps:
                self.animation_preview.set_sprites(sprite_pixmaps)
                self.statusBar().showMessage(f"Loaded {len(sprite_pixmaps)} sprites for animation preview")
            else:
                self.animation_preview.set_sprites([])
                self.statusBar().showMessage("No sprites in this group")
        else:
            # اگر آیتم اسپرایت است، فقط یک اسپرایت را نمایش می‌دهیم
            sprite_pixmaps = []
            self.tree_manager.export_operations._collect_sprite_pixmaps(item, sprite_pixmaps)
            
            if sprite_pixmaps:
                self.animation_preview.set_sprites(sprite_pixmaps)
                self.statusBar().showMessage(f"Showing sprite: {item.text(0)}")
    
    def _on_thumbnail_clicked(self, item):
        """
        Handle a thumbnail being clicked and update the status bar.
        
        Logs the clicked thumbnail's label and displays its text in the window's status bar for 3 seconds.
        
        Parameters:
            item (QTreeWidgetItem): The clicked thumbnail item; its text (column 0) is used for logging and status display.
        """
        print(f"Thumbnail clicked: {item.text(0)}")
        
        # نمایش اطلاعات sprite در status bar
        self.statusBar().showMessage(
            f"Selected: {item.text(0)}",
            3000  # نمایش برای 3 ثانیه
        )
    
    def closeEvent(self, event):
        """
        Handle the main window close event and perform resource cleanup.
        
        Performs necessary cleanup of application resources and accepts the provided close event.
        
        Parameters:
            event (QCloseEvent): The close event to accept.
        """
        # پاکسازی منابع
        self._cleanup_resources()
        
        # تایید بسته شدن
        event.accept()
        
        print("Application closed successfully")
    
    def _cleanup_resources(self):
        """
        Release and clear MainWindow resources used by the editor.
        
        Clears the canvas pixmap to free image memory, resets group counters, and invokes the sprite detector's `cleanup` method if a detector is present and provides that method.
        """
        # پاک کردن memory
        if hasattr(self, 'canvas'):
            self.canvas.pixmap = None
        
        # پاک کردن counters
        self.group_counters.clear()
        
        # پاک کردن worker threads
        if hasattr(self, 'sprite_detector'):
            # اگر sprite_detector قابلیت cleanup دارد
            if hasattr(self.sprite_detector, 'cleanup'):
                self.sprite_detector.cleanup()
    
    # ====== Utility Methods ======
    
    def _extract_sprite_pixmap(self, x, y, width, height):
        """
        Extract a cropped QPixmap from the canvas using the specified rectangle.
        
        Parameters:
            x (int): X coordinate of the top-left corner in canvas pixels.
            y (int): Y coordinate of the top-left corner in canvas pixels.
            width (int): Width of the rectangle in pixels.
            height (int): Height of the rectangle in pixels.
        
        Returns:
            QPixmap or None: The cropped pixmap if the canvas has a valid pixmap, otherwise `None`.
        """
        if hasattr(self.canvas, 'pixmap') and not self.canvas.pixmap.isNull():
            from PyQt6.QtCore import QRect
            sprite_rect = QRect(x, y, width, height)
            return self.canvas.pixmap.copy(sprite_rect)
        return None
    
    def update_properties_display(self, x, y, width, height):
        """
        Update the UI labels that display the selected sprite's position and size.
        
        Parameters:
            x (int): X-coordinate (pixels) of the sprite's top-left corner.
            y (int): Y-coordinate (pixels) of the sprite's top-left corner.
            width (int): Width (pixels) of the sprite.
            height (int): Height (pixels) of the sprite.
        """
        self.x_label.setText(str(x))
        self.y_label.setText(str(y))
        self.width_label.setText(str(width))
        self.height_label.setText(str(height))
    
    def reset_properties_display(self):
        """
        Reset the properties display fields to their default placeholder values.
        
        Sets the x, y, width, and height labels to "-" to indicate no selection.
        """
        self.x_label.setText("-")
        self.y_label.setText("-")
        self.width_label.setText("-")
        self.height_label.setText("-")