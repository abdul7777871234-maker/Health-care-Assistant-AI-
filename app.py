
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from groq import Groq


# ============================================================
# CONFIG
# ============================================================

GEMINI_MODEL = "gemini-3.8-flash"
GROQ_MODEL = "openai/gpt-oss-120b"

MAX_IMAGE_SIZE_MB = 10
MAX_HISTORY_MESSAGES = 10
MAX_REPORT_CONTEXT_CHARS = 12000
MAX_USER_QUESTION_CHARS = 3000


# ============================================================
# SIDEBAR OPEN/CLOSE STATE
# Must be resolved before st.set_page_config, since the sidebar
# state is set at page-config time.
# ============================================================

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state=(
        "expanded" if st.session_state.sidebar_open else "collapsed"
    ),
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "messages": [],
    "report_context": "",
    "report_name": "",
    "accent": "Rose",
    "theme_mode": "Dark",
    "app_mode": "AI Medical Analyst",
    "resp_length": "Balanced",
    "pending_question": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# ACCENTS
# ============================================================

ACCENTS = {
    "Rose": {
        "primary": "#FB4570",
        "secondary": "#FF8FA3",
        "soft": "rgba(251,69,112,.14)",
        "glow": "rgba(251,69,112,.30)",
    },
    "Blue": {
        "primary": "#2E7CF6",
        "secondary": "#6FA8FF",
        "soft": "rgba(46,124,246,.14)",
        "glow": "rgba(46,124,246,.30)",
    },
    "Emerald": {
        "primary": "#0BC98A",
        "secondary": "#4EE6AE",
        "soft": "rgba(11,201,138,.14)",
        "glow": "rgba(11,201,138,.30)",
    },
    "Cyan": {
        "primary": "#00C2D8",
        "secondary": "#5CE8F4",
        "soft": "rgba(0,194,216,.14)",
        "glow": "rgba(0,194,216,.30)",
    },
    "Violet": {
        "primary": "#8B5CF6",
        "secondary": "#B79CFF",
        "soft": "rgba(139,92,246,.14)",
        "glow": "rgba(139,92,246,.30)",
    },
    "Amber": {
        "primary": "#F5A524",
        "secondary": "#FFC864",
        "soft": "rgba(245,165,36,.14)",
        "glow": "rgba(245,165,36,.30)",
    },
    "Sunset": {
        "primary": "#FF5A5F",
        "secondary": "#FFB86B",
        "soft": "rgba(255,90,95,.14)",
        "glow": "rgba(255,90,95,.30)",
    },
}


# ============================================================
# THEME VARIABLES
# ============================================================

accent = ACCENTS[st.session_state.accent]

if st.session_state.theme_mode == "Light":

    bg_color = "#F5F7FB"
    card_bg = "rgba(255,255,255,.90)"
    text_color = "#0F172A"
    sub_text = "#475569"
    muted_text = "#64748B"
    border_color = "rgba(15,23,42,.12)"
    input_bg = "#EEF1F5"
    assistant_bg = "rgba(255,255,255,.92)"
    sidebar_bg = "#F8FAFC"
    select_text = "#0F172A"
    select_bg = "#EEF1F5"
    bottom_bg = "rgba(245,247,251,.88)"

else:

    bg_color = "#080B12"
    card_bg = "rgba(15,23,42,.78)"
    text_color = "#F8FAFC"
    sub_text = "#CBD5E1"
    muted_text = "#94A3B8"
    border_color = "rgba(148,163,184,.20)"
    input_bg = "rgba(15,23,42,.96)"
    assistant_bg = "rgba(15,23,42,.80)"
    sidebar_bg = "#0B1120"
    select_text = "#F8FAFC"
    select_bg = "#111827"
    bottom_bg = "rgba(8,11,18,1)"

color_scheme_value = (
    "light" if st.session_state.theme_mode == "Light" else "dark"
)


# ============================================================
# CSS
# ============================================================

