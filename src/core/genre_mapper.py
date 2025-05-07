import os
import json
from typing import Dict, Optional

class GenreMapper:
    """장르 매핑을 관리하는 클래스"""
    
    def __init__(self, mapping_file: str = 'config/genre_mapping.json'):
        self.mapping_file = mapping_file
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict[str, str]:
        """장르 매핑을 파일에서 로드하거나 기본값을 사용"""
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_mapping()
    
    def _get_default_mapping(self) -> Dict[str, str]:
        """기본 장르 매핑 반환"""
        return {
            'r&b': 'R&B/Soul',
            'soul': 'R&B/Soul',
            'neo soul': 'R&B/Soul',
            'contemporary r&b': 'R&B/Soul',
            'hip hop': 'Hip-Hop/Rap',
            'rap': 'Hip-Hop/Rap',
            'trap': 'Hip-Hop/Rap',
            'urban': 'Hip-Hop/Rap',
            'k-pop': 'K-Pop',
            'kpop': 'K-Pop',
            'korean pop': 'K-Pop',
            'pop': 'Pop',
            'dance pop': 'Pop',
            'electropop': 'Pop',
            'electronic': 'Electronic/Dance',
            'dance': 'Electronic/Dance',
            'edm': 'Electronic/Dance',
            'house': 'Electronic/Dance',
            'techno': 'Electronic/Dance',
            'rock': 'Rock',
            'alternative rock': 'Rock',
            'indie rock': 'Rock',
            'jazz': 'Jazz',
            'smooth jazz': 'Jazz',
            'classical': 'Classical',
            'orchestra': 'Classical'
        }
    
    def normalize_genre(self, genre: Optional[str]) -> Optional[str]:
        """장르 문자열을 정규화"""
        if not genre:
            return None
        genre = genre.lower().strip()
        for key, value in self.mapping.items():
            if key in genre:
                return value
        return None 