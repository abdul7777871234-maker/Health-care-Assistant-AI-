# -*- coding: utf-8 -*-

import os
import streamlit as st
from google import genai
from google.genai import types
from groq import Groq

# ===========================================================
# PAGE CONFIGURATION
# ===========================================================

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================================
# SESSION STATE
# ===========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "AI Medical Analyst"

if "response_style" not in st.session_state:
    st.session_state.response_style = "Balanced"

if "accent" not in st.session_state:
    st.session_state.accent = "Rose"

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# ===========================================================
# THEME & ACCENT CONFIGURATION MAPS
# ===========================================================

ACCENTS = {
    "Rose": {"primary": "#ff3d78", "soft": "#ff9dbb", "dim": "rgba(255,61,120,0.20)"},
    "Blue": {"primary": "#3d82ff", "soft": "#9dbbff", "dim": "rgba(61,130,255,0.20)"},
    "Emerald": {"primary": "#10b981", "soft": "#6ee7b7", "dim": "rgba(16,185,129,0.20)"},
    "Purple": {"primary": "#a855f7", "soft": "#d8b4fe", "dim": "rgba(168,85,247,0.20)"},
    "Amber": {"primary": "#f59e0b", "soft": "#fcd34d", "dim": "rgba(245,158,11,0.20)"}
}

current_accent = ACCENTS.get(st.session_state.accent, ACCENTS["Rose"])

if st.session_state.theme == "Light":
    bg_color = "#f8fafc"
    sidebar_color = "#f1f5f9"
    panel_color = "#ffffff"
    text_color = "#0f172a"
    muted_color = "#475569"
    border_color = "rgba(15,23,42,0.1)"
else:
    bg_color = "#080a10"
    sidebar_color = "#0b0e17"
    panel_color = "#11141e"
    text_color = "#f4f5f8"
    muted_color = "#9aa1ae"
    border_color = "rgba(255,255,255,0.075)"

# ===========================================================
# COMPLETE VISUAL SYSTEM
# ===========================================================

st.markdown(
f"""
<style>

:root {{
    --bg: {bg_color};
    --sidebar: {sidebar_color};
    --panel: {panel_color};
    --border: {border_color};
    --accent: {current_accent["primary"]};
    --accent-soft: {current_accent["soft"]};
    --accent-dim: {current_accent["dim"]};
    --text: {text_color};
    --muted: {muted_color};
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
}}

.stApp {{
    background: var(--bg) !important;
    color: var(--text);
}}

.main {{
    background: transparent !important;
}}

.block-container {{
    max-width: 1180px !important;
    padding-top: 28px !important;
    padding-bottom: 110px !important;
}}

section[data-testid="stSidebar"] {{
    width: 270px !important;
    min-width: 270px !important;
    max-width: 270px !important;
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
}}

section[data-testid="stSidebar"] > div {{
    padding: 0 18px 18px 18px !important;
}}

section[data-testid="stSidebar"] * {{
    color: var(--text) !important;
}}

.sidebar-menu {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-top: -3px;
    margin-bottom: 16px;
}}

.menu-box {{
    width: 39px;
    height: 39px;
    border: 1px solid var(--border);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: var(--panel);
}}

.menu-label {{
    font-size: 6px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--muted);
    margin-bottom: 2px;
}}

.menu-close {{
    font-size: 22px;
    line-height: 16px;
    color: var(--text);
}}

.brand-wrap {{
    text-align: center;
    padding: 0 0 19px 0;
}}

.brand-icon {{
    width: 51px;
    height: 51px;
    margin: 0 auto 11px auto;
    border: 1px solid var(--accent);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-dim);
}}

.brand-title {{
    font-size: 14px;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 5px;
}}

.brand-caption {{
    font-size: 10px;
    font-weight: 500;
    color: var(--muted);
}}

.sidebar-heading {{
    font-size: 15px;
    font-weight: 700;
    margin: 0 0 13px 0;
    color: var(--text);
}}

.sidebar-empty {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 18px;
}}

.sidebar-divider {{
    height: 1px;
    width: 100%;
    background: var(--border);
    margin: 0 0 20px 0;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
    min-height: 36px !important;
    background: var(--panel) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}}

.hero-container {{
    width: 830px;
    max-width: calc(100vw - 350px);
    margin: 0 auto 21px auto;
    padding: 22px 30px 28px 30px;
    background: var(--panel);
    border: 1px solid var(--accent);
    border-radius: 23px;
    text-align: center;
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}}

.hero-icon {{
    width: 56px;
    height: 56px;
    margin: 0 auto 11px auto;
    border-radius: 17px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--accent);
    background: var(--accent-dim);
}}

.hero-title {{
    color: var(--text);
    font-weight: 800;
    font-size: 31px;
    line-height: 1.2;
    margin: 0;
    letter-spacing: -0.8px;
}}

.hero-description {{
    color: var(--muted);
    margin: 10px 0 14px 0;
    font-size: 13px;
    line-height: 1.5;
}}

.hero-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 7px 14px;
    color: var(--accent);
    font-size: 10px;
    font-weight: 700;
    border: 1px solid var(--accent);
    border-radius: 999px;
    background: var(--accent-dim);
}}

.quick-label {{
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    font-weight: 500;
    margin: 5px 0 9px 0;
}}

div[data-testid="column"] .stButton > button {{
    min-height: 37px !important;
    background: var(--panel) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 11px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}}

.notice-box {{
    width: 830px;
    max-width: calc(100vw - 350px);
    margin: 17px auto 9px auto;
    padding: 9px 15px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--muted);
    font-size: 10px;
    text-align: left;
}}

.disclaimer-box {{
    width: 830px;
    max-width: calc(100vw - 350px);
    margin: 0 auto 20px auto;
    padding: 9px 15px;
    background: rgba(245,158,11,0.05);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 8px;
    color: #d97706;
    font-size: 10px;
    text-align: left;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: var(--panel) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 10px !important;
}}

[data-testid="stChatInput"] > div {{
    background: var(--panel) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 16px !important;
}}

#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    visibility: hidden !important;
    display: none !important;
}}

</style>
"""
,
    unsafe_allow_html=True
)

