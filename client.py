"""
Twilio API 클라이언트 - 음성 통화 및 녹음 관리
TTS, STT, 파일 다운로드를 처리합니다.
"""

import httpx
import os
import asyncio
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()


class TwilioClient:
    """Twilio API와 상호작용하는 클라이언트"""
    
    def __init__(
        self,
        server_base_url: str,
        voice_event: asyncio.Event,
        recording_event: asyncio.Event,
    ):
        self.server_base_url = server_base_url
        self.http_client = httpx.AsyncClient()
        self.voice_event = voice_event  # TTS 완료 이벤트
        self.recording_event = recording_event  # 녹음 완료 이벤트

        # Twilio 인증 정보 로드
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

        if not self.TWILIO_ACCOUNT_SID or not self.TWILIO_AUTH_TOKEN:
            raise ValueError(
                "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env for downloading recordings."
            )

        # 녹음 파일 저장 디렉토리 생성 (없으면 생성)
        self.RECORDINGS_DIR = "recordings"
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
        print(f"Recordings will be saved to: {os.path.abspath(self.RECORDINGS_DIR)}")

        # (한국 시간) YYYYMMDD_HHMMSS 디렉토리 생성
        kst = timezone(timedelta(hours=9))
        self.session_timestamp = datetime.now(kst).strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.RECORDINGS_DIR, self.session_timestamp)
        os.makedirs(self.session_dir, exist_ok=True)

    async def _wait_for_voice_event(self, call_sid: str):
        """음성 이벤트 대기"""
        self.voice_event.clear()
        await self.voice_event.wait()

    async def say(self, call_sid: str, text: str) -> bool:
        """TTS를 통해 텍스트를 음성으로 출력"""
        try:
            url = f"{self.server_base_url}/say-text"
            payload = {"call_sid": call_sid, "text": text}
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()

            await self._wait_for_voice_event(call_sid)

            return True
        except httpx.RequestError as e:
            print(f"Error sending 'say' request to server: {e}")
            return False

    async def listen(self, call_sid: str, phase: int) -> str | None:
        """사용자 음성을 녹음하고 파일로 다운로드"""
        try:
            print(
                f"[{call_sid}] Requesting server to start listening for user input (Phase: {phase})."
            )
            url = f"{self.server_base_url}/listen-to-user"
            payload = {"call_sid": call_sid}
            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()

            response_data = response.json()
            if response_data.get("status") != "success":
                print(
                    f"[{call_sid}] Server failed to initiate listen: {response_data.get('message')}"
                )
                return None

            self.recording_event.clear()
            await self.recording_event.wait()

            print(f"[{call_sid}] Waiting for recording URL to be available...")
            timeout = 30
            start_time = time.time()

            # Twilio에서 녹음 URL이 준비될 때까지 폴링
            recording_url = None
            while time.time() - start_time < timeout:
                get_url = f"{self.server_base_url}/get-recording-url/{call_sid}"
                recording_response = await self.http_client.get(get_url)
                recording_response.raise_for_status()
                recording_data = recording_response.json()

                if recording_data.get("status") == "ready" and recording_data.get(
                    "recording_url"
                ):
                    recording_url = recording_data["recording_url"]
                    print(f"[{call_sid}] Recording URL received")
                    break
                elif recording_data.get("status") == "processing":
                    print(f"[{call_sid}] Recording still processing, waiting...")

                await asyncio.sleep(0.5)

            if not recording_url:
                print(
                    f"[{call_sid}] Listen operation timed out. No recording URL received from Twilio."
                )
                return None

            local_wav_path = os.path.join(self.session_dir, f"USER_{phase+1:04d}.wav")

            print(f"[{call_sid}] Attempting to download recording to: {local_wav_path}")
            try:
                download_task = asyncio.create_task(
                    self._download_recording_file(
                        recording_url, local_wav_path, call_sid
                    )
                )
                success = await download_task
                if success:
                    print(
                        f"[{call_sid}] Recording successfully downloaded to {local_wav_path}"
                    )
                    return local_wav_path
                else:
                    return None

            except Exception as e:
                print(f"[{call_sid}] Unexpected error during download: {e}")
                if os.path.exists(local_wav_path):
                    os.remove(local_wav_path)
                return None
        except httpx.RequestError as e:
            print(f"Error in listen request to server: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in listen: {e}")
            return None

    async def _download_recording_file(
        self, recording_url: str, local_path: str, call_sid: str
    ) -> bool:
        """
        Twilio 녹음 파일을 비동기적으로 다운로드하는 헬퍼 메서드
        """
        try:
            # Twilio Basic 인증을 위한 헤더 설정
            auth = httpx.BasicAuth(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0), limits=httpx.Limits(max_connections=10)
            ) as client:
                response = await client.get(
                    recording_url, auth=auth, follow_redirects=True
                )
                response.raise_for_status()

                with open(local_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)

                return True

        except httpx.RequestError as e:
            print(f"[{call_sid}] Network error downloading recording: {e}")
            return False
        except httpx.HTTPStatusError as e:
            print(
                f"[{call_sid}] HTTP error downloading recording: {e.response.status_code}"
            )
            return False
        except Exception as e:
            print(f"[{call_sid}] Unexpected error downloading recording: {e}")
            return False

    async def hangup(self, call_sid: str) -> bool:
        """
        Twilio REST API를 사용하여 통화를 종료합니다.
        """
        try:
            twilio_api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.TWILIO_ACCOUNT_SID}/Calls/{call_sid}.json"
            auth = httpx.BasicAuth(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)

            payload = {"Status": "completed"}

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
