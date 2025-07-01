"""
수집된 일자리 공고 데이터를 필터링하고 거리 계산을 수행하는 서비스
- job_crawler.py에서 생성된 job_openings.pkl 파일을 로드하여 사용
- 출력: 사용자 조건에 맞는 필터링된 공고 리스트 (거리 정보 포함)

[전체 프로세스]
 1단계: 데이터 로드
  - job_openings.pkl에서 전체 공고 데이터 로드
  - 메타데이터 확인 (수집 시간, 총 개수)

 2단계: 조건별 필터링
  - 희망 분야(preferred_field) 기반 키워드 매칭
  - 지역(location) 기반 주소 필터링
  - 유효한 공고만 선별 (필수 정보 누락 제외)

 3단계: 거리 계산
  - 카카오 지도 API를 이용한 좌표 변환
  - 사용자 위치와 각 사업장 간의 직선 거리 계산
  - 거리 정보를 공고 데이터에 추가

 4단계: 최종 공고 리스트 반환
  - 필터링 + 거리 정보가 포함된 공고 데이터
  - job_recommender.py에서 AI 매칭에 사용
"""

import requests
import math
import re
import pickle
from typing import List, Dict, Any, Optional, Tuple
from xml.etree import ElementTree
from dotenv import load_dotenv
import os
from datetime import datetime

