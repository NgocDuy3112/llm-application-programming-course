"""
Module 6-7 - Model Adapter (Bài tập)

Bài tập 1: Kết nối LLM providers (Groq, Ollama) qua OpenAI-compatible API.

Cần làm:
- GroqAdapter._initialize_client(): Tạo client cho Groq API
- OllamaAdapter._initialize_client(): Tạo client cho Ollama local

BaseAdapter.response() đã có sẵn implementation.
"""

import os
from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv

from logger import global_logger


class BaseAdapter(ABC):
    """Base class cho LLM adapters - đã implement sẵn response()."""

    def __init__(self):
        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Khởi tạo OpenAI client - subclass phải implement."""
        pass

    def response(self, model: str, messages: list, **kwargs):
        """Gọi LLM API - đã implement sẵn."""
        return self.client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )


class GroqAdapter(BaseAdapter):
    """Adapter cho Groq API - cloud LLM provider."""

    def _initialize_client(self):
        # TODO(BT1-Groq): Khởi tạo đối tượng `OpenAI` client để gọi đến server Groq Cloud.
        # - Sử dụng base_url="https://api.groq.com/openai/v1"
        # - Lấy api_key từ biến môi trường `GROQ_API_KEY` thông qua os.getenv.
        global_logger.info("Khởi tạo Groq client...")


class OllamaAdapter(BaseAdapter):
    """Adapter cho Ollama - local LLM server."""

    def _initialize_client(self):
        # TODO(BT1-Ollama): Khởi tạo đối tượng `OpenAI` client để gọi đến server Ollama cục bộ.
        # - Sử dụng base_url="http://localhost:11434/v1"
        # - Sử dụng api_key="ollama" làm giá trị mặc định cho local setup.
        global_logger.info("Khởi tạo Ollama client...")
