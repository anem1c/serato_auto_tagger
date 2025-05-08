from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QProgressBar, QTextEdit, QCheckBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from serato_tagger.core.genre_organizer import GenreOrganizerThread

class LogTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 10px;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
            }
        """)

    def append_log(self, message):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # 메시지 타입에 따른 색상 설정
        format = QTextCharFormat()
        if "❌" in message:
            format.setForeground(QColor("#ff6b6b"))  # 빨간색 (에러)
        elif "⚠️" in message:
            format.setForeground(QColor("#ffd93d"))  # 노란색 (경고)
        elif "✅" in message:
            format.setForeground(QColor("#6bff6b"))  # 초록색 (성공)
        elif "🎵" in message:
            format.setForeground(QColor("#6b6bff"))  # 파란색 (정보)
        elif "📊" in message:
            format.setForeground(QColor("#ff6bff"))  # 보라색 (진행률)
        elif "✨" in message:
            format.setForeground(QColor("#ffb86c"))  # 주황색 (완료)
        else:
            format.setForeground(QColor("#ffffff"))  # 흰색 (기본)
        
        cursor.insertText(message + "\n", format)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serato Genre Organizer")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create title label
        title_label = QLabel("Serato 자동 태그 관리자")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Create UI elements
        self.folder_button = QPushButton("📁 폴더 선택")
        self.process_without_genre = QCheckBox("장르가 없는 곡만 처리")
        self.update_year = QCheckBox("연도 정보 업데이트")
        self.start_button = QPushButton("▶️ 장르 정리 시작")
        self.progress_bar = QProgressBar()
        self.log_output = LogTextEdit()
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """
        self.folder_button.setStyleSheet(button_style)
        self.start_button.setStyleSheet(button_style)
        
        # Style progress bar
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Style checkboxes
        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """
        self.process_without_genre.setStyleSheet(checkbox_style)
        self.update_year.setStyleSheet(checkbox_style)
        
        # Add widgets to layout
        layout.addWidget(title_label)
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
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "음악 폴더 선택")
        if folder:
            self.selected_folder = folder
            self.log_output.append_log(f"📁 선택된 폴더: {folder}")

    def start_processing(self):
        if not self.selected_folder:
            self.log_output.append_log("⚠️ 폴더를 먼저 선택해주세요.")
            return
        
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.log_output.append_log("⚠️ 이미 처리 중입니다.")
            return
        
        self.organizer_thread = GenreOrganizerThread(
            self.selected_folder,
            self.process_without_genre.isChecked()
        )
        
        self.organizer_thread.progress_updated.connect(self.update_progress)
        self.organizer_thread.log_message.connect(self.log_output.append_log)
        self.organizer_thread.finished.connect(self.processing_finished)
        
        self.start_button.setEnabled(False)
        self.organizer_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.log_output.append_log("✨ 처리가 완료되었습니다.")