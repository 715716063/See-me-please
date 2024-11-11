# file_processor.py

import os
import shutil
import tempfile
import zipfile

from s3_handler import S3Handler
from audio_processor import AudioProcessor
from gpt_analyzer import GPTAnalyzer
from aws_pii_processor import AWSPIIProcessor
from paddleocr_pii_processor import PaddleOCRPIIProcessor

class FileProcessor:
    """Class for handling file processing operations."""
    def __init__(self, config):
        self.temp_dir = None
        self.config = config
        self.s3_handler = S3Handler(config)
        self.audio_processor = AudioProcessor(config)
        self.gpt_analyzer = GPTAnalyzer(config)
        
        # Initialize PII processor based on configuration
        if self.config.pii_reduction_model == "Sensitive text detection (Based on AWS)":
            self.pii_processor = AWSPIIProcessor(config)
        else:
            self.pii_processor = PaddleOCRPIIProcessor(config)

    def create_temp_dir(self):
        """Create a temporary directory."""
        if self.temp_dir is None or not os.path.exists(self.temp_dir):
            self.temp_dir = tempfile.mkdtemp()
        return self.temp_dir

    def process_file(self, file_name, progress_callback=None):
        temp_dir = self.create_temp_dir()

        try:
            # Step 1: Download and extract the video file
            if progress_callback:
                progress_callback("Downloading file...", 0)
            zip_path = os.path.join(temp_dir, file_name)
            self.s3_handler.download_file(file_name, zip_path)

            if progress_callback:
                progress_callback("Extracting files...", 10)

            # Extract video file
            video_path = None
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                video_files = [f for f in zip_ref.namelist() if f.endswith(('.mp4', '.mov', '.avi'))]
                if not video_files:
                    raise Exception("No video file found in the ZIP archive.")
                video_file_name = video_files[0]
                zip_ref.extract(video_file_name, temp_dir)
                video_path = os.path.join(temp_dir, video_file_name)

            if not os.path.exists(video_path):
                raise Exception("Failed to extract video file.")

            # Step 2: Convert the original video to WAV (extract audio)
            if progress_callback:
                progress_callback("Converting video to audio...", 20)

            wav_path = os.path.join(temp_dir, "audio.wav")
            self.audio_processor.convert_to_wav(video_path, wav_path)

            # Step 3: Transcribe audio
            if progress_callback:
                progress_callback("Transcribing audio...", 30)

            transcription_result = self.audio_processor.transcribe_audio(wav_path)

            # Save VTT and transcript files
            if progress_callback:
                progress_callback("Saving transcription...", 50)

            vtt_path = os.path.join(temp_dir, "transcription.vtt")
            transcript_path = os.path.join(temp_dir, "transcript.txt")

            self._save_vtt(transcription_result, vtt_path)
            self._convert_vtt_to_transcript(vtt_path, transcript_path)

            # Step 4: Analyze friction points
            if progress_callback:
                progress_callback("Analyzing friction points...", 60)

            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_text = f.read()

            analysis_result = self.gpt_analyzer.analyze_friction_points(transcript_text)
            analysis_path = os.path.join(temp_dir, "friction_points_analysis.txt")

            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(analysis_result)

            # Step 5: Perform PII Reduction on the original video
            if progress_callback:
                progress_callback("Processing video for PII...", 80)

            pii_processed_path = os.path.join(temp_dir, "pii_processed_video.mp4")
            self.pii_processor.process_video(
                video_path,
                pii_processed_path,
                lambda msg, prog: progress_callback(msg, 80 + int(prog * 0.2))
            )

            if progress_callback:
                progress_callback("Processing complete!", 100)

            # Return paths to all processed files, including the processed video
            return {
                'vtt_path': vtt_path,
                'transcript_path': transcript_path,
                'analysis_path': analysis_path,
                'processed_video_path': pii_processed_path
            }

        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")


    def _save_vtt(self, result, vtt_path):
        """Save transcription result as VTT file."""
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in result['segments']:
                start = self._format_time(segment['start'])
                end = self._format_time(segment['end'])
                text = segment['text'].strip()
                f.write(f"{start} --> {end}\n{text}\n\n")

    def _convert_vtt_to_transcript(self, vtt_path, transcript_path):
        """Convert VTT file to a readable transcript."""
        with open(vtt_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        transcript_lines = []
        current_timestamp = ""

        for line in lines:
            line = line.strip()
            if not line or line == "WEBVTT" or line.isdigit():
                continue
            if '-->' in line:
                current_timestamp = line
                continue
            if line:
                transcript_lines.append(f"[{current_timestamp}] {line}")

        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(transcript_lines))

    def _format_time(self, seconds):
        """Format time in seconds to VTT timestamp."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        return f"{int(hours):02}:{int(minutes):02}:{seconds:02}.{milliseconds:03}"

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
