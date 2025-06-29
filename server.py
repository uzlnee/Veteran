from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from twilio.twiml.voice_response import VoiceResponse, Say, Record 
import os
import uvicorn
import asyncio
from dotenv import load_dotenv

# TwilioClient와 conversation_logic을 임포트합니다.
# 순환 참조를 피하기 위해 conversation_logic은 이 파일 뒤에 정의되므로
# 실제 실행 시에는 이 임포트가 정상적으로 동작하도록 파일 구조에 유의해야 합니다.
# (예: conversation_logic을 별도의 파일로 분리하고 client.py도 마찬가지로 분리)
from conversation_logic import conversation_logic
from client import TwilioClient

load_dotenv()
app = FastAPI()

# 전역 변수: 각 Call SID에 대한 conversation_logic 인스턴스와 Event 객체를 저장할 딕셔너리
active_conversations = {} 

active_calls_text_queue = {}
active_calls_recording_url = {} 

class SayTextRequest(BaseModel):
    call_sid: str
    text: str

class ListenRequest(BaseModel):
    call_sid: str

# start_logic 함수를 수정하여 해당 call_sid의 logic 인스턴스를 사용하도록 합니다.
async def start_logic_for_call(call_sid: str):
    print(f"[{call_sid}] [대화 시작] Logic 실행")
    if call_sid in active_conversations:
        logic_instance = active_conversations[call_sid]['logic_instance']
        await logic_instance.run()
    else:
        print(f"[{call_sid}] ERROR: No conversation logic instance found.")


# 텍스트 큐를 확인하고 TwiML을 반환하는 함수
async def process_call_say_queue(call_sid: str):
    response = VoiceResponse()
    
    if call_sid in active_calls_text_queue and active_calls_text_queue[call_sid]:
        instruction = active_calls_text_queue[call_sid].pop(0)
        
        if instruction == '__START_RECORDING__':
            print(f"[{call_sid}] Processing '__START_RECORDING__' instruction.")
            
            server_url = os.environ.get("SERVER_URL")
            if not server_url:
                print("ERROR: SERVER_URL environment variable is not set for Record action.")
                response.hangup()
                twiml_response_str = str(response)
                return Response(content=twiml_response_str, media_type="text/xml")
            
            record_callback_url = f"{server_url}/recording-callback"
            response.record(
                action=record_callback_url,
                maxLength=20, 
                finishOnKey='#', 
                trim='trim-silence',
                playBeep=True
            )
            
        else: # 일반 텍스트 메시지
            print(f"[{call_sid}] Dequeuing and saying: '{instruction}'")
            response.say(instruction, voice='alice', language='ko-KR')
            
            server_url = os.environ.get("SERVER_URL")
            if not server_url:
                print("ERROR: SERVER_URL environment variable is not set. Hanging up call.")
                response.hangup()
                twiml_response_str = str(response)
                return Response(content=twiml_response_str, media_type="text/xml")
            
            response.redirect(f"{server_url}/voice")

    else:
        print(f"[{call_sid}] Text queue is empty and no pending recording instruction. Playing a pause.")
        response.pause(length=10) 
        
        server_url = os.environ.get("SERVER_URL")
        if not server_url:
            print("ERROR: SERVER_URL environment variable is not set. Hanging up call.")
            response.hangup()
            twiml_response_str = str(response)
            return Response(content=twiml_response_str, media_type="text/xml")
        
        response.redirect(f"{server_url}/voice")
    
    twiml_response_str = str(response)
    print(f"DEBUG: Final TwiML response: {twiml_response_str}")

    # TwiML 응답을 보낸 직후, 해당 통화의 voice_event를 set()하여
    # conversation_logic의 대기를 해제합니다.
    if call_sid in active_conversations:
        active_conversations[call_sid]['voice_event'].set()
        print(f"[{call_sid}] Voice event set after TwiML response.")
    else:
        print(f"[{call_sid}] WARNING: Call SID not in active_conversations when setting voice event.")

    return Response(content=twiml_response_str, media_type="text/xml")

