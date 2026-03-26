# Module 5
# Import class OpenAI từ thư viện openai để kết nối với API tương thích OpenAI
from openai import OpenAI

class GroqCloudAdapter:
    """
    Adapter để kết nối với Groq Cloud API.
    
    Groq cung cấp API tương thích với OpenAI SDK, nên có thể sử dụng
    OpenAI client với base_url của Groq.
    
    Attributes:
        api_key (str | None): API key để xác thực với Groq
        client (OpenAI): OpenAI client được cấu hình cho Groq
    """
    
    def __init__(self, api_key: str | None):
        """
        Khởi tạo GroqCloudAdapter với API key.
        
        Args:
            api_key: API key từ Groq (bắt đầu với "gsk_")
        """
        # Gán api_key truyền vào cho thuộc tính của instance
        self.api_key = api_key
        # Khởi tạo client bằng cách gọi method private __initialize_client
        self.client = self.__initialize_client()

    def __initialize_client(self):
        """
        Khởi tạo OpenAI client với cấu hình cho Groq.
        
        Returns:
            OpenAI: Client đã được cấu hình để kết nối với Groq API
            
        Raises:
            ValueError: Nếu api_key là None
        """
        # TODO 1: Khởi tạo OpenAI client với base_url="https://api.groq.com/openai/v1"
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
        input: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ):
        """
        Gọi API để tạo phản hồi cho tin nhắn.
        
        Args:
            model: Tên model sử dụng (VD: "openai/gpt-oss-20b")
            input: Tin nhắn của người dùng
            temperature: Độ sáng tạo (0.0 - 1.0)
            max_tokens: Số token tối đa trong phản hồi
            **kwargs: Các tham số bổ sung
            
        Returns:
            object: Response object từ OpenAI API
        """
        # TODO 2: Định dạng input thành messages list theo format OpenAI API
        # Gợi ý: messages = [{"role": "user", "content": input}]
        # Tạo list chứa một message với role "user" và content là input
        messages = [{"role": "user", "content": input}]

        # TODO 3: Gọi API thông qua client để tạo phản hồi
        # Gọi API chat completions của OpenAI client
        # Các tham số:
        # - model: tên model sẽ sử dụng
        # - messages: danh sách tin nhắn trong hội thoại
        # - temperature: độ sáng tạo của phản hồi
        # - max_tokens: giới hạn số token trong phản hồi
        # - **kwargs: các tham số khác truyền thẳng vào API
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
