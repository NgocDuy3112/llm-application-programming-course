"""
Module 6-7 - Constants

Mô tả: Khai báo các hằng số được sử dụng trong toàn bộ ứng dụng demo.
Hiện tại chỉ chứa danh sách models được hỗ trợ cho từng provider.

Constants:
    MODELS_BY_PROVIDER (dict): Mapping từ provider đến danh sách model IDs.
        - Key: Provider name (groq, ollama)
        - Value: List of model identifiers available for that provider

Usage:
    from constants import MODELS_BY_PROVIDER
    models = MODELS_BY_PROVIDER["groq"]
"""

from custom_types import Provider


# Mapping of providers to their available model identifiers
MODELS_BY_PROVIDER = {
    Provider.GROQ.value: [
        "openai/gpt-oss-20b",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b"
    ],
    Provider.OLLAMA.value: [
        "qwen3:0.6b-q4_K_M",      # 4-bit quantized (smaller, faster)
        "qwen3:0.6b-q8_0",        # 8-bit quantized (balanced)
        "qwen3:0.6b-fp16",        # Full 16-bit precision (highest quality)
    ],
}