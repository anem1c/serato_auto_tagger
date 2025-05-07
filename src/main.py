import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Spotify API 설정
SPOTIFY_CLIENT_ID = 'a90fecc90966484d9f3b643fb35b686c'
SPOTIFY_CLIENT_SECRET = '24fa540fbc184f129a9defaf6ace494a'

def main():
    app = QApplication(sys.argv)
    window = MainWindow(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 