import os
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()


groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


class GroqAdapter:
    """Adapter để kết nối với Groq Cloud API."""

    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


class OllamaAdapter:
    """Adapter để kết nối với Ollama Local API."""

    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    def response(self, model: str, messages: list, temperature: float, max_tokens: int, **kwargs):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )