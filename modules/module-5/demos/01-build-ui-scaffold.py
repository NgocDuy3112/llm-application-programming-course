import os
import sys
from dotenv import load_dotenv
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.engine import FakeChatbotEngine


load_dotenv(dotenv_path=".env", override=True)



def main():
    engine = FakeChatbotEngine()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()