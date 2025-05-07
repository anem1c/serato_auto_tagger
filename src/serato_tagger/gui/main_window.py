from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QProgressBar, QTextEdit, QCheckBox
from PyQt5.QtCore import Qt
from serato_tagger.core.genre_organizer import GenreOrganizerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serato Genre Organizer")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create UI elements
        self.folder_button = QPushButton("폴더 선택")
        self.process_without_genre = QCheckBox("장르가 없는 곡만 처리")
        self.start_button = QPushButton("장르 정리 시작")
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        
        # Add widgets to layout
        layout.addWidget(self.folder_button)
        layout.addWidget(self.process_without_genre)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_output)