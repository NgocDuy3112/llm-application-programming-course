# Module 5
import os
import sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface
from orchestrator.engine import ChatbotEngine


load_dotenv(override=True)



def main():
    st.set_page_config(page_title="Bài tập Module 5", layout="wide")
    # Khởi tạo engine
    engine = ChatbotEngine()
    
    # Khởi tạo lịch sử chat trong session_state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Render các thành phần UI
    render_sidebar()
    render_chat_interface(engine=engine)


if __name__ == "__main__":
    main()
