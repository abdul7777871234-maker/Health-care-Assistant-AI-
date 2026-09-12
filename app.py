
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from groq import Groq


# ===========================================================
# CONFIG
# ===========================================================

GEMINI_MODEL = "gemini-3.8-flash"
GROQ_MODEL = "openai/gpt-oss-120b"

MAX_IMAGE_SIZE_MB = 10
MAX_HISTORY_MESSAGES = 10
MAX_REPORT_CONTEXT_CHARS = 12000
MAX_USER_QUESTION_CHARS = 3000


# ===========================================================
# PAGE CONFIG (Must be the first Streamlit command)
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


# ===========================================================
# ACCENTS
# ===========================================================

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


# ===========================================================
# THEME VARIABLES
# ===========================================================

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


# ===========================================================
# CSS (Fixed to ensure native sidebar visibility & controls)
# ===========================================================

css = """
<style>

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
    --select-text: __SELECT_TEXT__;
    --bottom-bg: __BOTTOM_BG__;
}

#MainMenu { visibility: visible; }
header { visibility: visible; }
footer { visibility: hidden; }

html, body {
    background: var(--bg) !important;
    min-height: 100vh !important;
}

.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.block-container {
    max-width: 1080px !important;
    padding-top: 1rem !important;
    padding-bottom: 7rem !important;
    color: var(--text) !important;
}

section[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] > div {
    background: var(--sidebar) !important;
}

</style>
"""

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

# ===========================================================
# API KEYS SETUP
# ===========================================================
