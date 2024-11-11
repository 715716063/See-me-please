# Video Anonymizer with AWS Rekognition

This Python script is a tool for video anonymization, specifically designed to detect and blur sensitive text information in a video file using **AWS Rekognition** and **OpenCV**. The script uploads a video to an AWS S3 bucket, initiates a text-detection job in AWS Rekognition, retrieves detection results, and then blurs sensitive information such as names, addresses, and other personal identifiers in each frame.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Functions Overview](#functions-overview)
- [License](#license)

## Features

- Uploads video to AWS S3 for cloud-based processing.
- Detects sensitive text using AWS Rekognition's text detection capabilities.
- Anonymizes sensitive information by blurring text in the video frames.
- Saves the processed video to a specified output path.

## Setup

### Prerequisites

1. **AWS Account**: Required for using AWS Rekognition and S3.
2. **AWS Credentials**: Set up AWS credentials with appropriate permissions for Rekognition and S3.
3. **Python Packages**: Install required packages using `pip`:

    ```bash
    pip install boto3 opencv-python tqdm
    ```

4. **OpenCV**: Install OpenCV if not already installed, as it’s used for video processing.

### AWS Configuration

To run the script, ensure that your AWS credentials (`AWS_ACCESS_KEY` and `AWS_SECRET_KEY`) and region are correctly set in the script or through environment variables.

### Security Notice

For security, avoid hardcoding your AWS credentials. Consider using environment variables or AWS IAM roles where possible.

## Usage

1. **Set up your paths**: Set `INPUT_VIDEO_PATH` and `OUTPUT_VIDEO_PATH` to point to the video you wish to anonymize and the location where you want to save the output, respectively.

2. **Run the Script**:

   ```bash
   python video_anonymizer.py


Configuration
The script can be customized using the following configuration parameters:

AWS_ACCESS_KEY and AWS_SECRET_KEY: AWS credentials for programmatic access.
AWS_REGION: Set to your region, e.g., "us-east-1".
S3_BUCKET_NAME: Your designated S3 bucket for storing video files.
Functions Overview
create_aws_client(service)
Creates an AWS client for the specified service.

upload_to_s3(file_path)
Uploads a file to S3 and displays a progress bar.

start_rekognition_job(video_name)
Starts a text-detection job in AWS Rekognition for the specified video file in S3.

get_rekognition_results(job_id)
Polls AWS Rekognition to retrieve text detection results.

anonymize_video(input_path, output_path)
Main function to process video frames, applying blur to sensitive information identified by Rekognition.

is_personal_info(text)
Utility function to determine if the detected text contains personal or sensitive information.