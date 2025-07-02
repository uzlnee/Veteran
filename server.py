"""
Twilio 음성 통화 서버 - 고령자 구직 상담 시스템
FastAPI 기반으로 Twilio webhook을 처리하고 대화 플로우를 관리합니다.
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from twilio.twiml.voice_response import VoiceResponse
import os
import uvicorn
import asyncio
from dotenv import load_dotenv

from conversation_logic import conversation_logic
from client import TwilioClient

load_dotenv()
app = FastAPI()

# 전역 상태 관리
active_conversations = {}  # Call SID별 대화 로직 인스턴스 저장
active_calls_text_queue = {}  # Call SID별 TTS 메시지 큐
active_calls_recording_url = {}  # Call SID별 녹음 URL 정보


class SayTextRequest(BaseModel):
    """TTS 요청을 위한 데이터 모델"""
    call_sid: str
    text: str


class ListenRequest(BaseModel):
    """음성 녹음 요청을 위한 데이터 모델"""
    call_sid: str


async def start_logic_for_call(call_sid: str):
    """대화 로직을 시작하는 백그라운드 태스크"""
    print(f"[{call_sid}] [대화 시작] Logic 실행")
    if call_sid in active_conversations:
        logic_instance = active_conversations[call_sid]["logic_instance"]
        await logic_instance.run()
    else:
        print(f"[{call_sid}] ERROR: No conversation logic instance found.")


async def process_call_say_queue(call_sid: str):
    """텍스트 큐를 처리하고 TwiML 응답을 생성"""
    response = VoiceResponse()

    # 큐에서 다음 명령어 처리
    if call_sid in active_calls_text_queue and active_calls_text_queue[call_sid]:
        instruction = active_calls_text_queue[call_sid].pop(0)

        # 녹음 시작 명령어 처리
        if instruction == "__START_RECORDING__":
            print(f"[{call_sid}] Processing '__START_RECORDING__' instruction.")

            server_url = os.environ.get("SERVER_URL")
            if not server_url:
                print(
                    "ERROR: SERVER_URL environment variable is not set for Record action."
                )
                response.hangup()
                twiml_response_str = str(response)
                return Response(content=twiml_response_str, media_type="text/xml")

            record_callback_url = f"{server_url}/recording-callback"
            response.record(
                action=record_callback_url,
                maxLength=20,
                finishOnKey="#",
                trim="trim-silence",
                playBeep=True,
            )

        # 일반 TTS 메시지 처리
        else:
            print(f"[{call_sid}] Dequeuing and saying: '{instruction}'")
            response.say(instruction, voice="alice", language="ko-KR")

            server_url = os.environ.get("SERVER_URL")
            if not server_url:
                print(
                    "ERROR: SERVER_URL environment variable is not set. Hanging up call."
                )
                response.hangup()
                twiml_response_str = str(response)
                return Response(content=twiml_response_str, media_type="text/xml")

            response.redirect(f"{server_url}/voice")

    else:
        print(
            f"[{call_sid}] Text queue is empty and no pending recording instruction. Playing a pause."
        )
        response.pause(length=10)

        server_url = os.environ.get("SERVER_URL")
        if not server_url:
            print("ERROR: SERVER_URL environment variable is not set. Hanging up call.")
            response.hangup()
            twiml_response_str = str(response)
            return Response(content=twiml_response_str, media_type="text/xml")

        response.redirect(f"{server_url}/voice")

    twiml_response_str = str(response)

    if call_sid in active_conversations:
        active_conversations[call_sid]["voice_event"].set()
    else:
        print(
            f"[{call_sid}] WARNING: Call SID not in active_conversations when setting voice event."
        )

    return Response(content=twiml_response_str, media_type="text/xml")


@app.post("/voice")
async def handle_voice_call(request: Request, background_tasks: BackgroundTasks):
    """Twilio 음성 통화 webhook 처리"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")

    if not call_sid:
        print("Error: CallSid not found in request.")
        return str(VoiceResponse().hangup())

    print(f"Received Twilio webhook for Call SID: {call_sid}")

    # 새로운 통화인 경우 대화 로직 초기화
    if call_sid not in active_conversations:
        voice_event = asyncio.Event()
        recording_event = asyncio.Event()

        # Twilio 클라이언트 인스턴스 생성
        client_instance = TwilioClient(
            server_base_url=os.environ.get("SERVER_URL"),
            voice_event=voice_event,
            recording_event=recording_event,
        )

        # 대화 로직 인스턴스 생성
        logic_instance = conversation_logic(
            call_sid=call_sid, client_instance=client_instance
        )

        active_conversations[call_sid] = {
            "logic_instance": logic_instance,
            "voice_event": voice_event,
            "recording_event": recording_event,
        }
        active_conversations[call_sid]["logic_instance"].compose_workflow()
        print(
            f"[{call_sid}] New conversation logic instance created and workflow composed."
        )

        background_tasks.add_task(start_logic_for_call, call_sid)
    else:
        active_conversations[call_sid]["voice_event"].set()

    return await process_call_say_queue(call_sid)


