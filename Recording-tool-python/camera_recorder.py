import cv2
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from contextlib import contextmanager
import queue
from threading import Lock

class CameraThread(QThread):
    """Separate thread for camera capture to prevent frame dropping"""
    frame_ready = pyqtSignal(object)

    def __init__(self, camera_capture, frame_queue, lock):
        super().__init__()
        self.camera_capture = camera_capture
        self.frame_queue = frame_queue
        self.lock = lock
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                if self.camera_capture and self.camera_capture.isOpened():
                    ret, frame = self.camera_capture.read()
                    if ret:
                        if self.frame_queue.full():
                            try:
                                self.frame_queue.get_nowait()  # Remove oldest frame
                            except queue.Empty:
                                pass
                        self.frame_queue.put(frame)
                        self.frame_ready.emit(frame)
            time.sleep(0.001)  # Prevent thread from hogging CPU

    def stop(self):
        self.running = False
        self.wait()

class CameraRecorder:
    def __init__(self, output_path, video_device, mirror=False, camera_window=None, warmup_time=1.0):
        self.output_path = output_path
        self.video_device = video_device
        self.mirror = mirror
        self.camera_window = camera_window
        self.camera_capture = None
        self.camera_writer = None
        self.camera_timer = None
        self.target_fps = 30.0
        self.frame_count = 0
        self.warmup_time = warmup_time
        self._is_warmed_up = False
        self.is_recording = False
        
        # Frame queue and thread management
        self.frame_queue = queue.Queue(maxsize=30)  # Limit queue size
        self.camera_lock = Lock()
        self.camera_thread = None
        
        # Performance monitoring
        self.last_frame_time = 0
        self.frame_times = []
        self.fps_update_interval = 30  # Update FPS every 30 frames

    @contextmanager
    def camera_session(self):
        """Context manager for handling camera resources"""
        try:
            self._initialize_camera()
            yield self
        finally:
            self._release_camera()

    def _initialize_camera(self):
        """Initialize camera with optimized settings"""
        if self.camera_window:
            self.camera_window.start_camera_stream()
            
        camera_index = self._get_camera_index(self.video_device)
        
        # Try different backends in order of preference
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
            self.camera_capture = cv2.VideoCapture(camera_index, backend)
            if self.camera_capture.isOpened():
                break
        
        if not self.camera_capture.isOpened():
            raise RuntimeError("Unable to open camera")

        # Optimize camera settings
        self._configure_camera_settings()
        
        if not self._is_warmed_up:
            self._warmup_camera()
            
        # Initialize camera thread
        self.camera_thread = CameraThread(self.camera_capture, self.frame_queue, self.camera_lock)
        self.camera_thread.frame_ready.connect(self._process_frame)
        self.camera_thread.start()

    def _configure_camera_settings(self):
        """Configure optimal camera settings"""
        # Essential settings
        self.camera_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camera_capture.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Try to set the highest resolution supported
        resolutions = [
            (1920, 1080),
            (1280, 720),
            (800, 600),
            (640, 480)
        ]
        
        for width, height in resolutions:
            self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = self.camera_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if actual_width == width and actual_height == height:
                break

        # Additional optimization settings
        self.camera_capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
        self.camera_capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Enable auto exposure

    def start(self):
        """Start camera recording"""
        try:
            if not self.camera_capture or not self.camera_capture.isOpened():
                self._initialize_camera()

            frame_size = (
                int(self.camera_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.camera_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.camera_writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.target_fps,
                frame_size
            )

            self.frame_count = 0
            self.is_recording = True
            self.last_frame_time = time.time()
            print("Camera recording started.")

        except Exception as e:
            print(f"Error starting camera recording: {e}")
            self._release_camera()

    def _process_frame(self, frame):
        """Process frames from the camera thread"""
        if not self.is_recording:
            return

        if self.mirror:
            frame = cv2.flip(frame, 1)

        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time

        # Update FPS statistics periodically
        if len(self.frame_times) >= self.fps_update_interval:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            print(f"Current FPS: {current_fps:.2f}")
            self.frame_times.clear()

        if self.camera_writer:
            self.camera_writer.write(frame)
        if self.camera_window:
            self.camera_window.update_frame(frame)
        self.frame_count += 1

    def stop(self):
        """Stop camera recording and release resources"""
        try:
            self.is_recording = False
            if self.camera_thread:
                self.camera_thread.stop()
                self.camera_thread = None
            self._release_camera()
            print("Camera recording stopped.")
        except Exception as e:
            print(f"Error stopping camera recording: {e}")

    def _release_camera(self):
        """Release all camera resources"""
        if self.camera_writer:
            self.camera_writer.release()
            self.camera_writer = None
        if self.camera_capture:
            self.camera_capture.release()
            self.camera_capture = None
        self._is_warmed_up = False
        
        # Clear frame queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

    def _get_camera_index(self, device_name):
        """Get camera index from device name"""
        return 0

    def _warmup_camera(self):
        """Warm up camera to reduce initial delay"""
        print("Warming up camera...")
        start_time = time.time()
        while time.time() - start_time < self.warmup_time:
            with self.camera_lock:
                ret, _ = self.camera_capture.read()
                if not ret:
                    break
        self._is_warmed_up = True
        print("Camera warmup complete")