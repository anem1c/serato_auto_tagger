import sys
import os
from PyQt5.QtWidgets import QApplication
from serato_tagger.gui.main_window import MainWindow

def main():
    # Set Spotify credentials
    os.environ["SPOTIFY_CLIENT_ID"] = "your_client_id"
    os.environ["SPOTIFY_CLIENT_SECRET"] = "your_client_secret"
    
    # Start application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()