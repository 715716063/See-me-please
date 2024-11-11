# merger.py

import os
import subprocess


class Merger:
    def __init__(self, ffmpeg_path, save_directory):
        self.ffmpeg_path = ffmpeg_path
        self.save_directory = save_directory

    def merge_segments(self, segments, output_filename):
        if len(segments) > 1:
            list_file = os.path.join(self.save_directory, f"{output_filename}_list.txt")
            with open(list_file, 'w') as f:
                for segment in segments:
                    f.write(f"file '{segment}'\n")
            merge_cmd = [
                self.ffmpeg_path, '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
                '-c', 'copy', os.path.join(self.save_directory, f"{output_filename}.mp4")
            ]
            subprocess.run(merge_cmd)
            return os.path.join(self.save_directory, f"{output_filename}.mp4")
        else:
            return segments[0]

    def merge_audio_video(self, video_file, audio_file, output_file):
        merge_command = [
            self.ffmpeg_path, '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy', '-c:a', 'aac',
            output_file
        ]
        subprocess.run(merge_command)
        print(f"Final output saved to: {output_file}")
