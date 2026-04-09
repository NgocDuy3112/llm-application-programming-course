"""
Module 5 - Chatbot Engine

Mô tả: Engine chính của chatbot, chịu trách nhiệm điều phối việc gọi API
và quản lý lịch sử hội thoại (memory).

TODO: Hoàn thành class ChatbotEngine dưới đây:

1. __init__(self, adapter, memory=None):
   - Lưu adapter và memory vào instance attributes
   - adapter: một trong các adapter từ model/adapter.py (GroqAdapter hoặc OllamaAdapter)
   - memory: object quản lý lịch sử hội thoại (có thể là None)

2. response(self, model, user_prompt, temperature, max_tokens, system_prompt=None, **kwargs):
   - Nếu có system_prompt, thêm system message vào đầu messages list
   - Nếu có memory, lấy lịch sử từ memory và thêm vào messages
   - Thêm user message vào messages
   - Gọi adapter.response() với messages đã xây dựng
   - Nếu có memory, lưu user message và assistant response vào memory
   - Trích xuất và trả về nội dung text từ response

Gợi ý: Format messages theo OpenAI API:
   - System: {"role": "system", "content": "..."}
   - User: {"role": "user", "content": "..."}
   - Assistant: {"role": "assistant", "content": "..."}
"""

from model.adapter import GroqAdapter, OllamaAdapter


class ChatbotEngine:
    """
    Engine chính của chatbot với kết nối API thật và quản lý memory.
    
    Class này chịu trách nhiệm:
    1. Khởi tạo kết nối với LLM API thông qua adapter
    2. Xử lý logic định dạng messages (bao gồm system prompt và history)
    3. Điều phối việc gọi API và trả về kết quả
    4. Quản lý lịch sử hội thoại thông qua memory object
    
    Attributes:
        adapter (GroqAdapter | OllamaAdapter): Adapter để kết nối với LLM API
        memory (object | None): Object quản lý lịch sử hội thoại
    """
    
    def __init__(self, adapter, memory=None):
        """
        Khởi tạo ChatbotEngine.
        
        Args:
            adapter: Instance của GroqAdapter hoặc OllamaAdapter
            memory: Object quản lý lịch sử hội thoại (có thể là None)
        """
        # TODO 1: Lưu adapter và memory vào instance attributes
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
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            user_prompt: Tin nhắn của người dùng
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            system_prompt: Câu lệnh hệ thống (có thể là None)
            **kwargs: Các tham số bổ sung cho API
            
        Returns:
            str: Nội dung phản hồi từ AI
        """
        # TODO 2: Xây dựng messages list
        # Bắt đầu với list rỗng
        messages = []
        
        # TODO 3: Nếu có system_prompt, thêm system message vào đầu messages
        # Format: {"role": "system", "content": system_prompt}
        
        # TODO 4: Nếu có memory, lấy lịch sử từ memory và thêm vào messages
        # Gợi ý: memory.get_messages() trả về list các messages trong lịch sử
        
        # TODO 5: Thêm user message vào messages
        # Format: {"role": "user", "content": user_prompt}
        
        # TODO 6: Gọi adapter.response() với messages đã xây dựng
        # Truyền: model, messages, temperature, max_tokens, **kwargs
        
        # TODO 7: Nếu có memory, lưu user message và assistant response vào memory
        # Gợi ý: memory.add_user_message(user_prompt) và memory.add_assistant_message(response_content)
        
        # TODO 8: Trích xuất và trả về nội dung text từ response
        # response.choices[0].message.content
        pass