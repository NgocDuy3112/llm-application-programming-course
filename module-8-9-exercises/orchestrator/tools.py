"""Bài tập Buổi 7 — Tích hợp RAG tool vào hệ thống function calling.

Nhiệm vụ:
  TODO 1: Khai báo _rag_instance và implement set_rag_instance()
  TODO 2: Implement knowledge_base_search()
  TODO 3: Đăng ký tool vào AVAILABLE_FUNCTIONS và DEFAULT_TOOLS
"""

from tavily import TavilyClient
from datetime import date
import os
import streamlit as st
from dotenv import load_dotenv
from logger import global_logger

load_dotenv(dotenv_path=".env", override=True)

if os.getenv("TAVILY_API_KEY"):
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
else:
    global_logger.warning("Tavily API key not found")
    tavily_client = None


# ================================================================
# CÁC TOOLS SẴN CÓ — KHÔNG CẦN SỬA
# ================================================================

def tavily_search(query: str) -> str:
    global_logger.debug(f"Executing tavily_search with query: {query}")
    if not tavily_client:
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.search(query=query, include_answer=True, time_range="year")
        if response is None:
            return "No response from Tavily"
        answer = response.get("answer") or ""
        for result in response.get("results", []):
            answer += f"\n\nSource: {result.get('url')}\nTitle: {result.get('title')}"
        return answer
    except Exception as e:
        return f"Error: {str(e)}"


def get_current_date() -> str:
    return date.today().isoformat()


# ================================================================
# TODO 1a: Khai báo RAG instance
# ================================================================

# Khai báo biến module-level lưu RAG instance (ban đầu là None)
# YOUR CODE HERE


def set_rag_instance(rag):
    """
    Nhận RAG instance từ app.py và lưu vào biến module-level.

    Args:
        rag: SimpleRAG instance được tạo trong app.py

    Gợi ý:
        - Cần dùng từ khóa `global` để sửa biến module-level
        - Gán: _rag_instance = rag
    """
    # YOUR CODE HERE
    raise NotImplementedError("TODO 1: Implement set_rag_instance()")


# ================================================================
# TODO 4a: Implement knowledge_base_search
# ================================================================

def knowledge_base_search(query: str) -> str:
    """
    Tìm kiếm thông tin từ knowledge base (tài liệu đã upload).

    Args:
        query (str): Câu hỏi cần tìm kiếm

    Returns:
        str: Context string từ RAG, hoặc thông báo lỗi/trống

    Các bước cần làm:
        1. Nếu _rag_instance is None  → return "Error: Knowledge base chưa được khởi tạo."
        2. Nếu _rag_instance.doc_count() == 0  → return "Knowledge base đang trống."
        3. Gọi result = _rag_instance.retrieve(query)
        4. Lưu result vào st.session_state["last_retrieved_docs"] để UI hiển thị
        5. return result
    """
    global_logger.debug(f"Executing knowledge_base_search with query: {query}")
    # YOUR CODE HERE
    raise NotImplementedError("TODO 4a: Implement knowledge_base_search()")


# ================================================================
# TODO 4b: Đăng ký tool
# ================================================================

# Thêm "knowledge_base_search": knowledge_base_search vào dict này
AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "tavily_search": tavily_search,
    # YOUR CODE HERE
}

# Thêm tool spec cho knowledge_base_search vào list này
DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Thực hiện tìm kiếm trên web sử dụng Tavily",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Câu truy vấn tìm kiếm."},
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
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    # TODO 4c: Thêm tool spec cho knowledge_base_search
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "knowledge_base_search",
    #         "description": "...",
    #         "parameters": { ... }
    #     }
    # }
]
