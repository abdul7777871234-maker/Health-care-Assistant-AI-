# -*- coding: utf-8 -*-
import os
from io import BytesIO
from PIL import Image
import streamlit as st
from google import genai
from google.genai import types
from groq import Groq

# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# ROBUST SIDEBAR & UI STYLING (FIXES HOSTED SIDEBAR BUG)
# ------------------------------------------------------------
st.markdown("""
<style>
/* Ensure sidebar and its toggle controls are always visible and interactive */
section[data-testid="stSidebar"] {
    background-color: #0d0f17 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    z-index: 100;
}

[data-testid="stSidebarNav"] {
    color: #f3f4f6;
}

/* Fix collapse / expand toggle visibility in cloud environments */
button[data-testid="stSidebarCollapsedControl"],
div[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 101 !important;
}

.stApp {
    background-color: #090a0f;
    color: #f3f4f6;
}

.hero {
    text-align: center;
    padding: 24px 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(244, 63, 94, 0.3);
    border-radius: 20px;
    background: #12141c;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f3f4f6 20%, #f43f5e 80%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# ENVIRONMENT & CLIENT SETUP
# ------------------------------------------------------------
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
GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "openai/gpt-oss-120b"

# ------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "AI Medical Analyst"
if "report_context" not in st.session_state:
    st.session_state.report_context = ""

# ------------------------------------------------------------
# SIDEBAR MENU (GUARANTEED VISIBILITY)
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🩺 AI Healthcare")
    st.caption("Smart health information assistant")
    st.markdown("---")
    
    st.session_state.app_mode = st.selectbox(
        "Assistant Mode", 
        ["AI Medical Analyst", "Symptom Checker", "Nutrition Coach"]
    )
    
    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.report_context = ""
        st.rerun()

# ------------------------------------------------------------
# MAIN UI HERO SECTION
# ------------------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-title">AI Healthcare Assistant</div>
    <p style="color: #9ca3af; margin: 0;">Mode: <b>{st.session_state.app_mode}</b></p>
</div>
""", unsafe_allow_html=True)

# File uploader & chat layout
uploaded_file = st.file_uploader("Upload Medical Report (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a health question or inquire about your report...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        report_analysis = st.session_state.report_context
        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
            
            with st.spinner("Analyzing report with Gemini..."):
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=["Extract key medical findings, values, and units clearly.", image_part]
                )
                report_analysis = response.text
                st.session_state.report_context = report_analysis

        with st.chat_message("assistant"):
            with st.spinner("Preparing answer..."):
                prompt = f"Medical Report: {report_analysis}\nUser Question: {user_input}"
                completion = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful healthcare assistant. Provide safe, structured guidance."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                answer = completion.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"An error occurred: {e}")
