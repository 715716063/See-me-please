# camera_window.py

import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize
from PyQt5.QtGui import QImage, QPixmap


class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cap = None
        self.dragging = False
        self.offset = QPoint()
        self.minimized = False  # Tracks if the window is minimized
        self.original_size = QSize(240, 180)  # Stores the original window size
        self.is_hovering = False  # Tracks if the mouse is over the window
        self.minimized_window = None  # Stores the minimized window
        self.minimized_window_position = None  # Stores the position of the minimized window

    def init_ui(self):
        # Set the window to be frameless and have a transparent background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Set window background to transparent

        self.setGeometry(100, 100, 240, 180)

        self.layout = QVBoxLayout(self)
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(240, 180)
        self.layout.addWidget(self.video_label)

        # Add minimize button
        self.minimize_button = QPushButton(self)
        self.minimize_button.setFixedSize(20, 20)
        # Ensure the button has no border and transparent background
        self.minimize_button.setStyleSheet("background-color: rgba(255, 255, 255, 50); border: none;")
        self.minimize_button.setToolTip("Minimize Window")  # Tooltip on hover
        self.minimize_button.clicked.connect(self.minimize_camera)
        self.minimize_button.move(15, 15)  # Move the button slightly from the top-left corner

    def start_camera_stream(self):
        # Position the camera window at the top-right corner of the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        self.move(screen_width - self.width() - 10, 10)
        self.show()

    def minimize_camera(self):
        if not self.minimized:
            self.minimized_window_position = self.pos()  # Record the position when minimized
            self.hide()  # Hide the camera window
            self.create_minimized_window()  # Create minimized window

    def create_minimized_window(self):
        # Create the minimized window
        self.minimized_window = QWidget()
        self.minimized_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.minimized_window.setGeometry(self.minimized_window_position.x(), self.minimized_window_position.y(), 200, 50)  # Set size and position
        self.minimized_window.setStyleSheet("background-color: rgba(100, 100, 100, 150);")  # Set transparent background

        layout = QVBoxLayout(self.minimized_window)
        restore_button = QPushButton("Restore Camera", self.minimized_window)
        restore_button.setStyleSheet("background-color: rgba(255, 255, 255, 80); border: none;")
        restore_button.setFixedSize(150, 30)
        layout.addWidget(restore_button)

        restore_button.clicked.connect(self.restore_camera_from_minimized_window)

        # Add dragging functionality
        self.minimized_window.mousePressEvent = self.minimized_mouse_press_event
        self.minimized_window.mouseMoveEvent = self.minimized_mouse_move_event
        self.minimized_window.mouseReleaseEvent = self.minimized_mouse_release_event

        self.minimized_window.show()

    def restore_camera_from_minimized_window(self):
        # Restore the camera window
        if self.minimized_window:
            self.minimized_window_position = self.minimized_window.pos()  # Record minimized window position
            self.minimized_window.close()  # Close minimized window
            self.minimized_window = None  # Clear reference
        # Move camera window to minimized window position
        self.move(self.minimized_window_position)
        self.show()  # Show camera window
        self.minimized = False  # Reset minimized state

    # Event handlers for dragging minimized window
    def minimized_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def minimized_mouse_move_event(self, event):
        if self.dragging:
            self.minimized_window.move(event.globalPos() - self.offset)

    def minimized_mouse_release_event(self, event):
        self.dragging = False

    def update_frame(self, frame):
        if frame is not None and not self.minimized:  # Update frame only when not minimized
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def enterEvent(self, event):
        # Show minimize button when mouse enters window
        self.is_hovering = True
        self.minimize_button.show()

    def leaveEvent(self, event):
        # Hide minimize button when mouse leaves window
        self.is_hovering = False
        self.minimize_button.hide()
