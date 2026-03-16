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