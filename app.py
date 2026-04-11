import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import json
import os
import html
from openai import OpenAI
from io import BytesIO

from dotenv import load_dotenv

# ==========================================
# 1. 환경 설정
# ==========================================
load_dotenv()
# 1) Dify API 설정
DIFY_API_KEY = os.environ.get("DIFY_API_KEY")
# URL 끝에 /가 있다면 제거하여 경로 중복 방지
DIFY_BASE_URL = os.environ.get("DIFY_URL", "https://api.dify.ai/v1").rstrip('/')
WORKFLOW_ID = os.environ.get("WORKFLOW_ID")

# 2) OpenAI API 설정 (Whisper STT용)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 앱 페이지 설정
st.set_page_config(page_title="BrainSync Auditor", page_icon="🧠", layout="wide")

# ==========================================
# 2. 핵심 기능 함수 (Dify & Whisper 연동)
# ==========================================

# (1) OpenAI Whisper를 이용한 오디오 -> 텍스트 변환
def transcribe_audio(audio_bytes, file_name="recorded_audio.wav"):
    try:
        # 오디오 데이터를 메모리 바이트 파일로 변환
        audio_file = BytesIO(audio_bytes)
        audio_file.name = file_name # Whisper API는 파일 이름 확장을 필요로 함
        
        # Whisper API 호출
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
        )
        return transcript
    except Exception as e:
        return f"❌ Transcription Error: {str(e)}"

# (2) Dify 특정 워크플로우 호출 및 JSON 파싱
def get_final_result(transcript):
    # Dify Endpoint URL 생성
    # url = f"{DIFY_BASE_URL}/workflows/{WORKFLOW_ID}/run"
    url = f"{DIFY_BASE_URL}/workflows/run"
    
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {"meeting_transcript": transcript},
        "response_mode": "blocking",
        "user": "berlin_hacker"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            res_data = response.json()
            outputs = res_data.get("data", {}).get("outputs", {})
            raw_result = outputs.get("result", "")
            
            # --- JSON 데이터 파싱 (마크다운 포맷 제거 포함) ---
            try:
                # 만약 결과가 텍스트라면 JSON으로 변환 시도
                if isinstance(raw_result, str):
                    clean_json = raw_result.replace("```json", "").replace("```", "").strip()
                    structured_data = json.loads(clean_json)
                    return structured_data
                # 이미 dict 형식이라면 그대로 반환
                return raw_result
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 안전하게 원본 텍스트 반환 (에러 방지용)
                return raw_result
        else:
            err_msg = response.json().get('message', 'Unknown error')
            return f"❌ Dify Error: {err_msg}"
            
    except Exception as e:
        return f"❌ Request Error: {str(e)}"


def get_transcript_stats(text):
    cleaned = (text or "").strip()
    if not cleaned:
        return {"chars": 0, "words": 0, "lines": 0}
    return {
        "chars": len(cleaned),
        "words": len(cleaned.split()),
        "lines": len(cleaned.splitlines()),
    }


