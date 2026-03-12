from core.model.adapter import GroqCloudAdapter


class ChatbotEngine:
    def __init__(self, api_key: str | None):
        self.adapter = GroqCloudAdapter(api_key=api_key)

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