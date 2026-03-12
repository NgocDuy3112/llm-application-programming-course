import os
from openai import OpenAI
from logger import global_logger
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)



class BaseAdapter:
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self.__initialize_client()

    def __initialize_client(self):
        match self.provider:
            case 'groq':
                global_logger.debug(f"Initializing Groq client")
                return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
            case 'ollama':
                global_logger.debug(f"Initializing Ollama client at http://localhost:11434/v1/")
                return OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")
            case _:
                global_logger.error(f"Unsupported provider: {self.provider}")
                raise ValueError(f"Không hỗ trợ nhà cung cấp {self.provider}")

    def response(
        self, 
        model: str, 
        messages: list, 
        tools: list,
        temperature: float,
        max_output_tokens: int,
        **kwargs
    ):
        global_logger.debug(f"Calling {self.provider} API with model {model}")
        return self.client.chat.completions.create(
            model=model, 
            messages=messages, 
            tools=tools,
            temperature=temperature,
            max_tokens=max_output_tokens,
            **kwargs
        )