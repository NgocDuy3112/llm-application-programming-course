from openai import OpenAI



class BaseAdapter:
    def __init__(self, provider: str,  api_key: str | None):
        self.provider = provider
        self.api_key = api_key
        self.client = self.__initialize_client()

    def __initialize_client(self):
        match self.provider:
            case 'groq':
                return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key)
            case 'ollama':
                return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            case _:
                raise ValueError(f"Unsupported provider: {self.provider}")

    def response(self, model: str, messages: list, **kwargs):
        return self.client.chat.completions.create(model=model, messages=messages, **kwargs)