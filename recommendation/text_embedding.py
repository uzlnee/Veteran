
"""
텍스트 임베딩 서비스

Upstage AI를 활용하여 텍스트를 고차원 벡터로 변환합니다.
사용자 프로필과 일자리 공고를 같은 벡터 공간에 매핑하여 의미적 유사도 계산을 가능하게 합니다.

Classes:
    UpstageEmbeddingService: Upstage API를 사용한 텍스트 임베딩 클래스

Functions:
    get_embeddings: 텍스트를 임베딩 벡터로 변환
    _call_api_single: 단일 텍스트에 대한 API 호출
"""

import os
import requests
from typing import List, Union
from dotenv import load_dotenv

class UpstageEmbeddingService:
    """Upstage AI를 사용한 텍스트 임베딩 서비스 클래스"""
    
    def __init__(self):
        """Upstage API 키 설정 및 초기화"""
        load_dotenv()
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        self.api_url = "https://api.upstage.ai/v1/embeddings"

    def get_embeddings(self, texts: Union[str, List[str]], model_name: str = "embedding-passage") -> List[List[float]]:
        """
        텍스트를 임베딩 벡터로 변환
        
        Args:
            texts: 변환할 텍스트 (단일 문자열 또는 문자열 리스트)
            model_name: 사용할 모델 ("embedding-query" 또는 "embedding-passage")
            
        Returns:
            List[List[float]]: 임베딩 벡터 리스트
        """
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY가 설정되지 않았습니다.")

        # 단일 텍스트 처리
        if isinstance(texts, str):
            if not texts.strip():
                print(">> 빈 텍스트입니다.")
                return []
            
            return self._call_api_single(texts.strip()[:8000], model_name)
        
        # 다중 텍스트 처리
        valid_texts = [text.strip()[:8000] for text in texts if text and text.strip()]
        if not valid_texts:
            print(">> 유효한 텍스트가 없습니다.")
            return []
        
        # 각 텍스트를 개별적으로 처리
        all_embeddings = []
        for text in valid_texts:
            embedding = self._call_api_single(text, model_name)
            if embedding:
                all_embeddings.extend(embedding)
            else:
                return []
        
        return all_embeddings

    def _call_api_single(self, text: str, model_name: str) -> List[List[float]]:
        """
        단일 텍스트에 대한 Upstage API 호출
        
        Args:
            text: 임베딩할 텍스트
            model_name: 사용할 모델명
            
        Returns:
            List[List[float]]: 임베딩 벡터 (단일 원소 리스트)
        """
        # API 요청 헤더 설정
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 요청 데이터 구성
        data = {
            "input": text,
            "model": model_name
        }

        try:
            # API 호출
            response = requests.post(self.api_url, headers=headers, json=data)
            
            # 응답 상태 확인
            if response.status_code != 200:
                print(f">> API 응답 상태: {response.status_code}")
                print(f">> 응답 내용: {response.text}")
                return []
            
            result = response.json()
            
            # 임베딩 벡터 추출 및 반환
            if 'data' in result and result['data']:
                embedding = result['data'][0]['embedding']
                return [embedding]
            else:
                print(f">> 예상과 다른 응답 형식: {result}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Upstage API 요청 중 오류 발생: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"응답 내용: {e.response.text}")
            return []
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return []

if __name__ == '__main__':
    """테스트 코드"""
    embedding_service = UpstageEmbeddingService()
    
    # 단일 텍스트 임베딩 테스트
    text = "안녕하세요, 업스테이지 임베딩 테스트입니다."
    embedding = embedding_service.get_embeddings(text)
    if embedding:
        print(f"단일 텍스트 임베딩 벡터의 차원: {len(embedding[0])}")

    # 다중 텍스트 임베딩 테스트
    texts = ["첫 번째 문서입니다.", "이것은 두 번째 문서입니다."]
    embeddings = embedding_service.get_embeddings(texts)
    if embeddings:
        print(f"총 {len(embeddings)}개의 텍스트에 대한 임베딩을 받았습니다.")
        print(f"각 벡터의 차원: {len(embeddings[0])}")
