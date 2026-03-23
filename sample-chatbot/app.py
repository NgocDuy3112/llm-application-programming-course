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
from orchestrator.rag import SimpleRAG

from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface


load_dotenv(dotenv_path=".env", override=True)



def get_memory(mode: ContextManagementMode):
    global_logger.debug(f"Creating memory with mode: {mode}")
    match mode:
        case ContextManagementMode.OFF.value:
            return None
        case ContextManagementMode.SLIDING_WINDOW.value:
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



@st.cache_resource(show_spinner="Đang khởi tạo RAG (embedding model + vector DB)...")
def get_rag() -> SimpleRAG:
    """Khởi tạo SimpleRAG 1 lần duy nhất, cache lại giữa các lần rerun."""
    global_logger.debug("Initializing SimpleRAG instance")
    return SimpleRAG(
        collection_name="knowledge_base",
        embedding_model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        cross_encoder_model_name=os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
        chroma_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
    )



def get_chatbot_engine(provider: Provider) -> FullChatbotEngine:
    global_logger.debug(f"Creating chatbot engine for provider: {provider}")
    adapter = get_adapter(provider)
    memory = get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
    return FullChatbotEngine(adapter=adapter, memory=memory)



def main():
    st.set_page_config(layout="wide")
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = Provider.GROQ.value
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "openai/gpt-oss-20b"

    # Khởi tạo RAG và đưa vào session_state + tools module
    rag = get_rag()
    st.session_state["rag"] = rag
    set_rag_instance(rag)

    # Pass provider as parameter so cache is invalidated when it changes
    engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
    render_sidebar()
    render_chat_interface(engine=engine)



if __name__ == "__main__":
    main()