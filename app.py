# -*- coding: utf-8 -*-

import os
import streamlit as st

from google import genai
from groq import Groq


# ===========================================================
# PAGE CONFIGURATION
# ===========================================================

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
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
# ACCENTS
# ===========================================================

ACCENTS = {
    "Rose": {
        "primary": "#ff3d78",
        "soft": "#ff9fbd",
        "rgb": "255,61,120",
    },
    "Blue": {
        "primary": "#3d82ff",
        "soft": "#9fbeff",
        "rgb": "61,130,255",
    },
    "Cyan": {
        "primary": "#22d3ee",
        "soft": "#a5f3fc",
        "rgb": "34,211,238",
    },
    "Violet": {
        "primary": "#a855f7",
        "soft": "#d8b4fe",
        "rgb": "168,85,247",
    },
    "Emerald": {
        "primary": "#10b981",
        "soft": "#6ee7b7",
        "rgb": "16,185,129",
    },
    "Amber": {
        "primary": "#f59e0b",
        "soft": "#fcd34d",
        "rgb": "245,158,11",
    },
}

accent = ACCENTS[st.session_state.accent]

ACCENT = accent["primary"]
ACCENT_SOFT = accent["soft"]
ACCENT_RGB = accent["rgb"]


# ===========================================================
# THEME
# ===========================================================

if st.session_state.theme == "Light":

    BG = "#f4f6fb"
    SIDEBAR = "#ffffff"
    PANEL = "#ffffff"
    PANEL_ALT = "#f8fafc"

    TEXT = "#111827"
    MUTED = "#667085"

    BORDER = "rgba(17,24,39,0.10)"

else:

    BG = "#080a10"
    SIDEBAR = "#0b0e17"
    PANEL = "#11141e"
    PANEL_ALT = "#0f121b"

    TEXT = "#f3f4f6"
    MUTED = "#9ca3af"

    BORDER = "rgba(255,255,255,0.08)"


# ===========================================================
# COMPLETE CSS
# ===========================================================

