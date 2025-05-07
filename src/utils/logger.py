import logging
import os
from datetime import datetime

def setup_logger(log_dir: str = 'logs') -> logging.Logger:
    """로거 설정"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(
        log_dir,
        f'genre_organizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    
    logger = logging.getLogger('GenreOrganizer')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 