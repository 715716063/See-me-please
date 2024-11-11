# loading_window.py

import tkinter as tk
from tkinter import Toplevel, Label

class LoadingWindow:
    """Loading window to show initialization progress."""
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("Loading Models")
        self.window.geometry("300x100")
        self.window.resizable(False, False)
        # Center the window on the screen
        self.center_window()

        self.label = Label(self.window, text="Initializing models...\nThis may take a few minutes.")
        self.label.pack(expand=True)

        # Update the window to ensure it displays properly
        self.window.update()

    def update_text(self, text):
        """Update the text displayed in the loading window."""
        self.label.config(text=text)
        self.window.update()

    def close(self):
        """Close the loading window."""
        self.window.destroy()

    def center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
