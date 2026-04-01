from tavily import TavilyClient
from datetime import date
import os
from dotenv import load_dotenv
from logger import global_logger


load_dotenv(dotenv_path=".env", override=True)
global_logger.debug("Đang load environment variables từ .env")


if os.getenv("TAVILY_API_KEY"):
    global_logger.debug("Tìm thấy Tavily API key, khởi tạo TavilyClient")
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
else:
    global_logger.warning("Không tìm thấy Tavily API key trong environment variables")
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
    global_logger.debug(f"Thực thi tavily_search với query: {query}")
    if not tavily_client:
        global_logger.error("Tavily client chưa được khởi tạo, có thể thiếu API key")
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.search(
            query=query,
            include_answer=True,
            time_range="year",
        )
        if response is None:
            global_logger.warning("Tavily search không trả về response")
            return "No response from Tavily"
        answer = response.get("answer") or ""
        for result in response.get("results", []):
            answer += f"\n\nSource: {result.get('url')}\nTitle: {result.get('title')}"
        global_logger.debug(f"Tìm kiếm web hoàn tất, độ dài kết quả: {len(answer)}")
        return answer
    except Exception as e:
        global_logger.error(f"Lỗi trong web_search: {str(e)}")
        return f"Error: {str(e)}"


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
    global_logger.debug(f"get_current_date được gọi, trả về: {date_str}")
    return date_str



AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "tavily_search": tavily_search,
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
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    }
]