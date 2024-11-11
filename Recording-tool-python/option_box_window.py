# option_box_window.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication, QDialog
from PyQt5.QtCore import Qt, pyqtSignal
from comment_dialog import CommentDialog


class OptionBoxWindow(QWidget):
    stop_signal = pyqtSignal()  # Signal to notify MainWindow to stop recording

    def __init__(self, recorder):
        super().__init__()
        self.recorder = recorder

        self.init_ui()

    def init_ui(self):
        # Set window flags to keep the window always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        self.setFixedHeight(50)
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        option_box_width = int(screen_width * 0.4)  # Occupies 40% of screen width
        self.setGeometry((screen_width - option_box_width) // 2, 0, option_box_width, 50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.pause_button = QPushButton("Pause Recording")
        self.start_button = QPushButton("Resume Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.comment_button = QPushButton("Comment")

        layout.addWidget(self.pause_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.comment_button)

        self.pause_button.clicked.connect(self.pause_recording)
        self.start_button.clicked.connect(self.resume_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.comment_button.clicked.connect(self.add_comment)

        self.start_button.setDisabled(True)  # Disable resume button initially

        # Adjust window and button transparency
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 220);  /* Increase opacity */
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 240);  /* Increase button opacity */
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 255);
            }
        """)

    def pause_recording(self):
        self.recorder.pause_recording()
        self.pause_button.setDisabled(True)
        self.start_button.setDisabled(False)

    def resume_recording(self):
        self.recorder.resume_recording()
        self.pause_button.setDisabled(False)
        self.start_button.setDisabled(True)

    def stop_recording(self):
        self.recorder.stop_recording()
        self.close()
        self.stop_signal.emit()  # Notify MainWindow to update UI

    def add_comment(self):
        # Open CommentDialog to input comment
        comment_dialog = CommentDialog(None, save_directory=self.recorder.save_directory, comment_number=self.recorder.comment_count)
        if comment_dialog.exec_() == QDialog.Accepted:
            self.recorder.comment_count += 1
