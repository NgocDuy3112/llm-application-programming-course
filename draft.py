# model/adapter.py
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    def __init__(self):
        self.client = self._initialize_client()

    @abstractmethod
    # Mỗi lớp con chịu trách nhiệm khởi tạo client cho từng nhà cung cấp (Groq, Ollama,...)
    # giúp tách biệt phần cấu hình cụ thể của từng provider khỏi logic chung của hệ thống
    def _initialize_client(self):
        pass

    # Phương thức response() chung được các lớp con kế thừa
    # cung cấp interface thống nhất để gọi LLM
    # giúp dễ dàng thay đổi model hoặc provider mà không ảnh hưởng đến phần còn lại của hệ thống
    def response(self, model: str, messages: list, **kwargs):
        return self.client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )