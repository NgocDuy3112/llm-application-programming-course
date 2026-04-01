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
import enum

from logger import global_logger
from custom_types import ToolChoice


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
        # TODO(BT1-Groq): Tạo OpenAI client cho Groq API
        # - base_url="https://api.groq.com/openai/v1"
        # - api_key từ os.getenv("GROQ_API_KEY")
        global_logger.info("Khởi tạo Groq client...")


class OllamaAdapter(BaseAdapter):
    """Adapter cho Ollama - local LLM server."""

    def _initialize_client(self):
        # TODO(BT1-Ollama): Tạo OpenAI client cho Ollama local
        # - base_url="http://localhost:11434/v1"
        # - api_key="ollama" (placeholder, không cần thật)
        global_logger.info("Khởi tạo Ollama client...")