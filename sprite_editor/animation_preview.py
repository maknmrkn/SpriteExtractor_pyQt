from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpinBox
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import QFrame


class AnimationPreviewWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(200, 200)  # Fixed size for the preview area
        
        layout = QVBoxLayout(self)
        
        # Label to display the current sprite
        self.sprite_label = QLabel()
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setMinimumSize(150, 150)
        layout.addWidget(self.sprite_label)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._toggle_animation)
        controls_layout.addWidget(self.play_button)
        
        # Frame rate control
        self.fps_label = QLabel("FPS:")
        controls_layout.addWidget(self.fps_label)
        
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 30)
        self.fps_spinbox.setValue(10)
        self.fps_spinbox.valueChanged.connect(self._update_timer_interval)
        controls_layout.addWidget(self.fps_spinbox)
        
        layout.addLayout(controls_layout)
        
        # Animation variables
        self.sprites = []
        self.current_frame = 0
        self.is_playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_frame)
        
        # Set initial state
        self._update_timer_interval()
        self.sprite_label.setText("No Animation")
        
    def set_sprites(self, sprites):
        """Set the list of sprites for the animation"""
        self.sprites = sprites
        self.current_frame = 0
        if self.sprites:
            self.sprite_label.setPixmap(self.sprites[0])
        else:
            self.sprite_label.setText("No Frames")
    
    def _toggle_animation(self):
        """Toggle between play and pause states"""
        if self.is_playing:
            self.timer.stop()
            self.play_button.setText("Play")
        else:
            if self.sprites:
                self.timer.start()
                self.play_button.setText("Pause")
        self.is_playing = not self.is_playing
    
    def _next_frame(self):
        """Show the next frame in the animation"""
        if self.sprites:
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.sprite_label.setPixmap(self.sprites[self.current_frame])
    
    def _update_timer_interval(self):
        """Update the timer interval based on the FPS value"""
        fps = self.fps_spinbox.value()
        interval = 1000 // fps  # Convert FPS to milliseconds
        self.timer.setInterval(interval)