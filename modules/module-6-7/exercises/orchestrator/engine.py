"""
Module 6-7 - Chatbot Engine

Mô tả: FullChatbotEngine - orchestration layer quản lý luồng hội thoại,
bao gồm:
- Quản lý context/memory
- Gọi LLM thông qua adapter
- Xử lý tool calls (function calling)
- Tách biệt reasoning content (thinking) và response text

Kiến trúc / Dependencies:
    - BaseAdapter: Interface để gọi LLM
    - WindowMemory: Class để quản lý chat history (sliding window)
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
from typing import Optional


class FullChatbotEngine:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại và tool execution.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (unlimited, sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (WindowMemory | None): Memory manager instance

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

    def __init__(self, adapter: BaseAdapter | None = None, memory: Optional["WindowMemory"] = None):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter | None): LLM adapter instance
                - Nếu có thì dùng cái này thay vì tạo từ provider
            memory (WindowMemory | None): Memory manager instance
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
        # System prompt: ensure `instruction` is converted into a system message
        # HƯỚNG DẪN: Xử lý input từ người dùng
        # 1. Khởi tạo system message từ instruction
        # 2. Kiểm tra chế độ tool_choice để quyết định có gửi tools lên API hay không
        global_logger.info(f"Processing user input: {input[:50]}...")
        # GỢI Ý (mức cao): Khi xử lý input, bạn có thể thực hiện các bước sau:
        # - Tạo `system_message` từ `instruction` nếu có.
        # - Nếu `tool_choice == ToolChoice.NONE` thì không gửi `tools` trong cuộc gọi tới provider.
        # - Lấy `streaming_output = kwargs.pop("streaming_output", False)` nếu cần xử lý streaming.
        # - Tạo `llm_input` (có thể tiền xử lý/preprocess input trước khi gửi đến LLM).
        # - Nếu bạn muốn lưu user message vào memory, gọi `self.memory.add(role="user", content=input)`.
        #
        # LƯU Ý: Giữ contract của `memory.add` là một dict với keys `role` và `content`;
        # assistant messages có thể chứa thêm `tool_calls` để engine biết model đã yêu cầu function calling.


        # Main tool-calling loop: keep executing until no more tool calls
        while True:
            # GỢI Ý (mức cao) — các bước chính trong vòng lặp:
            # Function-calling loop guidance (see exercises/EXERCISE_TODOs.md for flow):
            # 1) Build `messages` để gửi cho LLM: [system_message] + sanitized memory messages.
            #    - Khi sanitize, chỉ giữ `role` và `content` cho hầu hết messages.
            #    - Nếu `role == "tool"`, giữ thêm `tool_call_id` và `name` để link với tool output.
            # 2) Nếu bạn tiền xử lý (preprocess) user input, đảm bảo last user message content = llm_input.
            # 3) Gọi `self.adapter.response(...)` với các tham số phù hợp và kiểm tra `response.choices`.
            # 4) Lấy `last_message = response.choices[0].message` một cách an toàn.
            # 5) Nếu `last_message` không có `tool_calls`: lưu assistant message vào memory (nếu cần)
            #    và trả về `last_message.content` (loại bỏ `reasoning_content` khi hiển thị).
            # 6) Nếu có `tool_calls`: lưu assistant message kèm `tool_calls` vào memory, duyệt từng
            #    `tool_call`, parse arguments một cách robust (nếu là string thì json.loads, nếu dict dùng trực tiếp),
            #    gọi `AVAILABLE_FUNCTIONS[tool_name](**tool_args)` và lưu kết quả bằng `add_tool_message`.
            # 7) Lặp lại vòng vì LLM sẽ thấy kết quả tool trong memory và có thể trả lời tiếp.
            #
            # LƯU Ý: luôn log tại mỗi bước và xử lý exception để tránh loop vô hạn hoặc crash.
            break

