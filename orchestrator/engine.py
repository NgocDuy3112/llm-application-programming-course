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

    def response(
        self, 
        model: str, 
        user_prompt: str, 
        system_prompt: str | None = None,
        tools: list | None = None, 
        tool_choice: ToolChoice | None = ToolChoice.NONE,
        temperature: float | None = 0.2, 
        max_tokens: int | None = 65536
    ) -> str:
        """Xử lý user prompt và trả về response từ LLM."""
        global_logger.info(f"Xử lý input từ user: {user_prompt[:50]}...")
        # TODO(BT2): Xây dựng messages với system_prompt
        # Nếu system_prompt tồn tại, thêm vào đầu messages
        
        # TODO(BT3b): Tích hợp SlidingWindowMemory
        # 1. Thêm user_message vào memory
        # 2. Lấy messages từ memory để gửi cho LLM
        
        # TODO(BT4b): Tích hợp Function Calling
        # 1. Vòng lặp while xử lý tool_calls
        # 2. Execute tool và append kết quả vào messages
        # 3. Gọi lại LLM với messages mới
        
        # TODO(BT5): Hoàn thiện vòng lặp Function Calling
        # 1. Giới hạn max_iterations ≤ 8
        # 2. Sau vòng lặp, chỉ lưu final assistant message vào memory
        
        user_message = {"role": "user", "content": user_prompt}
        messages = [user_prompt]
        response = self.adapter.response(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
