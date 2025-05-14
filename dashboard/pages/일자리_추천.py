import streamlit as st
import pandas as pd

# def render():
#     st.title("💼 일자리 추천 결과")
#     df = pd.read_csv("data/recommendations.csv")

#     job_filter = st.selectbox("직종 필터", df["직종"].unique())
#     filtered = df[df["직종"] == job_filter]

#     for _, row in filtered.iterrows():
#         with st.expander(f"{row['직종']} - {row['회사명']}"):
#             st.write(f"📍 지역: {row['지역']}")
#             st.write(f"💰 급여: {row['급여']} / ⏱️ 근무시간: {row['근무시간']}")
#             st.write(f"📄 설명: {row['설명']}")

st.title("💼 일자리 추천 결과")

# 추천 결과 데이터 불러오기
df = pd.read_csv("data/recommendations.csv")  # 파일은 직접 준비해야 함

# 필터: 직종
job_type = st.selectbox("직종 필터", df["직종"].unique())

filtered = df[df["직종"] == job_type]

# 추천 일자리 목록
st.subheader(f"🔍 '{job_type}' 관련 추천 일자리")
for _, row in filtered.iterrows():
    with st.expander(f"{row['직종']} | {row['회사명']}"):
        st.write(f"📍 지역: {row['지역']}")
        st.write(f"💰 급여: {row['급여']} / ⏱ 근무시간: {row['근무시간']}")
        st.write(f"📄 상세 내용: {row['설명']}")
