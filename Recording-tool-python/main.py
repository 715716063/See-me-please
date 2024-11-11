import sys
import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from main_window import MainWindow

# Define workspace-relative paths
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(WORKSPACE_DIR, "config.json")

try:
    with open(CONFIG_FILE_PATH, 'r') as config_file:
        config = json.load(config_file)
        SAVE_DIRECTORY = os.path.join(WORKSPACE_DIR, config.get("SAVE_DIRECTORY", ""))
        FFMPEG_PATH = os.path.join(WORKSPACE_DIR, config.get("FFMPEG_PATH", ""))
        ICON_PATH = os.path.join(WORKSPACE_DIR, config.get("ICON_PATH", ""))
        AWS_ACCESS_KEY_ID = config.get("AWS_ACCESS_KEY_ID", "")
        AWS_SECRET_ACCESS_KEY = config.get("AWS_SECRET_ACCESS_KEY", "")
        S3_BUCKET_NAME = config.get("S3_BUCKET_NAME", "")
except Exception as e:
    print(f"Error loading configuration: {e}")
    sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # setting icon
    if os.path.exists(ICON_PATH):
        try:
            app_icon = QIcon(ICON_PATH)
            app.setWindowIcon(app_icon)
            print(f"Successfully set icon: {ICON_PATH}")
        except Exception as e:
            print(f"Error setting icon: {e}")
    else:
        print(f"Icon file not found: {ICON_PATH}")

    # creat main window and pass paramaters
    main_window = MainWindow(
        save_directory=SAVE_DIRECTORY,
        ffmpeg_path=FFMPEG_PATH,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        s3_bucket_name=S3_BUCKET_NAME
    )

    # show the main window
    main_window.show()
    sys.exit(app.exec_())
