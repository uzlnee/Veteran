
"""
노인 구인정보 API를 이용해 현재 모집중인 공고만 수집하여 pkl로 저장
- 모집기간이 지나지 않은 공고만 수집
- 재실행 시 만료된 공고 자동 삭제
- 출력: ./data/job_openings.pkl

[전체 프로세스]
 1단계: 초기화 및 정리
  - API 키 로드, 데이터 폴더 생성
  - 기존 데이터에서 만료된 공고 제거

 2단계: 공고 ID 수집
  - 최신 공고부터 순차적으로 수집 (1페이지 = 50개)
  - 연속 3페이지 비어있으면 종료

 3단계: 모집중인 공고만 필터링
  - 상세 정보 조회하여 모집기간 확인
  - 현재 모집중인 공고만 저장

 4단계: 최종 저장
  - 기존 유효 데이터 + 신규 모집중 데이터 병합
  - job_openings.pkl로 저장
"""

import requests
import pickle
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from xml.etree import ElementTree
from dotenv import load_dotenv
import time
import asyncio
import aiohttp

class JobDataCollector:
    # 데이터 키 상수 정의
    JOB_KEYS = {
        'ID': 'job_id',
        'TITLE': '채용제목',
        'COMPANY': '사업장명',
        'ADDRESS': '주소',
        'METHOD': '접수방법',
        'START_DATE': '접수시작일',
        'END_DATE': '접수종료일',
        'AGE': '연령',
        'AGE_LIMIT': '연령제한',
        'RECRUIT_NUM': '모집인원',
        'MANAGER': '담당자',
        'CONTACT': '담당자연락처',
        'DETAILS': '상세내용',
        'ETC': '기타사항',
        'HOMEPAGE': '홈페이지',
        'CREATE_DATE': '생성일자',
        'UPDATE_DATE': '변경일자',
        'COLLECT_TIME': '수집일시'
    }
    def __init__(self):
        load_dotenv()
        self.elderly_job_api_key = os.getenv('ELDERLY_JOB_API_KEY')
        self.data_dir = "data"
        self.pkl_file = os.path.join(self.data_dir, "job_openings.pkl")
        self.meta_file = os.path.join(self.data_dir, "collection_meta.pkl")
        
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
    
    def is_recruitment_active(self, start_date: str, end_date: str) -> bool:
        """모집기간이 현재 유효한지 확인합니다."""
        if not start_date or not end_date:
            return False
        
        try:
            today = datetime.now().strftime("%Y%m%d")
            # YYYYMMDD 형식으로 비교
            return start_date <= today <= end_date
        except (ValueError, TypeError):
            return False
    
    def clean_expired_jobs(self, existing_openings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """기존 데이터에서 모집기간이 만료된 공고들을 제거합니다."""
        if not existing_openings:
            return []
        
        valid_openings = []
        expired_count = 0
        
        for opening in existing_openings:
            start_date = opening.get(self.JOB_KEYS['START_DATE'])
            end_date = opening.get(self.JOB_KEYS['END_DATE'])
            
            if self.is_recruitment_active(start_date, end_date):
                valid_openings.append(opening)
            else:
                expired_count += 1
        
        if expired_count > 0:
            print(f">>> 만료된 공고 {expired_count}개 제거됨")
        
        return valid_openings
        
    def collect_recent_job_ids(self, max_pages: int = 100) -> List[str]:
        """최근 공고 ID만 효율적으로 수집합니다."""
        if not self.elderly_job_api_key:
            print(">>> API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return []
            
        all_job_ids = []
        page_no = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3
        
        print(f"=== 최근 {max_pages}페이지 공고 ID 수집 시작 ===")
        
        while consecutive_empty_pages < max_consecutive_empty and page_no <= max_pages:
            try:
                list_url = "http://apis.data.go.kr/B552474/SenuriService/getJobList"
                list_params = {
                    "serviceKey": self.elderly_job_api_key,
                    "pageNo": str(page_no),
                    "numOfRows": "50",
                    "type": "xml"
                }
                
                print(f">>> {page_no}페이지 조회 중...", end=" ")
                list_response = requests.get(list_url, params=list_params, timeout=30)
                list_response.raise_for_status()
                
                # XML 파싱
                list_root = ElementTree.fromstring(list_response.content)
                
                # 에러 메시지 확인
                result_code = list_root.find(".//resultCode")
                if result_code is not None and result_code.text != "00":
                    if page_no == 1:
                        result_msg = list_root.find(".//resultMsg")
                        error_msg = result_msg.text if result_msg is not None else '알 수 없는 API 오류'
                        print(f"\n>>> API 오류: {error_msg}")
                        return []
                    else:
                        consecutive_empty_pages += 1
                        print(f"오류 (연속 빈 페이지: {consecutive_empty_pages})")
                        page_no += 1
                        continue
                
                # 현재 페이지의 채용공고ID 수집
                items = list_root.findall(".//item")
                page_job_ids = []
                
                for item in items:
                    job_id = item.find("jobId")
                    if job_id is not None:
                        page_job_ids.append(job_id.text)
                
                if not page_job_ids:
                    consecutive_empty_pages += 1
                    print(f"빈 페이지 (연속 빈 페이지: {consecutive_empty_pages})")
                else:
                    consecutive_empty_pages = 0
                    all_job_ids.extend(page_job_ids)
                    print(f"{len(page_job_ids)}개 ID 수집 (누적: {len(all_job_ids)}개)")
                
                page_no += 1
                time.sleep(0.05)
                
            except Exception as e:
                print(f"\n>>> {page_no}페이지 조회 중 오류: {e}")
                consecutive_empty_pages += 1
                page_no += 1
                continue
        
        if page_no > max_pages:
            print(f">>> 최대 페이지 수({max_pages}) 도달")
        
        print(f"\n=== ID 수집 완료: 총 {len(all_job_ids)}개 ===")
        return all_job_ids
    
    async def fetch_job_detail_async(self, session: aiohttp.ClientSession, job_id: str) -> Dict[str, Any]:
        """비동기적으로 단일 채용공고 상세 정보를 가져옵니다."""
        detail_url = "http://apis.data.go.kr/B552474/SenuriService/getJobInfo"
        detail_params = {
            "serviceKey": self.elderly_job_api_key,
            "type": "xml",
            "id": job_id
        }
        
        try:
            async with session.get(detail_url, params=detail_params, timeout=10) as response:
                response.raise_for_status()
                content = await response.read()
                
                # XML 파싱
                detail_root = ElementTree.fromstring(content)
                
                # 상세 정보 파싱
                item = detail_root.find(".//item")
                if item is not None and self._validate_job_data(item):
                    # 모집기간 추출
                    start_date = item.find("frAcptDd").text if item.find("frAcptDd") is not None else ""
                    end_date = item.find("toAcptDd").text if item.find("toAcptDd") is not None else ""
                    
                    # 현재 모집중인 공고만 반환
                    if self.is_recruitment_active(start_date, end_date):
                        return {
                            self.JOB_KEYS['ID']: job_id,
                            self.JOB_KEYS['TITLE']: item.find("wantedTitle").text if item.find("wantedTitle") is not None else "-",
                            self.JOB_KEYS['COMPANY']: item.find("plbizNm").text if item.find("plbizNm") is not None else "-",
                            self.JOB_KEYS['ADDRESS']: item.find("plDetAddr").text if item.find("plDetAddr") is not None else "-",
                            self.JOB_KEYS['METHOD']: item.find("acptMthdCd").text if item.find("acptMthdCd") is not None else "-",
                            self.JOB_KEYS['START_DATE']: start_date,
                            self.JOB_KEYS['END_DATE']: end_date,
                            self.JOB_KEYS['AGE']: item.find("age").text if item.find("age") is not None else "-",
                            self.JOB_KEYS['AGE_LIMIT']: item.find("ageLim").text if item.find("ageLim") is not None else "-",
                            self.JOB_KEYS['RECRUIT_NUM']: item.find("clltPrnnum").text if item.find("clltPrnnum") is not None else "-",
                            self.JOB_KEYS['MANAGER']: item.find("clerk").text if item.find("clerk") is not None else "-",
                            self.JOB_KEYS['CONTACT']: item.find("clerkContt").text if item.find("clerkContt") is not None else "-",
                            self.JOB_KEYS['DETAILS']: item.find("detCnts").text if item.find("detCnts") is not None else "-",
                            self.JOB_KEYS['ETC']: item.find("etcItm").text if item.find("etcItm") is not None else "-",
                            self.JOB_KEYS['HOMEPAGE']: item.find("homepage").text if item.find("homepage") is not None else "-",
                            self.JOB_KEYS['CREATE_DATE']: item.find("createDy").text if item.find("createDy") is not None else "-",
                            self.JOB_KEYS['UPDATE_DATE']: item.find("updDy").text if item.find("updDy") is not None else "-",
                            self.JOB_KEYS['COLLECT_TIME']: datetime.now().isoformat()
                        }
                return None
        except Exception:
            return None

    async def collect_job_details_batch(self, job_ids: List[str], batch_size: int = 50, early_stop_threshold: int = 100) -> List[Dict[str, Any]]:
        """배치 단위로 비동기적으로 현재 모집중인 채용공고만 수집합니다. (조기 종료 지원)"""
        print(f"\n=== 모집중인 공고 수집 시작: {len(job_ids)}개 공고 확인 ===")
        print(f">>> 배치 크기: {batch_size}, 조기 종료 임계값: {early_stop_threshold}")
        
        active_openings = []
        expired_count = 0
        failed_count = 0
        consecutive_expired = 0
        
        # 커넥션 제한 설정
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100, ttl_dns_cache=300, use_dns_cache=True)
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 배치 단위로 처리
            for i in range(0, len(job_ids), batch_size):
                batch = job_ids[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(job_ids) + batch_size - 1) // batch_size
                
                print(f">>> 배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개)")
                
                # 배치 병렬 처리
                tasks = [self.fetch_job_detail_async(session, job_id) for job_id in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 배치 내 결과 분석
                batch_active_count = 0
                batch_expired_count = 0
                batch_failed_count = 0
                
                # 결과 처리
                for result in results:
                    if isinstance(result, dict) and result is not None:
                        active_openings.append(result)
                        batch_active_count += 1
                    elif result is None:
                        expired_count += 1
                        batch_expired_count += 1
                    else:
                        failed_count += 1
                        batch_failed_count += 1
                
                # 연속 만료 카운터 업데이트 (활성 공고가 있으면 리셋)
                if batch_active_count > 0:
                    consecutive_expired = 0
                else:
                    # 배치 전체가 만료/실패인 경우만 카운터 증가
                    consecutive_expired += len(batch)
                
                # 진행상황 출력
                print(f"    모집중: {len(active_openings)}개, 만료: {expired_count}개, 실패: {failed_count}개")
                
                # 조기 종료 조건 확인
                if consecutive_expired >= early_stop_threshold:
                    print(f">>> 연속 {consecutive_expired}개 공고가 만료됨. 조기 종료합니다.")
                    print(f">>> 남은 {len(job_ids) - i - batch_size}개 공고 스킵")
                    break
                
                # 배치 간 간격 조절
                if i + batch_size < len(job_ids):
                    await asyncio.sleep(0.1)
        
        print(f"\n=== 모집중인 공고 수집 완료 ===")
        print(f">>> 현재 모집중: {len(active_openings)}개")
        print(f">>> 모집 만료: {expired_count}개")  
        print(f">>> API 실패: {failed_count}개")
        
        return active_openings

    def collect_job_details(self, job_ids: List[str]) -> List[Dict[str, Any]]:
        """채용공고 ID 목록으로부터 상세 정보를 수집합니다. (효율적 수집)"""
        if not job_ids:
            return []
        
        # 적응적 파라미터 설정
        if len(job_ids) > 1000:
            batch_size = 30  # 대량 데이터시 작은 배치
            early_stop = 200  # 조기 종료 임계값 증가
        else:
            batch_size = 50  # 일반적인 배치 크기
            early_stop = 300 # 조기 종료 임계값 증가
        
        # 비동기 함수 실행
        return asyncio.run(self.collect_job_details_batch(job_ids, batch_size, early_stop))
    
    def save_data(self, openings: List[Dict[str, Any]]):
        """수집된 데이터를 pkl 파일로 저장합니다."""
        if not openings:
            print(">>> 저장할 데이터가 없습니다.")
            return
            
        try:
            # 메인 데이터 저장
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(openings, f)
            
            # 메타데이터 저장
            meta_data = {
                "collection_time": datetime.now().isoformat(),
                "total_count": len(openings),
                "file_path": self.pkl_file
            }
            
            with open(self.meta_file, 'wb') as f:
                pickle.dump(meta_data, f)
            
            print(f">>> 데이터 저장 완료:")
            print(f"    - 파일: {self.pkl_file}")
            print(f"    - 공고 수: {len(openings)}개")
            print(f"    - 수집 시간: {meta_data['collection_time']}")
            
        except Exception as e:
            print(f">>> 데이터 저장 중 오류: {e}")
    
    def load_existing_data(self) -> Tuple[List[Dict[str, Any]], dict]:
        """기존 pkl 파일에서 데이터를 로드합니다."""
        openings = []
        meta_data = {}
        
        try:
            if os.path.exists(self.pkl_file):
                with open(self.pkl_file, 'rb') as f:
                    openings = pickle.load(f)
            
            if os.path.exists(self.meta_file):
                with open(self.meta_file, 'rb') as f:
                    meta_data = pickle.load(f)
                    
        except Exception as e:
            print(f">>> 기존 데이터 로드 중 오류: {e}")
        
        return openings, meta_data
    
    def _validate_job_data(self, item) -> bool:
        """필수 데이터 필드가 있는지 검증합니다."""
        required_fields = ["wantedTitle", "plbizNm"]
        for field in required_fields:
            element = item.find(field)
            if element is None or not element.text or element.text.strip() in ["-", ""]:
                return False
        return True
    
    
    def run_collection(self):
        """모집중인 공고만 수집하는 프로세스를 실행합니다."""
        print("=" * 60)
        print("        현재 모집중인 공고 수집 시작")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # 1단계: 기존 데이터 로드 및 만료된 공고 제거
        existing_openings, existing_meta = self.load_existing_data()
        if existing_openings:
            print(f">>> 기존 데이터: {len(existing_openings)}개 공고")
            print(f">>> 수집 시간: {existing_meta.get('collection_time', '알 수 없음')}")
            
            # 만료된 공고 제거
            valid_existing = self.clean_expired_jobs(existing_openings)
            print(f">>> 유효한 기존 공고: {len(valid_existing)}개")
        else:
            valid_existing = []
            print(">>> 기존 데이터 없음")
        
        # 2단계: 최근 공고 ID 수집 (효율성을 위해 최근 100페이지만)
        job_ids = self.collect_recent_job_ids(max_pages=100)
        if not job_ids:
            print(">>> 공고 ID 수집 실패.")
            if valid_existing:
                print(">>> 기존 유효 데이터만 저장합니다.")
                self.save_data(valid_existing)
            return
        
        # 3단계: 신규 공고 중 모집중인 것만 수집
        existing_ids = {opening.get(self.JOB_KEYS['ID']) for opening in valid_existing if opening.get(self.JOB_KEYS['ID'])}
        new_job_ids = [job_id for job_id in job_ids if job_id not in existing_ids]
        
        if new_job_ids:
            print(f">>> 신규 공고 {len(new_job_ids)}개 확인 중...")
            new_active_openings = self.collect_job_details(new_job_ids)
        else:
            new_active_openings = []
            print(">>> 신규 공고 없음")
        
        # 4단계: 유효한 기존 데이터 + 신규 모집중 데이터 병합
        all_active_openings = valid_existing + new_active_openings
        
        if all_active_openings:
            self.save_data(all_active_openings)
        else:
            print(">>> 저장할 유효한 공고가 없습니다.")
        
        # 완료 보고
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("        모집중인 공고 수집 완료")
        print("=" * 60)
        print(f">>> 현재 모집중 공고: {len(all_active_openings)}개")
        print(f">>> 신규 모집중 공고: {len(new_active_openings)}개")
        print(f">>> 소요 시간: {duration}")
        print(f">>> 저장 위치: {self.pkl_file}")
        print("=" * 60)

def main():
    """메인 실행 함수"""
    collector = JobDataCollector()
    collector.run_collection()

if __name__ == "__main__":
    main()
