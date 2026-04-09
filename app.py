"""
Module 5 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần:
- UI components (sidebar, chat interface)
- Model adapters (Groq, Ollama)
- Memory management (sliding window)

Cách chạy:
   streamlit run app.py

TODO: Hoàn thành các factory functions và hàm main dưới đây:

1. get_memory(mode):
   - Factory function tạo memory object dựa trên chế độ được chọn
   - ContextManagementMode.OFF -> return None
   - ContextManagementMode.SLIDING_WINDOW -> return SlidingWindowMemory(sliding_window_size=window_size)

2. get_adapter(provider):
   - Factory function với caching (@st.cache_resource) để tạo adapter
   - Provider.GROQ -> return GroqAdapter()
   - Provider.OLLAMA -> return OllamaAdapter()

3. get_chatbot_engine(provider):
   - Tạo và trả về ChatbotEngine với adapter và memory được cấu hình
   - Lấy adapter từ get_adapter(provider)
   - Lấy memory từ get_memory(st.session_state.get("context_management_mode"))

4. main():
   - Cấu hình trang Streamlit (layout="wide")
   - Khởi tạo session_state defaults (selected_provider, selected_model)
   - Tạo engine từ get_chatbot_engine()
   - Render sidebar và chat interface
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


# TODO 1: Hoàn thành hàm get_memory(mode)
# Factory function để tạo memory object dựa trên chế độ được chọn.
# Sử dụng match/case để xử lý các chế độ:
# - ContextManagementMode.OFF.value -> return None
# - ContextManagementMode.SLIDING_WINDOW.value -> return SlidingWindowMemory(sliding_window_size=window_size)
#   với window_size = st.session_state.get("sliding_window_turns", 5)
def get_memory(mode: ContextManagementMode):
    pass


# TODO 2: Hoàn thành hàm get_adapter(provider)
# Factory function với caching để tạo adapter cho LLM provider.
# Thêm decorator @st.cache_resource(show_spinner=True) để cache adapter
# Sử dụng match/case để xử lý các provider:
# - Provider.GROQ -> return GroqAdapter()
# - Provider.OLLAMA -> return OllamaAdapter()
def get_adapter(provider: Provider):
    pass


# TODO 3: Hoàn thành hàm get_chatbot_engine(provider)
# Tạo và trả về chatbot engine với adapter và memory được cấu hình.
# - Lấy adapter từ get_adapter(provider)
# - Lấy memory từ get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
# - Return ChatbotEngine(adapter=adapter, memory=memory)
def get_chatbot_engine(provider: Provider):
    pass


# TODO 4: Hoàn thành hàm main()
# Entry point của Streamlit application.
# - st.set_page_config(layout="wide")
# - Khởi tạo session_state defaults:
#   if "selected_provider" not in st.session_state:
#       st.session_state.selected_provider = Provider.GROQ.value
#   if "selected_model" not in st.session_state:
#       st.session_state.selected_model = MODELS_BY_PROVIDER[Provider.GROQ.value][0]
# - Tạo engine: engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
# - Render sidebar: render_sidebar()
# - Render chat interface: render_chat_interface(engine=engine)
def main():
    pass


if __name__ == "__main__":
    main()