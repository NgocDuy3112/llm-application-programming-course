# Module 5
# Import thư viện os để làm việc với hệ điều hành và biến môi trường
import os
# Import hàm load_dotenv từ thư viện dotenv để load biến môi trường từ file .env
from dotenv import load_dotenv
# Import class GroqCloudAdapter từ module model/adapter.py
from model.adapter import GroqCloudAdapter


# Load biến môi trường từ file .env
# override=True cho phép ghi đè biến môi trường đã tồn tại
# dotenv_path=".env": chỉ định đường dẫn file .env trong thư mục hiện tại
load_dotenv(dotenv_path=".env", override=True)


class ChatbotEngine:
    """
    Engine chính của chatbot với kết nối API thật.
    
    Class này chịu trách nhiệm:
    1. Khởi tạo kết nối với Groq API thông qua adapter
    2. Xử lý logic định dạng messages
    3. Điều phối việc gọi API và trả về kết quả
    
    Attributes:
        adapter (GroqCloudAdapter): Adapter để kết nối với Groq API
    """
    
    def __init__(self):
        """
        Khởi tạo ChatbotEngine với GroqCloudAdapter.
        
        API key được lấy từ biến môi trường GROQ_API_KEY.
        File .env phải có dòng: GROQ_API_KEY=gsk_xxx
        """
        # Tạo adapter với API key lấy từ biến môi trường
        # os.getenv("GROQ_API_KEY"): lấy giá trị biến GROQ_API_KEY từ .env
        # Nếu không tìm thấy, trả về None
        self.adapter = GroqCloudAdapter(api_key=os.getenv("GROQ_API_KEY"))

    def response(
        self,
        model: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Tạo phản hồi cho tin nhắn của người dùng.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            user_prompt: Tin nhắn của người dùng
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung cho API
            
        Returns:
            str: Nội dung phản hồi từ AI
        """
        # Định dạng tin nhắn theo format OpenAI API
        # Tạo list chứa một message với role "user" và content là user_prompt
        user_message = [{"role": "user", "content": user_prompt}]
        
        # Gọi API thông qua adapter
        # Truyền các tham số cần thiết cho việc tạo phản hồi
        response = self.adapter.response(
            model=model,
            messages=user_message,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Trích xuất nội dung từ response
        # response.choices[0]: lấy completion option đầu tiên
        # .message.content: lấy nội dung text của message
        return response.choices[0].message.content
