# device_detector.py

import subprocess
import re


class DeviceDetector:
    def __init__(self, ffmpeg_path):
        self.ffmpeg_path = ffmpeg_path
        self.available_video_devices = []
        self.available_audio_devices = []

    def detect_devices(self):
        # Detect available video and audio devices using ffmpeg
        cmd = [self.ffmpeg_path, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        result = subprocess.run(cmd, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='ignore')

        video_device_re = re.compile(r'\[dshow.*\] *"(.*)" \(video\)')
        audio_device_re = re.compile(r'\[dshow.*\] *"(.*)" \(audio\)')

        video_devices = video_device_re.findall(result.stderr)
        audio_devices = audio_device_re.findall(result.stderr)

        self.available_video_devices = video_devices
        self.available_audio_devices = audio_devices

        return self.available_video_devices, self.available_audio_devices
