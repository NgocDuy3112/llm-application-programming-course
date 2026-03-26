# Import json module để parse tool call arguments
import json

# Import global_logger từ logger module để ghi log
from logger import global_logger
# Import tất cả các classes từ memory module (WindowMemory, BaseMemory, etc.)
from orchestrator.memory import *
# Import tất cả các functions/constants từ tools module (AVAILABLE_FUNCTIONS, DEFAULT_TOOLS, etc.)
from orchestrator.tools import *
# Import tất cả các classes từ adapter module (BaseAdapter, GroqAdapter, OllamaAdapter)
from model.adapter import *
# Import ToolChoice enum từ custom_types để điều khiển tool usage
from custom_types import ToolChoice


# Định nghĩa FullChatbotEngine class - engine chính xử lý chat logic
class FullChatbotEngine:
    """
    Chatbot engine chính - điều phối toàn bộ quá trình xử lý chat.
    
    Responsibilities:
    - Quản lý adapter (LLM provider)
    - Quản lý memory (lịch sử chat)
    - Xử lý tool calls
    - Generate responses
    """
    
    # Constructor của FullChatbotEngine class
    def __init__(self, adapter: BaseAdapter | None = None, memory: BaseMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.

        Args:
            adapter: BaseAdapter instance - nếu có thì dùng cái này thay vì tạo từ provider
            memory: BaseMemory instance - nếu None thì tạo mặc định
        """
        # Ghi log debug: khởi tạo engine với adapter và memory
        global_logger.debug("Initializing FullChatbotEngine with adapter={}, memory={}".format(adapter.__class__.__name__, memory.__class__.__name__))
        
        # Lưu adapter vào instance variable
        self.adapter = adapter
        
        # Lưu memory vào instance variable
        self.memory = memory

    # Method chính để tạo phản hồi chat
    def response(
        self,
        model: str,           # Tên model/ID để sử dụng
        input: str,           # Input của người dùng
        tools: list | None = None,  # Danh sách tools (nếu có)
        tool_choice: ToolChoice = ToolChoice.NONE,  # Chế độ sử dụng tools
        instruction: str | None = None,  # System instruction
        temperature: float = 0.2,  # Độ sáng tạo (0.0 - 1.0)
        max_tokens: int = 65536,  # Số tokens tối đa cho phản hồi
        **kwargs  # Các arguments bổ sung
    ) -> str:
        """
        Tạo phản hồi chat từ LLM.

        Args:
            model: Model name/ID
            input: Input của người dùng
            tools: Danh sách tools (nếu None thì không dùng tools)
            tool_choice: Chế độ sử dụng tools (NONE, AUTO, etc.)
            instruction: System instruction
            temperature: Độ sáng tạo (0.0 = deterministic, 1.0 = creative)
            max_tokens: Số tokens tối đa cho phản hồi

        Returns:
            str: Phản hồi từ LLM
        """
        # Ghi log info: bắt đầu xử lý input (50 ký tự đầu tiên)
        global_logger.info("Processing user input: {}...".format(input[:50]))
        
        # Tạo system message dictionary
        # Nếu có instruction thì dùng, ngược lại để content rỗng
        system_message = {"role": "system", "content": instruction if instruction else ""}
        
        # Nếu tool_choice là NONE thì không dùng tools (set tools = None)
        tools = tools if tool_choice != ToolChoice.NONE else None
        
        # Lấy flag streaming_output từ kwargs (dành cho streaming-style responses)
        # pop() trả về giá trị và xóa key khỏi kwargs
        streaming_output = kwargs.pop("streaming_output", False)
        
        # Ghi log debug: streaming_output flag
        global_logger.debug("streaming_output={}".format(streaming_output))

        # Lưu original input cho auditing/memory
        original_input = input
        
        # llm_input là version sẽ được gửi cho LLM (có thể là masked version)
        llm_input = input

        # Thêm user message vào memory (một lần, trước khi vào tool-calling loop)
        # Lưu original input cho auditing
        if self.memory is not None:
            self.memory.add(role="user", content=original_input)

        # ================================================================
        # TOOL-CALLING LOOP
        # ================================================================
        # Loop để xử lý tool calls (LLM có thể yêu cầu gọi nhiều tools)
        while True:
            # ================================================================
            # PREPARE MESSAGES
            # ================================================================
            
            # Nếu có memory, lấy messages từ memory
            if self.memory is not None:
                # Lấy raw messages từ memory
                raw_messages = self.memory.get_messages()
                
                # Simplified sanitization: repo invariant là raw_messages đều là dict
                # Chỉ giữ các trường cần thiết (role, content) và optional tool fields
                def _sanitize_dict(message: dict) -> dict:
                    # Lấy role (None nếu không có)
                    role = message.get("role")
                    # Lấy content (mặc định là chuỗi rỗng)
                    content = message.get("content", "")
                    # Tạo dict cơ bản chỉ giữ role và content
                    msg = {"role": role, "content": content}
                    # Nếu là tool message thì thêm các trường tùy chọn nếu tồn tại
                    if role == "tool":
                        tool_call_id = message.get("tool_call_id")
                        if tool_call_id is not None:
                            msg["tool_call_id"] = tool_call_id
                        name = message.get("name")
                        if name is not None:
                            msg["name"] = name
                    return msg

                sanitized = [_sanitize_dict(message) for message in raw_messages]
                
                # Tạo messages list với system message đầu tiên + sanitized messages
                messages = [system_message] + sanitized
                
                # Replace nội dung của user message cuối cùng với llm_input (masked version)
                if messages and messages[-1].get("role") == "user":
                    messages[-1] = {"role": "user", "content": llm_input}
            # Nếu không có memory
            else:
                # Tạo user message
                user_message = {"role": "user", "content": llm_input}
                # Messages list chỉ có system + user message
                messages = [system_message, user_message]
            
            # ================================================================
            # CALL LLM
            # ================================================================
            
            # Gọi adapter.response() để gọi LLM API
            response = self.adapter.response(
                model=model,            # Model name
                messages=messages,      # Messages list
                tools=tools,            # Tools (nếu có)
                tool_choice=tool_choice, # Tool choice mode
                temperature=temperature, # Temperature
                max_tokens=max_tokens,   # Max tokens
                **kwargs                # Additional arguments
            )
            
            # Lấy message đầu tiên từ response choices
            last_message = response.choices[0].message

            # ================================================================
            # CHECK FOR TOOL CALLS
            # ================================================================
            
            # Kiểm tra nếu không có tool calls trong response
            if not last_message.tool_calls:
                # Ghi log debug: không có tool calls
                global_logger.debug("No tool calls, returning assistant response")
                
                # Nếu có memory, thêm assistant response vào memory
                if self.memory is not None:
                    self.memory.add(role="assistant", content=last_message.content)
                
                # Lấy thinking content từ reasoning models (DeepSeek-R1, QwQ, o3...)
                # Tham chiếu: message.reasoning_content trong response object
                thinking = getattr(last_message, "reasoning_content", None) or ""
                
                # Lấy text content từ response
                text = last_message.content or ""
                
                # Ghi log debug: độ dài thinking và text
                global_logger.debug("Response complete - thinking: {} chars, text: {} chars".format(len(thinking), len(text)))
                
                # Trả về text content (không include thinking)
                return text

            # Nếu có tool calls, ghi log debug
            global_logger.debug("Tool calls detected: {}".format([tc.function.name for tc in last_message.tool_calls]))
            
            # Nếu có memory, thêm assistant message với tool calls vào memory
            if self.memory is not None:
                self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)

            # ================================================================
            # EXECUTE TOOLS
            # ================================================================
            
            # Lặp qua từng tool call trong response
            for tool_call in last_message.tool_calls:
                # Lấy tên tool từ function.name
                tool_name = tool_call.function.name
                
                # Ghi log debug: tên tool được thực thi
                global_logger.debug("Executing tool: {}".format(tool_name))
                
                # Try-except để parse arguments
                try:
                    # Parse arguments từ JSON string sang dictionary
                    tool_args = json.loads(tool_call.function.arguments) or {}
                except:
                    # Nếu parse failed, dùng empty dict
                    tool_args = {}

                # Kiểm tra nếu tool_name có trong AVAILABLE_FUNCTIONS
                if tool_name in AVAILABLE_FUNCTIONS:
                    try:
                        # Ghi log debug: gọi tool với arguments
                        global_logger.debug("Calling {} with args: {}".format(tool_name, tool_args))
                        
                        # Gọi tool function với unpacked arguments
                        tool_response = AVAILABLE_FUNCTIONS[tool_name](**tool_args)
                    # Xử lý exception nếu tool execution failed
                    except Exception as e:
                        # Ghi log error
                        global_logger.error("Error executing {}: {}".format(tool_name, str(e)))
                        # Set tool_response là error message
                        tool_response = "Error executing {}: {}".format(tool_name, str(e))
                # Nếu tool_name không có trong AVAILABLE_FUNCTIONS
                else:
                    # Ghi log warning: unknown tool
                    global_logger.warning("Unknown tool: {}".format(tool_name))
                    # Set tool_response là error message
                    tool_response = "Unknown tool: {}".format(tool_name)
                
                # Nếu có memory, thêm tool response vào memory
                if self.memory is not None:
                    self.memory.add_tool_message(tool_call, tool_response)
            
            # Loop tiếp tục để gọi LLM lại với tool responses