css = """
<style>

/* ============================================================
   ROOT VARIABLES
   ============================================================ */

:root {
    color-scheme: __COLOR_SCHEME__;

    --accent: __ACCENT_PRIMARY__;
    --accent-secondary: __ACCENT_SECONDARY__;
    --accent-soft: __ACCENT_SOFT__;
    --accent-glow: __ACCENT_GLOW__;

    --bg: __BG_COLOR__;
    --card: __CARD_BG__;
    --text: __TEXT_COLOR__;
    --subtext: __SUB_TEXT__;
    --muted: __MUTED_TEXT__;
    --border: __BORDER_COLOR__;
    --input: __INPUT_BG__;
    --assistant: __ASSISTANT_BG__;
    --sidebar: __SIDEBAR_BG__;
    --select-bg: __SELECT_BG__;
    --select-text: __TEXT_COLOR__;
    --select-text: __SELECT_TEXT__;
    --bottom-bg: __BOTTOM_BG__;
}


/* ============================================================
   GLOBAL STREAMLIT
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

html, body {
    background: var(--bg) !important;
    min-height: 100vh !important;
}

#root {
    background: var(--bg) !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% -10%,
            var(--accent-glow),
            transparent 40%
        ),
        radial-gradient(
            circle at 85% 0%,
            var(--accent-soft),
            transparent 45%
        ),
        radial-gradient(
            circle at 50% 100%,
            var(--accent-soft),
            transparent 55%
        ),
        var(--bg) !important;

    background-attachment: fixed !important;

    color: var(--text) !important;
}

.block-container {
    max-width: 1080px !important;

    padding-top: 1rem !important;
    padding-bottom: 7rem !important;

    color: var(--text) !important;
}


/* ============================================================
   FORCE TEXT COLOR
   ============================================================ */

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div {
    color: var(--text);
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background:
        var(--sidebar) !important;

    border-right:
        1px solid var(--border) !important;
}

section[data-testid="stSidebar"] > div {
    background:
        var(--sidebar) !important;
}

section[data-testid="stSidebar"] * {
    color:
        var(--text) !important;
}

/* Sidebar markdown headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color:
        var(--text) !important;

    opacity:
        1 !important;
}

/* Sidebar labels */
section[data-testid="stSidebar"] label {
    color:
        var(--text) !important;

    opacity:
        1 !important;
}

/* Sidebar caption */
section[data-testid="stSidebar"]
[data-testid="stCaptionContainer"] {
    color:
        var(--muted) !important;
}


/* ============================================================
   SIDEBAR TOGGLE BUTTON
   Real st.button, styled as a fixed pill with a label above
   the icon. Always on top, whether the sidebar is open or
   collapsed, since it lives in the main area, not inside the
   sidebar itself.
   ============================================================ */

/* Hide Streamlit's own default collapse arrow — we supply ours */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarContent"] button[kind="header"],
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

.st-key-sidebar_toggle_btn {
    position: fixed !important;
    top: 14px;
    left: 14px;
    z-index: 999999;
    width: auto !important;
}

.st-key-sidebar_toggle_btn button {
    min-height: 0 !important;
    height: auto !important;
    width: 44px !important;
    padding: 9px 0 7px 0 !important;

    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 3px !important;

    border-radius: 14px !important;
    background: var(--card) !important;
    border: 1px solid var(--accent) !important;
    box-shadow: 0 8px 22px rgba(0,0,0,.16) !important;
}

.st-key-sidebar_toggle_btn button p {
    font-size: 17px !important;
    line-height: 1 !important;
    color: var(--text) !important;
}

.st-key-sidebar_toggle_btn button::before {
    content: "MENU";
    font-size: 8px;
    font-weight: 800;
    letter-spacing: .6px;
    color: var(--muted);
    order: -1;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.sidebar-brand {
    text-align: center;

    padding:
        8px 5px 15px 5px;
}

.brand-icon {
    width: 56px;
    height: 56px;

    margin:
        0 auto 10px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 18px;

    background:
        var(--accent-soft);

    border:
        1px solid var(--accent);

    box-shadow:
        0 10px 30px var(--accent-glow);

    font-size: 27px;
}

.brand-title {
    color:
        var(--text) !important;

    font-size: 18px;
    font-weight: 800;

    letter-spacing: .4px;
}

.brand-subtitle {
    color:
        var(--muted) !important;

    font-size: 11px;

    margin-top:
        4px;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    text-align: center;

    padding:
        26px 20px 22px 20px;

    margin:
        0 0 12px 0;

    border:
        1px solid var(--accent);

    border-radius:
        26px;

    background:
        var(--card);

    backdrop-filter:
        blur(24px);

    -webkit-backdrop-filter:
        blur(24px);

    box-shadow:
        0 20px 60px rgba(0,0,0,.12),
        0 0 0 1px var(--accent-soft),
        0 0 40px var(--accent-glow);

    animation:
        fadeUp .30s ease;
}

.hero-icon {
    width: 62px;
    height: 62px;

    margin:
        0 auto 12px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 20px;

    background:
        var(--accent-soft);

    border:
        1px solid var(--accent);

    box-shadow:
        0 0 25px var(--accent-glow);

    font-size: 31px;

    animation:
        heroPulse 2.6s ease-in-out infinite;
}

.hero-title {
    margin:
        0 !important;

    padding:
        0 !important;

    font-size:
        clamp(36px, 5.5vw, 58px);

    line-height:
        .98;

    font-weight:
        850;

    letter-spacing:
        -2.5px;

    background:
        linear-gradient(
            135deg,
            var(--text) 20%,
            var(--accent) 65%,
            var(--accent-secondary)
        );

    background-clip:
        text;

    -webkit-background-clip:
        text;

    color:
        transparent;

    -webkit-text-fill-color:
        transparent;
}

.hero-subtitle {
    max-width:
        680px;

    margin:
        12px auto 0 auto;

    background:
        transparent !important;

    color:
        var(--subtext) !important;

    font-size:
        14px;

    line-height:
        1.5;
}

.mode-badge {
    display:
        inline-block;

    margin-top:
        13px;

    padding:
        6px 12px;

    border-radius:
        999px;

    background:
        var(--accent-soft);

    border:
        1px solid var(--accent);

    color:
        var(--accent) !important;

    font-size:
        11px;

    font-weight:
        700;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    min-height:
        40px !important;

    border-radius:
        12px !important;

    border:
        1px solid var(--border) !important;

    background:
        var(--card) !important;

    color:
        var(--text) !important;

    font-weight:
        600 !important;

    transition:
        all .16s ease !important;
}

.stButton > button p {
    color:
        var(--text) !important;
}

.stButton > button:hover {
    border-color:
        var(--accent) !important;

    color:
        var(--accent) !important;

    transform:
        translateY(-1px) !important;

    box-shadow:
        0 7px 22px var(--accent-glow) !important;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] {
    color:
        var(--select-text) !important;
}

[data-testid="stSelectbox"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
div[data-baseweb="select"] div[data-baseweb="base-input"] {
    background:
        var(--select-bg) !important;

    color:
        var(--select-text) !important;

    border-radius:
        11px !important;
}

div[data-baseweb="select"] > div {
    border:
        1px solid var(--border) !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] input {
    background: transparent !important;
    color:
        var(--select-text) !important;
}


/* Dropdown popup */
div[role="listbox"] {
    background:
        var(--select-bg) !important;

    border:
        1px solid var(--border) !important;
}

div[role="option"] {
    color:
        var(--select-text) !important;

    background:
        var(--select-bg) !important;
}

div[role="option"]:hover {
    background:
        var(--accent-soft) !important;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {
    border:
        1px solid var(--border) !important;

    border-radius:
        18px !important;

    margin-bottom:
        10px !important;

    background:
        var(--assistant) !important;

    padding:
        8px 12px !important;

    max-width: 85%;
}

/* User messages: accent-tinted, right-aligned */
[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) {
    margin-left: auto !important;
    background: var(--accent-soft) !important;
    border-color: var(--accent) !important;
}

/* Assistant messages: neutral card, left-aligned */
[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarAssistant"]
) {
    margin-right: auto !important;
}

[data-testid="stChatMessageContent"] {
    color:
        var(--text) !important;
}

[data-testid="stChatMessageContent"] p {
    color:
        var(--text) !important;

    margin-top:
        .15rem !important;

    margin-bottom:
        .38rem !important;

    line-height:
        1.52 !important;
}

[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3,
[data-testid="stChatMessageContent"] h4 {
    color:
        var(--text) !important;

    margin-top:
        .55rem !important;

    margin-bottom:
        .3rem !important;
}

[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol {
    margin-top:
        .2rem !important;

    margin-bottom:
        .45rem !important;
}


/* ============================================================
   CHAT INPUT — REDUCED WIDTH & FIXED BACKGROUND
   ============================================================ */

[data-testid="stBottom"] {
    background:
        var(--bottom-bg) !important;

    background-color:
        var(--bottom-bg) !important;

    border:
        none !important;

    box-shadow:
        none !important;
}

[data-testid="stBottomBlockContainer"] {
    background:
        var(--bottom-bg) !important;

    background-color:
        var(--bottom-bg) !important;

    border:
        none !important;

    box-shadow:
        none !important;

    padding:
        8px 0 14px 0 !important;
}

[data-testid="stChatInput"] {
    max-width: 780px !important;
    margin: 0 auto !important;
    
    background:
        var(--input) !important;

    border:
        1px solid var(--accent) !important;

    border-radius:
        18px !important;

    box-shadow:
        0 0 0 1px var(--accent-soft),
        0 10px 35px var(--accent-glow) !important;

    overflow:
        hidden !important;
}

[data-testid="stChatInput"] > div {
    background:
        var(--input) !important;

    border:
        none !important;
}

[data-testid="stChatInput"] textarea {
    background:
        transparent !important;

    color:
        var(--text) !important;

    caret-color:
        var(--accent) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color:
        var(--muted) !important;

    opacity:
        1 !important;
}


/* Chat input toolbar */
[data-testid="stChatInput"] button {
    color:
        var(--text) !important;

    background:
        transparent !important;
}

[data-testid="stChatInput"] button:hover {
    color:
        var(--accent) !important;
    background:
        var(--accent-soft) !important;
}


/* ============================================================
   QUICK ACTIONS
   ============================================================ */

.quick-title {
    text-align:
        center;

    color:
        var(--muted) !important;

    font-size:
        12px;

    margin:
        6px 0 6px 0;
}


/* ============================================================
   REPORT STATUS
   ============================================================ */

.report-status {
    margin:
        6px 0 10px 0;

    padding:
        9px 12px;

    border-radius:
        12px;

    background:
        var(--accent-soft);

    border:
        1px solid var(--accent);

    color:
        var(--accent) !important;

    font-size:
        12px;

    font-weight:
        600;
}


/* ============================================================
   DISCLAIMER
   ============================================================ */

.disclaimer {
    margin:
        14px 0 0 0;

    padding:
        10px 13px;

    border-radius:
        13px;

    background:
        rgba(245,158,11,.07);

    border:
        1px solid rgba(245,158,11,.22);

    color:
        var(--muted) !important;

    font-size:
        11px;

    line-height:
        1.5;
}

.disclaimer b {
    color:
        var(--text) !important;
}


/* ============================================================
   EPHEMERAL DATA NOTE
   ============================================================ */

.ephemeral-note {
    max-width: 780px !important;
    margin: 10px auto 8px auto !important;

    padding:
        8px 12px;

    border-radius:
        12px;

    background:
        var(--accent-soft);

    border:
        1px solid var(--border);

    color:
        var(--muted) !important;

    font-size:
        11px;

    line-height:
        1.5;

    text-align:
        center;
}


/* ============================================================
   DIVIDER
   ============================================================ */

hr {
    border-color:
        var(--border) !important;

    margin:
        10px 0 !important;
}


/* ============================================================
   ANIMATION — SLOW NEON BREATHING
   ============================================================ */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(7px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes neonBreath {
    0%, 100% {
        filter: brightness(1);
        box-shadow:
            0 0 0 1px var(--accent-soft),
            0 0 18px var(--accent-glow),
            0 0 38px rgba(0,0,0,0);
    }

    50% {
        filter: brightness(1.08);
        box-shadow:
            0 0 0 1px var(--accent-soft),
            0 0 30px var(--accent-glow),
            0 0 58px var(--accent-glow);
    }
}

@keyframes neonBorderBreath {
    0%, 100% {
        box-shadow:
            0 0 0 1px var(--accent-soft),
            0 0 18px var(--accent-glow);
    }

    50% {
        box-shadow:
            0 0 0 1px var(--accent-soft),
            0 0 30px var(--accent-glow),
            0 0 58px var(--accent-glow);
    }
}

@keyframes heroPulse {

    0%, 100% {
        box-shadow: 0 0 25px var(--accent-glow);
        transform: scale(1);
    }

    50% {
        box-shadow: 0 0 40px var(--accent-glow);
        transform: scale(1.04);
    }
}

/* Slow breathing glow on all intentional neon surfaces. */
.hero,
.brand-icon,
.hero-icon,
.mode-badge,
.report-status,
[data-testid="stChatInput"] {
    animation: neonBorderBreath 4.8s ease-in-out infinite;
}

/* Keep the hero icon's existing subtle pulse while adding the glow. */
.hero-icon {
    animation:
        heroPulse 2.6s ease-in-out infinite,
        neonBreath 4.8s ease-in-out infinite;
}

/* Interactive neon controls breathe slowly without changing layout. */
.stButton > button:hover,
.st-key-sidebar_toggle_btn button {
    animation: neonBreath 4.8s ease-in-out infinite;
}


/* ============================================================
   ACCESSIBILITY — RESPECT REDUCED MOTION
   ============================================================ */
@media (prefers-reduced-motion: reduce) {
    .hero,
    .brand-icon,
    .hero-icon,
    .mode-badge,
    .report-status,
    [data-testid="stChatInput"],
    .stButton > button:hover,
    .st-key-sidebar_toggle_btn button {
        animation: none !important;
    }
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 768px) {

    .block-container {
        padding-left:
            10px !important;

        padding-right:
            10px !important;

        padding-bottom:
            6.5rem !important;
    }

    .hero {
        padding:
            22px 14px 19px 14px;

        border-radius:
            21px;
    }

    .hero-title {
        font-size:
            40px;

        letter-spacing:
            -1.8px;
    }

    .hero-subtitle {
        font-size:
            13px;
    }

    [data-testid="stBottomBlockContainer"] {
        padding:
            7px 8px 12px 8px !important;
    }

    [data-testid="stChatInput"] {
        border-radius:
            16px !important;
    }
}

   DARK/LIGHT INPUT SURFACE FIX
   Keeps every input surface on the active theme.
   ============================================================ */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] textarea,
[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="base-input"] {
    background-color: var(--input) !important;
    background: var(--input) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    border-color: var(--border) !important;
}

[data-testid="stChatInput"] textarea {
    background-color: var(--input) !important;
    background: var(--input) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    caret-color: var(--accent) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
    -webkit-text-fill-color: var(--muted) !important;
    opacity: 1 !important;
}

/* ============================================================
   SELECTBOX — HARD DARK/LIGHT SURFACE FIX
   Prevents Streamlit/BaseWeb from reverting the controls to white.
   ============================================================ */
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="input"] > div {
    background: var(--select-bg) !important;
    background-color: var(--select-bg) !important;
    color: var(--select-text) !important;
    border-color: var(--border) !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] * {
    color: var(--select-text) !important;
    -webkit-text-fill-color: var(--select-text) !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] svg,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    color: var(--select-text) !important;
    fill: var(--select-text) !important;
    stroke: var(--select-text) !important;
}

/* BaseWeb sometimes paints the selected-value wrapper separately. */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [aria-haspopup="listbox"] {
    background: var(--select-bg) !important;
    background-color: var(--select-bg) !important;
    color: var(--select-text) !important;
}

/* Open select dropdown / popover. */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
li[role="option"],
li[role="option"] > div {
    background: var(--select-bg) !important;
    background-color: var(--select-bg) !important;
    color: var(--select-text) !important;
}

div[data-baseweb="popover"] *,
div[data-baseweb="menu"] *,
ul[role="listbox"] *,
li[role="option"] * {
    color: var(--select-text) !important;
    -webkit-text-fill-color: var(--select-text) !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: var(--accent-soft) !important;
    background-color: var(--accent-soft) !important;
}

</style>
"""

