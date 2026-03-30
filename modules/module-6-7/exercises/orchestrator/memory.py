"""
Module 6-7 - Memory Management

Mô tả: Quản lý lịch sử cuộc trò chuyện với hỗ trợ multiple memory strategies:
- None: Lưu tất cả messages (unlimited context)
- Sliding Window (k): Giữ k cặp messages gần nhất để hạn chế context length

Kiến trúc / Dependencies:
- logger: Global logger để tracking memory operations
- Được sử dụng bởi FullChatbotEngine để quản lý chat context

Design Patterns:
- Strategy Pattern: BaseMemory định nghĩa interface, WindowMemory implement strategy
- Template Method: add(), add_tool_message() được kế thừa, get_messages() được override

Usage:
    # Unlimited memory (keep all messages)
    memory = BaseMemory()
    
    # Sliding window (keep last k turns)
    memory = WindowMemory(sliding_window_size=5)
    memory.add("user", "Hello")
    messages = memory.get_messages()
"""

from abc import ABC, abstractmethod
from logger import global_logger


class BaseMemory(ABC):
    """
    Abstract base class cho các memory management strategies.

    Cung cấp interface thống nhất để lưu trữ và truy xuất chat history.
    Các subclass implement chiến lược lấy messages khác nhau (all, sliding window).

    Attributes:
        buffer (list): Danh sách tất cả messages được lưu
            Format: [{"role": str, "content": str, "tool_calls": list?}, ...]

    Note:
        - Buffer được copy khi khởi tạo để tránh side effects
        - Tool calls được lưu trữ cùng assistant messages khi có
    """

    def __init__(self, memory: list | None = None):
        """
        Khởi tạo memory buffer.

        Args:
            memory (list | None): Initial messages để load vào buffer
                - Nếu None: buffer rỗng
                - Nếu list: copy các messages vào buffer
        """
        # Copy the list instead of direct reference to avoid duplicate appends
        self.buffer = list(memory) if memory is not None else []

    def add(self, role: str, content: str | None = None, tool_calls=None):
        """
        HƯỚNG DẪN: Thêm message mới vào memory.
        - role: "user", "assistant", "system", hoặc "tool"
        - content: Nội dung text
        - tool_calls: Danh sách các tool calls (chỉ dành cho assistant role)
        """
        global_logger.debug(f"Adding message: role={role}, content={content}, tool_calls={tool_calls}")
        # TODO: Triển khai logic lưu message vào self.buffer
        pass

    def add_tool_message(self, tool_call, content: str):
        """
        HƯỚNG DẪN: Lưu phản hồi của tool vào memory.
        - tool_call_id: Phải khớp với 'id' của tool_call mà model đã yêu cầu.
        - name: Tên của tool đã được gọi (để model đối chiếu).
        - role: PHẢI là "tool" cho role của message này.
        """
        global_logger.debug(f"Adding tool message for {tool_call.function.name}")
        # TODO: Triển khai logic lưu tool response vào self.buffer
        pass

    @abstractmethod
    def get_messages(self) -> list:
        """
        Lấy messages theo strategy (all hoặc sliding window).

        Returns:
            list: List of message dicts ready to send to LLM API
                Format: [{"role": str, "content": str}, ...]
        """
        pass


class WindowMemory(BaseMemory):
    """
    Sliding window memory strategy - giữ k cặp messages gần nhất.

    Khi buffer vượt quá 2*k messages, chỉ giữ lại k cặp gần nhất.
    Điều này giúp hạn chế context length và chi phí API.

    Strategy:
        - Mỗi "turn" = 1 user message + 1 assistant message = 2 messages
        - sliding_window_size = k => giữ tối đa 2*k messages
        - Messages cũ hơn bị loại bỏ khỏi context gửi đến LLM

    Attributes:
        sliding_window_size (int | None): Số cặp messages để giữ lại
            - None: giữ tất cả (unlimited)
            - N: giữ 2*N messages (N user-assistant pairs)

    Example:
        >>> memory = WindowMemory(sliding_window_size=5)
        >>> memory.add("user", "Hello")
        >>> memory.add("assistant", "Hi there!")
        >>> messages = memory.get_messages()  # Returns list of dicts
    """

    def __init__(self, memory: list | None = None, sliding_window_size: int | None = None):
        """
        Khởi tạo sliding window memory.

        Args:
            memory (list | None): Initial messages để load vào buffer
            sliding_window_size (int | None): Số cặp messages để giữ lại
                - None: giữ tất cả (unlimited context)
                - N: giữ 2*N messages gần nhất
        """
        global_logger.debug(f"Initializing WindowMemory with sliding_window_size={sliding_window_size}")
        super().__init__(memory=memory)
        self.sliding_window_size = sliding_window_size


    def get_messages(self) -> list:
        """
        Lấy messages theo sliding window strategy.

        Returns:
            list:
                - Nếu sliding_window_size is None: tất cả messages trong buffer
                - Nếu có sliding_window_size: tối đa 2*sliding_window_size messages gần đây

        Note:
            - Buffer gốc không bị modify, chỉ trả về slice
            - Window luôn lấy từ end của buffer (messages gần nhất)
        """
        if self.sliding_window_size is None:
            global_logger.debug(f"Retrieving all messages from buffer (total: {len(self.buffer)})")
            return self.buffer
        num_messages = 2 * self.sliding_window_size
        recent_messages = self.buffer[-num_messages:]
        global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
        return recent_messages
