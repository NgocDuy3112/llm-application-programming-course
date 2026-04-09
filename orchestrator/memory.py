"""
Module 5 - Memory Management

Mô tả: Cung cấp các class quản lý lịch sử hội thoại (context memory)
cho chatbot. Memory giúp chatbot ghi nhớ các tin nhắn trước đó
để tạo phản hồi phù hợp với ngữ cảnh.

TODO: Hoàn thành class SlidingWindowMemory dưới đây:

1. __init__(self, sliding_window_size=5):
   - Khởi tạo với kích thước cửa sổ trượt (số cặp tin nhắn user-assistant)
   - Khởi tạo list rỗng để lưu trữ messages

2. add_user_message(self, content):
   - Thêm user message vào danh sách messages
   - Format: {"role": "user", "content": content}

3. add_assistant_message(self, content):
   - Thêm assistant message vào danh sách messages
   - Format: {"role": "assistant", "content": content}
   - Sau khi thêm, gọi _trim() để giữ chỉ sliding_window_size cặp tin nhắn gần nhất

4. get_messages(self):
   - Trả về danh sách messages hiện tại

5. _trim(self):
   - Xóa các tin nhắn cũ nhất, giữ lại chỉ sliding_window_size * 2 tin nhắn
   - (Mỗi cặp user-assistant = 2 tin nhắn)
   - Nếu số tin nhắn > sliding_window_size * 2, xóa tin nhắn cũ nhất trước

Gợi ý: Sliding window giữ lại k cặp user-assistant messages gần nhất.
Ví dụ: sliding_window_size=3 sẽ giữ lại 6 tin nhắn gần nhất (3 user + 3 assistant).
"""


class SlidingWindowMemory:
    """
    Quản lý lịch sử hội thoại bằng cửa sổ trượt (sliding window).
    
    Chỉ giữ lại k cặp user-assistant messages gần nhất, 
    trong đó k = sliding_window_size.
    
    Attributes:
        sliding_window_size (int): Số cặp tin nhắn user-assistant được giữ lại
        messages (list): Danh sách các tin nhắn trong lịch sử
    """
    
    def __init__(self, sliding_window_size: int = 5):
        """
        Khởi tạo SlidingWindowMemory.
        
        Args:
            sliding_window_size: Số cặp tin nhắn user-assistant được giữ lại (mặc định: 5)
        """
        # TODO 1: Lưu sliding_window_size vào instance attribute
        # TODO 2: Khởi tạo self.messages = []
        pass

    def add_user_message(self, content: str):
        """
        Thêm user message vào danh sách messages.
        
        Args:
            content: Nội dung tin nhắn của user
        """
        # TODO 3: Thêm {"role": "user", "content": content} vào self.messages
        pass

    def add_assistant_message(self, content: str):
        """
        Thêm assistant message vào danh sách messages và trim.
        
        Args:
            content: Nội dung phản hồi từ assistant
        """
        # TODO 4: Thêm {"role": "assistant", "content": content} vào self.messages
        # TODO 5: Gọi self._trim() để giữ chỉ sliding_window_size cặp tin nhắn gần nhất
        pass

    def get_messages(self) -> list:
        """
        Trả về danh sách messages hiện tại.
        
        Returns:
            list: Danh sách các tin nhắn trong lịch sử
        """
        # TODO 6: Trả về self.messages
        pass

    def _trim(self):
        """
        Xóa các tin nhắn cũ nhất, giữ lại chỉ sliding_window_size * 2 tin nhắn.
        Mỗi cặp user-assistant = 2 tin nhắn.
        """
        # TODO 7: Nếu số tin nhắn > sliding_window_size * 2,
        # xóa các tin nhắn cũ nhất để giữ lại chỉ sliding_window_size * 2 tin nhắn
        # Gợi ý: self.messages = self.messages[-(self.sliding_window_size * 2):]
        pass