# Theme placeholders are substituted after the CSS string is created.
# This avoids Python f-string parsing of CSS braces.
css = (
    css
    .replace("__COLOR_SCHEME__", color_scheme_value)
    .replace("__ACCENT_PRIMARY__", accent["primary"])
    .replace("__ACCENT_SECONDARY__", accent["secondary"])
    .replace("__ACCENT_SOFT__", accent["soft"])
    .replace("__ACCENT_GLOW__", accent["glow"])
    .replace("__BG_COLOR__", bg_color)
    .replace("__CARD_BG__", card_bg)
    .replace("__TEXT_COLOR__", text_color)
    .replace("__SUB_TEXT__", sub_text)
    .replace("__MUTED_TEXT__", muted_text)
    .replace("__BORDER_COLOR__", border_color)
    .replace("__INPUT_BG__", input_bg)
    .replace("__ASSISTANT_BG__", assistant_bg)
    .replace("__SIDEBAR_BG__", sidebar_bg)
    .replace("__SELECT_BG__", select_bg)
    .replace("__SELECT_TEXT__", select_text)
    .replace("__BOTTOM_BG__", bottom_bg)
)

st.markdown(css, unsafe_allow_html=True)


# ============================================================
# SIDEBAR TOGGLE BUTTON
# A real Streamlit button (not CSS/JS trickery), so click
# open/close is 100% reliable. Streamlit exposes a stable
# ".st-key-<key>" class on this button's wrapper for styling.
# ============================================================

