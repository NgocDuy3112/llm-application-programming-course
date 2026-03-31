"""
Module 6-7 - Memory Management

Mô tả: Quản lý lịch sử cuộc trò chuyện với hỗ trợ multiple memory strategies:
- None: Lưu tất cả messages (unlimited context)
- Sliding Window (k): Giữ k cặp messages gần nhất để hạn chế context length

Kiến trúc / Dependencies:
- logger: Global logger để tracking memory operations
- Được sử dụng bởi FullChatbotEngine để quản lý chat context

Design Notes:
- Đây chỉ cung cấp một implementation `WindowMemory` (sliding window).

Integration notes:
- Ensure `get_messages()` returns the correct slice of `buffer` (2 * sliding_window_size)
- Ensure `add()` and `add_tool_message()` produce messages in the expected shape for the adapter/engine

Usage:
    # Sliding window (keep last k turns)
    memory = WindowMemory(sliding_window_size=5)
    memory.add("user", "Hello")
    messages = memory.get_messages()
"""

from logger import global_logger


class WindowMemory:
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
        # Copy provided memory list (if any) to internal buffer
        self.buffer = list(memory) if memory is not None else []
        self.sliding_window_size = sliding_window_size


    def add(self, role: str, content: str | None = None, tool_calls=None):
        """
        Thêm message mới vào memory.

        Args:
            role (str): Role của message ('user', 'assistant', 'system', 'tool')
            content (str | None): Nội dung text của message
            tool_calls (list | None): Danh sách tool calls (cho assistant messages)
        """
        global_logger.debug(f"Adding message: role={role}, content={content}, tool_calls={tool_calls}")
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
            global_logger.debug(f"Message includes {len(tool_calls)} tool calls")
        self.buffer.append(msg)


    def add_tool_message(self, tool_call, content: str):
        """
        Thêm tool call result message vào buffer.

        Args:
            tool_call: Tool call object với attributes `.id` và `.function.name`
            content (str): Kết quả thực thi tool
        """
        global_logger.debug(f"Adding tool message for {tool_call.function.name}")
        self.buffer.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": str(content)
        })


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
