"""
Module 5 - Memory Management: Sliding Window Memory

Mô tả: Triển khai sliding window memory strategy - giữ k cặp messages gần nhất.
"""

from logger import global_logger


class SlidingWindowMemory:
    """
    Sliding window memory strategy - giữ k cặp messages gần nhất.
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
        if self.sliding_window_size is not None:
            if len(self.buffer) > self.sliding_window_size:
                self.buffer = self.buffer[-self.sliding_window_size:]

    def get_messages(self) -> list:
        """
        Lấy messages theo sliding window strategy.

        Returns:
            list: Messages trong buffer
        """
        if self.sliding_window_size is None:
            global_logger.debug(f"Retrieving all messages from buffer (total: {len(self.buffer)})")
            return self.buffer
        recent_messages = self.buffer[-self.sliding_window_size:]
        global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
        return recent_messages