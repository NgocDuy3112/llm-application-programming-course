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