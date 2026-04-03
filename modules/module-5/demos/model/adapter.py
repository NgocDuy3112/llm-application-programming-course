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
# IMPORTS - KHAI BÁO THƯ VIỆN
# =============================================================================
from openai import OpenAI  # Import OpenAI client từ thư viện openai


# =============================================================================
# CLASS DEFINITION - ĐỊNH NGHĨA LỚP
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
        ...     max_tokens=1024
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
        # Gán api_key truyền vào cho thuộc tính của instance
        self.api_key = api_key
        # Khởi tạo client bằng cách gọi method private __initialize_client
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
        # Kiểm tra nếu api_key có giá trị (không None, không rỗng)
        if self.api_key:
            # Tạo và trả về OpenAI client với cấu hình cho Groq
            # base_url: endpoint của Groq API (tương thích OpenAI)
            # api_key: key xác thực để gọi API
            return OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
        else:
            # Ném lỗi nếu không có API key
            raise ValueError("API key is required to initialize the OpenAI client.")

    def response(
        self,
        model: str,
        messages: list,
        **kwargs
    ) -> object:
        """
        Gọi API để tạo phản hồi cho tin nhắn.

        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b", "llama3-8b-8192")
            messages: Danh sách tin nhắn theo format OpenAI
                    [{"role": "user"|"assistant"|"system", "content": "..."}]
            **kwargs: Các tham số bổ sung (temperature, max_tokens, top_p, stream, etc.)

        Returns:
            object: Response object từ OpenAI API
                Thường có structure: response.choices[0].message.content

        Example:
            >>> response = adapter.response(
            ...     model="openai/gpt-oss-20b",
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     temperature=0.7,
            ...     max_tokens=1024
            ... )
            >>> print(response.choices[0].message.content)
        """
        # Gọi API chat completions của OpenAI client
        # Đây là method chính để tạo phản hồi từ model
        # Các tham số:
        # - model: tên model sẽ sử dụng
        # - messages: danh sách tin nhắn trong hội thoại
        # - temperature: độ sáng tạo của phản hồi
        # - max_tokens: giới hạn số token trong phản hồi
        # - **kwargs: các tham số khác truyền thẳng vào API
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
