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


# ===========================================================
# COMPLETE VISUAL SYSTEM
# ===========================================================

st.markdown(
r"""
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

:root {
    --bg: #080a10;
    --sidebar: #0c0f18;
    --panel: #11141e;
    --panel-2: #0f121b;
    --border: rgba(255,255,255,0.075);

    --rose: #ff3d78;
    --rose-soft: #ff9dbb;
    --rose-dim: rgba(255,61,120,0.20);

    --text: #f4f5f8;
    --muted: #9aa1ae;
    --muted-2: #747b88;

    --warning: #f7c14a;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

.stApp {
    background:
        radial-gradient(
            circle at 55% 8%,
            rgba(255, 40, 100, 0.025),
            transparent 28%
        ),
        #080a10 !important;
    color: var(--text);
}

.main {
    background: transparent !important;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 28px !important;
    padding-bottom: 110px !important;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    width: 270px !important;
    min-width: 270px !important;
    max-width: 270px !important;

    background: #0b0e17 !important;
    border-right: 1px solid rgba(255,255,255,0.075) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 18px 18px 18px !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text);
}


/* Sidebar top menu */

.sidebar-menu {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-top: -3px;
    margin-bottom: 16px;
}

.menu-box {
    width: 39px;
    height: 39px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    background: #101521;
    box-shadow: 0 5px 15px rgba(0,0,0,0.18);
}

.menu-label {
    font-size: 6px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #a7adba;
    margin-bottom: 2px;
}

.menu-close {
    font-size: 22px;
    line-height: 16px;
    color: #e2e5eb;
}


/* Sidebar brand */

.brand-wrap {
    text-align: center;
    padding: 0 0 19px 0;
}

.brand-icon {
    width: 51px;
    height: 51px;

    margin: 0 auto 11px auto;

    border: 1px solid rgba(255,61,120,0.80);
    border-radius: 16px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        radial-gradient(
            circle,
            rgba(255,61,120,0.08),
            rgba(255,61,120,0.015) 70%
        );

    box-shadow:
        0 0 12px rgba(255,61,120,0.18),
        0 0 26px rgba(255,61,120,0.07);

    animation: sidebar-breathe 3.3s ease-in-out infinite;
}

.brand-title {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: -0.2px;
    color: #f0f1f5;
    margin-bottom: 5px;
}

.brand-caption {
    font-size: 10px;
    font-weight: 500;
    color: #b5bac5;
}


/* Sidebar section */

.sidebar-heading {
    font-size: 15px;
    font-weight: 700;
    margin: 0 0 13px 0;
    color: #eef0f4;
}

.sidebar-empty {
    font-size: 12px;
    color: #858c99;
    margin-bottom: 18px;
}


/* Sidebar dividers */

.sidebar-divider {
    height: 1px;
    width: 100%;
    background: rgba(255,255,255,0.08);
    margin: 0 0 20px 0;
}


/* ==========================================================
   STREAMLIT SELECTBOX OVERRIDES
   ========================================================== */

section[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 8px;
}

section[data-testid="stSidebar"] .stSelectbox label {
    color: #f2f3f5 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    margin-bottom: 5px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #111722 !important;
    border: 1px solid rgba(255,255,255,0.065) !important;
    border-radius: 6px !important;
    min-height: 36px !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
    border-color: rgba(255,255,255,0.11) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #f1f3f6 !important;
    font-size: 11px !important;
}

section[data-testid="stSidebar"] svg {
    fill: #e6e8ed !important;
}


/* ==========================================================
   APPEARANCE
   ========================================================== */

.appearance-title {
    font-size: 14px;
    font-weight: 700;
    color: #f0f2f5;
    margin-top: 14px;
    margin-bottom: 10px;
}

.appearance-status {
    font-size: 11px;
    color: #8e95a2;
    margin-top: 7px;
}


/* ==========================================================
   SIDEBAR BUTTONS
   ========================================================== */

section[data-testid="stSidebar"] .stButton {
    margin: 0 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    min-height: 36px !important;

    background: #111722 !important;
    color: #eef0f4 !important;

    border: 1px solid rgba(255,255,255,0.075) !important;
    border-radius: 7px !important;

    font-size: 11px !important;
    font-weight: 600 !important;

    transition:
        border-color .2s ease,
        background .2s ease,
        box-shadow .2s ease;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #141925 !important;
    border-color: rgba(255,61,120,0.25) !important;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero-container {
    width: 830px;
    max-width: calc(100vw - 350px);

    margin: 0 auto 21px auto;

    padding: 22px 30px 28px 30px;

    background: #11141e;

    border: 1px solid rgba(255,61,120,0.75);
    border-radius: 23px;

    text-align: center;

    box-shadow:
        0 0 7px rgba(255,61,120,0.10),
        0 0 24px rgba(255,61,120,0.055),
        0 15px 35px rgba(0,0,0,0.35);

    animation: hero-breathe 3.6s ease-in-out infinite;
}

.hero-icon {
    width: 56px;
    height: 56px;

    margin: 0 auto 11px auto;

    border-radius: 17px;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 1px solid rgba(255,61,120,0.82);

    background:
        radial-gradient(
            circle,
            rgba(255,61,120,0.09),
            rgba(255,61,120,0.015) 75%
        );

    box-shadow:
        0 0 12px rgba(255,61,120,0.16),
        0 0 28px rgba(255,61,120,0.07);

    animation: icon-breathe 3s ease-in-out infinite;
}

.hero-title {
    color: #f4f5f8;
    font-weight: 800;
    font-size: 31px;
    line-height: 1.2;

    margin: 0;

    letter-spacing: -0.8px;
}

.hero-description {
    color: #9ca3af;

    margin: 10px 0 14px 0;

    font-size: 13px;
    line-height: 1.5;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 7px 14px;

    color: #ff3d78;

    font-size: 10px;
    font-weight: 700;

    border: 1px solid rgba(255,61,120,0.72);
    border-radius: 999px;

    background: rgba(255,61,120,0.02);

    box-shadow:
        0 0 8px rgba(255,61,120,0.09);

    animation: badge-breathe 2.9s ease-in-out infinite;
}


/* ==========================================================
   QUICK QUESTIONS
   ========================================================== */

.quick-label {
    text-align: center;

    color: #9da3ae;

    font-size: 11px;
    font-weight: 500;

    margin: 5px 0 9px 0;
}


/* Main-area Streamlit buttons */

div[data-testid="column"] .stButton {
    margin-bottom: 9px;
}

div[data-testid="column"] .stButton > button {
    min-height: 37px !important;

    background: #10141e !important;
    color: #e9ebef !important;

    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 11px !important;

    font-size: 11px !important;
    font-weight: 600 !important;

    box-shadow: none !important;

    transition:
        background .2s ease,
        border-color .2s ease,
        box-shadow .2s ease,
        transform .15s ease;
}

div[data-testid="column"] .stButton > button:hover {
    background: #121722 !important;

    border-color: rgba(255,61,120,0.22) !important;

    box-shadow:
        0 0 10px rgba(255,61,120,0.035) !important;

    transform: translateY(-1px);
}


/* ==========================================================
   INFORMATION BOXES
   ========================================================== */

.notice-box {
    width: 830px;
    max-width: calc(100vw - 350px);

    margin: 17px auto 9px auto;

    padding: 9px 15px;

    background: rgba(255,255,255,0.025);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 8px;

    color: #8f96a3;

    font-size: 10px;
    line-height: 1.45;

    text-align: left;
}

.notice-box b {
    color: #e6e8ec;
}


.disclaimer-box {
    width: 830px;
    max-width: calc(100vw - 350px);

    margin: 0 auto 20px auto;

    padding: 9px 15px;

    background: rgba(245,158,11,0.035);

    border: 1px solid rgba(245,158,11,0.24);

    border-radius: 8px;

    color: #c8a34f;

    font-size: 10px;
    line-height: 1.45;

    text-align: left;
}

.disclaimer-box b {
    color: #eec75e;
}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {
    width: 830px;
    max-width: calc(100vw - 350px);
    margin: 0 auto;
}

[data-testid="stFileUploaderDropzone"] {
    background: #10141e !important;
    border: 1px dashed rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploader"] small {
    color: #8f96a3 !important;
}


/* ==========================================================
   CHAT MESSAGES
   ========================================================== */

[data-testid="stChatMessage"] {
    width: 830px;
    max-width: calc(100vw - 350px);

    margin-left: auto;
    margin-right: auto;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    font-size: 13px;
}


/* ==========================================================
   CHAT INPUT — REFERENCE LOOK
   ========================================================== */

[data-testid="stChatInput"] {
    width: 830px !important;
    max-width: calc(100vw - 350px) !important;

    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stChatInput"] > div {
    background: #11151f !important;

    border: 1px solid rgba(255,61,120,0.75) !important;

    border-radius: 16px !important;

    box-shadow:
        0 0 8px rgba(255,61,120,0.10),
        0 0 22px rgba(255,61,120,0.045);

    animation: input-breathe 3.8s ease-in-out infinite;
}

[data-testid="stChatInput"] textarea {
    color: #e8eaf0 !important;
    font-size: 12px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #9097a4 !important;
}

[data-testid="stChatInput"] button {
    color: #e9ebf0 !important;
}


/* ==========================================================
   REMOVE UNNECESSARY STREAMLIT CHROME
   ========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}


/* ==========================================================
   NEON BREATHING
   ========================================================== */

@keyframes hero-breathe {

    0%, 100% {
        border-color: rgba(255,61,120,0.65);

        box-shadow:
            0 0 7px rgba(255,61,120,0.08),
            0 0 24px rgba(255,61,120,0.035),
            0 15px 35px rgba(0,0,0,0.35);
    }

    50% {
        border-color: rgba(255,61,120,0.98);

        box-shadow:
            0 0 10px rgba(255,61,120,0.19),
            0 0 34px rgba(255,61,120,0.10),
            0 15px 35px rgba(0,0,0,0.35);
    }
}


@keyframes icon-breathe {

    0%, 100% {
        border-color: rgba(255,61,120,0.70);

        box-shadow:
            0 0 10px rgba(255,61,120,0.13),
            0 0 23px rgba(255,61,120,0.05);
    }

    50% {
        border-color: rgba(255,61,120,1);

        box-shadow:
            0 0 13px rgba(255,61,120,0.28),
            0 0 31px rgba(255,61,120,0.12);
    }
}


@keyframes badge-breathe {

    0%, 100% {
        border-color: rgba(255,61,120,0.62);

        box-shadow:
            0 0 6px rgba(255,61,120,0.05);
    }

    50% {
        border-color: rgba(255,61,120,1);

        box-shadow:
            0 0 10px rgba(255,61,120,0.17),
            0 0 19px rgba(255,61,120,0.07);
    }
}


@keyframes input-breathe {

    0%, 100% {
        border-color: rgba(255,61,120,0.63);

        box-shadow:
            0 0 7px rgba(255,61,120,0.07);
    }

    50% {
        border-color: rgba(255,61,120,0.97);

        box-shadow:
            0 0 11px rgba(255,61,120,0.16),
            0 0 26px rgba(255,61,120,0.07);
    }
}


@keyframes sidebar-breathe {

    0%, 100% {
        box-shadow:
            0 0 9px rgba(255,61,120,0.12),
            0 0 21px rgba(255,61,120,0.04);
    }

    50% {
        box-shadow:
            0 0 14px rgba(255,61,120,0.23),
            0 0 30px rgba(255,61,120,0.08);
    }
}


/* ==========================================================
   REDUCED MOTION
   ========================================================== */

@media (prefers-reduced-motion: reduce) {

    .hero-container,
    .hero-icon,
    .hero-badge,
    .brand-icon,
    [data-testid="stChatInput"] > div {
        animation: none !important;
    }

}


/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media (max-width: 900px) {

    .hero-container,
    .notice-box,
    .disclaimer-box,
    [data-testid="stFileUploader"],
    [data-testid="stChatMessage"],
    [data-testid="stChatInput"] {
        width: calc(100vw - 320px) !important;
        max-width: none !important;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ===========================================================
# API CLIENTS
# ===========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GEMINI_API_KEY or not GROQ_API_KEY:
    st.error(
        "❌ API keys missing. Please configure "
        "GEMINI_API_KEY and GROQ_API_KEY."
    )
    st.stop()


@st.cache_resource(show_spinner=False)
def init_ai_clients():

    g_client = genai.Client(api_key=GEMINI_API_KEY)
    groq_client = Groq(api_key=GROQ_API_KEY)

    return g_client, groq_client


gemini_client, groq_client = init_ai_clients()

GEMINI_MODEL = "gemini-2.5-flash"
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
                <div class="menu-close">×</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="brand-wrap">

            <div class="brand-icon">

                <svg width="30" height="30"
                     viewBox="0 0 50 50"
                     fill="none"
                     xmlns="http://www.w3.org/2000/svg">

                    <path
                        d="M16 25V14
                           C16 9.6 19.6 6 24 6
                           C28.4 6 32 9.6 32 14V29
                           C32 35.1 36.9 40 43 40"
                        stroke="#a87aff"
                        stroke-width="2.8"
                        stroke-linecap="round"
                    />

                    <path
                        d="M16 20
                           C12.1 20 9 23.1 9 27
                           C9 30.9 12.1 34 16 34"
                        stroke="#ff3d78"
                        stroke-width="2.8"
                        stroke-linecap="round"
                    />

                    <circle
                        cx="16"
                        cy="25"
                        r="4"
                        stroke="#50c7ff"
                        stroke-width="2.2"
                    />

                    <circle
                        cx="43"
                        cy="40"
                        r="3"
                        stroke="#ff3d78"
                        stroke-width="2"
                    />

                </svg>

            </div>

            <div class="brand-title">AI HEALTHCARE</div>

            <div class="brand-caption">
                Smart health information assistant
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-heading">💬 Chat History</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.messages:

        st.markdown(
            '<div class="sidebar-empty">No previous messages yet.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.session_state.app_mode = st.selectbox(
        "Assistant Mode",
        [
            "AI Medical Analyst",
            "Symptom Checker",
            "Nutrition Coach"
        ],
        index=[
            "AI Medical Analyst",
            "Symptom Checker",
            "Nutrition Coach"
        ].index(st.session_state.app_mode)
    )

    st.session_state.response_style = st.selectbox(
        "Response Style",
        [
            "Balanced",
            "Concise",
            "Detailed"
        ],
        index=[
            "Balanced",
            "Concise",
            "Detailed"
        ].index(st.session_state.response_style)
    )

    st.session_state.accent = st.selectbox(
        "Accent",
        [
            "Rose",
            "Blue",
            "Emerald"
        ],
        index=[
            "Rose",
            "Blue",
            "Emerald"
        ].index(st.session_state.accent)
    )

    st.markdown(
        '<div class="appearance-title">🎨 Appearance</div>',
        unsafe_allow_html=True
    )

    appearance_col_1, appearance_col_2 = st.columns(2)

    with appearance_col_1:
        st.button("☀️ Light", use_container_width=True)

    with appearance_col_2:
        st.button("🌙 Dark", use_container_width=True)

    st.markdown(
        '<div class="appearance-status">Active theme: Dark</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()


# ===========================================================
# HERO
# ===========================================================

st.markdown(
    """
    <div class="hero-container">

        <div class="hero-icon">

            <svg width="33" height="33"
                 viewBox="0 0 50 50"
                 fill="none"
                 xmlns="http://www.w3.org/2000/svg">

                <path
                    d="M16 25V14
                       C16 9.6 19.6 6 24 6
                       C28.4 6 32 9.6 32 14V29
                       C32 35.1 36.9 40 43 40"
                    stroke="#ae7aff"
                    stroke-width="2.8"
                    stroke-linecap="round"
                />

                <path
                    d="M16 20
                       C12.1 20 9 23.1 9 27
                       C9 30.9 12.1 34 16 34"
                    stroke="#ff3d78"
                    stroke-width="2.8"
                    stroke-linecap="round"
                />

                <circle
                    cx="16"
                    cy="25"
                    r="4"
                    stroke="#54ccff"
                    stroke-width="2.2"
                />

                <circle
                    cx="43"
                    cy="40"
                    r="3"
                    stroke="#ff3d78"
                    stroke-width="2"
                />

            </svg>

        </div>

        <div class="hero-title">
            AI Healthcare Assistant
        </div>

        <div class="hero-description">
            Understand medical reports and health information in simple language.
        </div>

        <div class="hero-badge">
            AI Medical Analyst
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ===========================================================
# QUICK QUESTIONS
# ===========================================================

st.markdown(
    '<div class="quick-label">Try a quick question</div>',
    unsafe_allow_html=True
)

q1, q2 = st.columns(2, gap="small")

with q1:

    if st.button(
        "📄 Blood test basics",
        use_container_width=True
    ):

        st.session_state.messages.append(
            {
                "role": "user",
                "content":
                    "Can you explain the basics of a standard blood test?"
            }
        )

        st.rerun()

    if st.button(
        "🔍 Causes of fatigue",
        use_container_width=True
    ):

        st.session_state.messages.append(
            {
                "role": "user",
                "content":
                    "What are the common causes of chronic fatigue?"
            }
        )

        st.rerun()


with q2:

    if st.button(
        "🥗 Healthy diet",
        use_container_width=True
    ):

        st.session_state.messages.append(
            {
                "role": "user",
                "content":
                    "Give me tips for maintaining a healthy balanced diet."
            }
        )

        st.rerun()

    if st.button(
        "💊 Medication side effects",
        use_container_width=True
    ):

        st.session_state.messages.append(
            {
                "role": "user",
                "content":
                    "How can I check or manage common medication side effects?"
            }
        )

        st.rerun()


# ===========================================================
# INFORMATION BOXES
# ===========================================================

st.markdown(
    """
    <div class="notice-box">
        🔒 <b>Ephemeral Data Processing</b>
        — any medical document you attach is deleted automatically
        within 1 hour. Your chat history stays saved in this conversation.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="disclaimer-box">
        ⚠️ <b>Important:</b>
        This AI Healthcare Assistant provides general informational
        support only. It does not diagnose medical conditions,
        prescribe treatment, or replace advice from a qualified
        healthcare professional.
    </div>
    """,
    unsafe_allow_html=True
)


# ===========================================================
# MEDICAL REPORT UPLOAD
# ===========================================================

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ],
    label_visibility="collapsed"
)


# ===========================================================
# CHAT HISTORY
# ===========================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])


# ===========================================================
# CHAT INPUT
# ===========================================================

user_input = st.chat_input(
    "Ask anything about health or attach a medical report..."
)


# ===========================================================
# AI RESPONSE
# ===========================================================

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                completion = groq_client.chat.completions.create(

                    model=GROQ_MODEL,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful healthcare assistant. "
                                "Provide safe, structured guidance. "
                                "Do not diagnose conditions or prescribe "
                                "medication. Explain medical concepts "
                                "clearly in simple language."
                            )
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],

                    temperature=0.2
                )

                answer = completion.choices[0].message.content

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

    except Exception as e:

        st.error(f"An error occurred: {e}")

