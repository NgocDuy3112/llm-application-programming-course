from logger import global_logger



class SlidingWindowMemory():
    """Sliding window memory - giữ N messages gần nhất (Bài tập 3a).

    Bài tập: Implement add() và get_messages() để quản lý chat history.
    """

    def __init__(self, sliding_window_size: int):
        """Khởi tạo memory với sliding_window_size."""
        global_logger.debug(f"Khởi tạo SlidingWindowMemory với kích thước cửa sổ trượt là {sliding_window_size}")
        self.sliding_window_size = sliding_window_size
        self.buffer = []

    def add_message(self, message: dict):
        """Thêm message vào buffer."""
        # TODO(BT3a): Thực hiện lưu trữ message mới vào danh sách buffer để quản lý lịch sử trò chuyện.
        pass

    def get_messages(self) -> list:
        """Trả về messages theo sliding window strategy."""
        # TODO(BT3b): Triển khai thuật toán cửa sổ trượt để chỉ trả về N messages gần nhất (dựa trên sliding_window_size).
        pass
