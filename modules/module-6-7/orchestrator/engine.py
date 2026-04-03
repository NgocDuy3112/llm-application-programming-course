import json

from logger import global_logger
from orchestrator.tools import *
from orchestrator.memory import *
from model.adapter import *


class ChatbotEngine:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại và tool execution.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (unlimited, sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (WindowMemory | None): Memory manager instance

    Example:
        >>> engine = EngineFull(
        ...     adapter=GroqAdapter()
        ... )
        >>> response = engine.response(
        ...     model="qwen/qwen3-32b",
        ...     user_prompt="What's the weather today?",
        ...     tools=DEFAULT_TOOLS,
        ...     tool_choice=ToolChoice.AUTO
        ... )
    """

    def __init__(self, adapter: BaseAdapter, memory: SlidingWindowMemory):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter | None): LLM adapter instance
                - Nếu có thì dùng cái này thay vì tạo từ provider
        """
        global_logger.debug(f"Khởi tạo ChatbotEngine với adapter={adapter.__class__.__name__ if adapter else 'None'} và memory={memory.__class__.__name__ if memory else 'None'}")
        self.adapter = adapter
        self.memory = memory

    def response(
        self,
        model: str,
        user_prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_completion_tokens: int | None = None,
        tools: list | None = None,
        tool_choice: ToolChoice = ToolChoice.NONE,
        **kwargs
    ) -> str:
        global_logger.info(f"Xử lý input từ user: {user_prompt[:50]}...")
        system_message = {"role": "system", "content": system_prompt if system_prompt else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        messages = None
        user_message = {"role": "user", "content": user_prompt}
        
        # Tool call log để UI đọc sau (không cần parameter)
        self.tool_call_log = []
        
        # Memory is None when ContextManagementMode.OFF is selected
        if self.memory is not None:
            self.memory.add_message(user_message)
            messages = [system_message] + self.memory.get_messages() if system_prompt else self.memory.get_messages()
        else:
            messages = [system_message, user_message] if system_prompt else [user_message]

        while True:
            tool_choice_value = tool_choice.value if isinstance(tool_choice, ToolChoice) else tool_choice
            response = self.adapter.response(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice_value,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
                **kwargs
            )
            last_message = response.choices[0].message

            # Nếu không có tool calls: lưu assistant response vào memory và trả về
            if not last_message.tool_calls:
                global_logger.debug(f"Không có tool calls, trả về response từ assistant")
                assistant_message = {"role": "assistant", "content": last_message.content}
                if self.memory is not None:
                    self.memory.add_message(assistant_message)
                return last_message.content

            # Có tool calls:
            global_logger.debug(f"Phát hiện tool calls: {[tc.function.name for tc in last_message.tool_calls]}")
            
            # Nối assistant response vào messages (không lưu vào memory vì chưa chắc đã là final response)
            messages.append({
                "role": "assistant",
                "content": last_message.content,
                "tool_calls": last_message.tool_calls
            })

            # Thực thi tools và append tool responses vào messages (KHÔNG lưu vào memory)
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Thực thi tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments) or {}
                except:
                    tool_args = {}

                if tool_name in AVAILABLE_FUNCTIONS:
                    try:
                        global_logger.debug(f"Gọi {tool_name} với args: {tool_args}")
                        tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        global_logger.error(f"Lỗi khi thực thi {tool_name}: {str(e)}")
                        tool_response = f"Error executing {tool_name}: {str(e)}"
                else:
                    global_logger.warning(f"Tool không xác định: {tool_name}")
                    tool_response = f"Unknown tool: {tool_name}"

                # Append tool response vào messages (không lưu vào memory)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_response)
                })

            # Continue loop - messages đã có tool responses, không rebuild từ memory