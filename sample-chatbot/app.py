# Import os module để làm việc với paths và environment variables
import os
# Import sys module để làm việc với system-specific parameters
import sys
# Import streamlit - framework để xây dựng giao diện web app
import streamlit as st

# Thêm directory hiện tại vào sys.path để có thể import các modules từ project
# os.path.dirname(os.path.abspath(__file__)) trả về đường dẫn tuyệt đối của directory chứa file này
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import load_dotenv từ dotenv package để load environment variables từ file .env
from dotenv import load_dotenv
# Import Provider enum và ContextManagementMode enum từ custom_types module
from custom_types import Provider, ContextManagementMode
# Import tất cả các adapter classes từ model.adapter module
from model.adapter import *

# Import tất cả các functions/constants từ orchestrator.tools module
from orchestrator.tools import *
# Import set_rag_instance function từ orchestrator.tools
from orchestrator.tools import set_rag_instance
# Import tất cả các memory classes từ orchestrator.memory module
from orchestrator.memory import *
# Import FullChatbotEngine từ orchestrator.engine module
from orchestrator.engine import FullChatbotEngine
# Import SimpleRAG từ orchestrator.rag module
from orchestrator.rag import SimpleRAG

# Import render_sidebar function từ ui.sidebar module
from ui.sidebar import render_sidebar
# Import render_chat_interface function từ ui.chat_interface module
from ui.chat_interface import render_chat_interface


# Load environment variables từ file .env
# dotenv_path=".env" chỉ định file cần load
# override=True nghĩa là ghi đè lên các biến môi trường đã tồn tại
load_dotenv(dotenv_path=".env", override=True)


# Hàm factory để tạo memory instance dựa trên mode
def get_memory(mode: ContextManagementMode):
    """
    Factory function để tạo memory instance dựa trên context management mode.

    Args:
        Mode (ContextManagementMode): Chế độ quản lý ngữ cảnh
            - OFF: Không lưu lịch sử
            - SLIDING_WINDOW: Lưu k cặp messages gần nhất

    Returns:
        BaseMemory | None: Memory instance hoặc None nếu mode là OFF

    Raises:
        ValueError: Nếu mode không hợp lệ
    """
    # Ghi log debug: đang tạo memory với mode nào
    global_logger.debug(f"Creating memory with mode: {mode}")
    
    # Match-case statement (Python 3.10+) để xử lý các trường hợp mode khác nhau
    match mode:
        # Trường hợp: Tắt quản lý ngữ cảnh (OFF)
        case ContextManagementMode.OFF.value:
            # Trả về None - không lưu lịch sử
            return None
        
        # Trường hợp: Sliding window - chỉ giữ k cặp messages gần nhất
        case ContextManagementMode.SLIDING_WINDOW.value:
            # Lấy số turns từ session_state, default là 5
            # st.session_state.get() trả về giá trị hoặc default nếu key không tồn tại
            window_size = st.session_state.get("sliding_window_turns", 5)
            
            # Tạo và trả về WindowMemory instance
            # memory=st.session_state.get("chat_history", []) lấy lịch sử chat hiện tại
            # sliding_window_size=window_size đặt kích thước window
            return SlidingWindowMemory(sliding_window_size=window_size)
        
        # Default case: mode không hợp lệ
        case _:
            # Ghi log error: mode không được hỗ trợ
            global_logger.error(f"Unsupported context management mode: {mode}")
            # Raise ValueError với message tiếng Việt
            raise ValueError(f"Chế độ quản lý ngữ cảnh không hợp lệ: {mode}")


# Decorator @st.cache_resource để cache adapter instance giữa các lần rerun
# show_spinner=True hiển thị spinner trong khi đang khởi tạo
@st.cache_resource(show_spinner=True)
# Hàm factory để tạo adapter instance dựa trên provider
def get_adapter(provider: Provider) -> BaseAdapter:
    """
    Factory function để tạo model adapter dựa trên provider.

    Args:
        provider (Provider): Nhà cung cấp model (GROQ hoặc OLLAMA)

    Returns:
        BaseAdapter: Adapter instance tương ứng

    Raises:
        ValueError: Nếu provider không hợp lệ
    """
    # Ghi log debug: đang tạo adapter cho provider nào
    global_logger.debug(f"Creating adapter for provider: {provider}")
    
    # Match-case statement để xử lý các providers khác nhau
    match provider:
        # Trường hợp: Groq provider
        case Provider.GROQ:
            # Tạo và trả về GroqAdapter instance
            return GroqAdapter()
        
        # Trường hợp: Ollama provider
        case Provider.OLLAMA:
            # Tạo và trả về OllamaAdapter instance
            return OllamaAdapter()
        
        # Default case: provider không hợp lệ
        case _:
            # Ghi log error: provider không được hỗ trợ
            global_logger.error(f"Unsupported provider: {provider}")
            # Raise ValueError với message tiếng Việt
            raise ValueError(f"Không hỗ trợ nhà cung cấp {provider}")


