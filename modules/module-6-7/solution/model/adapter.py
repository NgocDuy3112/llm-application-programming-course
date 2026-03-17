"""
Module 6-7 - Model Adapter

Mô tả: Triển khai các adapter khác nhau để kết nối với các LLM provider
(Groq, Ollama) thông qua OpenAI-compatible API wrapper.

Kiến trúc / Dependencies:
- BaseAdapter: Abstract base class định nghĩa interface chung
- GroqAdapter: Triển khai cho Groq API
- OllamaAdapter: Triển khai cho Ollama local server
- Được dùng bởi FullChatbotEngine để gọi LLM
"""

import os
from abc import ABC, abstractmethod
from openai import OpenAI
from logger import global_logger
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)


class BaseAdapter(ABC):
    """
    Abstract base class cho LLM adapters.
    
    Các subclass phải implement:
    - _initialize_client(): Khởi tạo OpenAI client với đúng base_url và api_key
    """
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Khởi tạo và trả về OpenAI client"""
        pass

    def response(
        self, 
        model: str, 
        messages: list, 
        tools: list,
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        """
        Gọi LLM với messages và config.
        
        Args:
            model: Model name/ID
            messages: List of message dicts
            tools: Tool definitions (nếu None thì không dùng tool)
            temperature: Creativity level
            max_output_tokens: Max tokens in response
            
        Returns:
            Response object từ OpenAI API
        """
        global_logger.debug(f"Calling {self.provider} API with model {model}")
        return self.client.chat.completions.create(
            model=model, 
            messages=messages, 
            tools=tools,
            temperature=temperature,
            max_tokens=max_output_tokens,
            **kwargs
        )


class GroqAdapter(BaseAdapter):
    """
    Adapter cho Groq API (OpenAI-compatible).
    
    Requires: GROQ_API_KEY environment variable
    """
    def _initialize_client(self):
        global_logger.debug("Initializing Groq client")
        api_key = os.getenv("GROQ_API_KEY")
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
    
    Assumes Ollama runs at http://localhost:11434/v1/
    """
    def _initialize_client(self):
        global_logger.debug("Initializing Ollama client at http://localhost:11434/v1/")
        return OpenAI(
            base_url="http://localhost:11434/v1/", 
            api_key="ollama"  # Ollama doesn't require real API key
        )