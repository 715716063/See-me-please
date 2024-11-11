# Extracting Sensitive Text and Protecting Information in Videos

## Overview

This project aims to extract text from videos and identify sensitive information using OpenCV and PaddleOCR. The process includes:

- Text extraction
- Sensitive information capture
- Partial text capture and editing (blocking sensitive info)

The processed video is saved with sensitive information concealed, and extracted text is saved for further analysis.

---

## Dependency

The project uses the following libraries:

- **OpenCV**: For video editing and frame manipulation.
- **PaddleOCR**: For Optical Character Recognition (OCR) to identify/extract text from video frames.
- **JSON**: For handling and storing extracted text data with labels for sensitive information.

Installation of the required libraries is handled in the `Prepare` section of the code.

---

## Workflow

### 3.1. Settings

- **Video path**: Set to the video that needs to be processed.
- **Root folder**: Location where all outputs will be stored.
- **Sampling rate (r)**: Determines how frequently frames are processed.

**Impact on Performance**:
- Higher `r` values process fewer frames, improving speed but potentially losing detail.
- Sampling every frame does not always yield the best performance due to OCR limitations.
- Exploring inter-frame processing techniques like frame averaging could enhance accuracy.

---

### 3.2. Extracting Text from Video

- Isolate frames using OpenCV.
- Perform OCR on each frame with PaddleOCR.
- Save extracted text to `extracted_text.json`, including:
  - Frame number
  - Text content
  - Coordinates of text blocks

---

### 3.3. Processing Extracted Text

- Remove repeated frames.
- Label sensitive information in `extracted_text.json` using regular expressions.
- Identify sensitive data (e.g., email addresses, phone numbers, etc.).
- For unstructured text like names or addresses, consider using NLP models like spaCy with customized training.

---

### 3.4. Labeling Sensitive Information and Saving Results

- Use a **Trie Tree** to capture partial strings from sensitive information.
- Label sensitive substrings (e.g., “abc”, “abcd”, “de”) but avoid unrelated text to minimize false positives.
- Add an `"is_sensitive": true` attribute to flagged items in the JSON file.

---

### 3.5. Blocking Sensitive Information in the Video

- Use labeled data to block sensitive text in the video by drawing a black box over the text coordinates in relevant frames.

---

## Conclusion

This project leverages OpenCV and PaddleOCR to extract, process, and protect sensitive information in video files. The key phases are:

1. Text extraction
2. Sensitive information detection
3. Video editing to block sensitive content

### Current Challenges:
- When users scroll too fast, the blocking box may lose tracking due to sampling limitations.
- Increasing the sampling rate doesn't entirely solve the issue. Potential improvements include:
  - **Position prediction** between sampled frames.
  - **Larger blocking boxes** for better coverage.

Further enhancements and performance improvements are planned. Additional explanations and comments are included in the code.
