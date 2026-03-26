# Khai báo module docstring - mô tả chức năng của module memory management
"""
Module 6-7 - Memory Management

Mô tả: Quản lý lịch sử cuộc trò chuyện với hỗ trợ multiple memory strategies:
- None: Lưu tất cả messages (unlimited context)
- Sliding Window (k): Giữ k cặp messages gần nhất để hạn chế context length

Kiến trúc / Dependencies:
- logger: Global logger để tracking memory operations
- Được sử dụng bởi FullChatbotEngine để quản lý chat context
"""

# Import ABC (Abstract Base Class) và abstractmethod từ abc module
# Dùng để định nghĩa abstract class (class không thể khởi tạo trực tiếp)
from abc import ABC, abstractmethod
# Import global_logger từ logger module để ghi log hoạt động
from logger import global_logger


# Định nghĩa BaseMemory class kế thừa từ ABC (Abstract Base Class)
class BaseMemory(ABC):
    """
    Abstract base class cho các memory management strategies.

    Attributes:
        sliding_window_size (int | None): Kích thước sliding window (cặp messages)
            - None: lưu tất cả messages
            - N: lưu 2*N messages gần nhất (N user-assistant pairs)
        buffer (list): Danh sách tất cả messages
    """
    
    # Constructor của BaseMemory class
    def __init__(self, memory: list | None = None):
        """
        Khởi tạo BaseMemory với buffer lưu trữ messages.

        Args:
            memory (list | None): List messages ban đầu. Nếu None thì tạo list rỗng.
        """
        # Copy list thay vì reference trực tiếp để tránh duplicate appends
        # Nếu memory là None, tạo list rỗng []
        self.buffer = list(memory) if memory is not None else []

    # Method để thêm message vào buffer
    def add(self, role: str, content: str | None = None, tool_calls=None):
        """
        Thêm message vào buffer.

        Args:
            role (str): 'user', 'assistant', hoặc 'system'
            content (str | None): Nội dung message
            tool_calls (list | None): Danh sách tool calls (cho assistant messages)
        """
        # Ghi log debug: thông tin message được thêm
        global_logger.debug(f"Adding message: role={role}, content={content}, tool_calls={tool_calls}")
        
        # Tạo message dictionary với role và content
        msg = {"role": role, "content": content}
        
        # Nếu có tool_calls, thêm vào message dictionary
        if tool_calls:
            msg["tool_calls"] = tool_calls
            # Ghi log debug: số lượng tool calls
            global_logger.debug(f"Message includes {len(tool_calls)} tool calls")
        
        # Append message vào buffer
        self.buffer.append(msg)

    # Method để thêm tool call result message vào buffer
    def add_tool_message(self, tool_call, content: str):
        """
        Thêm tool call result message vào buffer.

        Args:
            tool_call: OpenAI ToolCall object (có .id, .function.name)
            content (str): Kết quả thực thi tool
        """
        # Ghi log debug: tên tool được thêm
        global_logger.debug(f"Adding tool message for {tool_call.function.name}")
        
        # Append tool message dictionary vào buffer
        self.buffer.append({
            # Role là "tool" cho tool response messages
            "role": "tool",
            # ID của tool call để link với request
            "tool_call_id": tool_call.id,
            # Tên của tool được gọi
            "name": tool_call.function.name,
            # Nội dung kết quả (convert sang string)
            "content": str(content)
        })

    # Abstract method - các subclass phải implement method này
    @abstractmethod
    def get_messages(self) -> list:
        """
        Lấy messages theo strategy (all hoặc sliding window).
        
        Returns:
            list: Danh sách messages
        """
        # Pass - implementation sẽ được định nghĩa trong subclass
        pass


# Định nghĩa WindowMemory class kế thừa từ BaseMemory
class WindowMemory(BaseMemory):
    """
    Sliding window memory strategy - giữ k cặp messages gần nhất.

    Khi buffer vượt quá 2*k messages, chỉ giữ lại k cặp gần nhất.
    Điều này giúp hạn chế context length và chi phí API.

    Args:
        sliding_window_size (int | None): Số cặp messages để giữ lại
            - None: giữ tất cả (unlimited)
            - N: giữ 2*N messages (N user-assistant pairs)

    Example:
        >>> memory = WindowMemory(sliding_window_size=5)
        >>> memory.add("user", "Hello")
        >>> memory.add("assistant", "Hi there!")
        >>> messages = memory.get_messages()  # Returns list of dicts
    """
    
    # Constructor của WindowMemory class
    def __init__(self, memory: list | None = None, sliding_window_size: int | None = None):
        """
        Khởi tạo WindowMemory với sliding window size.

        Args:
            memory (list | None): List messages ban đầu
            sliding_window_size (int | None): Số cặp messages để giữ lại
        """
        # Ghi log debug: khởi tạo với sliding window size
        global_logger.debug(f"Initializing WindowMemory with sliding_window_size={sliding_window_size}")
        
        # Gọi constructor của parent class (BaseMemory)
        super().__init__(memory=memory)
        
        # Lưu sliding window size vào instance variable
        self.sliding_window_size = sliding_window_size

    # Implement abstract method get_messages() từ BaseMemory
    def get_messages(self) -> list:
        """
        Lấy messages theo sliding window strategy.

        Returns:
            list:
                - Nếu sliding_window_size is None: tất cả messages trong buffer
                - Nếu có sliding_window_size: tối đa 2*sliding_window_size messages gần đây
        """
        # Kiểm tra nếu sliding_window_size là None (không giới hạn)
        if self.sliding_window_size is None:
            # Ghi log debug: lấy tất cả messages
            global_logger.debug(f"Retrieving all messages from buffer (total: {len(self.buffer)})")
            # Trả về toàn bộ buffer
            return self.buffer
        
        # Tính số messages cần lấy = 2 * số cặp (mỗi cặp có 1 user + 1 assistant)
        num_messages = 2 * self.sliding_window_size
        
        # Lấy danh sách messages gần nhất dùng slice [-num_messages:]
        # Slice này lấy num_messages messages từ cuối list
        recent_messages = self.buffer[-num_messages:]
        
        # Ghi log debug: số messages lấy được
        global_logger.debug(f"Retrieving {len(recent_messages)} recent messages from buffer (total: {len(self.buffer)})")
        
        # Trả về danh sách messages gần nhất
        return recent_messages
