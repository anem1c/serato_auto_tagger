import os
import eyed3
from PyQt5.QtCore import QThread, pyqtSignal
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import logging
import requests
from bs4 import BeautifulSoup
import time

# 로깅 설정
logging.getLogger('eyed3').setLevel(logging.ERROR)  # eyed3 경고 메시지 숨김

class GenreOrganizerThread(QThread):
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)

    def __init__(self, music_dir, only_without_genre=False):
        super().__init__()
        self.music_dir = music_dir
        self.only_without_genre = only_without_genre
        
        # Load genre mapping
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config", "genre_mapping.json"), "r", encoding="utf-8") as f:
            self.genre_mapping = json.load(f)
        
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        )
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def validate_year(self, year_str):
        """연도 문자열이 유효한 4자리 연도인지 검증"""
        if not year_str:
            return None
        
        # 4자리 숫자만 허용 (1900-2099)
        if re.match(r'^(19|20)\d{2}$', year_str):
            return year_str
        return None

    def search_google_music(self, track_name, artist_name):
        """Google Music에서 곡 정보 검색"""
        try:
            # 검색 쿼리 구성
            query = f"{track_name} {artist_name} music year genre"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Google 검색
            response = requests.get(f'https://www.google.com/search?q={query}', headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 검색 결과에서 정보 추출
            genres = []
            year = None
            
            # 검색 결과 텍스트에서 연도 찾기
            text = soup.get_text()
            year_match = re.search(r'(19|20)\d{2}', text)
            if year_match:
                year = self.validate_year(year_match.group())
            
            # 검색 결과에서 장르 찾기
            for genre in self.genre_mapping.keys():
                if genre.lower() in text.lower():
                    genres.append(genre)
            
            return genres, year
        except Exception as e:
            self.log_message.emit(f"Google Music 검색 중 오류 발생: {str(e)}")
            return [], None

    def get_track_info(self, track_name, artist_name):
        try:
            # Spotify에서 먼저 검색
            query = f"track:{track_name} artist:{artist_name}"
            results = self.spotify.search(q=query, type="track", limit=1)
            
            genres = []
            year = None
            
            if results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                
                # Get artist genres
                artist = self.spotify.artist(track["artists"][0]["id"])
                genres.extend(artist["genres"])
                
                # Get album genres if available
                album = self.spotify.album(track["album"]["id"])
                if album["genres"]:
                    genres.extend(album["genres"])
                
                # Get release year
                release_date = track["album"]["release_date"]
                year = self.validate_year(release_date.split("-")[0]) if release_date else None
                
                if year:
                    self.log_message.emit(f"🎵 {track_name} - Spotify에서 연도 정보를 찾았습니다: {year}")
                else:
                    self.log_message.emit(f"⚠️ {track_name} - Spotify에서 연도 정보를 찾지 못했습니다.")
            
            # Spotify에서 정보를 찾지 못한 경우 Google Music 검색
            if not genres or not year:
                self.log_message.emit(f"🔍 {track_name} - Google Music에서 추가 정보를 검색합니다...")
                google_genres, google_year = self.search_google_music(track_name, artist_name)
                
                if google_genres:
                    genres.extend(google_genres)
                    self.log_message.emit(f"🎵 {track_name} - Google Music에서 장르 정보를 찾았습니다: {', '.join(google_genres)}")
                
                if google_year and not year:
                    year = google_year
                    self.log_message.emit(f"🎵 {track_name} - Google Music에서 연도 정보를 찾았습니다: {year}")
                
                # API 요청 간 딜레이
                time.sleep(1)
            
            return genres, year
        except Exception as e:
            self.log_message.emit(f"❌ {track_name} - 정보 검색 중 오류 발생: {str(e)}")
            return [], None

    def process_file(self, file_path):
        try:
            audiofile = eyed3.load(file_path)
            if not audiofile or not audiofile.tag:
                self.log_message.emit(f"⚠️ {os.path.basename(file_path)} - 메타데이터를 읽을 수 없습니다.")
                return
            
            # Get current metadata
            title = audiofile.tag.title
            artist = audiofile.tag.artist
            
            if not title or not artist:
                self.log_message.emit(f"⚠️ {os.path.basename(file_path)} - 제목 또는 아티스트 정보가 없습니다.")
                return
            
            # Check if we should process this file
            if self.only_without_genre and audiofile.tag.genre:
                return
            
            # Get track info
            genres, year = self.get_track_info(title, artist)
            
            if genres:
                # Map genres
                mapped_genres = []
                for genre in genres:
                    for category, keywords in self.genre_mapping.items():
                        if any(keyword in genre.lower() for keyword in keywords):
                            mapped_genres.append(category)
                            break
                
                if mapped_genres:
                    # Update genre
                    audiofile.tag.genre = ", ".join(set(mapped_genres))
                    
                    # Update year if available
                    if year:
                        audiofile.tag.recording_date = year
                        self.log_message.emit(f"✅ {title} - 메타데이터가 업데이트되었습니다 (장르: {audiofile.tag.genre}, 연도: {year})")
                    else:
                        self.log_message.emit(f"✅ {title} - 장르 정보가 업데이트되었습니다 ({audiofile.tag.genre})")
                    
                    audiofile.tag.save()
                    return True
                else:
                    self.log_message.emit(f"⚠️ {title} - 매칭되는 장르를 찾지 못했습니다.")
            else:
                self.log_message.emit(f"⚠️ {title} - 장르 정보를 찾지 못했습니다.")
            
            return False
        except Exception as e:
            self.log_message.emit(f"❌ {os.path.basename(file_path)} - 처리 중 오류 발생: {str(e)}")
            return False

    def run(self):
        try:
            # Get all MP3 files
            mp3_files = []
            for root, _, files in os.walk(self.music_dir):
                for file in files:
                    if file.lower().endswith(".mp3"):
                        mp3_files.append(os.path.join(root, file))
            
            total_files = len(mp3_files)
            processed_files = 0
            updated_files = 0
            
            self.log_message.emit(f"🎵 총 {total_files}개의 MP3 파일을 처리합니다...")
            
            for file_path in mp3_files:
                if self.process_file(file_path):
                    updated_files += 1
                processed_files += 1
                self.progress_updated.emit(int((processed_files / total_files) * 100))
                self.log_message.emit(f"📊 진행률: {processed_files}/{total_files} (업데이트: {updated_files})")
            
            self.log_message.emit(f"✨ 완료! {updated_files}개 파일이 업데이트되었습니다.")
        except Exception as e:
            self.log_message.emit(f"❌ 오류 발생: {str(e)}")