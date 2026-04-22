import os
from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv

from logger import global_logger

# Load environment variables from .env file
load_dotenv()


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
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not set. "
                "Please set your Groq API key by creating a .env file with: GROQ_API_KEY=your_key_here"
            )
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )


class CerebrasAdapter(BaseAdapter):
    """Adapter cho Cerebras - cloud LLM provider."""

    def _initialize_client(self):
        global_logger.info("Khởi tạo Cerebras client...")
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError(
                "CEREBRAS_API_KEY environment variable not set. "
                "Please set your Cerebras API key by creating a .env file with: CEREBRAS_API_KEY=your_key_here"
            )
        return OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=api_key
        )