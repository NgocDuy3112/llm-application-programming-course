"""
Module 6-7 - Model Adapter (Solution)

Mô tả: Triển khai các adapter khác nhau để kết nối với các LLM providers
(Groq, Ollama) thông qua OpenAI-compatible API wrapper.

Kiến trúc / Dependencies:
- BaseAdapter: Abstract base class định nghĩa interface chung
- GroqAdapter: Triển khai cho Groq API
- OllamaAdapter: Triển khai cho Ollama local server
- Được dùng bởi FullChatbotEngine để gọi LLM

Design Patterns:
- Adapter Pattern: Chuẩn hóa interface cho các LLM providers khác nhau
- Template Method: _initialize_client() được override bởi subclasses

Usage:
    from model.adapter import GroqAdapter, OllamaAdapter
    adapter = GroqAdapter()
    response = adapter.response(model="...", messages=[...], ...)
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
    thông qua OpenAI-compatible API. Các subclass chỉ cần implement
    _initialize_client() để setup client riêng.

    Attributes:
        client (OpenAI): OpenAI client instance cho provider cụ thể

    Methods:
        _initialize_client(): Abstract method - khởi tạo client
        response(): Gọi LLM API với messages và config
    """

    def __init__(self):
        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """
        Khởi tạo và trả về OpenAI client cho provider cụ thể.

        Returns:
            OpenAI: Configured client instance

        Raises:
            ValueError: Nếu không thể khởi tạo client (thiếu API key, etc.)
        """
        pass

    def response(
        self,
        model: str,
        messages: list,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        tools: list | None = None,
        tool_choice: ToolChoice | None = ToolChoice.NONE,
    ):
        """
        Gọi LLM với messages và config.

        Args:
            model (str): Model name/ID (e.g., "qwen/qwen3-32b")
            messages (list): List of message dicts với format:
                [{"role": "user|assistant|system|tool", "content": "..."}]
            tools (list): Tool definitions cho function calling (nếu None thì không dùng)
            tool_choice (ToolChoice): Tool usage mode (NONE, AUTO)
            temperature (float): Creativity level (0.0 = deterministic, 1.0 = creative)
            max_tokens (int): Maximum tokens in response

        Returns:
            Response object từ OpenAI API với structure:
                response.choices[0].message.content  # Generated text
                response.choices[0].message.tool_calls  # Tool calls (nếu có)

        Note:
            - Tool choice được convert từ Enum sang value để tương thích API
            - kwargs được pass-through để hỗ trợ thêm params nếu cần
        """
        if isinstance(tool_choice, enum.Enum):
            tool_choice_value = tool_choice.value
        else:
            tool_choice_value = getattr(tool_choice, "value", tool_choice)

        params = dict(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice_value,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return self.client.chat.completions.create(**params)


class GroqAdapter(BaseAdapter):
    """
    Adapter cho Groq API (OpenAI-compatible).

    Groq cung cấp inference tốc độ cao cho các open-weight models.
    Adapter này tự động load GROQ_API_KEY từ environment variable.

    Environment Variables Required:
        GROQ_API_KEY: API key từ https://console.groq.com

    Example:
        >>> adapter = GroqAdapter()
        >>> response = adapter.response(
        ...     model="qwen/qwen3-32b",
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     tools=None,
        ...     tool_choice=ToolChoice.NONE,
        ...     temperature=0.7,
        ...     max_tokens=1024
        ... )
    """

    def _initialize_client(self):
        """
        Khởi tạo Groq OpenAI client.

        Returns:
            OpenAI: Groq client configured với base_url và API key

        Raises:
            ValueError: Nếu GROQ_API_KEY không được set trong environment
        """
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

    Ollama cho phép chạy LLM locally, phù hợp cho:
    - Development/testing
    - Privacy-sensitive applications
    - Offline usage

    Assumes:
        - Ollama server đang chạy tại http://localhost:11434
        - Models đã được pull qua `ollama pull <model_name>`

    Example:
        # Start Ollama server first:
        #   ollama serve
        # Pull a model:
        #   ollama pull qwen3:0.6b

        >>> adapter = OllamaAdapter()
        >>> response = adapter.response(...)
    """

    def _initialize_client(self):
        """
        Khởi tạo Ollama OpenAI client.

        Returns:
            OpenAI: Ollama client configured với localhost:11434

        Note:
            - Ollama doesn't require real API key, dùng "ollama" làm placeholder
            - Base URL: http://localhost:11434/v1/
        """
        global_logger.debug("Initializing Ollama client at http://localhost:11434/v1/")
        return OpenAI(
            base_url="http://localhost:11434/v1/",
            api_key="ollama"
        )
