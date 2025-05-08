import sys
import os
from PyQt5.QtWidgets import QApplication
from serato_tagger.gui.main_window import MainWindow

def main():
    # Set Spotify credentials
    os.environ["SPOTIFY_CLIENT_ID"] = "a90fecc90966484d9f3b643fb35b686c"  # 여기에 Spotify Client ID를 입력하세요
    os.environ["SPOTIFY_CLIENT_SECRET"] = "24fa540fbc184f129a9defaf6ace494a"  # 여기에 Spotify Client Secret을 입력하세요
    
    # Start application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()