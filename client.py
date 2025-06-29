import httpx
import os
import asyncio
import time
from dotenv import load_dotenv # .env 파일 로드를 위해 추가

load_dotenv() # 환경 변수 로드

class TwilioClient:
    def __init__(self, server_base_url: str, voice_event: asyncio.Event, recording_event: asyncio.Event):
        self.server_base_url = server_base_url
        self.http_client = httpx.AsyncClient()
        self.voice_event = voice_event
        self.recording_event = recording_event
        
        # Twilio 인증 정보 로드
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not self.TWILIO_ACCOUNT_SID or not self.TWILIO_AUTH_TOKEN:
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env for downloading recordings.")
            
        # 녹음 파일 저장 디렉토리 생성 (없으면 생성)
        self.RECORDINGS_DIR = "recordings"
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
        print(f"Recordings will be saved to: {os.path.abspath(self.RECORDINGS_DIR)}")

    async def _wait_for_voice_event(self, call_sid: str):
        self.voice_event.clear() 
        print(f"[{call_sid}] Waiting for voice event (cleared).")
        await self.voice_event.wait() 
        print(f"[{call_sid}] Voice event received (waited).")

    async def say(self, call_sid: str, text: str) -> bool:
        try:
            url = f"{self.server_base_url}/say-text"
            payload = {'call_sid': call_sid, 'text': text}
            response = await self.http_client.post(url, json=payload) 
            response.raise_for_status() 
            print(f"Successfully sent 'say' request to server for Call SID {call_sid}: '{text}'")
            
            await self._wait_for_voice_event(call_sid) 
            
            return True
        except httpx.RequestError as e:
            print(f"Error sending 'say' request to server: {e}")
            return False

    # listen 메서드에 phase 인자를 추가합니다.
    async def listen(self, call_sid: str, phase: int) -> str | None:
        try:
            print(f"[{call_sid}] Requesting server to start listening for user input (Phase: {phase}).")
            url = f"{self.server_base_url}/listen-to-user"
            payload = {'call_sid': call_sid}
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get('status') != 'success':
                print(f"[{call_sid}] Server failed to initiate listen: {response_data.get('message')}")
                return None
            
            self.recording_event.clear() 
            print(f"[{call_sid}] Waiting for recording event (cleared).")
            await self.recording_event.wait() 
            print(f"[{call_sid}] Recording event received (waited).")

            print(f"[{call_sid}] Waiting for recording URL to be available...")
            timeout = 30
            start_time = time.time()
            
            recording_url = None
            while time.time() - start_time < timeout:
                get_url = f"{self.server_base_url}/get-recording-url/{call_sid}"
                recording_response = await self.http_client.get(get_url)
                recording_response.raise_for_status()
                recording_data = recording_response.json()
                
                if recording_data.get('status') == 'ready' and recording_data.get('recording_url'):
                    recording_url = recording_data['recording_url']
                    print(f"[{call_sid}] Twilio Recording URL received: {recording_url}")
                    break
                elif recording_data.get('status') == 'processing':
                    print(f"[{call_sid}] Recording still processing, waiting...")
                
                await asyncio.sleep(1)
            
            if not recording_url:
                print(f"[{call_sid}] Listen operation timed out. No recording URL received from Twilio.")
                return None

            # --- Twilio 녹음 URL을 로컬 파일로 다운로드하는 새로운 로직 ---
            # recordings/{call_sid}/{phase}.wav 형식으로 경로를 생성합니다.
            call_recording_dir = os.path.join(self.RECORDINGS_DIR, call_sid)
            local_wav_path = os.path.join(call_recording_dir, f"{phase}.wav")
            
            # 해당 call_sid에 대한 디렉토리가 없으면 생성합니다.
            # os.makedirs는 중간 디렉토리가 없어도 한 번에 생성해줍니다.
            os.makedirs(call_recording_dir, exist_ok=True) 
            
            print(f"[{call_sid}] Attempting to download recording to: {local_wav_path}")
            try:
                # Twilio Basic 인증을 위한 헤더 설정
                auth = httpx.BasicAuth(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
                
                async with httpx.AsyncClient() as client: # 새 클라이언트 인스턴스를 사용하여 요청
                    response = await client.get(recording_url, auth=auth, follow_redirects=True)
                    response.raise_for_status() # HTTP 오류 발생 시 예외 발생

                    with open(local_wav_path, 'wb') as f:
                        f.write(response.content)
                print(f"[{call_sid}] Recording successfully downloaded to {local_wav_path}")
                return local_wav_path # 로컬 파일 경로 반환
            except httpx.RequestError as e:
                print(f"[{call_sid}] Error downloading recording to local file: {e}")
                if os.path.exists(local_wav_path): # 실패 시 부분 다운로드된 파일 제거
                    os.remove(local_wav_path)
                return None
            # -----------------------------------------------------------

        except httpx.RequestError as e:
            print(f"Error in listen request to server: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in listen: {e}")
            return None
    async def hangup(self, call_sid: str) -> bool:
        """
        Twilio REST API를 사용하여 통화를 종료합니다.
        """
        try:
            twilio_api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.TWILIO_ACCOUNT_SID}/Calls/{call_sid}.json"
            auth = httpx.BasicAuth(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
            
            payload = {"Status": "completed"} # 통화 상태를 'completed'로 설정하여 종료
            
            print(f"[{call_sid}] Attempting to hang up call...")
            async with self.http_client as client:
                response = await client.post(twilio_api_url, auth=auth, data=payload)
                response.raise_for_status() 
            
            print(f"[{call_sid}] Call successfully hung up.")
            return True
        except httpx.RequestError as e:
            print(f"[{call_sid}] Error hanging up call via Twilio API: {e}")
            return False
        except Exception as e:
            print(f"[{call_sid}] An unexpected error occurred during hangup: {e}")
            return False
