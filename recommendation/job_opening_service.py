import requests
from typing import List, Dict, Any
from xml.etree import ElementTree
from gemini_service import GeminiService
from dotenv import load_dotenv
import os

class JobOpeningService:
    # 고용형태 코드 상수 정의
    EMPLOYMENT_TYPE = {
        "TIME": "CM0103"  # 시간제일자리
    }
    
    # 접수방법 코드 상수 정의
    APPLICATION_METHOD = {
        "ONLINE": "CM0801",  # 온라인
        "EMAIL": "CM0802",   # 이메일
        "FAX": "CM0803",     # 팩스
        "VISIT": "CM0804"    # 방문
    }
    
    def __init__(self):
        load_dotenv()
        self.elderly_job_api_key = os.getenv('ELDERLY_JOB_API_KEY')
        self.gemini_service = GeminiService()

    def sort_by_distance(self, user_address: str, job_openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gemini를 사용하여 사용자 주소와 가까운 순으로 구인 정보를 정렬합니다."""
        if not job_openings:
            return []

        # Gemini에게 거리 정렬을 요청하는 프롬프트
        prompt = f"""
사용자 주소: {user_address}

각 구인 정보에 대해 사용자 주소와의 거리(km)를 계산하세요.
다음 구인 정보 목록을 사용자 주소와의 거리가 가까운 순으로 정렬해주세요.

구인 정보 목록:
{[{"사업장명": job["사업장명"], "주소": job["주소"]} for job in job_openings]}

JSON 형식으로 응답해주세요:
{{
    "sorted_jobs": [
        {{
            "index": 원본 리스트에서의 인덱스,
            "distance": 거리(km)
        }}
    ]
}}
"""
        try:
            # Gemini API 호출
            response = self.gemini_service.get_distance_based_sorting(prompt)
            
            # 정렬된 결과에 따라 구인 정보 재정렬
            sorted_openings = []
            for item in response["sorted_jobs"]:
                index = item["index"]
                distance = item["distance"]
                job = job_openings[index].copy()
                job["거리"] = f"{distance}km"
                sorted_openings.append(job)
            
            return sorted_openings
        except Exception as e:
            print(f"거리 기반 정렬 중 오류 발생: {str(e)}")
            return job_openings

    def get_job_openings(self, job_title: str, region: str) -> List[Dict[str, Any]]:
        """노인 구인정보 API를 통해 구인 정보를 가져옵니다."""
        try:
            # 먼저 구인 목록을 가져와서 채용공고ID를 수집
            list_url = "http://apis.data.go.kr/B552474/SenuriService/getJobList"
            list_params = {
                "serviceKey": self.elderly_job_api_key,
                "pageNo": "1",
                "numOfRows": "5",  # 5개로 제한
                "type": "xml",
                "jobcls": job_title,  # 직종 코드
                "workPlc": region,    # 근무지 코드
                "emplymShp": self.EMPLOYMENT_TYPE["TIME"]  # 시간제일자리
            }
            
            list_response = requests.get(list_url, params=list_params)
            list_response.raise_for_status()
            
            # XML 파싱
            list_root = ElementTree.fromstring(list_response.content)
            
            # 에러 메시지 확인
            result_code = list_root.find(".//resultCode")
            if result_code is not None and result_code.text != "00":
                error_message = list_root.find(".//resultMsg").text
                print(f"노인 구인정보 목록 API 에러: {error_message}")
                return []
            
            # 채용공고ID 수집
            job_ids = []
            for item in list_root.findall(".//item"):
                job_id = item.find("jobId")
                if job_id is not None:
                    job_ids.append(job_id.text)
            
            if not job_ids:
                print("검색된 구인 정보가 없습니다.")
                return []
            
            # 각 채용공고ID에 대해 상세 정보 조회
            openings = []
            for job_id in job_ids:
                detail_url = "http://apis.data.go.kr/B552474/SenuriService/getJobInfo"
                detail_params = {
                    "serviceKey": self.elderly_job_api_key,
                    "type": "xml",
                    "id": job_id
                }
                
                detail_response = requests.get(detail_url, params=detail_params)
                detail_response.raise_for_status()
                
                # XML 파싱
                detail_root = ElementTree.fromstring(detail_response.content)
                
                # 상세 정보 파싱
                item = detail_root.find(".//item")
                if item is not None:
                    opening = {
                        "채용제목": item.find("wantedTitle").text if item.find("wantedTitle") is not None else "-",
                        "사업장명": item.find("plbizNm").text if item.find("plbizNm") is not None else "-",
                        "주소": item.find("plDetAddr").text if item.find("plDetAddr") is not None else "-",
                        "접수방법": item.find("acptMthdCd").text if item.find("acptMthdCd") is not None else "-",
                        "접수기간": f"{item.find('frAcptDd').text} ~ {item.find('toAcptDd').text}" if item.find('frAcptDd') is not None and item.find('toAcptDd') is not None else "-",
                        "연령": item.find("age").text if item.find("age") is not None else "-",
                        "연령제한": item.find("ageLim").text if item.find("ageLim") is not None else "-",
                        "모집인원": item.find("clltPrnnum").text if item.find("clltPrnnum") is not None else "-",
                        "담당자": item.find("clerk").text if item.find("clerk") is not None else "-",
                        "담당자연락처": item.find("clerkContt").text if item.find("clerkContt") is not None else "-",
                        "상세내용": item.find("detCnts").text if item.find("detCnts") is not None else "-",
                        "기타사항": item.find("etcItm").text if item.find("etcItm") is not None else "-",
                        "홈페이지": item.find("homepage").text if item.find("homepage") is not None else "-",
                        "생성일자": item.find("createDy").text if item.find("createDy") is not None else "-",
                        "변경일자": item.find("updDy").text if item.find("updDy") is not None else "-"
                    }
                    openings.append(opening)
            
            return openings
            
        except Exception as e:
            print(f"구인 정보 조회 중 오류 발생: {str(e)}")
            return [] 