class JobOpeningService:
    @staticmethod
    def parse_distance(distance_str: str) -> float:
        """거리 문자열을 float로 안전하게 변환합니다."""
        try:
            if isinstance(distance_str, (int, float)):
                return float(distance_str)
            if isinstance(distance_str, str):
                # 'km' 제거하고 숫자만 추출
                cleaned = distance_str.replace('km', '').strip()
                return float(cleaned)
            return 999.0  # 기본값
        except (ValueError, AttributeError):
            return 999.0
    
    def __init__(self):
        load_dotenv()
        self.elderly_job_api_key = os.getenv('ELDERLY_JOB_API_KEY')
        self.kakao_api_key = os.getenv('KAKAO_API_KEY')
        
        # pkl 파일 경로 설정 (절대 경로 기준)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, "data")
        self.pkl_file = os.path.join(self.data_dir, "job_openings.pkl")
        self.meta_file = os.path.join(self.data_dir, "collection_meta.pkl")
        
        # 좌표 캐시 (메모리 캐싱)
        self._coords_cache = {}
        self._max_cache_size = 1000

    def _get_coords_from_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Kakao Maps API를 사용하여 주소를 좌표로 변환합니다. (캐싱, 폴백 로직 적용)"""
        if not address or not self.kakao_api_key:
            return None
        
        # 캐시 확인
        if address in self._coords_cache:
            return self._coords_cache[address]
        
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
        params = {"query": address}


        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("documents"):
                coords = data["documents"][0]
                result = (float(coords['y']), float(coords['x']))
                
                # 성공한 경우에만 캐시 저장
                if len(self._coords_cache) < self._max_cache_size:
                    self._coords_cache[address] = result
                return result
            
            # [폴백 로직] 초기 검색 실패 시, 지역명 뒤에 '청'을 붙여 재시도
            elif address.endswith(('구', '시', '군')) and not address.endswith('청'):
                fallback_address = address + '청'
                print(f"[알림] '{address}' 검색 실패. '{fallback_address}'(으)로 재시도합니다.")
                params["query"] = fallback_address
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("documents"):
                    coords = data["documents"][0]
                    result = (float(coords['y']), float(coords['x']))
                    
                    # 성공한 경우에만 캐시 저장
                    if len(self._coords_cache) < self._max_cache_size:
                        self._coords_cache[address] = result
                    return result

            # 최종 실패 시 None 반환 (캐시 저장 안 함)
            return None

        except Exception as e:
            print(f"주소 좌표 변환 중 오류 발생: {e}")
            return None

    def _calculate_haversine_distance(self, lat1, lon1, lat2, lon2) -> float:
        """하버사인 공식을 이용해 두 좌표 간의 거리를 km 단위로 계산합니다."""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance

    def sort_by_distance(self, user_address: str, job_openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """사용자 주소와 구인 정보 주소의 좌표를 기반으로 거리를 계산하고 정렬합니다."""
        if not job_openings:
            return []

        user_coords = self._get_coords_from_address(user_address)
        if not user_coords:
            print("사용자 주소의 좌표를 찾을 수 없어 거리순 정렬을 건너뜁니다.")
            return job_openings

        openings_with_dist = []
        for job in job_openings:
            job_address = job.get("주소", "")
            # 주소 앞의 5자리 우편번호와 공백 제거 (예: "12345 서울시...")
            cleaned_address = re.sub(r"^\d{5}\s+", "", job_address)
            
            job_coords = self._get_coords_from_address(cleaned_address)
            
            if job_coords:
                distance = self._calculate_haversine_distance(
                    user_coords[0], user_coords[1],
                    job_coords[0], job_coords[1]
                )
                job["거리"] = f"{distance:.2f}km"
            else:
                job["거리"] = "999km" # 좌표 변환 실패 시
            
            openings_with_dist.append(job)
            
        # 거리(숫자 부분)를 기준으로 오름차순 정렬
        sorted_openings = sorted(
            openings_with_dist, 
            key=lambda x: self.parse_distance(x.get("거리", "999"))
        )
        
        return sorted_openings

    def calculate_distance(self, user_address: str, job_address: str) -> float:
        """사용자 주소와 특정 공고 간의 거리를 계산합니다."""
        user_coords = self._get_coords_from_address(user_address)
        if not user_coords:
            return None
            
        # 주소에서 도로명 주소 부분만 추출
        match = re.match(r"^\d{5}\s+([^,]+)", job_address)
        if match:
            cleaned_address = match.group(1)
        else:
            cleaned_address = re.sub(r"^\d{5}\s+", "", job_address)
        
        job_coords = self._get_coords_from_address(cleaned_address)
        if not job_coords:
            return None
            
        distance = self._calculate_haversine_distance(
            user_coords[0], user_coords[1],
            job_coords[0], job_coords[1]
        )
        
        return distance

    def _filter_by_region(self, openings: List[Dict[str, Any]], target_region: str) -> List[Dict[str, Any]]:
        """지역 기반으로 공고를 필터링합니다. (완화된 필터링)"""
        if not target_region:
            return openings
        
        filtered = []
        # 지역 정보를 단계적으로 추출하여 부분 일치 허용
        region_parts = []
        
        # 시/도 추출
        target_city = target_region.split()[0].replace("특별시", "").replace("광역시", "").replace("도", "")
        region_parts.append(target_city)
        
        # 구/군 추출 (있는 경우)
        region_tokens = target_region.split()
        if len(region_tokens) > 1:
            district = region_tokens[1].replace("구", "").replace("군", "")
            region_parts.append(district)
        
        for opening in openings:
            address = opening.get("주소", "")
            # 지역 부분 중 하나라도 매칭되면 포함
            if any(part in address for part in region_parts if part):
                filtered.append(opening)
        
        return filtered
    
    def _prepare_openings_for_recommendation(self, openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """추천 시스템을 위해 공고 데이터를 준비 (하드코딩된 키워드 없이)"""
        if not openings:
            return openings
        
        # 모든 공고를 그대로 반환 (의미적 매칭은 job_recommender에서 임베딩으로 처리)
        prepared_openings = []
        for opening in openings:
            opening_copy = opening.copy()
            # 하드코딩된 키워드 점수 제거, 임베딩만 사용
            prepared_openings.append(opening_copy)
        
        return prepared_openings

    def load_job_openings_from_pkl(self) -> List[Dict[str, Any]]:
        """pkl 파일에서 일자리 공고 데이터를 로드합니다."""
        try:
            if not os.path.exists(self.pkl_file):
                print(">>> pkl 파일이 존재하지 않습니다. job_crawler.py를 먼저 실행해주세요.")
                return []
            
            # 메타데이터 확인
            if os.path.exists(self.meta_file):
                with open(self.meta_file, 'rb') as f:
                    meta_data = pickle.load(f)
                    collection_time = meta_data.get('collection_time', '알 수 없음')
                    total_count = meta_data.get('total_count', 0)
                    print(f">>> 저장된 데이터 로드: {total_count}개 공고")
                    print(f">>> 수집 시간: {collection_time}")
            
            # 실제 데이터 로드
            with open(self.pkl_file, 'rb') as f:
                openings = pickle.load(f)
            
            print(f">>> pkl 파일에서 {len(openings)}개 공고 로드 완료")
            # 데이터 검증 후 유효한 공고만 반환
            valid_openings = [job for job in openings if self._validate_job_opening(job)]
            invalid_count = len(openings) - len(valid_openings)
            if invalid_count > 0:
                print(f">>> 유효하지 않은 공고 {invalid_count}개 제외됨")
            
            return valid_openings
            
        except Exception as e:
            print(f">>> pkl 파일 로드 중 오류: {e}")
            return []
    
    def _validate_job_opening(self, job: Dict[str, Any]) -> bool:
        """공고 데이터가 유효한지 검증합니다."""
        required_fields = ['job_id', '채용제목', '사업장명', '접수시작일', '접수종료일']
        for field in required_fields:
            if not job.get(field) or job.get(field).strip() in ["-", ""]:
                return False
        return True

    def get_job_openings(self, job_title: str = "", region: str = "") -> List[Dict[str, Any]]:
        """pkl 파일에서 일자리 공고 데이터를 로드합니다. (기존 API 호출 방식 대체)"""
        return self.load_job_openings_from_pkl()
    

    def get_filtered_job_openings(self, preferred_fields: List[str], region: str) -> List[Dict[str, Any]]:
        """전체 공고를 검색한 후 지역과 키워드로 필터링합니다."""
        # 1. 전체 공고 검색
        all_openings = self.get_job_openings()
        
        if not all_openings:
            return []
        
        print(f">>> 총 {len(all_openings)}개 공고 검색 완료, 필터링 시작...")
        
        # 2. 지역별 필터링
        region_filtered = self._filter_by_region(all_openings, region)
        
        # 3. 추천을 위한 공고 데이터 준비 (임베딩 매칭은 job_recommender에서 처리)
        prepared_openings = self._prepare_openings_for_recommendation(region_filtered)
        
        return prepared_openings