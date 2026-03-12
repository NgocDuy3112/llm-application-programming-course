from openai import OpenAI

class GroqCloudAdapter:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.client = self.__initialize_client()

    def __initialize_client(self):
        # TODO 1: Khởi tạo OpenAI client với base_url="https://api.groq.com/openai/v1"
        # Gợi ý: return OpenAI(base_url=..., api_key=...)
        pass

    def response(
        self, 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         rride=True)

class ChatbotEngine:
    def __init__(self):
        # TODO 3: Lấy GROQ_API_KEY từ biến môi trường và khởi tạo adapter
        api_key = os.getenv("GROQ_API_KEY")
        self.adapter = GroqCloudAdapter(api_key=api_key)

    def response(
        self,
        model: str, 
        input: str, 
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        # TODO 4: Chuẩn bị danh sách messages (role "user")
        # TODO 5: Gọi self.adapter.response và trả về nội dung (content) của tin nhắn đầu tiên
        pass

class FakeChatbotEngine:
    def response(self, **kwargs):
        return "Đây là phản hồi giả định."
