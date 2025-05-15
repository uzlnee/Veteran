
import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd

BASE_DIR = "../recordings"

st.set_page_config(page_title="베테랑 대시보드", layout="wide")
st.title("🏠 베테랑 관리자 대시보드")

# 🔍 recordings 폴더에서 날짜 정보 추출
sessions = sorted([
    s for s in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, s))
])

session_dates = []
for s in sessions:
    try:
        date_str, time_str = s.split("_")
        dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        session_dates.append(dt)
    except:
        continue

# 📊 KPI 요약
now = datetime.now()
total_sessions = len(session_dates)
recent_sessions = sum(1 for d in session_dates if now - d <= timedelta(hours=24))
matching_rate = 68.5  # 예시 값

st.subheader("📊 주요 지표")
col1, col2, col3 = st.columns(3)
col1.metric("누적 상담 수", f"{total_sessions}건")
col2.metric("매칭 성공률", f"{matching_rate}%")
col3.metric("최근 상담(24h)", f"{recent_sessions}건")

# 📆 주차 선택 및 시각화
st.subheader("📈 주차별 상담 수 추이 (요일/날짜 기준)")

if not session_dates:
    st.warning("상담 데이터가 없습니다.")
else:
    session_dates.sort()
    first_day = session_dates[0].date()
    last_day = now.date()

    week_starts = []
    current = first_day - timedelta(days=first_day.weekday())
    while current <= last_day:
        week_starts.append(current)
        current += timedelta(weeks=1)

    week_options = [
        f"{ws.year}년 {ws.month}월 {ws.isocalendar()[1]}주차 ({ws.strftime('%m/%d')}~{(ws + timedelta(days=6)).strftime('%m/%d')})"
        for ws in week_starts
    ]
    selected_idx = st.selectbox("조회할 주차 선택", range(len(week_starts)), format_func=lambda i: week_options[i])
    selected_start = week_starts[selected_idx]
    selected_end = selected_start + timedelta(days=6)

    # 날짜별 상담 수 집계
    weekday_labels = ['월', '화', '수', '목', '금', '토', '일']
    week_dates = [selected_start + timedelta(days=i) for i in range(7)]
    date_counts = {d: 0 for d in week_dates}
    for dt in session_dates:
        d = dt.date()
        if selected_start <= d <= selected_end:
            date_counts[d] += 1

    # DataFrame 생성
    df = pd.DataFrame({
        "날짜": [d.strftime("%m/%d") for d in date_counts.keys()],
        "요일": [weekday_labels[d.weekday()] for d in date_counts.keys()],
        "상담 수": list(date_counts.values())
    })
    df["x축"] = df["요일"] + " (" + df["날짜"] + ")"
    df = df.sort_values("날짜")

    # 📈 그래프 유형 선택
    chart_type = st.radio("그래프 유형 선택", ["막대그래프", "선형그래프"], horizontal=True)
    if chart_type == "막대그래프":
        st.bar_chart(df.set_index("x축")["상담 수"])
    else:
        st.line_chart(df.set_index("x축")["상담 수"])

    # 📋 상담 수 요약 데이터 보기
    with st.expander("📋 상담 수 요약 테이블 보기"):
        st.dataframe(df[["요일", "날짜", "상담 수"]], use_container_width=True)

    # 📥 CSV 다운로드
    csv = df[["요일", "날짜", "상담 수"]].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 상담 수 데이터 CSV 다운로드",
        data=csv,
        file_name=f"상담수_요약_{selected_start.strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
