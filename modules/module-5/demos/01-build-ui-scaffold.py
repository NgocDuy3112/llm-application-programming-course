import os
import sys
from dotenv import load_dotenv
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from core.ui.sidebar import render_sidebar
from core.ui.chat_interface import render_chat_interface
from core.orchestrator.engine import FakeChatbotEngine


load_dotenv(override=True)



def main():
    engine = FakeChatbotEngine()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    render_sidebar()
    render_chat_interface(orchestrator_engine=engine)



if __name__ == "__main__":
    main()