import json

from logger import global_logger
from orchestrator.tools import *
from orchestrator.memory import *
from model.adapter import *


class ChatbotEngine:
    """Chatbot engine - tích hợp adapter, memory, system prompt và function calling.

    Bài tập:
    - BT2: Thêm system_prompt vào messages
    - BT3b: Tích hợp SlidingWindowMemory
    - BT4b: Thêm function calling với vòng lặp while
    - BT5: Thêm guardrail max_iterations và chỉ lưu final message
    """

    def __init__(self, adapter: BaseAdapter, memory: SlidingWindowMemory):
        """Khởi tạo engine với adapter và memory."""
        global_logger.debug(f"Khởi tạo ChatbotEngine với adapter={adapter.__class__.__name__ if adapter else 'None'} và memory={memory.__class__.__name__ if memory else 'None'}")
        self.adapter = adapter
        self.memory = memory
        self.default_system_prompt = """
        Bạn là một trợ lý ảo hữu ích và thân thiện. Hãy trả lời câu hỏi của người dùng một cách chính xác và ngắn gọn.
        """

    def response(
        self, 
        model: str, 
        user_prompt: str, 
        system_prompt: str | None = None,
        tools: list | None = None, 
        tool_choice: Literal["auto", "none"] = "none",
        temperature: float | None = 0.2, 
        max_completion_tokens: int | None = 65536
    ) -> str:
        """Xử lý user prompt và trả về response từ LLM."""
        global_logger.info(f"Xử lý input từ user: {user_prompt[:50]}...")
        # TODO(BT2a): Khởi tạo danh sách `messages`. Nếu `system_prompt` được cung cấp, hãy thêm nó làm message đầu tiên với role 'system'.
        # Sau đó thêm yêu cầu của người dùng (`user_prompt`) với role 'user'. Đừng quên sử dụng `temperature` và `max_completion_tokens` khi gọi adapter.
        
        # TODO(BT3c): Sử dụng đối tượng `self.memory` để quản lý ngữ cảnh:
        # 1. Gọi `add_message()` để lưu trữ message mới của user.
        # 2. Thay vì tự tạo list messages, hãy dùng `get_messages()` từ memory để lấy lịch sử đã được giới hạn bởi cửa sổ trượt.
        
        # TODO(BT4b): Implement cơ chế Loop-back cho Function Calling:
        # 1. Kiểm tra nếu LLM yêu cầu gọi tool (`tool_calls`).
        # 2. Thực thi hàm tương ứng trong `AVAILABLE_FUNCTIONS`, lấy kết quả và thêm vào context messages.
        # 3. Tiếp tục gọi LLM với messages mới cho đến khi nhận được câu trả lời cuối cùng.
        
        # TODO(BT5): Triển khai các quy tắc kiểm soát bổ sung:
        # 1. Kết hợp system prompt để hướng dẫn LLM chỉ trả về câu trả lời cuối cùng sau khi hoàn thành tất cả tool calls.
        # 2. Sử dụng self.memory để truy vết lịch sử hội thoại và chỉ lưu message cuối cùng (final answer) vào memory để tối ưu hóa ngữ cảnh cho các cuộc hội thoại dài hạn.
        
        user_message = {"role": "user", "content": user_prompt}
        messages = [user_message]
        response = self.adapter.response(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
