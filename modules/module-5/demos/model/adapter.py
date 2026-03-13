"""
Module 5 - Model Layer: GroqCloudAdapter

File này chứa adapter để kết nối với Groq API thông qua OpenAI SDK.
Groq cung cấp API tương thích với OpenAI, cho phép sử dụng SDK của OpenAI
với base_url của Groq.

Kiến trúc:
- Adapter Pattern: Chuyển đổi interface của Groq API thành interface thống nhất
- Dependency Injection: API key được inject từ bên ngoài (từ .env)

Lợi ích của Adapter Pattern:
1. Dễ dàng thay đổi provider (Groq -> OpenAI -> Anthropic)
2. Tập trung logic kết nối API ở một nơi
3. Dễ test và mock khi cần
"""

# =============================================================================
# IMPORTS
# =============================================================================
from openai import OpenAI


# =============================================================================
# CLASS DEFINITION
# =============================================================================
class GroqCloudAdapter:
    """
    Adapter để kết nối với Groq Cloud API.
    
    Groq cung cấp API tương thích với OpenAI SDK, nên chúng ta có thể sử dụng
    OpenAI client với base_url của Groq.
    
    Attributes:
        api_key (str | None): API key để xác thực với Groq
        client (OpenAI): OpenAI client được cấu hình để kết nối với Groq
    
    Example:
        >>> adapter = GroqCloudAdapter(api_key="gsk_xxx")
        >>> response = adapter.response(
        ...     model="openai/gpt-oss-20b",
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     temperature=0.7,
        ...     max_output_tokens=1024
        ... )
    """
    
    def __init__(self, api_key: str | None):
        """
        Khởi tạo GroqCloudAdapter với API key.
        
        Args:
            api_key: API key từ Groq (bắt đầu với "gsk_")
                    Có thể None nếu muốn xử lý lỗi sau
        
        Raises:
            ValueError: Nếu api_key là None khi gọi __initialize_client
        """
        self.api_key = api_key
        self.client = self.__initialize_client()

    def __initialize_client(self) -> OpenAI:
        """
        Khởi tạo OpenAI client với cấu hình cho Groq.
        
        Returns:
            OpenAI: Client đã được cấu hình để kết nối với Groq API
        
        Raises:
            ValueError: Nếu api_key là None
        
        Lưu ý:
        - base_url="https://api.groq.com/openai/v1" là endpoint của Groq
        - Groq sử dụng cùng format API với OpenAI nên có thể dùng SDK này
        """
        if self.api_key:
            return OpenAI(
                base_url="https://api.groq.com/openai/v1", 
                api_key=self.api_key
            )
        else:
            raise ValueError("API key is required to initialize the OpenAI client.")

    def response(
        self, 
        model: str, 
        messages: list, 
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ) -> object:
        """
        Gọi API để tạo phản hồi cho tin nhắn.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b", "llama3-8b-8192")
            messages: Danh sách tin nhắn theo format OpenAI
                     [{"role": "user"|"assistant"|"system", "content": "..."}]
            temperature: Độ sáng tạo (0.0 - 1.0)
                        0.0 = xác định nhất, 1.0 = sáng tạo nhất
            max_output_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung (top_p, stream, etc.)
        
        Returns:
            object: Response object từ OpenAI API
                   Thường có structure: response.choices[0].message.content
        
        Example:
            >>> response = adapter.response(
            ...     model="openai/gpt-oss-20b",
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     temperature=0.7,
            ...     max_output_tokens=1024
            ... )
            >>> print(response.choices[0].message.content)
        """
        return self.client.chat.completions.create(
            model=model, 
            messages=messages, 
            temperature=temperature,
            max_tokens=max_output_tokens,
            **kwargs
        )