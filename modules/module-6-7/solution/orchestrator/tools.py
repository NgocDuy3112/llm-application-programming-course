from tavily import TavilyClient
from datetime import date
import os
from dotenv import load_dotenv
from logger import global_logger


load_dotenv(dotenv_path=".env", override=True)
global_logger.debug("Loading environment variables from .env")

tavily_api_key = os.getenv("TAVILY_API_KEY")
if tavily_api_key:
    global_logger.debug("Tavily API key found, initializing TavilyClient")
    tavily_client = TavilyClient(tavily_api_key)
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
        result = response.get("answer", "No answer from Tavily") if response else "No response from Tavily"
        global_logger.debug(f"Tavily search completed, result length: {len(result) if result else 0}")
        return result
    except Exception as e:
        global_logger.error(f"Error in tavily_search: {str(e)}")
        return f"Error: {str(e)}"


def get_current_date() -> str:
    date_str = date.today().isoformat()
    global_logger.debug(f"get_current_date called, returning: {date_str}")
    return date_str



AVAILABLE_FUNCTIONS = {
    "tavily_search": tavily_search,
    "get_current_date": get_current_date,
}



DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Tìm kiếm thông tin trên Tavily",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Câu truy vấn tìm kiếm",
                    },
                },
                "required": ["query"],
            },
        }
    }
]