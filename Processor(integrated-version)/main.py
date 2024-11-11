# main.py
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import tkinter as tk
from gui import GUI


def main():
    """Main entry point for the application."""
    try:
        app = GUI()
        app.run()
    except Exception as e:
        # If the main window is not initialized, create a root window for the error message
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
