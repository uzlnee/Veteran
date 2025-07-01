"""
AI 기반 일자리 추천 엔진

임베딩 벡터와 거리 정보를 활용하여 사용자에게 최적화된 일자리를 추천합니다.
프로필 적합도와 거리를 종합하여 점수를 계산하고, AI가 추천 이유를 생성합니다.

Classes:
    JobRecommender: 일자리 추천을 수행하는 메인 클래스

Functions:
    get_recommendations: 사용자에게 맞춤형 일자리 추천 생성
    _calculate_profile_similarity: 사용자와 공고 간 프로필 유사도 계산
    _calculate_distance_score: 거리 기반 점수 계산
"""

import numpy as np
from typing import List, Dict, Any
from text_embedding import UpstageEmbeddingService
from job_filter import JobOpeningService
from ai_explainer import GeminiService

class JobRecommender:
    """일자리 추천 시스템의 메인 클래스"""
    
    def __init__(self):
        """추천 시스템에 필요한 서비스들을 초기화"""
        self.embedding_service = UpstageEmbeddingService()
        self.job_filter = JobOpeningService()
        self.ai_explainer = GeminiService()

    def _calculate_profile_similarity(self, user_vector: List[float], job_vectors: List[List[float]]) -> List[float]:
        """
        사용자 프로필과 공고 간 코사인 유사도 계산
        
        Args:
            user_vector: 사용자 프로필 임베딩 벡터
            job_vectors: 공고들의 임베딩 벡터 리스트
            
        Returns:
            List[float]: 각 공고와의 유사도 점수 리스트
        """
        user_vec = np.array(user_vector)
        job_vecs = np.array(job_vectors)
        
        # 코사인 유사도 계산
        dot_product = np.dot(job_vecs, user_vec)
        user_norm = np.linalg.norm(user_vec)
        job_norms = np.linalg.norm(job_vecs, axis=1)
        
        similarity = dot_product / (user_norm * job_norms)
        return similarity.tolist()

    def _calculate_distance_score(self, distances: List[float]) -> List[float]:
        """
        거리를 점수로 변환 (가까울수록 높은 점수)
        
        Args:
            distances: 거리 리스트 (km 단위)
            
        Returns:
            List[float]: 0~1 사이의 거리 점수 리스트
        """
        scores = []
        max_dist = 30.0  # 최대 거리 30km
        
        for dist in distances:
            if dist <= 1.0:  # 1km 이내는 만점
                score = 1.0
            elif dist > max_dist:  # 30km 초과는 0점
                score = 0.0
            else:
                # 선형적으로 점수 감소
                score = 1.0 - ((dist - 1.0) / (max_dist - 1.0))
            scores.append(score)
        return scores

    def get_recommendations(self, user, job_openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        사용자에게 맞춤형 일자리 추천 생성
        
        Args:
            user: 사용자 정보 객체
            job_openings: 필터링된 공고 리스트
            
        Returns:
            List[Dict[str, Any]]: 추천 이유가 포함된 상위 10개 추천 공고
        """
        if not job_openings:
            return []
        
        # 사용자 프로필 텍스트 생성
        user_profile_text = (
            f"희망 직종: {', '.join(user.preferred_field)}. "
            f"보유 경력: {user.career}. "
            f"보유 자격증: {', '.join(user.license) if user.license else '없음'}. "
            f"건강 상태: {user.health_condition}. "
            f"학력: {user.education}."
        )
        
        # 공고 텍스트 생성
        job_texts = [
            f"채용 제목: {job.get('채용제목', '')}. 상세 내용: {job.get('상세내용', '')}"
            for job in job_openings
        ]

        # 임베딩 벡터 생성
        try:
            user_vector = self.embedding_service.get_embeddings(user_profile_text, model_name="embedding-query")[0]
            job_vectors = self.embedding_service.get_embeddings(job_texts, model_name="embedding-passage")
        except Exception as e:
            print(f">> 임베딩 생성 중 오류 발생: {e}")
            return self.job_filter.sort_by_distance(user.location, job_openings)[:5]

        if not user_vector or not job_vectors:
            print(">> 임베딩 벡터를 가져오지 못했습니다.")
            return self.job_filter.sort_by_distance(user.location, job_openings)[:5]

        # 프로필 유사도 계산
        profile_scores = self._calculate_profile_similarity(user_vector, job_vectors)

        # 거리 정보 추가 및 거리 점수 계산
        job_openings_with_dist = []
        for job in job_openings:
            job_with_dist = job.copy()
            distance = self.job_filter.calculate_distance(user.location, job.get('주소', ''))
            job_with_dist['거리'] = f"{distance:.2f}km" if distance is not None else "999km"
            job_openings_with_dist.append(job_with_dist)
        
        distances = [self.job_filter.parse_distance(job.get('거리', '999')) for job in job_openings_with_dist]
        distance_scores = self._calculate_distance_score(distances)

        # 통합 점수 계산 (프로필 60% + 거리 40%)
        combined_scores = []
        for i, job in enumerate(job_openings_with_dist):
            score = (profile_scores[i] * 0.6) + (distance_scores[i] * 0.4)
            job['score'] = score
            combined_scores.append(job)

        # 점수순 정렬 및 상위 10개 선별
        ranked_jobs = sorted(combined_scores, key=lambda x: x['score'], reverse=True)
        top_10_jobs = ranked_jobs[:10]
        
        # AI 추천 이유 생성을 위한 프롬프트 구성
        prompt = f"""
        당신은 노인 채용 전문 컨설턴트입니다. 아래 구직자의 프로필과, 시스템이 1차적으로 추천한 구인 공고 목록을 검토해주세요.
        각 공고에 대해, 구직자의 프로필과 공고 내용을 근거로 하여 구직자가 이해하기 쉬운 **설득력 있는 추천 이유**를 각각 생성해주세요.

        [구직자 프로필]
        - 희망 지역: {user.location}
        - 희망 분야: {', '.join(user.preferred_field)}
        - 나이: {user.age}세
        - 보유 자격증: {', '.join(user.license) if user.license else '없음'}
        - 건강 상태: {user.health_condition}
        - 경력 사항: {user.career}
        - 학력: {user.education}

        [추천할 구인 공고 목록]
        {[{
            "index": i, 
            "title": opening.get('채용제목', '-'), 
            "company": opening.get('사업장명', '-'),
            "tasks": opening.get('상세내용', '-')
        } for i, opening in enumerate(top_10_jobs)]}

        [요청]
        아래 JSON 형식에 맞춰, 각 공고("index" 기준)에 대한 추천 이유("reason")를 작성해주세요.
        
        {{
            "recommendation_reasons": [
                {{
                    "index": 0,
                    "reason": "여기에 0번 공고를 추천하는 구체적인 이유를 작성합니다."
                }},
                {{
                    "index": 1,
                    "reason": "여기에 1번 공고를 추천하는 구체적인 이유를 작성합니다."
                }}
            ]
        }}
        """
        
        # AI로 추천 이유 생성 및 추가
        try:
            response = self.ai_explainer.generate_recommendation_reasons(prompt)
            reasons = response.get("recommendation_reasons", [])
            
            for reason_item in reasons:
                index = reason_item.get("index")
                if index is not None and index < len(top_10_jobs):
                    top_10_jobs[index]['reason'] = reason_item.get("reason", "AI 추천")

        except Exception as e:
            print(f">> 추천 사유 생성 중 오류 발생: {e}")
            for job in top_10_jobs:
                job['reason'] = "AI가 추천하는 맞춤 일자리입니다."

        return top_10_jobs