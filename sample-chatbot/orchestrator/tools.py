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


def web_search(query: str) -> str:
    global_logger.debug(f"Executing web_search with query: {query}")
    if not tavily_client:
        global_logger.error("Tavily client not initialized, API key missing")
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.search(
            query=query, 
            include_answer=True,
            time_range="year"
        )
        result = response.get("answer", "No answer from Tavily") if response else "No response from Tavily"
        global_logger.debug(f"Web search completed, result length: {len(result) if result else 0}")
        return result
    except Exception as e:
        global_logger.error(f"Error in web_search: {str(e)}")
        return f"Error: {str(e)}"


def get_courses(instructions: str) -> str:
    global_logger.debug(f"Executing get_courses with instructions: {instructions}")
    if not tavily_client:
        global_logger.error("Tavily client not initialized, API key missing")
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.crawl(
            url="https://csc.edu.vn/",
            instructions=instructions,
            limit=3,
            extract_depth="basic"
        )
        crawl_results = response.get("results", []) if response else []
        final_output = ""
        for result in crawl_results:
            raw_content = result.get("raw_content", "")
            url = result.get("url", "")
            final_output += f"URL: {url}\nContent:\n{raw_content}\n\n"
        global_logger.debug(f"get_courses completed, total results: {len(crawl_results)}")
        return final_output.strip() if final_output else "No relevant courses found"
    except Exception as e:
        global_logger.error(f"Error in get_courses: {str(e)}")
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
    "get_courses": get_courses,
    "get_current_date": get_current_date,
    "web_search": web_search,
    "knowledge_base_search": knowledge_base_search,
}


DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
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