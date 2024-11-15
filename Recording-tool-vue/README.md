# **Video Recording Application**

## **Project Overview**

This project is a highly innovative **Video Recording Application** built using **Vue.js** and **Element Plus** for the frontend, combined with **AWS S3** for cloud storage. The application allows users to record their screen, camera, and audio, merge recorded files, and upload them to an S3 bucket. It also includes customizable settings such as resolution and recording duration.

---

## **Features**

- **Screen and Camera Recording**  
  Users can record their screen, with an option to overlay their camera feed.

- **Audio Recording**  
  Records audio using the user's microphone.

- **Pause and Resume Recording**  
  Allows users to pause and resume recordings during the session.

- **Merge Video and Audio**  
  Supports merging multiple video and audio clips into a single file.

- **Customizable Settings**  
  Users can configure recording resolution and duration.

- **File Download and Upload**
    - Download recorded video and audio files directly.
    - Upload files to **AWS S3** for cloud storage.

- **User-friendly Interface**
    - Easy-to-use control panel.
    - Settings menu for advanced configurations.

---

## **Project Structure**

- **Frontend**: Built with Vue.js, using Element Plus for UI components.
- **Cloud Storage**: Integrated with AWS S3 for secure file storage.
- **Media Handling**: Uses `MediaRecorder` API for recording and `navigator.mediaDevices` for accessing screen, camera, and audio streams.

---

## **Setup Instructions**

### **1. Prerequisites**
- Node.js (v14 or higher)
- AWS S3 account and bucket configured with the necessary permissions.

### **2. Clone the Repository**
```bash
git clone <repository-url>
cd <project-directory>
