# aws_pii_processor.py

import io
import boto3
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from moviepy.editor import VideoFileClip
import numpy as np

class AWSPIIProcessor:
    """Class for handling PII detection and reduction using AWS services."""
    def __init__(self, config):
        self.config = config
        self.aws_client = boto3.client(
            'rekognition',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name
        )
        self.comp_detect = boto3.client(
            'comprehend',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name
        )

    def detect_pii_from_text(self, text, language_code="en"):
        """Detect PII entities in text using AWS Comprehend."""
        try:
            response = self.comp_detect.detect_pii_entities(
                Text=text,
                LanguageCode=language_code
            )
            return response['Entities']
        except Exception as e:
            raise Exception(f"PII detection failed: {str(e)}")

    def detect_text_from_image(self, image):
        """Detect text in image using AWS Rekognition."""
        try:
            image_bytes = self._pil_to_bytes(image)
            response = self.aws_client.detect_text(
                Image={'Bytes': image_bytes}
            )
            text_detections = response['TextDetections']
            text_corpus = []
            text_bounding_box = {}
            for text in text_detections:
                if text["Type"] == 'WORD':
                    detected_text = text['DetectedText']
                    text_corpus.append(detected_text)
                    text_bounding_box[detected_text] = text["Geometry"]["BoundingBox"]
            final_text_corpus = " ".join(text_corpus)
            return final_text_corpus, text_bounding_box
        except Exception as e:
            raise Exception(f"Text detection failed: {str(e)}")

    def _pil_to_bytes(self, image, format="PNG"):
        """Convert PIL image to bytes."""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    def _blur_mask(self, image, box):
        """Apply blur mask to a specific area of the image."""
        img_width, img_height = image.size
        left = img_width * box['Left']
        top = img_height * box['Top']
        width = img_width * box['Width']
        height = img_height * box['Height']

        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([left, top, left + width, top + height], fill=255)
        blurred = image.filter(ImageFilter.GaussianBlur(20))
        image.paste(blurred, mask=mask)
        return image

    def process_frame(self, image):
        """Process a single frame to detect and blur PII."""
        try:
            # image is a PIL Image
            text, text_bounding_box = self.detect_text_from_image(image)
            entities = self.detect_pii_from_text(text)
            for entity in entities:
                target_text = text[entity['BeginOffset']:entity['EndOffset']]
                if target_text in text_bounding_box:
                    box = text_bounding_box[target_text]
                    image = self._blur_mask(image, box)
            return image
        except Exception as e:
            raise Exception(f"Frame processing failed: {str(e)}")

    def process_video(self, input_path, output_path, progress_callback=None):
        try:
            video = VideoFileClip(input_path)
            audio = video.audio

            total_frames = int(video.duration * video.fps)
            current_frame = 0

            def process_frame(frame):
                nonlocal current_frame
                # Convert frame to PIL Image
                image = Image.fromarray(frame)
                # Process the image (blur PII)
                processed_image = self.process_frame(image)
                # Convert back to numpy array
                result_frame = np.array(processed_image)
                current_frame += 1
                if progress_callback:
                    progress = int((current_frame / total_frames) * 100)
                    progress_callback(f"Processing frame {current_frame}/{total_frames}", progress)
                return result_frame

            # Apply frame processing
            processed_video = video.fl_image(process_frame)

            # Set audio
            processed_video = processed_video.set_audio(audio)

            # Write the processed video to output file
            processed_video.write_videofile(output_path, audio_codec='aac')

        except Exception as e:
            raise Exception(f"Video processing failed: {str(e)}")
