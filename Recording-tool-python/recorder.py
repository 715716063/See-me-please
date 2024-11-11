# recorder.py

import os
import time
import subprocess
from screen_recorder import ScreenRecorder
from audio_recorder import AudioRecorder
from camera_recorder import CameraRecorder
from device_detector import DeviceDetector
from merger import Merger
import boto3


class Recorder:
    def __init__(self, save_directory, ffmpeg_path, video_quality="normal", use_camera=False,
                 mirror_camera=False, video_device=None, audio_device=None, upload_to_cloud=False,
                 aws_access_key_id=None, aws_secret_access_key=None, s3_bucket_name=None):
        # Initialize the recorder
        self.save_directory = save_directory
        self.ffmpeg_path = ffmpeg_path
        self.video_quality = video_quality
        self.use_camera = use_camera
        self.mirror_camera = mirror_camera
        self.video_device = video_device
        self.audio_device = audio_device
        self.upload_to_cloud = upload_to_cloud
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_bucket_name = s3_bucket_name

        self.camera_window = None
        self.is_paused = False  # Track pause state
        self.comment_count = 1  # Initialize comment count

        # For handling recording segments
        self.video_segments = []
        self.audio_segments = []
        self.camera_segments = []
        self.segment_index = 0

        # Quality settings
        self.quality_settings = {
            "low": {"bitrate": "500k", "framerate": 15, "resolution": "640x360"},
            "normal": {"bitrate": "1000k", "framerate": 30, "resolution": "1280x720"},
            "high": {"bitrate": "2500k", "framerate": 60, "resolution": "1920x1080"}
        }

        self.settings = self.quality_settings.get(self.video_quality, self.quality_settings["normal"])

        # Initialize recorders
        self.screen_recorder = None
        self.audio_recorder = None
        self.camera_recorder = None

        # Device detector
        self.device_detector = DeviceDetector(ffmpeg_path)
        self.available_video_devices = []
        self.available_audio_devices = []

    def detect_devices(self):
        self.available_video_devices, self.available_audio_devices = self.device_detector.detect_devices()
        if self.available_video_devices:
            if not self.video_device or self.video_device not in self.available_video_devices:
                self.video_device = self.available_video_devices[0]
            print(f"Detected video device: {self.video_device}")
        else:
            print("No video devices detected")

        if self.available_audio_devices:
            if not self.audio_device or self.audio_device not in self.available_audio_devices:
                self.audio_device = self.available_audio_devices[0]
            print(f"Detected audio device: {self.audio_device}")
        else:
            print("No audio devices detected")

    def start_recording(self):
        try:
            # Only detect devices once
            if self.segment_index == 0:
                self.detect_devices()

            if not self.audio_device:
                print("No audio device found for recording")
                return

            # Increment segment index
            self.segment_index += 1

            # Create a timestamped directory only once
            if self.segment_index == 1:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                self.save_directory = os.path.join(self.save_directory, timestamp)
                os.makedirs(self.save_directory, exist_ok=True)

            # Set output file paths for this segment
            video_output_segment = os.path.join(self.save_directory, f"screen_segment{self.segment_index}.mp4")
            audio_output_segment = os.path.join(self.save_directory, f"audio_segment{self.segment_index}.mp4")
            camera_output_segment = os.path.join(self.save_directory, f"camera_segment{self.segment_index}.mp4") if self.use_camera else None

            # Append to segments list
            self.video_segments.append(video_output_segment)
            self.audio_segments.append(audio_output_segment)
            if self.use_camera:
                self.camera_segments.append(camera_output_segment)

            # Start screen recording
            self.screen_recorder = ScreenRecorder(self.ffmpeg_path, video_output_segment, self.settings)
            self.screen_recorder.start()

            # Start audio recording
            self.audio_recorder = AudioRecorder(self.ffmpeg_path, audio_output_segment, self.audio_device)
            self.audio_recorder.start()

            # Start camera recording if enabled
            if self.use_camera:
                self.camera_recorder = CameraRecorder(camera_output_segment, self.video_device, self.mirror_camera, self.camera_window)
                self.camera_recorder.start()

            print("Recording segment started successfully")
        except Exception as e:
            print(f"An error occurred while starting recording: {e}")

    def pause_recording(self):
        try:
            # Stop current recording
            if self.screen_recorder:
                self.screen_recorder.stop()
            if self.audio_recorder:
                self.audio_recorder.stop()
            if self.use_camera and self.camera_recorder:
                self.camera_recorder.stop()

            self.is_paused = True
            print("Recording paused")
        except Exception as e:
            print(f"An error occurred while pausing recording: {e}")

    def resume_recording(self):
        try:
            self.start_recording()  # Start a new recording segment
            self.is_paused = False
            print("Recording resumed")
        except Exception as e:
            print(f"An error occurred while resuming recording: {e}")

    def stop_recording(self):
        try:
            # Stop current recording
            if self.screen_recorder:
                self.screen_recorder.stop()
            if self.audio_recorder:
                self.audio_recorder.stop()
            if self.use_camera and self.camera_recorder:
                self.camera_recorder.stop()
                if self.camera_window:
                    self.camera_window.close()
                    self.camera_window = None

            self.merge_recordings()
            print("Recording stopped successfully")
        except Exception as e:
            print(f"An error occurred while stopping recording: {e}")

    def merge_recordings(self):
        merger = Merger(self.ffmpeg_path, self.save_directory)

        # Merge video segments
        merged_video = merger.merge_segments(self.video_segments, "merged_video")

        # Merge audio segments
        merged_audio = merger.merge_segments(self.audio_segments, "merged_audio")

        # Merge video and audio
        output_file = os.path.join(self.save_directory, "final_output.mp4")
        merger.merge_audio_video(merged_video, merged_audio, output_file)

        # Merge camera segments if used
        if self.use_camera and self.camera_segments:
            merger.merge_segments(self.camera_segments, "merged_camera")
            # Handle merged camera video as needed

        if self.upload_to_cloud:
            self.upload_to_s3(output_file)

    def set_camera_window(self, window):
        self.camera_window = window

    def upload_to_s3(self, file_path):
        # Upload the file to AWS S3
        try:
            s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key_id,
                                   aws_secret_access_key=self.aws_secret_access_key)
            s3.upload_file(file_path, self.s3_bucket_name, os.path.basename(file_path))
            print(f"File {file_path} uploaded to S3 bucket {self.s3_bucket_name}")
        except Exception as e:
            print(f"An error occurred while uploading to S3: {e}")