toggle_icon = "✕" if st.session_state.sidebar_open else "☰"

if st.button(toggle_icon, key="sidebar_toggle_btn"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()


# ============================================================
# API KEYS
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GEMINI_API_KEY or not GROQ_API_KEY:

    st.error(
        "AI services are not configured. "
        "Please run Cell 3 and then Cell 8."
    )

    st.stop()


# ============================================================
# AI CLIENTS
# ============================================================

@st.cache_resource(show_spinner=False)
def get_clients():

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    groq_client = Groq(
        api_key=GROQ_API_KEY
    )

    return gemini_client, groq_client


gemini_client, groq_client = get_clients()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">🩺</div>
            <div class="brand-title">AI HEALTHCARE</div>
            <div class="brand-subtitle">
                Smart health information assistant
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CHAT HISTORY IN SIDEBAR
    # --------------------------------------------------------

    st.markdown("### 💬 Chat History")
    
    if not st.session_state.messages:
        st.caption("No previous messages yet.")
    else:
        history_container = st.container(height=200)
        with history_container:
            for idx, msg in enumerate(st.session_state.messages):
                role_label = "🧑‍💻 You" if msg.get("role") == "user" else "🤖 AI"
                content_preview = msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", "")
                st.markdown(f"**{role_label}:** {content_preview}")

    st.markdown("---")

    # --------------------------------------------------------
    # ASSISTANT MODE
    # --------------------------------------------------------

    st.markdown("### 🧠 Assistant Mode")

    mode_options = [
        "AI Medical Analyst",
        "Symptom Checker",
        "Nutrition Coach",
    ]

    current_mode = st.session_state.app_mode

    if current_mode not in mode_options:
        current_mode = mode_options[0]

    st.session_state.app_mode = st.selectbox(
        "Assistant Mode",
        mode_options,
        index=mode_options.index(current_mode),
        label_visibility="collapsed",
    )

    # --------------------------------------------------------
    # RESPONSE STYLE
    # --------------------------------------------------------

    st.markdown("### ✍️ Response Style")

    length_options = [
        "Concise",
        "Balanced",
        "Detailed Assessment",
    ]

    current_length = st.session_state.resp_length

    if current_length not in length_options:
        current_length = "Balanced"

    st.session_state.resp_length = st.selectbox(
        "Response Style",
        length_options,
        index=length_options.index(current_length),
        label_visibility="collapsed",
    )

    # --------------------------------------------------------
    # ACCENT
    # --------------------------------------------------------

    st.markdown("### 🎨 Accent")

    accent_options = list(ACCENTS.keys())

    current_accent = st.session_state.accent

    if current_accent not in accent_options:
        current_accent = "Rose"

    selected_accent = st.selectbox(
        "Accent",
        accent_options,
        index=accent_options.index(current_accent),
        label_visibility="collapsed",
    )

    if selected_accent != st.session_state.accent:

        st.session_state.accent = selected_accent
        st.rerun()

    # --------------------------------------------------------
    # APPEARANCE
    # --------------------------------------------------------

    st.markdown("### ☀️ Appearance")

    theme_col1, theme_col2 = st.columns(2)

    with theme_col1:

        if st.button(
            "☀️ Light",
            use_container_width=True,
            key="theme_light",
        ):

            if st.session_state.theme_mode != "Light":
                st.session_state.theme_mode = "Light"
                st.rerun()

    with theme_col2:

        if st.button(
            "🌙 Dark",
            use_container_width=True,
            key="theme_dark",
        ):

            if st.session_state.theme_mode != "Dark":
                st.session_state.theme_mode = "Dark"
                st.rerun()

    st.caption(
        f"Active theme: {st.session_state.theme_mode}"
    )

    # --------------------------------------------------------
    # ACTIVE REPORT
    # --------------------------------------------------------

    if st.session_state.report_context:

        st.markdown("---")

        st.markdown("### 📄 Active Report")

        report_display = (
            st.session_state.report_name
            or "Medical report loaded"
        )

        st.success(report_display)

        if st.button(
            "🗑️ Remove Report Context",
            use_container_width=True,
            key="remove_report",
        ):

            st.session_state.report_context = ""
            st.session_state.report_name = ""

            st.rerun()

    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
        key="clear_conversation",
    ):

        st.session_state.messages = []
        st.session_state.report_context = ""
        st.session_state.report_name = ""
        st.session_state.pending_question = ""

        st.rerun()


