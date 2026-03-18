import os
import sys
import streamlit as st
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, ContextManagementMode
from model.adapter import *

from orchestrator.tools import *
from orchestrator.memory import *
from orchestrator.engine import FullChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface



def get_memory(mode: ContextManagementMode):
    global_logger.debug(f"Creating memory with mode: {mode}")
    match mode:
        case ContextManagementMode.OFF.value:
            return None
        case ContextManagementMode.SLIDING_WINDOW.value:
            window_size = st.session_state.get("sliding_window_turns", 5)
            return WindowMemory(memory=st.session_state.get("chat_history", []), sliding_window_size=window_size)
        case ContextManagementMode.RELEVANCE_FILTERING.value:
            global_logger.warning("RELEVANCE_FILTERING chưa được triển khai, fallback về SLIDING_WINDOW")
            window_size = st.session_state.get("sliding_window_turns", 5)
            return WindowMemory(memory=st.session_state.get("chat_history", []), sliding_window_size=window_size)
        case _:
            global_logger.error(f"Unsupported context management mode: {mode}")
            raise ValueError(f"Chế độ quản lý ngữ cảnh không hợp lệ: {mode}")



@st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider) -> BaseAdapter:
    global_logger.debug(f"Creating adapter for provider: {provider}")
    match provider:
        case Provider.GROQ:
            return GroqAdapter()
        case Provider.OLLAMA:
            return OllamaAdapter()
        case _:
            global_logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Không hỗ trợ nhà cung cấp {provider}")



def get_chatbot_engine(provider: Provider) -> FullChatbotEngine:
    global_logger.debug(f"Creating chatbot engine for provider: {provider}")
    adapter = get_adapter(provider)
    memory = get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
    return FullChatbotEngine(adapter=adapter, memory=memory)



def main():
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"
    # Pass provider as parameter so cache is invalidated when it changes
    engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()