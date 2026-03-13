import json
from logger import global_logger
from orchestrator.memory import WindowMemory
from orchestrator.tools import *
from model.adapter import BaseAdapter, GroqAdapter, OllamaAdapter




class FullChatbotEngine:
    def __init__(self, provider: str | None = None, adapter: BaseAdapter | None = None, memory: WindowMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.
        
        Args:
            provider: Provider name ('groq', 'ollama') - dùng để tạo adapter tự động
            adapter: BaseAdapter instance - nếu có thì dùng cái này thay vì tạo từ provider
            memory: WindowMemory instance - nếu None thì tạo mặc định
        """
        # Create adapter from provider if not provided
        if adapter is None:
            if provider is None:
                raise ValueError("Must provide either provider or adapter")
            adapter = self._create_adapter(provider)
        
        # Create default memory if not provided
        if memory is None:
            memory = WindowMemory()
        
        global_logger.debug(f"Initializing FullChatbotEngine with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__}")
        self.memory = memory
        self.adapter = adapter
    
    @staticmethod
    def _create_adapter(provider: str) -> BaseAdapter:
        """Tạo adapter phù hợp dựa trên provider name"""
        match provider:
            case 'groq':
                global_logger.debug("Creating GroqAdapter")
                return GroqAdapter(provider='groq')
            case 'ollama':
                global_logger.debug("Creating OllamaAdapter")
                return OllamaAdapter(provider='ollama')
            case _:
                global_logger.error(f"Unsupported provider: {provider}")
                raise ValueError(f"Không hỗ trợ nhà cung cấp {provider}")

    def response(
        self, 
        model: str, 
        input: str, 
        tools: list | None = DEFAULT_TOOLS,
        instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 65536,
        **kwargs
    ):
        global_logger.info(f"Processing user input: {input[:50]}...")
        system_message = {"role": "system", "content": instruction if instruction else "You are a helpful assistant."}
        self.memory.add(role="user", content=input)
        
        while True:
            messages = [system_message] + self.memory.get_messages()
            response = self.adapter.response(
                model=model, 
                messages=messages, 
                tools=tools, 
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            last_message = response.choices[0].message
            
            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                self.memory.add(role="assistant", content=last_message.content)
                return last_message.content

            global_logger.debug(f"Tool calls detected: {[tc.function.name for tc in last_message.tool_calls]}")
            self.memory.add(role="assistant", content=last_message.content, tool_calls=last_message.tool_calls)

            for tool_call in last_message.tool_calls:
                tool_name = tool_call.function.name
                global_logger.debug(f"Executing tool: {tool_name}")
                try:
                    tool_args = json.loads(tool_call.function.arguments)
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
                self.memory.add_tool_message(tool_call, tool_response)