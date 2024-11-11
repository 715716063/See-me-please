# paddleocr_pii_processor.py

import re
import cv2
import numpy as np
from paddleocr import PaddleOCR

class PaddleOCRPIIProcessor:
    """Class for handling PII detection and reduction using PaddleOCR."""
    def __init__(self, config):
        self.use_gpu = config.device.type == 'cuda'
        print(f"PaddleOCR using GPU: {self.use_gpu}")
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=self.use_gpu,
            gpu_mem=500 if self.use_gpu else None,
            enable_mkldnn=not self.use_gpu,
            use_mp=True,
            total_process_num=4,
            use_tensorrt=False,  # Set to True if TensorRT is available
            det_use_gpu=self.use_gpu
        )
        self.patterns = {
            "myGov username": r"\b[A-Z0-9]{8}\b",
            "Date of birth": r"\b\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b",
            "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "Code": r"\b\d{6}\b",
            "Individual Healthcare Identifier": r"\b\d{16}\b",
            "Phone numbers": r"\b0\d{9}\b",
            "BSB/Account": r'\d{3}-\d{3}|\d{7}',
            "Card number": r'\b(?:\d[ -]*?){13,19}\b',
            'CVC': r'\b\d{3,4}\b'
        }

    def detect_text_from_frame(self, frame):
        """Detect text in a frame using PaddleOCR."""
        try:
            result = self.ocr.ocr(frame)
            if not result:
                return [], {}
            text_data = []
            text_boxes = {}
            for line in result:
                coords = line[0]
                text = line[1][0]
                text_data.append(text)
                x_coords = [coord[0] for coord in coords]
                y_coords = [coord[1] for coord in coords]
                text_boxes[text] = {
                    'Left': min(x_coords) / frame.shape[1],
                    'Top': min(y_coords) / frame.shape[0],
                    'Width': (max(x_coords) - min(x_coords)) / frame.shape[1],
                    'Height': (max(y_coords) - min(y_coords)) / frame.shape[0]
                }
            return text_data, text_boxes
        except Exception as e:
            raise Exception(f"Text detection failed: {str(e)}")

    def _match_sensitive_info(self, text):
        """Check if text matches sensitive information patterns."""
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False

    def _blur_mask(self, frame, box):
        """Apply blur mask to a specific area of the frame."""
        height, width = frame.shape[:2]
        left = int(width * box['Left'])
        top = int(height * box['Top'])
        right = int(left + (width * box['Width']))
        bottom = int(top + (height * box['Height']))
        roi = frame[top:bottom, left:right]
        blurred_roi = cv2.GaussianBlur(roi, (51, 51), 0)
        frame[top:bottom, left:right] = blurred_roi
        return frame

    def process_frame(self, frame):
        """Process a single frame to detect and blur PII using PaddleOCR."""
        try:
            text_data, text_boxes = self.detect_text_from_frame(frame)
            for text in text_data:
                if self._match_sensitive_info(text):
                    if text in text_boxes:
                        frame = self._blur_mask(frame, text_boxes[text])
            return frame
        except Exception as e:
            raise Exception(f"Frame processing failed: {str(e)}")

    def process_video(self, input_path, output_path, progress_callback=None):
        """Process video to blur PII information."""
        try:
            cap = cv2.VideoCapture(input_path)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
            current_frame = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                processed_frame = self.process_frame(frame)
                out.write(processed_frame)
                current_frame += 1
                if progress_callback:
                    progress = int((current_frame / frame_count) * 100)
                    progress_callback(f"Processing frame {current_frame}/{frame_count}", progress)
            cap.release()
            out.release()
        except Exception as e:
            raise Exception(f"Video processing failed: {str(e)}")
