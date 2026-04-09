"""
Module 5 - Model Layer: Base Adapter

Mô tả: Abstract base class và các adapter implementations cho LLM providers.
File này cung cấp interface thống nhất để gọi các LLM providers khác nhau.
"""

import os
from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv
import enum

from logger import global_logger
from custom_types import ToolChoice


class BaseAdapter(ABC):
    """
    Abstract base class cho LLM adapters.

    Cung cấp interface thống nhất để gọi các LLM providers khác nhau
    thông qua OpenAI-compatible API.
    """

    def __init__(self):
        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Khởi tạo và trả về OpenAI client cho provider cụ thể."""
        pass

    def response(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        tool_choice: ToolChoice | None = ToolChoice.NONE,
    ):
        """
        Gọi LLM với model và messages.

        Args:
            model (str): Model name/ID (e.g., "qwen/qwen3-32b")
            messages (list): List of message dicts với format:
                [{"role": "user|assistant|system|tool", "content": "..."}]
            tools (list): Tool definitions cho function calling (nếu None thì không dùng)
            tool_choice (ToolChoice): Tool usage mode (NONE, AUTO)

        Returns:
            Response object từ OpenAI API
        """
        if isinstance(tool_choice, enum.Enum):
            tool_choice_value = tool_choice.value
        else:
            tool_choice_value = getattr(tool_choice, "value", tool_choice)

        params = dict(
            model=model,
            messages=messages,
        )

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice_value

        return self.client.chat.completions.create(**params)


class GroqAdapter(BaseAdapter):
    """
    Adapter cho Groq API (OpenAI-compatible).
    """

    def _initialize_client(self):
        """Khởi tạo Groq OpenAI client."""
        load_dotenv(dotenv_path=".env", override=True)
        api_key = os.getenv("GROQ_API_KEY")
        global_logger.debug("Initializing Groq client")
        if not api_key:
            global_logger.error("GROQ_API_KEY not found in environment")
            raise ValueError("GROQ_API_KEY environment variable not set")
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )


class OllamaAdapter(BaseAdapter):
    """
    Adapter cho Ollama local server (OpenAI-compatible).
    """

    def _initialize_client(self):
        """Khởi tạo Ollama OpenAI client."""
        global_logger.debug("Initializing Ollama client at http://localhost:11434/v1/")
        return OpenAI(
            base_url="http://localhost:11434/v1/",
            api_key="ollama"
        )