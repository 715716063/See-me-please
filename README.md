# USYD Capstone Project: DEVELOPING ACCESSIBLE COMPONENTS BASED ON INACCESSIBLE TRENDS/MULTI-MODAL AI

This repository hosts the source code for the **USYD Capstone Project CS3**, sponsored by **See Me Please**. The project aims to develop an **accessible video recording software** tailored for users with diverse needs. The software is collaboratively designed and implemented by **Group CS3-2**.

## Project Overview

The project consists of two main components:

### 1. User-side Application
- This program enables users to record their screen activities and provides a customizable recording experience.
- **Key features include**:
  - **Recording Quality Selection**: Users can choose different quality levels for recording.
  - **Camera Functionality**: Option to enable or disable the front-facing camera during recording.
  - **Feedback interface**: Allow user to provide feedback during the testing phases.
  - **Cloud Upload**: Automatic file upload to a cloud storage platform.

### 2. Server-side Processing
- This backend service processes the recorded videos automatically and integrates two critical modules:
  - **Friction Point Detection**: Identifies moments of confusion or frustration encountered during testing. This is achieved by transcribing audio files and performing **sentiment analysis** using advanced LLM (Large Language Model) techniques.
  - **PII Protection**: Safeguards user privacy by analyzing video frames to detect sensitive information (e.g., text or personal details) and applying **blurring or masking** to obscure it.

---

## Repository Structure

The repository is organized into the following directories:

- **`Recording-tool-python`**  
  Contains the most complete and functional version of the screen recording tool, implemented in Python. This version supports key features such as customizable recording settings and cloud integration.

- **`Recording-tool-vue`**  
  A web-based alternative implementation using Vue.js. This version is under development and serves as a backup solution.

- **`PII-filter-aws`** and **`PII-filter-paddleor`**  
  Legacy development versions of the PII protection module. These contain experimental code and are provided for reference only.

- **`Friction-point-Whisper`**  
  Early prototype of the friction point detection module. This version is also archived and has been integrated into the main processor.

- **`Processor (integrated-version)`**  
  The consolidated version that includes both the friction point detection and PII protection functionalities. This is the primary implementation used in the server-side processing workflow.

---

## Usage Instructions

Please refer to the README files within each folder for detailed setup instructions and usage guides.

---

## Technologies Used

- **Python**: Core language for implementing the recording tool and server-side processing.
- **Vue.js**: Frontend framework for the web-based recording tool.
- **AWS Cloud Services**: For file storage and processing.
- **Whisper**: OpenAI's transcription model used for audio-to-text conversion.
- **LLM Sentiment Analysis**: For identifying emotional friction points in user feedback.
- **PaddleOCR**: Alternative text recognition framework.

---

## Acknowledgements

This project was made possible by the support of **See Me Please** and the contributions of the **CS3-2 team members**. The development and integration efforts aim to enhance accessibility and user experience through innovative AI-driven solutions.
