"""
Module 6-7 - Chatbot Engine (Solution)

Mô tả: FullChatbotEngine - orchestration layer quản lý luồng hội thoại,
bao gồm:
- Quản lý context/memory
- Gọi LLM thông qua adapter
- Xử lý tool calls (function calling)
- Tách biệt reasoning content (thinking) và response text

Kiến trúc / Dependencies:
- BaseAdapter: Interface để gọi LLM
- BaseMemory: Interface để quản lý chat history
- ToolChoice: Enum cho tool usage mode
- AVAILABLE_FUNCTIONS: Registry của các tools có sẵn

Flow:
1. Nhận user input
2. Thêm vào memory
3. Loop:
   a. Lấy messages từ memory
   b. Gọi LLM qua adapter
   c. Nếu có tool_calls: thực thi tools, thêm kết quả vào memory, lặp lại
   d. Nếu không: trả về response

Usage:
    engine = FullChatbotEngine(adapter=GroqAdapter(), memory=WindowMemory(...))
    response = engine.response(model="...", input="Hello", ...)
"""

import json

from logger import global_logger
from orchestrator.memory import *
from orchestrator.tools import *
from model.adapter import *


class FullChatbotEngine:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại và tool execution.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (unlimited, sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (BaseMemory | None): Memory manager instance

    Example:
        >>> engine = FullChatbotEngine(
        ...     adapter=GroqAdapter(),
        ...     memory=WindowMemory(sliding_window_size=5)
        ... )
        >>> response = engine.response(
        ...     model="qwen/qwen3-32b",
        ...     input="What's the weather today?",
        ...     tools=DEFAULT_TOOLS,
        ...     tool_choice=ToolChoice.AUTO
        ... )
    """

    def __init__(self, adapter: BaseAdapter | None = None, memory: BaseMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter | None): LLM adapter instance
                - Nếu có thì dùng cái này thay vì tạo từ provider
            memory (BaseMemory | None): Memory manager instance
                - Nếu None thì không lưu lịch sử hội thoại
        """
        global_logger.debug(f"Initializing FullChatbotEngine with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__ if memory else 'None'}")
        self.adapter = adapter
        self.memory = memory

    def response(
        self,
        model: str,
        input: str,
        tools: list | None = None,
        tool_choice: ToolChoice = ToolChoice.NONE,
        instruction: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 65536,
        **kwargs
    ) -> str:
        """
        Gọi LLM và trả về response text.

        Với các reasoning model (DeepSeek-R1, QwQ, o3...), phần thinking
        được lấy từ message.reasoning_content trong response object.
        Với các model thông thường, thinking sẽ là chuỗi rỗng.

        Args:
            model (str): Model name/ID to use
            input (str): User's input message
            tools (list | None): Tool definitions for function calling
            tool_choice (ToolChoice): Tool usage mode (NONE or AUTO)
            instruction (str | None): System instruction/prompt
            temperature (float): Creativity level (0.0-1.0)
            max_tokens (int): Maximum tokens in response
            **kwargs: Additional params passed to adapter

        Returns:
            str: The assistant's reply text (without reasoning blocks)

        Note:
            - Tool calls được xử lý trong loop cho đến khi không còn tool calls
            - Memory được cập nhật sau mỗi step (user, assistant, tool messages)
            - Reasoning content (<think>...</think>) được tách riêng, không hiển thị
        """
        global_logger.info(f"Processing user input: {input[:50]}...")
        system_message = {"role": "system", "content": instruction if instruction else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        streaming_output = kwargs.pop("streaming_output", False)
        global_logger.debug(f"streaming_output={streaming_output}")

        llm_input = input

        if self.memory is not None:
            self.memory.add(role="user", content=input)

        while True:
            if self.memory is not None:
                raw_messages = self.memory.get_messages()

                def _sanitize_dict(message: dict) -> dict:
                    role = message.get("role")
                    content = message.get("content") or ""
                    msg = {"role": role, "content": content}
                    if role == "tool":
                        msg["tool_call_id"] = message["tool_call_id"]
                        msg["name"] = message["name"]
                    return msg

                sanitized = [_sanitize_dict(message) for message in raw_messages]
                messages = [system_message] + sanitized
                if messages and messages[-1].get("role") == "user":
                    messages[-1] = {"role": "user", "content": llm_input}
            else:
                user_message = {"role": "user", "content": llm_input}
                messages = [system_message, user_message]

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

            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                if self.memory is not None:
                    self.memory.add(role="assistant", content=last_message.content)
                thinking = getattr(last_message, "reasoning_content", None) or ""
                text = last_message.content or ""
                global_logger.debug(f"Response complete - thinking: {len(thinking)} chars, text: {len(text)} chars")
                return text

            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")
            if self.memory is not None:
                self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Executing tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments) or {}
                except:
                    tool_args = {}

                if tool_name in AVAILABLE_FUNCTIONS:
                    try:
                        global_logger.debug(f"Calling {tool_name} with args: {tool_args}")
                        tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        global_logger.error(f"Error executing {tool_name}: {str(e)}")
                        tool_response = f"Error executing {tool_name}: {str(e)}"
                else:
                    global_logger.warning(f"Unknown tool: {tool_name}")
                    tool_response = f"Unknown tool: {tool_name}"

                if self.memory is not None:
                    self.memory.add_tool_message(tool_call, tool_response)
