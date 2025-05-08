import os
import eyed3
from PyQt5.QtCore import QThread, pyqtSignal
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

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

    def get_track_info(self, track_name, artist_name):
        try:
            # Search for the track
            query = f"track:{track_name} artist:{artist_name}"
            results = self.spotify.search(q=query, type="track", limit=1)
            
            if results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                genres = []
                
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
                    self.log_message.emit(f"Found year for {track_name}: {year}")
                else:
                    self.log_message.emit(f"No valid year found for {track_name}")
                
                return genres, year
            return [], None
        except Exception as e:
            self.log_message.emit(f"Error getting track info: {str(e)}")
            return [], None

    def process_file(self, file_path):
        try:
            audiofile = eyed3.load(file_path)
            if not audiofile or not audiofile.tag:
                return
            
            # Get current metadata
            title = audiofile.tag.title
            artist = audiofile.tag.artist
            
            if not title or not artist:
                return
            
            # Check if we should process this file
            if self.only_without_genre and audiofile.tag.genre:
                return
            
            # Get track info from Spotify
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
                        self.log_message.emit(f"Updated year for {title}: {year}")
                    
                    audiofile.tag.save()
                    return True
            
            return False
        except Exception as e:
            self.log_message.emit(f"Error processing {file_path}: {str(e)}")
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
            
            for file_path in mp3_files:
                if self.process_file(file_path):
                    updated_files += 1
                processed_files += 1
                self.progress_updated.emit(int((processed_files / total_files) * 100))
                self.log_message.emit(f"Processed {processed_files}/{total_files} files. Updated: {updated_files}")
            
            self.log_message.emit(f"Completed! Updated {updated_files} out of {total_files} files.")
        except Exception as e:
            self.log_message.emit(f"Error: {str(e)}")