from tavily import TavilyClient
from datetime import date
import os
import streamlit as st
from dotenv import load_dotenv
from logger import global_logger


load_dotenv(dotenv_path=".env", override=True)
global_logger.debug("Loading environment variables from .env")


# ---- RAG instance (được set từ app.py) ----
# Biến module-level để tools có thể truy cập RAG instance
_rag_instance = None

def set_rag_instance(rag):
    """Được gọi từ app.py để truyền RAG instance vào tools module."""
    global _rag_instance
    _rag_instance = rag
    global_logger.debug("RAG instance set in tools module")


if os.getenv("TAVILY_API_KEY"):
    global_logger.debug("Tavily API key found, initializing TavilyClient")
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
else:
    global_logger.warning("Tavily API key not found in environment variables")
    tavily_client = None


def tavily_search(query: str) -> str:
    global_logger.debug(f"Executing tavily_search with query: {query}")
    if not tavily_client:
        global_logger.error("Tavily client not initialized, API key missing")
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.search(
            query=query, 
            include_answer=True,
            time_range="year"
        )
        if response is None:
            global_logger.warning("Tavily search returned no response")
            return "No response from Tavily"
        answer = response.get("answer")
        for result in response.get("results"):
            answer += f"\n\nSource: {result.get('url')}\nTitle: {result.get('title')}"
        global_logger.debug("Web search completed, result length")
        return answer
    except Exception as e:
        global_logger.error(f"Error in web_search: {str(e)}")
        return f"Error: {str(e)}"


def get_current_date() -> str:
    date_str = date.today().isoformat()
    global_logger.debug(f"get_current_date called, returning: {date_str}")
    return date_str


def knowledge_base_search(query: str) -> str:
    """
    Tìm kiếm thông tin từ knowledge base (tài liệu đã upload).
    Sử dụng RAG pipeline: vector search → cross-encoder reranking.
    """
    global_logger.debug(f"Executing knowledge_base_search with query: {query}")
    if _rag_instance is None:
        global_logger.error("RAG instance not initialized")
        return "Error: Knowledge base chưa được khởi tạo."
    if _rag_instance.doc_count() == 0:
        return "Knowledge base hiện đang trống. Chưa có tài liệu nào được upload."
    try:
        result = _rag_instance.retrieve(query)
        # Lưu kết quả retrieve vào session_state để hiển thị trên UI
        st.session_state["last_retrieved_docs"] = result
        global_logger.debug(f"knowledge_base_search completed, result length: {len(result)}")
        return result
    except Exception as e:
        global_logger.error(f"Error in knowledge_base_search: {str(e)}")
        return f"Error: {str(e)}"


AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "web_search": web_search,
    "knowledge_base_search": knowledge_base_search,
}


DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Thực hiện tìm kiếm trên web sử dụng Tavily",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Câu truy vấn tìm kiếm trên web.",
                    },
                },
                "required": ["query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Lấy ngày hiện tại",
            "parameters": {},
        }
    },
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