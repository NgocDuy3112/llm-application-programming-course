from tavily import TavilyClient
from datetime import date

from settings import *


settings = Settings()
tavily_client = TavilyClient(settings.TAVILY_API_KEY)


Tool = dict[str, Any]


def openai_tool_to_groq(tool: Tool) -> Tool:
    """
    Convert a single tool schema from OpenAI format to Groq/Harmony format.

    OpenAI (nested) example:
        {"type":"function","function":{"name":"x","description":"...","parameters":{...},"strict":true}}

    Groq/Harmony (top-level) output:
        {"type":"function","name":"x","description":"...","parameters":{...},"strict":true}

    Notes:
    - If the tool is already in Groq/Harmony top-level format, return as-is.
    - Preserves extra keys on the tool object (except the nested "function" wrapper).
    - "strict" is kept if present either at tool level or inside tool["function"].
    """
    if not isinstance(tool, dict):
        raise TypeError(f"tool must be a dict, got {type(tool)!r}")

    if tool.get("type") != "function":
        # Non-function tools: pass through unchanged
        return tool

    # Already top-level (Groq/Harmony or OpenAI "flat" style)
    if "name" in tool and ("parameters" in tool or "description" in tool):
        return tool

    fn = tool.get("function")
    if not isinstance(fn, dict):
        # Unexpected shape; pass through (or raise if you prefer strictness)
        return tool

    out: Tool = {k: v for k, v in tool.items() if k != "function"}  # keep type + any extra keys

    # Lift function fields to top-level
    out["name"] = fn.get("name")
    if "description" in fn:
        out["description"] = fn.get("description")
    if "parameters" in fn:
        out["parameters"] = fn.get("parameters")

    # strict may exist at either level; prefer explicit top-level if already set
    if "strict" not in out and "strict" in fn:
        out["strict"] = fn["strict"]

    return out


def openai_tools_to_groq(tools: list[Tool]) -> list[Tool]:
    """Convert a list of tools (OpenAI schema) to Groq/Harmony schema."""
    if not tools:
        return []
    return [openai_tool_to_groq(t) for t in tools]


def tavily_search(query: str) -> str:
    return tavily_client.search(
        query=query, 
        include_answer=True,
        time_range="year"
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
                    "description": "Câu hỏi hoặc từ khóa liên quan đến thông tin cần tìm"
                },
            },
            "required": ["query"],
        }
    }
]