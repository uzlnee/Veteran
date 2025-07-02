"""
음성-텍스트 변환 및 정제 서비스
RTZR STT API와 OpenAI를 사용하여 음성을 텍스트로 변환하고 정제합니다.
"""

import os
import yaml
import openai
from dotenv import load_dotenv
from rtzr_client import RTZRClient


class VoiceToText:
    """음성을 텍스트로 변환하고 정제하는 클래스"""
    
    def __init__(self, model_size="small"):
        load_dotenv()

        # RTZR STT 클라이언트 초기화
        self.rtzr_client = RTZRClient()

        # OpenAI API Key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=openai.api_key)

        # 교정 프롬프트 로드
        correction_config = yaml.safe_load(
            open("./configs/sentence_correction_prompts.yaml", "r", encoding="utf-8")
        )
        self.correction_prompt = [correction_config["sentence_correction1"]]

    def listen(self, audio_path: str) -> str:
        """
        사용자의 음성을 받아 텍스트로 변환하고, 정제된 문장을 반환하는 함수
        - audio_path: .wav 파일 경로
        RTZR STT API의 sommers 모델을 사용합니다.
        """
        try:
            raw_text = self.rtzr_client.transcribe_file(
                audio_path, model_name="sommers"
            )
            if not raw_text:
                return "[음성 인식 실패]"
            normalized = self.normalize(raw_text)
            return normalized
        except Exception as e:
            print(f"[RTZR STT 오류] {str(e)}")
            return "[음성 인식 오류]"

    def normalize(self, text: str) -> str:
        """OpenAI GPT를 사용하여 STT 결과를 문법적으로 정제"""
        prompt = f'{self.correction_prompt}\n"{text}"'

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 한국어 문장을 교정하는 도우미입니다.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=256,
        )

        refined = response.choices[0].message.content.strip()
        return refined
