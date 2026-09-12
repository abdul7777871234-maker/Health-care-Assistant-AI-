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

# Application MUST start in dark theme.
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"


# ===========================================================
# ACCENT PALETTES
# ===========================================================

ACCENTS = {
    "Rose": {
        "accent": "#ff3d78",
        "accent_soft": "#ff9dbb",
        "accent_rgb": "255,61,120",
    },

    "Blue": {
        "accent": "#4da3ff",
        "accent_soft": "#9dccff",
        "accent_rgb": "77,163,255",
    },

    "Cyan": {
        "accent": "#35d8ff",
        "accent_soft": "#9cefff",
        "accent_rgb": "53,216,255",
    },

    "Violet": {
        "accent": "#9b6cff",
        "accent_soft": "#c7b0ff",
        "accent_rgb": "155,108,255",
    },

    "Emerald": {
        "accent": "#32d296",
        "accent_soft": "#9af0ce",
        "accent_rgb": "50,210,150",
    },

    "Amber": {
        "accent": "#ffb52e",
        "accent_soft": "#ffd889",
        "accent_rgb": "255,181,46",
    },
}


accent_data = ACCENTS[st.session_state.accent]

ACCENT = accent_data["accent"]
ACCENT_SOFT = accent_data["accent_soft"]
ACCENT_RGB = accent_data["accent_rgb"]


# ===========================================================
# THEME VARIABLES
# ===========================================================

if st.session_state.theme == "Dark":

    BG = "#07090f"
    SIDEBAR = "#0b0e17"
    PANEL = "#11141e"
    PANEL_2 = "#10131c"

    TEXT = "#f3f4f7"
    MUTED = "#9aa1ad"
    MUTED_2 = "#737b89"

    BUTTON = "#10141e"
    BUTTON_HOVER = "#141925"

    INPUT = "#11151f"

    DIVIDER = "rgba(255,255,255,0.08)"
    BORDER = "rgba(255,255,255,0.075)"

else:

    BG = "#f5f7fb"
    SIDEBAR = "#ffffff"
    PANEL = "#ffffff"
    PANEL_2 = "#f9fafc"

    TEXT = "#1f2430"
    MUTED = "#667085"
    MUTED_2 = "#8a93a1"

    BUTTON = "#ffffff"
    BUTTON_HOVER = "#f7f9fc"

    INPUT = "#ffffff"

    DIVIDER = "rgba(20,30,50,0.10)"
    BORDER = "rgba(20,30,50,0.10)"


# ===========================================================
# CUSTOM CSS
# ===========================================================

