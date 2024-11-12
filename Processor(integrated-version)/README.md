# Video Processing Server

This project is a server-side application designed to process videos by downloading them from an AWS S3 bucket and performing advanced operations such as PII reduction and Friction Point Detection. The program is built with modular components to ensure flexibility, scalability, and ease of maintenance.

## Features

1. **S3 Integration**:
   - Downloads videos from a specified AWS S3 bucket using the `s3_handler` module.
   - Supports batch processing and efficient file management.

2. **Video Processing**:
   - PII (Personally Identifiable Information) detection and masking powered by PaddleOCR and AWS-based PII analyzers.
   - Friction Point Detection using Whisper model to transcribe the audio into text format, and use LLM-based sentiment analysis for detecting the friction point.

3. **Extensible Architecture**:
   - Modular code structure with clearly defined components for file processing, AI integration, and GUI interaction.
   - Easily extendable for additional features or integrations.

## Key Components

- **`s3_handler.py`**:
  Handles file interactions with AWS S3, including downloading and managing video files.
  
- **`paddleocr_pii_processor.py`**:
  Implements OCR-based PII detection and masking using PaddleOCR.

- **`aws_pii_processor.py`**:
  Leverages AWS PII detection services for comprehensive analysis.

- **`audio_processor.py`**:
  Processes audio tracks from videos, including extraction and analysis.

- **`gpt_analyzer.py`**:
  Performs friction point detection and advanced sentiment analysis using GPT models.

- **`file_processor.py`**:
  Manages local file handling, including temporary storage and cleanup after processing.

- **`trie.py`**:
  Implements efficient data structures for managing sensitive keywords or patterns.

- **`gui.py`**:
  Provides an optional graphical interface for interacting with the server, configuring processing options, and monitoring progress.

- **`config.py`**:
  Centralized configuration management for customizable options like AWS credentials, S3 bucket details, and processing parameters.

- **`loading_window.py`**:
  Implements a progress indicator for GUI-based interactions.

## AWS Configuration
To enable file downloads from AWS S3, update the `config.py` file with your AWS credentials and bucket information:
```
{
    "AWS_ACCESS_KEY_ID": "YourAccessKey",
    "AWS_SECRET_ACCESS_KEY": "YourSecretKey",
    "S3_BUCKET_NAME": "YourBucketName",
    "LOCAL_STORAGE_PATH": "ProcessedVideos/"
}
```

## Usage

1. Launch the application by running `main.py`.
```
python main.py
```
2. Downloading Videos:
   - Specify the video(s) to process in the S3 bucket.

3. Use the GUI to configure processing settings:
   - Select the model used to identify the PII(AWS based or paddleocr based)
   - Select the model used to transcribe the audio into text format
   - Select the saving directory
   - 
4. Output:
   - Processed files are saved locally in the specified LOCAL_STORAGE_PATH.


## Development Notes
- **`Environment Setup`**: Ensure all dependencies are installed for stable performance.

- **`Modularity`**: Each functionality is encapsulated in a dedicated module, allowing easy testing and maintenance.

- **`Extensibility`**: Additional AI models or processing pipelines can be integrated by extending the respective modules.
