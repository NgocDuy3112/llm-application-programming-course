"""Bài tập Buổi 7 — Tích hợp RAG vào ứng dụng chatbot.

Nhiệm vụ:
  TODO 1: Implement get_rag() factory function
  TODO 2: Khởi tạo RAG trong main() và kết nối vào tools
"""

import os
import sys
import streamlit as st
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from custom_types import Provider, ContextManagementMode
from model.adapter import *

from orchestrator.tools import *
from orchestrator.tools import set_rag_instance
from orchestrator.memory import *
from orchestrator.engine import FullChatbotEngine

from excercise.ui.sidebar import render_sidebar
from excercise.ui.chat_interface import render_chat_interface

load_dotenv(dotenv_path=".env", override=True)


# ================================================================
# CÁC FACTORY FUNCTIONS SẴN CÓ — KHÔNG CẦN SỬA
# ================================================================

def get_memory(mode: ContextManagementMode):
    match mode:
        case ContextManagementMode.OFF.value:
            return None
        case ContextManagementMode.SLIDING_WINDOW.value:
            window_size = st.session_state.get("sliding_window_turns", 5)
            return SlidingWindowMemory(
                memory=st.session_state.get("chat_history", []),
                sliding_window_size=window_size
            )
        case _:
            raise ValueError(f"Chế độ không hợp lệ: {mode}")


@st.cache_resource(show_spinner=True)
def get_adapter(provider: Provider) -> BaseAdapter:
    match provider:
        case Provider.GROQ:
            return GroqAdapter()
        case Provider.OLLAMA:
            return OllamaAdapter()
        case _:
            raise ValueError(f"Không hỗ trợ provider: {provider}")


def get_chatbot_engine(provider: Provider) -> FullChatbotEngine:
    adapter = get_adapter(provider)
    memory = get_memory(
        st.session_state.get("context_management_mode", ContextManagementMode.OFF.value)
    )
    return FullChatbotEngine(adapter=adapter, memory=memory)


# ================================================================
# TODO 1: RAG Factory
# ================================================================

@st.cache_resource(show_spinner="Đang khởi tạo RAG model...")
def get_rag():
    """
    Tạo và cache SimpleRAG instance.

    Returns:
        SimpleRAG: Instance đã được khởi tạo

    Các bước cần làm:
        1. Import SimpleRAG từ orchestrator.rag
        2. Đọc embedding model từ env:
           os.getenv("EMBEDDING_MODEL", "AITeamVN/Vietnamese_Embedding_v2")
        3. Đọc cross encoder từ env:
           os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        4. Xác định chroma_path:
           os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        5. Trả về SimpleRAG(embedding_model_name=..., cross_encoder_model_name=..., chroma_path=...)
    """
    # YOUR CODE HERE
    raise NotImplementedError("TODO 1: Implement get_rag()")


# ================================================================
# TODO 2: Cập nhật main()
# ================================================================

def main():
    st.set_page_config(layout="wide")

    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"

    # TODO: Khởi tạo RAG và kết nối vào hệ thống
    # Các bước cần làm:
    #   1. rag = get_rag()
    #   2. st.session_state["rag"] = rag    ← để sidebar truy cập được
    #   3. set_rag_instance(rag)             ← để knowledge_base_search() dùng được
    # YOUR CODE HERE

    engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
    render_sidebar()
    render_chat_interface(engine=engine)


if __name__ == "__main__":
    main()
