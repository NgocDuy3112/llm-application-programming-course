"""
Module 5 - Orchestrator Layer: ChatbotEngine (Simplified)

Mô tả: Chatbot engine đơn giản hóa - chỉ sử dụng model và messages parameters.
File này chứa logic nghiệp vụ chính của chatbot.
"""

from logger import global_logger
from orchestrator.memory import SlidingWindowMemory
from model.adapter import BaseAdapter


class ChatbotEngine:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (SlidingWindowMemory | None): Memory manager instance
    """

    def __init__(self, adapter: BaseAdapter, memory: SlidingWindowMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter): LLM adapter instance
            memory (SlidingWindowMemory | None): Memory manager instance (optional)
        """
        global_logger.debug(f"Initializing ChatbotEngine with adapter={adapter.__class__.__name__}")
        self.adapter = adapter
        self.memory = memory

    def response(
        self,
        model: str,
        user_prompt: str,
    ) -> str:
        """
        Tạo phản hồi cho tin nhắn của người dùng.

        Args:
            model (str): Model name/ID (e.g., "qwen/qwen3-32b")
            user_prompt (str): Tin nhắn của người dùng

        Returns:
            str: Nội dung phản hồi từ AI
        """
        global_logger.info(f"Processing with model: {model}, user_prompt: {user_prompt[:50]}...")

        # Tạo messages list từ user_prompt
        messages = [{"role": "user", "content": user_prompt}]

        # Gọi LLM với chỉ model và messages
        response = self.adapter.response(
            model=model,
            messages=messages,
        )

        # Trích xuất nội dung từ response
        return response.choices[0].message.content