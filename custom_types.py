"""
Module 5 - Custom Types

Mô tả: Định nghĩa các enum types được sử dụng trong ứng dụng.

Exports:
    Provider: Enum cho các LLM providers (GROQ, OLLAMA)
    MODELS_BY_PROVIDER: Dict ánh xạ Provider -> danh sách models
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