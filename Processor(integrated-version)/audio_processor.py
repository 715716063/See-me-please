# audio_processor.py

import os
import torch
import whisper
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

class AudioProcessor:
    """Class for handling audio processing operations."""
    def __init__(self, config):
        self.device = config.device
        print(f"AudioProcessor using device: {self.device}")
        self.model = whisper.load_model("medium", device=self.device)

    def convert_to_wav(self, input_path, output_path):
        """Convert audio or video file to WAV format."""
        try:
            # Try to load as a video file
            video_clip = VideoFileClip(input_path)
            if video_clip.audio is not None:
                video_clip.audio.write_audiofile(output_path, verbose=False, logger=None)
                video_clip.close()
            else:
                # If no audio track, try loading directly as audio
                audio = AudioSegment.from_file(input_path)
                audio.export(output_path, format="wav")
        except Exception as e:
            try:
                # Alternative method using pydub directly
                audio = AudioSegment.from_file(input_path)
                audio.export(output_path, format="wav")
            except Exception as inner_e:
                raise Exception(f"Failed to convert audio: {str(e)}; {str(inner_e)}")

    def transcribe_audio(self, audio_path):
        """Transcribe audio file using Whisper model."""
        try:
            return self.model.transcribe(audio_path, language='en')
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
