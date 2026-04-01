"""
Module 5 - Tools

Mô tả: Định nghĩa các tools có sẵn cho chatbot.
"""

from datetime import date
from logger import global_logger


def get_current_date() -> str:
    """
    Lấy ngày hiện tại của hệ thống.

    Returns:
        str: Date string theo ISO 8601 format (YYYY-MM-DD)
    """
    date_str = date.today().isoformat()
    global_logger.debug(f"get_current_date called, returning: {date_str}")
    return date_str


AVAILABLE_FUNCTIONS = {
    "get_current_date": get_current_date,
}

DEFAULT_TOOLS = [
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