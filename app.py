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
    "Sunset": ("#EA580C", "rgba(234,88,12,.15)"),
    "Neon Purple": ("#9333EA", "rgba(147,51,234,.15)"),
    "Cyber Pink": ("#DB2777", "rgba(219,39,119,.15)"),
    "Electric Lime": ("#16A34A", "rgba(22,163,74,.15)"),
    "Gold": ("#CA8A04", "rgba(202,138,4,.15)"),
    "Neon Orange": ("#C2410C", "rgba(194,65,12,.15)"),
    "Deep Teal": ("#0F766E", "rgba(15,118,110,.15)"),
    "Sky Blue": ("#0284C7", "rgba(2,132,199,.15)"),
}

ACCENT, GLOW = ACCENTS[st.session_state.accent]

if st.session_state.theme == "Dark":
    BG = "#050811"
    PANEL = "#0B1120"
    PANEL2 = "#101827"
    TEXT = "#F7FAFF"
    MUTED = "#97A4B8"
    BORDER = "rgba(255,255,255,.09)"
    SELECT_BG = "#0B1120"
    SELECT_TEXT = "#F7FAFF"
    BTN_BG = "#101827"
    BOTTOM_BG = "#050811"
    CHAT_BG = "#0B1120"
    CHAT_INPUT_BG = "#0B1120"
    CHAT_INPUT_TEXT = "#F7FAFF"
else:
    BG = "#FFFFFF"
    PANEL = "#F8FAFC"
    PANEL2 = "#F1F5F9"
    TEXT = "#0F172A"
    MUTED = "#64748B"
    BORDER = "rgba(15,23,42,.12)"
    SELECT_BG = "#FFFFFF"
    SELECT_TEXT = "#0F172A"
    BTN_BG = "#FFFFFF"
    BOTTOM_BG = "#FFFFFF"
    CHAT_BG = "#F1F5F9"
    CHAT_INPUT_BG = "#0B1120"
    CHAT_INPUT_TEXT = "#F7FAFF"

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

# ---------------- CSS ----------------

