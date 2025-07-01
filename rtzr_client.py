import os
import requests
import json
import time
from dotenv import load_dotenv

class RTZRClient:
    """
    RTZR STT API 클라이언트
    JWT 토큰 인증과 sommers 모델을 사용한 STT
    """
    
    def __init__(self):
        load_dotenv() # 환경 변수 로드
        self.api_id = os.getenv("RTZR_API_ID")
        self.api_key = os.getenv("RTZR_API_KEY")
        self.base_url = "https://openapi.vito.ai/v1"
        self.access_token = None
        self.token_expires_at = None
        
        if not self.api_id or not self.api_key:
            raise ValueError("RTZR_API_ID와 RTZR_API_KEY가 .env 파일에 설정되어야 합니다.")
    
    def _get_access_token(self) -> str:
        """
        JWT 액세스 토큰을 획득합니다.
        토큰이 만료되었거나 없는 경우 새로 발급받습니다.
        """
        # 토큰이 유효한지 확인 (5분 여유)
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at - 300:
            return self.access_token
        
        # 새 토큰 요청
        auth_url = f"{self.base_url}/authenticate"
        payload = {
            "client_id": self.api_id,
            "client_secret": self.api_key
        }
        
        try:
            # application/x-www-form-urlencoded 형식으로 전송
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data["access_token"]
            # 토큰 만료 시간 설정 (일반적으로 1시간, 안전하게 50분으로 설정)
            self.token_expires_at = time.time() + 3000
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"RTZR 인증 실패: {str(e)}")
    
    def transcribe_file(self, audio_file_path: str, model_name: str = "sommers") -> str:
        """
        오디오 파일을 텍스트로 변환합니다.
        
        Args:
            audio_file_path: 변환할 오디오 파일 경로
            model_name: 사용할 모델 (기본값: sommers)
            
        Returns:
            변환된 텍스트
        """
        # 액세스 토큰 획득
        token = self._get_access_token()
        
        # 파일 존재 확인
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_file_path}")
        
        # STT 요청 시작
        transcribe_id = self._start_transcription(audio_file_path, token, model_name)
        
        # 결과 폴링
        result = self._poll_transcription_result(transcribe_id, token)
        
        return result
    
    def _start_transcription(self, audio_file_path: str, token: str, model_name: str) -> str:
        """
        음성 인식 작업을 시작하고 transcribe_id를 반환합니다.
        """
        transcribe_url = f"{self.base_url}/transcribe"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        config = {
            "model_name": model_name,
            "language": "ko"
        }
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': audio_file,
                    'config': (None, json.dumps(config))
                }
                
                response = requests.post(transcribe_url, headers=headers, files=files)
                response.raise_for_status()
                
                result = response.json()
                return result["id"]
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"음성 인식 요청 실패: {str(e)}")
    
    def _poll_transcription_result(self, transcribe_id: str, token: str, 
                                 max_wait_time: int = 300, poll_interval: int = 2) -> str:
        """
        음성 인식 결과를 폴링하여 완료될 때까지 대기하고 결과를 반환합니다.
        
        Args:
            transcribe_id: 음성 인식 작업 ID
            token: 액세스 토큰
            max_wait_time: 최대 대기 시간 (초)
            poll_interval: 폴링 간격 (초)
            
        Returns:
            인식된 텍스트
        """
        result_url = f"{self.base_url}/transcribe/{transcribe_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(result_url, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                
                if status == "completed":
                    # 결과에서 텍스트 추출
                    utterances = result.get("results", {}).get("utterances", [])
                    if utterances:
                        # 모든 발화를 하나의 텍스트로 결합
                        full_text = " ".join([utterance.get("msg", "") for utterance in utterances])
                        return full_text.strip()
                    else:
                        return ""
                
                elif status == "failed":
                    raise Exception(f"음성 인식 실패: {result.get('message', '알 수 없는 오류')}")
                
                elif status == "transcribing":
                    # 계속 대기
                    time.sleep(poll_interval)
                    continue
                
                else:
                    raise Exception(f"알 수 없는 상태: {status}")
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"결과 조회 실패: {str(e)}")
        
        raise Exception(f"음성 인식 시간 초과 ({max_wait_time}초)")