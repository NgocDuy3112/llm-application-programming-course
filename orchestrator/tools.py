from tavily import TavilyClient
from datetime import date
import os
from dotenv import load_dotenv
from logger import global_logger


load_dotenv(dotenv_path=".env", override=True)
global_logger.debug("Loading environment variables from .env")


if os.getenv("TAVILY_API_KEY"):
    global_logger.debug("Tavily API key found, initializing TavilyClient")
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
else:
    global_logger.warning("Tavily API key not found in environment variables")
    tavily_client = None


def tavily_search(query: str) -> str:
    """Tìm kiếm web qua Tavily API - trả về kết quả + source URLs."""
    if not tavily_client:
        return "Error: Tavily client not initialized"
    try:
        response = tavily_client.search(query=query, include_answer=True, time_range="year")
        answer = response.get("answer") or ""
        for r in response.get("results", []):
            answer += f"\n\nSource: {r['url']}\nTitle: {r['title']}"
        return answer
    except Exception as e:
        return f"Error: {e}"


def get_current_date() -> str:
    """Trả về ngày hiện tại (YYYY-MM-DD)."""
    return date.today().isoformat()



AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
    "tavily_search": tavily_search,
}


DEFAULT_TOOLS = [
    # TODO(BT4a): Định nghĩa cấu trúc JSON schema cho các công cụ (tools) theo chuẩn Function Calling của OpenAI.
    # 1. Định nghĩa `get_current_date`: Mô tả rằng hàm này trả về ngày hệ thống.
    # 2. Định nghĩa `tavily_search`: Mô tả rằng đây là công cụ tìm kiếm trên internet khi LLM không biết thông tin hiện tại, yêu cầu tham số `query`.
    # 
    # Mẫu cấu trúc một cụ:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "tên_hàm",
    #         "description": "Giải thích vai trò của hàm cho LLM hiểu",
    #         "parameters": {
    #             "type": "object",
    #             "properties": { "param_name": { "type": "string", "description": "..." } },
    #             "required": ["param_name"]
    #         }
    #     }
    # }
]