# ============================================================
# HERO
# ============================================================

MODE_DESCRIPTIONS = {
    "AI Medical Analyst":
        "Understand medical reports and health information in simple language.",

    "Symptom Checker":
        "Describe symptoms and receive general educational health information.",

    "Nutrition Coach":
        "Ask nutrition and healthy-lifestyle questions.",
}

st.markdown(
    f"""<div class="hero">
<div class="hero-icon">🩺</div>
<h1 class="hero-title">AI Healthcare<br>Assistant</h1>
<div class="hero-subtitle">{MODE_DESCRIPTIONS[st.session_state.app_mode]}</div>
<div class="mode-badge">{st.session_state.app_mode}</div>
</div>""",
    unsafe_allow_html=True,
)


# ============================================================
# CLEAN QUESTION
# ============================================================

def clean_question(text):

    if not text:
        return ""

    return text.strip()[:MAX_USER_QUESTION_CHARS]


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_image(uploaded_file):

    if uploaded_file is None:

        return (
            False,
            None,
            None,
            "Please attach a medical report image.",
        )

    mime_type = uploaded_file.type or ""

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if mime_type not in allowed_types:

        return (
            False,
            None,
            None,
            "Only JPG, JPEG, PNG and WEBP images are supported.",
        )

    image_bytes = uploaded_file.getvalue()

    if not image_bytes:

        return (
            False,
            None,
            None,
            "The uploaded image is empty.",
        )

    size_mb = len(image_bytes) / (1024 * 1024)

    if size_mb > MAX_IMAGE_SIZE_MB:

        return (
            False,
            None,
            None,
            f"Image is too large. Maximum size is "
            f"{MAX_IMAGE_SIZE_MB} MB.",
        )

    try:

        image = Image.open(
            BytesIO(image_bytes)
        )

        image.verify()

    except Exception:

        return (
            False,
            None,
            None,
            "The uploaded file is not a valid image.",
        )

    return (
        True,
        image_bytes,
        mime_type,
        None,
    )


