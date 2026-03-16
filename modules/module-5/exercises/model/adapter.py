# Module 5
from openai import OpenAI

class GroqCloudAdapter:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.client = self.__initialize_client()

    def __initialize_client(self):
        # TODO 1: Khởi tạo OpenAI client với base_url="https://api.groq.com/openai/v1"
        pass

    def response(
        self, 
        model: str, 
        input: str, 
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        # TODO 2: Định dạng input thành messages list theo format OpenAI API
        # Gợi ý: messages = [{"role": "user", "content": input}]
        
        # TODO 3: Gọi API thông qua client để tạo phản hồi
        pass