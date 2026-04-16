# Khai báo module docstring - mô tả chức năng của module adapter
"""
Module 6-7 - Model Adapter

Mô tả: Triển khai các adapter khác nhau để kết nối với các LLM providers
(Groq, Ollama) thông qua OpenAI-compatible API wrapper.

Kiến trúc / Dependencies:
- BaseAdapter: Abstract base class định nghĩa interface chung
- GroqAdapter: Triển khai cho Groq API
- OllamaAdapter: Triển khai cho Ollama local server
- Được dùng bởi FullChatbotEngine để gọi LLM
"""

# Import os module để đọc environment variables
import os
# Import ABC (Abstract Base Class) và abstractmethod từ abc module
# Dùng để định nghĩa abstract class (class không thể khởi tạo trực tiếp)
from abc import ABC, abstractmethod
# Import OpenAI client từ openai package
from openai import OpenAI
# Import load_dotenv từ dotenv package để load environment variables từ file .env
from dotenv import load_dotenv
# Import enum module (được sử dụng nhưng không trực tiếp trong code này)
import enum

# Import global_logger từ logger module để ghi log hoạt động
from logger import global_logger
# Import ToolChoice enum từ custom_types module
from custom_types import ToolChoice


# Định nghĩa BaseAdapter class kế thừa từ ABC (Abstract Base Class)
class BaseAdapter(ABC):
    """
    Abstract base class cho LLM adapters.

    Các subclass phải implement:
    - _initialize_client(): Khởi tạo OpenAI client với đúng base_url và api_key
    """
    
    # Constructor của BaseAdapter class
    def __init__(self):
        """
        Khởi tạo adapter và initialize client.
        
        Workflow:
            1. Gọi _initialize_client() để tạo client
            2. Lưu client vào instance variable
        """
        # Gọi method _initialize_client() và lưu kết quả vào self.client
        # Client này sẽ được dùng để gọi API trong method response()
        self.client = self._initialize_client()

    # Abstract method - các subclass phải implement method này
    @abstractmethod
    def _initialize_client(self):
        """
        Khởi tạo và trả về OpenAI client.
        
        Returns:
            OpenAI: OpenAI client instance đã được cấu hình
        """
        # Pass - implementation sẽ được định nghĩa trong subclass
        pass

    # Method để gọi LLM API
    def response(
        self,
        model: str,           # Tên model/ID để sử dụng
        messages: list,       # List of message dicts (role, content)
        tools: list,          # Tool definitions (nếu None thì không dùng tool)
        tool_choice: ToolChoice,  # Tool usage mode (NONE, AUTO, etc.)
        temperature: float,   # Độ sáng tạo (0.0 - 1.0)
        max_tokens: int,      # Số tokens tối đa cho phản hồi
        **kwargs              # Các arguments bổ sung
    ):
        """
        Gọi LLM với messages và config.

        Args:
            model: Model name/ID
            messages: List of message dicts
            tools: Tool definitions (nếu None thì không dùng tool)
            tool_choice: Tool usage mode (ToolChoice)
            temperature: Creativity level
            max_tokens: Max tokens in response

        Returns:
            Response object từ OpenAI API
        """
        # Ghi log debug: đang gọi API với model name
        global_logger.debug(f"Calling API with model {model}")
        
        # Ensure tool_choice là JSON-serializable
        # Convert Enum object thành value của nó (string)
        if isinstance(tool_choice, enum.Enum):
            # Nếu là Enum, lấy .value
            tool_choice_value = tool_choice.value
        else:
            # Fallback: nếu object có .value attribute thì lấy nó, ngược lại dùng as-is
            tool_choice_value = getattr(tool_choice, "value", tool_choice)

        # Tạo parameters dictionary để truyền vào API call
        # dict() constructor với keyword arguments
        params = dict(
            model=model,              # Model name
            messages=messages,        # Conversation history
            tools=tools,              # Function definitions
            tool_choice=tool_choice_value,  # Tool choice mode (đã convert)
            temperature=temperature,  # Temperature setting
            max_tokens=max_tokens,    # Max tokens limit
            **kwargs                  # Additional arguments
        )
        
        # Gọi OpenAI API và trả về response
        # client.chat.completions.create() là method chính để gọi chat completion
        return self.client.chat.completions.create(**params)


# Định nghĩa GroqAdapter class kế thừa từ BaseAdapter
class GroqAdapter(BaseAdapter):
    """
    Adapter cho Groq API (OpenAI-compatible).

    Requires: GROQ_API_KEY environment variable
    
    Groq cung cấp API tương thích với OpenAI format,
    nên có thể dùng OpenAI client với base_url của Groq.
    """
    
    # Implement abstract method _initialize_client() từ BaseAdapter
    def _initialize_client(self):
        """
        Khởi tạo và trả về Groq OpenAI client.

        Returns:
            OpenAI: OpenAI client đã cấu hình cho Groq API
        """
        # Load environment variables từ file .env
        # override=True nghĩa là ghi đè lên các biến đã tồn tại
        load_dotenv(dotenv_path=".env", override=True)
        
        # Lấy GROQ_API_KEY từ environment variables
        api_key = os.getenv("GROQ_API_KEY")
        
        # Ghi log debug: đang khởi tạo Groq client
        global_logger.debug("Initializing Groq client")
        
        # Kiểm tra nếu không tìm thấy API key
        if not api_key:
            # Ghi log error: API key không tồn tại
            global_logger.error("GROQ_API_KEY not found in environment")
            # Raise ValueError để thông báo lỗi
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Khởi tạo và trả về OpenAI client với Groq configuration
        return OpenAI(
            # Base URL của Groq API (OpenAI-compatible endpoint)
            base_url="https://api.groq.com/openai/v1",
            # API key lấy từ environment
            api_key=api_key
        )


# Định nghĩa OllamaAdapter class kế thừa từ BaseAdapter
class OllamaAdapter(BaseAdapter):
    """
    Adapter cho Ollama local server (OpenAI-compatible).

    Assumes Ollama runs at http://localhost:11434/v1/
    
    Ollama là công cụ chạy LLM locally, cung cấp API
    tương thích với OpenAI format.
    """
    
    # Implement abstract method _initialize_client() từ BaseAdapter
    def _initialize_client(self):
        """
        Khởi tạo và trả về Ollama OpenAI client.

        Returns:
            OpenAI: OpenAI client đã cấu hình cho Ollama local server
        """
        # Ghi log debug: đang khởi tạo Ollama client với local URL
        global_logger.debug("Initializing Ollama client at http://localhost:11434/v1/")
        
        # Khởi tạo và trả về OpenAI client với Ollama configuration
        return OpenAI(
            # Base URL của Ollama local server
            base_url="http://localhost:11434/v1/",
            # Ollama không yêu cầu API key thật, dùng placeholder "ollama"
            api_key="ollama"  # Ollama doesn't require real API key
        )
