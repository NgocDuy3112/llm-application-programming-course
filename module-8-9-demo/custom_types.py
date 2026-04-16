# Import Enum từ enum module để định nghĩa các enumeration types
from enum import Enum


# Định nghĩa Provider class kế thừa từ Enum
# Enum giúp tạo ra các hằng số có tên, tránh việc dùng magic strings
class Provider(Enum):
    """
    Enumeration cho các LLM providers.

    Values:
        GROQ: Groq cloud API (https://groq.com)
        OLLAMA: Ollama local server (https://ollama.com)
    """
    # Groq provider - cloud API với tốc độ cao
    GROQ = 'groq'
    # Ollama provider - chạy models locally
    OLLAMA = 'ollama'


# Định nghĩa ContextManagementMode class kế thừa từ Enum
class ContextManagementMode(Enum):
    """
    Enumeration cho các chế độ quản lý ngữ cảnh (context management).

    Values:
        OFF: Không lưu lịch sử chat
        SLIDING_WINDOW: Chỉ giữ lại k cặp messages gần nhất
    """
    # Tắt quản lý ngữ cảnh - không lưu lịch sử
    OFF = "Tắt"
    # Sliding window - giữ lại k cặp user-assistant gần nhất
    # Giúp hạn chế context length và chi phí API
    SLIDING_WINDOW = "Cửa sổ trượt (sliding window)"


# Định nghĩa ToolChoice class kế thừa từ Enum
class ToolChoice(Enum):
    """
    Enumeration cho các chế độ sử dụng tools (function calling).

    Values:
        NONE: Không sử dụng tools
        AUTO: Để LLM tự quyết định có dùng tool hay không
    """
    # Không sử dụng tools - LLM chỉ generate text
    NONE = "none"
    # Auto mode - LLM tự quyết định khi nào cần gọi tools
    AUTO = "auto"