st.markdown(
    f"""
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {{
    background: {BG} !important;
}}

.stApp {{
    background: {BG} !important;
    color: {TEXT} !important;
}}

.main {{
    background: transparent !important;
}}

.block-container {{
    max-width: none !important;

    padding-top: 27px !important;
    padding-bottom: 105px !important;
    padding-left: 22px !important;
    padding-right: 22px !important;
}}


/* ==========================================================
   KEEP NATIVE STREAMLIT SIDEBAR ARROW
   ========================================================== */

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

#MainMenu {{
    visibility: hidden !important;
}}

footer {{
    visibility: hidden !important;
}}

[data-testid="stToolbar"] {{
    visibility: hidden !important;
}}

[data-testid="stDecoration"] {{
    visibility: hidden !important;
}}

/*
   IMPORTANT:
   header itself is NOT display:none.
   Therefore Streamlit's native sidebar collapse arrow
   remains available.
*/

[data-testid="collapsedControl"] button {{
    color: {MUTED} !important;
}}

[data-testid="collapsedControl"] button:hover {{
    color: {ACCENT} !important;
}}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {{
    width: 270px !important;
    min-width: 270px !important;
    max-width: 270px !important;

    background: {SIDEBAR} !important;

    border-right:
        1px solid {BORDER} !important;
}}

section[data-testid="stSidebar"] > div {{
    padding:
        10px 18px 18px 18px !important;
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT};
}}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.sidebar-spacer {{
    height: 24px;
}}

.brand-wrap {{
    text-align: center;

    padding:
        4px 0 19px 0;
}}

.brand-icon {{
    width: 51px;
    height: 51px;

    margin:
        0 auto 11px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border:
        1px solid {ACCENT};

    border-radius: 16px;

    background:
        rgba({ACCENT_RGB}, 0.055);

    box-shadow:
        0 0 11px rgba({ACCENT_RGB}, 0.17),
        0 0 27px rgba({ACCENT_RGB}, 0.06);

    animation:
        sidebar-breathe 3.3s ease-in-out infinite;
}}

.brand-title {{
    font-size: 14px;
    font-weight: 800;

    letter-spacing: 0.1px;

    margin-bottom: 5px;
}}

.brand-caption {{
    color: {MUTED} !important;

    font-size: 10px;
    font-weight: 500;
}}


/* ==========================================================
   SIDEBAR DIVIDERS
   ========================================================== */

.sidebar-divider {{
    height: 1px;
    width: 100%;

    background: {BORDER};

    margin:
        0 0 20px 0;
}}


/* ==========================================================
   CHAT HISTORY
   ========================================================== */

.sidebar-heading {{
    color: {TEXT};

    font-size: 14px;
    font-weight: 700;

    margin-bottom: 13px;
}}

.sidebar-empty {{
    color: {MUTED} !important;

    font-size: 11px;

    margin-bottom: 19px;
}}


/* ==========================================================
   SELECT BOXES
   ========================================================== */

section[data-testid="stSidebar"] .stSelectbox {{
    margin-bottom: 7px !important;
}}

section[data-testid="stSidebar"] .stSelectbox label {{
    color: {TEXT} !important;

    font-size: 11px !important;
    font-weight: 700 !important;

    margin-bottom: 5px !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    min-height: 36px !important;

    background: {PANEL_ALT} !important;

    border:
        1px solid {BORDER} !important;

    border-radius: 7px !important;

    box-shadow: none !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
    border-color:
        rgba({ACCENT_RGB}, 0.40) !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: {TEXT} !important;

    font-size: 11px !important;
}}

section[data-testid="stSidebar"] svg {{
    fill: {TEXT} !important;
}}


/* ==========================================================
   APPEARANCE
   ========================================================== */

.appearance-title {{
    color: {TEXT};

    font-size: 14px;
    font-weight: 700;

    margin:
        13px 0 9px 0;
}}

.appearance-status {{
    color: {MUTED} !important;

    font-size: 10px;

    margin-top: 7px;
}}


/* ==========================================================
   SIDEBAR BUTTONS
   ========================================================== */

section[data-testid="stSidebar"] .stButton {{
    margin: 0 !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
    min-height: 36px !important;

    background: {PANEL_ALT} !important;

    color: {TEXT} !important;

    border:
        1px solid {BORDER} !important;

    border-radius: 7px !important;

    font-size: 11px !important;
    font-weight: 600 !important;

    box-shadow: none !important;

    transition:
        background .18s ease,
        border-color .18s ease,
        box-shadow .18s ease;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {PANEL} !important;

    border-color:
        rgba({ACCENT_RGB}, 0.40) !important;

    box-shadow:
        0 0 10px rgba({ACCENT_RGB}, 0.05) !important;
}}


/* ==========================================================
   MAIN CONTENT WIDTH
   ========================================================== */

.reference-width {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto;
}}


/* ==========================================================
   HERO
   ========================================================== */

.hero {{
    width: 830px;
    max-width: calc(100vw - 340px);

    min-height: 277px;

    margin:
        0 auto 20px auto;

    padding:
        23px 30px 27px 30px;

    box-sizing: border-box;

    display: flex;
    flex-direction: column;
    align-items: center;

    text-align: center;

    background:
        {PANEL};

    border:
        1px solid {ACCENT};

    border-radius: 23px;

    box-shadow:
        0 0 8px rgba({ACCENT_RGB}, 0.10),
        0 0 30px rgba({ACCENT_RGB}, 0.04),
        0 14px 30px rgba(0,0,0,0.20);

    animation:
        hero-breathe 3.6s ease-in-out infinite;
}}

.hero-icon {{
    width: 56px;
    height: 56px;

    margin-bottom: 12px;

    display: flex;
    align-items: center;
    justify-content: center;

    border:
        1px solid {ACCENT};

    border-radius: 17px;

    background:
        rgba({ACCENT_RGB}, 0.055);

    box-shadow:
        0 0 12px rgba({ACCENT_RGB}, 0.17),
        0 0 28px rgba({ACCENT_RGB}, 0.06);

    animation:
        icon-breathe 3.1s ease-in-out infinite;
}}

.hero-title {{
    color: {ACCENT_SOFT};

    font-size: 35px;
    line-height: 1.25;

    font-weight: 800;

    letter-spacing: -1px;

    margin: 0;
}}

.hero-description {{
    color: {MUTED};

    font-size: 12px;
    line-height: 1.5;

    margin:
        13px 0 14px 0;
}}

.hero-badge {{
    display: inline-flex;

    align-items: center;
    justify-content: center;

    padding:
        7px 14px;

    border:
        1px solid {ACCENT};

    border-radius: 999px;

    color: {ACCENT};

    background:
        rgba({ACCENT_RGB}, 0.018);

    font-size: 10px;
    font-weight: 700;

    animation:
        badge-breathe 2.9s ease-in-out infinite;
}}


/* ==========================================================
   QUICK QUESTIONS
   ========================================================== */

.quick-label {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto 9px auto;

    text-align: center;

    color: {MUTED};

    font-size: 11px;
}}

.quick-row {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto;
}}

.quick-row .stButton > button {{
    min-height: 37px !important;

    background: {PANEL} !important;

    color: {TEXT} !important;

    border:
        1px solid {BORDER} !important;

    border-radius: 11px !important;

    font-size: 11px !important;
    font-weight: 600 !important;

    box-shadow: none !important;

    transition:
        background .18s ease,
        border-color .18s ease,
        transform .15s ease;
}}

.quick-row .stButton > button:hover {{
    background: {PANEL_ALT} !important;

    border-color:
        rgba({ACCENT_RGB}, 0.38) !important;

    transform:
        translateY(-1px);
}}


/* ==========================================================
   INFO BOX
   ========================================================== */

.notice {{
    width: 702px;
    max-width: calc(100vw - 420px);

    margin:
        14px auto 9px auto;

    padding:
        9px 14px;

    box-sizing: border-box;

    background:
        {PANEL};

    color:
        {MUTED};

    border:
        1px solid {BORDER};

    border-radius: 8px;

    font-size: 9px;
    line-height: 1.5;
}}

.notice b {{
    color: {TEXT};
}}


/* ==========================================================
   DISCLAIMER
   ========================================================== */

.disclaimer {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto 14px auto;

    padding:
        9px 14px;

    box-sizing: border-box;

    background:
        rgba(245,158,11,0.04);

    color:
        #c8a54e;

    border:
        1px solid rgba(245,158,11,0.25);

    border-radius: 8px;

    font-size: 9px;
    line-height: 1.5;
}}

.disclaimer b {{
    color: #efc85c;
}}


/* ==========================================================
   FILE UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {{
    width: 830px;

    max-width:
        calc(100vw - 340px);

    margin:
        0 auto;
}}

[data-testid="stFileUploaderDropzone"] {{
    background:
        {PANEL_ALT} !important;

    border:
        1px dashed {BORDER} !important;

    border-radius:
        10px !important;
}}


/* ==========================================================
   CHAT
   ========================================================== */

[data-testid="stChatMessage"] {{
    width: 830px;

    max-width:
        calc(100vw - 340px);

    margin-left:
        auto;

    margin-right:
        auto;
}}

[data-testid="stChatInput"] {{
    width: 702px !important;

    max-width:
        calc(100vw - 420px) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;
}}

[data-testid="stChatInput"] > div {{
    min-height:
        52px !important;

    background:
        {PANEL} !important;

    border:
        1px solid {ACCENT} !important;

    border-radius:
        16px !important;

    box-shadow:
        0 0 9px rgba({ACCENT_RGB},0.09),
        0 0 25px rgba({ACCENT_RGB},0.035);

    animation:
        input-breathe 3.8s ease-in-out infinite;
}}

[data-testid="stChatInput"] textarea {{
    color:
        {TEXT} !important;

    font-size:
        11px !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color:
        {MUTED} !important;
}}


/* ==========================================================
   BREATHING NEON
   ========================================================== */

@keyframes hero-breathe {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB},0.64);

        box-shadow:
            0 0 7px rgba({ACCENT_RGB},0.07),
            0 0 24px rgba({ACCENT_RGB},0.025),
            0 14px 30px rgba(0,0,0,0.20);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB},1);

        box-shadow:
            0 0 11px rgba({ACCENT_RGB},0.20),
            0 0 35px rgba({ACCENT_RGB},0.09),
            0 14px 30px rgba(0,0,0,0.20);
    }}
}}

@keyframes icon-breathe {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB},0.66);

        box-shadow:
            0 0 9px rgba({ACCENT_RGB},0.10),
            0 0 22px rgba({ACCENT_RGB},0.035);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB},1);

        box-shadow:
            0 0 14px rgba({ACCENT_RGB},0.25),
            0 0 32px rgba({ACCENT_RGB},0.09);
    }}
}}

@keyframes badge-breathe {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB},0.62);

        box-shadow:
            0 0 6px rgba({ACCENT_RGB},0.04);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB},1);

        box-shadow:
            0 0 11px rgba({ACCENT_RGB},0.18),
            0 0 20px rgba({ACCENT_RGB},0.07);
    }}
}}

@keyframes input-breathe {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB},0.62);

        box-shadow:
            0 0 7px rgba({ACCENT_RGB},0.06);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB},0.98);

        box-shadow:
            0 0 12px rgba({ACCENT_RGB},0.17),
            0 0 27px rgba({ACCENT_RGB},0.065);
    }}
}}

@keyframes sidebar-breathe {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB},0.64);

        box-shadow:
            0 0 9px rgba({ACCENT_RGB},0.10),
            0 0 22px rgba({ACCENT_RGB},0.035);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB},1);

        box-shadow:
            0 0 14px rgba({ACCENT_RGB},0.23),
            0 0 30px rgba({ACCENT_RGB},0.08);
    }}
}}


/* ==========================================================
   REDUCED MOTION
   ========================================================== */

@media (prefers-reduced-motion: reduce) {{

    .hero,
    .hero-icon,
    .hero-badge,
    .brand-icon,
    [data-testid="stChatInput"] > div {{
        animation:
            none !important;
    }}
}}

</style>
""",
    unsafe_allow_html=True,
)


