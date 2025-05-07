from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QCheckBox, QFileDialog, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt
from pathlib import Path
from typing import Optional

from ..core.genre_organizer import GenreOrganizerThread
from ..utils.logger import setup_logger

class MainWindow(QMainWindow):
    def __init__(self, spotify_client_id: str, spotify_client_secret: str):
        super().__init__()
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.logger = setup_logger()
        self.initUI()
        
    def initUI(self):
        """UI 초기화"""
        self.setWindowTitle('음악 장르 정리기')
        self.setGeometry(100, 100, 800, 600)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 디렉토리 선택
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel('음악 폴더:')
        self.dir_path = QLabel('선택되지 않음')
        self.dir_button = QPushButton('폴더 선택')
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)
        
        # 옵션
        self.empty_only_checkbox = QCheckBox('장르가 없는 곡만 처리')
        layout.addWidget(self.empty_only_checkbox)
        
        # 진행 상태
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 로그 출력
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 실행 버튼
        self.run_button = QPushButton('장르 정리 시작')
        self.run_button.clicked.connect(self.start_processing)
        layout.addWidget(self.run_button)
        
        self.statusBar().showMessage('준비됨')
        
    def select_directory(self):
        """디렉토리 선택 대화상자"""
        dir_path = QFileDialog.getExistingDirectory(self, '음악 폴더 선택')
        if dir_path:
            self.dir_path.setText(dir_path)
            
    def log(self, message: str):
        """로그 메시지 추가"""
        self.log_text.append(message)
        self.logger.info(message)
        
    def start_processing(self):
        """처리 시작"""
        if self.dir_path.text() == '선택되지 않음':
            QMessageBox.warning(self, '경고', '음악 폴더를 선택해주세요.')
            return
            
        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        self.organizer_thread = GenreOrganizerThread(
            self.dir_path.text(),
            self.empty_only_checkbox.isChecked(),
            self.spotify_client_id,
            self.spotify_client_secret
        )
        
        self.organizer_thread.progress.connect(self.update_progress)
        self.organizer_thread.log.connect(self.log)
        self.organizer_thread.finished.connect(self.processing_finished)
        
        self.organizer_thread.start()
        
    def update_progress(self, current: int, total: int):
        """진행 상태 업데이트"""
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.statusBar().showMessage(f'처리 중... ({current}/{total})')
        
    def processing_finished(self, stats):
        """처리 완료"""
        self.run_button.setEnabled(True)
        self.statusBar().showMessage('완료됨')
        
        self.log('\n=== 처리 완료 통계 ===')
        self.log(f"총 파일 수: {stats.total_files}")
        self.log(f"처리된 파일 수: {stats.processed_files}")
        self.log(f"업데이트된 파일 수: {stats.updated_files}")
        self.log(f"오류 발생 파일 수: {stats.error_files}")
        self.log(f"장르를 찾지 못한 파일 수: {len(stats.not_found_files)}")
        
        if stats.not_found_files:
            self.log('\n=== 장르를 찾지 못한 파일 목록 ===')
            for file in stats.not_found_files:
                self.log(file) 