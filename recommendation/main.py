
"""
일자리 추천 시스템의 메인 실행 스크립트
- recordings/의 사용자 데이터를 읽어와 맞춤형 일자리 추천 수행
- 출력: 터미널 출력 + JSON 파일 저장 (recommendation/result/사용자명_날짜.json)

[전체 프로세스]
 1단계: 사용자 데이터 로드
  - recordings 폴더에서 가장 최근 폴더 탐색
  - metadata.json에서 사용자 정보 로드 (이름, 나이, 지역, 희망분야 등)

 2단계: 공고 데이터 필터링
  - job_filter를 통해 전체 공고에서 사용자 조건에 맞는 후보 추출
  - 희망 분야 + 지역 기반 1차 필터링

 3단계: AI 추천 수행
  - job_recommender를 통해 점수 계산 및 순위 결정
  - 상위 추천 공고에 대한 AI 추천 이유 생성

 4단계: 결과 출력 및 저장
  - 터미널에 추천 결과 출력 (순위, 점수, 추천 이유, 회사 정보)
  - JSON 형식으로 상세 결과를 해당 recordings 폴더에 저장
  - 구직자명_YYYYMMDD_HHMMSS.json 형식으로 파일명 생성

[실행 조건]
 - job_crawler.py를 통해 job_openings.pkl 파일이 생성되어 있어야 함
 - recordings/YYYYMMDD_HHMMSS/ 폴더에 metadata.json 파일이 있어야 함
"""

import os
import json
import sys # sys 모듈 추가
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from job_recommender import JobRecommender
from job_filter import JobOpeningService

class ElderlyUser(BaseModel):
    """구직자 정보를 담는 데이터 클래스"""
    name: str = Field(default="")
    age: int = Field(default=0)
    location: str = Field(default="")
    available_time: str = Field(default="")
    license: List[str] = Field(default_factory=list)
    preferred_field: List[str] = Field(default_factory=list)
    health_condition: str = Field(default="")
    career: str = Field(default="")
    education: str = Field(default="")

def print_recommendation_results(user: ElderlyUser, ranked_openings: List[dict]):
    """새로운 추천 결과를 터미널에 출력합니다."""
    print("\n" + "="*50)
    print(f"      맞춤 공고 추천 결과")
    print("="*50)
    print(f"\n[ 구직자 정보 ]")
    print(f"  - 이름: {user.name} ({user.age}세)")
    print(f"  - 희망 지역: {user.location}")
    print(f"  - 희망 분야: {', '.join(user.preferred_field)}")
    
    print(f"[ AI 추천 맞춤 공고 목록 ]")
    if not ranked_openings:
        print(">> 추천할 수 있는 맞춤 공고가 없습니다.")
    else:
        for i, opening in enumerate(ranked_openings, 1):
            print(f"\n--- {i}순위: {opening.get('채용제목', '정보 없음')} (점수: {opening.get('score', 0):.2f}) ---")
            print(f"  - 추천 이유: {opening.get('reason', 'AI 추천')}")
            print(f"  - 사업장: {opening.get('사업장명', '정보 없음')}")
            print(f"  - 주소: {opening.get('주소', '정보 없음')} (거리: {opening.get('거리', '-')})")
    print("\n" + "="*50)

