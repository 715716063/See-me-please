# gui.py

import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Listbox, Toplevel, Label, Button

from config import Config
from file_processor import FileProcessor
from loading_window import LoadingWindow

class GUI:
    """Class for handling the graphical user interface."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window while loading

        # Show loading window
        loading_window = LoadingWindow(self.root)

        # Initialize components
        loading_window.update_text("Loading configuration...")
        self.config = Config()

        loading_window.update_text("Initializing processors...")
        self.file_processor = FileProcessor(self.config)

        # Close the loading window and show the main window
        loading_window.close()
        self.root.deiconify()

        self.selected_file = None
        self.download_path = None
        self.processed_files = None

        self.setup_main_window()
        self.create_widgets()

    def setup_main_window(self):
        """Set up the main window."""
        self.root.title("S3 File Processor")
        self.center_window(self.root, self.config.main_window_width, self.config.main_window_height)
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_close)

    def center_window(self, window, width, height):
        """Center a window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def create_centered_toplevel(self, title, width, height):
        """Create a centered toplevel window."""
        window = Toplevel(self.root)
        window.title(title)
        self.center_window(window, width, height)
        return window

    def create_widgets(self):
        """Create all widgets for the main window."""
        # Progress bar and label
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.progress_label = Label(self.root, text="Waiting to start...")
        self.progress_label.pack(pady=5)

        # Main buttons
        Button(self.root, text="List Files", command=self.show_file_list).pack(pady=10)
        Button(self.root, text="Process Selected File", command=self.process_file).pack(pady=10)
        Button(self.root, text="Download Results", command=self.download_results).pack(pady=10)
        Button(self.root, text="Settings", command=self.show_settings).pack(pady=10)

    def show_file_list(self):
        """Show the file list window."""
        file_window = self.create_centered_toplevel("Available Files",
                                                    self.config.file_list_width,
                                                    self.config.file_list_height)

        file_list = Listbox(file_window, width=60, height=15)
        file_list.pack(pady=10)

        try:
            files = self.file_processor.s3_handler.list_files()
            for file in files:
                file_list.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            file_window.destroy()
            return

        def select_file():
            self.selected_file = file_list.get(tk.ACTIVE)
            if self.selected_file:
                messagebox.showinfo("File Selected", f"{self.selected_file} has been selected for processing.")
                file_window.destroy()
            else:
                messagebox.showwarning("Warning", "Please select a file first.")

        Button(file_window, text="Select File", command=select_file).pack(pady=10)

    def show_settings(self):
        """Show the settings window."""
        settings_window = self.create_centered_toplevel("Settings",
                                                        self.config.settings_width,
                                                        self.config.settings_height)

        # Create a main frame for all settings
        main_frame = ttk.Frame(settings_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Download Path Section
        path_frame = ttk.LabelFrame(main_frame, text="Download Settings", padding="5")
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        current_path = self.download_path if self.download_path else "Not selected"
        download_path_label = Label(path_frame, text=f"Download Path:\n{current_path}")
        download_path_label.pack(pady=5)

        def select_download_path():
            path = filedialog.askdirectory(title="Select Download Path")
            if path:
                self.download_path = path
                download_path_label.config(text=f"Download Path:\n{self.download_path}")

        Button(path_frame, text="Select Path", command=select_download_path).pack(pady=5)

        # Model Selection Section
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding="5")
        model_frame.pack(fill=tk.X, padx=5, pady=5)

        # Friction Point Detection Model
        ttk.Label(model_frame, text="Friction Point Detection Model:").pack(pady=5)
        friction_var = tk.StringVar(value=self.config.friction_detection_model)
        friction_combo = ttk.Combobox(model_frame,
                                      textvariable=friction_var,
                                      values=["Semantic analysis by LLM (Based on GPT-4)"],
                                      state="readonly")
        friction_combo.pack(pady=5)

        # PII Reduction Model
        ttk.Label(model_frame, text="PII Reduction Model:").pack(pady=5)
        pii_var = tk.StringVar(value=self.config.pii_reduction_model)
        pii_combo = ttk.Combobox(model_frame,
                                 textvariable=pii_var,
                                 values=["Sensitive text detection (Based on AWS)",
                                         "Sensitive text detection (Based on PaddleOCR)"],
                                 state="readonly")
        pii_combo.pack(pady=5)

        def save_settings():
            self.config.friction_detection_model = friction_var.get()
            self.config.pii_reduction_model = pii_var.get()
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Save Settings", command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)

    def update_progress(self, message, value):
        """Update progress bar and label."""
        self.progress_label.config(text=message)
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def process_file(self):
        """Process the selected file."""
        if not self.selected_file:
            messagebox.showwarning("Warning", "No file selected for processing.")
            return

        try:
            self.processed_files = self.file_processor.process_file(
                self.selected_file,
                progress_callback=self.update_progress
            )
            messagebox.showinfo("Process Complete", "Transcription and friction point analysis completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progress_label.config(text="Waiting to start...")
            self.progress_bar['value'] = 0
            self.root.update_idletasks()

    def download_results(self):
        """Download the processed files."""
        if not self.download_path:
            messagebox.showwarning("Warning", "No download path set. Please set a download path in settings first.")
            self.show_settings()
            return

        if not os.path.exists(self.download_path):
            messagebox.showerror("Error", "Selected download path does not exist.")
            return

        if not self.selected_file or not self.processed_files:
            messagebox.showwarning("Warning", "No processed files available. Please process a file first.")
            return

        try:
            # Create folder for the processed files
            folder_name = os.path.splitext(self.selected_file)[0]
            folder_path = os.path.join(self.download_path, folder_name)

            # Create folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Copy all processed files
            file_paths = {
                'VTT File': ('transcription.vtt', self.processed_files['vtt_path']),
                'Transcript': ('transcript.txt', self.processed_files['transcript_path']),
                'Analysis': ('friction_points_analysis.txt', self.processed_files['analysis_path']),
                'Processed Video': ('pii_processed_video.mp4', self.processed_files['processed_video_path'])
            }

            saved_files = []
            for file_type, (dest_name, source_path) in file_paths.items():
                if os.path.exists(source_path):
                    destination = os.path.join(folder_path, dest_name)
                    shutil.copy2(source_path, destination)
                    saved_files.append(f"- {file_type}: {dest_name}")

            messagebox.showinfo("Download Successful",
                                f"Files downloaded to folder:\n{folder_path}\n\n"
                                f"Files saved:\n" + "\n".join(saved_files))

        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download files: {str(e)}")

    def cleanup_and_close(self):
        """Clean up and close the application."""
        try:
            self.file_processor.cleanup()
        except Exception as e:
            print(f"Cleanup error: {e}")
        self.root.destroy()

    def run(self):
        """Start the application."""
        self.root.mainloop()
