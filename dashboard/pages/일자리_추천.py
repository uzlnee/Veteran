import streamlit as st
import json
import os
import glob
from datetime import datetime

# 페이지 제목 설정
st.title("💼 일자리 추천 결과")

# recommendation 폴더에서 JSON 파일 목록 가져오기
recommendation_path = "../recommendation"
json_files = glob.glob(os.path.join(recommendation_path, "*.json"))

# 파일이 없는 경우 처리
if not json_files:
    st.warning("추천 결과 파일이 없습니다. 먼저 일자리 추천을 실행해주세요.")
    st.stop()

# 파일 선택 옵션 제공
file_options = [os.path.basename(file) for file in json_files]
selected_file = st.selectbox("추천 결과 파일 선택", file_options)

# 선택한 파일 읽기
with open(os.path.join(recommendation_path, selected_file), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 사용자 정보 추출
user_info = data.get("jobSeeker", {})
name = user_info.get("name", "알 수 없음")

# 부제목 표시
st.subheader(f"{name}님의 일자리 추천 결과")

# 생성 시간 표시
generated_at = data.get("generatedAt", "")
if generated_at:
    try:
        # ISO 형식 시간 파싱 및 포맷팅
        dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        formatted_date = dt.strftime("%Y년 %m월 %d일 %H:%M")
        st.caption(f"생성일시: {formatted_date}")
    except ValueError:
        st.caption(f"생성일시: {generated_at}")

# 사용자 정보 표시
with st.expander("👤 구직자 정보", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**이름:** {user_info.get('name', '-')}")
        st.write(f"**나이:** {user_info.get('age', '-')}세")
        st.write(f"**희망 지역:** {user_info.get('location', '-')}")
        st.write(f"**가능 시간:** {user_info.get('availableTime', '-')}")
    
    with col2:
        st.write(f"**보유 자격증:** {', '.join(user_info.get('licenses', ['-']))}")
        st.write(f"**희망 분야:** {', '.join(user_info.get('preferredFields', ['-']))}")
        st.write(f"**건강 상태:** {user_info.get('healthCondition', '-')}")
        st.write(f"**학력:** {user_info.get('education', '-')}")
    
    # 경력 정보 표시
    if user_info.get('career'):
        st.write("**경력:**")
        for career in user_info.get('career', []):
            st.write(f"- {career.get('org', '')} {career.get('title', '')} {career.get('years', '')}년")

# 추천 직업 목록 표시
recommendations = data.get("recommendations", [])
if recommendations:
    st.header("📋 추천 직업 목록")
    
    # 탭 생성
    tabs = st.tabs([f"{i+1}순위: {rec.get('occupation', {}).get('title', '정보 없음')}" 
                    for i, rec in enumerate(recommendations)])
    
    # 각 탭에 직업 정보 표시
    for i, (tab, rec) in enumerate(zip(tabs, recommendations)):
        with tab:
            occupation = rec.get("occupation", {})
            
            # 직업 정보 표시
            st.subheader(f"{occupation.get('title', '정보 없음')}")
            st.write(f"**직업 분류:** {occupation.get('category', '정보 없음')}")
            st.write(f"**추천 이유:** {occupation.get('reason', '정보 없음')}")
            st.write(f"**직업 코드:** {occupation.get('code', '정보 없음')}")
            
            # 직업 상세 정보
            with st.expander("직업 상세 정보", expanded=True):
                st.write(f"**요약:** {occupation.get('summary', '정보 없음')}")
                
                # 하는 일 목록
                if occupation.get('tasks'):
                    st.write("**하는 일:**")
                    for task in occupation.get('tasks', []):
                        if task.strip():
                            st.write(f"- {task}")
                
                st.write(f"**되는 길:** {occupation.get('careerPath', '정보 없음')}")
            
            # 구인 정보 표시
            job_postings = rec.get("jobPostings", [])
            if job_postings:
                st.subheader("📢 구인 정보")
                
                for j, posting in enumerate(job_postings):
                    with st.expander(f"{posting.get('title', '정보 없음')}"):
                        st.write(f"**사업장명:** {posting.get('company', '-')}")
                        st.write(f"**사업장주소:** {posting.get('address', '-')}")
                        
                        # 거리 정보가 있으면 표시
                        if posting.get('distanceKm') is not None:
                            st.write(f"**거리:** {posting.get('distanceKm')}km")
                        
                        st.write(f"**연령:** {posting.get('ageLimit', '-')}")
                        
                        # 접수기간 정보
                        period = posting.get('applicationPeriod', {})
                        if period and (period.get('from') or period.get('to')):
                            st.write(f"**접수기간:** {period.get('from', '-')} ~ {period.get('to', '-')}")
                        
                        # 접수방법
                        if posting.get('applyMethod'):
                            st.write(f"**접수방법:** {posting.get('applyMethod')}")
                        
                        # 연락처 정보
                        if posting.get('contact'):
                            st.write(f"**담당자연락처:** {posting.get('contact')}")
                        
                        # 홈페이지 정보
                        if posting.get('homepage') and posting.get('homepage') != '-':
                            st.write(f"**홈페이지:** {posting.get('homepage')}")
                        
                        # 상세 내용
                        if posting.get('details') and posting.get('details') != '-':
                            st.write(f"**상세 내용:** {posting.get('details')}")
            else:
                st.info("현재 구인 정보가 없습니다.")
else:
    st.warning("추천 직업 정보가 없습니다.")
