"""
Module 6-7 - Main Chatbot Application

Mô tả: Streamlit application chính cho demo chatbot. Ứng dụng này tích hợp
các thành phần:
- UI components (sidebar, chat interface)
- Model adapters (Groq, Ollama)
- Memory management (sliding window, unlimited)
- Tool orchestration

Kiến trúc / Dependencies:
- Streamlit: Web UI framework
- model.adapter: LLM providers abstraction
- orchestrator.engine: Chat processing logic
- orchestrator.memory: Context management
- ui.*: User interface components

Cách chạy:
   streamlit run exercises/app.py
"""

import os
import sys
import streamlit as st
# Thêm thư mục hiện tại vào PATH để import các module/các phần tử nội bộ
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_types import Provider, ContextManagementMode
from model.adapter import *

from orchestrator.tools import *
from orchestrator.memory import *
from orchestrator.engine import FullChatbotEngine

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface


def get_memory(mode: ContextManagementMode):
   """
   Factory function để tạo memory object dựa trên chế độ được chọn.

   Args:
      mode (ContextManagementMode): Chế độ quản lý ngữ cảnh
         - OFF: Không lưu lịch sử
         - SLIDING_WINDOW: Giữ lại k cặp messages gần nhất

   Returns:
      WindowMemory | None: Memory object hoặc None nếu tắt

   Raises:
      ValueError: Nếu mode không hợp lệ
   """
   global_logger.debug(f"Creating memory with mode: {mode}")
   match mode:
      case ContextManagementMode.OFF.value:
         global_logger.debug("Memory mode OFF - no history will be stored")
         return None
      case ContextManagementMode.SLIDING_WINDOW.value:
         window_size = st.session_state.get("sliding_window_turns", 5)
         global_logger.debug(f"Memory mode SLIDING_WINDOW with {window_size} turns")
         return WindowMemory(memory=st.session_state.get("chat_history", []), sliding_window_size=window_size)
      case _:
         global_logger.error(f"Unsupported context management mode: {mode}")
         raise ValueError(f"Chế độ quản lý ngữ cảnh không hợp lệ: {mode}")



@st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider) -> BaseAdapter:
   """
   Factory function với caching để tạo adapter cho LLM provider.

   Sử dụng @st.cache_resource để tránh tạo lại adapter mỗi khi rerun,
   giúp tiết kiệm tài nguyên và tăng tốc độ phản hồi.

   Args:
      provider (Provider): Nhà cung cấp LLM (GROQ hoặc OLLAMA)

   Returns:
      BaseAdapter: Adapter đã khởi tạo cho provider

   Raises:
      ValueError: Nếu provider không được hỗ trợ
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


def get_chatbot_engine(provider: Provider) -> FullChatbotEngine:
   """
   Tạo và trả về chatbot engine với adapter và memory được cấu hình.

   Args:
      provider (Provider): Nhà cung cấp LLM để sử dụng

   Returns:
      FullChatbotEngine: Engine đã được cấu hình đầy đủ
   """
   global_logger.debug(f"Creating chatbot engine for provider: {provider}")
   adapter = get_adapter(provider)
   memory = get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
   global_logger.info(f"Chatbot engine created with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__ if memory else 'None'}")
   return FullChatbotEngine(adapter=adapter, memory=memory)


def main():
   """
   Entry point của Streamlit application.

   Khởi tạo:
   - Page configuration
   - Session state defaults
   - Chatbot engine
   - UI components (sidebar, chat interface)
   """
   st.set_page_config(layout="wide")
   # Initialize session state defaults if not present
   if "selected_provider" not in st.session_state:
      st.session_state.selected_provider = Provider.GROQ.value
   if "selected_model" not in st.session_state:
      st.session_state.selected_model = "openai/gpt-oss-20b"
    
   # Create chatbot engine with current provider
   engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
    
   # Render UI components
   render_sidebar()
   render_chat_interface(engine=engine)



if __name__ == "__main__":
   main()
