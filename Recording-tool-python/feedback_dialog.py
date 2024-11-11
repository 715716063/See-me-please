# feedback_dialog.py

import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox


class FeedbackDialog(QDialog):
    def __init__(self, parent=None, save_directory=None):
        super().__init__(parent)
        self.setWindowTitle("Feedback")
        self.save_directory = save_directory
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Please provide your feedback:")
        layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_feedback(self):
        feedback_text = self.text_edit.toPlainText()
        if feedback_text.strip():
            feedback_file = os.path.join(self.save_directory, "feedback.txt")
            with open(feedback_file, 'w', encoding='utf-8') as f:
                f.write(feedback_text)
            QMessageBox.information(self, "Feedback Submitted", "Your feedback has been saved.")
            self.accept()
        else:
            QMessageBox.warning(self, "Feedback is Empty", "Please enter your feedback before submitting.")
