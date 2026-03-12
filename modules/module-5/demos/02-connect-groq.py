import os
import sys

import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.engine import ChatbotEngine



@st.cache_resource()
def get_chatbot_engine():
    return ChatbotEngine()


def main():
    engine = get_chatbot_engine()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()