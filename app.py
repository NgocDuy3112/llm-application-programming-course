"""
Module 5 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần:
- UI components (sidebar, chat interface)
- Model adapter (Groq)

Cách chạy:
   streamlit run app.py
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, ContextManagementMode, MODELS_BY_PROVIDER

from orchestrator.engine import ChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface


def main():
    """
    Entry point của Streamlit application.
    """
    st.set_page_config(layout="wide")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    engine = ChatbotEngine()

    render_sidebar()
    render_chat_interface(engine=engine)


if __name__ == "__main__":
    main()