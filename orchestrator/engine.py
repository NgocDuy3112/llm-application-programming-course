"""
Module 5 - Chatbot Engine

Mô tả: Engine chính của chatbot, chịu trách nhiệm điều phối việc gọi API
và quản lý lịch sử hội thoại (memory).

TODO 3: Hoàn thành class ChatbotEngine:
- __init__(self, adapter, memory=None): Lưu adapter và memory vào instance attributes
- response(self, model, user_prompt, temperature, max_tokens, system_prompt=None, **kwargs):
  1. Xây dựng messages list: thêm system message (nếu có), thêm history từ memory (nếu có), thêm user message
  2. Gọi adapter.response() với messages đã xây dựng
  3. Nếu có memory, lưu user message và assistant response vào memory
  4. Trích xuất và trả về nội dung text từ response (response.choices[0].message.content)

Format messages theo OpenAI API:
  - System: {"role": "system", "content": "..."}
  - User: {"role": "user", "content": "..."}
  - Assistant: {"role": "assistant", "content": "..."}
"""

from model.adapter import GroqAdapter, OllamaAdapter


class ChatbotEngine:
    """
    Engine chính của chatbot với kết nối API thật và quản lý memory.
    """

    def __init__(self, adapter, memory=None):
        # TODO 3: Lưu adapter và memory vào instance attributes
        pass

    def response(
        self,
        model: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
        **kwargs
    ):
        """
        Tạo phản hồi cho tin nhắn của người dùng.

        Quy trình:
        1. Xây dựng messages list (system + history + user)
        2. Gọi adapter.response()
        3. Lưu vào memory (nếu có)
        4. Trích xuất và trả về nội dung text
        """
        # TODO 3: Implement toàn bộ logic response
        pass