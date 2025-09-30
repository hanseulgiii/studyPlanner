import os
import re
import json
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

# -------------------------------
# 환경 변수 로드
# -------------------------------
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# -------------------------------
# JSON 추출 유틸 함수
# -------------------------------
def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """GPT 응답에서 JSON만 뽑아내는 함수"""
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

# -------------------------------
# 학습 플랜 생성
# -------------------------------
def generate_plan(video_urls: List[str], days: int = 2, num_questions: int = 4) -> Dict[str, Any]:
    """동영상 기반 학습 플랜 + 퀴즈 생성"""
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
      "thumbnail_url": "string (없으면 https://placehold.co/300x200?text=No+Thumbnail)",
      "reason": "string (논리적으로 최소 4문장)"
    }
  ],
  "study_plan": [
    {
      "day": 1,
      "goals": ["string"],
      "sessions": [
        {
          "time_of_day": "morning",
          "focus": "string",
          "tasks": ["string"],
          "est_time_min": 90
        },
        {
          "time_of_day": "afternoon",
          "focus": "string",
          "tasks": ["string"],
          "est_time_min": 90
        },
        {
          "time_of_day": "evening",
          "focus": "string",
          "tasks": ["string"],
          "est_time_min": 60
        }
      ],
      "review": ["string"]
    }
  ],
  "quiz": [
    {
      "type": "mc",
      "question": "string",
      "choices": ["A","B","C","D"],
      "answer": "A",
      "explanation": "string"
    }
  ]
}
""".strip()

    user = f"""
다음 동영상 목록을 바탕으로:
1) 학습에 적합한 순서(근거 포함, 최소 4문장 이상)
2) {days}일 학습 플랜
3) 객관식 퀴즈 {num_questions}문항

학습 플랜 작성 규칙:
- 각 day는 morning / afternoon / evening 3개의 세션으로 나눠라.
- 각 세션에는 time_of_day, focus, tasks, est_time_min을 반드시 포함해야 한다.
- tasks는 단순히 '영상 보기'가 아니라 '영상 보며 키워드 메모', '핵심 개념 요약', '관련 예제 풀기', '퀴즈 풀기'처럼 구체적이어야 한다.
- review에는 하루가 끝난 후 수행할 복습 활동(요약, 퀴즈 풀기, 토론, 개념 맵 작성 등)을 반드시 넣어라.
- 출력은 오직 JSON만.

동영상 URL 목록: {video_urls}

JSON 스키마(참고):
{schema}
""".strip()

    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        temperature=0.6,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = resp.choices[0].message.content
    parsed = _extract_json(content)

    return parsed if parsed else {}

# -------------------------------
# 점수 기반 피드백 생성
# -------------------------------
def get_feedback(score: int, total: int, ordered_videos: list) -> dict:
    """점수 기반 학습 피드백 + GPT 추천 영상"""
    ratio = score / total if total > 0 else 0
    feedback = {}

    if ratio < 0.5:
        feedback["message"] = f"점수가 낮습니다. 👉 {ordered_videos[0]['title_guess']} 부터 다시 복습하세요."
        restart_index = 0
    elif ratio < 0.8:
        feedback["message"] = f"절반 이상은 이해했지만 부족합니다. 👉 {ordered_videos[1]['title_guess']} 부터 다시 보시는 게 좋아요."
        restart_index = min(1, len(ordered_videos) - 1)
    else:
        feedback["message"] = f"잘하고 있습니다! 👉 마지막 영상만 복습해도 충분합니다."
        restart_index = len(ordered_videos) - 1

    # GPT로 추천 영상 받아오기
    user_prompt = f"""
    학습 주제는 {ordered_videos[restart_index]['title_guess']} 입니다.
    이와 관련된 온라인 학습 영상 4개를 추천해주세요.
    반드시 JSON 배열 형식으로만, 각 항목은 title과 url을 포함해야 합니다.
    """

    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "JSON 배열만 출력"},
            {"role": "user", "content": user_prompt},
        ]
    )

    recs = _extract_json(resp.choices[0].message.content) or []
    feedback["recommendations"] = recs
    return feedback
