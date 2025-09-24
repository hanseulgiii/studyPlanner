import os, re, json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", text).strip("` \n\t")
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(cleaned[start:end+1])
        except:
            pass
    try:
        return json.loads(cleaned)
    except:
        return None

def generate_plan(video_urls: List[str], days: int = 2, num_questions: int = 4) -> Dict[str, Any]:
    assert DEPLOYMENT, "환경변수 AZURE_OPENAI_DEPLOYMENT가 설정되지 않았습니다."

    system = (
        "너는 한국어로 답하는 교육 설계 도우미다. "
        "반드시 JSON만 출력하고, 마크다운/설명/코드펜스를 절대 포함하지 마."
    )

    schema = """
{
  "ordered_videos": [
    {
      "index": 1,
      "url": "string",
      "title_guess": "string",
      "thumbnail_url": "string (가능하다면 영상 썸네일 링크, 알 수 없으면 https://placehold.co/300x200?text=No+Thumbnail)",
      "reason": "string (논리적으로 최소 4문장)"
    }
  ],
  "study_plan": [
    {"day": 1, "goals": ["string"], "tasks": ["string"], "est_time_min": 90, "review": ["string"]}
  ],
  "quiz": [
    {"type": "mc", "question": "string", "choices": ["A","B","C","D"], "answer": "A", "explanation": "string"}
  ]
}
""".strip()

    user = f"""
다음 동영상 목록을 바탕으로:
1) 학습에 적합한 순서(근거 포함, 최소 4문장 이상)
2) {days}일 학습 플랜(목표/할 일/예상 시간/복습 포인트)
3) 객관식 퀴즈 {num_questions}문항

출력 규칙:
- JSON만 출력.
- ordered_videos 배열의 각 항목은 반드시 index, url, title_guess, thumbnail_url, reason 을 포함할 것.
- thumbnail_url은 가능하다면 실제 썸네일을, 불가능하면 'https://placehold.co/300x200?text=No+Thumbnail' 을 넣어라.

동영상 URL 목록: {video_urls}

JSON 스키마(참고):
{schema}
""".strip()

    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        temperature=0.5,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = resp.choices[0].message.content
    parsed = _extract_json(content)

    return parsed if parsed else {}
