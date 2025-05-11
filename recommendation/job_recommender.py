import requests
from typing import List, Dict, Any
from xml.etree import ElementTree
from gemini_service import GeminiService
from dotenv import load_dotenv
import os

class JobRecommender:
    def __init__(self):
        load_dotenv()
        self.work24_api_key = os.getenv('WORK24_API_KEY')
        self.gemini_service = GeminiService()
    
    def get_recommended_jobs(self, user) -> List[Dict[str, Any]]:
        """직업 정보 API를 통해 적합한 직업을 추천합니다."""
        # Work24 API 호출
        job_info_url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212L01.do"
        params = {
            "authKey": self.work24_api_key,
            "returnType": "XML",
            "target": "JOBCD"  # 직업분류코드 기준 검색
        }
        
        try:
            response = requests.get(job_info_url, params=params)
            response.raise_for_status()
            
            # XML 응답을 파싱
            root = ElementTree.fromstring(response.text)
            
            # 에러 메시지 확인
            message_element = root.find("message")
            if message_element is not None:
                error_message = message_element.text
                print(f"Work24 API 에러: {error_message}")
                return []
            
            # 직업 정보 파싱
            available_jobs = []
            for job in root.findall(".//jobList"):
                job_info = {
                    "position": job.find("jobNm").text if job.find("jobNm") is not None else "",
                    "job_code": job.find("jobCd").text if job.find("jobCd") is not None else "",
                    "category_code": job.find("jobClcd").text if job.find("jobClcd") is not None else "",
                    "category_name": job.find("jobClcdNM").text if job.find("jobClcdNM") is not None else ""
                }
                available_jobs.append(job_info)
            
            if not available_jobs:
                print("Work24 API: 검색된 직업 정보가 없습니다.")
                return []
            
            print(f"전체 직업 수: {len(available_jobs)}")
            
            # 사용자의 희망 분야와 매칭되는 직업 찾기
            suitable_jobs = []
            for job in available_jobs:
                job_name = job["position"].lower()
                category_name = job["category_name"].lower()
                
                for field in user.preferred_field:
                    field = field.lower()
                    if field in job_name or field in category_name:
                        suitable_jobs.append(job)
                        break
            
            print(f"희망 분야 매칭 직업 수: {len(suitable_jobs)}")
            
            if not suitable_jobs:
                print("희망 분야와 매칭되는 직업을 찾을 수 없어 전체 직업에서 추천합니다.")
                suitable_jobs = available_jobs
            
            # 상위 10개만 선택하여 LLM 추천
            suitable_jobs = suitable_jobs[:10]
            
            # 각 직업의 상세 정보 가져오기
            for job in suitable_jobs:
                details = self.get_job_details(job["job_code"])
                job.update(details)
            
            # LLM을 사용하여 직업 추천
            prompt = f"""
            고령 구직자 정보:
            나이: {user.age}세
            보유 자격증: {', '.join(user.license)}
            희망 분야: {', '.join(user.preferred_field)}
            건강 상태: {user.health_condition}
            학력: {user.education}
            경력 사항: {user.career}

            가능한 직업 목록:
            {[{
                "직업명": job["position"],
                "직업 분류": job["category_name"],
                "요약": job["summary"],
                "되는 길": job["way"]
            } for job in suitable_jobs]}

            위 구직자에게 가장 적합한 직업 5개를 추천해주세요.
            추천 시 다음의 사항을 고려해주세요.
            1. 구직자의 희망 직종에 부합하는지
            2. 구직자의 나이와 건강 상태에 적합한지
            3. 구직자의 학력, 경력, 자격 사항이 해당 직업의 '되는 길'에 부합하는지

            JSON 형식으로 응답:
            {{
                "recommendations": [
                    {{
                        "job_title": "직업명",
                        "reason": "추천 이유 (50자 이내)"
                    }}
                ]
            }}
            """
            
            recommendations = self.gemini_service.get_recommendations(prompt, suitable_jobs)
            
            # 추천된 직업 정보와 원본 직업 정보 결합
            recommended_jobs = []
            for rec in recommendations["recommendations"]:
                for job in suitable_jobs:
                    if job["position"] == rec["job_title"]:
                        job.update(rec)
                        recommended_jobs.append(job)
                        break
            
            return recommended_jobs
            
        except Exception as e:
            print(f"직업 추천 중 오류 발생: {e}")
            return []

    def get_job_details(self, job_code: str) -> Dict[str, str]:
        """직업 상세 정보를 가져옵니다."""
        try:
            # 요약 및 되는 길 정보
            url1 = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212D01.do"
            params1 = {
                "authKey": self.work24_api_key,
                "returnType": "XML",
                "target": "JOBDTL",
                "jobGb": "1",
                "jobCd": job_code,
                "dtlGb": "1"
            }
            
            # 수행 업무 정보
            url2 = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212D01.do"
            params2 = {
                "authKey": self.work24_api_key,
                "returnType": "XML",
                "target": "JOBDTL",
                "jobGb": "1",
                "jobCd": job_code,
                "dtlGb": "2"
            }
            
            # 요약 및 되는 길 정보 요청
            response1 = requests.get(url1, params=params1)
            response1.raise_for_status()
            root1 = ElementTree.fromstring(response1.text)
            
            # 수행 업무 정보 요청
            response2 = requests.get(url2, params=params2)
            response2.raise_for_status()
            root2 = ElementTree.fromstring(response2.text)
            
            # 정보 추출
            details = {
                "summary": root1.find(".//jobSum").text if root1.find(".//jobSum") is not None else "-",
                "way": root1.find(".//way").text if root1.find(".//way") is not None else "-",
                "tasks": root2.find(".//execJob").text if root2.find(".//execJob") is not None else "-"
            }
            
            return details
        except Exception as e:
            print(f"직업 상세 정보 조회 중 오류 발생: {e}")
            return {
                "summary": "-",
                "way": "-",
                "tasks": "-"
            } 