# ===========================================================
# API SETUP
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

    gemini = genai.Client(
        api_key=GEMINI_API_KEY
    )

    groq = Groq(
        api_key=GROQ_API_KEY
    )

    return gemini, groq


gemini_client, groq_client = init_ai_clients()

GROQ_MODEL = "openai/gpt-oss-120b"


# ===========================================================
# SIDEBAR
# ===========================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-spacer"></div>',
        unsafe_allow_html=True
    )

    # ---------------- BRAND ----------------

    st.markdown(
        f"""
        <div class="brand-wrap">

            <div class="brand-icon">

                <svg
                    width="30"
                    height="30"
                    viewBox="0 0 50 50"
                    fill="none"
                >

                    <path
                        d="M16 25V14
                           C16 9.6 19.6 6 24 6
                           C28.4 6 32 9.6 32 14V29
                           C32 35.1 36.9 40 43 40"
                        stroke="{ACCENT_SOFT}"
                        stroke-width="2.8"
                        stroke-linecap="round"
                    />

                    <path
                        d="M16 20
                           C12.1 20 9 23.1 9 27
                           C9 30.9 12.1 34 16 34"
                        stroke="{ACCENT}"
                        stroke-width="2.8"
                        stroke-linecap="round"
                    />

                    <circle
                        cx="16"
                        cy="25"
                        r="4"
                        stroke="#58d0ff"
                        stroke-width="2.2"
                    />

                    <circle
                        cx="43"
                        cy="40"
                        r="3"
                        stroke="{ACCENT}"
                        stroke-width="2"
                    />

                </svg>

            </div>

            <div class="brand-title">
                AI HEALTHCARE
            </div>

            <div class="brand-caption">
                Smart health information assistant
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # ---------------- CHAT HISTORY ----------------

    st.markdown(
        '<div class="sidebar-heading">💬 Chat History</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.messages:

        st.markdown(
            '<div class="sidebar-empty">No previous messages yet.</div>',
            unsafe_allow_html=True
        )

    else:

        st.caption(
            f"{len(st.session_state.messages)} messages"
        )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # ---------------- MODE ----------------

    st.session_state.app_mode = st.selectbox(
        "Assistant Mode",
        [
            "AI Medical Analyst",
            "Symptom Checker",
            "Nutrition Coach",
        ],
        index=[
            "AI Medical Analyst",
            "Symptom Checker",
            "Nutrition Coach",
        ].index(
            st.session_state.app_mode
        ),
    )

    # ---------------- RESPONSE STYLE ----------------

    st.session_state.response_style = st.selectbox(
        "Response Style",
        [
            "Balanced",
            "Concise",
            "Detailed",
        ],
        index=[
            "Balanced",
            "Concise",
            "Detailed",
        ].index(
            st.session_state.response_style
        ),
    )

    # ---------------- ACCENT ----------------

    st.session_state.accent = st.selectbox(
        "Accent",
        list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(
            st.session_state.accent
        ),
    )

    # ---------------- APPEARANCE ----------------

    st.markdown(
        '<div class="appearance-title">🎨 Appearance</div>',
        unsafe_allow_html=True
    )

    light_col, dark_col = st.columns(2)

    with light_col:

        if st.button(
            "☀️ Light",
            use_container_width=True
        ):

            if st.session_state.theme != "Light":

                st.session_state.theme = "Light"
                st.rerun()

    with dark_col:

        if st.button(
            "🌙 Dark",
            use_container_width=True
        ):

            if st.session_state.theme != "Dark":

                st.session_state.theme = "Dark"
                st.rerun()

    st.markdown(
        f"""
        <div class="appearance-status">
            Active theme: {st.session_state.theme}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="height:20px;"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # ---------------- CLEAR ----------------

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
    f"""
    <div class="hero">

        <div class="hero-icon">

            <svg
                width="33"
                height="33"
                viewBox="0 0 50 50"
                fill="none"
            >

                <path
                    d="M16 25V14
                       C16 9.6 19.6 6 24 6
                       C28.4 6 32 9.6 32 14V29
                       C32 35.1 36.9 40 43 40"
                    stroke="{ACCENT_SOFT}"
                    stroke-width="2.8"
                    stroke-linecap="round"
                />

                <path
                    d="M16 20
                       C12.1 20 9 23.1 9 27
                       C9 30.9 12.1 34 16 34"
                    stroke="{ACCENT}"
                    stroke-width="2.8"
                    stroke-linecap="round"
                />

                <circle
                    cx="16"
                    cy="25"
                    r="4"
                    stroke="#58d0ff"
                    stroke-width="2.2"
                />

                <circle
                    cx="43"
                    cy="40"
                    r="3"
                    stroke="{ACCENT}"
                    stroke-width="2"
                />

            </svg>

        </div>

        <div class="hero-title">
            AI Healthcare<br>
            Assistant
        </div>

        <div class="hero-description">
            Understand medical reports and health information in simple language.
        </div>

        <div class="hero-badge">
            AI Medical Analyst
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ===========================================================
# QUICK QUESTIONS
# ===========================================================

st.markdown(
    '<div class="quick-label">Try a quick question</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="quick-row">',
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
                    "Can you explain the basics of a standard blood test?",
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
                    "What are the common causes of chronic fatigue?",
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
                    "Give me tips for maintaining a healthy balanced diet.",
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
                    "How can I check or manage common medication side effects?",
            }
        )

        st.rerun()


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ===========================================================
# NOTICE
# ===========================================================

st.markdown(
    """
    <div class="notice">
        🔒 <b>Ephemeral Data Processing</b>
        — any medical document you attach is deleted automatically
        within 1 hour. Your chat history stays saved in this conversation.
    </div>
    """,
    unsafe_allow_html=True,
)


# ===========================================================
# DISCLAIMER
# ===========================================================

st.markdown(
    """
    <div class="disclaimer">
        ⚠️ <b>Important:</b>
        This AI Healthcare Assistant provides general informational
        support only. It does not diagnose medical conditions,
        prescribe treatment, or replace advice from a qualified
        healthcare professional.
    </div>
    """,
    unsafe_allow_html=True,
)


# ===========================================================
# FILE UPLOAD
# ===========================================================

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
    label_visibility="collapsed",
)


# ===========================================================
# CHAT HISTORY
# ===========================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )


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
            "content": user_input,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_input
        )

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
                            ),
                        },
                        {
                            "role": "user",
                            "content": user_input,
                        },
                    ],

                    temperature=0.2,
                )

                answer = (
                    completion
                    .choices[0]
                    .message
                    .content
                )

                st.markdown(
                    answer
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

    except Exception as e:

        st.error(
            f"An error occurred: {e}"
        )


# ===========================================================
# END
# ===========================================================
