from logger import global_logger



class SlidingWindowMemory():
    """Sliding window memory - giữ N messages gần nhất (Bài tập 3a).

    Bài tập: Implement add() và get_messages() để quản lý chat history.
    """

    def __init__(self, sliding_window_size: int | None = None):
        """Khởi tạo memory với sliding_window_size."""
        global_logger.debug(f"Khởi tạo SlidingWindowMemory với kích thước cửa sổ trượt là {sliding_window_size}")
        self.sliding_window_size = sliding_window_size
        self.buffer = []

    def add(self, message: dict):
        """Thêm message vào buffer."""
        # TODO: Thêm message vào buffer
        pass

    def get_messages(self) -> list:
        """Trả về messages theo sliding window strategy."""
        # TODO: Trả về messages theo sliding window
        pass
