from tavily import TavilyClient
from settings import *


settings = Settings()
tavily_client = TavilyClient(settings.TAVILY_API_KEY)


def tavily_search(query: str) -> str:
    return tavily_client.search(
        query=query, 
        include_answer=True
    ).get("answer", "No answer from Tavily")



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
                    "description": "Truy vấn tìm kiếm, có thể là câu hỏi hoặc từ khóa liên quan đến thông tin cần tìm"
                },
            },
            "required": ["query"],
        }
    }
]