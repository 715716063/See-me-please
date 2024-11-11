# audio_recorder.py

import subprocess


class AudioRecorder:
    def __init__(self, ffmpeg_path, output_path, audio_device):
        self.ffmpeg_path = ffmpeg_path
        self.output_path = output_path
        self.audio_device = audio_device
        self.process = None

    def start(self):
        # Start audio recording using ffmpeg
        try:
            audio_device_escaped = self.audio_device.replace('\\', '\\\\')
            self.process = subprocess.Popen([
                self.ffmpeg_path, '-y', '-f', 'dshow', '-i', f'audio={audio_device_escaped}',
                '-c:a', 'aac', '-b:a', '192k', self.output_path
            ], stdin=subprocess.PIPE)
            print("Audio recording started.")
        except Exception as e:
            print(f"An error occurred while starting audio recording: {e}")

    def stop(self):
        # Stop audio recording
        if self.process:
            self.process.stdin.write('q'.encode())
            self.process.stdin.flush()
            self.process.wait()
            self.process = None
            print("Audio recording stopped.")
