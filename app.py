import os
import base64
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- STATE ----------------

st.session_state.setdefault("theme", "Light")
st.session_state.setdefault("accent", "Cyan")
st.session_state.setdefault("messages", [])
st.session_state.setdefault("ai_persona", "AI Medical Analyst")
st.session_state.setdefault("response_style", "Balanced")

ACCENTS = {
    "Cyan": ("#00B4D8", "rgba(0,180,216,.15)"),
    "Blue": ("#2563EB", "rgba(37,99,235,.15)"),
    "Violet": ("#7C3AED", "rgba(124,58,237,.15)"),
    "Rose": ("#E11D48", "rgba(225,29,72,.15)"),
    "Emerald": ("#059669", "rgba(5,150,105,.15)"),
    "Amber": ("#D97706", "rgba(217,119,6,.15)"),
}

ACCENT, GLOW = ACCENTS.get(st.session_state.accent, ("#00B4D8", "rgba(0,180,216,.15)"))

# Force explicit color schemes based on active state
if st.session_state.theme == "Dark":
    BG = "#050811"
    PANEL = "#0B1120"
    TEXT = "#F7FAFF"
    MUTED = "#97A4B8"
    BORDER = "rgba(255,255,255,.15)"
    WIDGET_BG = "#101827"
    WIDGET_TEXT = "#F7FAFF"
    CHAT_INPUT_BG = "#1E1F20"  # Matched with Image 2 Dark Input Box Color
else:
    BG = "#F8FAFC"        # Clean light grey/white background
    PANEL = "#FFFFFF"     # Solid white panels
    TEXT = "#0F172A"      # Pitch dark text
    MUTED = "#334155"     # Darker muted text for high contrast visibility
    BORDER = "#CBD5E1"    # Clear visible borders
    WIDGET_BG = "#FFFFFF" # Pure white for dropdowns/inputs in light mode
    WIDGET_TEXT = "#0F172A"
    CHAT_INPUT_BG = "#FFFFFF"

# ---------------- GROQ ----------------

key = os.getenv("GROQ_API_KEY", "").strip()
groq = Groq(api_key=key) if key else None

# ---------------- PERSONAS & STYLES ----------------

PERSONAS = {
    "AI Medical Analyst": "You are an expert AI Medical Analyst. Help users understand medical reports, lab values, and clinical terms in simple, clear language. Do not diagnose or prescribe.",
    "Symptom Checker": "You are a supportive Symptom Checker assistant. Help users evaluate symptoms by asking clarifying questions, suggesting potential non-urgent explanations, and emphasizing professional medical consultation.",
    "Nutrition Coach": "You are a professional Nutrition Coach. Provide evidence-based guidance on healthy eating, macronutrients, meal planning, and balanced daily diets.",
    "General Health Advisor": "You are a friendly General Health Advisor focused on wellness, lifestyle improvements, sleep hygiene, and preventive health habits."
}

STYLES = {
    "Concise": {"max_tokens": 300, "instruction": " Keep your answer brief, direct, and straight to the point."},
    "Balanced": {"max_tokens": 600, "instruction": " Provide a well-rounded, clear, and structured response."},
    "Detailed": {"max_tokens": 1200, "instruction": " Provide an in-depth, comprehensive breakdown with structured sections, explanations, and context."}
}

# ---------------- ADVANCED CSS INJECTION ----------------