@app.post("/say-text")
async def receive_say_text(request_data: SayTextRequest):
    """TTS 텍스트를 큐에 추가"""
    call_sid = request_data.call_sid
    text = request_data.text

    if call_sid not in active_calls_text_queue:
        active_calls_text_queue[call_sid] = []
        print(f"[{call_sid}] New call SID registered for text queue.")

    active_calls_text_queue[call_sid].append(text)
    print(f"[{call_sid}] Enqueued text: '{text}'")
    return {"status": "success", "message": "Text enqueued"}


@app.post("/listen-to-user")
async def listen_to_user(request_data: ListenRequest):
    """사용자 음성 녹음 시작"""
    call_sid = request_data.call_sid

    active_calls_recording_url[call_sid] = {"status": "pending"}

    if call_sid not in active_calls_text_queue:
        active_calls_text_queue[call_sid] = []

    active_calls_text_queue[call_sid].insert(0, "__START_RECORDING__")

    print(
        f"[{call_sid}] Recording request received. Added '__START_RECORDING__' to text queue."
    )
    return {"status": "success", "message": "Recording initiated"}


@app.post("/recording-callback")
async def handle_recording_callback(request: Request):
    """Twilio 녹음 완료 콜백 처리"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    recording_duration = form_data.get("RecordingDuration")

    if not all([call_sid, recording_url, recording_duration]):
        print(
            f"Error: Missing data in recording callback for Call SID: {call_sid}. Data: {form_data}"
        )
        raise HTTPException(status_code=400, detail="Missing recording data")

    print(
        f"[{call_sid}] Recording completed! URL: {recording_url}, Duration: {recording_duration}s"
    )

    active_calls_recording_url[call_sid] = {
        "status": "ready",
        "recording_url": recording_url,
        "duration": recording_duration,
    }

    if call_sid in active_conversations:
        active_conversations[call_sid]["recording_event"].set()

    response = VoiceResponse()
    server_url = os.environ.get("SERVER_URL")
    if not server_url:
        print(
            "ERROR: SERVER_URL environment variable is not set for post-recording redirect."
        )
        response.hangup()
    else:
        response.redirect(f"{server_url}/voice")

    twiml_response_str = str(response)
    return Response(content=twiml_response_str, media_type="text/xml")


@app.get("/get-recording-url/{call_sid}")
async def get_recording_url(call_sid: str):
    """녹음 URL 조회"""
    recording_info = active_calls_recording_url.get(call_sid)

    if recording_info:
        if recording_info["status"] == "ready":
            return {"status": "ready", "recording_url": recording_info["recording_url"]}
        elif recording_info["status"] == "pending":
            return {"status": "processing", "message": "Recording still pending."}

    return {
        "status": "not_found",
        "message": "No recording found or initiated for this Call SID.",
    }


@app.post("/status")
async def handle_call_status(request: Request):
    """통화 상태 변경 webhook 처리"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")

    print(f"Call SID: {call_sid}, Status: {call_status}")

    if call_status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in active_calls_text_queue:
            del active_calls_text_queue[call_sid]
            print(f"[{call_sid}] Call ended. Cleaned up text queue.")
        if call_sid in active_calls_recording_url:
            del active_calls_recording_url[call_sid]
            print(f"[{call_sid}] Call ended. Cleaned up recording URL.")
        if call_sid in active_conversations:
            del active_conversations[call_sid]
            print(
                f"[{call_sid}] Call ended. Cleaned up conversation logic instance and events."
            )

    return ""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
