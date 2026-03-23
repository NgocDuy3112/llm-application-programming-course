"""
Module 5 - Orchestrator Layer: ChatbotEngine

File này chứa logic nghiệp vụ chính của chatbot, đóng vai trò là tầng điều phối
(orchestrator) giữa UI và Model layer.

Trách nhiệm của Orchestrator Layer:
1. Nhận input từ UI layer
2. Xử lý logic nghiệp vụ (định dạng messages, xử lý context, etc.)
3. Gọi Model layer để lấy dữ liệu
4. Trả kết quả về UI layer

Kiến trúc 3 tầng:
┌─────────────────┐
│   UI Layer      │  ← Giao diện người dùng (Streamlit)
├─────────────────┤
│ Orchestrator    │  ← Logic nghiệp vụ (File này)
├─────────────────┤
│   Model Layer   │  ← Kết nối API (adapter.py)
└─────────────────┘
"""

# =============================================================================
# IMPORTS
# =============================================================================
import os

from dotenv import load_dotenv
from model.adapter import GroqCloudAdapter


# =============================================================================
# CONFIGURATION
# =============================================================================
# Load biến môi trường từ file .env
# override=True cho phép ghi đè biến môi trường đã tồn tại
load_dotenv(dotenv_path=".env", override=True)


# =============================================================================
# CLASS DEFINITIONS
# =============================================================================
class ChatbotEngine:
    """
    Engine chính của chatbot với kết nối API thật.
    
    Class này chịu trách nhiệm:
    1. Khởi tạo kết nối với Groq API thông qua adapter
    2. Xử lý logic định dạng messages
    3. Điều phối việc gọi API và trả về kết quả
    
    Attributes:
        adapter (GroqCloudAdapter): Adapter để kết nối với Groq API
    
    Example:
        >>> engine = ChatbotEngine()
        >>> response = engine.response(
        ...     model="openai/gpt-oss-20b",
        ...     input="Hello, how are you?",
        ...     temperature=0.7,
        ...     max_tokens=1024
        ... )
    """
    
    def __init__(self):
        """
        Khởi tạo ChatbotEngine với GroqCloudAdapter.
        
        API key được lấy từ biến môi trường GROQ_API_KEY.
        File .env phải có dòng: GROQ_API_KEY=gsk_xxx
        """
        self.adapter = GroqCloudAdapter(api_key=os.getenv("GROQ_API_KEY"))

    def response(
        self,
        model: str, 
        input: str, 
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """
        Tạo phản hồi cho tin nhắn của người dùng.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            input: Tin nhắn của người dùng
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung cho API
        
        Returns:
            str: Nội dung phản hồi từ AI
        
        Quy trình xử lý:
        1. Định dạng input thành messages list theo format OpenAI
        2. Gọi adapter để gửi request đến API
        3. Trích xuất nội dung từ response
        """
        # Định dạng tin nhắn theo format OpenAI API
        # Format: [{"role": "user"|"assistant"|"system", "content": "..."}]
        user_message = [{"role": "user", "content": input}]
        
        # Gọi API thông qua adapter
        response = self.adapter.response(
            model=model, 
            messages=user_message, 
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Trích xuất nội dung từ response
        # response.choices là danh sách các completion options
        # message.content là nội dung tin nhắn
        return response.choices[0].message.content


class FakeChatbotEngine:
    """
    Engine giả định để test UI mà không cần kết nối API.
    
    Class này hữu ích khi:
    1. Phát triển UI mà chưa có API key
    2. Test giao diện mà không tốn quota API
    3. Demo tính năng cho khách hàng
    
    Returns:
        str: Phản hồi giả định chứa thông tin về request
    
    Example:
        >>> engine = FakeChatbotEngine()
        >>> response = engine.response(
        ...     model="test-model",
        ...     input="Hello",
        ...     temperature=0.5,
        ...     max_tokens=100
        ... )
        >>> print(response)
        "Đây là phản hồi giả cho tin nhắn: 'Hello' ..."
    """
    
    def response(
        self, 
        model: str, 
        input: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """
        Tạo phản hồi giả định cho mục đích test.
        
        Args:
            model: Tên model (không sử dụng)
            input: Tin nhắn của người dùng
            temperature: Độ sáng tạo (không sử dụng)
            max_tokens: Số token tối đa (không sử dụng)
            **kwargs: Các tham số khác (không sử dụng)
        
        Returns:
            str: Phản hồi giả định chứa thông tin request
        """
        return f"Đây là phản hồi giả cho tin nhắn: '{input}' (model: {model}, temperature: {temperature}, max_tokens: {max_tokens}), các tham số khác: {kwargs})"