st.markdown(
    f"""
    <style>
    :root {{
        --accent:{ACCENT};
        --glow:{GLOW};
        --bg:{BG};
        --panel:{PANEL};
        --panel2:{PANEL2};
        --text:{TEXT};
        --muted:{MUTED};
        --border:{BORDER};
        --select-bg:{SELECT_BG};
        --select-text:{SELECT_TEXT};
        --btn-bg:{BTN_BG};
        --bottom-bg:{BOTTOM_BG};
        --chat-bg:{CHAT_BG};
        --chat-input-bg:{CHAT_INPUT_BG};
        --chat-input-text:{CHAT_INPUT_TEXT};
    }}

    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"] {{
        background:var(--bg)!important;
    }}

    .stApp {{
        background: var(--bg)!important;
        color: var(--text)!important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: var(--chat-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }}

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] li {{
        color: var(--text) !important;
        font-weight: 500;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    #MainMenu, footer {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] {{
        background: var(--panel) !important;
        border-right: 1px solid var(--border) !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: var(--select-bg) !important;
        color: var(--select-text) !important;
        border-color: var(--border) !important;
    }}

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {{
        color: var(--select-text) !important;
    }}

    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {{
        background-color: var(--select-bg) !important;
        border: 1px solid var(--border) !important;
    }}

    div[data-baseweb="menu"] div {{
        color: var(--select-text) !important;
    }}

    div.stButton > button {{
        background-color: var(--btn-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }}

    [data-testid="stChatInput"] {{
        background-color: var(--chat-input-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 24px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,.06) !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: var(--chat-input-text) !important;
        background: transparent !important;
    }}

    [data-testid="stChatInput"] button {{
        color: var(--chat-input-text) !important;
    }}

    [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] {{
        background: var(--bottom-bg) !important;
    }}

    @keyframes breathe {{
        0%, 100% {{
            transform: scale(1);
            box-shadow: 0 0 15px var(--glow), inset 0 0 8px var(--glow);
        }}
        50% {{
            transform: scale(1.05);
            box-shadow: 0 0 25px var(--accent), inset 0 0 12px var(--accent);
        }}
    }}

    .breathing-icon {{
        animation: breathe 3.5s ease-in-out infinite;
    }}

    .brand-box {{
        padding: 12px 5px 18px;
        margin-bottom: 12px;
        border-bottom: 1px solid var(--border);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}

    .brand-icon {{
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        border-radius: 16px;
        background: radial-gradient(circle, var(--glow), transparent 72%);
        border: 1.5px solid var(--accent);
    }}

    .brand-icon svg {{
        width: 28px;
        height: 28px;
        filter: drop-shadow(0 0 4px var(--glow));
    }}

    .brand-title {{
        color: var(--text);
        font-size: 15px;
        font-weight: 800;
        letter-spacing: .9px;
    }}

    .brand-caption {{
        color: var(--muted);
        font-size: 11px;
        margin-top: 3px;
        line-height: 1.4;
    }}

    .sidebar-label {{
        color: var(--muted);
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 12px 0 4px;
    }}

    .hero {{
        position: relative;
        max-width: 800px;
        margin: 12px auto 0;
        padding: 38px 24px 34px;
        text-align: center;
        overflow: hidden;
        border-radius: 26px;
        background: var(--panel);
        border: 1px solid var(--border);
        box-shadow: 0 20px 50px rgba(0,0,0,.04);
    }}

    .hero::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 12%;
        right: 12%;
        height: 2px;
        background: linear-gradient(90deg,transparent,var(--accent),transparent);
        box-shadow: 0 0 18px var(--glow);
    }}

    .hero-glow {{
        position: absolute;
        width: 280px;
        height: 160px;
        top: -105px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--glow);
        filter: blur(65px);
    }}

    .hero-icon {{
        position: relative;
        width: 72px;
        height: 72px;
        margin: 0 auto 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
        background: radial-gradient(circle,var(--glow),transparent 72%);
        border: 1.5px solid var(--accent);
    }}

    .hero-icon svg {{
        width: 36px;
        height: 36px;
        filter: drop-shadow(0 0 6px var(--glow));
    }}

    .hero-title {{
        position: relative;
        color: var(--text);
        font-size: 48px;
        font-weight: 850;
        line-height: .98;
        letter-spacing: -2px;
    }}

    .hero-title-accent {{
        color: var(--accent);
    }}

    .hero-description {{
        position: relative;
        max-width: 600px;
        margin: 16px auto 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.6;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        margin-top: 17px;
        padding: 7px 13px;
        border-radius: 999px;
        color: var(--accent);
        background: var(--glow);
        border: 1px solid var(--accent);
        font-size: 11px;
        font-weight: 800;
    }}

    .hero-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 8px var(--accent);
    }}

    .suggestions-title {{
        max-width: 800px;
        margin: 23px auto 10px;
        color: var(--muted);
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .suggestions div.stButton > button {{
        height: 56px!important;
        min-height: 56px!important;
        padding: 8px 12px!important;
        border-radius: 13px!important;
        background-color: var(--btn-bg)!important;
        background-image: none !important;
        border: 1px solid var(--border)!important;
        color: var(--text)!important;
        font-size: 11px!important;
        font-weight: 700!important;
        box-shadow: 0 4px 14px rgba(0,0,0,.03)!important;
    }}

    .suggestions div.stButton > button:hover {{
        color: var(--accent)!important;
        border-color: var(--accent)!important;
        box-shadow: 0 0 18px var(--glow)!important;
        transform: translateY(-1px);
    }}

    .notice {{
        max-width: 800px;
        margin: 16px auto 7px;
        padding: 9px 13px;
        text-align: center;
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--muted);
        background: var(--panel);
        font-size: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,.01);
    }}

    .disclaimer {{
        max-width: 800px;
        margin: auto;
        padding: 10px 13px;
        text-align: center;
        border: 1px solid rgba(217,119,6,.20);
        border-radius: 10px;
        color: #B45309;
        background: rgba(217,119,6,.03);
        font-size: 10px;
    }}

    @media(max-width: 700px) {{
        .hero {{ padding: 28px 16px 25px; }}
        .hero-title {{ font-size: 38px; }}
        .hero-description {{ font-size: 14px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

EKG_LOGO_SVG = '<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 32H18L24 18L32 46L40 22L46 32H60" stroke="var(--accent)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

with st.sidebar:
    st.markdown(
        f"""
<div class="brand-box">
    <div class="brand-icon breathing-icon">
        {EKG_LOGO_SVG}
    </div>
    <div class="brand-title">AI HEALTHCARE</div>
    <div class="brand-caption">Smart health information assistant</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">AI Persona / Model</div>', unsafe_allow_html=True)
    selected_persona = st.selectbox(
        "Persona",
        list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.ai_persona),
        label_visibility="collapsed",
    )
    if selected_persona != st.session_state.ai_persona:
        st.session_state.ai_persona = selected_persona
        st.rerun()

    st.markdown('<div class="sidebar-label">Response Style</div>', unsafe_allow_html=True)
    selected_style = st.selectbox(
        "Style",
        list(STYLES.keys()),
        index=list(STYLES.keys()).index(st.session_state.response_style),
        label_visibility="collapsed",
    )
    if selected_style != st.session_state.response_style:
        st.session_state.response_style = selected_style
        st.rerun()

    st.markdown('<div class="sidebar-label">Accent Color</div>', unsafe_allow_html=True)
    new_accent = st.selectbox(
        "Accent",
        list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(st.session_state.accent),
        label_visibility="collapsed",
    )
    if new_accent != st.session_state.accent:
        st.session_state.accent = new_accent
        st.rerun()

    st.markdown('<div class="sidebar-label">Appearance</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "Light"
            st.rerun()
    with c2:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "Dark"
            st.rerun()

    st.markdown(
        f'<div style="font-size:10px;color:var(--muted);margin-top:4px">Theme: <b style="color:var(--accent)">{st.session_state.theme}</b></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='margin:15px 0 10px; border-color:var(--border);'>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:10px;color:var(--muted);margin-bottom:8px">💬 Messages in session: <b>{len(st.session_state.messages)}</b></div>', unsafe_allow_html=True)
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.messages:
    st.markdown(
        f"""
<div class="hero">
    <div class="hero-glow"></div>
    <div class="hero-icon breathing-icon">
        {EKG_LOGO_SVG}
    </div>
    <div class="hero-title">
        AI Healthcare<br>
        <span class="hero-title-accent">Assistant</span>
    </div>
    <div class="hero-description">
        Understand medical reports, check symptoms, and get wellness guidance in simple terms.
    </div>
    <div class="hero-badge">
        <span class="hero-dot"></span>
        {st.session_state.ai_persona} ({st.session_state.response_style})
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="suggestions-title">Suggested questions</div>', unsafe_allow_html=True)

    suggestions = [
        "🩸 Blood test basics",
        "🥗 Heart-healthy diet",
        "⚡ Causes of fatigue",
        "💊 Medication side effects",
    ]

    prompts = [
        "Can you explain the basic components of a CBC test?",
        "What are the core components of a heart-healthy daily diet?",
        "What are common causes of chronic fatigue?",
        "How can I safely check medication side effects?",
    ]

    st.markdown('<div class="suggestions">', unsafe_allow_html=True)
    a, b = st.columns(2, gap="small")

    for i, label in enumerate(suggestions):
        col = a if i % 2 == 0 else b
        with col:
            if st.button(label, use_container_width=True, key=f"question_{i}"):
                st.session_state.messages.append({"role": "user", "content": prompts[i]})
                answer = "Please configure GROQ_API_KEY to enable AI responses."

                if groq:
                    try:
                        system_content = PERSONAS[st.session_state.ai_persona] + STYLES[st.session_state.response_style]["instruction"]
                        max_tok = STYLES[st.session_state.response_style]["max_tokens"]

                        r = groq.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": system_content},
                                {"role": "user", "content": prompts[i]},
                            ],
                            temperature=0.2,
                            max_tokens=max_tok,
                        )
                        answer = r.choices[0].message.content
                    except Exception as e:
                        answer = f"Unable to respond: {e}"

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="notice">🔒 Your health information is processed to provide the requested assistance.</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer">⚠ Clinical Disclaimer: This assistant provides general informational support only and does not replace professional medical advice.</div>', unsafe_allow_html=True)

else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "file_name" in msg and msg["file_name"]:
                st.info(f"📎 Attached file for analysis: **{msg['file_name']}**")
            st.markdown(msg["content"])

user_submission = st.chat_input(
    "Ask Gemini or attach a report...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "pdf", "txt"]
)

if user_submission:
    user_text = user_submission.text if hasattr(user_submission, "text") else str(user_submission)
    uploaded_files = user_submission.files if hasattr(user_submission, "files") else []
    
    file_name = uploaded_files[0].name if uploaded_files else None
    prompt_content = user_text if user_text else "Please analyze this attached medical report/image."
    
    st.session_state.messages.append({"role": "user", "content": prompt_content, "file_name": file_name})

    with st.chat_message("user"):
        if file_name:
            st.info(f"📎 Attached file for analysis: **{file_name}**")
        st.markdown(prompt_content)

    answer = "Please configure GROQ_API_KEY to enable AI responses."

    if groq:
        try:
            system_content = PERSONAS[st.session_state.ai_persona] + STYLES[st.session_state.response_style]["instruction"]
            max_tok = STYLES[st.session_state.response_style]["max_tokens"]
            
            user_content_payload = []
            
            if uploaded_files:
                uploaded_file = uploaded_files[0]
                file_bytes = uploaded_file.getvalue()
                if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                    user_content_payload.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{uploaded_file.type};base64,{encoded_image}"
                        }
                    })
                else:
                    try:
                        file_text = file_bytes.decode("utf-8", errors="ignore")
                        prompt_content += f"\n--- Attached File Content ---\n{file_text}"
                    except Exception:
                        pass

            user_content_payload.append({
                "type": "text",
                "text": prompt_content
            })

            r = groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content_payload},
                ],
                temperature=0.2,
                max_tokens=max_tok,
            )
            answer = r.choices[0].message.content
        except Exception as e:
            answer = f"Unable to respond: **{e}**"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
