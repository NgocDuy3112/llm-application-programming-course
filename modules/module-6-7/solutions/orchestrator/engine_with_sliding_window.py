from logger import global_logger
from orchestrator.memory import *
from model.adapter import *


memory = SlidingWindowMemory()


class EngineWithSlidingWindowMemory:
    """
    Chatbot engine orchestrator - quản lý luồng hội thoại và tool execution.

    Engine này kết hợp:
    - Adapter: Để gọi LLM (Groq, Ollama, etc.)
    - Memory: Để quản lý chat history (unlimited, sliding window)

    Attributes:
        adapter (BaseAdapter): LLM adapter instance
        memory (WindowMemory | None): Memory manager instance

    Example:
        >>> engine = EngineWithSlidingWindowMemory(
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

    def __init__(self, adapter: BaseAdapter, memory: SlidingWindowMemory):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter (BaseAdapter | None): LLM adapter instance
                - Nếu có thì dùng cái này thay vì tạo từ provider
            memory (SlidingWindowMemory | None): Memory manager instance
                - Nếu None thì không lưu lịch sử hội thoại
        """
        global_logger.debug(f"Initializing EngineWithSlidingWindowMemory with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__}")
        self.adapter = adapter
        self.memory = memory

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
        # 1. Tạo user message
        user_message = {"role": "user", "content": user_prompt}
        # 2. Lưu trữ user message và truy xuất messages theo sliding window strategy
        self.memory.add(user_message)
        history_messages = self.memory.get_messages()
        # 3. Truyền system prompt + ngữ cảnh ở bước (2)
        messages = [system_message] + history_messages 
        # 4. Gọi API thông qua adapter và nhận phản hồi
        response = self.adapter.response(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        # 5. Lưu trữ assistant response vào memory
        assistant_message = {"role": "assistant", "content": response.choices[0].message.content}
        self.memory.add(assistant_message)
        # 6. Trả về nội dung phản hồi từ assistant
        return assistant_message["content"]
