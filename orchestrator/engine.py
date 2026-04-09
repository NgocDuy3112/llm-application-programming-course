from model.adapter import groq_client 


class ChatbotEngine:
    def __init__(self):
        self.client = groq_client
    
    def response(self, model: str, user_prompt: str):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.choices[0].message.content