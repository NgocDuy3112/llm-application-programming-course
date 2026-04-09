"""
Module 5 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần:
- UI components (sidebar, chat interface)
- Model adapters (Groq, Ollama)

Cách chạy:
   streamlit run app.py
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, MODELS_BY_PROVIDER

from model.adapter import GroqAdapter, OllamaAdapter
from orchestrator.engine import ChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface


@st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider):
    """
    Factory function với caching để tạo adapter cho LLM provider.
    """
    match provider:
        case Provider.GROQ:
            return GroqAdapter()
        case Provider.OLLAMA:
            return OllamaAdapter()
        case _:
            raise ValueError(f"Không hỗ trợ nhà cung cấp {provider}")


def get_chatbot_engine(provider: Provider):
    """
    Tạo và trả về chatbot engine với adapter được cấu hình.
    """
    adapter = get_adapter(provider)
    return ChatbotEngine(adapter=adapter)


def main():
    """
    Entry point của Streamlit application.
    """
    st.set_page_config(layout="wide")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]

    engine = get_chatbot_engine(Provider(st.session_state.selected_provider))

    render_sidebar()
    render_chat_interface(engine=engine)


if __name__ == "__main__":
    main()