from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime
from collections import defaultdict, Counter
import re

app = FastAPI()

# # 정적 폴더 경로를 절대경로로 확인
# base_dir = os.path.dirname(os.path.abspath(__file__))
# job_data_path = os.path.join(base_dir, "../recommendation/user_jobs")

# app.mount("/api/jobs", StaticFiles(directory=job_data_path), name="user-jobs")

# CORS 설정 (필요시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프론트엔드 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RECORDINGS_DIR = "/home/yujin/Veteran/recordings"
USER_JOBS_DIR = "/home/yujin/Veteran/recommendation/result"


# 상담 총 횟수
def get_total_sessions():
    return len([
        name for name in os.listdir(RECORDINGS_DIR)
        if os.path.isdir(os.path.join(RECORDINGS_DIR, name))
    ])

# 최근 24시간 상담
def get_recent_sessions():
    count = 0
    today = datetime.now().date()
    for folder in os.listdir(RECORDINGS_DIR):
        meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
                created_at = meta.get("created_at")
                if created_at:
                    try:
                        created_date = datetime.strptime(created_at, "%Y-%m-%d").date()
                        if created_date == today:
                            count += 1
                    except:
                        continue
    return count

# 매칭 성공률
def get_match_success_rate():
    success = 0
    total = 0
    for folder in os.listdir(RECORDINGS_DIR):
        meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
                total += 1
                if meta.get("matched", False):
                    success += 1
    return round((success / total) * 100, 1) if total > 0 else 0.0

# 신규 사용자 수 (오늘 생성된 user_id 수)
def get_new_users_today():
    today = datetime.now().date()
    user_ids = set()
    for folder in os.listdir(RECORDINGS_DIR):
        meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
                created_at = meta.get("created_at")
                user_id = meta.get("user_id")
                if created_at and user_id:
                    try:
                        created_date = datetime.strptime(created_at, "%Y-%m-%d").date()
                        if created_date == today:
                            user_ids.add(user_id)
                    except:
                        continue
    return len(user_ids)

def get_weekly_session_counts():
    weekly = defaultdict(int)
    for folder in os.listdir(RECORDINGS_DIR):
        try:
            date_str = folder.split("_")[0]
            session_date = datetime.strptime(date_str, "%Y%m%d")
            weekday = session_date.strftime("%a")
            weekday_kor = {
                "Mon": "월", "Tue": "화", "Wed": "수",
                "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"
            }[weekday]
            weekly[weekday_kor] += 1
        except:
            continue
    # 요일 순서대로 출력
    return [{"day": d, "count": weekly.get(d, 0)} for d in ["월", "화", "수", "목", "금", "토", "일"]]

def get_match_rate_trend():
    match_by_day = defaultdict(list)
    for file in os.listdir(USER_JOBS_DIR):
        if file.endswith(".json"):
            try:
                with open(os.path.join(USER_JOBS_DIR, file), encoding="utf-8") as f:
                    data = json.load(f)
                date_str = file.split("_")[1].split(".")[0]
                date = datetime.strptime(date_str, "%Y%m%d")
                weekday = date.strftime("%a")
                weekday_kor = {
                    "Mon": "월", "Tue": "화", "Wed": "수",
                    "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"
                }[weekday]
                matched = any(
                    job.get("matched", False)
                    for rec in data.get("recommendations", [])
                    for job in rec.get("jobPostings", [])
                )
                match_by_day[weekday_kor].append(matched)
            except:
                continue
    return [
        {
            "day": d,
            "rate": round(sum(match_by_day[d]) / len(match_by_day[d]) * 100, 1) if match_by_day[d] else 0.0
        }
        for d in ["월", "화", "수", "목", "금", "토", "일"]
    ]

# 1. 전체 recordings 디렉토리를 순회해서 기존 user_id 수집
def get_next_user_id():
    user_ids = []
    for folder in os.listdir(RECORDINGS_DIR):
        meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)
                    uid = meta.get("user_id")
                    if uid:
                        user_ids.append(uid)
            except:
                continue
    return generate_user_id_new(user_ids)

# 2. 날짜와 상관없이 user_id 숫자만 증가시키는 방식
def generate_user_id_new(existing_ids):
    # 숫자만 추출해서 max 값 계산
    max_id = 0
    for uid in existing_ids:
        match = re.search(r"(\d+)$", uid)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    new_id = max_id + 1
    return f"{new_id:04d}"  # 예: '0001', '0002', ...

