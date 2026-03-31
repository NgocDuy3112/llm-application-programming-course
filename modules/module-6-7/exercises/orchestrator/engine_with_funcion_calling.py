import json

from logger import global_logger
from orchestrator.tools import *
from model.adapter import *


class EngineWithFunctionCalling:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại và tool execution.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (unlimited, sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (WindowMemory | None): Memory manager instance

    Example:
        >>> engine = EngineWithFunctionCalling(
        ...     adapter=GroqAdapter()
        ... )
        >>> response = engine.response(
        ...     model="qwen/qwen3-32b",
        ...     user_prompt="What's the weather today?",
        ...     tools=DEFAULT_TOOLS,
        ...     tool_choice=ToolChoice.AUTO
        ... )
    """

    def __init__(self, adapter: BaseAdapter | None = None):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter | None): LLM adapter instance
                - Nếu có thì dùng cái này thay vì tạo từ provider
            memory (WindowMemory | None): Memory manager instance
                - Nếu None thì không lưu lịch sử hội thoại
        """
        global_logger.debug(f"Initializing EngineWithSlidingWindowMemory with adapter={adapter.__class__.__name__}")
        self.adapter = adapter

    def response(
        self,
        model: str,
        user_prompt: str,
        system_prompt: str | None = None,
        tools: list | None = None,
        tool_choice: ToolChoice = ToolChoice.NONE,
        temperature: float = 0.2,
        max_tokens: int = 65536,
        **kwargs
    ) -> str:
        global_logger.info(f"Processing user input: {user_prompt[:50]}...")
        system_message = {"role": "system", "content": system_prompt if system_prompt else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        messages = None
        user_message = {"role": "user", "content": user_prompt}
        if system_prompt:
            messages = [system_message, user_message]
        else:
            messages = [user_message]

        while True:
            # Gọi LLM
            response = self.adapter.response(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            last_message = response.choices[0].message

            # Nếu không có tool calls: lưu assistant response vào memory và trả về
            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                text = last_message.content
                return text

            # Có tool calls:
            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")

            # Append assistant message với tool calls vào messages list
            messages.append({
                "role": "assistant",
                "content": last_message.content,
                "tool_calls": last_message.tool_calls
            })

            # Thực thi tools và append tool responses vào messages (KHÔNG lưu vào memory)
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                global_logger.debug(f"Calling {tool_name} with args: {tool_args}")
                tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)

                # Append tool response vào messages (không lưu vào memory)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_response)
                })

            # Continue loop - messages đã có tool responses, không rebuild từ memory
