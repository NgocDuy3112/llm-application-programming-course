import json

from logger import global_logger
from orchestrator.memory import *
from orchestrator.tools import *
from model.adapter import *




class FullChatbotEngine:
    def __init__(self, adapter: BaseAdapter | None = None, memory: BaseMemory | None = None):
        """
        Khởi tạo engine với adapter và memory.
        
        Args:
            adapter: BaseAdapter instance - nếu có thì dùng cái này thay vì tạo từ provider
            memory: BaseMemory instance - nếu None thì tạo mặc định
        """
        global_logger.debug(f"Initializing FullChatbotEngine with adapter={adapter.__class__.__name__}, memory={memory.__class__.__name__}")
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
        max_output_tokens: int = 65536,
        **kwargs
    ):
        global_logger.info(f"Processing user input: {input[:50]}...")
        system_message = {"role": "system", "content": instruction if instruction else ""}
        tools = tools if tool_choice != ToolChoice.NONE else None
        
        # Add user message once, before the tool-calling loop
        if self.memory is not None:
            self.memory.add(role="user", content=input)
        
        while True:
            if self.memory is not None:
                messages = [system_message] + self.memory.get_messages()
            else:
                user_message = {"role": "user", "content": input}
                messages = [system_message, user_message]
            response = self.adapter.response(
                model=model, 
                messages=messages, 
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            )
            last_message = response.choices[0].message
            
            if not last_message.tool_calls:
                global_logger.debug(f"No tool calls, returning assistant response")
                if self.memory is not None:
                    self.memory.add(role="assistant", content=last_message.content)
                return last_message.content

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