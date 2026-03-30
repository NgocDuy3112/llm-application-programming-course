"""
Module 6-7 - Custom Types

Mô tả: Định nghĩa các enum types được sử dụng xuyên suốt ứng dụng demo.
Các type này giúp chuẩn hóa việc truyền tham số và kiểm soát logic.

Exports:
    Provider: Enum cho các LLM providers (GROQ, OLLAMA)
    ContextManagementMode: Enum cho các chế độ quản lý ngữ cảnh
    ToolChoice: Enum cho các chế độ sử dụng tools

Usage:
    from custom_types import Provider, ContextManagementMode, ToolChoice
    provider = Provider.GROQ
    mode = ContextManagementMode.SLIDING_WINDOW
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
            + Ưu điểm: Kiểm soát được độ dài context, giảm chi phí API
            + Nhược điểm: Mất ngữ cảnh xa khi hội thoại dài
    """
    OFF = "Tắt"
    SLIDING_WINDOW = "Cửa sổ trượt (sliding window)"


class ToolChoice(Enum):
    """
    Enum cho các chế độ lựa chọn tool/function calling.

    Members:
        NONE: Không sử dụng tools, chỉ generate text thuần túy
        AUTO: Để model tự quyết định khi nào cần gọi tool
    """
    NONE = "none"
    AUTO = "auto"
