# red_border_window.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor


class RedBorderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the red border window UI
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make window non-interactive
        self.setWindowState(Qt.WindowFullScreen)

    def paintEvent(self, event):
        # Draw a red border
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 10, Qt.SolidLine))
        painter.drawRect(self.rect())
