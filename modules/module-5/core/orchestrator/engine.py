from core.model.adapter import GroqCloudAdapter


class ChatbotEngine:
    def __init__(self, api_key: str | None):
        self.adapter = GroqCloudAdapter(api_key=api_key)

    def response(self, model: str, input: str, **kwargs):
        user_message = [{"role": "user", "content": input}]
        response = self.adapter.response(model=model, messages=user_message, **kwargs)
        return response.choices[0].message.content


class FakeChatbotEngine:
    def response(self, input: str, **kwargs):
        return "Đây là phản hồi giả cho tin nhắn: " + input