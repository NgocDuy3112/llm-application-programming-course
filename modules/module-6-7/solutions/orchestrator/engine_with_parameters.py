from logger import global_logger
from model.adapter import *


class EngineWithParameters:
    """
    Chatbot engine đơn giản với system prompt cố định.

    Engine này chỉ kết hợp adapter để gọi LLM, không có memory management.

    Attributes:
        adapter (BaseAdapter): LLM adapter instance để gọi LLM. System prompt sẽ được truyền trực tiếp trong mỗi call.
    """
    def __init__(self, adapter: BaseAdapter):
        """
        Khởi tạo engine với adapter.

        Args:
            adapter (BaseAdapter): LLM adapter instance để gọi LLM. System prompt sẽ được truyền trực tiếp trong mỗi call.
        """
        global_logger.debug(f"Initializing EngineWithParameters with adapter={adapter.__class__.__name__}")
        self.adapter = adapter

    def response(
        self,
        model: str,
        user_prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 65536,
        **kwargs
    ) -> str:
        global_logger.info(f"Processing user input: {user_prompt[:50]}...")
        system_message = {"role": "system", "content": system_prompt if system_prompt else ""}
        user_message = {"role": "user", "content": user_prompt}
        messages = [system_message, user_message]
        response = self.adapter.call(
            model=model, 
            messages=messages, 
            temperature=temperature, 
            max_tokens=max_tokens, 
            **kwargs
        )
        return response.choices[0].message.content