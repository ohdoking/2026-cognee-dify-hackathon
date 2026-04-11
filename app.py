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


THEMES = {
    "Light": {
        "bg_left": "rgba(46, 108, 246, 0.18)",
        "bg_right": "rgba(15, 123, 108, 0.12)",
        "bg_gradient": "linear-gradient(180deg, #f5f8fc 0%, #eaf0f8 100%)",
        "surface": "rgba(255, 255, 255, 0.74)",
        "surface_strong": "#ffffff",
        "line": "rgba(19, 32, 51, 0.10)",
        "text": "#132033",
        "muted": "#6b778d",
        "accent": "#2e6cf6",
        "accent_deep": "#1d4ed8",
        "olive": "#0f7b6c",
        "gold": "#d97706",
        "hero_start": "rgba(255, 255, 255, 0.95)",
        "hero_end": "rgba(228, 238, 255, 0.90)",
        "hero_orb": "rgba(46, 108, 246, 0.18)",
        "pill_border": "rgba(46, 108, 246, 0.14)",
        "pill_bg": "rgba(255, 255, 255, 0.58)",
        "card_shadow": "rgba(19, 32, 51, 0.08)",
        "stat_bg": "rgba(255, 255, 255, 0.86)",
        "tab_bg": "rgba(255, 255, 255, 0.60)",
        "tab_selected": "rgba(46, 108, 246, 0.12)",
        "tab_selected_border": "rgba(46, 108, 246, 0.26)",
        "input_bg": "rgba(255, 255, 255, 0.95)",
        "button_bg": "#f8fbff",
        "primary_start": "#2e6cf6",
        "primary_end": "#0f7b6c",
        "primary_shadow": "rgba(46, 108, 246, 0.28)",
    },
    "Dark": {
        "bg_left": "rgba(34, 211, 238, 0.14)",
        "bg_right": "rgba(14, 165, 233, 0.10)",
        "bg_gradient": "linear-gradient(180deg, #08101d 0%, #0d1726 100%)",
        "surface": "rgba(10, 18, 31, 0.82)",
        "surface_strong": "#101a2b",
        "line": "rgba(148, 163, 184, 0.14)",
        "text": "#e6edf7",
        "muted": "#95a4bb",
        "accent": "#22d3ee",
        "accent_deep": "#67e8f9",
        "olive": "#38bdf8",
        "gold": "#f59e0b",
        "hero_start": "rgba(12, 20, 34, 0.92)",
        "hero_end": "rgba(16, 26, 43, 0.98)",
        "hero_orb": "rgba(34, 211, 238, 0.16)",
        "pill_border": "rgba(34, 211, 238, 0.18)",
        "pill_bg": "rgba(15, 23, 42, 0.52)",
        "card_shadow": "rgba(2, 6, 23, 0.30)",
        "stat_bg": "rgba(16, 26, 43, 0.92)",
        "tab_bg": "rgba(15, 23, 42, 0.72)",
        "tab_selected": "rgba(34, 211, 238, 0.16)",
        "tab_selected_border": "rgba(34, 211, 238, 0.30)",
        "input_bg": "rgba(15, 23, 42, 0.92)",
        "button_bg": "#0f172a",
        "primary_start": "#22d3ee",
        "primary_end": "#2563eb",
        "primary_shadow": "rgba(37, 99, 235, 0.32)",
    },
}

# ==========================================
# 3. UI 레이아웃 및 컴포넌트
# ==========================================
if "final_transcript" not in st.session_state:
    st.session_state["final_transcript"] = ""
if "audit_result" not in st.session_state:
    st.session_state["audit_result"] = None
if "input_source" not in st.session_state:
    st.session_state["input_source"] = "Awaiting input"
if "color_mode" not in st.session_state:
    st.session_state["color_mode"] = "Light"

theme_cols = st.columns([0.78, 0.22])
with theme_cols[1]:
    st.radio(
        "Mode",
        options=["Light", "Dark"],
        horizontal=True,
        key="color_mode",
    )

theme = THEMES[st.session_state["color_mode"]]
theme_css = """
    <style>
        :root {
            --surface: __surface__;
            --surface-strong: __surface_strong__;
            --line: __line__;
            --text: __text__;
            --muted: __muted__;
            --accent: __accent__;
            --accent-deep: __accent_deep__;
            --olive: __olive__;
            --gold: __gold__;
            --pill-border: __pill_border__;
            --pill-bg: __pill_bg__;
            --card-shadow: __card_shadow__;
            --stat-bg: __stat_bg__;
            --tab-bg: __tab_bg__;
            --tab-selected: __tab_selected__;
            --tab-selected-border: __tab_selected_border__;
            --input-bg: __input_bg__;
            --button-bg: __button_bg__;
            --primary-start: __primary_start__;
            --primary-end: __primary_end__;
            --primary-shadow: __primary_shadow__;
            --hero-start: __hero_start__;
            --hero-end: __hero_end__;
            --hero-orb: __hero_orb__;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, __bg_left__, transparent 30%),
                radial-gradient(circle at top right, __bg_right__, transparent 24%),
                __bg_gradient__;
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
                linear-gradient(140deg, var(--hero-start), var(--hero-end)),
                var(--surface-strong);
            border-radius: 28px;
            padding: 2rem 2rem 1.6rem;
            box-shadow: 0 24px 60px var(--card-shadow);
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
            background: radial-gradient(circle, var(--hero-orb), transparent 68%);
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
            border: 1px solid var(--pill-border);
            background: var(--pill-bg);
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
            box-shadow: 0 16px 40px var(--card-shadow);
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
            background: var(--stat-bg);
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
            border: 1px solid var(--line);
            background: var(--tab-bg);
            padding: 0.55rem 0.95rem;
            color: var(--muted);
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: var(--tab-selected);
            border-color: var(--tab-selected-border);
            color: var(--accent-deep);
        }

        div[data-testid="stTextArea"] textarea {
            background: var(--input-bg);
            border-radius: 18px;
            color: var(--text);
            border: 1px solid var(--line);
        }

        div[data-testid="stFileUploader"] section,
        div[data-testid="stAudio"] {
            border-radius: 18px;
        }

        div[data-testid="stFileUploader"] section {
            background: var(--input-bg);
            border: 1px dashed var(--line);
        }

        div[data-testid="stButton"] button {
            border-radius: 999px;
            min-height: 3rem;
            font-weight: 700;
            border: 1px solid var(--line);
            background: var(--button-bg);
            color: var(--text);
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-start), var(--primary-end));
            color: #f8fbff;
            border: none;
            box-shadow: 0 14px 30px var(--primary-shadow);
        }

        div[data-testid="stRadio"] label,
        div[data-testid="stCaptionContainer"],
        label[data-testid="stWidgetLabel"] p,
        .stMarkdown,
        .stTextArea label,
        .stFileUploader label {
            color: var(--text);
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            justify-content: flex-end;
            gap: 0.4rem;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label {
            border: 1px solid var(--line);
            background: var(--tab-bg);
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
        }

        div[data-testid="stAlert"] {
            border-radius: 18px;
        }
    </style>
    """
for key, value in theme.items():
    theme_css = theme_css.replace(f"__{key}__", value)

st.markdown(theme_css, unsafe_allow_html=True)

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
