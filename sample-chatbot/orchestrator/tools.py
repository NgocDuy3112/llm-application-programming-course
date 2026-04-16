# Import TavilyClient từ tavily package - công cụ tìm kiếm web
from tavily import TavilyClient
# Import date từ datetime module để lấy ngày hiện tại
from datetime import date
# Import os module để làm việc với environment variables
import os
# Import streamlit để làm việc với session_state
import streamlit as st
# Import load_dotenv từ dotenv để load biến môi trường từ file .env
from dotenv import load_dotenv
# Import global_logger từ logger module để ghi log
from logger import global_logger


# Load environment variables từ file .env
# override=True nghĩa là ghi đè lên các biến đã tồn tại
load_dotenv(dotenv_path=".env", override=True)
# Ghi log debug: đã load environment variables
global_logger.debug("Loading environment variables from .env")


# ---- RAG instance (được set từ app.py) ----
# Biến module-level để tools có thể truy cập RAG instance
# Ban đầu là None, sẽ được set qua hàm set_rag_instance()
_rag_instance = None

# Hàm để set RAG instance từ app.py vào module này
def set_rag_instance(rag):
    """Được gọi từ app.py để truyền RAG instance vào tools module."""
    # Khai báo sử dụng biến global _rag_instance
    global _rag_instance
    # Gán RAG instance vào biến global
    _rag_instance = rag
    # Ghi log debug: đã set RAG instance
    global_logger.debug("RAG instance set in tools module")


# Kiểm tra nếu TAVILY_API_KEY tồn tại trong environment variables
if os.getenv("TAVILY_API_KEY"):
    # Ghi log debug: đã tìm thấy API key
    global_logger.debug("Tavily API key found, initializing TavilyClient")
    # Khởi tạo TavilyClient với API key từ environment
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
# Nếu không tìm thấy API key
else:
    # Ghi log warning: không tìm thấy API key
    global_logger.warning("Tavily API key not found in environment variables")
    # Set tavily_client = None (không thể sử dụng search)
    tavily_client = None


# Hàm tìm kiếm web sử dụng Tavily API
def tavily_search(query: str) -> str:
    # Ghi log debug: bắt đầu thực hiện search với query
    global_logger.debug(f"Executing tavily_search with query: {query}")
    
    # Kiểm tra nếu tavily_client chưa được khởi tạo (không có API key)
    if not tavily_client:
        # Ghi log error: client chưa được khởi tạo
        global_logger.error("Tavily client not initialized, API key missing")
        # Trả về message lỗi
        return "Error: Tavily client not initialized"
    
    # Try-except block để xử lý exceptions
    try:
        # Gọi API search của Tavily
        response = tavily_client.search(
            query=query,              # Câu truy vấn tìm kiếm
            include_answer=True,      # Bao gồm câu trả lời tổng hợp
            time_range="year"         # Chỉ tìm trong 1 năm trở lại
        )
        
        # Kiểm tra nếu response là None (không có kết quả)
        if response is None:
            # Ghi log warning: search không có kết quả
            global_logger.warning("Tavily search returned no response")
            # Trả về message "No response"
            return "No response from Tavily"
        
        # Lấy answer từ response (câu trả lời tổng hợp từ Tavily)
        answer = response.get("answer")
        
        # Lặp qua từng result trong danh sách results
        for result in response.get("results"):
            # Thêm source URL và title vào answer
            answer += f"\n\nSource: {result.get('url')}\nTitle: {result.get('title')}"
        
        # Ghi log debug: search hoàn tất, kèm độ dài kết quả
        global_logger.debug(f"Tavily search completed, result length: {len(answer)}")
        
        # Trả về kết quả search
        return answer
    
    # Xử lý exception nếu có lỗi xảy ra
    except Exception as e:
        # Ghi log error với message lỗi
        global_logger.error(f"Error in tavily_search: {str(e)}")
        # Trả về message lỗi
        return f"Error: {str(e)}"


