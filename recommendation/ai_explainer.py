"""
AI 기반 추천 이유 생성 서비스

Google Gemini AI를 활용하여 추천된 일자리에 대한 개인화된 설명을 생성합니다.
사용자의 프로필과 공고 정보를 분석하여 왜 해당 일자리가 적합한지 설명합니다.

Classes:
    GeminiService: Gemini AI API를 사용한 추천 이유 생성 클래스

Functions:
    generate_recommendation_reasons: 추천 이유 생성
    generate_fitness_scores_and_reasons: 적합도 점수와 추천 이유 함께 생성
"""

import google.generativeai as genai
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

class GeminiService:
    """Gemini AI를 사용한 추천 이유 생성 서비스 클래스"""
    
    def __init__(self):
        """Gemini API 초기화 및 모델 설정"""
        load_dotenv()
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_recommendation_reasons(self, prompt: str) -> Dict[str, str]:
        """
        추천 이유 생성
        
        Args:
            prompt: 사용자 정보와 공고 정보가 포함된 프롬프트
            
        Returns:
            Dict[str, str]: 추천 이유가 포함된 딕셔너리
        """
        try:
            # Gemini AI로 추천 이유 생성
            response = self.model.generate_content(prompt)
            
            # JSON 형식 응답에서 내용 추출
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            # JSON 파싱 및 반환
            try:
                recommendations = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                print("LLM 응답이 JSON 형식이 아닙니다. 기본 추천 이유를 사용합니다.")
                recommendations = {}
            
            return recommendations
            
        except Exception as e:
            print(f"LLM 추천 이유 생성 중 오류 발생: {e}")
            return {}

    def generate_fitness_scores_and_reasons(self, prompt: str) -> Dict[str, Any]:
        """
        적합도 점수와 추천 이유 함께 생성
        
        Args:
            prompt: 사용자 정보와 공고 정보가 포함된 프롬프트
            
        Returns:
            Dict[str, Any]: 적합도 점수와 추천 이유가 포함된 딕셔너리
        """
        try:
            # Gemini AI로 적합도 평가 및 추천 이유 생성
            response = self.model.generate_content(prompt)
            
            # JSON 형식 응답에서 내용 추출
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            # JSON 파싱 및 반환
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                print("LLM 응답이 JSON 형식이 아닙니다. 기본값을 사용합니다.")
                result = {}
            
            return result
            
        except Exception as e:
            print(f"LLM 적합도 평가 중 오류 발생: {e}")
            return {}

 