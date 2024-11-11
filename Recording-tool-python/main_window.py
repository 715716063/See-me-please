# main_window.py

import os
import sys
import zipfile
import boto3
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox, QApplication, QDesktopWidget, QDialog)
from PyQt5.QtGui import QIcon
from recorder import Recorder
from camera_window import CameraWindow
from red_border_window import RedBorderWindow
from option_box_window import OptionBoxWindow
from settings_dialog import SettingsDialog
from feedback_dialog import FeedbackDialog




class MainWindow(QMainWindow):
    def __init__(self, save_directory, ffmpeg_path, aws_access_key_id, aws_secret_access_key, s3_bucket_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_directory = save_directory
        self.ffmpeg_path = ffmpeg_path
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_bucket_name = s3_bucket_name
        self.init_ui()
        self.recorder = None
        self.camera_window = None
        self.red_border_window = None
        self.option_box_window = None
        self.current_settings = {
            'save_directory': self.save_directory,
            'video_quality': 'High',
            'use_camera': True,
            'mirror_camera': False,
            'video_device': '',
            'audio_device': '',
            'available_video_devices': [],
            'available_audio_devices': [],
            'upload_to_cloud': True
        }

    def init_ui(self):
        # Set up the main window UI
        self.setWindowTitle('Screen Recording Tool')
        self.setGeometry(200, 200, 300, 150)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.start_button = QPushButton("Start Recording", self)
        self.start_button.clicked.connect(self.start_recording)

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.start_button)
        layout.addWidget(self.settings_button)

        self.center_window()

    def center_window(self):
        # Center the window
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_settings(self):
        # Update available devices before opening settings dialog
        self.update_available_devices()
        settings_dialog = SettingsDialog(self, self.current_settings)
        if settings_dialog.exec_() == QDialog.Accepted:
            self.current_settings = settings_dialog.get_settings()
            print("Settings updated:", self.current_settings)

    def update_available_devices(self):
        # Create a temporary Recorder to get available devices
        temp_recorder = Recorder(save_directory=self.save_directory, ffmpeg_path=self.ffmpeg_path)
        temp_recorder.detect_devices()
        self.current_settings['available_video_devices'] = temp_recorder.available_video_devices
        self.current_settings['available_audio_devices'] = temp_recorder.available_audio_devices

    def start_recording(self):
        video_quality = self.current_settings['video_quality'].lower()
        use_camera = self.current_settings['use_camera']
        mirror_camera = self.current_settings['mirror_camera']
        save_directory = self.current_settings['save_directory'] or self.save_directory
        video_device = self.current_settings['video_device']
        audio_device = self.current_settings['audio_device']
        upload_to_cloud = self.current_settings.get('upload_to_cloud', False)

        if not save_directory:
            QMessageBox.warning(self, "Error", "Please specify a save directory in Settings.")
            return

        msg = QMessageBox()
        msg.setWindowTitle("Start Recording")
        if use_camera:
            msg.setText("Recording is about to start, including the camera.")
        else:
            msg.setText("Recording is about to start.")
        msg.exec_()

        # Initialize the Recorder
        self.recorder = Recorder(
            save_directory=save_directory,
            ffmpeg_path=self.ffmpeg_path,
            video_quality=video_quality,
            use_camera=use_camera,
            mirror_camera=mirror_camera,
            video_device=video_device,
            audio_device=audio_device,
            upload_to_cloud=upload_to_cloud,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            s3_bucket_name=self.s3_bucket_name
        )

        if use_camera:
            self.camera_window = CameraWindow()
            self.recorder.set_camera_window(self.camera_window)
            self.camera_window.start_camera_stream()

        self.start_red_border()

        self.recorder.start_recording()
        self.start_button.setDisabled(True)

        # Show the option box window
        self.option_box_window = OptionBoxWindow(self.recorder)
        self.option_box_window.stop_signal.connect(self.handle_stop_signal)
        self.option_box_window.show()

    def handle_stop_signal(self):
        recording_directory = self.recorder.save_directory if self.recorder else None
        self.recorder = None  # Ensure recorder is reset
        self.stop_red_border()
        self.start_button.setDisabled(False)

        # After recording ends, ask user if they want to provide feedback
        reply = QMessageBox.question(self, 'Recording Finished',
                                     "Recording has finished. Would you like to provide feedback?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            feedback_dialog = FeedbackDialog(self, save_directory=recording_directory)
            feedback_dialog.exec_()
            # Feedback saved
        else:
            QMessageBox.information(self, "Recording Stopped", "Recording has been saved.")

        # Now compress the necessary files into a zip file
        zip_file_path = recording_directory + ".zip"
        self.compress_selected_files_to_zip(recording_directory, zip_file_path)

        # Upload the zip file to S3
        self.upload_file_to_s3(zip_file_path)

        # Close option box window and camera window (if not already closed)
        if self.option_box_window:
            self.option_box_window.close()
            self.option_box_window = None
        if self.camera_window:
            self.camera_window.close()
            self.camera_window = None

    def compress_selected_files_to_zip(self, directory_path, output_zip_path):
        try:
            # Define the list of files to include
            files_to_include = [
                os.path.join(directory_path, "final_output.mp4"),
                os.path.join(directory_path, "merged_audio.mp4"),
                os.path.join(directory_path, "merged_camera.mp4"),
                os.path.join(directory_path, "feedback.txt")
            ]

            # Include comment files
            for filename in os.listdir(directory_path):
                if filename.startswith("comment") and filename.endswith(".txt"):
                    files_to_include.append(os.path.join(directory_path, filename))

            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_include:
                    if os.path.exists(file_path):
                        # Write file to zip, preserving the relative path
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                        print(f"Added {file_path} to zip.")
                    else:
                        print(f"File not found and skipped: {file_path}")
            print(f"Selected files compressed into ZIP file: {output_zip_path}")
        except Exception as e:
            print(f"An error occurred while compressing selected files: {e}")

    def upload_file_to_s3(self, file_path):
        # Upload the file to AWS S3
        try:
            s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key_id,
                                   aws_secret_access_key=self.aws_secret_access_key)
            s3.upload_file(file_path, self.s3_bucket_name, os.path.basename(file_path))
            print(f"File {file_path} uploaded to S3 bucket {self.s3_bucket_name}")
            QMessageBox.information(self, "Upload Successful", f"File uploaded to S3 bucket {self.s3_bucket_name}.")
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")
            QMessageBox.warning(self, "Upload Failed", f"An error occurred while uploading to S3: {e}")

    def start_red_border(self):
        # Show red border
        self.red_border_window = RedBorderWindow()
        self.red_border_window.show()

    def stop_red_border(self):
        # Remove red border
        if self.red_border_window:
            self.red_border_window.close()
            self.red_border_window = None
