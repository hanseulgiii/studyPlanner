import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from planner import generate_plan, get_feedback

# -------------------------------
# 페이지 설정 (타이틀/파비콘)
# -------------------------------
st.set_page_config(
    page_title="AI 스마트 학습 로드맵 플래너",
    page_icon="🎓",
)

# -------------------------------
# CSS 스타일
# -------------------------------
st.markdown("""
    <style>
    /* selectbox 폭 고정 */
    div[data-baseweb="select"] {
        width: 100px !important;
        min-width: 100px !important;
        max-width: 100px !important;
    }
    /* 버튼 간격 동일 */
    .stButton button {
        margin-right: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 상단 소개 카드
# -------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h2 style="margin:0;">🎓 AI 스마트 학습 로드맵 플래너</h2>
        <p style="margin:0; font-size:15px;">
            동영상 URL을 입력하면 AI가 <b>학습 순서</b>, <b>플랜</b>, <b>퀴즈</b>를 자동으로 만들어드립니다! 🚀
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 세션 상태 초기화
# -------------------------------
if "result" not in st.session_state:
    st.session_state.result = {}
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0


urls = st.text_area("📥 동영상 URL 입력 (줄바꿈으로 구분)", height=150)

# 버튼 + 옵션
col1, col2, col3 = st.columns([1, 1, 2])
btn_order = col1.button("📜 학습 순서 추천", use_container_width=True)
btn_plan = col2.button("🗓️ 학습 플랜 생성", use_container_width=True)

with col3:
    c1, c2 = st.columns([0.3, 0.7])
    quiz_num = c1.selectbox(
        "퀴즈 개수",
        options=list(range(1, 31)),
        index=4,
        label_visibility="collapsed",
        key="quiz_num"
    )
    btn_quiz = c2.button("🧩 학습 퀴즈 생성", use_container_width=True, key="quiz_button")

st.markdown("</div>", unsafe_allow_html=True)

url_list = [u.strip() for u in urls.splitlines() if u.strip()] if urls.strip() else []
if (btn_order or btn_plan or btn_quiz) and not url_list:
    st.warning("먼저 동영상 URL을 입력해 주세요!")

# -------------------------------
# 유틸 - 썸네일 가져오기
# -------------------------------
def get_youtube_id(url: str) -> str | None:
    m = re.search(r"youtu\.be/([^\?&]+)", url)
    if m: return m.group(1)
    m = re.search(r"[?&]v=([^\?&]+)", url)
    if m: return m.group(1)
    return None

def resolve_thumbnail(url: str) -> str:
    vid = get_youtube_id(url)
    if vid:
        return f"https://img.youtube.com/vi/{vid}/0.jpg"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code >= 400:
            return "https://placehold.co/300x200?text=No+Thumbnail"
        soup = BeautifulSoup(r.text, "html.parser")
        for key in [
            {"property": "og:image"},
            {"name": "og:image"},
            {"name": "twitter:image"},
            {"property": "twitter:image"},
        ]:
            tag = soup.find("meta", key)
            if tag and tag.get("content"):
                return urljoin(r.url, tag["content"])
        link_tag = soup.find("link", rel="image_src")
        if link_tag and link_tag.get("href"):
            return urljoin(r.url, link_tag["href"])
    except Exception:
        return "https://placehold.co/300x200?text=No+Thumbnail"
    return "https://placehold.co/300x200?text=No+Thumbnail"

# -------------------------------
# 메인 로직
# -------------------------------
if url_list:
    # 학습 순서 추천
    if btn_order:
        with st.spinner("🧠 학습 순서를 계산 중이에요... 잠시만 기다려주세요! ✨"):
            st.session_state.result = generate_plan(url_list, num_questions=quiz_num)

        st.subheader("📜 추천 학습 순서")
        for item in st.session_state.result.get("ordered_videos", []):
            thumb_url = resolve_thumbnail(item["url"])
            c_img, c_txt = st.columns([1, 3])
            with c_img:
                st.markdown(
                    f'<a href="{item["url"]}" target="_blank">'
                    f'<img src="{thumb_url}" width="300" style="border-radius:12px;"/></a>',
                    unsafe_allow_html=True,
                )
            with c_txt:
                st.markdown(f"### [{item['title_guess']}]({item['url']})")
                st.write(f"📝 이유: {item['reason']}")
            st.markdown("---")

    # 학습 플랜
    if btn_plan:
        with st.spinner("📅 학습 플랜을 만드는 중이에요... 곧 완성돼요! ⏳"):
            st.session_state.result = generate_plan(url_list, num_questions=quiz_num)

        st.subheader("🗓️ 학습 플랜")
        for day in st.session_state.result.get("study_plan", []):
            with st.expander(f"Day {day['day']}"):
                st.markdown(f"🎯 **목표**: {', '.join(day['goals'])}")
                for sess in day.get("sessions", []):
                    st.markdown(f"🕑 **{sess['time_of_day'].capitalize()} 세션**")
                    st.write(f"- 📌 Focus: {sess['focus']}")
                    st.write(f"- 📝 Tasks: {', '.join(sess['tasks'])}")
                    st.write(f"- ⏱️ 예상 시간: {sess['est_time_min']}분")
                st.markdown(f"🔄 **복습**: {', '.join(day['review'])}")

    # 퀴즈 생성 시작
    if btn_quiz:
        with st.spinner("🧩 퀴즈를 출제하는 중이에요... 두근두근! 🎉"):
            st.session_state.result = generate_plan(url_list, num_questions=quiz_num)
            st.session_state.quiz_started = True
            st.session_state.quiz_submitted = False
            st.session_state.quiz_data = st.session_state.result.get("quiz", [])
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = 0

    # 퀴즈 화면
    if st.session_state.quiz_started:
        st.subheader(f"🧩 학습 퀴즈 ({len(st.session_state.quiz_data)}문항)")

        for i, q in enumerate(st.session_state.quiz_data, 1):
            st.markdown(f"**Q{i}. {q['question']}**")

            if not st.session_state.quiz_submitted:
                # 제출 전 → 라디오 선택 가능
                st.session_state.quiz_answers[i] = st.radio(
                    f"답변 선택 (Q{i})",
                    q["choices"],
                    key=f"quiz_{i}"
                )
            else:
                # 제출 후 → 읽기 전용 + 정답/해설
                st.radio(
                    f"답변 선택 (Q{i})",
                    q["choices"],
                    index=q["choices"].index(st.session_state.quiz_answers.get(i))
                    if st.session_state.quiz_answers.get(i) in q["choices"] else 0,
                    key=f"quiz_{i}_disabled",
                    disabled=True
                )
                st.write(f"👉 당신의 답변: **{st.session_state.quiz_answers.get(i)}**")
                st.write(f"✅ 정답: **{q['answer']}**")
                st.caption(f"해설: {q['explanation']}")

            st.markdown("---")

        if not st.session_state.quiz_submitted:
            if st.button("제출하기"):
                with st.spinner("채점 중이에요... ✍️"):
                    score = 0
                    for i, q in enumerate(st.session_state.quiz_data, 1):
                        if st.session_state.quiz_answers.get(i) == q["answer"]:
                            score += 1
                    st.session_state.quiz_score = score
                    st.session_state.quiz_submitted = True
                st.rerun()

        if st.session_state.quiz_submitted:
            score = st.session_state.quiz_score
            st.success(f"총 {len(st.session_state.quiz_data)}문항 중 {score}점!")

            with st.spinner("맞춤 피드백을 생성하는 중... 🧭"):
                feedback = get_feedback(
                    score,
                    len(st.session_state.quiz_data),
                    st.session_state.result.get("ordered_videos", [])
                )

            st.info(feedback["message"])

            st.markdown("### 📺 추천 영상")
            for rec in feedback.get("recommendations", []):
                st.markdown(f"- [{rec['title']}]({rec['url']})")
