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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# CUSTOM STYLING (MATCHING THE EXACT DARK THEME & ACCENT)
# ------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #090a0f;
    color: #f3f4f6;
}
section[data-testid="stSidebar"] {
    background-color: #0d0f17 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
.hero-box {
    border: 1px solid rgba(244, 63, 94, 0.4);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    background: #12141c;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border: 1px solid rgba(244, 63, 94, 0.5);
    border-radius: 20px;
    color: #f43f5e;
    font-size: 0.85rem;
    margin-top: 10px;
}
.notice-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 15px;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #9ca3af;
    margin-bottom: 10px;
}
.disclaimer-box {
    background: rgba(245, 158, 11, 0.05);
    border: 1px solid rgba(245, 158, 11, 0.2);
    padding: 10px 15px;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #fbbf24;
    margin-bottom: 20px;
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
# SESSION STATE
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "AI Medical Analyst"

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🩺 AI Healthcare")
    st.caption("Smart health information assistant")
    st.markdown("---")
    
    st.markdown("**💬 Chat History**")
    if not st.session_state.messages:
        st.caption("No previous messages yet.")
    
    st.markdown("---")
    st.session_state.app_mode = st.selectbox("Assistant Mode", ["AI Medical Analyst", "Symptom Checker", "Nutrition Coach"])
    response_style = st.selectbox("Response Style", ["Balanced", "Concise", "Detailed"])
    accent = st.selectbox("Accent", ["Rose", "Blue", "Emerald"])
    
    st.markdown("**🎨 Appearance**")
    c1, c2 = st.columns(2)
    with c1:
        st.button("☀️ Light", use_container_width=True)
    with c2:
        st.button("🌙 Dark", use_container_width=True)
    st.caption("Active theme: Dark")
    
    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------
# MAIN CONTENT AREA
# ------------------------------------------------------------
st.markdown("""
<div class="hero-box">
    <div style="font-size: 2.5rem; margin-bottom: 10px;">🩺</div>
    <h1 style="color: #f3f4f6; font-weight: 800; margin: 0; font-size: 2.2rem;">AI Healthcare Assistant</h1>
    <p style="color: #9ca3af; margin-top: 5px;">Understand medical reports and health information in simple language.</p>
    <div class="badge">AI Medical Analyst</div>
</div>
""", unsafe_allow_html=True)

# Quick Questions
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>Try a quick question</p>", unsafe_allow_html=True)
q1, q2 = st.columns(2)
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

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="notice-box">🔒 <b>Ephemeral Data Processing</b> — any medical document you attach is deleted automatically within 1 hour. Your chat history stays saved in this conversation.</div>', unsafe_allow_html=True)
st.markdown('<div class="disclaimer-box">⚠️ <b>Important:</b> This AI Healthcare Assistant provides general informational support only. It does not diagnose medical conditions, prescribe treatment, or replace advice from a qualified healthcare professional.</div>', unsafe_allow_html=True)

# Chat Messages
uploaded_file = st.file_uploader("Upload Medical Report", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

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
