# import streamlit as st
# import os
# import json
# from datetime import datetime

# # 절대 경로 설정
# BASE_DIR = "/Users/jeong-yujin/Desktop/Veteran/recordings"

# st.title("📞 상담 로그")

# # 상담 세션 폴더 리스트 불러오기
# sessions = sorted(os.listdir(BASE_DIR), reverse=True)  # 최신 순 정렬
# sessions = [s for s in sessions if os.path.isdir(os.path.join(BASE_DIR, s))]

# # 사용자 선택
# selected_session = st.selectbox("상담 세션 선택", sessions)


# # 세션 경로 설정
# session_path = os.path.join(BASE_DIR, selected_session)
# audio_files = sorted([f for f in os.listdir(session_path) if f.endswith(".wav")])
# text_path = os.path.join(session_path, "transcript.txt")

# # 날짜, 시간 정보 추출
# date_str, time_str = selected_session.split("_")
# date_fmt = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
# time_fmt = datetime.strptime(time_str, "%H%M%S").strftime("%H:%M:%S")

# st.markdown(f"🗓️ **상담일자**: {date_fmt} / 🕒 **상담시간**: {time_fmt}")

# # 사용자 이름 추출 (예시: USER_0001.wav → 0001)
# user_id = ""
# for f in audio_files:
#     if f.startswith("USER"):
#         user_id = f.replace("USER_", "").replace(".wav", "")
#         break
# st.markdown(f"👤 **사용자 ID**: {user_id if user_id else '알 수 없음'}")

# # 녹음 파일 재생
# st.subheader("🔊 녹음파일")
# cols = st.columns(2)
# for f in audio_files:
#     with cols[0 if f.startswith("USER") else 1]:
#         st.audio(os.path.join(session_path, f), format="audio/wav", start_time=0)
#         st.caption(f)

# # 텍스트 출력
# st.subheader("📝 상담 내용 (transcript.txt)")
# if os.path.exists(text_path):
#     with open(text_path, "r", encoding="utf-8") as file:
#         content = file.read()
#     st.text_area("상담 텍스트", content, height=300)
# else:
#     st.warning("transcript.txt 파일이 없습니다.")

import streamlit as st
import os
import json
from datetime import datetime

BASE_DIR = "../recordings"

st.title("📞 상담 로그")

# 1. 상담 세션 목록 (오름차순 정렬)
sessions = sorted([
    s for s in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, s))
])  # 오름차순 = 오래된 순

selected_session = st.selectbox("상담 세션 선택", sessions)

# 2. 날짜, 시간 추출
session_path = os.path.join(BASE_DIR, selected_session)
date_str, time_str = selected_session.split("_")
date_fmt = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
time_fmt = datetime.strptime(time_str, "%H%M%S").strftime("%H:%M:%S")

st.markdown(f"🗓️ **상담일자**: {date_fmt}")
st.markdown(f"🕒 **상담시간**: {time_fmt}")

# 3. 사용자 ID = 오름차순 세션 순서대로 부여
session_index = sessions.index(selected_session) + 1
user_id = f"USER_{session_index:03d}"
st.markdown(f"👤 **사용자 ID**: {user_id}")

# 4. 사용자 정보 요약 (metadata.json)
st.subheader("📋 구직희망자 정보 요약")

meta_path = os.path.join(session_path, "metadata.json")
if os.path.exists(meta_path):
    with open(meta_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    field_mapping = {
        'name': '이름',
        'age': '나이',
        'location': '거주지',
        'available_time': '희망 시간대',
        'license': '자격증',
        'preferred_field': '희망 분야',
        'health_condition': '건강 상태',
        'carrer': '경력',
        'education': '학력'
    }

    for i, (key, label) in enumerate(field_mapping.items()):
        if i % 2 == 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{label}**")
                st.write(user_data.get(key, '없음'))
        else:
            with col2:
                st.markdown(f"**{label}**")
                st.write(user_data.get(key, '없음'))

else:
    st.warning("metadata.json 파일이 없습니다.")

# 5. 상담 대화 텍스트
st.subheader("📝 상담 대화 텍스트")

text_path = os.path.join(session_path, "transcript.txt")
if os.path.exists(text_path):
    with open(text_path, "r", encoding="utf-8") as file:
        transcript = file.read()
    st.text_area("음성 텍스트(STT 결과)", transcript, height=300)
else:
    st.warning("transcript.txt 파일이 없습니다.")

# 6. 녹음 파일 (하단 expander)
st.subheader("🔊 상담 녹음파일")
audio_files = sorted([
    f for f in os.listdir(session_path)
    if f.endswith(".wav")
])

with st.expander("🎧 녹음파일 보기"):
    cols = st.columns(2)
    for f in audio_files:
        with cols[0 if f.startswith("USER") else 1]:
            st.audio(os.path.join(session_path, f), format="audio/wav", start_time=0)
            st.caption(f)