def generate_json_output(user: ElderlyUser, ranked_openings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """새로운 추천 결과를 JSON 형식의 딕셔너리로 생성합니다."""
    job_seeker_data = user.dict()

    recommendations_data = []
    for i, opening in enumerate(ranked_openings, 1):
        recommendation = {
            "rank": i,
            "unifiedScore": round(opening.get('score', 0), 4),
            "reason": opening.get('reason', 'AI 추천'),
            "jobPosting": {
                "title": opening.get('채용제목', ''),
                "company": opening.get('사업장명', ''),
                "address": opening.get('주소', ''),
                "distanceKm": JobOpeningService.parse_distance(opening.get('거리', '999')) if opening.get('거리') else None,
                "details": opening.get('상세내용', '')
            }
        }
        recommendations_data.append(recommendation)

    return {
        "generatedAt": datetime.now().isoformat(),
        "jobSeeker": job_seeker_data,
        "recommendations": recommendations_data
    }

def save_json_output(data: Dict[str, Any], user_name: str, recording_folder: str):
    """JSON 데이터를 해당 recordings 폴더에 저장합니다."""
    # 파일명을 구직자명_YYYYMMDD_HHMMSS.json 형식으로 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{user_name}_{timestamp}.json"
    full_path = os.path.join(recording_folder, filename)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n>>> [성공] 최종 결과가 다음 경로에 저장되었습니다: {full_path}")
    except Exception as e:
        print(f"\n>>> [오류] JSON 파일 저장 중 오류 발생: {e}")

def load_user_from_metadata(metadata_path: str) -> Optional[ElderlyUser]:
    """metadata.json 파일에서 사용자 정보를 로드합니다."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ElderlyUser(**data)
    except Exception as e:
        print(f">>> [오류] 메타데이터 로드 중 예외 발생: {e}")
        return None

def get_latest_recording_folder():
    """recordings 폴더에서 가장 최근에 수정된 폴더를 찾습니다."""
    try:
        # 스크립트 파일의 절대 경로를 기준으로 상위 폴더 경로를 계산
        base_dir = os.path.dirname(os.path.abspath(__file__))
        recordings_dir = os.path.join(base_dir, '..', 'recordings')
        
        # 경로 정규화 (e.g., /a/b/../c -> /a/c)
        recordings_dir = os.path.normpath(recordings_dir)

        if not os.path.exists(recordings_dir):
            print(f">>> [오류] 'recordings' 폴더를 찾을 수 없습니다. 확인된 경로: {recordings_dir}")
            return None
        # recordings 디렉토리의 모든 하위 폴더 가져오기
        subfolders = [f for f in os.scandir(recordings_dir) if f.is_dir()]

        if not subfolders:
            print(f">>> [오류] 'recordings' 폴더에 하위 폴더가 없습니다.")
            return None

        # YYYYMMDD_HHMMSS 형식의 폴더만 필터링
        valid_folders = []
        for f in subfolders:
            try:
                datetime.strptime(f.name, "%Y%m%d_%H%M%S")
                valid_folders.append(f.path)
            except ValueError:
                continue

        if not valid_folders:
            print(f">>> [오류] 'recordings' 폴더 내에 'YYYYMMDD_HHMMSS' 형식의 폴더가 없습니다.")
            return None

        # 이름순으로 정렬하여 가장 최신 폴더를 반환
        return max(valid_folders)
    except Exception as e:
        print(f">>> [오류] 녹음 폴더를 찾는 중 예외 발생: {e}")
        return None

def main():
    print("="*40)
    print(">>> [0] 프로그램 실행 시작")
    
    # 명령줄 인자로 폴더 경로가 주어졌는지 확인
    if len(sys.argv) > 1:
        recording_folder = sys.argv[1]
        if not os.path.isdir(recording_folder):
            print(f">>> [오류] 지정된 폴더를 찾을 수 없습니다: {recording_folder}")
            return
        print(f">>> [정보] 지정된 폴더로 처리: {os.path.basename(recording_folder)}")
    else:
        recording_folder = get_latest_recording_folder()
        if not recording_folder: return
        print(f">>> [정보] 처리 대상 폴더: {os.path.basename(recording_folder)}")
    
    metadata_path = os.path.join(recording_folder, "metadata.json")
    user = load_user_from_metadata(metadata_path)
    if not user: return
    
    print(f">>> [1] '{user.name}' 정보 로드 완료.")

    print("\n>>> [2] 전체 공고 검색 후 사용자 맞춤 필터링을 시작합니다.")
    job_filter = JobOpeningService()
    
    candidate_openings = job_filter.get_filtered_job_openings(
        user.preferred_field, 
        user.location
    )
    
    if not candidate_openings:
        print(">> 검색된 구인 공고가 없습니다. 프로그램을 종료합니다.")
        return

    print(f"\n>>> 총 {len(candidate_openings)}개의 후보 공고를 찾았습니다.")

    print("\n>>> [3] 점수 계산 및 AI 추천을 시작합니다.")
    job_recommender = JobRecommender()
    ranked_openings = job_recommender.get_recommendations(user, candidate_openings)

    print("\n>>> [4] 최종 추천 결과 출력을 시작합니다.")
    print_recommendation_results(user, ranked_openings)
    
    json_output = generate_json_output(user, ranked_openings)
    save_json_output(json_output, user.name, recording_folder)

    print("\n>>> [5] 모든 작업 완료. 프로그램을 종료합니다.")
    print("="*40)

if __name__ == "__main__":
    main()
