# comment_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
import os
import time


class CommentDialog(QDialog):
    def __init__(self, parent=None, save_directory=None, comment_number=1):
        super().__init__(parent)
        self.setWindowTitle("Add Comment")
        self.save_directory = save_directory
        self.comment_number = comment_number
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Please enter your comment:")
        layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_comment)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_comment(self):
        comment_text = self.text_edit.toPlainText()
        if comment_text.strip():
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            comment_filename = f"comment{self.comment_number}.txt"
            comment_file = os.path.join(self.save_directory, comment_filename)
            with open(comment_file, 'w', encoding='utf-8') as f:
                f.write(f"Timestamp: {timestamp}\n")
                f.write(comment_text)
            QMessageBox.information(self, "Comment Saved", f"Your comment has been saved as {comment_filename}.")
            self.accept()
        else:
            QMessageBox.warning(self, "Comment is Empty", "Please enter your comment before submitting.")
