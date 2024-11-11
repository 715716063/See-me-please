# screen_recorder.py

import subprocess


class ScreenRecorder:
    def __init__(self, ffmpeg_path, output_path, settings):
        self.ffmpeg_path = ffmpeg_path
        self.output_path = output_path
        self.settings = settings
        self.process = None

    def start(self):
        # Start screen recording using ffmpeg
        try:
            self.process = subprocess.Popen([
                self.ffmpeg_path, '-y', '-f', 'gdigrab', '-framerate', str(self.settings["framerate"]),
                '-i', 'desktop', '-s', self.settings["resolution"], '-b:v', self.settings["bitrate"],
                '-pix_fmt', 'yuv420p', '-c:v', 'h264_nvenc', '-preset', 'fast',
                '-threads', '0', self.output_path
            ], stdin=subprocess.PIPE)

            print("Screen recording started.")
        except Exception as e:
            print(f"An error occurred while starting screen recording: {e}")

    def stop(self):
        # Stop screen recording
        if self.process:
            self.process.stdin.write('q'.encode())
            self.process.stdin.flush()
            self.process.wait()
            self.process = None
            print("Screen recording stopped.")