st.markdown(
    f"""
<style>

/* ==========================================================
   CORE PAGE
   ========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {{
    background: {BG} !important;
}}

.stApp {{
    background:
        radial-gradient(
            circle at 52% 6%,
            rgba({ACCENT_RGB}, 0.035),
            transparent 26%
        ),
        {BG} !important;

    color: {TEXT} !important;
}}

.main {{
    background: transparent !important;
}}

.block-container {{
    width: 100% !important;
    max-width: none !important;

    padding-top: 26px !important;
    padding-bottom: 100px !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
}}


/* ==========================================================
   KEEP STREAMLIT NATIVE SIDEBAR COLLAPSE ARROW
   ========================================================== */

/*
   IMPORTANT:
   Do NOT hide stHeader / stToolbar.
   Streamlit's native sidebar collapse arrow lives there.
*/

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

#MainMenu {{
    visibility: hidden !important;
}}

footer {{
    visibility: hidden !important;
}}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {{
    width: 270px !important;
    min-width: 270px !important;
    max-width: 270px !important;

    background: {SIDEBAR} !important;

    border-right: 1px solid {DIVIDER} !important;
}}

section[data-testid="stSidebar"] > div {{
    padding: 10px 18px 18px 18px !important;
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT};
}}


/* Native collapse control */
[data-testid="collapsedControl"] button {{
    color: {MUTED} !important;
}}

[data-testid="collapsedControl"] button:hover {{
    color: {ACCENT} !important;
}}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.sidebar-top {{
    min-height: 31px;

    display: flex;
    justify-content: flex-end;
    align-items: center;

    margin-bottom: 11px;
}}

.sidebar-brand {{
    text-align: center;
    padding-bottom: 19px;
}}

.sidebar-brand-icon {{
    width: 51px;
    height: 51px;

    margin: 0 auto 10px auto;

    border-radius: 16px;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 1px solid rgba({ACCENT_RGB}, 0.82);

    background:
        radial-gradient(
            circle,
            rgba({ACCENT_RGB}, 0.10),
            rgba({ACCENT_RGB}, 0.015) 72%
        );

    box-shadow:
        0 0 12px rgba({ACCENT_RGB}, 0.18),
        0 0 27px rgba({ACCENT_RGB}, 0.075);

    animation:
        sidebarGlow 3.2s ease-in-out infinite;
}}

.sidebar-brand-title {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.1px;

    color: {TEXT};

    margin-bottom: 5px;
}}

.sidebar-brand-subtitle {{
    font-size: 10px;
    font-weight: 500;

    color: {MUTED};
}}

.sidebar-divider {{
    width: 100%;
    height: 1px;

    background: {DIVIDER};

    margin: 0 0 20px 0;
}}


/* ==========================================================
   SIDEBAR HEADINGS
   ========================================================== */

.sidebar-heading {{
    font-size: 14px;
    font-weight: 700;

    color: {TEXT};

    margin: 0 0 12px 0;
}}

.sidebar-empty {{
    font-size: 11px;

    color: {MUTED_2};

    margin-bottom: 19px;
}}


/* ==========================================================
   SELECT BOXES
   ========================================================== */

section[data-testid="stSidebar"] .stSelectbox {{
    margin-bottom: 7px !important;
}}

section[data-testid="stSidebar"] .stSelectbox label {{
    font-size: 11px !important;
    font-weight: 700 !important;

    color: {TEXT} !important;

    margin-bottom: 5px !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    min-height: 36px !important;

    background: {BUTTON} !important;

    border:
        1px solid {BORDER} !important;

    border-radius: 7px !important;

    box-shadow: none !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
    border-color:
        rgba({ACCENT_RGB}, 0.35) !important;
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
    margin-top: 12px;
    margin-bottom: 10px;

    color: {TEXT};

    font-size: 14px;
    font-weight: 700;
}}

.appearance-status {{
    margin-top: 7px;

    color: {MUTED};

    font-size: 10px;
}}


/* ==========================================================
   SIDEBAR BUTTONS
   ========================================================== */

section[data-testid="stSidebar"] .stButton {{
    margin: 0 !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
    min-height: 36px !important;

    padding: 0 10px !important;

    background: {BUTTON} !important;

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
    background: {BUTTON_HOVER} !important;

    border-color:
        rgba({ACCENT_RGB}, 0.38) !important;

    box-shadow:
        0 0 10px rgba({ACCENT_RGB}, 0.06) !important;
}}


/* ==========================================================
   ACTIVE THEME / ACTIVE ACCENT BUTTON
   ========================================================== */

section[data-testid="stSidebar"] .theme-active button {{
    border-color:
        rgba({ACCENT_RGB}, 0.70) !important;

    box-shadow:
        0 0 9px rgba({ACCENT_RGB}, 0.10) !important;
}}


/* ==========================================================
   MAIN CONTENT WIDTH
   ========================================================== */

.reference-width {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin-left: auto;
    margin-right: auto;
}}


/* ==========================================================
   HERO
   ========================================================== */

.hero {{
    width: 830px;
    max-width: calc(100vw - 340px);

    min-height: 277px;

    margin: 0 auto 19px auto;

    padding: 23px 30px 25px 30px;

    box-sizing: border-box;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;

    text-align: center;

    background: {PANEL};

    border:
        1px solid rgba({ACCENT_RGB}, 0.82);

    border-radius: 24px;

    box-shadow:
        0 0 9px rgba({ACCENT_RGB}, 0.11),
        0 0 32px rgba({ACCENT_RGB}, 0.045),
        0 13px 30px rgba(0,0,0,0.22);

    animation: heroGlow 3.6s ease-in-out infinite;
}}

.hero-icon {{
    width: 57px;
    height: 57px;

    margin-bottom: 13px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 17px;

    border:
        1px solid rgba({ACCENT_RGB}, 0.86);

    background:
        radial-gradient(
            circle,
            rgba({ACCENT_RGB}, 0.105),
            rgba({ACCENT_RGB}, 0.015) 72%
        );

    box-shadow:
        0 0 11px rgba({ACCENT_RGB}, 0.18),
        0 0 29px rgba({ACCENT_RGB}, 0.07);

    animation: iconGlow 3.1s ease-in-out infinite;
}}

.hero-title {{
    max-width: 510px;

    margin: 0;

    color: {ACCENT_SOFT};

    font-size: 35px;
    line-height: 1.25;

    font-weight: 800;

    letter-spacing: -1px;
}}

.hero-description {{
    margin:
        13px 0 14px 0;

    color: {MUTED};

    font-size: 12px;
    line-height: 1.5;
}}

.hero-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 7px 14px;

    border-radius: 999px;

    border:
        1px solid rgba({ACCENT_RGB}, 0.82);

    background:
        rgba({ACCENT_RGB}, 0.018);

    color: {ACCENT};

    font-size: 10px;
    font-weight: 700;

    box-shadow:
        0 0 9px rgba({ACCENT_RGB}, 0.08);

    animation: badgeGlow 2.9s ease-in-out infinite;
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
    font-weight: 500;
}}

.quick-row {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin-left: auto;
    margin-right: auto;
}}

.quick-row .stButton {{
    margin-bottom: 9px !important;
}}

.quick-row .stButton > button {{
    height: 37px !important;

    min-height: 37px !important;

    background: {BUTTON} !important;

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
        transform .15s ease,
        box-shadow .18s ease;
}}

.quick-row .stButton > button:hover {{
    background: {BUTTON_HOVER} !important;

    border-color:
        rgba({ACCENT_RGB}, 0.35) !important;

    box-shadow:
        0 0 11px rgba({ACCENT_RGB}, 0.055) !important;

    transform: translateY(-1px);
}}


/* ==========================================================
   NOTICE / DISCLAIMER
   ========================================================== */

.notice-box {{
    width: 702px;
    max-width: calc(100vw - 420px);

    margin:
        14px auto 9px auto;

    padding:
        9px 14px;

    box-sizing: border-box;

    color: {MUTED};

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid {DIVIDER};

    border-radius: 8px;

    font-size: 9px;
    line-height: 1.5;

    text-align: left;
}}

.notice-box b {{
    color: {TEXT};
}}

.disclaimer-box {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto 14px auto;

    padding:
        9px 14px;

    box-sizing: border-box;

    color:
        #c6a44d;

    background:
        rgba(245,158,11,0.035);

    border:
        1px solid rgba(245,158,11,0.23);

    border-radius: 8px;

    font-size: 9px;
    line-height: 1.5;

    text-align: left;
}}

.disclaimer-box b {{
    color: #efc85e;
}}


/* ==========================================================
   UPLOADER
   ========================================================== */

[data-testid="stFileUploader"] {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin:
        0 auto;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: {PANEL_2} !important;

    border:
        1px dashed {DIVIDER} !important;

    border-radius: 10px !important;
}}

[data-testid="stFileUploaderDropzone"] button {{
    border-radius: 8px !important;

    border:
        1px solid {BORDER} !important;

    background: {BUTTON} !important;

    color: {TEXT} !important;
}}

[data-testid="stFileUploader"] small {{
    color: {MUTED} !important;
}}


/* ==========================================================
   CHAT MESSAGES
   ========================================================== */

[data-testid="stChatMessage"] {{
    width: 830px;
    max-width: calc(100vw - 340px);

    margin-left: auto;
    margin-right: auto;
}}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
    font-size: 13px;
}}


/* ==========================================================
   CHAT INPUT
   ========================================================== */

[data-testid="stChatInput"] {{
    width: 702px !important;
    max-width: calc(100vw - 420px) !important;

    margin-left: auto !important;
    margin-right: auto !important;
}}

[data-testid="stChatInput"] > div {{
    min-height: 52px !important;

    background: {INPUT} !important;

    border:
        1px solid rgba({ACCENT_RGB}, 0.82) !important;

    border-radius: 16px !important;

    box-shadow:
        0 0 9px rgba({ACCENT_RGB}, 0.09),
        0 0 25px rgba({ACCENT_RGB}, 0.035);

    animation:
        inputGlow 3.8s ease-in-out infinite;
}}

[data-testid="stChatInput"] textarea {{
    color: {TEXT} !important;

    font-size: 11px !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: {MUTED} !important;
}}

[data-testid="stChatInput"] button {{
    color: {TEXT} !important;
}}


/* ==========================================================
   NEON BREATHING
   ========================================================== */

@keyframes heroGlow {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB}, 0.64);

        box-shadow:
            0 0 7px rgba({ACCENT_RGB}, 0.07),
            0 0 25px rgba({ACCENT_RGB}, 0.025),
            0 13px 30px rgba(0,0,0,0.22);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB}, 0.99);

        box-shadow:
            0 0 11px rgba({ACCENT_RGB}, 0.19),
            0 0 36px rgba({ACCENT_RGB}, 0.095),
            0 13px 30px rgba(0,0,0,0.22);
    }}
}}

@keyframes iconGlow {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB}, 0.68);

        box-shadow:
            0 0 9px rgba({ACCENT_RGB}, 0.10),
            0 0 23px rgba({ACCENT_RGB}, 0.035);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB}, 1);

        box-shadow:
            0 0 14px rgba({ACCENT_RGB}, 0.24),
            0 0 32px rgba({ACCENT_RGB}, 0.09);
    }}
}}

@keyframes badgeGlow {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB}, 0.62);

        box-shadow:
            0 0 6px rgba({ACCENT_RGB}, 0.045);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB}, 1);

        box-shadow:
            0 0 11px rgba({ACCENT_RGB}, 0.18),
            0 0 21px rgba({ACCENT_RGB}, 0.07);
    }}
}}

@keyframes inputGlow {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB}, 0.62);

        box-shadow:
            0 0 7px rgba({ACCENT_RGB}, 0.06);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB}, 0.98);

        box-shadow:
            0 0 12px rgba({ACCENT_RGB}, 0.17),
            0 0 27px rgba({ACCENT_RGB}, 0.065);
    }}
}}

@keyframes sidebarGlow {{

    0%, 100% {{
        border-color:
            rgba({ACCENT_RGB}, 0.66);

        box-shadow:
            0 0 9px rgba({ACCENT_RGB}, 0.10),
            0 0 22px rgba({ACCENT_RGB}, 0.035);
    }}

    50% {{
        border-color:
            rgba({ACCENT_RGB}, 1);

        box-shadow:
            0 0 14px rgba({ACCENT_RGB}, 0.23),
            0 0 30px rgba({ACCENT_RGB}, 0.08);
    }}
}}


/* ==========================================================
   LIGHT THEME ADJUSTMENTS
   ========================================================== */

body {{
    transition:
        background-color .25s ease;
}}

[data-testid="stAppViewContainer"],
section[data-testid="stSidebar"] {{
    transition:
        background-color .25s ease,
        border-color .25s ease;
}}


/* ==========================================================
   RESPONSIVE
   ========================================================== */

@media (max-width: 900px) {{

    .hero,
    .quick-label,
    .quick-row,
    .disclaimer-box,
    [data-testid="stFileUploader"],
    [data-testid="stChatMessage"] {{
        width: calc(100vw - 320px) !important;

        max-width: none !important;
    }}

    .notice-box,
    [data-testid="stChatInput"] {{
        width: calc(100vw - 360px) !important;

        max-width: none !important;
    }}
}}


/* ==========================================================
   REDUCED MOTION
   ========================================================== */

@media (prefers-reduced-motion: reduce) {{

    .hero,
    .hero-icon,
    .hero-badge,
    .sidebar-brand-icon,
    [data-testid="stChatInput"] > div {{
        animation: none !important;
    }}
}}

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

    # Keep the native Streamlit collapse arrow untouched.
    st.markdown(
        '<div class="sidebar-top"></div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------
    # BRAND
    # -------------------------------------------------------

    st.markdown(
        f"""
        <div class="sidebar-brand">

            <div class="sidebar-brand-icon">

                <svg
                    width="30"
                    height="30"
                    viewBox="0 0 50 50"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >

                    <path
                        d="
                            M16 25V14
                            C16 9.6 19.6 6 24 6
                            C28.4 6 32 9.6 32 14V29
                            C32 35.1 36.9 40 43 40
                        "
                        stroke="{ACCENT_SOFT}"
                        stroke-width="2.8"
                        stroke-linecap="round"
                    />

                    <path
                        d="
                            M16 20
                            C12.1 20 9 23.1 9 27
                            C9 30.9 12.1 34 16 34
                        "
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

            <div class="sidebar-brand-title">
                AI HEALTHCARE
            </div>

            <div class="sidebar-brand-subtitle">
                Smart health information assistant
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------
    # CHAT HISTORY
    # -------------------------------------------------------

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
            f"{len(st.session_state.messages)} message"
            f"{'' if len(st.session_state.messages) == 1 else 's'}"
        )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------
    # ASSISTANT MODE
    # -------------------------------------------------------

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

    # -------------------------------------------------------
    # RESPONSE STYLE
    # -------------------------------------------------------

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

    # -------------------------------------------------------
    # ACCENT COLORS
    # -------------------------------------------------------

    st.session_state.accent = st.selectbox(
        "Accent",
        list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(
            st.session_state.accent
        )
    )

    # -------------------------------------------------------
    # APPEARANCE
    # -------------------------------------------------------

    st.markdown(
        '<div class="appearance-title">🎨 Appearance</div>',
        unsafe_allow_html=True
    )

    theme_col1, theme_col2 = st.columns(2)

    with theme_col1:

        if st.button(
            "☀️ Light",
            use_container_width=True
        ):

            if st.session_state.theme != "Light":

                st.session_state.theme = "Light"
                st.rerun()

    with theme_col2:

        if st.button(
            "🌙 Dark",
            use_container_width=True
        ):

            if st.session_state.theme != "Dark":

                st.session_state.theme = "Dark"
                st.rerun()

    st.markdown(
        f'<div class="appearance-status">'
        f'Active theme: {st.session_state.theme}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------------
    # CLEAR
    # -------------------------------------------------------

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
                xmlns="http://www.w3.org/2000/svg"
            >

                <path
                    d="
                        M16 25V14
                        C16 9.6 19.6 6 24 6
                        C28.4 6 32 9.6 32 14V29
                        C32 35.1 36.9 40 43 40
                    "
                    stroke="{ACCENT_SOFT}"
                    stroke-width="2.8"
                    stroke-linecap="round"
                />

                <path
                    d="
                        M16 20
                        C12.1 20 9 23.1 9 27
                        C9 30.9 12.1 34 16 34
                    "
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
    unsafe_allow_html=True
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

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ===========================================================
# DATA NOTICE
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


# ===========================================================
# DISCLAIMER
# ===========================================================

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

        st.error(
            f"An error occurred: {e}"
        )