# Decorator @st.cache_resource để cache RAG instance giữa các lần rerun
# show_spinner="..." hiển thị spinner với message tiếng Việt trong khi khởi tạo
@st.cache_resource(show_spinner="Đang khởi tạo RAG (embedding model + vector DB)...")
# Hàm factory để tạo và cache RAG instance
def get_rag() -> SimpleRAG:
    """
    Khởi tạo SimpleRAG 1 lần duy nhất, cache lại giữa các lần rerun.

    Returns:
        SimpleRAG: RAG instance đã được khởi tạo
    """
    # Ghi log debug: đang khởi tạo SimpleRAG instance
    global_logger.debug("Initializing SimpleRAG instance")
    
    # Tạo và trả về SimpleRAG instance với các parameters từ environment
    return SimpleRAG(
        # Tên collection trong ChromaDB
        collection_name="knowledge_base",
        # Model embedding từ environment variable, default là "all-MiniLM-L6-v2"
        embedding_model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        # Model cross-encoder từ environment variable, default là "cross-encoder/ms-marco-MiniLM-L-6-v2"
        cross_encoder_model_name=os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
        # Đường dẫn lưu ChromaDB từ environment variable, default là "./chroma_db"
        chroma_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
    )


# Hàm factory để tạo chatbot engine
def get_chatbot_engine(provider: Provider) -> FullChatbotEngine:
    """
    Factory function để tạo FullChatbotEngine instance.

    Args:
        provider (Provider): Nhà cung cấp model

    Returns:
        FullChatbotEngine: Chatbot engine instance
    """
    # Ghi log debug: đang tạo chatbot engine cho provider nào
    global_logger.debug(f"Creating chatbot engine for provider: {provider}")
    
    # Tạo adapter instance dùng hàm get_adapter()
    adapter = get_adapter(provider)
    
    # Tạo memory instance dùng hàm get_memory()
    # Lấy context management mode từ session_state, default là OFF
    memory = get_memory(st.session_state.get("context_management_mode", ContextManagementMode.OFF.value))
    
    # Tạo và trả về FullChatbotEngine instance với adapter và memory
    return FullChatbotEngine(adapter=adapter, memory=memory)


# Hàm main - entry point của ứng dụng Streamlit
def main():
    """
    Main function - khởi tạo và chạy ứng dụng chatbot.
    """
    # Cấu hình page layout là "wide" để sử dụng toàn bộ chiều ngang màn hình
    st.set_page_config(layout="wide")
    
    # Kiểm tra nếu "selected_provider" chưa tồn tại trong session_state
    if "selected_provider" not in st.session_state:
        # Khởi tạo giá trị mặc định là GROQ
        st.session_state.selected_provider = Provider.GROQ.value
    
    # Kiểm tra nếu "selected_model" chưa tồn tại trong session_state
    if "selected_model" not in st.session_state:
        # Khởi tạo model mặc định là "openai/gpt-oss-20b"
        st.session_state.selected_model = "openai/gpt-oss-20b"

    # Khởi tạo RAG instance và đưa vào session_state + tools module
    
    # Gọi get_rag() để tạo RAG instance (được cache bởi @st.cache_resource)
    rag = get_rag()
    
    # Lưu RAG instance vào session_state để các components khác có thể truy cập
    st.session_state["rag"] = rag
    
    # Gọi set_rag_instance() để truyền RAG instance vào tools module
    # Điều này cho phép knowledge_base_search tool truy cập RAG
    set_rag_instance(rag)

    # Tạo chatbot engine instance với provider đã chọn
    # Provider(st.session_state.selected_provider) convert string thành Provider enum
    engine = get_chatbot_engine(Provider(st.session_state.selected_provider))
    
    # Render sidebar với các cài đặt chatbot
    render_sidebar()
    
    # Render chat interface với engine đã tạo
    render_chat_interface(engine=engine)


# Entry point - chỉ chạy main() nếu file này được chạy trực tiếp
# (không phải khi được import như module)
if __name__ == "__main__":
    # Gọi main function để khởi động ứng dụng
    main()
