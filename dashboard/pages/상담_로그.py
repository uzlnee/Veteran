import streamlit as st
import pandas as pd
import os
from datetime import datetime

# def render():
#     st.title("📞 상담 로그")
#     df = pd.read_csv("data/logs.csv")
#     st.dataframe(df)

#     # 선택된 사용자의 상담 내용 보기
#     user = st.selectbox("상담자 선택", df["이름"].unique())
#     selected = df[df["이름"] == user]
#     st.subheader("상담 내용 요약")
#     st.text_area("상담 STT 요약", selected["상담요약"].values[0], height=200)

# 절대 경로 설정
BASE_DIR = "/Users/jeong-yujin/Desktop/Veteran/recordings"

st.title("📞 상담 로그")

# 상담 세션 폴더 리스트 불러오기
sessions = sorted(os.listdir(BASE_DIR), reverse=True)  # 최신 순 정렬
sessions = [s for s in sessions if os.path.isdir(os.path.join(BASE_DIR, s))]

# 사용자 선택
selected_session = st.selectbox("상담 세션 선택", sessions)


# 세션 경로 설정
session_path = os.path.join(BASE_DIR, selected_session)
audio_files = sorted([f for f in os.listdir(session_path) if f.endswith(".wav")])
text_path = os.path.join(session_path, "transcript.txt")

# 날짜, 시간 정보 추출
date_str, time_str = selected_session.split("_")
date_fmt = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
time_fmt = datetime.strptime(time_str, "%H%M%S").strftime("%H:%M:%S")

st.markdown(f"🗓️ **상담일자**: {date_fmt} / 🕒 **상담시간**: {time_fmt}")

# 사용자 이름 추출 (예시: USER_0001.wav → 0001)
user_id = ""
for f in audio_files:
    if f.startswith("USER"):
        user_id = f.replace("USER_", "").replace(".wav", "")
        break
st.markdown(f"👤 **사용자 ID**: {user_id if user_id else '알 수 없음'}")

# 녹음 파일 재생
st.subheader("🔊 녹음파일")
cols = st.columns(2)
for f in audio_files:
    with cols[0 if f.startswith("USER") else 1]:
        st.audio(os.path.join(session_path, f), format="audio/wav", start_time=0)
        st.caption(f)

# 텍스트 출력
st.subheader("📝 상담 내용 (transcript.txt)")
if os.path.exists(text_path):
    with open(text_path, "r", encoding="utf-8") as file:
        content = file.read()
    st.text_area("상담 텍스트", content, height=300)
else:
    st.warning("transcript.txt 파일이 없습니다.")