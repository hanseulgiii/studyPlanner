# 🤖✨ AI 스마트 학습 로드맵 플래너 🎯📚

https://rg-sgsg-webapp-mvp-ahe8emg6dtdfh9hk.swedencentral-01.azurewebsites.net/

### 🌟 프로젝트 개요
- **프로젝트명**: AI 스마트 학습 로드맵 플래너  
- **문제**  
  - 🎬 교육 동영상을 볼 때 어떤 순서로 공부해야 할지 헷갈림  
  - 😵 계획 없이 보다가 중간에 포기하거나 복습이 어려움  
- **누구를 위한 건가요?**  
  - 👩‍💼 회사 교육 듣는 직원  
  - 📖 자기계발하려는 학습자  
- **해결 방법**  
  - 🔗 동영상 여러 개를 입력하면 → AI가 **학습 순서**를 정해주고  
  - 🗓️ **간단한 학습 계획**과 📝 **퀴즈**까지 만들어줌  

---

### 📂 프로젝트 구조
```bash
studyPlanner
├─ app.py              # Streamlit 메인 UI
├─ planner.py          # OpenAI API 호출 및 플랜/퀴즈 생성 로직
├─ .env                # 실제 환경변수 (gitignore로 제외)
├─ .env.example        # 공유용 환경변수 템플릿
├─ requirements.txt    # 필요한 패키지 목록
├─ README.md           # 프로젝트 설명 문서 
└─ .gitignore          # 민감정보/캐시 제외 설정
```
---

### 🏗️ 아키텍처 다이어그램
- **사용한 것들**  
  - 💻 **Streamlit**: 화면(UI)  
  - 🐍 **Python**: 기본 로직  
  - ☁️ **Azure OpenAI**: AI 모델 불러오기 (GPT-4o-mini)  
- **흐름**  
  1. 👤 사용자가 동영상 링크 입력  
  2. 🔄 Python이 Azure OpenAI에 요청  
  3. 🤖 AI가 학습 순서/계획/퀴즈 생성  
  4. 📺 결과를 화면에 보여줌  

---

### ⚙️ 파일별 담당 역할

## 1️⃣ app.py (프론트엔드/UI)
- **Streamlit 기반 UI**  
  - 동영상 URL 입력, 버튼 클릭으로 기능 실행  
  - 버튼: 📜 학습 순서 추천 / 🗓️ 학습 플랜 생성 / 🧩 학습 퀴즈 생성  
  - SelectBox로 퀴즈 개수 선택 가능  
- **출력 기능**  
  - 학습 순서 → 썸네일 + 제목 + 이유  
  - 학습 플랜 → Day별 목표/과제/복습  
  - 학습 퀴즈 → 정답은 제출 후 확인 가능  
- **UX**  
  - `st.spinner()` 로딩 표시  
  - `session_state`로 퀴즈 상태 관리  

## 2️⃣ planner.py (백엔드/AI 로직)
- **Azure OpenAI 호출**  
  - `.env`에서 API 키, 엔드포인트 불러오기  
- **핵심 함수**
  - `generate_plan()` → 학습 순서 + 플랜 + 퀴즈 생성  
  - `get_feedback()` → 퀴즈 채점 결과 분석 + 추천 영상 제시  
- **프롬프트 설계**  
  - JSON만 출력하도록 강제 → 파싱 안정성 확보  

## 3️⃣ requirements.txt (의존성)
- 프로젝트 실행에 필요한 패키지 목록  
  - `streamlit`, `openai`, `python-dotenv`, `requests`, `beautifulsoup4`  
- 한 줄 설치:  
  ```bash
  pip install -r requirements.txt
  ```

## 4️⃣ .env / .env.example (환경변수)
- .env
  - 실제 API 키와 엔드포인트 저장
  - 보안상 .gitignore에 추가해서 GitHub에 올리지 않음
- .env.example
  - 공유용 템플릿
  - API 키 대신 your_api_key_here 같은 placeholder 작성

## 5️⃣ README.md (문서)
- 프로젝트 소개 문서
  - 개요, 아키텍처, 실행 방법, 향후 개선 계획 정리
- 용도
  - 발표 자료처럼 활용 가능
  - 깃허브 첫 화면에서 프로젝트 설명 제공

---

### 🔑 핵심 기술 포인트
- 💡 **AI 프롬프트**  
  - "순서 + 계획 + 퀴즈를 JSON으로 만들어줘" 라고 요청  
- ☁️ **Azure OpenAI**  
  - 마이크로소프트 클라우드에서 AI 모델 사용  
- 🗂️ **간단한 구조**  
  - `app.py` (화면) + `planner.py` (AI 요청)  
  - 최소한의 파일로 빠르게 만들 수 있음  

---

### 🚀 실행 방법
## 1. 저장소 클론 & 진입
```bash
git clone https://github.com/yourname/studyPlanner.git
cd studyPlanner
```

## 2. 가상환경 및 패키지 설치
```bash
python -m venv .venv
source .venv/Scripts/activate   # (Windows PowerShell)
pip install -r requirements.txt
```

## 3. 환경변수 파일 설정
.env.example을 복사해서 .env 파일 생성
Azure OpenAI 리소스에서 발급받은 값 입력
```bash
envAZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```
### 4. 앱 실행
```bash
streamlit run app.py
```
→ 실행 후 http://localhost:8501 에 접속

---

### 🎥 라이브 데모  
- **보여줄 것**  
  - 🔗 동영상 링크 여러 개 입력  
  - ▶️ 버튼 클릭하면 → 학습 순서 + 학습 계획 + 퀴즈가 화면에 바로 뜸  
- **실행 방법**  
  - 💻 로컬에서 Streamlit 실행  
  - 🌐 Azure Web App에 배포해서 접속   
---

### 🎬 시연 영상

https://github.com/user-attachments/assets/ed4eecdc-a36f-4bc0-87d9-9936b5fbb4d2

---
### 🚀 앞으로 하고 싶은 것  
- 🔍 Azure AI Search 연결해서 자료 검색 가능하게 만들기 
- 🎥 Azure Video Indexer를 연동해서, 자동 자막·키워드·심층 요약 기반 맞춤형 학습 가능하게 만들기. 
- 👩‍🎓 학습자 맞춤형 계획 (초보자 / 중급자 / 고급자) 제안  
- 🗄️ 데이터베이스 연결해서 학습 진도 저장  
- 임직원 교육 플랫폼에 적용하기(직무나 조직 기준) 
