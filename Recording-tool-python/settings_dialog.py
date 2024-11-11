# settings_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, QComboBox,
                             QCheckBox, QLineEdit, QHBoxLayout, QPushButton, QFileDialog)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.current_settings = current_settings if current_settings else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create tabs
        self.tab_widget = QTabWidget()

        # Recording Settings Tab
        self.recording_settings_tab = self.create_recording_settings_tab()
        self.tab_widget.addTab(self.recording_settings_tab, "Recording Settings")

        # Device Settings Tab
        self.device_settings_tab = self.create_device_settings_tab()
        self.tab_widget.addTab(self.device_settings_tab, "Device Settings")

        # Storage Settings Tab
        self.storage_settings_tab = self.create_storage_settings_tab()
        self.tab_widget.addTab(self.storage_settings_tab, "Storage Settings")

        # Add tabs to the main layout
        layout.addWidget(self.tab_widget)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_recording_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        # Video quality selection
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Normal", "High"])
        self.quality_combo.setCurrentText(self.current_settings.get('video_quality', 'High'))
        layout.addRow("Select Video Quality:", self.quality_combo)

        # Enable camera
        self.camera_checkbox = QCheckBox("Enable Camera")
        self.camera_checkbox.setChecked(self.current_settings.get('use_camera', True))
        layout.addRow(self.camera_checkbox)

        # Mirror camera
        self.mirror_checkbox = QCheckBox("Mirror Camera")
        self.mirror_checkbox.setChecked(self.current_settings.get('mirror_camera', False))
        layout.addRow(self.mirror_checkbox)

        tab.setLayout(layout)
        return tab

    def create_device_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        # Camera device selection
        self.video_device_combo = QComboBox()
        self.video_device_combo.addItems(self.current_settings.get('available_video_devices', []))
        self.video_device_combo.setCurrentText(self.current_settings.get('video_device', ''))
        layout.addRow("Select Camera Device:", self.video_device_combo)

        # Audio device selection
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.addItems(self.current_settings.get('available_audio_devices', []))
        self.audio_device_combo.setCurrentText(self.current_settings.get('audio_device', ''))
        layout.addRow("Select Audio Device:", self.audio_device_combo)

        tab.setLayout(layout)
        return tab

    def create_storage_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        # Save path selection
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_settings.get('save_directory', ''))
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        layout.addRow("Save Directory:", path_layout)

        # Cloud upload option
        self.upload_checkbox = QCheckBox("Upload recordings to cloud")
        self.upload_checkbox.setChecked(self.current_settings.get('upload_to_cloud', True))
        layout.addRow(self.upload_checkbox)

        tab.setLayout(layout)
        return tab

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.path_edit.text())
        if directory:
            self.path_edit.setText(directory)

    def get_settings(self):
        return {
            'video_quality': self.quality_combo.currentText(),
            'use_camera': self.camera_checkbox.isChecked(),
            'mirror_camera': self.mirror_checkbox.isChecked(),
            'video_device': self.video_device_combo.currentText(),
            'audio_device': self.audio_device_combo.currentText(),
            'save_directory': self.path_edit.text(),
            'upload_to_cloud': self.upload_checkbox.isChecked(),
        }
