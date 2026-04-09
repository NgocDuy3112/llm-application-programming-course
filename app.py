"""
Module 5 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần: UI, Model adapters, Memory management.

Cách chạy: streamlit run app.py

TODO 4: Hoàn thành toàn bộ ứng dụng Streamlit:
1. get_memory(mode): Factory function tạo memory object dựa trên chế độ
   - ContextManagementMode.OFF.value -> return None
   - ContextManagementMode.SLIDING_WINDOW.value -> return SlidingWindowMemory(sliding_window_size=st.session_state.get("sliding_window_turns", 5))

2. get_adapter(provider): Factory function với @st.cache_resource(show_spinner=True) để tạo adapter
   - Provider.GROQ -> return GroqAdapter()
   - Provider.OLLAMA -> return OllamaAdapter()

3. get_chatbot_engine(provider): Tạo ChatbotEngine(adapter=get_adapter(provider), memory=get_memory(...))

4. main(): Entry point
   - st.set_page_config(layout="wide")
   - Khởi tạo session_state defaults (selected_provider, selected_model)
   - engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
   - render_sidebar() và render_chat_interface(engine=engine)
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


# TODO 4: Hoàn thành get_memory(mode)
def get_memory(mode: ContextManagementMode):
    pass


# TODO 4: Hoàn thành get_adapter(provider) - nhớ thêm @st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider):
    pass


# TODO 4: Hoàn thành get_chatbot_engine(provider)
def get_chatbot_engine(provider: Provider):
    pass


# TODO 4: Hoàn thành main()
def main():
    pass


if __name__ == "__main__":
    main()