# Hàm lấy ngày hiện tại
def get_current_date() -> str:
    # Gọi date.today() để lấy ngày hiện tại
    # isoformat() chuyển đổi thành string format "YYYY-MM-DD"
    date_str = date.today().isoformat()
    # Ghi log debug: function được gọi
    global_logger.debug(f"get_current_date called, returning: {date_str}")
    # Trả về ngày hiện tại dưới dạng string
    return date_str


# Hàm tìm kiếm trong knowledge base (tài liệu đã upload)
def knowledge_base_search(query: str) -> str:
    """
    Tìm kiếm thông tin từ knowledge base (tài liệu đã upload).
    Sử dụng RAG pipeline: vector search → cross-encoder reranking.
    """
    # Ghi log debug: bắt đầu thực hiện search với query
    global_logger.debug(f"Executing knowledge_base_search with query: {query}")
    
    # Kiểm tra nếu _rag_instance chưa được khởi tạo
    if _rag_instance is None:
        # Ghi log error: RAG chưa được khởi tạo
        global_logger.error("RAG instance not initialized")
        # Trả về message lỗi
        return "Error: Knowledge base chưa được khởi tạo."
    
    # Kiểm tra nếu knowledge base không có documents nào
    if _rag_instance.doc_count() == 0:
        # Trả về message thông báo knowledge base trống
        return "Knowledge base hiện đang trống. Chưa có tài liệu nào được upload."
    
    # Try-except block để xử lý exceptions
    try:
        # Gọi method retrieve() của RAG instance để tìm kiếm
        # Truyền use_hybrid từ session_state (toggle Hybrid Search trên sidebar)
        use_hybrid = st.session_state.get("use_hybrid_search", False)
        use_rerank = st.session_state.get("use_rerank", True)
        result = _rag_instance.retrieve(query, use_hybrid=use_hybrid, use_rerank=use_rerank)
        
        # Lưu kết quả retrieve vào session_state để hiển thị trên UI
        st.session_state["last_retrieved_docs"] = result
        
        # Ghi log debug: search hoàn tất, kèm độ dài kết quả
        global_logger.debug(f"knowledge_base_search completed, result length: {len(result)}")
        
        # Trả về kết quả tìm kiếm
        return result
    
    # Xử lý exception nếu có lỗi xảy ra
    except Exception as e:
        # Ghi log error với message lỗi
        global_logger.error(f"Error in knowledge_base_search: {str(e)}")
        # Trả về message lỗi
        return f"Error: {str(e)}"


# Dictionary chứa danh sách các functions có sẵn để LLM có thể gọi
# Key: tên function (string), Value: function object
AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "tavily_search": tavily_search,
    "knowledge_base_search": knowledge_base_search,
}


# Danh sách các tools mặc định để gửi cho LLM
# Format theo OpenAI function calling specification
DEFAULT_TOOLS = [
    # Tool 1: Tavily search
    {
        "type": "function",  # Loại tool là function
        "function": {
            # Tên function
            "name": "tavily_search",
            # Mô tả chức năng của tool
            "description": "Thực hiện tìm kiếm trên web sử dụng Tavily",
            # Định nghĩa parameters
            "parameters": {
                "type": "object",  # Parameters là object
                "properties": {
                    # Parameter: query
                    "query": {
                        "type": "string",  # Kiểu string
                        # Mô tả parameter
                        "description": "Câu truy vấn tìm kiếm trên web.",
                    },
                },
                # Danh sách required parameters
                "required": ["query"],
            },
        }
    },
    # Tool 2: Get current date
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Lấy ngày hiện tại",
            # Không có parameters — dùng schema chuẩn OpenAI
            "parameters": {"type": "object", "properties": {}},
        }
    },
    # Tool 3: Knowledge base search
    {
        "type": "function",
        "function": {
            "name": "knowledge_base_search",
            "description": "Tìm kiếm thông tin từ knowledge base (tài liệu đã được upload). Sử dụng tool này khi người dùng hỏi về nội dung tài liệu hoặc cần thông tin từ dữ liệu đã cung cấp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Câu truy vấn tìm kiếm trong knowledge base.",
                    },
                },
                "required": ["query"],
            },
        }
    }
]
