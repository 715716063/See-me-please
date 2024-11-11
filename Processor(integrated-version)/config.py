# config.py

import os
import torch

# Detect GPU availability
GPU_AVAILABLE = torch.cuda.is_available()

class Config:
    """Configuration class for storing all constants and settings."""
    def __init__(self):
        # AWS configuration (use environment variables for sensitive data)
        self.aws_access_key_id = 'aws access key id'
        self.aws_secret_access_key = 'aws secret access key'
        self.region_name = 'ap-southeast-2'
        self.bucket_name = 'bucket name'

        # OpenAI configuration
        self.openai_api_key = 'openai key'

        # Model settings
        self.friction_detection_model = "Semantic analysis by LLM (Based on GPT-4)"
        self.pii_reduction_model = "Sensitive text detection (Based on AWS)"  # or "Sensitive text detection (Based on PaddleOCR)"

        # Device settings
        self.device = torch.device("cuda" if GPU_AVAILABLE else "cpu")

        # Window sizes
        self.main_window_width = 400
        self.main_window_height = 300
        self.file_list_width = 500
        self.file_list_height = 400
        self.settings_width = 500  # Increased width to accommodate new options
        self.settings_height = 400  # Increased height to accommodate new options
