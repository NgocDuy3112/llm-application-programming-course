import os
from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv
import enum

from logger import global_logger
from custom_types import ToolChoice


class BaseAdapter(ABC):
    def __init__(self):
        self.client = self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        pass

    def response(self, model, messages, tools, tool_choice, temperature, max_tokens, **kwargs):
        global_logger.debug(f"Calling API with model {model}")
        if isinstance(tool_choice, enum.Enum):
            tool_choice_value = tool_choice.value
        else:
            tool_choice_value = getattr(tool_choice, "value", tool_choice)

        params = dict(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice_value,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return self.client.chat.completions.create(**params)


class GroqAdapter(BaseAdapter):
    def _initialize_client(self):
        load_dotenv(dotenv_path=".env", override=True)
        api_key = os.getenv("GROQ_API_KEY")
        global_logger.debug("Initializing Groq client")
        if not api_key:
            global_logger.error("GROQ_API_KEY not found in environment")
            raise ValueError("GROQ_API_KEY environment variable not set")
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )


class OllamaAdapter(BaseAdapter):
    def _initialize_client(self):
        global_logger.debug("Initializing Ollama client at http://localhost:11434/v1/")
        return OpenAI(
            base_url="http://localhost:11434/v1/",
            api_key="ollama"
        )
