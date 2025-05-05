import whisper
import torch
import os
import tempfile
import openai
from dotenv import load_dotenv

class VoiceToText:
    def __init__(self, model_size="small"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_size = model_size
        
        # Load Whisper model
        self.whisper_model = whisper.load_model(self.model_size).to(self.device)
        
        # OpenAI API Key
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=openai.api_key)

    def listen(self, audio_path: str) -> str:
        """
        사용자의 음성을 받아 텍스트로 변환하고, 정제된 문장을 반환하는 함수
        audio_path: .wav 파일 경로
        """
        result = self.whisper_model.transcribe(audio_path, fp16=False, language="ko")
        raw_text = result["text"].strip()
        normalized = self.normalize(raw_text)
        return normalized
    
    def normalize(self, text: str) -> str:
        """
        Whisper로부터 받은 텍스트에서 잘못된 단어나 문장들을 교정하는 함수
        """
        prompt = (
            f'다음 문장에서 잘못된 단어를 문맥에 맞게 수정한 문장만 출력하세요. 설명 없이, 교정된 문장만 출력하세요.:\n"{text}"'
        )
        messages = [{"role": "user", "content": prompt}]

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
 
    def speak(self, text: str):
        """
        텍스트를 음성으로 출력하는 부분 (TTS 모델 연결 필요)
        현재는 print()로 대체
        """
        print("[AI] " +  text)