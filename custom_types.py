"""
Module 5 - Custom Types

Mô tả: Định nghĩa các enum types và dictionary được sử dụng trong ứng dụng.

TODO 1: Hoàn thành tất cả các định nghĩa dưới đây:
- class Provider(Enum): GROQ = 'groq', OLLAMA = 'ollama'
- class ContextManagementMode(Enum): OFF = "Tắt", SLIDING_WINDOW = "Cửa sổ trượt (sliding window)"
- MODELS_BY_PROVIDER: dict ánh xạ Provider value -> danh sách model names
    + GROQ: ["openai/gpt-oss-20b", "moonshotai/kimi-k2-instruct-0905", "qwen/qwen3-32b"]
    + OLLAMA: ["qwen3:0.6b-q4_K_M", "qwen3:0.6b-q8_0", "qwen3:0.6b-fp16"]
"""

from enum import Enum


# TODO 1: Hoàn thành Provider, ContextManagementMode enums và MODELS_BY_PROVIDER dict