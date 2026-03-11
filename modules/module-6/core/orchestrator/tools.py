from tavily import TavilyClient
from datetime import date
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env", override=True)


tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))


def tavily_search(query: str) -> str:
    return tavily_client.search(
        query=query, 
        include_answer=True,
        time_range="year"
    ).get("answer", "No answer from Tavily")


def get_current_date() -> str:
    return date.today().isoformat()



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