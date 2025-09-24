import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from planner import generate_plan

st.title("🤖 AI 스마트 학습 로드맵 플래너")

urls = st.text_area("동영상 URL을 여러 개 입력하세요 (줄바꿈으로 구분)", height=150)

col1, col2, col3 = st.columns(3)
btn_order = col1.button("📜 학습 순서 추천")
btn_plan = col2.button("🗓️ 학습 플랜 생성")
btn_quiz = col3.button("🧩 학습 퀴즈 생성")

url_list = [u.strip() for u in urls.splitlines() if u.strip()] if urls.strip() else []

if (btn_order or btn_plan or btn_quiz) and not url_list:
    st.warning("먼저 동영상 URL을 입력해 주세요!")

def get_youtube_id(url: str) -> str | None:
    """유튜브 URL에서 영상 ID 추출"""
    m = re.search(r"youtu\.be/([^\?&]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"[?&]v=([^\?&]+)", url)
    if m:
        return m.group(1)
    return None

def resolve_thumbnail(url: str) -> str:
    """유튜브 → 강제 생성, 그 외 → og:image 파싱"""
    vid = get_youtube_id(url)
    if vid:
        return f"https://img.youtube.com/vi/{vid}/0.jpg"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
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

if url_list and (btn_order or btn_plan or btn_quiz):
    result = generate_plan(url_list)

    if btn_order:
        st.subheader("📜 추천 학습 순서")
        for item in result.get("ordered_videos", []):
            thumb_url = resolve_thumbnail(item["url"])
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(
                    f'<a href="{item["url"]}" target="_blank">'
                    f'<img src="{thumb_url}" width="300" style="border-radius:12px;"/></a>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(f"### [{item['title_guess']}]({item['url']})")
                st.write(f"📝 이유: {item['reason']}")
            st.markdown("---")

    if btn_plan:
        st.subheader("🗓️ 학습 플랜")
        for day in result.get("study_plan", []):
            with st.expander(f"Day {day['day']}"):
                st.markdown(f"🎯 **목표**: {', '.join(day['goals'])}")
                st.markdown(f"📝 **할 일**: {', '.join(day['tasks'])}")
                st.markdown(f"⏱️ **예상 시간**: {day['est_time_min']}분")
                st.markdown(f"🔄 **복습 포인트**: {', '.join(day['review'])}")

    if btn_quiz:
        st.subheader("🧩 학습 퀴즈")
        for i, q in enumerate(result.get("quiz", []), 1):
            st.markdown(f"**Q{i}. {q['question']}**")
            for choice in q["choices"]:
                st.write(f"- {choice}")
            st.markdown(f"✅ 정답: **{q['answer']}**")
            st.caption(f"해설: {q['explanation']}")
            st.markdown("---")
