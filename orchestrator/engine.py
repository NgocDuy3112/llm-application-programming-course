from model.adapter import groq_adapter


class ChatbotEngine:
    """
    Engine chính của chatbot với kết nối API thật và quản lý memory.
    
    Class này chịu trách nhiệm:
    1. Khởi tạo kết nối với LLM API thông qua adapter
    2. Xử lý logic định dạng messages (bao gồm system prompt và history)
    3. Điều phối việc gọi API và trả về kết quả
    4. Quản lý lịch sử hội thoại thông qua memory object
    
    Attributes:
        adapter: Adapter để kết nối với LLM API
    """
    
    def __init__(self, adapter):
        self.adapter = adapter

    def response(
        self,
        model: str,
        user_prompt: str,
    ):
        """
        Tạo phản hồi cho tin nhắn của người dùng.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            user_prompt: Tin nhắn của người dùng
            
        Returns:
            str: Nội dung phản hồi từ AI
        """
        # TODO: Tạo mảng messages chứa một từ điển có dạng {"role": "user", "content": user_prompt}
        # để thư viện hiểu được đúng định dạng tin nhắn đầu vào
    
        # TODO: Truyền vào model và user_prompt vào phương thức chat.completions.create() trong self.client 
        # để lấy về phản hồi, lưu vào biến response

        # TODO: Trả về nội dung của phản hồi
        # để hiển thị lên giao diện
        pass
