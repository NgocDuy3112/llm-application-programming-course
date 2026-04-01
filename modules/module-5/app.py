"""
Module 5 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần:
- UI components (sidebar, chat interface)
- Model adapters (Groq, Ollama)
- Memory management (sliding window)

Cách chạy:
   streamlit run module-5/app.py
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, ContextManagementMode, MODELS_BY_PROVIDER

from model.adapter import GroqAdapter, OllamaAdapter
from orchestrator.memory import SlidingWindowMemory
from orchestrator.engine import ChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface


def get_memory(mode: ContextManagementMode):
    """
    Factory function để tạo memory object dựa trên chế độ được chọn.
    """
    global_logger.debug(f"Creating memory with mode: {mode}")
    match mode:
        case ContextManagementMode.OFF.value:
            global_logger.debug("Memory mode OFF - no history will be stored")
            return None
        case ContextManagementMode.SLIDING_WINDOW.value:
            window_size = st.session_state.get("sliding_window_turns", 5)
            global_logger.debug(f"Memory mode SLIDING_WINDOW with {window_size} turns")
            return SlidingWindowMemory(sliding_window_size=window_size)
        case _:
            global_logger.error(f"Unsupported context management mode: {mode}")
            raise ValueError(f"Chế độ quản lý ngữ cảnh không hợp lệ: {mode}")


@st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider):
    """
    Factory function với caching để tạo adapter cho LLM provider.
    """
    global_logger.debug(f"Creating adapter for provider: {provider}")
    match provider:
        case Provider.GROQ:
            global_logger.info("Using Groq adapter for cloud-based inference")
            return GroqAdapter()
        case Provider.OLLAMA:
            global_logger.info("Using Ollama adapter for local inference")
            return OllamaAdapter()
        case _:
            global_logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Không hỗ trợ nhà cung cấp {provider}")


def get_chatbot_engine(provider: Provider):
    """
    Tạo và trả về chatbot engine với adapter và memory được cấu hình.
    """
    global_logger.debug(f"Creating chatbot engine for provider: {provider}")
    adapter = get_adapter(provider)
    memory = get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
    global_logger.info(f"Chatbot engine created with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__ if memory else 'None'}")
    return ChatbotEngine(adapter=adapter, memory=memory)


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