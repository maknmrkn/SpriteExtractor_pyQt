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
        """تنظیمات اولیه ویندوز"""
        self.setWindowTitle("Sprite Editor")
        self.resize(1200, 800)
        
        # تنظیمات geometry
        self.setMinimumSize(800, 600)
        
    def _init_managers(self):
        """مقداردهی اولیه managerها"""
        # ایجاد managerها
        self.widget_initializer = WidgetInitializer(self)
        self.layout_manager = None
        self.menu_manager = MenuManager(self)
        self.toolbar_manager = ToolbarManager(self)
        self.signal_manager = SignalManager(self)
        self.style_manager = StyleManager(self)
    
    def _setup_ui(self):
        """راه‌اندازی رابط کاربری"""
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
        """اختصاص ویجت‌ها به attributes کلاس"""
        for name, widget in widgets.items():
            setattr(self, name, widget)
    
    def _connect_signals(self):
        """اتصال signalها"""
        self.signal_manager.setup_connections()
    
    def _apply_styles(self):
        """اعمال استایل به برنامه"""
        self.style_manager.apply_theme('light ')
    
    def _setup_status_bar(self):
        """تنظیم status bar"""
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
        """باز کردن فایل تصویر"""
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
        """تشخیص خودکار فریم‌ها"""
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
        """پردازش تشخیص خودکار کامل شده"""
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
        """پاک کردن تشخیص‌ها"""
        self.canvas.selected_cells = []
        self.canvas.detected_sprites = []
        self.canvas.update_display()
        
        self.statusBar().showMessage("Cleared all detections.")
    
    def _toggle_auto_detect_mode(self, checked):
        """تغییر بین حالت grid و auto-detect"""
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
        """تغییر visibility گرید"""
        self.canvas.show_grid = checked
        self.canvas.update_display()
        
        status = "visible" if checked else "hidden"
        self.statusBar().showMessage(f"Grid {status}")
    
    # ====== Event Handlers ======
    
    def _on_grid_cell_clicked(self, x, y, width, height):
        """Handler برای کلیک روی سلول گرید"""
        # این متد برای consistency با signalها نگه داشته شده
        # منطق اصلی در کلاس Canvas پیاده‌سازی شده
        pass
    
    def _on_tree_item_clicked(self, item, column):
        """Handler برای کلیک روی آیتم درختی"""
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
        """Handler برای کلیک روی thumbnail"""
        print(f"Thumbnail clicked: {item.text(0)}")
        
        # نمایش اطلاعات sprite در status bar
        self.statusBar().showMessage(
            f"Selected: {item.text(0)}",
            3000  # نمایش برای 3 ثانیه
        )
    
    def closeEvent(self, event):
        """Handler برای بسته شدن برنامه"""
        # پاکسازی منابع
        self._cleanup_resources()
        
        # تایید بسته شدن
        event.accept()
        
        print("Application closed successfully")
    
    def _cleanup_resources(self):
        """پاکسازی منابع"""
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
        """استخراج pixmap از canvas"""
        if hasattr(self.canvas, 'pixmap') and not self.canvas.pixmap.isNull():
            from PyQt6.QtCore import QRect
            sprite_rect = QRect(x, y, width, height)
            return self.canvas.pixmap.copy(sprite_rect)
        return None
    
    def update_properties_display(self, x, y, width, height):
        """آپدیت نمایش properties"""
        self.x_label.setText(str(x))
        self.y_label.setText(str(y))
        self.width_label.setText(str(width))
        self.height_label.setText(str(height))
    
    def reset_properties_display(self):
        """بازنشانی نمایش properties"""
        self.x_label.setText("-")
        self.y_label.setText("-")
        self.width_label.setText("-")
        self.height_label.setText("-")