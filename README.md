# 유럽 5대 리그 선수 시즌 기록 분석 — Understat

FBref + Selenium 대신 Understat 공개 선수 시즌 통계를 사용합니다. Understat 수집기는 HTTP 요청 기반이므로 Chrome/ChromeDriver가 필요하지 않습니다.

## 실행
`pip install -r requirements.txt` 후 `streamlit run app.py`를 실행합니다.
선수 이름(영문 권장)과 시즌(예: `2022-2023`)을 입력합니다.

## 배포
GitHub 저장소 루트에서 `app.py`, `requirements.txt`, `README.md`를 교체한 뒤 Streamlit 앱을 재배포하세요. 이전 버전의 `packages.txt`는 삭제해도 됩니다.

## 출처
- Understat: https://understat.com/
- soccerdata: https://soccerdata.readthedocs.io/en/latest/datasources/Understat.html

대상 리그: 프리미어리그, 라리가, 분데스리가, 세리에 A, 리그 1.
