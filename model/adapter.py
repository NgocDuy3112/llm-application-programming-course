"""
Module 5 - Model Adapter

Mô tả: Cung cấp các adapter để kết nối với các LLM providers khác nhau.
Mỗi adapter đóng gói chi tiết kết nối API và cung cấp interface thống nhất.

TODO 2: Hoàn thành GroqAdapter và OllamaAdapter:
- GroqAdapter.__init__(): Khởi tạo OpenAI client với base_url="https://api.groq.com/openai/v1"
  và api_key=os.getenv("GROQ_API_KEY")
- GroqAdapter.response(): Gọi self.client.chat.completions.create() với model, messages, temperature, max_tokens
- OllamaAdapter.__init__(): Khởi tạo OpenAI client với base_url="http://localhost:11434/v1"
  và api_key="ollama"
- OllamaAdapter.response(): Gọi self.client.chat.completions.create() với model, messages, temperature, max_tokens

Gợi ý: Cả hai adapter đều sử dụng OpenAI SDK vì Groq và Ollama đều tương thích OpenAI API format.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class GroqAdapter:
    """
    Adapter để kết nối với Groq Cloud API.
    Groq cung cấp API tương thích với OpenAI SDK.
    """

    def __init__(self):
        # TODO 2: Khởi tạo self.client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
        pass

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        # TODO 2: Gọi self.client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        pass


class OllamaAdapter:
    """
    Adapter để kết nối với Ollama Local API.
    Ollama cung cấp API tương thích với OpenAI SDK.
    """

    def __init__(self):
        # TODO 2: Khởi tạo self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        pass

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        # TODO 2: Gọi self.client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        pass