@app.get("/api/summary")
def get_summary():
    # 연령/지역/희망분야 집계
    ages = []
    locations = []
    fields = []
    for folder in os.listdir(RECORDINGS_DIR):
        meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
        if not os.path.exists(meta_path):
            continue
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            if "age" in meta: ages.append(meta["age"])
            if "location" in meta:
                loc = str(meta["location"]).strip()
                # 띄어쓰기 기준 앞 요소만 사용
                loc_main = loc.split()[0] if loc else loc
                locations.append(loc_main)
            if "preferred_field" in meta: fields.append(meta["preferred_field"])
        except:
            continue
    # 연령대별 분포
    age_bins = Counter()
    for age in ages:
        try:
            a = int(age)
            if a < 70:
                age_bins["60대"] += 1
            elif a < 80:
                age_bins["70대"] += 1
            else:
                age_bins["80대 이상"] += 1
        except:
            continue
    age_distribution = [{"label": k, "value": v} for k, v in age_bins.items()]
    # 지역 분포
    region_distribution = Counter(locations)
    region_distribution = [{"label": k, "value": v} for k, v in region_distribution.items()]
    # 희망분야 분포
    field_distribution = Counter(fields)
    field_distribution = [{"label": k, "value": v} for k, v in field_distribution.items()]

    return {
        "total_sessions": get_total_sessions(),
        "match_success_rate": get_match_success_rate(),
        "last_24h_sessions": get_recent_sessions(),
        "new_users": get_new_users_today(),
        "traffic_change": 4.5,
        "match_rate_change": -1.2,
        "recent_change": 6.3,
        "user_change": 3.1,
        "weekly_session_counts": get_weekly_session_counts(),
        "match_rate_trend": [
            {"day": "월", "rate": 75.0},
            {"day": "화", "rate": 78.0},
            {"day": "수", "rate": 76.5},
            {"day": "목", "rate": 79.0},
            {"day": "금", "rate": 80.0},
            {"day": "토", "rate": 74.5},
            {"day": "일", "rate": 72.0}
        ],
        "age_distribution": age_distribution,
        "region_distribution": region_distribution,
        "field_distribution": field_distribution
    }

@app.patch("/api/sessions/{session_id}/metadata")
async def update_metadata(session_id: str, request: Request):
    path = os.path.join(RECORDINGS_DIR, session_id, "metadata.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="metadata.json not found")
    
    try:
        # 기존 메타데이터 읽기
        with open(path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # 요청 본문에서 새로운 값 가져오기
        update_data = await request.json()
        is_job_seeking = update_data.get("is_job_seeking")
        if is_job_seeking is not None:
            metadata["is_job_seeking"] = is_job_seeking

        # 업데이트된 메타데이터 저장
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return {"status": "success", "session_id": session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/init")
def initialize_metadata(session_id: str):
    folder = os.path.join(RECORDINGS_DIR, session_id)
    os.makedirs(folder, exist_ok=True)
    
    user_id = get_next_user_id()
    metadata = {
        "user_id": user_id,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "matched": False,
        "job_seeking": False,
        "other_info": {}
    }

    meta_path = os.path.join(folder, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return {"message": "metadata initialized", "user_id": user_id}

# recordings 내 세션 폴더 리스트
@app.get("/api/sessions")
def get_sessions():
    try:
        folders = [
            name for name in os.listdir(RECORDINGS_DIR)
            if os.path.isdir(os.path.join(RECORDINGS_DIR, name))
        ]
        return sorted(folders)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# metadata.json
@app.get("/api/sessions/{session_id}/metadata")
def get_metadata(session_id: str):
    path = os.path.join(RECORDINGS_DIR, session_id, "metadata.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="metadata.json not found")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# transcript.txt
@app.get("/api/sessions/{session_id}/transcript", response_class=PlainTextResponse)
def get_transcript(session_id: str):
    path = os.path.join(RECORDINGS_DIR, session_id, "transcript.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="transcript.txt not found")
    with open(path, encoding="utf-8") as f:
        return f.read()

# 오디오 파일 목록
@app.get("/api/sessions/{session_id}/audios")
def get_audio_list(session_id: str):
    folder = os.path.join(RECORDINGS_DIR, session_id)
    if not os.path.exists(folder):
        raise HTTPException(status_code=404, detail="Session not found")

    wav_files = [
        f for f in os.listdir(folder)
        if f.endswith(".wav") and os.path.isfile(os.path.join(folder, f))
    ]
    return wav_files

# 정적 파일 (오디오) 서비스
app.mount("/recordings", StaticFiles(directory=RECORDINGS_DIR), name="recordings")


