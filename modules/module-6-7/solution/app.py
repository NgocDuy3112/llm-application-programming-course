import os
import sys
import streamlit as st
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.full_engine import FullChatbotEngine



@st.cache_resource()
def get_chatbot_engine(provider: str):
    return FullChatbotEngine(provider=provider)



def main():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = "groq"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
    
    # Pass provider as parameter so cache is invalidated when it changes
    engine = get_chatbot_engine(provider=st.session_state.selected_provider)
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()