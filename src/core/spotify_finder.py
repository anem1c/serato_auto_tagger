import logging
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyGenreFinder:
    """Spotify API를 사용하여 장르를 찾는 클래스"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
    
    def find_genre(self, track_name: str, artist_name: str) -> Optional[str]:
        """Spotify에서 곡의 장르를 검색"""
        try:
            results = self.sp.search(
                q=f'track:{track_name} artist:{artist_name}',
                type='track',
                limit=1
            )
            
            if not results['tracks']['items']:
                return None
                
            track = results['tracks']['items'][0]
            artist_id = track['artists'][0]['id']
            artist = self.sp.artist(artist_id)
            
            return artist['genres'][0] if artist['genres'] else None
            
        except Exception as e:
            logging.error(f"Spotify API 오류: {str(e)}")
            return None 