# ============================================================
# GEMINI MEDICAL REPORT ANALYSIS
# ============================================================

def analyze_medical_report(
    image_bytes,
    mime_type,
    user_question,
):

    prompt = f"""
You are the medical-report extraction component of an
AI Healthcare Assistant.

Analyze ONLY information actually visible in the
uploaded medical report image.

Do NOT invent:
- values
- diagnoses
- symptoms
- medications
- medical history
- reference ranges
- measurements
- patient details

If text or a value is unreadable, write:
"Unreadable from the uploaded image."

Extract useful information including, when visible:

1. Test/report name
2. Important test values
3. Units
4. Displayed reference ranges
5. Results outside displayed reference ranges
6. Important observations
7. Visible impression/conclusion
8. Information relevant to the user's question

Rules:

- Preserve exact values and units.
- Distinguish observed facts from interpretation.
- Do not diagnose.
- Do not prescribe medication.
- Do not provide medication doses.
- Keep analysis structured and compact.
- Prioritize accuracy.

USER QUESTION:
{user_question or "Please explain this medical report in simple language."}
"""

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    response = gemini_client.models.generate_content(

        model=GEMINI_MODEL,

        contents=[
            prompt,
            image_part,
        ],

        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="low",
            )
        ),
    )

    analysis = (
        response.text or ""
    ).strip()

    if not analysis:

        raise RuntimeError(
            "Gemini returned an empty report analysis."
        )

    return analysis[:MAX_REPORT_CONTEXT_CHARS]


# ============================================================
# RESPONSE SETTINGS
# ============================================================

