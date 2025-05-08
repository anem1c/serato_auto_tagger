from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QFileDialog, QProgressBar, QTextEdit, QCheckBox, 
                            QLabel, QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont, QIcon
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
        self.setWindowTitle("Serato 자동 태그 관리자")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # 메인 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 상단 섹션
        top_section = QFrame()
        top_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        top_layout = QVBoxLayout(top_section)
        
        # 타이틀
        title_label = QLabel("Serato 자동 태그 관리자")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # 설명
        description = QLabel("음악 파일의 장르와 연도 정보를 자동으로 업데이트합니다.")
        description.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                padding: 5px;
            }
        """)
        description.setAlignment(Qt.AlignCenter)
        
        top_layout.addWidget(title_label)
        top_layout.addWidget(description)
        
        # 중앙 섹션
        center_section = QFrame()
        center_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        center_layout = QVBoxLayout(center_section)
        
        # 폴더 선택 버튼
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("📁 음악 폴더 선택")
        self.folder_button.setIconSize(QSize(24, 24))
        self.folder_button.setMinimumHeight(50)
        folder_layout.addWidget(self.folder_button)
        
        # 옵션 체크박스들
        options_layout = QHBoxLayout()
        self.process_without_genre = QCheckBox("장르가 없는 곡만 처리")
        self.update_year = QCheckBox("연도 정보 업데이트")
        self.update_year.setChecked(True)
        options_layout.addWidget(self.process_without_genre)
        options_layout.addWidget(self.update_year)
        
        # 시작 버튼
        self.start_button = QPushButton("▶️ 장르 정리 시작")
        self.start_button.setMinimumHeight(50)
        
        # 진행 상태 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        
        center_layout.addLayout(folder_layout)
        center_layout.addLayout(options_layout)
        center_layout.addWidget(self.start_button)
        center_layout.addWidget(self.progress_bar)
        
        # 로그 섹션
        log_section = QFrame()
        log_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        log_layout = QVBoxLayout(log_section)
        
        log_title = QLabel("처리 로그")
        log_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        self.log_output = LogTextEdit()
        self.log_output.setMinimumHeight(300)
        
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_output)
        
        # 스타일 설정
        button_style = """
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """
        
        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 14px;
                padding: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
            QCheckBox::indicator:unchecked {
                background-color: #4a4a4a;
            }
            QCheckBox::indicator:hover {
                background-color: #5a5a5a;
            }
        """
        
        progress_style = """
            QProgressBar {
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d2d;
                color: white;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """
        
        self.folder_button.setStyleSheet(button_style)
        self.start_button.setStyleSheet(button_style)
        self.process_without_genre.setStyleSheet(checkbox_style)
        self.update_year.setStyleSheet(checkbox_style)
        self.progress_bar.setStyleSheet(progress_style)
        
        # 레이아웃에 섹션 추가
        main_layout.addWidget(top_section)
        main_layout.addWidget(center_section)
        main_layout.addWidget(log_section)
        
        # 시그널 연결
        self.folder_button.clicked.connect(self.select_folder)
        self.start_button.clicked.connect(self.start_processing)
        
        # 변수 초기화
        self.selected_folder = None
        self.organizer_thread = None
        
        # 윈도우 스타일
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
            self.start_button.setEnabled(True)

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
        self.folder_button.setEnabled(False)
        self.organizer_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.folder_button.setEnabled(True)
        self.log_output.append_log("✨ 처리가 완료되었습니다.")