# ===========================================================
# API CLIENTS
# ===========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GEMINI_API_KEY or not GROQ_API_KEY:
    st.error("❌ API keys missing. Please configure GEMINI_API_KEY and GROQ_API_KEY.")
    st.stop()

@st.cache_resource(show_spinner=False)
def init_ai_clients():
    g_client = genai.Client(api_key=GEMINI_API_KEY)
    groq_client = Groq(api_key=GROQ_API_KEY)
    return g_client, groq_client

gemini_client, groq_client = init_ai_clients()
GROQ_MODEL = "openai/gpt-oss-120b"

# ===========================================================
# SIDEBAR
# ===========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-menu">
            <div class="menu-box">
                <div class="menu-label">MENU</div>
                <div class="menu-close">«</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="brand-wrap">
            <div class="brand-icon">
                <svg width="30" height="30" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 25V14C16 9.6 19.6 6 24 6C28.4 6 32 9.6 32 14V29C32 35.1 36.9 40 43 40" stroke="{current_accent["soft"]}" stroke-width="2.8" stroke-linecap="round"/>
                    <path d="M16 20C12.1 20 9 23.1 9 27C9 30.9 12.1 34 16 34" stroke="{current_accent["primary"]}" stroke-width="2.8" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="brand-title">AI HEALTHCARE</div>
            <div class="brand-caption">Smart health information assistant</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-heading">💬 Chat History</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown('<div class="sidebar-empty">No previous messages yet.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.session_state.app_mode = st.selectbox("Assistant Mode", ["AI Medical Analyst", "Symptom Checker", "Nutrition Coach"])
    st.session_state.response_style = st.selectbox("Response Style", ["Balanced", "Concise", "Detailed"])
    st.session_state.accent = st.selectbox("Accent", ["Rose", "Blue", "Emerald", "Purple", "Amber"])

    st.markdown('<div class="appearance-title">🎨 Appearance</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "Light"
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "Dark"
            st.rerun()

    st.markdown(f'<div class="appearance-status">Active theme: {st.session_state.theme}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ===========================================================
# HERO SECTION
# ===========================================================

st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-icon">
            <svg width="33" height="33" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 25V14C16 9.6 19.6 6 24 6C28.4 6 32 9.6 32 14V29C32 35.1 36.9 40 43 40" stroke="{current_accent["soft"]}" stroke-width="2.8" stroke-linecap="round"/>
                <path d="M16 20C12.1 20 9 23.1 9 27C9 30.9 12.1 34 16 34" stroke="{current_accent["primary"]}" stroke-width="2.8" stroke-linecap="round"/>
            </svg>
        </div>
        <div class="hero-title">AI Healthcare Assistant</div>
        <div class="hero-description">Understand medical reports and health information in simple language.</div>
        <div class="hero-badge">{st.session_state.app_mode}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ===========================================================
# QUICK QUESTIONS
# ===========================================================

st.markdown('<div class="quick-label">Try a quick question</div>', unsafe_allow_html=True)
q1, q2 = st.columns(2, gap="small")

with q1:
    if st.button("📄 Blood test basics", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Can you explain the basics of a standard blood test?"})
        st.rerun()
    if st.button("🔍 Causes of fatigue", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What are the common causes of chronic fatigue?"})
        st.rerun()

with q2:
    if st.button("🥗 Healthy diet", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Give me tips for maintaining a healthy balanced diet."})
        st.rerun()
    if st.button("💊 Medication side effects", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "How can I check or manage common medication side effects?"})
        st.rerun()

# ===========================================================
# INFO & UPLOADER
# ===========================================================

st.markdown(
    """
    <div class="notice-box">
        🔒 <b>Ephemeral Data Processing</b> — any medical document you attach is deleted automatically within 1 hour.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="disclaimer-box">
        ⚠️ <b>Important:</b> General informational support only. Does not replace professional medical advice.
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload Medical Report", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

# ===========================================================
# CHAT LOGIC
# ===========================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask anything about health or attach a medical report...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                completion = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful healthcare assistant. Provide safe, structured guidance."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.2
                )
                answer = completion.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"An error occurred: {e}")
