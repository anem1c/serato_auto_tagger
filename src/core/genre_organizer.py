import os
from pathlib import Path
from typing import List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time
import eyed3

from PyQt5.QtCore import QThread, pyqtSignal
from .genre_mapper import GenreMapper
from .spotify_finder import SpotifyGenreFinder

@dataclass
class ProcessingStats:
    total_files: int = 0
    processed_files: int = 0
    updated_files: int = 0
    error_files: int = 0
    not_found_files: List[str] = None

    def __post_init__(self):
        if self.not_found_files is None:
            self.not_found_files = []

class GenreOrganizerThread(QThread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    finished = pyqtSignal(ProcessingStats)

    def __init__(self, directory: str, only_empty_genres: bool, 
                 spotify_client_id: str, spotify_client_secret: str):
        super().__init__()
        self.directory = directory
        self.only_empty_genres = only_empty_genres
        self.genre_mapper = GenreMapper()
        self.spotify_finder = SpotifyGenreFinder(spotify_client_id, spotify_client_secret)
        self.stats = ProcessingStats()

    def process_file(self, file_path: str) -> None:
        """단일 파일 처리"""
        try:
            audiofile = eyed3.load(file_path)
            if not audiofile or not audiofile.tag:
                return

            current_genre = audiofile.tag.genre.name if audiofile.tag.genre else None
            
            if self.only_empty_genres and current_genre:
                return
                
            new_genre = self.genre_mapper.normalize_genre(current_genre)
            
            if not new_genre:
                track_name = audiofile.tag.title or Path(file_path).stem
                artist_name = audiofile.tag.artist or "Unknown"
                spotify_genre = self.spotify_finder.find_genre(track_name, artist_name)
                
                if spotify_genre:
                    new_genre = self.genre_mapper.normalize_genre(spotify_genre)
                    if new_genre:
                        self.log.emit(f"Spotify에서 장르를 찾았습니다: {Path(file_path).name} - {new_genre}")
                    else:
                        self.stats.not_found_files.append(Path(file_path).name)
                        self.log.emit(f"장르를 찾을 수 없습니다: {Path(file_path).name}")
                        return
                else:
                    self.stats.not_found_files.append(Path(file_path).name)
                    self.log.emit(f"장르를 찾을 수 없습니다: {Path(file_path).name}")
                    return
            
            audiofile.tag.genre = new_genre
            audiofile.tag.save()
            self.stats.updated_files += 1
            self.log.emit(f"업데이트 완료: {Path(file_path).name} - {current_genre or '장르 없음'} -> {new_genre}")
            
        except Exception as e:
            self.stats.error_files += 1
            self.log.emit(f"처리 중 오류 발생: {Path(file_path).name} - {str(e)}")

    def run(self):
        """메인 처리 로직"""
        # MP3 파일 목록 수집
        mp3_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith('.mp3'):
                    mp3_files.append(os.path.join(root, file))
        
        self.stats.total_files = len(mp3_files)
        self.log.emit(f"총 {self.stats.total_files}개의 MP3 파일을 찾았습니다.")

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=4) as executor:
            for i, file_path in enumerate(mp3_files, 1):
                executor.submit(self.process_file, file_path)
                self.stats.processed_files = i
                self.progress.emit(i, self.stats.total_files)
                time.sleep(0.1)  # UI 업데이트를 위한 짧은 지연

        self.finished.emit(self.stats) 