"""
Module 5 - Model Adapter

Mô tả: Cung cấp các adapter để kết nối với các LLM providers khác nhau.
Mỗi adapter đóng gói chi tiết kết nối API và cung cấp interface thống nhất.

TODO: Hoàn thành các class adapter dưới đây:

1. GroqAdapter:
   - __init__(): Khởi tạo OpenAI client với base_url="https://api.groq.com/openai/v1"
                 và api_key từ biến môi trường GROQ_API_KEY
   - response(model, messages, temperature, max_tokens, **kwargs):
                 Gọi API và trả về response object

2. OllamaAdapter:
   - __init__(): Khởi tạo OpenAI client với base_url="http://localhost:11434/v1"
                 và api_key="ollama" (Ollama không yêu cầu API key)
   - response(model, messages, temperature, max_tokens, **kwargs):
                 Gọi API và trả về response object

Gợi ý: Cả hai adapter đều sử dụng OpenAI SDK vì Groq và Ollama đều
       tương thích với OpenAI API format.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class GroqAdapter:
    """
    Adapter để kết nối với Groq Cloud API.
    
    Groq cung cấp API tương thích với OpenAI SDK, nên có thể sử dụng
    OpenAI client với base_url của Groq.
    
    Attributes:
        client (OpenAI): OpenAI client được cấu hình cho Groq
    """

    def __init__(self):
        """
        Khởi tạo GroqAdapter.
        
        TODO 1: Khởi tạo OpenAI client với:
        - base_url: "https://api.groq.com/openai/v1"
        - api_key: lấy từ biến môi trường GROQ_API_KEY (os.getenv("GROQ_API_KEY"))
        """
        # TODO: Khởi tạo self.client
        pass

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        """
        Gọi API để tạo phản hồi cho tin nhắn.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            messages: Danh sách tin nhắn theo format OpenAI
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung
            
        Returns:
            object: Response object từ OpenAI API
        """
        # TODO 2: Gọi self.client.chat.completions.create() với các tham số trên
        pass


class OllamaAdapter:
    """
    Adapter để kết nối với Ollama Local API.
    
    Ollama cung cấp API tương thích với OpenAI SDK, nên có thể sử dụng
    OpenAI client với base_url của Ollama.
    
    Attributes:
        client (OpenAI): OpenAI client được cấu hình cho Ollama
    """

    def __init__(self):
        """
        Khởi tạo OllamaAdapter.
        
        TODO 3: Khởi tạo OpenAI client với:
        - base_url: "http://localhost:11434/v1"
        - api_key: "ollama" (Ollama không yêu cầu API key thật)
        """
        # TODO: Khởi tạo self.client
        pass

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        """
        Gọi API để tạo phản hồi cho tin nhắn.
        
        Args:
            model: Tên model sử dụng (VD: "qwen3:0.6b-q4_K_M")
            messages: Danh sách tin nhắn theo format OpenAI API
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung
            
        Returns:
            object: Response object từ OpenAI API
        """
        # TODO 4: Gọi self.client.chat.completions.create() với các tham số trên
        pass