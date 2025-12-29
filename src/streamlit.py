# ui_streamlit.py
import streamlit as st
import requests
from st_chat_message import message
from st_on_hover_tabs import on_hover_tabs

# -----------------------------
# Page Config + Style
# -----------------------------
st.set_page_config(
    layout="wide",
    page_title="AI Task Assistant",
    page_icon="🤖"
)

st.markdown(
    '<style>' + open('./style.css').read() + '</style>',
    unsafe_allow_html=True
)

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="header-container">
    <div class="sub-header-content">
        <h1 class="header-title">🤖 AI Task Assistant</h1>
        <p class="header-subtitle">
            Ask anything about Task Management System
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    tabs = on_hover_tabs(
        tabName=['Chat Bot', 'About'],
        iconName=['chat', 'info'],
        default_choice=0
    )
    show_sources = st.toggle("Show Retrieved Sources", value=False)

# -----------------------------
# Chat Bot Page
# -----------------------------
if tabs == 'Chat Bot':

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # render history
    for i, chat in enumerate(st.session_state.chat_history):
        message(
            chat["content"],
            is_user=(chat["role"] == "user"),
            key=f"msg_{i}"
        )

    # user input
    if user_input := st.chat_input("Ask about the system..."):
        message(user_input, is_user=True)
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        # call RAG system via FastAPI
        if "thread_id" not in st.session_state:
            st.session_state.thread_id = "streamlit_session_1"

        try:
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={
                    "query": user_input,
                    "thread_id": st.session_state.thread_id
                }
            )
            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                sources = data["sources"]
            else:
                answer = f"Error: {response.status_code} - {response.text}"
                sources = []
        except Exception as e:
            answer = f"Connection Error: {str(e)}"
            sources = []
        message(answer, is_user=False)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        # optional debug
        if show_sources and sources:
            with st.expander("🔍 Retrieved Sources"):
                for src in sources:
                    st.text(src)

# -----------------------------
# About Page
# -----------------------------
elif tabs == 'About':
    st.subheader("About this Chatbot")
    st.write("""
    This system is a Retrieval-Augmented Generation (RAG) chatbot
    designed for answering questions about a Task Management System.
    """)
