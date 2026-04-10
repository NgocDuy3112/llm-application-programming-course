# from logger import global_logger


# class SlidingWindowMemory():
#     def __init__(self, sliding_window_size: int | None = None, memory: list | None = None):
#         global_logger.debug(f"Initializing SlidingWindowMemory with sliding_window_size={sliding_window_size}")
#         self.sliding_window_size = sliding_window_size
#         self.buffer = list(memory) if memory else []

#     def add(self, message: dict):
#         self.buffer.append(message)
#         if self.sliding_window_size is not None:
#             if len(self.buffer) > self.sliding_window_size:
#                 self.buffer = self.buffer[-self.sliding_window_size:]

#     def get_messages(self) -> list:
#         if self.sliding_window_size is None:
#             global_logger.debug(f"Retrieving all messages from buffer (total: {len(self.buffer)})")
#             return self.buffer
#         recent_messages = self.buffer[-self.sliding_window_size:]
#         global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
#         return recent_messages

from logger import global_logger



class SlidingWindowMemory():
    """
    Sliding window memory strategy - giữ k cặp messages gần nhất.

    Khi buffer vượt quá 2*k messages, chỉ giữ lại k cặp gần nhất.
    Điều này giúp hạn chế context length và chi phí API.

    Strategy:
        - Giữ lại N messages gần nhất 
        - Messages cũ hơn bị loại bỏ khỏi context gửi đến LLM

    Attributes:
        sliding_window_size (int | None): Số cặp messages để giữ lại
            - None: giữ tất cả (unlimited)
            - N: giữ N messages gần nhất

    Example:
        >>> memory = SlidingWindowMemory(sliding_window_size=5)
        >>> memory.add("user", "Hello")
        >>> memory.add("assistant", "Hi there!")
        >>> messages = memory.get_messages()  # Returns list of dicts
    """

    def __init__(self, sliding_window_size: int | None = None):
        """
        Khởi tạo memory buffer.

        Args:
            sliding_window_size (int | None): Số cặp messages để giữ lại
                - None: giữ tất cả (unlimited context)
                - N: giữ N messages gần nhất
        """
        global_logger.debug(f"Initializing SlidingWindowMemory with sliding_window_size={sliding_window_size}")
        self.sliding_window_size = sliding_window_size
        self.buffer = []

    def add(self, message: dict):
        """
        Thêm message vào buffer.

        Args:
            message (dict): Message dictionary with keys "role" and "content"
        """
        self.buffer.append(message)
        # Nếu buffer vượt quá giới hạn, loại bỏ messages cũ
        if self.sliding_window_size is not None:
            if len(self.buffer) > self.sliding_window_size:
                self.buffer = self.buffer[-self.sliding_window_size:]

    def get_messages(self) -> list:
        """
        Lấy messages theo sliding window strategy.

        Returns:
            list:
                - Nếu sliding_window_size is None: tất cả messages trong buffer
                - Nếu có sliding_window_size: tối đa sliding_window_size messages gần đây

        Note:
            - Buffer gốc không bị modify, chỉ trả về slice
            - Window luôn lấy từ end của buffer (messages gần nhất)
        """
        if self.sliding_window_size is None:
            global_logger.debug(f"Retrieving all messages from buffer (total: {len(self.buffer)})")
            return self.buffer
        recent_messages = self.buffer[-self.sliding_window_size:]
        global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
        return recent_messages
