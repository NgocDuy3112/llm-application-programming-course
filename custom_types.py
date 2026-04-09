"""
Module 5 - Custom Types

Mô tả: Định nghĩa các enum types được sử dụng trong ứng dụng.

TODO: Hoàn thành các định nghĩa enum và dictionary dưới đây dựa trên yêu cầu:

1. Provider enum:
   - GROQ: giá trị 'groq' - Cloud-based inference qua Groq API (tốc độ cao)
   - OLLAMA: giá trị 'ollama' - Local inference qua Ollama server (riêng tư, offline)

2. ContextManagementMode enum:
   - OFF: giá trị "Tắt" - Không lưu trữ lịch sử, mỗi message được xử lý độc lập
   - SLIDING_WINDOW: giá trị "Cửa sổ trượt (sliding window)" - Giữ lại k cặp user-assistant messages gần nhất

3. MODELS_BY_PROVIDER dictionary:
   - GROQ: ["openai/gpt-oss-20b", "moonshotai/kimi-k2-instruct-0905", "qwen/qwen3-32b"]
   - OLLAMA: ["qwen3:0.6b-q4_K_M", "qwen3:0.6b-q8_0", "qwen3:0.6b-fp16"]
"""

from enum import Enum


# TODO 1: Định nghĩa class Provider(Enum) với 2 members: GROQ và OLLAMA


# TODO 2: Định nghĩa class ContextManagementMode(Enum) với 2 members: OFF và SLIDING_WINDOW


# TODO 3: Định nghĩa MODELS_BY_PROVIDER dictionary ánh xạ Provider -> danh sách models


class ToolChoice(Enum):
    """
    Enum cho các chế độ sử dụng tools.
    
    Members:
        OFF: Tắt - Không sử dụng tools
        AUTO: Tự động - Model tự quyết định khi nào dùng tools
        REQUIRED: Bắt buộc - Model phải dùng tools
    """
    # TODO 4: Định nghĩa các members: OFF = "off", AUTO = "auto", REQUIRED = "required"
    pass
"""
Module 5 - Custom Types

Mô tả: Định nghĩa các enum types được sử dụng trong ứng dụng.

Exports:
    Provider: Enum cho các LLM providers (GROQ, OLLAMA)
    ContextManagementMode: Enum cho các chế độ quản lý ngữ cảnh
    ToolChoice: Enum cho các chế độ sử dụng tools
"""

from enum import Enum


class Provider(Enum):
    """
    Enum cho các nhà cung cấp LLM được hỗ trợ.

    Members:
        GROQ: Cloud-based inference qua Groq API (tốc độ cao)
        OLLAMA: Local inference qua Ollama server (riêng tư, offline)
    """
    GROQ = 'groq'
    OLLAMA = 'ollama'


class ContextManagementMode(Enum):
    """
    Enum cho các chế độ quản lý lịch sử hội thoại (context memory).

    Members:
        OFF: Tắt - Không lưu trữ lịch sử, mỗi message được xử lý độc lập
        SLIDING_WINDOW: Cửa sổ trượt - Giữ lại k cặp user-assistant messages gần nhất
    """
    OFF = "Tắt"
    SLIDING_WINDOW = "Cửa sổ trượt (sliding window)"


MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b"
    ],
    Provider.OLLAMA.value: [
        "qwen3:0.6b-q4_K_M",
        "qwen3:0.6b-q8_0",
        "qwen3:0.6b-fp16",
    ],
}