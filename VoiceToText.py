import os
import yaml
import openai
from datetime import datetime
from dotenv import load_dotenv
from rtzr_client import RTZRClient

class VoiceToText:
    def __init__(self, model_size="small"):
        load_dotenv()        
        
        # RTZR STT 클라이언트 초기화
        self.rtzr_client = RTZRClient()
        
        # OpenAI API Key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=openai.api_key)

        # 대화 저장 폴더 생성 (날짜 + 시간)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join("recordings", timestamp)
        os.makedirs(self.session_dir, exist_ok=True)
        
        self.ai_counter = 1 # AI 응답 파일 번호
        self.user_counter = 1 # 사용자 질문 파일 번호
        self.transcript_path = os.path.join(self.session_dir, "transcript.txt")
        # self.wav_counter = 1 # 대화 중 파일 번호

        # 교정 프롬프트 로드
        correction_config = yaml.safe_load(open('./configs/sentence_correction_prompts.yaml', 'r', encoding='utf-8'))
        self.correction_prompt = [correction_config['sentence_correction1']]

    def speak(self, text: str):
        """
        AI 음성을 TTS로 출력하고 AI_XXXX.wav로 저장
        """
        filename = f"AI_{self.ai_counter:04}.wav"
        path = os.path.join(self.session_dir, filename)

        tts = gTTS(text=text, lang='ko')
        tts.save(path)

        self._append_transcript("[AI]", text)
        self.ai_counter += 1
        print(f"[AI] {text}")

    def record(self, threshold=80, silence_duration=3, sample_rate=16000) -> str:
        """
        사용자의 음성을 입력 받아, 3초 침묵하면 녹음을 종료하고 wav 파일로 저장하는 함수
        """
        buffer = []
        is_silent = False
        silence_start_time = None

        print("[녹음 시작] 말씀해주세요.")

        def callback(indata, frames, time_info, status):
            nonlocal is_silent, silence_start_time

            if status:
                print("Stream status: ", status)

            buffer.append(indata.copy())
            volume = np.abs(indata).mean()

            # 침묵 감지
            if volume < threshold:
                if not is_silent:
                    is_silent = True
                    silence_start_time = time.time()
                elif time.time() - silence_start_time >= silence_duration:
                    raise sd.CallbackStop()
            else:
                is_silent = False
                silence_start_time = None

        filename = f"USER_{self.user_counter:04}.wav"
        path = os.path.join(self.session_dir, filename)

        try:
            with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate, dtype='int16', blocksize=1024) as stream:
                while stream.active:
                    time.sleep(0.1)  # CPU 낭비 막기용 짧은 대기

        except Exception as e:
            print("녹음 종료됨:", str(e))
        
        if buffer:
            recorded = np.concatenate(buffer, axis=0)
            write(path, sample_rate, recorded)
            print(f"[저장 완료] {path}에 저장되었습니다.")

            # RTZR STT + 정제
            text = self.listen(path)
            self._append_transcript("[USER]", text)
            self.user_counter += 1
            return text

        else:
            print("[오류] 녹음된 데이터가 없습니다. 마이크 입력을 확인하세요.")
            return "[녹음 실패]"

    def listen(self, audio_path: str) -> str:
        """
        사용자의 음성을 받아 텍스트로 변환하고, 정제된 문장을 반환하는 함수
        - audio_path: .wav 파일 경로
        RTZR STT API의 sommers 모델을 사용합니다.
        """
        try:
            raw_text = self.rtzr_client.transcribe_file(audio_path, model_name="sommers")
            if not raw_text:
                return "[음성 인식 실패]"
            normalized = self.normalize(raw_text)
            return normalized
        except Exception as e:
            print(f"[RTZR STT 오류] {str(e)}")
            return "[음성 인식 오류]"
    
    def normalize(self, text: str) -> str:
        """
        RTZR STT로부터 받은 텍스트에서 잘못된 단어나 문장들을 교정하는 함수
        """
        prompt = (
            f'{self.correction_prompt}\n"{text}"'
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 한국어 문장을 교정하는 도우미입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=256
        )

        refined = response.choices[0].message.content.strip()
        return refined
    
    def _append_transcript(self, speaker: str, text: str):
        with open(self.transcript_path, "a", encoding="utf-8") as f:
            f.write(f"{speaker} : {text}\n")