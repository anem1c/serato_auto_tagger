# Serato Auto Tagger

Serato DJ 소프트웨어를 위한 자동 음악 장르 태깅 도구입니다. 이 프로그램은 MP3 파일의 메타데이터를 분석하고, Spotify API를 활용하여 누락된 장르 정보와 연도 정보를 자동으로 채워넣습니다.

## 주요 기능

- MP3 파일의 장르 정보 자동 정리
- Spotify API를 통한 장르 정보 검색
- Spotify API를 통한 연도 정보 검색
- 직관적인 GUI 인터페이스
- 실시간 진행 상황 모니터링
- 상세한 처리 결과 로깅
- 병렬 처리로 빠른 성능

## 설치 방법

1. Python 3.7 이상이 필요합니다.
2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## Spotify API 설정

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에 접속합니다.
2. 로그인 후 "Create App" 버튼을 클릭합니다.
3. 애플리케이션 이름과 설명을 입력합니다.
4. 생성된 애플리케이션의 Client ID와 Client Secret을 복사합니다.
5. `src/main.py` 파일에서 다음 부분을 수정합니다:
```python
os.environ["SPOTIFY_CLIENT_ID"] = "YOUR_SPOTIFY_CLIENT_ID"  # 복사한 Client ID로 교체
os.environ["SPOTIFY_CLIENT_SECRET"] = "YOUR_SPOTIFY_CLIENT_SECRET"  # 복사한 Client Secret으로 교체
```

## 사용 방법

1. 프로그램 실행:
```bash
python src/main.py
```

2. GUI에서 다음 단계를 따릅니다:
   - "폴더 선택" 버튼을 클릭하여 음악 파일이 있는 디렉토리 선택
   - "장르가 없는 곡만 처리" 옵션 선택 (선택사항)
   - "연도 정보 업데이트" 옵션 선택 (선택사항)
   - "장르 정리 시작" 버튼 클릭

3. 처리 결과는 실시간으로 로그 창에 표시됩니다.

## 장르 매핑

기본 장르 매핑은 다음과 같습니다:

- R&B/Soul: r&b, soul, neo soul, contemporary r&b
- Hip-Hop/Rap: hip hop, rap, trap, urban
- K-Pop: k-pop, kpop, korean pop
- Pop: pop, dance pop, electropop
- Electronic/Dance: electronic, dance, edm, house, techno
- Rock: rock, alternative rock, indie rock
- Jazz: jazz, smooth jazz
- Classical: classical, orchestra

장르 매핑은 `genre_mapping.json` 파일을 통해 커스터마이즈할 수 있습니다.

## 로깅

프로그램은 `genre_organizer.log` 파일에 상세한 로그를 기록합니다. 로그에는 다음 정보가 포함됩니다:

- 처리된 파일 수
- 업데이트된 파일 수
- 오류 발생 파일
- 장르를 찾지 못한 파일 목록
- 연도 정보 업데이트 결과

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해 주세요.
