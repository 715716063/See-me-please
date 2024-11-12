# Recording Tool(Python Version)

This project is a comprehensive screen recording tool that integrates **FFmpeg** for high-quality screen recording, **OpenCV** for real-time camera capture, and **PyQt** for designing an intuitive graphical user interface (GUI).

## Features

- **Screen Recording**: High-performance screen capture using FFmpeg, ensuring smooth and high-resolution recordings.
- **Camera Integration**: Real-time video capture from a connected camera, displayed in a resizable, borderless floating window.
- **User Interface**: A clean and accessible GUI developed with PyQt5, providing options to configure video quality, enable/disable the camera, and toggle additional features.
- **AWS S3 Integration**: Automatic uploading of recorded files to an Amazon S3 bucket for easy storage and access.
- **Customizable Configuration**: All major parameters, such as AWS credentials and save paths, are easily adjustable through a `config.json` file.

Install the dependencies with:
```
pip install -r requirements.txt
```

## Installation

To ensure compatibility, please configure the environment using the exact dependencies specified in the `requirements.txt` file:
```
PyQt5==5.15.4
boto3==1.20.24
opencv-python==4.5.4.60
```

## FFmpeg Setup

Due to GitHub's file size restrictions, the FFmpeg binaries are not included in the repository. Please download FFmpeg from the official website:

[FFmpeg Download Page](https://www.gyan.dev/ffmpeg/builds/)

- **Recommended version**: `ffmpeg-release-essentials version 7.1`
- After downloading, extract the files to the root directory of the project and rename the folder to `ffmpeg`. The final path should look like this:

```
Recording-tool-python/ffmpeg/bin/ffmpeg.exe
```

## AWS Configuration
To enable file uploads to AWS S3, update the `config.json` file with your AWS credentials and bucket information:
```
{
    "AWS_ACCESS_KEY_ID": "YourAccessKey",
    "AWS_SECRET_ACCESS_KEY": "YourSecretKey",
    "S3_BUCKET_NAME": "YourBucketName",
    "SAVE_DIRECTORY": "Recordings",
    "FFMPEG_PATH": "ffmpeg/bin/ffmpeg.exe",
    "ICON_PATH": "ICON.ico"
}
```
## Usage

1. Launch the application by running `main.py`.
```
python main.py
```
2. Use the GUI to configure recording settings:
   - Select video quality (low, medium, high).
   - Enable/disable the camera.
   - Start/stop recording.
3. Recorded files are saved in the `SAVE_DIRECTORY` specified in `config.json` and automatically uploaded to the configured S3 bucket.

## Key Components

- **FFmpeg Integration**: High-speed and efficient video processing.
- **Real-Time Camera Window**: Designed with OpenCV, supporting dynamic resizing and position adjustments.
- **Interactive GUI**: Developed with PyQt5 for ease of use.
- **Cloud Storage**: Seamless integration with AWS S3 for file storage.

## Development Notes

- Ensure that the FFmpeg binary path matches the configuration in `config.json`.
- This project has been tested on Windows systems. Cross-platform compatibility requires further testing.
- For development purposes, consider isolating each functionality into separate modules or classes for better maintainability and scalability.


