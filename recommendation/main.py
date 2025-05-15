from dataclasses import dataclass
from typing import List, Dict, Any
import json
from datetime import datetime
import re
from job_recommender import JobRecommender
from job_opening_service import JobOpeningService
from gemini_service import GeminiService

@dataclass
class ElderlyUser:
    name: str
    age: int
    location: str
    available_time: str
    license: List[str]
    preferred_field: List[str]
    health_condition: str
    career: str
    education: str

def print_recommendation_results(user: ElderlyUser, recommended_jobs: List[dict], job_openings: List[dict]):
    """추천 결과를 보기 좋게 출력합니다."""
    from datetime import datetime
    
    print("\n" + "="*30)
    print(f"고령자 취업 추천 결과 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*30)
    
    print(f"\n[구직자 정보]")
    print(f"이름: {user.name}")
    print(f"나이: {user.age}세")
    print(f"희망 지역: {user.location}")
    print(f"가능 시간: {user.available_time}")
    print(f"보유 자격증: {', '.join(user.license)}")
    print(f"희망 분야: {', '.join(user.preferred_field)}")
    print(f"건강 상태: {user.health_condition}")
    print(f"학력: {user.education}")
    print(f"경력: {user.career}")
    
    print("\n" + "="*30)
    print("[추천 직업 목록]")
    print("="*30)
    
    job_opening_service = JobOpeningService()
    
    for i, job in enumerate(recommended_jobs, 1):
        print(f"\n{i}순위: {job.get('position', '정보 없음')}")
        print("-"*30)
        print(f"직업 분류: {job.get('category_name', '정보 없음')}")
        print(f"추천 이유: {job.get('reason', '정보 없음')}")
        print(f"직업 코드: {job.get('job_code', '정보 없음')}")
        print("\n[직업 상세 정보]")
        print(f"요약: {job.get('summary', '정보 없음')}")
        print(f"하는 일: {job.get('tasks', '정보 없음')}")
        print(f"되는 길: {job.get('way', '정보 없음')}")
        
        # 해당 직업의 구인 정보 출력
        if job_openings:
            print("\n[구인 정보]")
            print("-"*30)
            
            # 거리 기반으로 정렬된 구인 정보 가져오기
            sorted_openings = job_opening_service.sort_by_distance(user.location, job_openings)
            
            for j, opening in enumerate(sorted_openings, 1):
                print(f"\n* 채용 공고 {j} *")
                print(f"<{opening.get('채용제목', '-')}>")
                print(f"사업장명: {opening.get('사업장명', '-')}")
                print(f"사업장주소: {opening.get('주소', '-')}")
                print(f"거리: {opening.get('거리', '-')}")
                print(f"연령: {opening.get('연령', '-')}세")
                print()
                print(f"접수기간: {opening.get('접수기간', '-')}")
                
                # 접수방법 코드 변환
                method_code = opening.get('접수방법', '')
                method = "-"
                if method_code == job_opening_service.APPLICATION_METHOD["ONLINE"]:
                    method = "온라인"
                elif method_code == job_opening_service.APPLICATION_METHOD["EMAIL"]:
                    method = "이메일"
                elif method_code == job_opening_service.APPLICATION_METHOD["FAX"]:
                    method = "팩스"
                elif method_code == job_opening_service.APPLICATION_METHOD["VISIT"]:
                    method = "방문"
                print(f"접수방법: {method}")
                
                print(f"담당자연락처: {opening.get('담당자연락처', '-')}")
                print(f"홈페이지: {opening.get('홈페이지', '-')}")
                print(f"상세 내용: {opening.get('상세내용', '-')}")
                print("-"*30)
        else:
            print("\n[구인 정보]")
            print("-"*30)
            print("현재 구인 정보가 없습니다.")
            print("-"*30)
        
        print("\n" + "="*30)

def generate_json_output(user: ElderlyUser, recommended_jobs: List[dict], job_openings: List[dict]) -> Dict[str, Any]:
    """추천 결과를 JSON 형식으로 반환합니다."""
    # 현재 시간을 ISO 형식으로 변환
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # 경력 정보 파싱 (예: "수원시청 시설관리직 15년, 대한부동산 공인중개사 10년")
    career_list = []
    career_pattern = r"([^,]+) ([^\d]+)(\d+)년"
    for career_match in re.finditer(career_pattern, user.career):
        org = career_match.group(1).strip()
        title = career_match.group(2).strip()
        years = int(career_match.group(3))
        career_list.append({
            "title": title,
            "org": org,
            "years": years
        })
    
    # 구직자 정보
    job_seeker = {
        "name": user.name,
        "age": user.age,
        "location": user.location,
        "availableTime": user.available_time,
        "licenses": user.license,
        "preferredFields": user.preferred_field,
        "healthCondition": user.health_condition,
        "career": career_list,
        "education": user.education
    }
    
    # 추천 직업 목록
    recommendations = []
    job_opening_service = JobOpeningService()
    
    for i, job in enumerate(recommended_jobs, 1):
        # 직업 정보
        occupation = {
            "title": job.get('position', '정보 없음'),
            "category": job.get('category_name', '정보 없음'),
            "code": job.get('job_code', '정보 없음'),
            "reason": job.get('reason', '정보 없음'),
            "summary": job.get('summary', '정보 없음'),
            "tasks": job.get('tasks', '정보 없음').split('\n') if job.get('tasks') else [],
            "careerPath": job.get('way', '정보 없음')
        }
        
        # 구인 정보
        job_postings = []
        if job_openings:
            # 거리 기반으로 정렬된 구인 정보 가져오기
            sorted_openings = job_opening_service.sort_by_distance(user.location, job_openings)
            
            for opening in sorted_openings:
                # 접수기간 파싱
                application_period = {"from": "", "to": ""}
                period = opening.get('접수기간', '-')
                if period and period != '-':
                    period_parts = period.split('~')
                    if len(period_parts) == 2:
                        application_period = {
                            "from": period_parts[0].strip(),
                            "to": period_parts[1].strip()
                        }
                
                # 접수방법 코드 변환
                method_code = opening.get('접수방법', '')
                method = None
                if method_code == job_opening_service.APPLICATION_METHOD["ONLINE"]:
                    method = "온라인"
                elif method_code == job_opening_service.APPLICATION_METHOD["EMAIL"]:
                    method = "이메일"
                elif method_code == job_opening_service.APPLICATION_METHOD["FAX"]:
                    method = "팩스"
                elif method_code == job_opening_service.APPLICATION_METHOD["VISIT"]:
                    method = "방문"
                
                # 거리 정보 추출
                distance_km = None
                distance_str = opening.get('거리', '-')
                if distance_str and distance_str != '-' and 'km' in distance_str:
                    try:
                        distance_km = float(distance_str.replace('km', ''))
                    except ValueError:
                        pass
                
                job_posting = {
                    "title": opening.get('채용제목', '-'),
                    "company": opening.get('사업장명', '-'),
                    "address": opening.get('주소', '-'),
                    "distanceKm": distance_km,
                    "ageLimit": opening.get('연령', '-'),
                    "applicationPeriod": application_period,
                    "applyMethod": method,
                    "contact": opening.get('담당자연락처', '-') if opening.get('담당자연락처') != '-' else None,
                    "homepage": opening.get('홈페이지', '-') if opening.get('홈페이지') != '-' else None,
                    "details": opening.get('상세내용', '-') if opening.get('상세내용') != '-' else None
                }
                job_postings.append(job_posting)
        
        recommendation = {
            "rank": i,
            "occupation": occupation,
            "jobPostings": job_postings
        }
        recommendations.append(recommendation)
    
    # 최종 JSON 구조
    result = {
        "generatedAt": current_time,
        "jobSeeker": job_seeker,
        "recommendations": recommendations
    }
    
    return result

def save_json_output(data: Dict[str, Any]) -> None:
    """JSON 데이터를 파일로 저장합니다. 파일명은 name_yyyymmdd.json 형식으로 생성됩니다."""
    # 사용자 이름과 현재 날짜로 파일명 생성
    name = data.get("jobSeeker", {}).get("name", "unknown")
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{name}_{current_date}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nJSON 결과가 {filename}에 저장되었습니다.")

def main():
    import os
    import sys
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        # 특정 폴더가 지정된 경우
        recording_folder = sys.argv[1]
        if not os.path.isdir(recording_folder):
            print(f"Error: {recording_folder}는 유효한 폴더가 아닙니다.")
            return
    else:
        # 가장 최근 녹음 폴더 사용
        recording_folder = get_latest_recording_folder()
        if not recording_folder:
            print("Error: 처리할 녹음 폴더를 찾을 수 없습니다.")
            return
    
    # metadata.json 파일 경로
    metadata_path = os.path.join(recording_folder, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"Error: {metadata_path} 파일이 존재하지 않습니다.")
        return
    
    # 사용자 정보 로드
    user = load_user_from_metadata(metadata_path)
    if not user:
        print("Error: 사용자 정보를 로드할 수 없습니다.")
        return
    
    print(f"\n[INFO] {recording_folder} 폴더의 사용자 정보를 처리합니다.")
    
    # 직업 추천 서비스 초기화
    job_recommender = JobRecommender()
    
    # 직업 추천
    recommended_jobs = job_recommender.get_recommended_jobs(user)
    if not recommended_jobs:
        print("추천할 수 있는 직업이 없습니다.")
        return
    
    # 구인 정보 서비스 초기화
    job_opening_service = JobOpeningService()
    
    # 모든 추천 직업에 대한 구인 정보 조회
    job_openings = job_opening_service.get_job_openings(recommended_jobs[0].get('job_code'), user.location)
    
    # 콘솔에 출력
    print_recommendation_results(user, recommended_jobs, job_openings)
    
    # JSON 형식으로 변환 및 저장
    json_output = generate_json_output(user, recommended_jobs, job_openings)
    
    # 결과 파일 저장 경로
    result_path = os.path.join(recording_folder, f"{user.name}_{datetime.now().strftime('%Y%m%d')}.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"\n결과가 {result_path}에 저장되었습니다.")
    
    # 기존 저장 방식도 유지 (프로젝트 루트에 저장)
    save_json_output(json_output)

def load_user_from_metadata(metadata_path):
    """metadata.json 파일에서 사용자 정보를 로드합니다."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # license와 preferred_field가 리스트가 아닌 경우 리스트로 변환
        license_data = data.get('license', [])
        if isinstance(license_data, str):
            license_data = [license_data] if license_data else []
        
        preferred_field_data = data.get('preferred_field', [])
        if isinstance(preferred_field_data, str):
            preferred_field_data = [preferred_field_data] if preferred_field_data else []
        
        # career 필드명이 carrer로 잘못 입력된 경우 처리
        career = data.get('career', data.get('carrer', ''))
        
        return ElderlyUser(
            name=data.get('name', ''),
            age=data.get('age', 0),
            location=data.get('location', ''),
            available_time=data.get('available_time', ''),
            license=license_data,
            preferred_field=preferred_field_data,
            health_condition=data.get('health_condition', ''),
            career=career,
            education=data.get('education', '')
        )
    except Exception as e:
        print(f"메타데이터 로드 중 오류 발생: {e}")
        return None

def get_latest_recording_folder():
    """recordings 폴더에서 가장 최근의 녹음 폴더를 찾습니다."""
    import os
    from datetime import datetime
    
    recordings_dir = "../recordings"
    if not os.path.exists(recordings_dir):
        print(f"Error: {recordings_dir} 폴더가 존재하지 않습니다.")
        return None
    
    folders = []
    for folder in os.listdir(recordings_dir):
        folder_path = os.path.join(recordings_dir, folder)
        if os.path.isdir(folder_path):
            try:
                # 폴더명이 날짜_시간 형식인지 확인 (예: 20250515_143009)
                date_str, time_str = folder.split('_')
                if len(date_str) == 8 and len(time_str) == 6:
                    dt = datetime.strptime(folder, "%Y%m%d_%H%M%S")
                    folders.append((folder, dt))
            except (ValueError, IndexError):
                continue
    
    if not folders:
        print("Error: 유효한 녹음 폴더가 없습니다.")
        return None
    
    # 날짜 기준으로 정렬하여 가장 최근 폴더 반환
    folders.sort(key=lambda x: x[1], reverse=True)
    return os.path.join(recordings_dir, folders[0][0])

def list_recording_folders():
    """recordings 폴더의 모든 녹음 폴더를 리스트로 반환합니다."""
    import os
    
    recordings_dir = "../recordings"
    if not os.path.exists(recordings_dir):
        print(f"Error: {recordings_dir} 폴더가 존재하지 않습니다.")
        return []
    
    folders = []
    for folder in os.listdir(recordings_dir):
        folder_path = os.path.join(recordings_dir, folder)
        if os.path.isdir(folder_path):
            try:
                # 폴더명이 날짜_시간 형식인지 확인 (예: 20250515_143009)
                date_str, time_str = folder.split('_')
                if len(date_str) == 8 and len(time_str) == 6:
                    folders.append(folder_path)
            except (ValueError, IndexError):
                continue
    
    return folders

if __name__ == "__main__":
    main() 