def render_result_block(result):
    if isinstance(result, dict) and "quizzes" in result:
        st.markdown(
            """
            <div class="section-heading">
                <span>Audit output</span>
                <h3>Conflict checks and recall prompts</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        quizzes = result.get("quizzes", [])
        for idx, item in enumerate(quizzes, start=1):
            category = html.escape(item.get("category", "Analysis"))
            question = html.escape(item.get("question", ""))
            correct_answer = html.escape(str(item.get("correct_answer", "")))
            insight = html.escape(item.get("insight", ""))
            options = item.get("options", {})

            st.markdown(
                f"""
                <div class="quiz-card">
                    <div class="quiz-card__meta">
                        <span class="quiz-index">Case {idx:02d}</span>
                        <span class="quiz-category">{category}</span>
                    </div>
                    <div class="quiz-card__question">{question}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            option_cols = st.columns(2)
            option_cols[0].markdown(
                f"""
                <div class="option-card">
                    <div class="option-card__label">Option A</div>
                    <div class="option-card__body">{html.escape(options.get("A", ""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            option_cols[1].markdown(
                f"""
                <div class="option-card">
                    <div class="option-card__label">Option B</div>
                    <div class="option-card__body">{html.escape(options.get("B", ""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-card__label">Correct answer</div>
                    <div class="answer-card__value">{correct_answer}</div>
                    <div class="answer-card__insight">{insight}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="section-heading">
                <span>Audit output</span>
                <h3>Raw workflow response</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(result)

# ==========================================
# 3. UI 레이아웃 및 컴포넌트
# ==========================================
st.markdown(
    """
    <style>
        :root {
            --bg: #f4efe7;
            --surface: rgba(255, 251, 245, 0.88);
            --surface-strong: #fffaf2;
            --line: rgba(64, 47, 34, 0.12);
            --text: #241b15;
            --muted: #6d5c4f;
            --accent: #b6522f;
            --accent-deep: #7d2f19;
            --olive: #435744;
            --gold: #d7a95b;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(214, 169, 91, 0.28), transparent 30%),
                radial-gradient(circle at top right, rgba(182, 82, 47, 0.12), transparent 24%),
                linear-gradient(180deg, #f8f1e7 0%, #f1e7d9 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1320px;
            padding-top: 2.2rem;
            padding-bottom: 2.5rem;
        }

        h1, h2, h3 {
            font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
            letter-spacing: -0.02em;
            color: var(--text);
        }

        .hero-shell {
            border: 1px solid var(--line);
            background:
                linear-gradient(140deg, rgba(255, 250, 242, 0.96), rgba(249, 240, 228, 0.86)),
                #fffaf2;
            border-radius: 28px;
            padding: 2rem 2rem 1.6rem;
            box-shadow: 0 24px 60px rgba(64, 47, 34, 0.08);
            margin-bottom: 1.4rem;
            position: relative;
            overflow: hidden;
        }

        .hero-shell::after {
            content: "";
            position: absolute;
            inset: auto -40px -55px auto;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(182, 82, 47, 0.18), transparent 68%);
        }

        .hero-eyebrow {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(67, 87, 68, 0.08);
            color: var(--olive);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 3.2rem;
            line-height: 0.96;
            margin: 0;
            max-width: 760px;
        }

        .hero-copy {
            max-width: 720px;
            color: var(--muted);
            font-size: 1.03rem;
            line-height: 1.7;
            margin: 0.9rem 0 1.4rem;
        }

        .pill-row {
            display: flex;
            gap: 0.7rem;
            flex-wrap: wrap;
        }

        .pill {
            border: 1px solid rgba(67, 87, 68, 0.14);
            background: rgba(255, 255, 255, 0.52);
            padding: 0.7rem 0.95rem;
            border-radius: 18px;
            min-width: 150px;
        }

        .pill-label {
            display: block;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-bottom: 0.28rem;
        }

        .pill-value {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
        }

        .panel {
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.2rem 1.2rem 1.35rem;
            background: var(--surface);
            box-shadow: 0 16px 40px rgba(64, 47, 34, 0.06);
            backdrop-filter: blur(8px);
        }

        .panel + .panel {
            margin-top: 1rem;
        }

        .section-heading span {
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.76rem;
            font-weight: 700;
        }

        .section-heading h3 {
            margin: 0.22rem 0 0.3rem;
            font-size: 1.5rem;
        }

        .section-copy {
            color: var(--muted);
            margin-bottom: 1rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.9rem 0 0.4rem;
        }

        .stat-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            background: rgba(255, 250, 244, 0.78);
        }

        .stat-card__label {
            font-size: 0.74rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .stat-card__value {
            font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
            font-size: 1.65rem;
            color: var(--text);
            margin-top: 0.18rem;
        }

        .quiz-card,
        .option-card,
        .answer-card,
        .empty-state {
            border: 1px solid var(--line);
            border-radius: 20px;
            background: var(--surface-strong);
        }

        .quiz-card {
            padding: 1rem 1.05rem;
            margin-top: 0.95rem;
        }

        .quiz-card__meta {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.75rem;
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .quiz-card__question {
            font-size: 1.05rem;
            line-height: 1.55;
            color: var(--text);
            font-weight: 600;
        }

        .option-card {
            padding: 0.95rem 1rem;
            height: 100%;
            margin-top: 0.7rem;
        }

        .option-card__label,
        .answer-card__label {
            color: var(--accent);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 0.38rem;
        }

        .option-card__body {
            color: var(--text);
            line-height: 1.55;
        }

        .answer-card {
            margin: 0.7rem 0 0.2rem;
            padding: 0.95rem 1rem 1rem;
            border-left: 5px solid var(--gold);
        }

        .answer-card__value {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
        }

        .answer-card__insight {
            margin-top: 0.55rem;
            color: var(--muted);
            line-height: 1.55;
        }

        .empty-state {
            padding: 1.1rem 1rem;
            color: var(--muted);
            line-height: 1.6;
        }

        .footer-note {
            text-align: center;
            color: var(--muted);
            font-size: 0.88rem;
            padding: 1rem 0 0.2rem;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px;
            border: 1px solid rgba(64, 47, 34, 0.12);
            background: rgba(255, 255, 255, 0.48);
            padding: 0.55rem 0.95rem;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: rgba(182, 82, 47, 0.12);
            border-color: rgba(182, 82, 47, 0.3);
            color: var(--accent-deep);
        }

        div[data-testid="stTextArea"] textarea {
            background: rgba(255, 250, 244, 0.92);
            border-radius: 18px;
        }

        div[data-testid="stFileUploader"] section,
        div[data-testid="stAudio"] {
            border-radius: 18px;
        }

        div[data-testid="stButton"] button {
            border-radius: 999px;
            min-height: 3rem;
            font-weight: 700;
            border: 1px solid rgba(64, 47, 34, 0.12);
            background: #fff7ee;
            color: var(--text);
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #b6522f, #8d3a21);
            color: #fffaf5;
            border: none;
            box-shadow: 0 14px 30px rgba(182, 82, 47, 0.24);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "final_transcript" not in st.session_state:
    st.session_state["final_transcript"] = ""
if "audit_result" not in st.session_state:
    st.session_state["audit_result"] = None
if "input_source" not in st.session_state:
    st.session_state["input_source"] = "Awaiting input"

transcript_stats = get_transcript_stats(st.session_state["final_transcript"])

st.markdown(
    f"""
    <section class="hero-shell">
        <div class="hero-eyebrow">Meeting Reliability Console</div>
        <h1 class="hero-title">BrainSync Auditor</h1>
        <p class="hero-copy">
            Review meeting transcripts, challenge weak consensus, and turn fuzzy alignment into concrete recall checks.
            Designed for fast live audits instead of generic demo dashboards.
        </p>
        <div class="pill-row">
            <div class="pill">
                <span class="pill-label">Current source</span>
                <span class="pill-value">{html.escape(st.session_state["input_source"])}</span>
            </div>
            <div class="pill">
                <span class="pill-label">Transcript size</span>
                <span class="pill-value">{transcript_stats["words"]} words</span>
            </div>
            <div class="pill">
                <span class="pill-label">Audit pipeline</span>
                <span class="pill-value">Whisper -> Dify -> Quiz</span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1.15, 0.85], gap="large")

with col1:
    st.markdown(
        """
        <div class="panel">
            <div class="section-heading">
                <span>Input capture</span>
                <h3>Bring in the meeting record</h3>
            </div>
            <div class="section-copy">
                Choose the fastest path: paste raw text, capture a live discussion, or upload notes and audio.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Direct Text", "Live Recording", "File Upload"])

    with tab1:
        text_input = st.text_area(
            "Paste meeting transcript or raw conversation text here",
            height=280,
            placeholder="Drop in meeting notes, transcript fragments, or a full conversation log.",
        )
        if st.button("Load text into workspace", use_container_width=True):
            st.session_state["final_transcript"] = text_input
            st.session_state["input_source"] = "Direct text"
            st.session_state["audit_result"] = None
            st.success("Transcript loaded from direct text.")

    with tab2:
        st.caption("Capture a live conversation, then transcribe it with Whisper.")
        audio_recorded = mic_recorder(
            start_prompt="Start recording",
            stop_prompt="Stop and transcribe",
            key="recorder",
            format="wav",
        )

        if audio_recorded:
            with st.spinner("Transcribing recording..."):
                transcript = transcribe_audio(audio_recorded["bytes"], file_name="recorded.wav")
                st.session_state["final_transcript"] = transcript
                st.session_state["input_source"] = "Live recording"
                st.session_state["audit_result"] = None
            st.audio(audio_recorded["bytes"])
            st.success("Recording transcribed and loaded.")

    with tab3:
        st.caption("Upload `.txt`, `.mp3`, or `.wav` input.")
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "mp3", "wav"])

        if uploaded_file is not None:
            if uploaded_file.type == "text/plain":
                st.session_state["final_transcript"] = uploaded_file.read().decode("utf-8")
                st.session_state["input_source"] = f"Text file: {uploaded_file.name}"
                st.session_state["audit_result"] = None
                st.success("Text file loaded.")
            else:
                with st.spinner(f"Transcribing {uploaded_file.name}..."):
                    transcript = transcribe_audio(uploaded_file.read(), file_name=uploaded_file.name)
                    st.session_state["final_transcript"] = transcript
                    st.session_state["input_source"] = f"Audio file: {uploaded_file.name}"
                    st.session_state["audit_result"] = None
                st.success("Audio file transcribed and loaded.")

    refreshed_stats = get_transcript_stats(st.session_state["final_transcript"])

    st.markdown(
        """
        <div class="panel">
            <div class="section-heading">
                <span>Transcript review</span>
                <h3>Clean the source before you audit it</h3>
            </div>
            <div class="section-copy">
                Fix names, remove filler, and make the conversation precise enough for reliable conflict checks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-card__label">Words</div>
                <div class="stat-card__value">{refreshed_stats["words"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card__label">Characters</div>
                <div class="stat-card__value">{refreshed_stats["chars"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card__label">Lines</div>
                <div class="stat-card__value">{refreshed_stats["lines"]}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_transcript = st.text_area(
        "Review and edit the loaded transcript before auditing",
        value=st.session_state["final_transcript"],
        height=320,
        placeholder="Your working transcript appears here.",
    )
    st.session_state["final_transcript"] = current_transcript

with col2:
    st.markdown(
        """
        <div class="panel">
            <div class="section-heading">
                <span>Audit run</span>
                <h3>Generate conflict checks</h3>
            </div>
            <div class="section-copy">
                The transcript is compared through your Cognee and Dify workflow, then returned as comprehension checks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    run_button = st.button(
        "Analyze transcript",
        type="primary",
        use_container_width=True,
    )

    if run_button:
        if current_transcript.strip():
            with st.spinner("Analyzing transcript against workflow..."):
                st.session_state["audit_result"] = get_final_result(current_transcript)
        else:
            st.warning("Provide a transcript before running the audit.")

    result = st.session_state["audit_result"]

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if result is None:
        st.markdown(
            """
            <div class="empty-state">
                Run an audit to populate this workspace. Structured quiz results will be rendered as review cards instead of raw expanders.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        render_result_block(result)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer-note">
        MindSync @ Berlin Hackathon 2026 | Powered by Cognee, Dify, and Whisper
    </div>
    """,
    unsafe_allow_html=True,
)
