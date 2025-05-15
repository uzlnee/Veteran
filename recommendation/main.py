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
    # 테스트용 사용자 정보
    test_user = ElderlyUser(
        name="김영수",
        age=68,
        location="경기도 수원시 팔달구 권광로 367번길 11",
        available_time="오전 근무만 가능",
        license=["요양보호사 자격증", "공인중개사"],
        preferred_field=["요양", "청소", "시설관리"],
        health_condition="허리 디스크로 무거운 물건은 불가",
        career="수원시청 시설관리직 15년, 대한부동산 공인중개사 10년",
        education="고등학교 졸업"
    )
    
    # 직업 추천 서비스 초기화
    job_recommender = JobRecommender()
    
    # 직업 추천
    recommended_jobs = job_recommender.get_recommended_jobs(test_user)
    if not recommended_jobs:
        print("추천할 수 있는 직업이 없습니다.")
        return
    
    # 구인 정보 서비스 초기화
    job_opening_service = JobOpeningService()
    
    # 모든 추천 직업에 대한 구인 정보 조회
    job_openings = job_opening_service.get_job_openings(recommended_jobs[0].get('job_code'), test_user.location)
    
    # 콘솔에 출력
    print_recommendation_results(test_user, recommended_jobs, job_openings)
    
    # JSON 형식으로 변환 및 저장
    json_output = generate_json_output(test_user, recommended_jobs, job_openings)
    save_json_output(json_output)

if __name__ == "__main__":
    main() 