from openai import OpenAI



class GroqCloudAdapter:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.client = self.__initialize_client()

    def __initialize_client(self):
        if self.api_key:
            return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key)
        else:
            raise ValueError("API key is required to initialize the OpenAI client.")

    def response(self, model_name: str, messages: list, **kwargs):
        return self.client.chat.completions.create(model=model_name, messages=messages, **kwargs)