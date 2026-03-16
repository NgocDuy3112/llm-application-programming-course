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


AVAILABLE_FUNCTIONS = {
    "get_courses": get_courses,
    "get_current_date": get_current_date,
    "web_search": web_search,
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
            "name": "get_courses",
            "description": "Tìm kiếm các khoá học tại Trung tâm tin học, Đại học KHoa học Tự nhiên, Đại học Quốc gia TPHCM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "string",
                        "description": "Chỉ dẫn cụ thể về các khoá học cần trích xuất.",
                    },
                },
                "required": ["instructions"],
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
    }
]