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
        self.update_year = QCheckBox("연도 정보 업데이트")
        self.start_button = QPushButton("장르 정리 시작")
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        
        # Add widgets to layout
        layout.addWidget(self.folder_button)
        layout.addWidget(self.process_without_genre)
        layout.addWidget(self.update_year)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_output)
        
        # Connect signals
        self.folder_button.clicked.connect(self.select_folder)
        self.start_button.clicked.connect(self.start_processing)
        
        # Initialize variables
        self.selected_folder = None
        self.organizer_thread = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "음악 폴더 선택")
        if folder:
            self.selected_folder = folder
            self.log_output.append(f"선택된 폴더: {folder}")

    def start_processing(self):
        if not self.selected_folder:
            self.log_output.append("폴더를 먼저 선택해주세요.")
            return
        
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.log_output.append("이미 처리 중입니다.")
            return
        
        self.organizer_thread = GenreOrganizerThread(
            self.selected_folder,
            self.process_without_genre.isChecked()
        )
        
        self.organizer_thread.progress_updated.connect(self.update_progress)
        self.organizer_thread.log_message.connect(self.log_output.append)
        self.organizer_thread.finished.connect(self.processing_finished)
        
        self.start_button.setEnabled(False)
        self.organizer_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.log_output.append("처리가 완료되었습니다.")