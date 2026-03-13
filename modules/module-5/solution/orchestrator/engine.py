# Module 5
import os
from dotenv import load_dotenv
from model.adapter import GroqCloudAdapter


load_dotenv(dotenv_path=".env", override=True)


class ChatbotEngine:
    def __init__(self):
        self.adapter = GroqCloudAdapter(api_key=os.getenv("GROQ_API_KEY"))

    def response(
        self,
        model: str, 
        input: str, 
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        user_message = [{"role": "user", "content": input}]
        response = self.adapter.response(
            model=model, 
            messages=user_message, 
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs
        )
        return response.choices[0].message.content


class FakeChatbotEngine:
    def response(
        self, 
        model: str, 
        input: str,
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        return f"Đây là phản hồi giả cho tin nhắn: '{input}' (model: {model}, temperature: {temperature}, max_output_tokens: {max_output_tokens}), các tham số khác: {kwargs})"