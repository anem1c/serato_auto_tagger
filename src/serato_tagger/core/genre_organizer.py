import os
import eyed3
from PyQt5.QtCore import QThread, pyqtSignal
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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