from dataclasses import dataclass
from typing import List
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
    print_recommendation_results(test_user, recommended_jobs, job_openings)

if __name__ == "__main__":
    main() 