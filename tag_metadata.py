import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 로드
openai_api_key = os.getenv("OPENAI_API_KEY")

RECORDINGS_DIR = "/home/yujin/Veteran/recordings"

location_categories = ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
field_categories = ["요양보호", "경비", "청소", "운전", "사무", "상담", "교육", "기타"]

def classify_with_llm(text, categories, prompt_template):
    prompt = prompt_template.format(categories=', '.join(categories), input=text)
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

location_prompt = """
아래의 지역명을 내가 제공한 대분류 중 하나만 선택해서 대분류명만 한 단어로 출력해줘.
- 대분류: {categories}
- 입력: "{input}"
- 출력 예시: "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"
- 답변은 반드시 대분류 중 하나만 선택해서 쌍따옴표 없이 한글로 출력해.
"""

field_prompt = """
아래의 희망분야명을 내가 제공한 대분류 중 하나만 선택해서 대분류명만 한 단어로 출력해줘. 
- 대분류: {categories}
- 입력: "{input}"
- 출력 예시: "요양보호", "경비", "청소", "운전", "사무", "상담", "교육", "기타"
- 답변은 반드시 대분류 중 하나만 선택해서 쌍따옴표 없이 한글로 출력해.
"""

for folder in os.listdir(RECORDINGS_DIR):
    meta_path = os.path.join(RECORDINGS_DIR, folder, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        # location 분류
        loc = meta.get("location", "")
        if loc:
            loc_tag = classify_with_llm(loc, location_categories, location_prompt)
            meta["location_tag"] = loc_tag
        # preferred_field 분류
        pf = meta.get("preferred_field", "")
        if pf:
            if isinstance(pf, list):
                pf_tag = [classify_with_llm(x, field_categories, field_prompt) for x in pf]
            else:
                pf_tag = classify_with_llm(pf, field_categories, field_prompt)
            meta["preferred_field_tag"] = pf_tag
        # 저장
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"Updated: {meta_path}")
    else:
        print(f"metadata.json 파일이 없습니다: {meta_path}")