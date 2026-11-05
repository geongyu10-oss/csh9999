import streamlit as st
import pandas as pd
import soccerdata as sd
import re
from pathlib import Path

st.set_page_config(page_title="유럽 5대 리그 선수 기록 분석", page_icon="⚽", layout="wide")
st.title("⚽ 유럽 5대 리그 선수 시즌 기록 분석")
st.write("선수 이름과 시즌을 입력하면 Understat의 공개 통계에서 기록을 조회합니다.")

LEAGUES = ["ENG-Premier League", "ESP-La Liga", "GER-Bundesliga", "ITA-Serie A", "FRA-Ligue 1"]
KOREAN = {
    "ENG-Premier League": "프리미어리그", "ESP-La Liga": "라리가",
    "GER-Bundesliga": "분데스리가", "ITA-Serie A": "세리에 A", "FRA-Ligue 1": "리그 1"
}
CACHE = Path("/tmp/understat_cache")
CACHE.mkdir(parents=True, exist_ok=True)

@st.cache_data(ttl=86400, show_spinner=False)
def load_season(year):
    # Understat reader uses HTTP requests; it does not launch Selenium or Chrome.
    reader = sd.Understat(leagues=LEAGUES, seasons=[str(year)], data_dir=CACHE)
    df = reader.read_player_season_stats().reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join(str(v) for v in c if str(v) not in ("", "nan", "None")).strip() for c in df.columns]
    return df

def colname(df, key):
    return next((c for c in df.columns if str(c).strip().lower() == key.lower()), None)

with st.form("search"):
    c1, c2 = st.columns(2)
    with c1:
        player = st.text_input("선수 이름", placeholder="예: Son Heung-Min")
    with c2:
        season = st.text_input("시즌", value="2022-2023", placeholder="예: 2022-2023")
    go = st.form_submit_button("시즌 기록 검색", type="primary", use_container_width=True)

st.caption("선수 이름은 영문 입력을 권장합니다. 2022-2023 시즌은 2022-2023으로 입력하세요.")

if go:
    m = re.fullmatch(r"\s*(\d{4})\s*[-/]\s*(\d{2,4})\s*", season)
    if not player.strip():
        st.error("선수 이름을 입력해 주세요.")
    elif not m:
        st.error("시즌은 2022-2023 형식으로 입력해 주세요.")
    elif not 2014 <= int(m.group(1)) <= 2035:
        st.error("2014년 이후 시즌을 입력해 주세요.")
    else:
        year = int(m.group(1))
        try:
            with st.spinner("Understat에서 5대 리그 시즌 통계를 가져오는 중입니다. 첫 조회는 시간이 걸릴 수 있습니다."):
                df = load_season(year)
            pc = colname(df, "player")
            lc = colname(df, "league")
            if pc is None:
                st.error("자료에서 선수 이름 항목을 찾지 못했습니다.")
            else:
                mask = df[pc].fillna("").astype(str).str.casefold().str.contains(re.escape(player.strip().casefold()), na=False)
                found = df[mask].copy()
                if found.empty:
                    st.warning("해당 시즌에서 선수를 찾지 못했습니다. 영문 이름 일부로 다시 검색해 보세요.")
                else:
                    found["_label"] = found[pc].astype(str)
                    name = st.selectbox("검색 결과에서 선수 선택", found["_label"].drop_duplicates().tolist())
                    selected = found[found["_label"] == name]
                    st.subheader(f"{name} · {year}-{year+1} 시즌")
                    tc = colname(selected, "team")
                    metrics = [
                        ("출전 경기", "matches"), ("출전 시간(분)", "minutes"),
                        ("골", "goals"), ("도움", "assists"), ("기대 득점(xG)", "xg"),
                        ("기대 도움(xA)", "xa"), ("슈팅", "shots"), ("키 패스", "key_passes"),
                        ("경고", "yellow_cards"), ("퇴장", "red_cards")
                    ]
                    for i, (_, row) in enumerate(selected.iterrows()):
                        league = str(row[lc]) if lc else ""
                        team = str(row[tc]) if tc else "-"
                        st.markdown(f"### {KOREAN.get(league, league)} · {team}")
                        vals = []
                        for label, key in metrics:
                            cc = colname(selected, key)
                            v = row[cc] if cc else "-"
                            if pd.isna(v): v = "-"
                            elif isinstance(v, float): v = round(v, 2)
                            vals.append((label, v))
                        for start in range(0, len(vals), 5):
                            group = vals[start:start+5]
                            cols = st.columns(len(group))
                            for ui, (label, value) in zip(cols, group):
                                ui.metric(label, str(value))
                        table = pd.DataFrame(vals, columns=["기록 항목", "시즌 기록"])
                        st.dataframe(table, hide_index=True, use_container_width=True)
                        st.download_button("CSV 다운로드", table.to_csv(index=False).encode("utf-8-sig"),
                                           file_name=f"player_{year}_{i+1}.csv", mime="text/csv", key=f"csv{i}")
        except Exception as exc:
            st.error("Understat 자료를 불러오지 못했습니다.")
            st.caption(f"오류 종류: {type(exc).__name__}")
            st.code(str(exc))
            st.info("사이트 접속 제한 또는 네트워크 문제일 수 있습니다. 잠시 후 다시 시도해 주세요.")

with st.expander("자료 출처 및 안내"):
    st.markdown("""
    - 자료 출처: [Understat](https://understat.com/)
    - 수집 도구: [soccerdata Understat 문서](https://soccerdata.readthedocs.io/en/latest/datasources/Understat.html)
    - 대상: 프리미어리그, 라리가, 분데스리가, 세리에 A, 리그 1
    - 기록: 출전 경기, 출전 시간, 골, 도움, xG, xA, 슈팅, 키 패스, 경고, 퇴장 등
    - Understat에서 제공하는 과거 시즌 범위와 통계 항목에 따라 결과가 달라질 수 있습니다.
    - 이 버전은 FBref, Selenium, Chrome을 사용하지 않습니다.
    """)
