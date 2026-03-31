"""
Module 6-7 - Tools

Mô tả: Triển khai các tools (function calling) cho chatbot. Tools cho phép
LLM thực thi các tác vụ bên ngoài như search web, gọi API, query database.

Kiến trúc / Dependencies:
- TavilyClient: Web search API client
- AVAILABLE_FUNCTIONS: Registry mapping tool names to function implementations
- DEFAULT_TOOLS: Tool specifications cho LLM (OpenAI function calling format)

Tool Flow:
1. LLM nhận tool definitions trong API call
2. LLM quyết định gọi tool nào dựa trên user input
3. Engine thực thi tool function với arguments từ LLM
4. Kết quả được thêm vào memory và gửi lại cho LLM
5. LLM generate response dựa trên tool output

Usage:
    from orchestrator.tools import tavily_search, get_current_date
    result = tavily_search("Python programming")
    date = get_current_date()
"""

from tavily import TavilyClient
from datetime import date
import os
from dotenv import load_dotenv
from logger import global_logger


# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)
global_logger.debug("Loading environment variables from .env")


# Initialize Tavily client if API key is available
if os.getenv("TAVILY_API_KEY"):
    global_logger.debug("Tavily API key found, initializing TavilyClient")
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
else:
    global_logger.warning("Tavily API key not found in environment variables")
    tavily_client = None


def tavily_search(query: str) -> str:
    """
    Thực hiện tìm kiếm web sử dụng Tavily API.

    Tavily là search API được optimize cho LLM agents, cung cấp:
    - Search results với relevance scoring
    - Extracted content từ web pages
    - Anti-bot handling

    Args:
        query (str): Search query string

    Returns:
        str: Concatenated search results bao gồm:
            - Answer summary (nếu có)
            - Source URLs và titles

    Raises:
        Returns error string nếu:
            - Tavily client không được khởi tạo (thiếu API key)
            - API call thất bại

    Example:
        >>> result = tavily_search("Python programming tutorials")
        >>> print(result[:200])  # Print first 200 chars
    """
    global_logger.debug(f"Executing tavily_search with query: {query}")
    if not tavily_client:
        global_logger.error("Tavily client not initialized, API key missing")
        return "Error: Tavily client not initialized"

    # Implementation hint: call `tavily_client.search(...)`, extract `answer`
    # and `results`, concatenate into a single string and return. Handle
    # exceptions and return a user-friendly error string if needed.
    # For exercises this function is left intentionally unimplemented so
    # students can implement a real call or return a mocked string.
    pass


def get_current_date() -> str:
    """
    Lấy ngày hiện tại của hệ thống.

    Returns:
        str: Date string theo ISO 8601 format (YYYY-MM-DD)

    Example:
        >>> get_current_date()
        '2025-03-27'

    Use case:
        - LLM không có khái niệm về thời gian thực
        - Tool này giúp chatbot trả lời các câu hỏi về ngày tháng
    """
    date_str = date.today().isoformat()
    global_logger.debug(f"get_current_date called, returning: {date_str}")
    return date_str


# Registry of available tool functions
# Engine sẽ lookup tên tool (string) và gọi hàm tương ứng với kwargs parsed từ model.
# GỢI Ý: Đăng ký functions theo tên như ví dụ dưới (mapping thực tế được giữ để code chạy):
# Example (commented):
# AVAILABLE_FUNCTIONS = {
#     "get_current_date": get_current_date,
#     "tavily_search": tavily_search,
# }
AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "tavily_search": tavily_search,
}


# Tool specifications cho LLM (OpenAI function calling format)
# GỢI Ý: Mỗi entry phải mô tả name, description và parameters schema.
# Ví dụ mẫu (uncomment để dùng):
# {
#   "type": "function",
#   "function": {"name": "tavily_search", "description": "...", "parameters": {...}}
# }
DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Thực hiện tìm kiếm trên web sử dụng Tavily",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Câu truy vấn tìm kiếm"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Lấy ngày hiện tại",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