def get_response_settings():

    length = st.session_state.resp_length
    mode = st.session_state.app_mode

    if mode == "AI Medical Analyst":

        mode_instruction = """
You are a careful medical information assistant.

Explain medical reports and health information clearly.
Do not diagnose the user.
"""

    elif mode == "Symptom Checker":

        mode_instruction = """
You are a symptom-information assistant.

Provide general educational information about symptoms,
possible categories of causes, and appropriate next steps.

Do not diagnose.
Mention urgent warning signs when genuinely relevant.
"""

    else:

        mode_instruction = """
You are a nutrition and healthy-lifestyle assistant.

Give practical general nutrition guidance.
Do not prescribe medical diets or medication.
Do not claim food can cure a disease.
"""

    if length == "Concise":

        style_instruction = """
Keep the answer SHORT.

- Direct answer first
- 2–5 short bullets or paragraphs
- No unnecessary sections
- Roughly 80–180 words when appropriate
"""

        reasoning = "low"
        max_tokens = 450

    elif length == "Detailed Assessment":

        style_instruction = """
Give a detailed but readable answer.

- Use useful headings
- Use bullets where helpful
- Explain important terminology
- For reports, explain actual visible values and ranges
- Avoid filler
- Roughly 350–700 words when appropriate
"""

        reasoning = "medium"
        max_tokens = 1200

    else:

        style_instruction = """
Give a balanced answer.

- Informative but efficient
- Use short headings only when useful
- Roughly 150–350 words when appropriate
- Avoid filler
"""

        reasoning = "low"
        max_tokens = 750

    return (
        mode_instruction,
        style_instruction,
        reasoning,
        max_tokens,
    )


# ============================================================
# CONVERSATION CONTEXT
# ============================================================

def build_conversation_context():

    recent = st.session_state.messages[
        -MAX_HISTORY_MESSAGES:
    ]

    if not recent:

        return "No previous conversation."

    lines = []

    for msg in recent:

        role = msg.get(
            "role",
            "user",
        ).upper()

        content = (
            msg.get("content", "")
            or ""
        )

        if len(content) > 2500:
            content = content[:2500]

        lines.append(
            f"{role}: {content}"
        )

    return "\n".join(lines)


# ============================================================
# GROQ RESPONSE
# ============================================================

def generate_final_answer(
    user_question,
    report_context="",
):

    (
        mode_instruction,
        style_instruction,
        reasoning,
        max_tokens,
    ) = get_response_settings()

    conversation = build_conversation_context()

    report_text = (
        report_context
        if report_context
        else
        "No medical report is currently attached."
    )

    prompt = f"""
{mode_instruction}

{style_instruction}

You are the final patient-facing response layer.

Answer the user's actual question directly.

MEDICAL REPORT CONTEXT:
-----------------------
{report_text}
-----------------------

RECENT CONVERSATION:
-----------------------
{conversation}
-----------------------

CURRENT USER QUESTION:
-----------------------
{user_question}
-----------------------

SAFETY RULES:

- This is informational support only.
- Never claim to be a doctor.
- Never provide a definitive diagnosis.
- Never invent report values.
- Never invent patient history.
- Never prescribe medication.
- Never provide medication doses.
- Do not turn a possibility into a diagnosis.
- Clearly distinguish report findings from general information.
- If information is missing, say so.
- If symptoms suggest an emergency, recommend appropriate urgent medical care.
- Answer normal/general questions naturally.
- A medical report is NOT required for normal questions.
- Do not mention Gemini.
- Do not mention Groq.
- Do not mention APIs.
- Do not mention internal processing.
- Do not repeat the entire conversation.
- Produce ONE patient-friendly answer.

Return ONLY the final answer.
"""

    response = groq_client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content":
                    "You are a safe, accurate and patient-friendly "
                    "healthcare information assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        reasoning_effort=reasoning,

        include_reasoning=False,

        temperature=0.2,

        max_tokens=max_tokens,

        stream=True,
    )

    return response


# ============================================================
# STREAM RESPONSE
# ============================================================

def stream_groq_response(response):

    full_text = ""

    placeholder = st.empty()

    for chunk in response:

        try:

            delta = (
                chunk.choices[0]
                .delta.content
            )

        except Exception:

            delta = None

        if delta:

            full_text += delta

            placeholder.markdown(
                full_text
            )

    if not full_text.strip():

        raise RuntimeError(
            "Groq returned an empty response."
        )

    return full_text.strip()


# ============================================================
# QUICK QUESTIONS
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="quick-title">
            Try a quick question
        </div>
        """,
        unsafe_allow_html=True,
    )

    q1, q2 = st.columns(2)

    with q1:

        if st.button(
            "📄 Blood test basics",
            use_container_width=True,
            key="quick_blood",
        ):

            st.session_state.pending_question = (
                "How do I understand a blood test?"
            )

            st.rerun()

    with q2:

        if st.button(
            "🥗 Healthy diet",
            use_container_width=True,
            key="quick_diet",
        ):

            st.session_state.pending_question = (
                "What is a healthy diet?"
            )

            st.rerun()

    q3, q4 = st.columns(2)

    with q3:

        if st.button(
            "🔍 Causes of fatigue",
            use_container_width=True,
            key="quick_fatigue",
        ):

            st.session_state.pending_question = (
                "What are some common causes of fatigue?"
            )

            st.rerun()

    with q4:

        if st.button(
            "💊 Medication side effects",
            use_container_width=True,
            key="quick_medicine",
        ):

            st.session_state.pending_question = (
                "What are common medication side effects?"
            )

            st.rerun()


# ============================================================
# ACTIVE REPORT STATUS
# ============================================================

if st.session_state.report_context:

    report_name = (
        st.session_state.report_name
        or "Medical report"
    )

    st.markdown(
        f"""
        <div class="report-status">
            📄 <b>{report_name}</b> is active.
            Ask follow-up questions without uploading again.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:

    with st.chat_message(
        msg.get("role", "assistant")
    ):

        content = (
            msg.get("content", "")
            or ""
        )

        if content:
            st.markdown(content)

        attachment = msg.get("attachment")

        if attachment:

            st.caption(
                f"📎 {attachment}"
            )


