import os
import sys
from dotenv import load_dotenv
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from core.ui.sidebar import render_sidebar
from core.ui.chat_interface import render_chat_interface
from core.orchestrator.engine import ChatbotEngine


load_dotenv(dotenv_path=".env", override=True)


@st.cache_resource()
def get_chatbot_engine():
    return ChatbotEngine(provider=st.session_state.selected_provider, api_key=os.getenv("GROQ_API_KEY"))


def main():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = "groq"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
    engine = get_chatbot_engine()
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()