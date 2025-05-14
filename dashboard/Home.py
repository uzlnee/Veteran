import streamlit as st

st.set_page_config(page_title="베테랑 대시보드", layout="wide")

st.title("🏠 베테랑 관리자 대시보드")

# KPI 요약 지표
st.subheader("📊 주요 지표")
col1, col2, col3 = st.columns(3)
col1.metric("누적 상담 수", "1,230건")
col2.metric("매칭 성공률", "68.5%")
col3.metric("최근 상담(24h)", "47건")

# 상담 지역별 분포 (예시)
st.subheader("📍 지역별 상담 분포")
region_data = {
    "서울": 150,
    "경기": 200,
    "전남": 90,
    "경북": 80,
    "부산": 120
}
st.bar_chart(region_data)