@app.post("/voice")
async def handle_voice_call(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.form()
    call_sid = form_data.get('CallSid')
    
    if not call_sid:
        print("Error: CallSid not found in request.")
        return str(VoiceResponse().hangup())

    print(f"Received Twilio webhook for Call SID: {call_sid}")
    
    if call_sid not in active_conversations:
        # TwilioClient에 Event 객체들을 주입합니다.
        voice_event = asyncio.Event()
        recording_event = asyncio.Event()
        
        client_instance = TwilioClient(
            server_base_url=os.environ.get("SERVER_URL"),
            voice_event=voice_event,
            recording_event=recording_event
        )
        
        logic_instance = conversation_logic(
            call_sid=call_sid,
            client_instance=client_instance # conversation_logic에 TwilioClient 인스턴스 주입
        )

        active_conversations[call_sid] = {
            'logic_instance': logic_instance,
            'voice_event': voice_event,
            'recording_event': recording_event
        }
        active_conversations[call_sid]['logic_instance'].compose_workflow() 
        print(f"[{call_sid}] New conversation logic instance created and workflow composed.")
        
        # 첫 번째 /voice 요청 시에만 대화 로직 시작 (백그라운드 태스크)
        background_tasks.add_task(start_logic_for_call, call_sid)
    else:
        # 기존 통화의 경우, voice_event를 set()하여 대기 중인 conversation_logic이 진행되도록 합니다.
        # (client.py의 _wait_for_voice_event에서 clear()를 했기 때문)
        active_conversations[call_sid]['voice_event'].set()
        print(f"[{call_sid}] Existing conversation. Setting voice event.")
        
    return await process_call_say_queue(call_sid)

@app.post("/say-text")
async def receive_say_text(request_data: SayTextRequest):
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
    call_sid = request_data.call_sid
    
    active_calls_recording_url[call_sid] = {'status': 'pending'}
    
    if call_sid not in active_calls_text_queue:
        active_calls_text_queue[call_sid] = []
    
    active_calls_text_queue[call_sid].insert(0, '__START_RECORDING__') 
    
    print(f"[{call_sid}] Recording request received. Added '__START_RECORDING__' to text queue.")
    return {"status": "success", "message": "Recording initiated"}

@app.post("/recording-callback")
async def handle_recording_callback(request: Request):
    form_data = await request.form()
    call_sid = form_data.get('CallSid')
    recording_url = form_data.get('RecordingUrl')
    recording_duration = form_data.get('RecordingDuration')
    
    if not all([call_sid, recording_url, recording_duration]):
        print(f"Error: Missing data in recording callback for Call SID: {call_sid}. Data: {form_data}")
        raise HTTPException(status_code=400, detail="Missing recording data")

    print(f"[{call_sid}] Recording completed! URL: {recording_url}, Duration: {recording_duration}s")
    
    active_calls_recording_url[call_sid] = {
        'status': 'ready', 
        'recording_url': recording_url, 
        'duration': recording_duration
    }
    
    if call_sid in active_conversations:
        # 녹음 완료 시 녹음 이벤트를 설정하여 conversation_logic이 진행되도록 합니다.
        print(f"[{call_sid}] Recording callback received. Setting recording event.")
        active_conversations[call_sid]['recording_event'].set()
        
    response = VoiceResponse()
    server_url = os.environ.get("SERVER_URL")
    if not server_url:
        print("ERROR: SERVER_URL environment variable is not set for post-recording redirect.")
        response.hangup()
    else:
        response.redirect(f"{server_url}/voice")
    
    twiml_response_str = str(response)
    print(f"DEBUG: TwiML response after recording callback: {twiml_response_str}")
    return Response(content=twiml_response_str, media_type="text/xml")


@app.get("/get-recording-url/{call_sid}")
async def get_recording_url(call_sid: str):
    recording_info = active_calls_recording_url.get(call_sid)
    
    if recording_info:
        if recording_info['status'] == 'ready':
            return {"status": "ready", "recording_url": recording_info['recording_url']}
        elif recording_info['status'] == 'pending':
            return {"status": "processing", "message": "Recording still pending."}
    
    return {"status": "not_found", "message": "No recording found or initiated for this Call SID."}

@app.post("/status") 
async def handle_call_status(request: Request):
    form_data = await request.form()
    call_sid = form_data.get('CallSid')
    call_status = form_data.get('CallStatus')
    
    print(f"Call SID: {call_sid}, Status: {call_status}")
    
    if call_status in ['completed', 'failed', 'busy', 'no-answer']:
        if call_sid in active_calls_text_queue:
            del active_calls_text_queue[call_sid]
            print(f"[{call_sid}] Call ended. Cleaned up text queue.")
        if call_sid in active_calls_recording_url: 
            del active_calls_recording_url[call_sid]
            print(f"[{call_sid}] Call ended. Cleaned up recording URL.")
        if call_sid in active_conversations: # conversation_logic 인스턴스와 Event 객체 정리
            del active_conversations[call_sid]
            print(f"[{call_sid}] Call ended. Cleaned up conversation logic instance and events.")
    
    return "" 

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001)) 
    uvicorn.run(app, host="0.0.0.0", port=port)