st.markdown(
    f"""
    <style>
    /* Global Overrides */
    .stApp {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {PANEL} !important;
        border-right: 1px solid {BORDER} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}

    /* Force all text elements to respect theme */
    p, span, label, div {{
        color: {TEXT};
    }}

    /* Selectboxes / Inputs Visibility Fix */
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {WIDGET_BG} !important;
        color: {WIDGET_TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}

    .stSelectbox div[data-baseweb="select"] * {{
        color: {WIDGET_TEXT} !important;
    }}

    /* Buttons Fix */
    .stButton > button {{
        background-color: {WIDGET_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}

    .stButton > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
    }}

    /* Chat Messages */
    [data-testid="stChatMessage"] {{
        background-color: {PANEL} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
    }}

    /* Chat Input Bar */
    [data-testid="stChatInput"] {{
        background-color: {CHAT_INPUT_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 28px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {WIDGET_TEXT} !important;
        background: transparent !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    #MainMenu, footer {{
        display: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- EKG LOGO SVG ----------------
EKG_LOGO_SVG = '<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 32H18L24 18L32 46L40 22L46 32H60" stroke="' + ACCENT + '" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 10px 0 20px;">
            <div style="width:48px;height:48px;margin:0 auto 10px;display:flex;align-items:center;justify-content:center;border-radius:14px;background:rgba(0,180,216,0.1);border:1px solid {ACCENT};">
                {EKG_LOGO_SVG}
            </div>
            <h3 style="margin:0;font-size:16px;font-weight:bold;">AI HEALTHCARE</h3>
            <p style="margin:4px 0 0;font-size:11px;color:{MUTED};">Smart Assistant</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"<p style='font-size:11px;font-weight:bold;color:{MUTED};text-transform:uppercase;'>AI Persona / Model</p>", unsafe_allow_html=True)
    selected_persona = st.selectbox(
        "Persona",
        list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.ai_persona),
        label_visibility="collapsed",
    )
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        st.rerun()

    st.markdown(f"<p style='font-size:11px;font-weight:bold;color:{MUTED};text-transform:uppercase;margin-top:10px;'>Response Style</p>", unsafe_allow_html=True)
    selected_style = st.selectbox(
        "Style",
        list(STYLES.keys()),
        index=list(STYLES.keys()).index(st.session_state.response_style),
        label_visibility="collapsed",
    )
    if selected_style != st.session_state.response_style:
        st.session_state.response_style = selected_style
        st.rerun()

    st.markdown(f"<p style='font-size:11px;font-weight:bold;color:{MUTED};text-transform:uppercase;margin-top:10px;'>Accent Color</p>", unsafe_allow_html=True)
    new_accent = st.selectbox(
        "Accent",
        list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(st.session_state.accent),
        label_visibility="collapsed",
    )
    if new_accent != st.session_state.accent:
        st.session_state.accent = new_accent
        st.rerun()

    st.markdown(f"<p style='font-size:11px;font-weight:bold;color:{MUTED};text-transform:uppercase;margin-top:10px;'>Appearance</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "Light"
            st.rerun()
    with c2:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "Dark"
            st.rerun()

    st.markdown(f"<hr style='border-color:{BORDER};margin:15px 0;'>", unsafe_allow_html=True)
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- HERO OR CHAT ----------------

if not st.session_state.messages:
    st.markdown(
        f"""
        <div style="max-width:750px; margin:40px auto; padding:40px; text-align:center; background:{PANEL}; border:1px solid {BORDER}; border-radius:24px; box-shadow: 0 10px 30px rgba(0,0,0,0.03);">
            <div style="width:64px;height:64px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;border-radius:18px;background:rgba(0,180,216,0.1);border:1.5px solid {ACCENT};">
                {EKG_LOGO_SVG}
            </div>
            <h1 style="font-size:42px;font-weight:800;margin:0 0 10px;line-height:1.1;">AI Healthcare <span style="color:{ACCENT};">Assistant</span></h1>
            <p style="font-size:15px;color:{MUTED};max-width:550px;margin:0 auto 20px;">Understand medical reports, check symptoms, and get wellness guidance safely.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🩺 Explain Blood Test (CBC)", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Can you explain the basic components of a CBC test?"})
            st.rerun()
    with col2:
        if st.button("🥗 Heart-Healthy Diet Tips", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What are the core components of a heart-healthy daily diet?"})
            st.rerun()
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "file_name" in msg and msg["file_name"]:
                st.info(f"📎 Attached file: **{msg['file_name']}**")
            st.markdown(msg["content"])

# ---------------- CHAT INPUT ----------------

user_submission = st.chat_input("Ask Gemini or attach a report...", accept_file=True, file_type=["png", "jpg", "jpeg", "pdf", "txt"])

if user_submission:
    user_text = user_submission.text if hasattr(user_submission, "text") else str(user_submission)
    uploaded_files = user_submission.files if hasattr(user_submission, "files") else []
    file_name = uploaded_files[0].name if uploaded_files else None
    prompt_content = user_text if user_text else "Please analyze this attached file."

    st.session_state.messages.append({"role": "user", "content": prompt_content, "file_name": file_name})

    answer = "Please configure GROQ_API_KEY to enable AI responses."
    if groq:
        try:
            system_content = PERSONAS[st.session_state.ai_persona] + STYLES[st.session_state.response_style]["instruction"]
            max_tok = STYLES[st.session_state.response_style]["max_tokens"]

            user_content_payload = [{"type": "text", "text": prompt_content}]
            if uploaded_files:
                file_bytes = uploaded_files[0].getvalue()
                if uploaded_files[0].type in ["image/png", "image/jpeg"]:
                    encoded = base64.b64encode(file_bytes).decode("utf-8")
                    user_content_payload.append({"type": "image_url", "image_url": {"url": f"data:{uploaded_files[0].type};base64,{encoded}"}})

            r = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": system_content}, {"role": "user", "content": user_content_payload}],
                temperature=0.2,
                max_tokens=max_tok,
            )
            answer = r.choices[0].message.content
        except Exception as e:
            answer = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
