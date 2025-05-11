import google.generativeai as genai
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

class GeminiService:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Gemini API 설정
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def get_recommendations(self, prompt: str, suitable_jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
        """Gemini API를 사용하여 직업 추천을 받습니다."""
        try:
            response = self.model.generate_content(prompt)
            print("LLM 응답:", response.text)  # 응답 내용 확인
            
            # JSON 부분만 추출
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            try:
                recommendations = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                print("LLM 응답이 JSON 형식이 아닙니다. 기본 추천을 진행합니다.")
                recommendations = {
                    "recommendations": [
                        {
                            "job_title": job["position"],
                            "reason": f"{job['position']} 직업이 구직자의 희망 분야와 일치합니다."
                        }
                        for job in suitable_jobs[:5]  # 상위 5개 직업만 선택
                    ]
                }
            
            return recommendations
            
        except Exception as e:
            print(f"LLM 추천 중 오류 발생: {e}")
            return {
                "recommendations": [
                    {
                        "job_title": job["position"],
                        "reason": f"{job['position']} 직업이 구직자의 희망 분야와 일치합니다."
                    }
                    for job in suitable_jobs[:5]  # 상위 5개 직업만 선택
                ]
            }

    def get_distance_based_sorting(self, prompt: str) -> Dict[str, List[Dict[str, Any]]]:
        """Gemini API를 사용하여 거리 기반 정렬 결과를 받습니다."""
        try:
            response = self.model.generate_content(prompt)
            
            # JSON 부분만 추출
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            try:
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                # 기본 정렬 순서 반환
                return {
                    "sorted_jobs": [
                        {"index": i, "distance": 0}
                        for i in range(5)  # 기본적으로 원래 순서 유지
                    ]
                }
                
        except Exception as e:
            print(f"거리 기반 정렬 중 오류 발생: {e}")
            return {
                "sorted_jobs": [
                    {"index": i, "distance": 0}
                    for i in range(5)  # 기본적으로 원래 순서 유지
                ]
            } 