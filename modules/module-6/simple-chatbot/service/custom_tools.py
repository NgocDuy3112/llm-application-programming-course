from tavily import TavilyClient
from datetime import date

from settings import *


settings = Settings()
tavily_client = TavilyClient(settings.TAVILY_API_KEY)


def tavily_search(query: str) -> str:
    return tavily_client.search(
        query=query, 
        include_answer=True,
        time_range="year"
    ).get("answer", "No answer from Tavily")


def get_current_date() -> str:
    return date.today().isoformat()



DEFAULT_TOOLS = [
    {
        "type": "function",
        "name": "tavily_search",
        "description": "Thực hiện tìm kiếm thông tin trên web để hỗ trợ trả lời câu hỏi của người dùng. Sử dụng khi bạn cần tra cứu thông tin cập nhật hoặc chi tiết mà bạn không chắc chắn. Đảm bảo chỉ sử dụng công cụ này khi thực sự cần",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi hoặc từ khóa liên quan đến thông tin cần tìm"
                },
            },
            "required": ["query"],
        }
    },
    {
        "type": "function",
        "name": "get_current_date",
        "description": "Lấy ngày hiện tại",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        }
    },
]