# ============================================================
# EPHEMERAL DATA NOTICE
# Shown directly above the chat / file-upload box.
# ============================================================

st.markdown(
    """
    <div class="ephemeral-note">
        🔒 <b>Ephemeral Data Processing</b> — any medical document
        you attach is deleted automatically within 1 hour.
        Your chat history stays saved in this conversation.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHAT INPUT
#
# Image is OPTIONAL.
# Text is OPTIONAL.
# At least one is required by the handler.
# ============================================================

chat_input = st.chat_input(
    "Ask anything about health or attach a medical report...",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)


# ============================================================
# DETERMINE REQUEST
# ============================================================

if (
    not chat_input
    and st.session_state.pending_question
):

    user_question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = ""

    files = []

elif chat_input:

    user_question = clean_question(
        getattr(
            chat_input,
            "text",
            "",
        )
    )

    files = list(
        getattr(
            chat_input,
            "files",
            [],
        )
        or []
    )

else:

    user_question = ""
    files = []


# ============================================================
# HANDLE REQUEST
# ============================================================

if user_question or files:

    # --------------------------------------------------------
    # Image-only request
    # --------------------------------------------------------

    if not user_question:

        user_question = (
            "Please explain this medical report "
            "in simple language."
        )

    # --------------------------------------------------------
    # One image only
    # --------------------------------------------------------

    if len(files) > 1:

        st.warning(
            "Please upload one medical report image at a time."
        )

        st.stop()

    uploaded_file = (
        files[0]
        if files
        else None
    )

    try:

        # ====================================================
        # VALIDATE IMAGE FIRST
        # ====================================================

        attachment_name = None
        image_bytes = None
        mime_type = None

        if uploaded_file:

            (
                valid,
                image_bytes,
                mime_type,
                error,
            ) = validate_image(
                uploaded_file
            )

            if not valid:

                st.error(error)
                st.stop()

            attachment_name = (
                uploaded_file.name
            )

        # ====================================================
        # SAVE USER MESSAGE
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_question,
                "attachment": attachment_name,
            }
        )

        # ====================================================
        # SHOW USER MESSAGE
        # ====================================================

        with st.chat_message("user"):

            st.markdown(
                user_question
            )

            if attachment_name:

                st.caption(
                    f"📎 {attachment_name}"
                )

        # ====================================================
        # IMAGE / REPORT PIPELINE
        # ====================================================

        if uploaded_file:

            with st.chat_message("assistant"):

                status = st.empty()

                status.markdown(
                    "🔎 **Reading your medical report...**"
                )

                report_analysis = (
                    analyze_medical_report(
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                        user_question=user_question,
                    )
                )

                status.empty()

                # --------------------------------------------
                # Save text analysis only
                # --------------------------------------------

                st.session_state.report_context = (
                    report_analysis
                )

                st.session_state.report_name = (
                    uploaded_file.name
                )

                # --------------------------------------------
                # Generate patient response
                # --------------------------------------------

                status = st.empty()

                status.markdown(
                    "🤖 **Preparing your answer...**"
                )

                groq_stream = (
                    generate_final_answer(
                        user_question=user_question,
                        report_context=report_analysis,
                    )
                )

                status.empty()

                final_answer = (
                    stream_groq_response(
                        groq_stream
                    )
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": final_answer,
                    }
                )

        # ====================================================
        # NORMAL TEXT CHAT
        # ====================================================

        else:

            with st.chat_message("assistant"):

                status = st.empty()

                status.markdown(
                    "🤖 **Thinking...**"
                )

                groq_stream = (
                    generate_final_answer(
                        user_question=user_question,
                        report_context=
                            st.session_state.report_context,
                    )
                )

                status.empty()

                final_answer = (
                    stream_groq_response(
                        groq_stream
                    )
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": final_answer,
                    }
                )

    except Exception as e:

        # ----------------------------------------------------
        # Remove failed user message
        # ----------------------------------------------------

        if (
            st.session_state.messages
            and st.session_state.messages[-1].get("role")
            == "user"
        ):

            st.session_state.messages.pop()

        st.error(
            "I couldn't process that request right now. "
            "Please try again."
        )

        print(
            "Internal application error:",
            type(e).__name__,
            str(e)[:500],
        )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">
        ⚠️ <b>Important:</b>
        This AI Healthcare Assistant provides general
        informational support only. It does not diagnose
        medical conditions, prescribe treatment, or replace
        advice from a qualified healthcare professional.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# END OF STREAMLIT APP
# ============================================================
